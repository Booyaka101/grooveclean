#include "StreamEngine.h"
#include "WorkerProcess.h"
#include "Editor.h"
#include "base/source/fstreamer.h"
#include "base/source/fstring.h"
#include "pluginterfaces/vst/ivstparameterchanges.h"
#include "pluginterfaces/vst/ivstprocesscontext.h"
#include "public.sdk/source/main/pluginfactory.h"
#include "public.sdk/source/vst/vstaudioeffect.h"
#include "public.sdk/source/vst/vsteditcontroller.h"
#include <algorithm>
#include <atomic>
#include <cmath>
#include <cstring>

namespace groove {
using namespace Steinberg;
using namespace Steinberg::Vst;

const FUID processorId(0x89BE7683, 0x44E24DE2, 0xB786035B, 0xAF9C0512);
const FUID controllerId(0x5949C018, 0x857D4659, 0x9EB70593, 0xE60EBAF3);
enum ParameterIds : ParamID { Sensitivity = 0, Monitor = 1, Bypass = 2, Health = 3 };

struct Settings {
    double sensitivity = 0.5;
    double monitor = 0;
    double bypass = 0;
};

bool readSettings(IBStream* state, Settings& settings) {
    if (!state) return false;
    IBStreamer stream(state, kLittleEndian);
    int32 version = 0;
    Settings value;
    if (!stream.readInt32(version) || version != 1 ||
        !stream.readDouble(value.sensitivity) || !stream.readDouble(value.monitor) ||
        !stream.readDouble(value.bypass)) return false;
    for (double number : {value.sensitivity, value.monitor, value.bypass})
        if (!std::isfinite(number) || number < 0 || number > 1) return false;
    settings = value;
    return true;
}

class Processor final : public AudioEffect {
public:
    Processor() : engine_(worker_) { setControllerClass(controllerId); }
    ~Processor() override { engine_.stop(); }
    static FUnknown* create(void*) { return static_cast<IAudioProcessor*>(new Processor); }

    tresult PLUGIN_API initialize(FUnknown* context) override {
        const auto result = AudioEffect::initialize(context);
        if (result != kResultOk) return result;
        addAudioInput(STR16("Input"), SpeakerArr::kStereo);
        addAudioOutput(STR16("Output"), SpeakerArr::kStereo);
        return kResultOk;
    }

    tresult PLUGIN_API setBusArrangements(SpeakerArrangement* inputs, int32 numInputs,
                                         SpeakerArrangement* outputs, int32 numOutputs) override {
        if (numInputs != 1 || numOutputs != 1 || !inputs || !outputs ||
            inputs[0] != outputs[0] ||
            (inputs[0] != SpeakerArr::kMono && inputs[0] != SpeakerArr::kStereo))
            return kResultFalse;
        channels_ = inputs[0] == SpeakerArr::kMono ? 1 : 2;
        return AudioEffect::setBusArrangements(inputs, numInputs, outputs, numOutputs);
    }

    tresult PLUGIN_API canProcessSampleSize(int32 size) override {
        return size == kSample32 ? kResultTrue : kResultFalse;
    }

    tresult PLUGIN_API setupProcessing(ProcessSetup& setup) override {
        if (setup.symbolicSampleSize != kSample32 ||
            !std::isfinite(setup.sampleRate) || setup.sampleRate <= 0 ||
            setup.maxSamplesPerBlock <= 0 ||
            (setup.processMode != kRealtime && setup.processMode != kPrefetch && setup.processMode != kOffline))
            return kResultFalse;
        const bool supported = setup.sampleRate >= 8000 && setup.sampleRate <= 192000 &&
                               std::floor(setup.sampleRate) == setup.sampleRate;
        if (setup.processMode == kOffline && !supported) return kResultFalse;
        const auto result = AudioEffect::setupProcessing(setup);
        if (result != kResultOk) return result;
        supportedRate_ = supported;
        offline_ = setup.processMode == kOffline;
        if (supportedRate_) rate_ = static_cast<uint32_t>(setup.sampleRate);
        return result;
    }

    uint32 PLUGIN_API getLatencySamples() override { return supportedRate_ ? rate_ * 5 : 0; }
    uint32 PLUGIN_API getTailSamples() override { return getLatencySamples(); }

    tresult PLUGIN_API setActive(TBool active) override {
        if (active && supportedRate_) {
            if (!engine_.prepare(rate_, channels_, offline_)) return kResultFalse;
            const bool launched = worker_.launch();
            if (offline_ && !launched) return kResultFalse;
            engine_.setSensitivity(static_cast<float>(sensitivity_.load()));
            engine_.setMonitor(static_cast<int>(std::round(monitor_.load() * 2)));
            engine_.setBypass(bypass_.load() >= 0.5);
            engine_.start();
        } else {
            engine_.stop();
            worker_.close();
        }
        havePosition_ = false;
        return AudioEffect::setActive(active);
    }

    tresult PLUGIN_API setProcessing(TBool) override {
        engine_.reset();
        havePosition_ = false;
        return kResultOk;
    }

    tresult PLUGIN_API process(ProcessData& data) override {
        if ((data.processMode == kOffline) != offline_) return kResultFalse;
        if (data.inputParameterChanges) {
            for (int32 index = 0; index < data.inputParameterChanges->getParameterCount(); ++index) {
                auto* queue = data.inputParameterChanges->getParameterData(index);
                if (!queue || queue->getPointCount() == 0) continue;
                int32 offset = 0;
                ParamValue value = 0;
                if (queue->getPoint(queue->getPointCount() - 1, offset, value) != kResultTrue ||
                    !std::isfinite(value)) continue;
                value = std::clamp(value, 0.0, 1.0);
                switch (queue->getParameterId()) {
                case Sensitivity:
                    sensitivity_.store(value);
                    engine_.setSensitivity(static_cast<float>(value));
                    break;
                case Monitor:
                    monitor_.store(value);
                    engine_.setMonitor(static_cast<int>(std::round(value * 2)));
                    break;
                case Bypass:
                    bypass_.store(value);
                    engine_.setBypass(value >= 0.5);
                    break;
                }
            }
        }
        if (data.numSamples == 0) return kResultOk;
        if (data.numSamples < 0 || !data.inputs || !data.outputs ||
            data.symbolicSampleSize != kSample32 || data.numInputs != 1 || data.numOutputs != 1 ||
            data.inputs[0].numChannels != channels_ || data.outputs[0].numChannels != channels_ ||
            !data.inputs[0].channelBuffers32 || !data.outputs[0].channelBuffers32)
            return kResultFalse;
        // Offline streams are delimited by setProcessing, not transport flags.
        // Hosts may stop or freeze the project clock while still delivering a tail.
        if (!offline_ && data.processContext) {
            const bool playing = (data.processContext->state & ProcessContext::kPlaying) != 0;
            const auto position = data.processContext->projectTimeSamples;
            // Stopping can begin host-supplied tail delivery. Preserve that audio;
            // restarting playback or seeking while playing starts a new stream.
            if (havePosition_ && playing && (!wasPlaying_ || position != expectedPosition_))
                engine_.reset();
            wasPlaying_ = playing;
            expectedPosition_ = position + data.numSamples;
            havePosition_ = true;
        } else havePosition_ = false;

        bool processed = true;
        if (supportedRate_) {
            if (offline_) {
                processed = engine_.processOffline(data.inputs[0].channelBuffers32,
                                                    data.outputs[0].channelBuffers32, data.numSamples);
            } else {
                engine_.process(data.inputs[0].channelBuffers32, data.outputs[0].channelBuffers32,
                                data.numSamples);
            }
        } else {
            // VST hosts can negotiate arbitrary positive rates. Keep those sessions
            // usable, but visibly unavailable, without allocating unbounded buffers
            // or quietly running the model at a different rate.
            const bool removed = monitor_.load() >= .75 && bypass_.load() < .5;
            for (int32 channel = 0; channel < channels_; ++channel) {
                auto* output = data.outputs[0].channelBuffers32[channel];
                const auto* input = data.inputs[0].channelBuffers32[channel];
                if (!output) continue;
                for (int32 frame = 0; frame < data.numSamples; ++frame)
                    output[frame] = removed || !input || !std::isfinite(input[frame]) ? 0 : input[frame];
            }
        }
        data.outputs[0].silenceFlags = 0;
        if (data.outputParameterChanges) {
            int32 index = 0;
            if (auto* queue = data.outputParameterChanges->addParameterData(Health, index))
                queue->addPoint(0, supportedRate_ ? engine_.status() / 3.0 : 1.0, index);
        }
        return processed ? kResultOk : kResultFalse;
    }

    tresult PLUGIN_API setState(IBStream* state) override {
        Settings value;
        if (!readSettings(state, value)) return kResultFalse;
        sensitivity_.store(value.sensitivity);
        monitor_.store(value.monitor);
        bypass_.store(value.bypass);
        engine_.setSensitivity(static_cast<float>(value.sensitivity));
        engine_.setMonitor(static_cast<int>(std::round(value.monitor * 2)));
        engine_.setBypass(value.bypass >= 0.5);
        return kResultOk;
    }

    tresult PLUGIN_API getState(IBStream* state) override {
        if (!state) return kResultFalse;
        IBStreamer stream(state, kLittleEndian);
        return stream.writeInt32(1) && stream.writeDouble(sensitivity_.load()) &&
               stream.writeDouble(monitor_.load()) && stream.writeDouble(bypass_.load())
            ? kResultOk : kResultFalse;
    }

private:
    WorkerProcess worker_;
    StreamEngine engine_;
    static_assert(std::atomic<double>::is_always_lock_free);
    std::atomic<double> sensitivity_{0.5}, monitor_{0}, bypass_{0};
    uint32_t rate_ = 44100;
    bool supportedRate_ = true;
    bool offline_ = false;
    int32 channels_ = 2;
    int64 expectedPosition_ = 0;
    bool havePosition_ = false;
    bool wasPlaying_ = false;
};

class Controller final : public EditController {
public:
    static FUnknown* create(void*) { return static_cast<IEditController*>(new Controller); }
    IPlugView* PLUGIN_API createView(FIDString name) override {
        return name && !std::strcmp(name, ViewType::kEditor) ? createEditor(this) : nullptr;
    }
    tresult PLUGIN_API initialize(FUnknown* context) override {
        const auto result = EditController::initialize(context);
        if (result != kResultOk) return result;
        parameters.addParameter(STR16("Sensitivity"), nullptr, 0, 0.5,
                                ParameterInfo::kCanAutomate, Sensitivity);
        auto* monitor = new StringListParameter(STR16("Listen"), Monitor, nullptr,
                                                ParameterInfo::kIsList);
        monitor->appendString(STR16("Cleaned"));
        monitor->appendString(STR16("Original"));
        monitor->appendString(STR16("Removed"));
        parameters.addParameter(monitor);
        parameters.addParameter(STR16("Bypass"), nullptr, 1, 0,
                                ParameterInfo::kCanAutomate | ParameterInfo::kIsBypass, Bypass);
        auto* health = new StringListParameter(STR16("Processing"), Health, nullptr,
                            ParameterInfo::kIsList | ParameterInfo::kIsReadOnly);
        health->appendString(STR16("Warming up"));
        health->appendString(STR16("Ready"));
        health->appendString(STR16("Overload detected: original fallback"));
        health->appendString(STR16("Worker or sample rate unavailable"));
        parameters.addParameter(health);
        return kResultOk;
    }

    tresult PLUGIN_API setComponentState(IBStream* state) override {
        Settings settings;
        if (!readSettings(state, settings)) return kResultFalse;
        setParamNormalized(Sensitivity, settings.sensitivity);
        setParamNormalized(Monitor, settings.monitor);
        setParamNormalized(Bypass, settings.bypass);
        return kResultOk;
    }
};
} // namespace groove

using namespace Steinberg;
using namespace Steinberg::Vst;
BEGIN_FACTORY_DEF("GrooveClean", "https://github.com/Booyaka101/grooveclean", "cbosch101@gmail.com")
DEF_CLASS2(INLINE_UID_FROM_FUID(groove::processorId), PClassInfo::kManyInstances,
           kVstAudioEffectClass, "GrooveClean", 0, "Fx|Restoration", "0.1.0",
           kVstVersionString, groove::Processor::create)
DEF_CLASS2(INLINE_UID_FROM_FUID(groove::controllerId), PClassInfo::kManyInstances,
           kVstComponentControllerClass, "GrooveClean Controller", 0, "", "0.1.0",
           kVstVersionString, groove::Controller::create)
END_FACTORY
