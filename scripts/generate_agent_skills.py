#!/usr/bin/env python3
"""Generate an agent-neutral `npx skills add` package from legacy skill files."""

from __future__ import annotations

from pathlib import Path
import json
import re
import shutil


REPO_ROOT = Path(__file__).resolve().parents[1]
LEGACY_SKILLS_DIR = REPO_ROOT / "Skills"
PACKAGED_SKILLS_DIR = REPO_ROOT / ".agents" / "skills"

FRONTMATTER_PATTERN = re.compile(
    r"^---\r?\n(?P<frontmatter>[\s\S]*?)\r?\n---\r?\n?(?P<body>[\s\S]*)$"
)


def parse_skill_file(skill_path: Path) -> tuple[list[str], str]:
    raw_content = skill_path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(raw_content)
    if match is None:
        raise ValueError(f"{skill_path} is missing YAML frontmatter.")

    frontmatter_lines = match.group("frontmatter").splitlines()
    if not any(line.lstrip().startswith("description:") for line in frontmatter_lines):
        raise ValueError(f"{skill_path} is missing the required description field.")

    return frontmatter_lines, match.group("body")


def build_packaged_content(frontmatter_lines: list[str], body: str, skill_name: str) -> str:
    normalized_frontmatter = []

    for line in frontmatter_lines:
        stripped_line = line.lstrip()
        if stripped_line.startswith("argument-hint:"):
            key, raw_value = line.split(":", 1)
            normalized_frontmatter.append(f"{key}: {json.dumps(raw_value.strip())}")
            continue
        normalized_frontmatter.append(line)

    if not any(line.lstrip().startswith("name:") for line in normalized_frontmatter):
        # `npx skills add` requires `name`; the instruction body stays byte-for-byte unchanged.
        normalized_frontmatter.insert(0, f"name: {skill_name}")

    return "---\n" + "\n".join(normalized_frontmatter) + "\n---\n" + body


def generate_packaged_skills() -> None:
    if not LEGACY_SKILLS_DIR.is_dir():
        raise FileNotFoundError(f"Legacy skills directory not found: {LEGACY_SKILLS_DIR}")

    shutil.rmtree(PACKAGED_SKILLS_DIR, ignore_errors=True)
    PACKAGED_SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    for legacy_skill_path in sorted(LEGACY_SKILLS_DIR.glob("*.md")):
        skill_name = legacy_skill_path.stem
        frontmatter_lines, body = parse_skill_file(legacy_skill_path)
        packaged_skill_path = PACKAGED_SKILLS_DIR / skill_name / "SKILL.md"
        packaged_skill_path.parent.mkdir(parents=True, exist_ok=True)
        packaged_skill_path.write_text(
            build_packaged_content(frontmatter_lines, body, skill_name),
            encoding="utf-8",
        )


if __name__ == "__main__":
    generate_packaged_skills()
