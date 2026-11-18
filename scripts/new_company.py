#!/usr/bin/env python3
"""Create a new company folder from company-template/.

Usage:
    python3 scripts/new_company.py /absolute/path/to/my-company [--no-skills]

The folder must be OUTSIDE this repository. Your company facts belong in a
private place, never in a clone you might publish. Standard library only.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = KIT_ROOT / "company-template"
SKILLS = KIT_ROOT / "skills"


def is_inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def create_company(target: Path, with_skills: bool = True, kit_root: Path = KIT_ROOT) -> list[Path]:
    """Copy the template (and skills) to target. Returns the files written.

    Raises ValueError with a plain message when the target is not allowed.
    """
    kit_root = kit_root.resolve()
    template = kit_root / "company-template"
    skills = kit_root / "skills"
    target = target.expanduser().resolve()

    if not template.is_dir():
        raise ValueError(f"template not found: {template}")
    if is_inside(target, kit_root):
        raise ValueError(
            f"refusing to create the company folder inside the kit ({kit_root}). "
            "Pick a private path outside this repository."
        )
    if is_inside(kit_root, target):
        raise ValueError("refusing: the target contains the kit. Pick a new, empty folder.")
    if target.exists() and any(target.iterdir()):
        raise ValueError(f"refusing: {target} already exists and is not empty.")

    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template, target, dirs_exist_ok=True)

    if with_skills:
        dest = target / ".claude" / "skills"
        dest.mkdir(parents=True, exist_ok=True)
        for skill_dir in sorted(p for p in skills.iterdir() if (p / "SKILL.md").is_file()):
            shutil.copytree(skill_dir, dest / skill_dir.name)

    return sorted(p for p in target.rglob("*") if p.is_file())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a company folder from the AI OS template.")
    parser.add_argument("target", help="absolute path for the new company folder, outside this repository")
    parser.add_argument("--no-skills", action="store_true", help="do not copy skills into .claude/skills/")
    args = parser.parse_args(argv)

    try:
        files = create_company(Path(args.target), with_skills=not args.no_skills)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    target = Path(args.target).expanduser().resolve()
    print(f"company folder created: {target}")
    print(f"files written: {len(files)}")
    print("")
    print("next:")
    print(f"  1. cd {target}")
    print("  2. cp READ-FIRST.md AGENTS.md && cp READ-FIRST.md CLAUDE.md")
    print("  3. fill in core/clients.md first, then the rest of core/")
    print("  4. open the folder in Claude Code or Codex and follow START-HERE.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
