#!/usr/bin/env python3
"""Map documentation-related assets in a repository.

This script is intentionally heuristic. It helps an agent quickly discover
documentation conventions before applying docs-governance rules.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


ROOT_FILES = [
    "README.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".cursorrules",
    "mkdocs.yml",
    "docs.json",
    "mint.json",
    "docusaurus.config.js",
    "docusaurus.config.ts",
    "package.json",
    "pyproject.toml",
]

DOC_DIRS = [
    "docs",
    "examples",
    "articles",
    "guides",
    "tutorials",
    "cookbook",
    "notebooks",
    "rfcs",
    "rfc",
    "decisions",
    "adr",
    "adrs",
    ".agents",
    "skills",
    "prompts",
    "evals",
]

NAV_FILES = [
    "docs.json",
    "mint.json",
    "mkdocs.yml",
    "sidebars.js",
    "sidebars.ts",
    "_sidebar.md",
]


def existing(paths: list[str], root: Path) -> list[Path]:
    return [root / item for item in paths if (root / item).exists()]


def find_by_name(root: Path, names: list[str], max_depth: int = 4) -> list[Path]:
    found: list[Path] = []
    root_parts = len(root.parts)
    ignored = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}

    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        depth = len(current_path.parts) - root_parts
        dirs[:] = [d for d in dirs if d not in ignored]
        if depth >= max_depth:
            dirs[:] = []
        for file_name in files:
            if file_name in names:
                found.append(current_path / file_name)
    return sorted(set(found))


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def print_section(title: str, values: list[Path], root: Path) -> None:
    print(f"\n## {title}")
    if not values:
        print("- none found")
        return
    for value in values:
        print(f"- {rel(value, root)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan repository documentation assets.")
    parser.add_argument("repo", nargs="?", default=".", help="Repository root")
    args = parser.parse_args()

    root = Path(args.repo).resolve()
    if not root.exists():
        raise SystemExit(f"Repository path does not exist: {root}")

    root_files = existing(ROOT_FILES, root)
    root_dirs = existing(DOC_DIRS, root)
    nav_files = find_by_name(root, NAV_FILES)

    print(f"# Documentation Governance Scan\n\nroot: {root}")
    print_section("Root documentation/config files", root_files, root)
    print_section("Documentation-like root directories", root_dirs, root)
    print_section("Navigation/config files", nav_files, root)

    print("\n## Suggested next checks")
    if any(path.name in {"docs.json", "mint.json", "mkdocs.yml"} for path in nav_files):
        print("- Update docs navigation when adding, moving, or deleting pages.")
    if any(path.name in {"AGENTS.md", "CLAUDE.md", ".cursorrules"} for path in root_files):
        print("- Keep agent rules operational and link to longer docs instead of copying them.")
    if any(path.name.lower() in {"adr", "adrs", "decisions", "rfcs", "rfc"} for path in root_dirs):
        print("- Use the existing decision-record convention for durable design choices.")
    if not root_dirs:
        print("- No docs-like root directory found; prefer minimal README changes unless user asks to add docs structure.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
