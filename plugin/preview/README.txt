GrooveClean VST3 experimental Windows x64 test kit

This is an unsigned development preview, not a stable release. Back up your
session, use a disposable project and keep your original audio. Do not replace
your production restoration workflow or overwrite source recordings with it.

REQUIREMENTS
Windows 10 22H2 x64 or later, Python 3.11 x64 (python.org), an internet connection
for setup, and a 64-bit VST3 host. Start with Cubase Pro 13. Cubase 5 / 32-bit VST2
is not supported. FL Studio 12 compatibility has not been established.
The Microsoft Visual C++ 2015-2022 x64 runtime may be required:
https://aka.ms/vs/17/release/vc_redist.x64.exe
No Visual Studio, compiler, Git or GPU is needed.

SETUP
1. Extract the complete ZIP to a permanent, writable folder, for example
   C:\Users\YourName\GrooveClean-Preview. Do not run scripts from inside the ZIP.
   Keep this folder in place after setup: the Python runtime is not relocatable.
2. Install Python 3.11 x64 from python.org, including its Python launcher.
3. Review Setup.ps1, then open PowerShell in this extracted folder and run:
     powershell -NoProfile -ExecutionPolicy Bypass -File .\Setup.ps1
   This execution-policy override applies only to that PowerShell process.
   It creates a dedicated runtime here, installs CPU PyTorch and dependencies
   from the official PyTorch index and PyPI, then installs the BUNDLED preview
   wheel, including the model. Do not install the public grooveclean 1.4.0 wheel
   instead: it does not contain this preview worker. Downloads can be hundreds
   of MB; allow several minutes and a few GB of free disk space.
   No admin rights, persistent environment changes or automatic DAW launch.
   The worker/model smoke test must pass before continuing.
4. Close your DAW completely. Copy the whole GrooveClean.vst3 FOLDER to:
     C:\Program Files\Common Files\VST3\GrooveClean.vst3
   Windows may ask for admin approval for this copy. Do not copy just the DLL
   inside it, or overwrite another GrooveClean installation. A per-user VST3
   folder is also possible if your particular host supports it.
5. Launch the DAW from this folder with its actual full executable path:
     powershell -NoProfile -ExecutionPolicy Bypass -File .\Launch-DAW.ps1 -Daw "C:\Path\To\Cubase13.exe"
   The script sets GROOVECLEAN_PYTHON only for the launched process. Always
   close an already-running DAW first, otherwise its old environment may win.
   Rescan plugins using the host's plugin manager if needed.

FIRST TEST
Use a recorded mono/stereo transfer at 44.1 or 48 kHz. Select 32-bit float
processing in the DAW if it offers a 32/64-bit processing choice. Enable plugin
delay compensation, insert GrooveClean and start sensitivity at 0.5.

There is FIVE SECONDS of reported latency: this is not for live monitoring.
Allow several seconds after changing sensitivity. Check Processing status:
Warming is startup, Ready indicates results are arriving, Overloaded means
some audio fell back to delayed original, and Unavailable means not cleaning.
Audition Original, Cleaned and Removed. Removed should contain unwanted damage,
not musical transients. Check bypass and save/reopen the disposable project.
Try stop/start, seeking and looping. Test offline export separately and listen
to the beginning AND end. Allow at least five seconds of silence after the
source to drain processing; host compensation/tail handling is not qualified.
Discard any failed export. A successful-looking export is not a quality guarantee.
Do not assume preview output matches the full-file CLI exactly.

FEEDBACK
Reply at https://github.com/Booyaka101/grooveclean/issues/11 with:
- Windows and DAW version, CPU, sample rate and audio buffer size.
- Whether setup, plugin scan, editor and Processing status work.
- Whether sensitivity/Removed help find the right setting.
- Dropouts, clicks at segment boundaries, overloads or lost end-of-file audio.
- Offline export, transport and saved-session behaviour.
- Reproduction steps and installed-runtime.txt if a problem occurs.
Worker diagnostics are the newest gcv*.tmp files in your Windows TEMP folder.
Review logs before sharing. Share audio only if you have the rights to do so.

UNINSTALL
Close the DAW. Remove only the GrooveClean.vst3 folder you copied and this
extracted test-kit folder. Setup does not modify your existing Python installs
or persistently configure Windows. Other Python/VC runtime installs are separate.

BUILD DETAILS
manifest.json identifies the source and SHA-256 of included files. source.zip
contains the corresponding project source snapshot. Third-party Python packages
are downloaded during setup, not bundled. requirements.txt pins direct worker
dependencies; transitive packages are recorded in installed-runtime.txt.
LICENSE, CREDITS.md and THIRD-PARTY.txt contain licensing information.
