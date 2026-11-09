#include "StreamEngine.h"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <condition_variable>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <mutex>
#include <stdexcept>
#include <thread>
#include <vector>

namespace {

constexpr uint32_t rate = 8000;
constexpr uint32_t delay = rate * 5;

void require(bool condition, const char* message) {
    if (!condition)
        throw std::runtime_error(message);
}

template <typename Predicate>
void waitFor(Predicate predicate, const char* message) {
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(3);
    while (!predicate()) {
        require(std::chrono::steady_clock::now() < deadline, message);
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
}

float signal(uint64_t position, uint32_t channel, int seed) {
    return static_cast<float>(int((position * 17 + channel * 37 + seed * 71) % 997) - 498) / 1024.0f;
}

class FakeBackend : public groove::Backend {
public:
    explicit FakeBackend(float value = 0.5f) : gain(value) {}

    bool process(const std::vector<float>& input, uint32_t sampleRate,
                 uint32_t channels, float sensitivity,
                 std::vector<float>& output) override {
        const int core = entered.fetch_add(1);
        lastSensitivity.store(sensitivity);
        {
            std::unique_lock<std::mutex> lock(mutex);
            condition.wait(lock, [&] { return !paused || cancelled; });
            if (cancelled)
                return false;
        }
        const auto contextFrames = sampleRate / 2;
        const auto coreFrames = sampleRate * 2;
        const auto windowFrames = coreFrames + contextFrames * 2;
        if (input.size() != size_t(windowFrames) * channels ||
            sensitivity < 0.0f || sensitivity > 1.0f)
            valid.store(false);
        if (expectedSeed >= 0) {
            for (uint32_t index = 0; index < windowFrames; ++index) {
                const int64_t position = int64_t(core) * coreFrames + index - contextFrames;
                for (uint32_t channel = 0; channel < channels; ++channel) {
                    const float expected = position < 0 ? 0.0f :
                        signal(static_cast<uint64_t>(position), channel, expectedSeed);
                    if (input[size_t(index) * channels + channel] != expected)
                        valid.store(false);
                }
            }
        }
        output.resize(input.size());
        for (size_t index = 0; index < input.size(); ++index)
            output[index] = input[index] * gain;
        if (invalidOutput) output[0] = std::numeric_limits<float>::quiet_NaN();
        calls.fetch_add(1);
        return !fail.load();
    }

    void cancel() override {
        cancellations.fetch_add(1);
        std::lock_guard<std::mutex> lock(mutex);
        cancelled = true;
        condition.notify_all();
    }

    void pause() {
        std::lock_guard<std::mutex> lock(mutex);
        paused = true;
    }

    void release() {
        std::lock_guard<std::mutex> lock(mutex);
        paused = false;
        condition.notify_all();
    }

    float gain;
    int expectedSeed = -1;
    bool invalidOutput = false;
    std::atomic<float> lastSensitivity{0};
    std::atomic<int> cancellations{0};
    std::atomic<int> calls{0};
    std::atomic<int> entered{0};
    std::atomic<bool> fail{false};
    std::atomic<bool> valid{true};
    std::mutex mutex;
    std::condition_variable condition;
    bool paused = false;
    bool cancelled = false;
};

// Split at second boundaries so tests can let the worker get ahead without
// sleeping, allocating, or otherwise helping it from inside the callback.
std::vector<float> render(groove::StreamEngine& engine, FakeBackend& backend,
                          uint32_t channels, uint32_t total, int seed,
                          bool pace = true, int completedBefore = 0, bool inPlace = false,
                          uint32_t sourceStart = 0) {
    const uint32_t blocks[] = {1, 31, 257, 1001, 13, 4096, 9001, 7};
    std::vector<float> result(size_t(total) * channels);
    std::vector<float> input[2], output[2];
    for (uint32_t channel = 0; channel < channels; ++channel) {
        input[channel].resize(9001);
        output[channel].resize(9001);
    }
    uint32_t position = 0;
    size_t block = 0;
    while (position < total) {
        const auto count = std::min({blocks[block++ % 8], total - position,
                                     rate - position % rate});
        const float* inputs[2] = {input[0].data(), input[1].data()};
        float* outputs[2] = {inPlace ? input[0].data() : output[0].data(),
                             inPlace ? input[1].data() : output[1].data()};
        for (uint32_t channel = 0; channel < channels; ++channel)
            for (uint32_t index = 0; index < count; ++index)
                input[channel][index] = signal(sourceStart + position + index, channel, seed);
        engine.process(inputs, outputs, static_cast<int>(count));
        for (uint32_t index = 0; index < count; ++index)
            for (uint32_t channel = 0; channel < channels; ++channel)
                result[size_t(position + index) * channels + channel] = outputs[channel][index];
        position += count;
        if (pace && position % rate == 0 && position >= rate * 3) {
            const int expected = completedBefore + static_cast<int>((position - rate / 2) / (rate * 2));
            waitFor([&] { return backend.calls.load() >= expected; }, "worker did not complete a core");
        }
        std::this_thread::yield();
    }
    return result;
}

void verify(const std::vector<float>& output, uint32_t channels, int seed, float gain) {
    const uint32_t frames = static_cast<uint32_t>(output.size() / channels);
    for (uint32_t position = 0; position < frames; ++position) {
        for (uint32_t channel = 0; channel < channels; ++channel) {
            const float expected = position < delay ? 0.0f :
                signal(position - delay, channel, seed) * gain;
            require(output[size_t(position) * channels + channel] == expected,
                    "sample or fixed-delay timeline mismatch");
        }
    }
}

void testValidation() {
    FakeBackend backend;
    groove::StreamEngine engine(backend);
    require(!engine.prepare(7999, 1), "accepted low sample rate");
    require(!engine.prepare(192001, 2), "accepted high sample rate");
    require(!engine.prepare(rate, 0), "accepted zero channels");
    require(!engine.prepare(rate, 3), "accepted excess channels");
    require(engine.prepare(192000, 2), "rejected upper sample-rate limit");
    require(engine.latency() == 960000, "wrong upper-limit latency");
    require(engine.prepare(8001, 1), "rejected valid odd sample rate");
    require(engine.latency() == 40005, "wrong odd-rate latency");
    require(engine.prepare(rate, 1), "rejected valid sample rate");
    require(engine.latency() == delay, "wrong latency");
    engine.process(nullptr, nullptr, 0);
}

void testMonitor(float backendGain, int monitor, bool bypass, uint32_t channels) {
    FakeBackend backend(backendGain);
    backend.expectedSeed = 2;
    groove::StreamEngine engine(backend);
    require(engine.prepare(rate, channels), "prepare failed");
    engine.setMonitor(monitor);
    engine.setBypass(bypass);
    engine.setSensitivity(4.0f);
    engine.start();
    engine.start();
    const auto output = render(engine, backend, channels, rate * 8 + 173, 2, true, 0, true);
    const float expectedGain = bypass || monitor == groove::StreamEngine::Original ? 1.0f :
        monitor == groove::StreamEngine::Removed ? 1.0f - backendGain : backendGain;
    verify(output, channels, 2, expectedGain);
    require(backend.valid.load(), "invalid backend window or sensitivity");
    require(engine.status() == groove::StreamEngine::Ready, "cleaned output did not become ready");
}

void testReset() {
    FakeBackend backend;
    groove::StreamEngine engine(backend);
    require(engine.prepare(rate, 2), "prepare failed");
    engine.start();
    render(engine, backend, 2, rate * 7, 1);
    const int completed = backend.calls.load();
    engine.reset();
    require(engine.status() == groove::StreamEngine::Warming, "reset did not warm up");
    verify(render(engine, backend, 2, rate * 7, 9, true, completed), 2, 9, 0.5f);
}

void testInflightReset() {
    FakeBackend backend;
    backend.pause();
    groove::StreamEngine engine(backend);
    require(engine.prepare(rate, 1), "prepare failed");
    engine.start();
    render(engine, backend, 1, rate * 3, 1, false);
    waitFor([&] { return backend.entered.load() == 1; }, "backend was not entered");
    engine.reset();
    backend.release();
    waitFor([&] { return backend.calls.load() == 1; }, "old backend did not return");
    verify(render(engine, backend, 1, rate * 7, 11, true, 1), 1, 11, 0.5f);
}

void testFailure() {
    FakeBackend backend;
    backend.fail.store(true);
    groove::StreamEngine engine(backend);
    require(engine.prepare(rate, 2), "prepare failed");
    engine.start();
    verify(render(engine, backend, 2, rate * 6, 3), 2, 3, 1.0f);
    require(engine.status() == groove::StreamEngine::Unavailable, "backend failure was not visible");
    engine.setMonitor(groove::StreamEngine::Removed);
    const auto removed = render(engine, backend, 2, rate, 4, false);
    for (size_t index = (rate / 200) * 2; index < removed.size(); ++index)
        require(removed[index] == 0.0f, "removed fallback must be silence after switch ramp");
}

void testOverloadAndStop() {
    FakeBackend backend;
    backend.pause();
    groove::StreamEngine engine(backend);
    require(engine.prepare(rate, 1), "prepare failed");
    engine.start();
    const auto output = render(engine, backend, 1, rate * 11, 5, false);
    verify(output, 1, 5, 1.0f);
    require(engine.status() == groove::StreamEngine::Overloaded, "missed deadlines were not visible");
    waitFor([&] { return backend.entered.load() > 0; }, "blocking backend was not entered");
    const auto before = std::chrono::steady_clock::now();
    engine.stop();
    require(std::chrono::steady_clock::now() - before < std::chrono::seconds(1),
            "stop did not cancel backend promptly");
    engine.stop();
}

void testLateResults() {
    FakeBackend backend;
    backend.pause();
    groove::StreamEngine engine(backend);
    require(engine.prepare(rate, 1), "prepare failed");
    engine.start();
    auto initial = render(engine, backend, 1, rate * 3, 6, false);
    waitFor([&] { return backend.entered.load() == 1; }, "late backend was not entered");
    const auto remainder = render(engine, backend, 1, rate * 3, 6, false, 0, false, rate * 3);
    initial.insert(initial.end(), remainder.begin(), remainder.end());
    verify(initial, 1, 6, 1.0f);
    backend.release();
    waitFor([&] { return backend.calls.load() >= 2; }, "late backend did not catch up");
    const auto resumed = render(engine, backend, 1, rate * 2, 7, false);
    for (uint32_t index = 0; index < resumed.size(); ++index) {
        const float original = signal(rate + index, 0, 6);
        require(resumed[index] == original || resumed[index] == original * 0.5f,
                "late result was shifted onto the wrong sample");
        if (index >= rate)
            require(resumed[index] == original * 0.5f, "stale output obstructed recovery");
    }
}

void testLargeSilentBlock() {
    FakeBackend backend;
    groove::StreamEngine engine(backend);
    require(engine.prepare(rate, 2), "prepare failed");
    engine.setMonitor(groove::StreamEngine::Original);
    std::vector<float> left(rate * 6, 1.0f), right(rate * 6, 1.0f);
    float* output[] = {left.data(), right.data()};
    engine.process(nullptr, output, static_cast<int>(left.size()));
    for (size_t index = 0; index < left.size(); ++index)
        require(left[index] == 0.0f && right[index] == 0.0f, "null input was not silence");
}

void testOffline(int monitor, bool bypass, uint32_t channels, bool singleBlock) {
    FakeBackend backend(.25f);
    groove::StreamEngine engine(backend);
    require(engine.prepare(rate, channels, true), "offline prepare failed");
    engine.setMonitor(monitor);
    engine.setBypass(bypass);
    engine.start();
    // Include a partial final core and five seconds of host-supplied tail silence.
    const uint32_t duration = rate * 31 + 173;
    const uint32_t total = duration + delay;
    std::vector<float> buffers[2];
    for (auto& buffer : buffers) buffer.resize(total);
    const float gain = bypass || monitor == groove::StreamEngine::Original ? 1.f :
        monitor == groove::StreamEngine::Removed ? .75f : .25f;
    for (int pass = 0; pass < 2; ++pass) {
        if (pass) engine.reset();
        for (uint32_t channel = 0; channel < channels; ++channel)
            for (uint32_t frame = 0; frame < total; ++frame)
                buffers[channel][frame] = frame < duration ? signal(frame, channel, pass + 1) : 0.f;
        uint32_t offset = 0;
        const uint32_t sizes[] = {1, 257, 8193, 17, 441};
        size_t block = 0;
        while (offset < total) {
            const auto count = std::min(total - offset, singleBlock ? total : sizes[block++ % 5]);
            const float* input[] = {buffers[0].data() + offset, buffers[1].data() + offset};
            float* output[] = {buffers[0].data() + offset, buffers[1].data() + offset};
            require(engine.processOffline(input, output, static_cast<int>(count)), "offline render failed");
            offset += count;
        }
        for (uint32_t channel = 0; channel < channels; ++channel)
            for (uint32_t frame = 0; frame < total; ++frame) {
                const float expected = frame < delay ? 0.f : signal(frame - delay, channel, pass + 1) * gain;
                require(buffers[channel][frame] == expected, "offline sample, reset or final-tail mismatch");
            }
        require(engine.status() == groove::StreamEngine::Ready, "offline status not ready");
    }
}

void testOfflineFailure() {
    FakeBackend backend;
    backend.fail.store(true);
    groove::StreamEngine engine(backend);
    require(engine.prepare(rate, 1, true), "offline prepare failed");
    engine.start();
    std::vector<float> audio(rate * 9, .5f), output(audio.size(), 1.f);
    const float* input[] = {audio.data()};
    float* outputs[] = {output.data()};
    require(!engine.processOffline(input, outputs, static_cast<int>(audio.size())), "offline failure was hidden");
    require(engine.status() == groove::StreamEngine::Unavailable, "offline failure status");
    for (float sample : output) require(sample == 0, "failed offline block was not silenced");
    backend.fail.store(false);
    require(!engine.processOffline(input, outputs, 1), "failed offline export silently recovered");
}

void testOfflineTimeout() {
    FakeBackend backend;
    backend.pause();
    groove::StreamEngine engine(backend);
    require(engine.prepare(rate, 1, true, 20), "timeout prepare failed");
    engine.start();
    std::vector<float> audio(rate * 9, .5f);
    const float* input[] = {audio.data()};
    float* output[] = {audio.data()};
    const auto before = std::chrono::steady_clock::now();
    require(!engine.processOffline(input, output, static_cast<int>(audio.size())), "stalled export succeeded");
    require(std::chrono::steady_clock::now() - before < std::chrono::seconds(1), "timeout not bounded");
    require(backend.cancellations.load() > 0, "timeout did not cancel blocked backend");
    for (float sample : audio) require(sample == 0, "timeout left partial output");
}

void testFiniteAudio() {
    FakeBackend backend;
    groove::StreamEngine engine(backend);
    require(engine.prepare(rate, 1), "finite audio prepare failed");
    std::vector<float> audio(rate * 6, .25f);
    audio[0] = std::numeric_limits<float>::quiet_NaN();
    audio[1] = std::numeric_limits<float>::infinity();
    audio[2] = -std::numeric_limits<float>::infinity();
    const float* input[] = {audio.data()};
    float* output[] = {audio.data()};
    engine.process(input, output, static_cast<int>(audio.size()));
    for (uint32_t index = 0; index < audio.size(); ++index) {
        const float expected = index < delay + 3 ? 0.f : .25f;
        require(audio[index] == expected, "non-finite input escaped sanitized dry fallback");
    }
    require(engine.prepare(rate, 1, true), "offline finite prepare failed");
    engine.start();
    audio[0] = std::numeric_limits<float>::quiet_NaN();
    require(!engine.processOffline(input, output, 16), "offline non-finite input accepted");
    for (int index = 0; index < 16; ++index) require(audio[index] == 0, "invalid offline block not silenced");
}

void testInvalidBackendAudio() {
    FakeBackend backend;
    backend.invalidOutput = true;
    groove::StreamEngine engine(backend);
    require(engine.prepare(rate, 1, true), "bad backend prepare failed");
    engine.start();
    std::vector<float> audio(rate * 6, .25f);
    const float* input[] = {audio.data()};
    float* output[] = {audio.data()};
    require(!engine.processOffline(input, output, static_cast<int>(audio.size())), "non-finite backend accepted");
    for (float sample : audio) require(sample == 0, "invalid backend output escaped export");
}

void testSensitivityCapture() {
    FakeBackend backend;
    backend.pause();
    groove::StreamEngine engine(backend);
    require(engine.prepare(rate, 1), "sensitivity prepare failed");
    engine.setSensitivity(.2f);
    engine.start();
    render(engine, backend, 1, rate * 3, 1, false);
    waitFor([&] { return backend.entered.load() == 1; }, "first sensitivity job not started");
    engine.setSensitivity(.4f);
    render(engine, backend, 1, rate * 2, 1, false, 0, false, rate * 3);
    engine.setSensitivity(.9f);
    backend.release();
    waitFor([&] { return backend.calls.load() >= 2; }, "queued sensitivity job did not finish");
    require(backend.lastSensitivity.load() == .4f, "sensitivity changed with worker scheduling");
}

void testSwitchSmoothing() {
    FakeBackend backend;
    groove::StreamEngine engine(backend);
    require(engine.prepare(rate, 1, true), "switch prepare failed");
    engine.start();
    std::vector<float> audio(rate * 6, .25f);
    const float* input[] = {audio.data()};
    float* output[] = {audio.data()};
    require(engine.processOffline(input, output, static_cast<int>(audio.size())), "switch warmup failed");
    const int ramp = rate / 200;
    const auto transition = [&](int monitor, bool bypass, float from, float to) {
        engine.setMonitor(monitor);
        engine.setBypass(bypass);
        std::fill(audio.begin(), audio.end(), .25f);
        require(engine.processOffline(input, output, ramp + 16), "switch render failed");
        float previous = from;
        for (int index = 0; index < ramp; ++index) {
            require(std::abs(audio[index] - previous) < .004f, "monitor switch stepped abruptly");
            previous = audio[index];
        }
        for (int index = ramp - 1; index < ramp + 16; ++index)
            require(audio[index] == to, "monitor switch did not settle exactly");
    };
    transition(groove::StreamEngine::Original, false, .125f, .25f);
    transition(groove::StreamEngine::Removed, false, .25f, .125f);
    transition(groove::StreamEngine::Removed, true, .125f, .25f);
    transition(groove::StreamEngine::Cleaned, false, .25f, .125f);
}

} // namespace

int main() {
    try {
        testValidation();
        testMonitor(0.5f, groove::StreamEngine::Original, false, 2);
        testMonitor(0.5f, groove::StreamEngine::Cleaned, false, 2);
        testMonitor(0.5f, groove::StreamEngine::Removed, false, 2);
        testMonitor(1.0f, groove::StreamEngine::Cleaned, false, 1);
        testMonitor(1.0f, groove::StreamEngine::Removed, false, 1);
        testMonitor(0.5f, groove::StreamEngine::Removed, true, 1);
        testReset();
        testInflightReset();
        testFailure();
        testOverloadAndStop();
        testLateResults();
        testLargeSilentBlock();
        testOffline(groove::StreamEngine::Cleaned, false, 2, true);
        testOffline(groove::StreamEngine::Removed, false, 2, false);
        testOffline(groove::StreamEngine::Original, false, 1, false);
        testOffline(groove::StreamEngine::Removed, true, 1, true);
        testOfflineFailure();
        testOfflineTimeout();
        testFiniteAudio();
        testInvalidBackendAudio();
        testSensitivityCapture();
        testSwitchSmoothing();
        std::cout << "stream tests passed\n";
        return EXIT_SUCCESS;
    } catch (const std::exception& error) {
        std::cerr << "stream test failed: " << error.what() << '\n';
        return EXIT_FAILURE;
    }
}
