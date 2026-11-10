"""Reapply the fork's presentation after an upstream merge (standard library only)."""

import argparse
from pathlib import Path
import re


REPOSITORY = "PDGamerSG/pd-winutil"
RELEASE_URL = f"https://github.com/{REPOSITORY}/releases/latest/download/winutil.ps1"
DEV_URL = f"https://raw.githubusercontent.com/{REPOSITORY}/main/windev.ps1"
PRODUCT = "Pallab Das Windows Utility"
LOGO_PATH = (
    "F0 M6,20 H29 C41,20 48,28 48,40 C48,52 41,60 29,60 H18 V80 H6 Z "
    "M18,31 V49 H28 C34,49 36,46 36,40 C36,34 34,31 28,31 Z "
    "M55,20 H73 C89,20 96,30 96,50 C96,70 89,80 73,80 H55 Z "
    "M67,32 V68 H73 C81,68 84,62 84,50 C84,38 81,32 73,32 Z"
)
BANNER = '''# PD-BANNER-BEGIN
Write-WinUtilHost @"
 PPPPPP    DDDDDD
 PP   PP   DD   DD
 PPPPPP    DD   DD
 PP        DD   DD
 PP        DDDDDD

 Pallab Das Windows Utility
"@ -ForegroundColor Cyan
# PD-BANNER-END'''
LOGO = f'''      'logo' {{
          # PD-LOGO-BEGIN
          $pdPath = New-Object Windows.Shapes.Path
          $pdPath.Data = [Windows.Media.Geometry]::Parse("{LOGO_PATH}")
          $pdPath.Fill = [System.Windows.Media.BrushConverter]::new().ConvertFromString("#0567ff")
          $canvas.Children.Add($pdPath) | Out-Null
          # PD-LOGO-END
      }}
'''


def replace_block(text, pattern, replacement, description):
    result, count = re.subn(pattern, lambda _: replacement, text, flags=re.MULTILINE | re.DOTALL)
    if count != 1:
        raise ValueError(f"Upstream {description} layout changed; review the branding policy before releasing.")
    return result


def product_text(text):
    # Attribution injected below must stay upstream attribution on subsequent runs.
    lines = text.splitlines(keepends=True)
    return "".join(line if re.match(r"\s*Upstream\s*:", line) else brand_line(line) for line in lines)


def brand_line(text):
    text = re.sub(r"ChrisTitusTech/winutil", REPOSITORY, text, flags=re.IGNORECASE)
    text = re.sub(r"https://christitus\.com/windev(?![\w/-])", DEV_URL, text)
    text = re.sub(r"https://christitus\.com/win(?![\w/-])", RELEASE_URL, text)
    text = text.replace("/download/Winutil.ps1", "/download/winutil.ps1")
    text = text.replace("Chris Titus Tech's Windows Utility", PRODUCT)
    for name in ("Chris Titus Tech", "Christ Tech Tips", "Chris Tech Tips"):
        text = text.replace(name, "Pallab Das")
    return text


def apply(root, check=False):
    """Return changed relative paths; validate all structural edits before writing."""
    root = Path(root)
    for name in ("scripts/main.ps1", "scripts/start.ps1", "xaml/inputXML.xaml",
                 "functions/private/Invoke-WinUtilAssets.ps1",
                 "functions/private/Start-WinUtilUserInterface.ps1"):
        if not (root / name).is_file():
            raise ValueError(f"Required branding source moved or is missing: {name}")
    paths = {root / "windev.ps1", root / "pester/impex-command.Tests.ps1",
             root / "tools/devdocs-generator.ps1", root / "docs/astro.config.mjs",
             root / "docs/src/lib/winutil-release.js",
             root / "docs/src/components/config-builder/ConfigBuilder.jsx",
             root / ".github/CONTRIBUTING.md", root / ".github/READMEITALIAN.md",
             root / "tools/title-screen/capture_winutil.py",
             root / ".github/workflows/generate-title-screen.yaml"}
    for directory in ("scripts", "functions"):
        paths.update((root / directory).rglob("*.ps1"))
    paths.update((root / ".github/ISSUE_TEMPLATE").glob("*.yaml"))
    reference = root / "docs/src/content/docs/code-reference"
    for path in (root / "docs/src/content/docs").rglob("*.mdx"):
        if path.is_relative_to(reference) and path.relative_to(reference).parts[0] in ("tweaks", "features"):
            continue
        paths.add(path)

    originals = {}
    planned = {}
    for path in sorted(paths):
        if not path.is_file():
            continue
        original = path.read_bytes()
        originals[path] = original
        text = product_text(original.decode("utf-8-sig").replace("\r\n", "\n"))
        relative = path.relative_to(root).as_posix()
        if relative == "scripts/main.ps1":
            if "# PD-BANNER-BEGIN" in text:
                pattern = r"^# PD-BANNER-BEGIN\n.*?^# PD-BANNER-END"
            else:
                pattern = r'^Write-Host @"\n.*?^"@'
            text = replace_block(text, pattern, BANNER, "terminal banner")
        elif relative == "scripts/start.ps1":
            text = text.replace("Author         : Chris Titus @christitustech", "Maintainer     : Pallab Das @PDGamerSG\n    Upstream       : Chris Titus @christitustech (MIT)")
            text = text.replace("GitHub         : https://github.com/ChrisTitusTech", f"GitHub         : https://github.com/{REPOSITORY}")
            license_text = (root / "LICENSE").read_text(encoding="utf-8").strip()
            license_block = "    PD-LICENSE-BEGIN\n" + "\n".join("    " + line if line else "" for line in license_text.splitlines()) + "\n    PD-LICENSE-END\n"
            if "    PD-LICENSE-BEGIN\n" in text:
                text = replace_block(text, r"^    PD-LICENSE-BEGIN\n.*?^    PD-LICENSE-END\n", license_block, "license notice")
            elif text.startswith("<#\n") and "#>" in text:
                text = text.replace("#>", license_block + "#>", 1)
            else:
                raise ValueError("Upstream startup license header changed; review the branding policy.")
            text, count = re.subn(r'(\$Host\.UI\.RawUI\.WindowTitle = )"(?:WinUtil|Pallab Das Windows Utility)"', rf'\1"{PRODUCT}"', text)
            if count != 1:
                raise ValueError("Upstream terminal title layout changed; review the branding policy.")
        elif relative == "functions/private/Invoke-WinUtilAssets.ps1":
            text = replace_block(text, r"^      'logo' \{\n.*?^      \}\n(?=      'checkmark' \{)", LOGO, "application logo")
        elif relative == "functions/private/Start-WinUtilUserInterface.ps1":
            text = text.replace('Author   : <a href="https://github.com/ChrisTitusTech">@ChrisTitusTech</a>',
                                f'Maintainer : <a href="https://github.com/PDGamerSG">Pallab Das (@PDGamerSG)</a>\nUpstream   : <a href="https://github.com/ChrisTitusTech/winutil">Chris Titus Tech / WinUtil (MIT)</a>')
            text = text.replace(f"https://github.com/{REPOSITORY}/releases/tag/$($sync.version)", f"https://github.com/{REPOSITORY}/releases/latest")
            text = text.replace("Current sponsors for ChrisTitusTech:", "Upstream sponsors for ChrisTitusTech:")
        elif relative == "functions/private/Set-WinUtilTaskbarItem.ps1":
            text = text.replace("CTT logo preset:", "PD logo preset:")
        elif relative == "windev.ps1":
            text = text.replace("# Runs the pre-release version of winutil", "# Runs the latest verified release of Pallab Das Windows Utility")
            text = text.replace(f"(Invoke-RestMethod https://api.github.com/repos/{REPOSITORY}/tags).Name | Select-Object -First 1",
                                f"(Invoke-RestMethod https://api.github.com/repos/{REPOSITORY}/releases/latest).tag_name")
        elif relative == "tools/title-screen/capture_winutil.py":
            text = text.replace(r'r"WinUtil \d{2}', r'r"(?:WinUtil|Pallab Das Windows Utility) \d{2}')
        elif relative == ".github/workflows/generate-title-screen.yaml":
            text = text.replace(r"'^WinUtil\s+\d'", r"'^(?:WinUtil|Pallab Das Windows Utility)\s+\d'")
        planned[path] = text

    xaml = root / "xaml/inputXML.xaml"
    originals[xaml] = xaml.read_bytes()
    text = originals[xaml].decode().replace("\r\n", "\n")
    text, count = re.subn(r'Title="(?:WinUtil|Pallab Das Windows Utility)"', f'Title="{PRODUCT}"', text)
    if count != 1:
        raise ValueError("Upstream window title layout changed; review the branding policy.")
    planned[xaml] = text
    readme = root / "README.md"
    originals[readme] = readme.read_bytes() if readme.exists() else b""
    planned[readme] = (root / "pd/README.template.md").read_text(encoding="utf-8")

    changes = {}
    for path, text in planned.items():
        original = originals[path]
        if b"\r\n" in original:
            text = text.replace("\n", "\r\n")
        data = text.encode("utf-8")
        if original.startswith(b"\xef\xbb\xbf"):
            data = b"\xef\xbb\xbf" + data
        if data != original:
            changes[path] = data
    if not check:
        for path, data in changes.items():
            path.write_bytes(data)
    return [path.relative_to(root).as_posix() for path in changes]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report drift without changing any files")
    args = parser.parse_args()
    changed = apply(Path(__file__).resolve().parents[1], check=args.check)
    for name in changed:
        print(name)
    if args.check and changed:
        raise SystemExit("PD branding has drifted; run python pd/apply_branding.py and review the changes.")
