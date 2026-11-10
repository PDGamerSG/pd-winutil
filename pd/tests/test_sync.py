"""Use real local Git branches to prove upstream updates preserve fork work."""

import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PD_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PD_ROOT))
SPEC = importlib.util.spec_from_file_location("pd_sync", PD_ROOT / "sync_upstream.py")
sync = None
if SPEC and SPEC.loader and Path(SPEC.origin).exists():
    sync = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(sync)


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("scripts/start.ps1", "scripts/main.ps1", "xaml/inputXML.xaml",
                     "functions/private/Invoke-WinUtilAssets.ps1",
                     "functions/private/Start-WinUtilUserInterface.ps1"):
            source = PD_ROOT.parent / name
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
        self.write("LICENSE", "MIT License\nCopyright (c) 2022 CT Tech Group LLC\n")
        self.write("README.md", "# Original upstream README\n")
        self.git("init", "-b", "main")
        self.git("config", "user.name", "PD Sync Test")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.autocrlf", "false")
        self.commit("initial upstream")
        self.git("branch", "upstream")
        self.write("pd/README.template.md", "# Pallab Das Windows Utility\nFork credits\n")
        self.write("README.md", "# Pallab Das Windows Utility\nFork credits\n")
        self.write("functions/private/Invoke-WinUtilExtra.ps1", "function Invoke-WinUtilExtra { 'fork feature' }\n")
        self.commit("fork branding and extra feature")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True, text=True, capture_output=True).stdout.strip()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def commit(self, message):
        self.git("add", "--all")
        self.git("commit", "-m", message)

    def upstream_change(self, path, text):
        self.git("checkout", "upstream")
        self.write(path, text)
        self.commit("upstream change")
        self.git("checkout", "main")

    def prepare(self):
        self.assertIsNotNone(sync, "The upstream sync has not been implemented")
        return sync.prepare(self.root, "upstream")

    def test_merge_keeps_new_upstream_work_and_fork_features(self):
        self.upstream_change("config/new.json", '{"upstream_fix": true}\n')
        upstream_sha = self.git("rev-parse", "upstream")
        self.assertTrue(self.prepare())
        self.assertEqual('{"upstream_fix": true}\n', (self.root / "config/new.json").read_text())
        self.assertIn("fork feature", (self.root / "functions/private/Invoke-WinUtilExtra.ps1").read_text())
        self.assertIn(upstream_sha, (self.root / "pd/upstream.json").read_text())
        self.assertEqual("# Original upstream README\n", (self.root / "docs/upstream/README.md").read_text())
        self.assertEqual("MIT License\nCopyright (c) 2022 CT Tech Group LLC\n", (self.root / "LICENSE").read_text())
        self.commit("verified sync")
        self.assertTrue(self.git("merge-base", "--is-ancestor", "upstream", "HEAD") == "")

    def test_repeat_sync_is_a_noop(self):
        self.prepare()
        self.commit("record initial provenance")
        self.assertFalse(self.prepare())
        self.assertEqual("", self.git("status", "--porcelain"))

    def test_readme_conflict_uses_template_and_archives_upstream(self):
        self.upstream_change("README.md", "# Improved upstream README\nNew setup guidance\n")
        self.prepare()
        self.assertEqual("# Pallab Das Windows Utility\nFork credits\n", (self.root / "README.md").read_text())
        self.assertIn("New setup guidance", (self.root / "docs/upstream/README.md").read_text())
        self.assertEqual("", self.git("diff", "--name-only", "--diff-filter=U"))

    def test_source_conflicts_abort_without_losing_either_side(self):
        self.write("shared.txt", "base\n")
        self.commit("common functionality")
        self.git("branch", "-f", "upstream", "HEAD")
        self.write("shared.txt", "fork functionality\n")
        self.commit("fork edit")
        self.upstream_change("shared.txt", "upstream functionality\n")
        before = self.git("rev-parse", "HEAD")
        self.assertIsNotNone(sync, "The upstream sync has not been implemented")
        with self.assertRaisesRegex(RuntimeError, "shared.txt"):
            sync.prepare(self.root, "upstream")
        self.assertEqual(before, self.git("rev-parse", "HEAD"))
        self.assertEqual("fork functionality\n", (self.root / "shared.txt").read_text())
        self.assertEqual("", self.git("status", "--porcelain"))
        self.assertEqual("upstream functionality", self.git("show", "upstream:shared.txt"))

    def test_dirty_checkout_is_rejected_without_touching_user_work(self):
        self.write("my-notes.txt", "do not discard\n")
        self.assertIsNotNone(sync, "The upstream sync has not been implemented")
        with self.assertRaisesRegex(RuntimeError, "clean"):
            sync.prepare(self.root, "upstream")
        self.assertEqual("do not discard\n", (self.root / "my-notes.txt").read_text())


if __name__ == "__main__":
    unittest.main()
