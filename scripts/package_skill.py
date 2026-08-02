#!/usr/bin/env python3
"""Build a runtime-only ja-ai-polish directory and zip archive."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
BUNDLE = DIST / "ja-ai-polish"
ALLOWED_ROOT_FILES = ("SKILL.md",)
ALLOWED_DIRECTORIES = ("agents", "references")


def build() -> tuple[Path, Path]:
    if DIST.exists():
        shutil.rmtree(DIST)
    BUNDLE.mkdir(parents=True)

    for name in ALLOWED_ROOT_FILES:
        shutil.copy2(ROOT / name, BUNDLE / name)
    for name in ALLOWED_DIRECTORIES:
        shutil.copytree(ROOT / name, BUNDLE / name)

    archive = DIST / "ja-ai-polish.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        for path in sorted(BUNDLE.rglob("*")):
            if path.is_file():
                handle.write(path, Path("ja-ai-polish") / path.relative_to(BUNDLE))
    return BUNDLE, archive


def main() -> int:
    bundle, archive = build()
    print(f"Built {bundle}")
    print(f"Built {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
