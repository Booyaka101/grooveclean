#include "base/source/fstreamer.h"
#include "pluginterfaces/gui/iplugview.h"
#include "pluginterfaces/vst/ivstaudioprocessor.h"
#include "pluginterfaces/vst/ivsteditcontroller.h"
#include "pluginterfaces/vst/ivstprocesscontext.h"
#include "public.sdk/source/common/memorystream.h"
#include "public.sdk/source/vst/hosting/hostclasses.h"
#include "public.sdk/source/vst/hosting/module.h"
#include "public.sdk/source/vst/hosting/parameterchanges.h"
#include <windows.h>
#include <commctrl.h>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <thread>
#include <vector>

using namespace Steinberg;
using namespace Steinberg::Vst;
void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

int main(int argc, char** argv) {
    try {
        require(argc == 2, "Provide the VST3 bundle path");
        std::string error;
        auto module = VST3::Hosting::Module::create(argv[1], error);
        require(module != nullptr, error.c_str());
        const auto& factory = module->getFactory();
        const auto classes = factory.classInfos();
        require(classes.size() == 2, "Expected processor and controller classes");
        IPtr<IComponent> component;
        IPtr<IEditController> controller;
        for (const auto& info : classes) {
            if (info.category() == kVstAudioEffectClass)
                component = factory.createInstance<IComponent>(info.ID());
            if (info.category() == kVstComponentControllerClass)
                controller = factory.createInstance<IEditController>(info.ID());
        }
        auto host = owned(new HostApplication);
        require(component && controller, "Cannot instantiate classes");
        require(component->initialize(host) == kResultOk, "Processor initialization");
        require(controller->initialize(host) == kResultOk, "Controller initialization");
        FUnknownPtr<IAudioProcessor> processor(component);
        require(processor != nullptr, "Missing audio processor");

        MemoryStream state;
        IBStreamer writer(&state, kLittleEndian);
        writer.writeInt32(1);
        writer.writeDouble(0.7);
        writer.writeDouble(0.5); // Original monitor, exact dry-delay assertions below.
        writer.writeDouble(0.0);
        state.seek(0, IBStream::kIBSeekSet, nullptr);
        require(component->setState(&state) == kResultOk, "Restore processor state");
        state.seek(0, IBStream::kIBSeekSet, nullptr);
        require(controller->setComponentState(&state) == kResultOk, "Restore controller state");
        require(controller->getParamNormalized(0) == 0.7 &&
                controller->getParamNormalized(1) == 0.5, "Restored parameter values");
        for (double invalid : {-.1, 1.1, std::numeric_limits<double>::quiet_NaN()}) {
            MemoryStream badState;
            IBStreamer badWriter(&badState, kLittleEndian);
            badWriter.writeInt32(1);
            badWriter.writeDouble(invalid);
            badWriter.writeDouble(0);
            badWriter.writeDouble(0);
            badState.seek(0, IBStream::kIBSeekSet, nullptr);
            require(component->setState(&badState) != kResultOk, "Invalid processor state accepted");
            badState.seek(0, IBStream::kIBSeekSet, nullptr);
            require(controller->setComponentState(&badState) != kResultOk, "Invalid controller state accepted");
            require(controller->getParamNormalized(0) == .7, "Rejected state changed controller");
        }

        // Exercise the native editor without displaying or altering a user's DAW.
        HWND parent = CreateWindowExW(0, L"STATIC", L"GrooveClean smoke test", WS_OVERLAPPED,
                                       0, 0, 500, 340, nullptr, nullptr, GetModuleHandleW(nullptr), nullptr);
        require(parent != nullptr, "Create editor parent");
        auto view = owned(controller->createView(ViewType::kEditor));
        require(view && view->attached(parent, kPlatformTypeHWND) == kResultOk, "Attach native editor");
        const HWND editor = GetWindow(parent, GW_CHILD);
        const HWND slider = GetDlgItem(editor, 100);
        require(slider && GetDlgItem(editor, 112) && GetDlgItem(editor, 120), "Editor controls missing");
        SendMessageW(slider, TBM_SETPOS, TRUE, 73);
        SendMessageW(editor, WM_HSCROLL, TB_THUMBPOSITION, reinterpret_cast<LPARAM>(slider));
        require(controller->getParamNormalized(0) == .73, "Editor slider did not edit sensitivity");
        SendDlgItemMessageW(editor, 112, BM_CLICK, 0, 0);
        require(controller->getParamNormalized(1) == 1, "Editor Removed button did not edit monitor");
        SendDlgItemMessageW(editor, 120, BM_CLICK, 0, 0);
        require(controller->getParamNormalized(2) == 1, "Editor bypass did not edit parameter");
        state.seek(0, IBStream::kIBSeekSet, nullptr);
        require(controller->setComponentState(&state) == kResultOk, "Restore editor state after input checks");
        ViewRect rect;
        require(view->getSize(&rect) == kResultOk && rect.getWidth() == 480, "Editor dimensions");
        require(view->removed() == kResultOk, "Detach native editor");
        require(view->attached(parent, kPlatformTypeHWND) == kResultOk, "Reattach native editor");
        DestroyWindow(parent);
        require(view->removed() == kResultOk, "Detach editor after parent destruction");
        view = nullptr;

        SpeakerArrangement arrangement = SpeakerArr::kStereo;
        require(processor->setBusArrangements(&arrangement, 1, &arrangement, 1) == kResultOk,
                "Stereo arrangement");
        constexpr int rate = 44100, block = 441, seconds = 10, duration = 5 * rate + 173;
        ProcessSetup setup{kRealtime, kSample32, block, rate};
        require(processor->setupProcessing(setup) == kResultOk, "Realtime setup");
        require(processor->getLatencySamples() == 5 * rate, "Reported five-second latency");
        require(processor->getTailSamples() == 5 * rate, "Reported flush tail");
        require(component->setActive(true) == kResultOk, "Activate processor");
        require(processor->setProcessing(true) == kResultOk, "Start processing");

        std::vector<float> left(block), right(block), outLeft(block), outRight(block);
        float* inputs[] = {left.data(), right.data()};
        float* outputs[] = {outLeft.data(), outRight.data()};
        AudioBusBuffers inputBus{}, outputBus{};
        inputBus.numChannels = outputBus.numChannels = 2;
        inputBus.channelBuffers32 = inputs;
        outputBus.channelBuffers32 = outputs;
        ParameterChanges changes(4);
        ProcessContext context{};
        context.state = ProcessContext::kPlaying;
        context.sampleRate = rate;
        ProcessData data{};
        data.processMode = kRealtime;
        data.symbolicSampleSize = kSample32;
        data.numSamples = block;
        data.numInputs = data.numOutputs = 1;
        data.inputs = &inputBus;
        data.outputs = &outputBus;
        data.outputParameterChanges = &changes;
        data.processContext = &context;
        const bool workerConfigured = std::getenv("GROOVECLEAN_PYTHON") != nullptr;
        const auto tone = [=](int frame) {
            const double fade = std::clamp((duration - frame) / (rate * .1), 0.0, 1.0);
            return static_cast<float>(.05 * fade * std::sin(frame * 440.0 * 6.283185307179586 / rate));
        };
        const auto sourceAt = [&](int frame, bool damaged) {
            if (frame < 0 || frame >= duration) return 0.f;
            float value = tone(frame);
            const float click[] = {.5f, -.4f, .25f, -.15f, .08f};
            if (damaged) for (int seam : {2 * rate, 4 * rate, duration - 3}) {
                const int at = frame - (seam - 2);
                if (at >= 0 && at < 5) value += click[at];
            }
            return value;
        };
        // First verify exact Original monitoring, then reset the transport and verify
        // actual model repairs through the loaded plugin, not only the fake backend.
        for (int playback = 0; playback < 3; ++playback) {
            if (playback) {
                require(processor->setProcessing(false) == kResultOk, "Stop before transport reset");
                if (playback == 2) {
                    require(component->setActive(false) == kResultOk, "Deactivate before offline mode");
                    setup.processMode = kOffline;
                    data.processMode = kOffline;
                    require(processor->setupProcessing(setup) == kResultOk, "Offline setup");
                    const auto activated = component->setActive(true);
                    if (!workerConfigured) {
                        require(activated != kResultOk, "Offline activation accepted missing worker");
                        break;
                    }
                    require(activated == kResultOk, "Offline activation");
                }
                require(processor->setProcessing(true) == kResultOk, "Restart after transport reset");
            }
            bool ready = false;
            int repaired = 0;
            const auto begin = std::chrono::steady_clock::now();
            ParameterChanges edits(1);
            int32 point = 0;
            const ParamID monitorId = 1;
            edits.addParameterData(monitorId, point)->addPoint(0, playback ? 0.0 : 0.5, point);
            const int total = playback == 2 ? duration + 5 * rate : seconds * rate;
            context.state = ProcessContext::kPlaying;
            for (int offset = 0; offset < total; offset += block) {
                const int count = std::min(block, total - offset);
                data.numSamples = count;
                for (int i = 0; i < count; ++i) {
                    left[i] = sourceAt(offset + i, false);
                    right[i] = sourceAt(offset + i, true);
                }
                context.projectTimeSamples = offset;
                if (offset >= duration) {
                    context.state = 0;
                    context.projectTimeSamples = duration;
                }
                data.inputParameterChanges = offset == 0 ? &edits : nullptr;
                changes.clearQueue();
                require(processor->process(data) == kResultOk, "Process callback failed");
                for (int i = 0; i < count; ++i) {
                    const int source = offset + i - 5 * rate;
                    if (!playback || !workerConfigured) {
                        require(outLeft[i] == sourceAt(source, false) &&
                                outRight[i] == sourceAt(source, true), "Dry delay alignment");
                    } else if (source >= rate) {
                        require(outLeft[i] == sourceAt(source, false), "Clean channel was modified");
                        for (int seam : {2 * rate, 4 * rate, duration - 3}) if (source >= seam - 2 && source < seam + 3) {
                            require(std::abs(outRight[i] - tone(source)) < .05f,
                                    "Boundary click survived end-to-end plugin playback");
                            ++repaired;
                        }
                    }
                }
                for (int i = 0; i < changes.getParameterCount(); ++i) {
                    auto* queue = changes.getParameterData(i);
                    int32 at = 0;
                    double value = 0;
                    if (queue->getParameterId() == 3 && queue->getPoint(0, at, value) == kResultOk &&
                        std::abs(value - 1.0 / 3.0) < 1e-6) ready = true;
                }
                if (workerConfigured && playback != 2)
                    std::this_thread::sleep_until(begin + std::chrono::milliseconds((offset + block) * 1000LL / rate));
            }
            require(!workerConfigured || ready, "Configured model never became ready during real-time playback");
            require(!workerConfigured || !playback || repaired == (playback == 2 ? 15 : 10),
                    "Not all boundary/final-click samples were checked");
        }
        data.inputParameterChanges = nullptr;
        if (workerConfigured) {
            require(processor->setProcessing(false) == kResultOk, "Stop before failure test");
            require(processor->setProcessing(true) == kResultOk, "Reset before failure test");
            bool failed = false;
            data.numSamples = block;
            for (int offset = 0; offset < 9 * rate; offset += block) {
                std::fill(left.begin(), left.end(), 0.f);
                std::fill(right.begin(), right.end(), 0.f);
                if (!offset) right[0] = std::numeric_limits<float>::quiet_NaN();
                context.projectTimeSamples = offset;
                changes.clearQueue();
                if (processor->process(data) != kResultOk) {
                    failed = true;
                    for (int i = 0; i < block; ++i)
                        require(outLeft[i] == 0 && outRight[i] == 0, "Failed export block was not silenced");
                    bool unavailable = false;
                    for (int i = 0; i < changes.getParameterCount(); ++i) {
                        auto* queue = changes.getParameterData(i);
                        int32 at = 0;
                        double value = 0;
                        if (queue->getParameterId() == 3 && queue->getPoint(0, at, value) == kResultOk &&
                            value == 1) unavailable = true;
                    }
                    require(unavailable, "Offline failure status not delivered to host");
                    break;
                }
            }
            require(failed, "Invalid model input silently exported");
            require(processor->process(data) != kResultOk, "Failed export silently recovered");
        }
        require(processor->setProcessing(false) == kResultOk, "Stop processing");
        require(component->setActive(false) == kResultOk, "Deactivate processor");

        setup.processMode = kOffline;
        setup.sampleRate = 384000;
        require(processor->setupProcessing(setup) != kResultOk, "Offline unsupported rate must fail");
        require(processor->getLatencySamples() == 5 * rate, "Rejected setup altered previous latency");
        setup.processMode = kRealtime;
        data.processMode = kRealtime;
        data.numSamples = block;
        for (double unsupported : {384000.0, 12345.678}) {
            setup.sampleRate = unsupported;
            require(processor->setupProcessing(setup) == kResultOk, "Negotiate unsupported rate safely");
            require(processor->getLatencySamples() == 0, "Unsupported-rate passthrough latency");
            require(component->setActive(true) == kResultOk, "Activate unsupported-rate passthrough");
            changes.clearQueue();
            require(processor->process(data) == kResultOk, "Unsupported-rate passthrough callback");
            for (int index = 0; index < block; ++index) {
                require(outLeft[index] == (std::isfinite(left[index]) ? left[index] : 0.f) &&
                        outRight[index] == (std::isfinite(right[index]) ? right[index] : 0.f),
                        "Unsupported-rate passthrough modified finite audio or leaked non-finite input");
            }
            bool unavailable = false;
            for (int i = 0; i < changes.getParameterCount(); ++i) {
                auto* queue = changes.getParameterData(i);
                int32 at = 0;
                double value = 0;
                if (queue->getParameterId() == 3 && queue->getPoint(0, at, value) == kResultOk &&
                    value == 1) unavailable = true;
            }
            require(unavailable, "Unsupported-rate passthrough did not report unavailable");
            require(component->setActive(false) == kResultOk, "Deactivate unsupported-rate passthrough");
        }
        require(component->terminate() == kResultOk, "Terminate processor");
        require(controller->terminate() == kResultOk, "Terminate controller");
        std::cout << "VST3 load, state, editor, latency and playback smoke test passed\n";
        return 0;
    } catch (const std::exception& exception) {
        std::cerr << exception.what() << '\n';
        return 1;
    }
}
