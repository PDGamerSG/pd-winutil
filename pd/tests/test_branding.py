"""Exercise the branding policy against source inputs, without running tweaks."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


PD_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pd_branding", PD_ROOT / "apply_branding.py")
branding = None
if SPEC and SPEC.loader and Path(SPEC.origin).exists():
    branding = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(branding)


class BrandingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        files = {
            "pd/README.template.md": "# Pallab Das Windows Utility\nUpstream: ChrisTitusTech/winutil\n",
            "scripts/main.ps1": 'Write-Host @"\nCTT\n====Chris Titus Tech=====\n"@\n\n# preserve job queue\n',
            "scripts/start.ps1": '<#\n    Author         : Chris Titus @christitustech\n    Runspace Author: @DeveloperDurp\n    GitHub         : https://github.com/ChrisTitusTech\n#>\n$Host.UI.RawUI.WindowTitle = "WinUtil"\n$url = "https://github.com/ChrisTitusTech/winutil/releases/latest/download/winutil.ps1"\n',
            "xaml/inputXML.xaml": '<Window Title="WinUtil"><Grid Name="WPFMainGrid"/></Window>\n',
            "functions/private/Invoke-WinUtilAssets.ps1": "function Invoke-WinUtilAssets {\n switch ($type) {\n      'logo' {\n        $oldLogo = 'CTT'\n      }\n      'checkmark' { 'preserved' }\n }\n}\n",
            "functions/private/Start-WinUtilUserInterface.ps1": 'Author   : <a href="https://github.com/ChrisTitusTech">@ChrisTitusTech</a>\nUI       : @MyDrift-user\nGitHub   : https://github.com/ChrisTitusTech/winutil\nCurrent sponsors for ChrisTitusTech:\n',
            "functions/public/Invoke-WPFImpex.ps1": "$url = 'https://christitus.com/win'\n",
            "functions/private/Invoke-WinUtilInstallPSProfile.ps1": '$url = "https://github.com/ChrisTitusTech/powershell-profile/raw/main/setup.ps1"\n',
            "windev.ps1": '$latestTag = (Invoke-RestMethod https://api.github.com/repos/ChrisTitusTech/winutil/tags).Name | Select-Object -First 1\n',
            "LICENSE": "MIT License\nCopyright (c) 2022 CT Tech Group LLC\n",
            "docs/src/content/docs/guides/getting-started.mdx": 'Chris Titus Tech\nirm https://christitus.com/win | iex\nhttps://christitus.com/windev\n',
            "docs/src/content/docs/code-reference/tweaks/generated.mdx": "Upstream Chris Titus Tech\n",
        }
        for name, contents in files.items():
            self.write(name, contents)

    def write(self, name, contents):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents.encode())

    def read(self, name):
        return (self.root / name).read_text()

    def apply(self):
        self.assertIsNotNone(branding, "The branding policy has not been implemented")
        return branding.apply(self.root)

    def test_product_launches_and_elevation_use_the_fork(self):
        self.apply()
        self.assertIn("Pallab Das", self.read("scripts/main.ps1"))
        self.assertNotIn("CTT", self.read("scripts/main.ps1"))
        self.assertIn("preserve job queue", self.read("scripts/main.ps1"))
        for path in ("scripts/start.ps1", "functions/public/Invoke-WPFImpex.ps1"):
            self.assertIn("https://github.com/PDGamerSG/pd-winutil/releases/latest/download/winutil.ps1", self.read(path))
        self.assertIn('Title="Pallab Das Windows Utility"', self.read("xaml/inputXML.xaml"))

    def test_repeat_application_changes_nothing_and_keeps_crlf(self):
        self.write("scripts/main.ps1", self.read("scripts/main.ps1").replace("\n", "\r\n"))
        self.apply()
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual([], self.apply())
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})
        self.assertNotIn(b"\n", (self.root / "scripts/main.ps1").read_bytes().replace(b"\r\n", b""))

    def test_preserves_license_dependencies_and_generated_docs(self):
        preserved = ("LICENSE", "functions/private/Invoke-WinUtilInstallPSProfile.ps1", "docs/src/content/docs/code-reference/tweaks/generated.mdx")
        before = {p: (self.root / p).read_bytes() for p in preserved}
        self.apply()
        for path, contents in before.items():
            self.assertEqual(contents, (self.root / path).read_bytes(), path)
        self.assertIn("@DeveloperDurp", self.read("scripts/start.ps1"))
        self.assertIn("@MyDrift-user", self.read("functions/private/Start-WinUtilUserInterface.ps1"))
        self.assertIn("Upstream", self.read("functions/private/Start-WinUtilUserInterface.ps1"))

    def test_new_upstream_documentation_gets_the_fork_launch_command(self):
        self.write("docs/src/content/docs/guides/new.mdx", "Christ Tech Tips\nirm https://christitus.com/win | iex\n")
        self.apply()
        result = self.read("docs/src/content/docs/guides/new.mdx")
        self.assertIn("Pallab Das", result)
        self.assertIn("PDGamerSG/pd-winutil", result)

    def test_launcher_uses_a_published_release_instead_of_inherited_tags(self):
        self.apply()
        result = self.read("windev.ps1")
        self.assertIn("https://api.github.com/repos/PDGamerSG/pd-winutil/releases/latest", result)
        self.assertNotIn("/tags", result)
        self.assertIn(".tag_name", result)

    def test_unknown_banner_layout_fails_before_any_file_is_changed(self):
        self.write("scripts/main.ps1", "# completely new startup\nStart-NewUpstreamUI\n")
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertIsNotNone(branding, "The branding policy has not been implemented")
        with self.assertRaisesRegex(ValueError, "banner"):
            branding.apply(self.root)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_check_mode_detects_drift_without_writing(self):
        self.assertIsNotNone(branding, "The branding policy has not been implemented")
        before = (self.root / "scripts/main.ps1").read_bytes()
        self.assertIn("scripts/main.ps1", branding.apply(self.root, check=True))
        self.assertEqual(before, (self.root / "scripts/main.ps1").read_bytes())


if __name__ == "__main__":
    unittest.main()
