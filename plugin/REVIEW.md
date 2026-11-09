# VST3 review and repair ledger

Scope: native streaming, host lifecycle/state, worker protocol/process ownership,
editor, regression coverage, build/CI and setup documentation. Local review only;
no PR, publication, installer or real-DAW qualification is implied.

Budget: one inspection pass, two repair/verification rounds. Stop after those rounds
with either verified fixes or explicit remaining blockers.

## Confirmed findings, now fixed

- High: stopping the transport during real-time/offline tail delivery resets pending audio.
- High: rejected offline sample rates mutate the previous negotiated configuration.
- High: non-finite real-time input can reach the delayed-original fallback.
- Medium: the offline timeout covers the whole call instead of stalled progress and
  does not cancel the blocked backend immediately.
- Medium: sensitivity is sampled by the worker, making queued-job settings depend on
  scheduling rather than the input timeline.
- Enhancement: monitor/bypass changes need a short, bounded output transition.
- Coverage: exercise stopped-transport tails, rejected setup, invalid input/output,
  timeout cancellation, sensitivity capture and switch transitions.

## Inspection coverage

Inspected complete native sources/headers, native tests, Python worker/protocol tests,
plugin CMake/workflow and plugin setup guide. Checked SDK buffer and processing-mode
contracts. Existing engine repair/detection algorithms are not being rewritten.

## Verification

Repair round 1: native build/47 SDK checks, portable stream tests and worker tests passed.
The plugin integration test caught an outdated NaN passthrough assertion after sanitization
was introduced. Updated it to require exact finite passthrough and zero for non-finite input.
Round 2 also extends tail coverage to real-time transport stop, not only offline stop.

Final verification completed locally in repair round 2:

- Release build: passed all 47 Steinberg validator tests; no warning/error matches in
  `build/plugin-review-build.log`.
- Native CTest: all three suites passed (stream, actual Python worker, loaded plugin),
  in 30.55 seconds. Missing-worker plugin coverage also passed separately.
- AddressSanitizer: portable streaming suite passed in 3.60 seconds using MSVC x64
  with `/fsanitize=address /Zi /EHsc` and `/INCREMENTAL:NO /DEBUG`. This does not cover
  the complete loaded plugin or Python process under the sanitizer.
- Python: all 410 tests passed. One existing CUDA-discovery warning was emitted.
- Ruff and whitespace checks passed.

Additional lifecycle hardening rejects broken protocol reuse, validates the worker
executable, cleans up exceptional launch paths and cancels only the owned worker/job.
Regression coverage includes cancellation/relaunch, handle cleanup, malformed state,
editor interaction/reattachment, stopped-clock tails and finite audio.

Rebuilt development artifact: `build/plugin/VST3/Release/GrooveClean.vst3`.
The bounded review is complete. No additional repair rounds were started.

## Remaining release gates

- Actual DAW qualification: delay compensation, transport, tail delivery, automation,
  offline bounce and failure handling across supported hosts.
- Installer/runtime packaging, including Python dependencies and model availability.
- Broader listening and sustained performance validation on representative transfers
  and hardware. Five-second latency remains unsuitable for live monitoring.
- UI scaling/DPI and accessibility qualification.
- Remote CI on the exact proposed commit. All results above are local only.

At the end of the initial review, work remained uncommitted and unpublished; no PR,
issue reply or release had been created by that review pass.

## Tester package follow-up

Prepared an experimental x64 ZIP using `plugin/preview/build_package.py` with the
complete native bundle, matching worker wheel and weights, setup/launch scripts,
licenses, source snapshot and SHA-256 manifest. Setup downloads CPU-only PyTorch
2.6.0 and pinned direct dependencies into a new isolated Python 3.11 environment.
It does not persist environment variables or install the plugin automatically.

Two bounded setup attempts: the first exposed Windows PowerShell treating redirected
native stderr as a terminating error; the checked-command wrapper now uses native
exit codes. The second clean setup passed the installed worker/model smoke test.
All three native suites then passed against that isolated CPU runtime in 30.49 seconds.
ZIP file hashes, runtime exclusion, Ruff and staged whitespace checks passed.

Local candidate: `build/preview-local-v2/GrooveClean-VST3-Windows-x64-preview.zip`
(1,278,290 bytes). It is a dirty-source development candidate, not a CI-qualified
public release. The workflow now builds the same package and checks isolated setup;
an exact-commit remote CI run is still required before publishing a tester download.
