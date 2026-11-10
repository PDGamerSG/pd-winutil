# Maintaining Pallab Das Windows Utility

This is an independent public fork of
[ChrisTitusTech/winutil](https://github.com/ChrisTitusTech/winutil), maintained by
Pallab Das at [PDGamerSG/pd-winutil](https://github.com/PDGamerSG/pd-winutil).
All upstream source, configuration, tests, documentation and Git history are
copied. The original MIT notice and other third-party licenses remain intact.

## What is customized

- The utility's terminal banner spells PD and displays Pallab Das.
- The WPF window title, application logo, taskbar overlay and About dialog
  identify this fork. Existing UI and runspace credits are retained.
- Administrator relaunch, exported `-Config` commands, development launcher,
  handwritten launch documentation and Config Builder use this fork's releases.
- Internal WinUtil function names, selection keys, presets and settings paths
  remain compatible with upstream. Normal Windows system behavior is inherited.

Original author names in attribution, sponsor links, legal notices and external
dependencies are intentional. For example, the optional CTT PowerShell profile
still installs the actual upstream profile from its original repository.
Launching PD WinUtil shows the PD banner; this fork does not change every
unrelated terminal session or silently install a system-wide PowerShell profile.

The documentation site's source is copied, but a new hosted website/domain is
not provisioned. Existing upstream reference links remain usable. The original
title-screen image and documentation copyright are upstream assets; the fork's
README uses `pd/logo.svg` instead. The docs site still requires Docker tooling
as described in `AGENTS.md`.

## Automatic updates

`.github/workflows/pd-update.yml` runs on main pushes, pull requests, manual
dispatch and daily at 03:17 UTC (08:47 IST). For main/manual/scheduled runs:

1. Fetch upstream main, using a full-history checkout.
2. Prepare an ordinary Git merge. Resolve only the generated root README
   from `pd/README.template.md`; source conflicts stop the update.
3. Reapply `pd/apply_branding.py`, save the exact upstream commit to
   `pd/upstream.json`, and archive the untouched upstream README under
   `docs/upstream/README.md`.
4. Test branding and merge behavior, compile, parse with PowerShell 7 and
   Windows PowerShell 5.1, render the PD WPF logo, and run upstream's Pester suite.
5. Commit and push the passing candidate, then create a uniquely tagged release
   containing `winutil.ps1`, its SHA-256 checksum, `LICENSE` and `upstream.json`.

Pull requests are checked without pushing or releasing. Rechecking the same
source commit does not publish another release. Failed builds and conflicts
never publish; the last successful release remains the launch target.
Passing tests do not guarantee every upstream bug is fixed, especially for
machine-specific Windows and ISO operations.

The workflow uses the built-in repository token with Contents write permission;
no custom PAT, upstream signing certificate or `AUTO_MERGE` secret is needed.
Releases are unsigned. Copied upstream maintenance workflows are disabled on this
fork; use **PD build and upstream sync** to build and publish this product.

GitHub schedules run on the default branch, may be delayed, and may be disabled
after 60 days of repository inactivity. GitHub Actions must remain enabled. If
needed, re-enable this workflow under Actions and use **Run workflow**. Hosting
this copy elsewhere does not by itself run the GitHub schedule.

## Local maintenance

Python 3.10+ is used only for source maintenance; the compiled Windows utility
does not require Python. Start from a clean checkout:

```text
git remote add upstream https://github.com/ChrisTitusTech/winutil.git
git fetch --no-tags upstream main
python pd/sync_upstream.py
python -m unittest discover -s pd/tests -v
python pd/apply_branding.py --check
```

If the upstream remote already exists, omit the first command. In PowerShell:

```powershell
.\Compile.ps1
.\pd\Verify-PDWinUtil.ps1
Import-Module Pester -RequiredVersion 5.8.0 -Force
Invoke-Pester -Path 'pester/*.Tests.ps1' -Output Detailed -CI
```

Install Pester 5.8.0 using the command in `AGENTS.md` if needed. The sync tool
prepares changes but deliberately does not commit, push or release them. Commit
only after verification. Do not commit generated `winutil.ps1`.

For branding changes, edit `pd/apply_branding.py`, `pd/README.template.md` and
`pd/logo.svg`, then run `python pd/apply_branding.py`. Edit the template rather
than the generated root README. Keep branding changes separate from functionality
so an upstream conflict can be understood and resolved.

## Resolving an upstream conflict

The sync tool aborts conflicting merges and names the affected source files.
Neither side is silently discarded. In a clean checkout, merge manually:

```text
git fetch upstream main
git merge --no-ff --no-commit upstream/main
```

Resolve each conflict using both the upstream fix and the fork's intended behavior.
Run `python pd/apply_branding.py`, then record provenance with:

```text
python -c "import sys; from pathlib import Path; sys.path.insert(0, 'pd'); from sync_upstream import record_upstream; record_upstream(Path('.'), 'upstream/main')"
```

Run the checks above, commit and push. A failed update is visible in the Actions
run logs. If a release upload fails after a verified main push, retry the workflow.

## Adding the next repository

Supply its repository URL and the features you want exposed. First check its
license and Windows compatibility. Implement the chosen functionality in separate
WinUtil functions and config entries; use the existing job/runspace and UI event
contracts described in `SPEC.md`. Keep third-party attribution with the imported
code and list the new source in the README credits. Add meaningful regression
coverage to the same release gate. A second update remote or plugin system is not
added until the actual integration requires it.
