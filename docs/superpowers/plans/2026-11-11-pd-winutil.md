# PD WinUtil Implementation Plan

**Goal:** Publish a Pallab Das fork of WinUtil that can incorporate upstream fixes.

**Architecture:** Retain the full Git history, source compiler and Windows
features. Reapply a small branding policy after ordinary upstream merges, then
test the candidate before updating main or the latest release.

**Tech stack:** Windows PowerShell, WPF, Python standard library, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-11-11-pd-winutil-design.md`.

## Constraints

- Preserve `LICENSE`, contributor credits and external dependency URLs.
- Generate `winutil.ps1` with `Compile.ps1`; never commit it.
- Do not edit generated tweak/feature documentation manually.
- Use `PDGamerSG/pd-winutil` for product releases and issue reporting.
- Stop failed/conflicting updates before pushing or publishing.

## Tasks

- [x] Clone the complete upstream repository and read its operating contract.
- [x] Add failing Python tests for branding, unchanged licenses, repeatable
  application and changed-anchor rejection; add real-Git sync fixtures for
  clean merges, README conflicts and source conflicts.
- [x] Implement `pd/apply_branding.py`, `pd/sync_upstream.py`,
  `pd/README.template.md` and `pd/logo.svg`; run the focused tests.
- [x] Apply branding to source: terminal banner, window title, application logo,
  About dialog, elevation/export/development URLs and handwritten launch docs.
- [x] Add `pd/Verify-PDWinUtil.ps1` and `.github/workflows/pd-update.yml` to
  merge, test, compile, record provenance and publish after success.
- [x] Document operation and future integrations in `docs/PD-MAINTENANCE.md`,
  update the project contract, and retain the upstream README snapshot.
- [ ] Compile and parse locally; run focused Pester tests where supported;
  push to the authorized public fork and run Windows verification in Actions.
- [ ] Publish the verified first release, confirm its download and schedule,
  and report remaining platform limitations.
