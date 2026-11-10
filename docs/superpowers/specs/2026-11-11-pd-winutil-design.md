# Pallab Das Windows Utility

The public fork is `PDGamerSG/pd-winutil`, based on the complete history of
`ChrisTitusTech/winutil`. Its Windows utility displays Pallab Das and a PD
terminal and application logo. Launch, elevation, export and development URLs
must use the fork's releases. The MIT license and third-party author credits
remain intact; the README explicitly credits upstream.

Use upstream's modular sources and compiler. Keep the branding policy in
`pd/apply_branding.py`, with a fork-owned README template and logo. The policy
is idempotent, preserves line endings, and rejects changed structural anchors
before writing. Do not rename internal WinUtil function names, config keys or
settings directories, which would break compatibility. Third-party downloads
and upstream documentation retain their real destinations and attribution.

A daily GitHub Actions workflow fetches upstream main, prepares a normal Git
merge, reapplies branding, compiles and parses the script, and runs the Python
sync tests and upstream Pester suite on Windows. Only a passing candidate is
pushed and published as a new release. Source conflicts fail visibly and
retain the previous release. Only the generated root README may be resolved
automatically from its fork-owned template. Archive the upstream README and
record the precise upstream commit in `pd/upstream.json`.

The workflow also validates pull requests without publishing. It uses the
repository's built-in token; no personal access token or signing secret is
required. Copied upstream maintenance workflows remain available in the copy
but are disabled on this fork. An unsigned release must be described honestly.

No functionality from the second repository is invented before it is supplied.
Keep future additions in separate functions/config entries and commits, follow
the existing WinUtil contracts, and preserve the automated regression gate.

Acceptance: full clone and public fork; PD product surfaces and launch paths;
original license and README credits; repeatable compilation; meaningful sync
tests covering conflicts, idempotence and retained fork functionality; a working
published release and enabled schedule. Windows UI rendering is checked in CI
where practical; this macOS workspace cannot run WPF interactively.
