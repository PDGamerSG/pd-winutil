"""Exercise the capture tool's pure matcher without loading Windows APIs."""

import ast
from pathlib import Path
import re
import unittest


class WindowIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[2] / "tools/title-screen/capture_winutil.py"
        tree = ast.parse(path.read_text())
        matcher = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_is_winutil_window")
        namespace = {"re": re}
        exec(compile(ast.Module(body=[matcher], type_ignores=[]), str(path), "exec"), namespace)
        cls.matches = staticmethod(namespace["_is_winutil_window"])

    def test_capture_tool_finds_the_branded_wpf_window(self):
        self.assertTrue(self.matches("Pallab Das Windows Utility 26.11.11", "HwndWrapper[PowerShell;123;abc]"))
        self.assertTrue(self.matches("WinUtil 26.11.11", "HwndWrapper[PowerShell;123;abc]"))

    def test_capture_tool_still_rejects_terminals_and_editors(self):
        self.assertFalse(self.matches("Pallab Das Windows Utility", "CASCADIA_HOSTING_WINDOW_CLASS"))
        self.assertFalse(self.matches("Pallab Das Windows Utility 26.11.11 - Editor", "HwndWrapper[PowerShell;123;abc]"))
        self.assertFalse(self.matches("Pallab Das Windows Utility 26.11.11", "ConsoleWindowClass"))
