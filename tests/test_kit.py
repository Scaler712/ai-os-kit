"""Tests for scripts/new_company.py and scripts/check_kit.py. Standard library only."""
from __future__ import annotations

import codecs
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT / "scripts"))

import check_kit  # noqa: E402
import new_company  # noqa: E402


def rot(s: str) -> str:
    return codecs.decode(s, "rot13")


class NewCompanyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_creates_folder_with_core_files_and_skills(self):
        target = self.tmp / "acme"
        files = new_company.create_company(target)
        self.assertTrue(files)
        for rel in [
            "READ-FIRST.md", "START-HERE.md", "corrections.md", "decisions.md",
            "core/business.md", "core/clients.md", "core/pricing-and-limits.md",
            "core/people.md", "core/priorities.md", "core/open-questions.md",
            "log/cards.md", "output/README.md",
            ".claude/skills/process-a-lead/SKILL.md",
        ]:
            self.assertTrue((target / rel).is_file(), rel)
        skills = sorted(p.name for p in (target / ".claude/skills").iterdir())
        self.assertEqual(skills, sorted(p.parent.name for p in (KIT / "skills").glob("*/SKILL.md")))

    def test_no_skills_flag(self):
        target = self.tmp / "acme"
        new_company.create_company(target, with_skills=False)
        self.assertFalse((target / ".claude").exists())
        self.assertTrue((target / "core/clients.md").is_file())

    def test_refuses_inside_repo(self):
        with self.assertRaises(ValueError) as ctx:
            new_company.create_company(KIT / "my-company-should-not-exist")
        self.assertIn("inside the kit", str(ctx.exception))
        self.assertFalse((KIT / "my-company-should-not-exist").exists())

    def test_refuses_parent_of_repo(self):
        with self.assertRaises(ValueError):
            new_company.create_company(KIT.parent)

    def test_refuses_non_empty_target(self):
        target = self.tmp / "busy"
        target.mkdir()
        (target / "keep.txt").write_text("mine")
        with self.assertRaises(ValueError):
            new_company.create_company(target)
        self.assertEqual((target / "keep.txt").read_text(), "mine")

    def test_cli_exit_codes(self):
        script = str(KIT / "scripts/new_company.py")
        ok = subprocess.run([sys.executable, script, str(self.tmp / "cli")], capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertIn("company folder created", ok.stdout)
        bad = subprocess.run([sys.executable, script, str(KIT / "nope")], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)
        self.assertIn("refusing", bad.stderr)


def make_kit(root: Path) -> None:
    """A minimal valid kit tree for check_kit tests."""
    (root / "skills/demo-job").mkdir(parents=True)
    (root / "skills/demo-job/SKILL.md").write_text(
        "---\nname: demo-job\ndescription: Does a demo. Use when testing.\n---\n"
        "# Demo\nRead `core/clients.md`.\n"
    )
    (root / "company-template/core").mkdir(parents=True)
    (root / "company-template/core/clients.md").write_text("# Clients\n")
    (root / "README.md").write_text("See `skills/demo-job/SKILL.md`.\n")


class CheckKitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        make_kit(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_check(self):
        out = io.StringIO()
        code = check_kit.run(self.tmp, out=out)
        return code, out.getvalue()

    def test_real_kit_passes(self):
        out = io.StringIO()
        self.assertEqual(check_kit.run(KIT, out=out), 0, out.getvalue())

    def test_minimal_kit_passes(self):
        code, out = self.run_check()
        self.assertEqual(code, 0, out)

    def test_name_must_match_folder(self):
        p = self.tmp / "skills/demo-job/SKILL.md"
        p.write_text(p.read_text().replace("name: demo-job", "name: other-name"))
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("does not match folder", out)

    def test_description_needs_use_when(self):
        p = self.tmp / "skills/demo-job/SKILL.md"
        p.write_text(p.read_text().replace("Use when testing.", "For tests."))
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("Use when", out)

    def test_missing_frontmatter(self):
        (self.tmp / "skills/demo-job/SKILL.md").write_text("# no frontmatter\n")
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("frontmatter", out)

    def test_broken_path_fails_and_placeholders_skip(self):
        (self.tmp / "README.md").write_text(
            "See `core/missing.md` and `output/YYYY-MM-DD-x.md` and `contacts/<company>.md`.\n"
        )
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("core/missing.md", out)
        self.assertNotIn("YYYY", out)
        self.assertNotIn("<company>", out)

    def test_denylist_names_case_insensitive(self):
        for term in ["urval", "nggvb", "Ersf"]:
            word = rot(term)
            (self.tmp / "README.md").write_text(f"Thanks to {word.upper()} for this.\n")
            code, out = self.run_check()
            self.assertEqual(code, 1, word)
            self.assertIn("FAIL denylist", out)

    def test_denylist_is_word_based(self):
        (self.tmp / "README.md").write_text("An explanation of planar maps.\n")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)

    def test_git_ref_url_allowed(self):
        (self.tmp / "README.md").write_text("https://example.org/archive/" + rot("ersf") + "/heads/main.zip\n")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)

    def test_email_key_ip_detected(self):
        samples = {
            "email": "write to someone" + "@" + "example.com",
            "key": "s" + "k-" + "a1B2c3D4e5F6g7H8i9",
            "ip": ".".join(["10", "0", "0", "12"]),
        }
        for kind, text in samples.items():
            (self.tmp / "README.md").write_text(text + "\n")
            code, out = self.run_check()
            self.assertEqual(code, 1, kind)
            self.assertIn(f"{kind}:", out)

    def test_em_dash_fails_style(self):
        (self.tmp / "README.md").write_text("one \u2014 two\n")
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("FAIL style", out)

    def test_scan_covers_any_file_type(self):
        (self.tmp / "notes.txt").write_text(rot("nwp") + " group\n")
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("notes.txt", out)


if __name__ == "__main__":
    unittest.main()
