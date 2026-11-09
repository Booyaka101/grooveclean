# GrooveClean VST3 (experimental)

A Windows x64 restoration-preview plugin using GrooveClean's existing CPU detector and
repair engine. This is a development prototype, not a released or DAW-qualified product.
It does not replace the offline CLI.

## What it does

- Mono or stereo, float32 audio, integer sample rates from 8 to 192 kHz.
- Sensitivity, original/cleaned/removed monitoring, latency-preserving bypass.
- Native Windows editor and host-provided generic parameter controls.
- Fixed **five-second latency**, reported to the host for delay compensation.
- Two-second processing segments with half a second of input context on either side.
- A persistent, CPU-only Python worker isolated from the audio callback.
- Bounded queues, transport-discontinuity invalidation, and aligned original-audio fallback.
- Five-millisecond monitor/bypass crossfades and finite-audio safeguards.
- Session settings saved in versioned plugin state.
- Offline DAW bounce with worker backpressure, exact-result waits and explicit failure.

This is for playing recorded transfers, not live input monitoring. Each worker job captures
sensitivity when its final input-context sample arrives, not whenever the background worker
happens to run. Already-queued windows retain their setting. Listen for several seconds after
moving the control. Monitor and bypass changes use a five-millisecond output crossfade;
steady Original and bypass remain exact delayed passthrough for finite input.
At other positive sample rates, the plugin reports unavailable and passes original audio
with zero latency (or silence in Removed mode). It never rounds the rate or claims to clean it.

The real-time callback does no file/pipe I/O, inference, matrix solving, locking or allocation.
It only moves samples through preallocated queues and the dry delay, with bounded mixing
and safety checks. Background processing can still
compete with other plugins for CPU, so a fast average benchmark is not a dropout guarantee.

## Build

Requires Windows x64, Visual Studio 2022 C++ tools, CMake 3.25+, Git and Python 3.11+.
Use a dedicated Python environment. For example, from the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"

git clone https://github.com/steinbergmedia/vst3sdk.git build/vst3sdk
git -C build/vst3sdk checkout 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0
git -C build/vst3sdk submodule update --init --depth 1 base cmake pluginterfaces public.sdk

cmake -S plugin -B build/plugin -A x64 -DVST3_SDK_ROOT="$PWD/build/vst3sdk"
cmake --build build/plugin --config Release --parallel 2
$env:GROOVECLEAN_PYTHON = "$PWD/.venv/Scripts/python.exe"
ctest --test-dir build/plugin -C Release --output-on-failure
```

The SDK is pinned to VST3 3.8.0 (MIT licensed). No SDK source is vendored and no JUCE
dependency is introduced. The SDK validator runs as part of the plugin build.
The portable streaming tests can also run on Linux:

```sh
cmake -S plugin -B build/plugin -DGROOVECLEAN_BUILD_VST3=OFF
cmake --build build/plugin
ctest --test-dir build/plugin --output-on-failure
```

## Try it in a DAW

For testers without a source checkout, `preview/` contains a test-kit builder,
dedicated-runtime setup, worker smoke check and process-local DAW launcher. The
Windows CI job packages the complete VST3 bundle, preview wheel/model, instructions,
source snapshot and checksums, then tests setup in an isolated Python environment.
The archive does not include Python or its third-party dependencies; setup downloads
them. This remains a manual experimental installation, not a production installer.

1. Set `GROOVECLEAN_PYTHON` to the **absolute path** of the dedicated environment's
   `python.exe`, then launch the DAW from that environment. To use a persistent Windows
   environment variable, set it through Windows Environment Variables and restart the DAW.
   The plugin deliberately does not search PATH for an executable or install dependencies.
2. Copy the complete `build/plugin/VST3/Release/GrooveClean.vst3` bundle to a VST3 directory
   scanned by your DAW, for example `%LOCALAPPDATA%/Programs/Common/VST3/`. Do not copy just
   the DLL inside the bundle. No installation or DAW rescan happens automatically.
3. Insert GrooveClean on a recorded mono/stereo transfer. Turn on host latency compensation.
   Some hosts may require choosing 32-bit plugin processing.
4. Start with sensitivity 0.5. Check **Processing** before trusting the cleaned output.
   Listen to **Removed** to check that musical transients are not being taken away.
5. Real-time recording/bounce and host-negotiated **offline bounce** are supported.
   Offline mode waits for restoration rather than substituting original audio. It is not
   necessarily faster than real time on every CPU. Use `grooveclean clean` when you need
   the full-file CLI's difference/report files.

### Offline bounce and the final buffer

The host must negotiate `kOffline` through VST3 `setupProcessing` before activation.
Switching modes requires deactivation and reactivation. A process call with the wrong
mode is rejected, so a host cannot accidentally make a real-time callback wait.

The five-second latency is unchanged in offline mode. The plugin also reports a
five-second tail. The host must continue providing silent input after the source ends
to drain this buffer, then apply its latency compensation. There is no separate VST3
end-of-file callback; simply stopping process calls cannot flush pending audio.
Stopping the transport does not discard the buffered tail. Offline renders use
`setProcessing` to delimit streams and do not infer resets from host transport clocks,
which may be frozen during bounce. Start a new processing stream for a new offline render
or an offline seek. Real-time playback resets on a seek while playing or a playback restart.

Offline mode uses the same windows, sensitivity and repair path as playback, with bounded
queues. Input backpressure and exact-result waits replace deadline-based fallback. Missing
workers, unsupported sample rates, processing failures and wait timeouts fail the export
instead of claiming an unprocessed render succeeded. A failing process call silences its
entire output block and returns an error; it does not erase any earlier blocks already
written by the host. Discard a failed bounce and fix the cause before reactivating.
Each stalled queue/result wait has a 60-second limit, rather than imposing a total-duration
limit on a large block that is making progress. A timeout cancels this instance's worker
immediately and silences the failing block. Hosts must honour VST3 error
returns; a host that ignores errors can still write an invalid file.

These behaviours are covered by a small test host, including final partial cores, a click
at the end of a transfer, fast input, in-place buffers and deliberate worker failure.
They still need qualification in actual DAWs, especially host-specific tail handling.

During real-time playback, if the worker fails or a deadline is missed, cleaned output falls back to delayed original
audio and removed output is zero for those frames. This preserves timing, not restoration.
It must not be mistaken for a successfully cleaned render. Processing status distinguishes
warmup, ready, overload and unavailable. Worker failures require deactivating/reactivating
the plugin after fixing configuration. There are no automatic process-restart loops.
Recent overloads remain visible for at least a second so a brief fallback is not hidden
between UI refreshes. Processing status is not an export-quality certificate.
Non-finite input is replaced by silence during real-time playback and reported unavailable
through its delayed output interval. Offline mode rejects non-finite input instead. Invalid
worker output never enters the result queue. These checks do not clamp valid audio to full
scale or promise protection against every audible fault.

Worker stderr is written to a unique `gcv*.tmp` file in the Windows temporary directory;
its exact location is also emitted through `OutputDebugString`. A missing module, wrong
environment or missing weights should be visible there. No audio is written to that log.
Only the worker process and descendants in this instance's owned job are terminated when
it deactivates. Broken protocol streams are not reused. Native tests also check cancellation,
relaunch and Windows handle cleanup.

## Quality and release gates

The worker uses the complete detector event API, including impulse evidence and clipping
checks, and the existing LSAR repair with the default 20 ms maximum width. It does not
replace detection with a raw probability threshold or use a smaller/quantised model.

The shorter analysis windows, zero-padded stream start, floating-point DAW input and fixed
segment boundaries mean **plugin output is not guaranteed bit-identical to offline output**.
No claim of equal listening quality is made until boundary and real-transfer comparisons
have been completed. The CLI's integer-file reconstruction guarantee is not a plugin claim.

Before a release, require:

- Existing Python regression gates, worker protocol tests, native stream tests and SDK validator.
- Measured boundary-click and dense-damage comparisons against the offline pipeline.
- Real-time testing at 44.1/48/96/192 kHz on representative CPUs, with other plugins running.
- DAW checks for mono/stereo, variable blocks, seek/loop/reset, bypass and state restoration.
- Verification that latency compensation and real-time/offline bounce include the processing tail.
- UI/DPI/accessibility checks and a tested installer/runtime distribution strategy.

AU, macOS/Linux transport, GPU inference, sample-accurate sensitivity
automation, cached auditioning, per-click undo and file-report export are not implemented.

## Initial timing evidence

On an i9-14900K, using two CPU threads and the first three seconds of the bundled worn
78 transfer, three measured repetitions after warmup gave these worker-only times:

| Stereo sample rate | Median | Maximum |
| --- | --- | --- |
| 44.1 kHz | 439 ms | 503 ms |
| 48 kHz | 1175 ms | 1183 ms |
| 96 kHz | 1230 ms | 1231 ms |
| 192 kHz | 1469 ms | 1484 ms |

This is why the prototype uses two-second output jobs, not one-second jobs. Five seconds
of latency gives room for the 2.5 seconds of required incoming audio plus computation and
scheduling. These are not deadline guarantees: IPC/startup are excluded, the machine is
high-end, and other damage or DAW CPU contention can cost more. Reproduce on your machine:

```powershell
.\.venv\Scripts\python.exe plugin/bench_worker.py tests/data/excerpt78.flac
```

Synthetic five-sample clicks crossing both two-second output seams are also tested at
44.1/48/96/192 kHz against the offline block pipeline. That checks a narrow boundary
regression, not general quality equivalence or a fresh blind evaluation.

The bounded review findings, verification results and remaining release gates are recorded
in [`REVIEW.md`](REVIEW.md).
