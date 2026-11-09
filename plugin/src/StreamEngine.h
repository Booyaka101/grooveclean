#pragma once

#include <cstdint>
#include <memory>
#include <vector>

namespace groove {

class Backend {
public:
    virtual ~Backend() = default;
    virtual bool process(const std::vector<float>& interleaved, uint32_t rate,
                         uint32_t channels, float sensitivity,
                         std::vector<float>& cleaned) = 0;
    virtual void cancel() = 0;
};

class StreamEngine {
public:
    enum Monitor { Cleaned = 0, Original = 1, Removed = 2 };
    enum Status { Warming = 0, Ready = 1, Overloaded = 2, Unavailable = 3 };

    explicit StreamEngine(Backend& backend);
    ~StreamEngine();
    StreamEngine(const StreamEngine&) = delete;
    StreamEngine& operator=(const StreamEngine&) = delete;

    // Lifecycle calls are serialized by the host, outside the audio callback.
    // prepare must not run concurrently with process. The backend is started
    // externally; cancel must unblock an in-flight backend call for stop().
    // Two-second cores use half-second context per side and five-second latency.
    // Context is floor(rate / 2) frames, including for odd sample rates.
    bool prepare(uint32_t rate, uint32_t channels, bool offline = false,
                 uint32_t offlineTimeoutMs = 60000);
    void start();
    void stop();
    void reset() noexcept;
    void setSensitivity(float sensitivity) noexcept;
    void setMonitor(int monitor) noexcept;
    void setBypass(bool bypass) noexcept;
    void process(const float* const* input, float* const* output, int frames) noexcept;
    // Only for a host-negotiated offline session. Waits for exact results, never
    // substitutes original audio on failure. The host must feed silence to flush latency.
    bool processOffline(const float* const* input, float* const* output, int frames) noexcept;
    uint32_t latency() const noexcept;
    int status() const noexcept;

private:
    bool render(const float* const* input, float* const* output, int frames, bool offline) noexcept;
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace groove
