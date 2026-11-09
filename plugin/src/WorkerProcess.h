#pragma once

#include "StreamEngine.h"
#include <atomic>
#include <windows.h>
#include <string>

namespace groove {

// All pipe I/O runs on StreamEngine's worker. cancel() may run concurrently;
// launch/close require that worker to be stopped and joined first.
class WorkerProcess final : public Backend {
public:
    ~WorkerProcess() override;
    bool launch();
    bool process(const std::vector<float>& input, uint32_t rate, uint32_t channels,
                 float sensitivity, std::vector<float>& cleaned) override;
    void cancel() override;
    void close();

private:
    bool read(void* bytes, size_t count);
    bool write(const void* bytes, size_t count);
    HANDLE process_ = nullptr;
    HANDLE input_ = nullptr;
    HANDLE output_ = nullptr;
    HANDLE job_ = nullptr;
    bool ready_ = false;
    bool broken_ = false;
    std::atomic<bool> cancelled_{false};
};

} // namespace groove
