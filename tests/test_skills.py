"""Checks every SKILL.md: header, length, shared rule blocks, referenced files."""
import re
import unittest

from helpers import ROOT, SKILLS, tracked_files

COMMON = ROOT / "common"
MAX_BODY_LINES = 200
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
BLOCK = re.compile(r"<!-- common:([a-z-]+) -->\n(.*?)\n<!-- /common:\1 -->", re.S)
LINKED = re.compile(r"\b((?:references|scripts)/[A-Za-z0-9_.-]+\.(?:md|py))")

# Which shared rule blocks each skill must carry, word for word.
REQUIRED = {
    "tri-onboarding": {"tone", "state-files", "safety"},
    "tri-tests": {"tone", "state-files", "safety", "open-water", "session-format"},
    "tri-plan": {"tone", "state-files", "safety"},
    "tri-semaine": {"tone", "state-files", "safety", "open-water", "session-format"},
    "tri-bilan": {"tone", "state-files", "safety"},
    "tri-renfo": {"tone", "state-files", "safety", "session-format"},
    "tri-nutrition": {"tone", "state-files", "safety", "safety-nutrition"},
    "tri-jour-j": {"tone", "state-files", "safety", "safety-nutrition", "open-water"},
    "tri-connect": {"tone", "state-files"},
    "tri-guide": {"tone", "open-water"},
}


def skill_dirs():
    return sorted(p for p in SKILLS.iterdir() if p.is_dir())


def split(path):
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path}: no front matter"
    header, body = text[4:].split("\n---\n", 1)
    return header, body


class SkillFilesTest(unittest.TestCase):
    def test_every_skill_is_known(self):
        for skill in skill_dirs():
            self.assertIn(skill.name, REQUIRED)
            self.assertTrue((skill / "SKILL.md").is_file(), skill.name)

    def test_front_matter(self):
        for skill in skill_dirs():
            with self.subTest(skill=skill.name):
                header, _ = split(skill / "SKILL.md")
                fields = dict(line.split(": ", 1) for line in header.splitlines())
                self.assertEqual(set(fields), {"name", "description"})
                name, description = fields["name"], fields["description"]
                self.assertEqual(name, skill.name)
                self.assertRegex(name, NAME)
                self.assertLessEqual(len(name), 64)
                self.assertNotIn("claude", name)
                self.assertNotIn("anthropic", name)
                self.assertTrue(description.strip())
                self.assertLessEqual(len(description), 1024)
                self.assertNotRegex(description, r"[<>]")
                self.assertIn("Use when", description)

    def test_body_under_200_lines(self):
        for skill in skill_dirs():
            with self.subTest(skill=skill.name):
                _, body = split(skill / "SKILL.md")
                self.assertLess(len(body.splitlines()), MAX_BODY_LINES)

    def test_shared_blocks_match_common_word_for_word(self):
        for skill in skill_dirs():
            with self.subTest(skill=skill.name):
                _, body = split(skill / "SKILL.md")
                blocks = dict(BLOCK.findall(body))
                self.assertEqual(set(blocks), REQUIRED[skill.name])
                for name, text in blocks.items():
                    canonical = (COMMON / f"{name}.md").read_text(encoding="utf-8").strip()
                    self.assertEqual(text.strip(), canonical,
                                     f"{skill.name}: block '{name}' differs from common/{name}.md")

    def test_referenced_files_exist(self):
        for skill in skill_dirs():
            with self.subTest(skill=skill.name):
                _, body = split(skill / "SKILL.md")
                linked = set(LINKED.findall(body))
                for relative in linked:
                    self.assertTrue((skill / relative).is_file(), f"{skill.name}: {relative}")
                on_disk = {str(p.relative_to(skill)) for p in skill.rglob("*")
                           if p.is_file() and p.name != "SKILL.md" and "__pycache__" not in p.parts}
                self.assertEqual(on_disk - linked, set(), f"{skill.name}: files never mentioned")


class RepositoryTextTest(unittest.TestCase):
    def test_no_em_or_en_dash_anywhere(self):
        for path in tracked_files():
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for number, line in enumerate(text.splitlines(), 1):
                self.assertNotRegex(line, "[\N{EN DASH}\N{EM DASH}]", f"{path.relative_to(ROOT)}:{number}")

    def test_scripts_use_only_the_standard_library(self):
        allowed = {"argparse", "base64", "csv", "datetime", "io", "json", "math", "os", "re",
                   "sys", "urllib", "time"}
        for script in SKILLS.glob("*/scripts/*.py"):
            for line in script.read_text(encoding="utf-8").splitlines():
                match = re.match(r"(?:import|from) ([a-z_]+)", line)
                if match:
                    self.assertIn(match.group(1), allowed, f"{script.name}: {line}")


if __name__ == "__main__":
    unittest.main()
