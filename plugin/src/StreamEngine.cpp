#include "StreamEngine.h"

#include <atomic>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <thread>

namespace groove {
namespace {

constexpr uint32_t latencySeconds = 5;
constexpr uint32_t coreSeconds = 2;

static_assert(std::atomic<uint64_t>::is_always_lock_free &&
              std::atomic<int>::is_always_lock_free &&
              std::atomic<float>::is_always_lock_free &&
              std::atomic<bool>::is_always_lock_free,
              "The audio callback requires native lock-free atomics");

struct Frame {
    uint64_t epoch = 0;
    uint64_t position = 0;
    float samples[2] = {};
    float sensitivity = 0.5f;
};

// Each queue has exactly one producer and one consumer. Indices are never
// reset while either thread is active, including when the host seeks.
class FrameQueue {
public:
    void prepare(size_t capacity) {
        frames_.resize(capacity);
        write_.store(0, std::memory_order_relaxed);
        read_.store(0, std::memory_order_relaxed);
    }

    bool push(const Frame& frame) noexcept {
        const auto write = write_.load(std::memory_order_relaxed);
        if (write - read_.load(std::memory_order_acquire) >= frames_.size())
            return false;
        frames_[write % frames_.size()] = frame;
        write_.store(write + 1, std::memory_order_release);
        return true;
    }

    bool peek(Frame& frame) const noexcept {
        const auto read = read_.load(std::memory_order_relaxed);
        if (read == write_.load(std::memory_order_acquire))
            return false;
        frame = frames_[read % frames_.size()];
        return true;
    }

    void pop() noexcept {
        read_.store(read_.load(std::memory_order_relaxed) + 1,
                    std::memory_order_release);
    }

private:
    std::vector<Frame> frames_;
    alignas(64) std::atomic<uint64_t> write_{0};
    alignas(64) std::atomic<uint64_t> read_{0};
};

} // namespace

struct StreamEngine::Impl {
    explicit Impl(Backend& instance) : backend(instance) {}

    Backend& backend;
    uint32_t rate = 0;
    uint32_t channels = 0;
    uint32_t delay = 0;
    bool prepared = false;
    bool offline = false;
    uint32_t offlineTimeoutMs = 60000;
    FrameQueue inputQueue;
    FrameQueue outputQueue;
    std::vector<float> dry;
    std::vector<float> history;
    std::vector<float> window;
    std::vector<float> cleaned;
    std::thread worker;
    std::atomic<bool> running{false};
    std::atomic<uint64_t> epoch{1};
    std::atomic<float> sensitivity{0.5f};
    std::atomic<int> monitor{Cleaned};
    std::atomic<bool> bypass{false};
    std::atomic<int> reportedStatus{Warming};
    std::atomic<uint64_t> failedEpoch{0};
    // Only the audio thread touches these, even during reset.
    uint64_t audioEpoch = 0;
    uint64_t position = 0;
    uint64_t overloadUntil = 0;
    uint64_t invalidUntil = 0;
    float dryMix = 0.f, wetMix = 1.f;
    float targetDry = 0.f, targetWet = 1.f;
    uint32_t transitionLeft = 0;

    template <typename Predicate>
    bool waitFor(Predicate ready, uint64_t expectedEpoch) {
        // Invoked only after an offline queue operation cannot make progress.
        const auto deadline = std::chrono::steady_clock::now() +
                              std::chrono::milliseconds(offlineTimeoutMs);
        for (;;) {
            if (!running.load(std::memory_order_acquire) ||
                failedEpoch.load(std::memory_order_acquire) == expectedEpoch ||
                epoch.load(std::memory_order_acquire) != expectedEpoch)
                return false;
            if (ready()) return true;
            if (std::chrono::steady_clock::now() >= deadline) return false;
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
    }

    void run() {
        uint64_t workerEpoch = 0;
        uint64_t previous = 0;
        uint64_t nextCore = 0;
        bool contiguous = false;
        const uint32_t coreFrames = rate * coreSeconds;
        const uint32_t contextFrames = rate / 2;
        const uint64_t windowFrames = uint64_t(coreFrames) + contextFrames * 2;
        while (running.load(std::memory_order_acquire)) {
            Frame frame;
            if (!inputQueue.peek(frame)) {
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
                continue;
            }
            inputQueue.pop();
            if (frame.epoch != epoch.load(std::memory_order_acquire))
                continue;

            if (!contiguous || frame.epoch != workerEpoch || frame.position != previous + 1) {
                workerEpoch = frame.epoch;
                // After a gap, wait for a complete left context. Only the very
                // first core may substitute silence for that context.
                nextCore = frame.position == 0 ? 0 :
                    ((frame.position + contextFrames + coreFrames - 1) / coreFrames) * coreFrames;
                contiguous = true;
            }
            previous = frame.position;
            const auto slot = static_cast<size_t>(frame.position % windowFrames) * channels;
            for (uint32_t channel = 0; channel < channels; ++channel)
                history[slot + channel] = frame.samples[channel];

            if (frame.position < nextCore + coreFrames + contextFrames - 1)
                continue;

            for (uint64_t index = 0; index < windowFrames; ++index) {
                const bool leftSilence = nextCore == 0 && index < contextFrames;
                const auto source = leftSilence ? 0 :
                    (nextCore + index - contextFrames) % windowFrames;
                for (uint32_t channel = 0; channel < channels; ++channel)
                    window[static_cast<size_t>(index) * channels + channel] =
                        leftSilence ? 0.0f : history[static_cast<size_t>(source) * channels + channel];
            }

            if (!running.load(std::memory_order_acquire))
                break;
            if (workerEpoch != epoch.load(std::memory_order_acquire))
                continue;
            bool ok = false;
            try {
                ok = backend.process(window, rate, channels, frame.sensitivity, cleaned);
                ok = ok && cleaned.size() == window.size();
                if (ok)
                    for (const auto sample : cleaned)
                        if (!std::isfinite(sample)) { ok = false; break; }
            } catch (...) {
                ok = false;
            }
            if (workerEpoch != epoch.load(std::memory_order_acquire))
                continue;
            failedEpoch.store(ok ? 0 : workerEpoch, std::memory_order_release);
            if (!ok && offline) {
                // A failed export stays failed until the host starts a new stream.
                while (running.load(std::memory_order_acquire) &&
                       workerEpoch == epoch.load(std::memory_order_acquire))
                    std::this_thread::sleep_for(std::chrono::milliseconds(1));
                continue;
            }
            if (ok) {
                for (uint32_t index = 0; index < coreFrames; ++index) {
                    if (!running.load(std::memory_order_acquire) ||
                        workerEpoch != epoch.load(std::memory_order_acquire))
                        break;
                    Frame result;
                    result.epoch = workerEpoch;
                    result.position = nextCore + index;
                    const auto source = static_cast<size_t>(contextFrames + index) * channels;
                    for (uint32_t channel = 0; channel < channels; ++channel)
                        result.samples[channel] = cleaned[source + channel];
                    // Never wait behind a full result queue. Missing samples
                    // retain their deadline and fall back to delayed original.
                    if (!outputQueue.push(result))
                        break;
                }
            }
            nextCore += coreFrames;
        }
    }
};

StreamEngine::StreamEngine(Backend& backend) : impl_(new Impl(backend)) {}

StreamEngine::~StreamEngine() { stop(); }

bool StreamEngine::prepare(uint32_t rate, uint32_t channels, bool offline, uint32_t offlineTimeoutMs) {
    stop();
    auto& state = *impl_;
    state.prepared = false;
    state.delay = 0;
    if (rate < 8000 || rate > 192000 || (channels != 1 && channels != 2) ||
        offlineTimeoutMs == 0 || offlineTimeoutMs > 60000) {
        state.reportedStatus.store(Unavailable, std::memory_order_release);
        return false;
    }
    try {
        state.inputQueue.prepare(static_cast<size_t>(rate) * 4);
        state.outputQueue.prepare(static_cast<size_t>(rate) * (latencySeconds + coreSeconds));
        state.dry.resize(static_cast<size_t>(rate) * latencySeconds * channels);
        const auto windowFrames = static_cast<size_t>(rate) * coreSeconds + (rate / 2) * 2;
        state.history.resize(windowFrames * channels);
        state.window.resize(windowFrames * channels);
        state.cleaned.resize(state.window.size());
    } catch (...) {
        state.reportedStatus.store(Unavailable, std::memory_order_release);
        return false;
    }
    state.rate = rate;
    state.channels = channels;
    state.delay = rate * latencySeconds;
    state.prepared = true;
    state.offline = offline;
    state.offlineTimeoutMs = offlineTimeoutMs;
    reset();
    return true;
}

void StreamEngine::start() {
    auto& state = *impl_;
    if (!state.prepared || state.worker.joinable())
        return;
    reset();
    state.running.store(true, std::memory_order_release);
    try {
        state.worker = std::thread([&state] { state.run(); });
    } catch (...) {
        state.running.store(false, std::memory_order_release);
        state.failedEpoch.store(state.epoch.load(std::memory_order_acquire), std::memory_order_release);
        state.reportedStatus.store(Unavailable, std::memory_order_release);
    }
}

void StreamEngine::stop() {
    auto& state = *impl_;
    state.running.store(false, std::memory_order_release);
    if (state.worker.joinable()) {
        state.backend.cancel();
        state.worker.join();
    }
}

void StreamEngine::reset() noexcept {
    impl_->failedEpoch.store(0, std::memory_order_release);
    impl_->epoch.fetch_add(1, std::memory_order_acq_rel);
    impl_->reportedStatus.store(Warming, std::memory_order_release);
}

void StreamEngine::setSensitivity(float sensitivity) noexcept {
    if (!std::isfinite(sensitivity))
        sensitivity = 0.5f;
    impl_->sensitivity.store(sensitivity < 0.0f ? 0.0f : sensitivity > 1.0f ? 1.0f : sensitivity,
                             std::memory_order_relaxed);
}

void StreamEngine::setMonitor(int monitor) noexcept {
    impl_->monitor.store(monitor >= Cleaned && monitor <= Removed ? monitor : Cleaned,
                         std::memory_order_relaxed);
}

void StreamEngine::setBypass(bool bypass) noexcept {
    impl_->bypass.store(bypass, std::memory_order_relaxed);
}

void StreamEngine::process(const float* const* input, float* const* output, int frames) noexcept {
    render(input, output, frames, false);
}

bool StreamEngine::processOffline(const float* const* input, float* const* output, int frames) noexcept {
    return render(input, output, frames, true);
}

bool StreamEngine::render(const float* const* input, float* const* output, int frames, bool offline) noexcept {
    auto& state = *impl_;
    const auto fail = [&] {
        if (offline) {
            state.running.store(false, std::memory_order_release);
            try { state.backend.cancel(); } catch (...) {}
        }
        for (uint32_t channel = 0; channel < state.channels; ++channel)
            if (output && output[channel] && frames > 0)
                std::fill_n(output[channel], frames, 0.0f);
        state.failedEpoch.store(state.epoch.load(std::memory_order_acquire), std::memory_order_release);
        state.reportedStatus.store(Unavailable, std::memory_order_release);
        return false;
    };
    if (!state.prepared || offline != state.offline || frames < 0)
        return fail();
    if (frames == 0) return true;
    int blockStatus = Warming;
    bool droppedInput = false;
    for (int index = 0; index < frames; ++index) {
        const auto epoch = state.epoch.load(std::memory_order_acquire);
        const auto monitor = state.monitor.load(std::memory_order_relaxed);
        const bool bypass = state.bypass.load(std::memory_order_relaxed);
        const float targetDry = bypass || monitor == Original || monitor == Removed ? 1.f : 0.f;
        const float targetWet = bypass || monitor == Original ? 0.f : monitor == Removed ? -1.f : 1.f;
        if (state.audioEpoch != epoch) {
            state.audioEpoch = epoch;
            state.position = 0;
            state.overloadUntil = 0;
            state.invalidUntil = 0;
            state.dryMix = state.targetDry = targetDry;
            state.wetMix = state.targetWet = targetWet;
            state.transitionLeft = 0;
        }
        if (targetDry != state.targetDry || targetWet != state.targetWet) {
            state.targetDry = targetDry;
            state.targetWet = targetWet;
            state.transitionLeft = std::max(1u, state.rate / 200); // 5 ms, including mid-ramp changes.
        }
        if (state.transitionLeft) {
            state.dryMix += (targetDry - state.dryMix) / state.transitionLeft;
            state.wetMix += (targetWet - state.wetMix) / state.transitionLeft;
            if (--state.transitionLeft == 0) {
                state.dryMix = targetDry;
                state.wetMix = targetWet;
            }
        }
        const auto position = state.position++;
        const bool due = position >= state.delay;
        const auto desired = due ? position - state.delay : 0;
        const auto slot = static_cast<size_t>(position % state.delay) * state.channels;
        Frame incoming;
        incoming.epoch = epoch;
        incoming.position = position;
        incoming.sensitivity = state.sensitivity.load(std::memory_order_relaxed);
        float original[2] = {};
        for (uint32_t channel = 0; channel < state.channels; ++channel) {
            incoming.samples[channel] = input && input[channel] ? input[channel][index] : 0.0f;
            if (!std::isfinite(incoming.samples[channel])) {
                if (offline) return fail();
                incoming.samples[channel] = 0.f;
                state.invalidUntil = position + state.delay + state.rate;
            }
            original[channel] = due ? state.dry[slot + channel] : 0.0f;
            state.dry[slot + channel] = incoming.samples[channel];
        }
        if (offline) {
            if (!state.running.load(std::memory_order_acquire) ||
                state.failedEpoch.load(std::memory_order_acquire) == epoch) return fail();
            if (!state.inputQueue.push(incoming) &&
                !state.waitFor([&] { return state.inputQueue.push(incoming); }, epoch)) return fail();
        } else if (state.running.load(std::memory_order_acquire) && !state.inputQueue.push(incoming)) {
            droppedInput = true;
        }

        Frame result;
        bool haveCleaned = false;
        // A seek can leave a full old-epoch queue. Drain a bounded amount per
        // sample, even during warmup, so old results cannot obstruct new ones.
        const auto receive = [&] {
            for (int attempt = 0; attempt < 8; ++attempt) {
                if (!state.outputQueue.peek(result))
                    break;
                if (result.epoch != epoch || (due && result.position < desired)) {
                    state.outputQueue.pop();
                    continue;
                }
                if (due && result.position == desired) {
                    state.outputQueue.pop();
                    haveCleaned = true;
                }
                break;
            }
            return haveCleaned;
        };
        receive();
        if (offline && due && !haveCleaned && !state.waitFor(receive, epoch)) return fail();
        const bool failed = state.failedEpoch.load(std::memory_order_acquire) == epoch ||
                            !state.running.load(std::memory_order_acquire);
        int frameStatus = failed || position < state.invalidUntil ? Unavailable :
                          !due ? Warming : haveCleaned ? Ready : Overloaded;
        if (frameStatus > blockStatus)
            blockStatus = frameStatus;
        for (uint32_t channel = 0; channel < state.channels; ++channel) {
            const float cleaned = haveCleaned ? result.samples[channel] : original[channel];
            // Keep steady modes exact. Double accumulation avoids intermediate
            // overflow during transitions between otherwise finite float32 signals.
            float sample = state.transitionLeft == 0 ?
                (bypass || monitor == Original ? original[channel] :
                 monitor == Removed ? original[channel] - cleaned : cleaned) :
                static_cast<float>(double(state.dryMix) * original[channel] + double(state.wetMix) * cleaned);
            if (!std::isfinite(sample)) {
                if (offline) return fail();
                sample = 0.f;
                blockStatus = Unavailable;
            }
            if (output && output[channel])
                output[channel][index] = sample;
        }
    }
    if (droppedInput && blockStatus != Unavailable)
        blockStatus = Overloaded;
    if (blockStatus == Overloaded)
        state.overloadUntil = state.position + state.rate;
    else if (blockStatus == Ready && state.position < state.overloadUntil)
        blockStatus = Overloaded;
    state.reportedStatus.store(blockStatus, std::memory_order_release);
    return true;
}

uint32_t StreamEngine::latency() const noexcept { return impl_->delay; }

int StreamEngine::status() const noexcept {
    return impl_->reportedStatus.load(std::memory_order_acquire);
}

} // namespace groove
