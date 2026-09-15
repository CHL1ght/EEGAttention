"""Check repository-relative links in Markdown files without modifying files."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SKIP_PREFIXES = ("#", "http://", "https://", "mailto:", "data:", "codex:")


def main() -> None:
    checked = 0
    errors: list[str] = []
    for markdown in sorted(ROOT.rglob("*.md")):
        if ".git" in markdown.parts:
            continue
        text = markdown.read_text(encoding="utf-8-sig")
        for raw_target in LINK_RE.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(SKIP_PREFIXES):
                continue
            path_part = unquote(target.split("#", 1)[0])
            if not path_part:
                continue
            checked += 1
            resolved = (markdown.parent / path_part).resolve()
            if not resolved.exists():
                errors.append(f"{markdown.relative_to(ROOT)} -> {target}")
    if errors:
        raise AssertionError("Broken Markdown links:\n" + "\n".join(errors))
    print(f"Markdown relative links OK: {checked} links")


if __name__ == "__main__":
    main()
