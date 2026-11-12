"""No personal term from the private method notes may reach the repository.

The term list lives in private/sensitive_terms.txt, which Git ignores. Without
that file the test is skipped. Set PRIVACY_HISTORY=1 to scan the whole Git
history as well as the current files.
"""
import os
import re
import subprocess
import unittest

from helpers import ROOT, tracked_files

TERMS = ROOT / "private" / "sensitive_terms.txt"


def patterns():
    lines = TERMS.read_text(encoding="utf-8").splitlines()
    return [re.compile(line, re.I) for line in lines if line.strip() and not line.startswith("#")]


@unittest.skipUnless(TERMS.is_file(), "private/sensitive_terms.txt not present")
class PrivacyTest(unittest.TestCase):
    def assert_clean(self, label, text):
        for number, line in enumerate(text.splitlines(), 1):
            for pattern in patterns():
                self.assertIsNone(pattern.search(line),
                                  f"{label}:{number} matches /{pattern.pattern}/")

    def test_private_folder_is_ignored(self):
        result = subprocess.run(["git", "check-ignore", "-q", "private/methode.md"], cwd=ROOT)
        self.assertEqual(result.returncode, 0)
        listed = subprocess.run(["git", "ls-files", "private"], cwd=ROOT,
                                capture_output=True, text=True).stdout
        self.assertEqual(listed, "")

    def test_tracked_files_are_clean(self):
        for path in tracked_files():
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            self.assert_clean(str(path.relative_to(ROOT)), text)

    @unittest.skipUnless(os.environ.get("PRIVACY_HISTORY"), "set PRIVACY_HISTORY=1 to scan history")
    def test_history_is_clean(self):
        log = subprocess.run(["git", "log", "-p", "--all", "--format=commit %H%n%an%n%s%n%b"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
        added = "\n".join(l for l in log.splitlines() if not l.startswith("-"))
        self.assert_clean("git history", added)


if __name__ == "__main__":
    unittest.main()
