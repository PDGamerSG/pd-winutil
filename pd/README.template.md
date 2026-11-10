# Pallab Das Windows Utility

[![PD build and upstream sync](https://github.com/PDGamerSG/pd-winutil/actions/workflows/pd-update.yml/badge.svg)](https://github.com/PDGamerSG/pd-winutil/actions/workflows/pd-update.yml)
[![Latest release](https://img.shields.io/github/v/release/PDGamerSG/pd-winutil)](https://github.com/PDGamerSG/pd-winutil/releases/latest)

<img src="pd/logo.svg" alt="PD" width="96" />

Windows app installation, tweaks, repairs, update settings and ISO tools,
maintained by **Pallab Das**. Based on [WinUtil by Chris Titus Tech and its
contributors](https://github.com/ChrisTitusTech/winutil), with a PD terminal
banner and application logo.

## Run on Windows

Open **PowerShell or Terminal as Administrator** and run:

```powershell
irm https://github.com/PDGamerSG/pd-winutil/releases/latest/download/winutil.ps1 | iex
```

This launches this fork's latest tested release. Releases are unsigned.
Review the settings before applying system changes. Windows 11 is the
upstream-supported platform.

For a repeatable setup using an upstream preset:

```powershell
& ([ScriptBlock]::Create((irm https://github.com/PDGamerSG/pd-winutil/releases/latest/download/winutil.ps1))) -Preset Standard
```

Available presets: `Standard`, `Minimal`, `Advanced`. You can also export your
selections and use `-Config 'C:\path\to\settings.json'`.

## Build from the complete source

```powershell
git clone https://github.com/PDGamerSG/pd-winutil.git
cd pd-winutil
.\Compile.ps1
.\winutil.ps1
```

`winutil.ps1` is generated and is distributed through releases, not committed
to the repository. All upstream functions, configurations, tests, documentation
and Git history are retained.

## Automatic upstream updates

[PD build and upstream sync](https://github.com/PDGamerSG/pd-winutil/actions/workflows/pd-update.yml)
checks upstream `main` daily at **03:17 UTC (08:47 IST)**. It merges updates,
reapplies branding, compiles and parses the script, and runs the sync tests and
upstream Windows tests before pushing and publishing a new release.

Merge conflicts or failing tests stop the update and preserve the previous
release. Run the workflow manually to retry or check for updates immediately.
The exact upstream commit is recorded in [pd/upstream.json](pd/upstream.json).
GitHub schedules can be delayed or disabled after prolonged inactivity; see
[maintenance and integration instructions](docs/PD-MAINTENANCE.md).

## Credits and license

The original utility was created by **Chris Titus Tech / CT Tech Group LLC**
and the [WinUtil contributors](https://github.com/ChrisTitusTech/winutil/graphs/contributors).
Their Windows functionality is the foundation of this fork. UI and runspace
credits remain in the application. Pallab Das maintains this fork's branding,
integration and update automation; this fork is independent of the upstream team.

The original **MIT license and copyright notice are preserved** in [LICENSE](LICENSE).
Additional third-party notices, including documentation component licenses,
remain with their files. The [upstream README snapshot](docs/upstream/README.md)
retains upstream resources and sponsorship information.

- [Report an issue with this fork](https://github.com/PDGamerSG/pd-winutil/issues)
- [Upstream documentation](https://winutil.christitus.com/)
- [Maintaining this fork and adding the next repository](docs/PD-MAINTENANCE.md)
