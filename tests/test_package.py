"""Plugin manifests and the two READMEs."""
import json
import re
import unittest

from helpers import ROOT, SKILLS


def load(name):
    return json.loads((ROOT / ".claude-plugin" / name).read_text(encoding="utf-8"))


class ManifestTest(unittest.TestCase):
    def test_plugin_manifest(self):
        plugin = load("plugin.json")
        self.assertRegex(plugin["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertNotIn("claude", plugin["name"])
        for field in ("version", "description", "license"):
            self.assertTrue(plugin[field])
        self.assertEqual(plugin["author"]["name"], "Rapha")
        self.assertEqual(plugin["license"], "MIT")

    def test_marketplace_lists_the_plugin_at_the_repository_root(self):
        market = load("marketplace.json")
        self.assertTrue(market["owner"]["name"])
        self.assertEqual([p["name"] for p in market["plugins"]], [load("plugin.json")["name"]])
        self.assertEqual(market["plugins"][0]["source"], "./")

    def test_skills_sit_where_the_plugin_loads_them(self):
        self.assertEqual(len(list(SKILLS.glob("*/SKILL.md"))), 10)

    def test_no_secret_looking_file_is_shipped(self):
        for path in ROOT.rglob("*"):
            if ".git" in path.parts or "private" in path.parts:
                continue
            self.assertNotIn(path.name, (".env", "credentials.json"), path)


class ReadmeTest(unittest.TestCase):
    def setUp(self):
        self.english = (ROOT / "README.md").read_text(encoding="utf-8")
        self.french = (ROOT / "README.fr.md").read_text(encoding="utf-8")

    def test_both_languages_have_the_same_structure(self):
        count = lambda text: len(re.findall(r"^#{2,3} ", text, flags=re.M))
        self.assertEqual(count(self.english), count(self.french))
        self.assertIn("README.fr.md", self.english)
        self.assertIn("README.md", self.french)

    def test_every_skill_is_presented_in_both(self):
        for skill in SKILLS.iterdir():
            self.assertIn(f"`{skill.name}`", self.english)
            self.assertIn(f"`{skill.name}`", self.french)

    def test_install_commands_match_the_manifests(self):
        plugin, market = load("plugin.json")["name"], load("marketplace.json")["name"]
        for text in (self.english, self.french):
            self.assertIn(f"claude plugin install {plugin}@{market}", text)
            self.assertIn("claude plugin marketplace add raphael-saltiel/tri-coach-skills", text)

    def test_disclaimer_and_known_limits_are_present(self):
        self.assertIn("replaces neither a doctor nor a certified coach", self.english)
        self.assertIn("ne remplace ni un médecin ni un entraîneur diplômé", self.french)
        self.assertIn("## Known limits", self.english)
        self.assertIn("## Limites connues", self.french)


if __name__ == "__main__":
    unittest.main()
