#include "WorkerProcess.h"
#include <cmath>
#include <cstdlib>
#include <iostream>

int main() {
    groove::WorkerProcess worker;
    if (!std::getenv("GROOVECLEAN_PYTHON")) {
        std::cout << "SKIP: set GROOVECLEAN_PYTHON to exercise the Python worker\n";
        return 77;
    }
    if (!worker.launch()) return 1;
    constexpr uint32_t rate = 44100;
    std::vector<float> original(rate * 2);
    for (uint32_t i = 0; i < rate; ++i) {
        const float value = 0.1f * std::sin(i * 440.0 * 6.283185307179586 / rate);
        original[i * 2] = value;
        original[i * 2 + 1] = -value;
    }
    for (float sensitivity : {0.3f, 0.5f, 0.7f}) {
        std::vector<float> cleaned;
        if (!worker.process(original, rate, 2, sensitivity, cleaned) ||
            cleaned.size() != original.size()) return 2;
        for (size_t i = 0; i < cleaned.size(); ++i)
            if (!std::isfinite(cleaned[i]) || std::abs(cleaned[i] - original[i]) > 0.01f) return 3;
    }
    worker.cancel();
    std::vector<float> cancelledOutput;
    if (worker.process(original, rate, 2, .5f, cancelledOutput)) return 4;
    worker.close();
    DWORD before = 0, after = 0;
    if (!GetProcessHandleCount(GetCurrentProcess(), &before)) return 5;
    for (int repeat = 0; repeat < 2; ++repeat) {
        if (!worker.launch()) return 6;
        std::vector<float> cleaned;
        if (!worker.process(original, rate, 2, .5f, cleaned)) return 7;
        worker.close();
    }
    if (!GetProcessHandleCount(GetCurrentProcess(), &after) || before != after) return 8;
    std::cout << "Persistent native/Python worker round-trip passed\n";
    return 0;
}
