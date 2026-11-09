#include "WorkerProcess.h"
#include <array>
#include <cmath>
#include <cstring>
#include <filesystem>
#include <vector>

namespace groove {
namespace {
void release(HANDLE& handle) {
    if (handle && handle != INVALID_HANDLE_VALUE) CloseHandle(handle);
    handle = nullptr;
}

struct ChildHandles {
    HANDLE input = nullptr, output = nullptr, error = nullptr;
    ~ChildHandles() { release(input); release(output); release(error); }
};

struct AttributeList {
    LPPROC_THREAD_ATTRIBUTE_LIST value;
    ~AttributeList() { DeleteProcThreadAttributeList(value); }
};

struct Request {
    char magic[4] = {'G', 'C', 'R', 'Q'};
    uint32_t version = 1;
    uint32_t rate;
    uint32_t channels;
    uint32_t frames;
    float sensitivity;
    float width = 20.f;
};
struct Response {
    char magic[4];
    uint32_t version;
    uint32_t status;
    uint32_t frames;
};
static_assert(sizeof(Request) == 28 && sizeof(Response) == 16);
}

WorkerProcess::~WorkerProcess() { close(); }

bool WorkerProcess::launch() try {
    close();
    std::array<wchar_t, 32768> python{};
    const auto length = GetEnvironmentVariableW(L"GROOVECLEAN_PYTHON", python.data(),
                                                static_cast<DWORD>(python.size()));
    if (!length || length >= python.size()) return false;
    const std::filesystem::path executable(python.data());
    const auto attributes = GetFileAttributesW(python.data());
    if (!executable.is_absolute() || _wcsicmp(executable.extension().c_str(), L".exe") ||
        attributes == INVALID_FILE_ATTRIBUTES || (attributes & FILE_ATTRIBUTE_DIRECTORY)) return false;

    SECURITY_ATTRIBUTES security{sizeof(SECURITY_ATTRIBUTES), nullptr, TRUE};
    ChildHandles childHandles;
    auto& childInput = childHandles.input;
    auto& childOutput = childHandles.output;
    auto& childError = childHandles.error;
    const auto cleanup = [&] {
        release(childInput);
        release(childOutput);
        release(childError);
    };
    if (!CreatePipe(&childInput, &input_, &security, 0) ||
        !CreatePipe(&output_, &childOutput, &security, 0) ||
        !SetHandleInformation(input_, HANDLE_FLAG_INHERIT, 0) ||
        !SetHandleInformation(output_, HANDLE_FLAG_INHERIT, 0)) {
        cleanup(); close(); return false;
    }
    // Each process owns a separate diagnostic log; neither protocol nor DAW stdout is used.
    std::array<wchar_t, MAX_PATH> temp{}, log{};
    if (!GetTempPathW(static_cast<DWORD>(temp.size()), temp.data()) ||
        !GetTempFileNameW(temp.data(), L"gcv", 0, log.data())) {
        cleanup(); close(); return false;
    }
    childError = CreateFileW(log.data(), GENERIC_WRITE, FILE_SHARE_READ, &security,
                             OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (childError == INVALID_HANDLE_VALUE) {
        cleanup(); close(); return false;
    }
    OutputDebugStringW((std::wstring(L"GrooveClean worker log: ") + log.data() + L"\n").c_str());

    SIZE_T attributeSize = 0;
    InitializeProcThreadAttributeList(nullptr, 1, 0, &attributeSize);
    std::vector<unsigned char> attributeStorage(attributeSize);
    auto* list = reinterpret_cast<LPPROC_THREAD_ATTRIBUTE_LIST>(attributeStorage.data());
    if (!InitializeProcThreadAttributeList(list, 1, 0, &attributeSize)) {
        cleanup(); close(); return false;
    }
    AttributeList attributeList{list};
    HANDLE inherited[] = {childInput, childOutput, childError};
    STARTUPINFOEXW startup{};
    startup.StartupInfo.cb = sizeof(startup);
    startup.StartupInfo.dwFlags = STARTF_USESTDHANDLES;
    startup.StartupInfo.hStdInput = childInput;
    startup.StartupInfo.hStdOutput = childOutput;
    startup.StartupInfo.hStdError = childError;
    startup.lpAttributeList = list;
    PROCESS_INFORMATION child{};
    std::wstring command = L"\"" + executable.wstring() +
                           L"\" -I -u -m grooveclean.plugin_worker";
    const bool configured = UpdateProcThreadAttribute(list, 0,
        PROC_THREAD_ATTRIBUTE_HANDLE_LIST, inherited, sizeof(inherited), nullptr, nullptr) != FALSE;
    // Suspended creation ensures the child belongs to our kill-on-close job before it runs.
    const bool created = configured && CreateProcessW(python.data(), command.data(), nullptr,
        nullptr, TRUE, CREATE_NO_WINDOW | CREATE_SUSPENDED | EXTENDED_STARTUPINFO_PRESENT,
        nullptr, executable.parent_path().c_str(), &startup.StartupInfo, &child);
    cleanup();
    if (!created) { close(); return false; }
    process_ = child.hProcess;
    job_ = CreateJobObjectW(nullptr, nullptr);
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits{};
    limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
    const bool owned = job_ && SetInformationJobObject(job_, JobObjectExtendedLimitInformation,
        &limits, sizeof(limits)) && AssignProcessToJobObject(job_, process_);
    if (!owned || ResumeThread(child.hThread) == static_cast<DWORD>(-1)) {
        release(child.hThread); close(); return false;
    }
    release(child.hThread);
    cancelled_.store(false, std::memory_order_release);
    return true;
} catch (...) {
    close();
    return false;
}

bool WorkerProcess::read(void* bytes, size_t count) {
    auto* cursor = static_cast<unsigned char*>(bytes);
    while (count) {
        DWORD done = 0;
        if (!output_ || !ReadFile(output_, cursor, static_cast<DWORD>(count), &done, nullptr) || !done)
            return false;
        cursor += done;
        count -= done;
    }
    return true;
}

bool WorkerProcess::write(const void* bytes, size_t count) {
    const auto* cursor = static_cast<const unsigned char*>(bytes);
    while (count) {
        DWORD done = 0;
        if (!input_ || !WriteFile(input_, cursor, static_cast<DWORD>(count), &done, nullptr) || !done)
            return false;
        cursor += done;
        count -= done;
    }
    return true;
}

bool WorkerProcess::process(const std::vector<float>& input, uint32_t rate, uint32_t channels,
                            float sensitivity, std::vector<float>& cleaned) try {
    if (!process_ || broken_ || cancelled_.load(std::memory_order_acquire) ||
        channels < 1 || channels > 2 || rate < 8000 || rate > 192000 ||
        input.empty() || input.size() % channels || input.size() / channels > 5 * rate ||
        !std::isfinite(sensitivity) || sensitivity < 0 || sensitivity > 1) return false;
    if (!ready_) {
        char magic[8];
        if (!read(magic, sizeof(magic)) || std::memcmp(magic, "GCREADY1", 8)) {
            broken_ = true;
            return false;
        }
        ready_ = true;
    }
    Request request;
    request.rate = rate;
    request.channels = channels;
    request.frames = static_cast<uint32_t>(input.size() / channels);
    request.sensitivity = sensitivity;
    Response response{};
    if (!write(&request, sizeof(request)) || !write(input.data(), input.size() * sizeof(float)) ||
        !read(&response, sizeof(response)) || std::memcmp(response.magic, "GCRS", 4) ||
        response.version != 1 || response.status > 1 ||
        response.frames != (response.status ? 0 : request.frames)) {
        broken_ = true;
        return false;
    }
    if (response.status) return false;
    cleaned.resize(input.size());
    if (!read(cleaned.data(), cleaned.size() * sizeof(float))) {
        broken_ = true;
        return false;
    }
    for (const auto sample : cleaned) if (!std::isfinite(sample)) { broken_ = true; return false; }
    return true;
} catch (...) {
    // Once a response is partly consumed, another request cannot safely resync it.
    broken_ = true;
    return false;
}

void WorkerProcess::cancel() {
    cancelled_.store(true, std::memory_order_release);
    if (job_) TerminateJobObject(job_, 0);
    // Also cover suspended children whose assignment to our job failed.
    if (process_) TerminateProcess(process_, 0);
}

void WorkerProcess::close() {
    cancel();
    if (process_) WaitForSingleObject(process_, 5000);
    release(input_); release(output_); release(process_); release(job_);
    ready_ = false;
    broken_ = false;
}

} // namespace groove
