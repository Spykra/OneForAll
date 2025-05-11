from __future__ import annotations

import re
from typing import List

from oneforall.llm.ollama_client import chat

SYSTEM_PROMPT = """
You are a technical writer. Use the outline and bullet summaries to compose a Markdown report.

Rules
1. ≤200 words per section.
2. Each section starts with the given header exactly once.
3. Paste the bullets verbatim, then write new prose without repeating the title or the bullets.
4. No extra Markdown headings.
5. If no bullets, write prose only (no placeholders).
""".strip()

SECTION_TMPL = "## {title}\n\n{bullets}{body}\n"


class WriterAgent:
    """Turn outline + summaries into a clean Markdown draft."""

    _BULLET_RE = re.compile(r"^\s*(?:[\u2022\-])\s*")

    @classmethod
    def _clean_bullets(cls, raw: str) -> str:
        lines = []
        for line in raw.splitlines():
            if cls._BULLET_RE.match(line):
                txt = cls._BULLET_RE.sub("", line).strip()
                if txt:
                    lines.append(f"- {txt}")
        return "\n".join(lines)

    @staticmethod
    def _strip_title_echoes(text: str, title: str) -> str:
        norm = re.sub(r"\W+", "", title).lower()
        cleaned = []
        for line in text.splitlines():
            bare = re.sub(r"[\W_]+", "", line).lower()
            if bare in (norm, f"{norm}s"):
                continue
            if not re.search(r"[A-Za-z0-9]", line):
                continue
            cleaned.append(line)
        return "\n".join(cleaned).strip()

    def __init__(self, *, temperature: float = 0.3) -> None:
        self.temperature = temperature

    def run(self, outline: List[str], summaries: List[dict]) -> str:
        bullets = [
            "" if s.get("summary", "").lstrip().startswith("[Skipped]") else self._clean_bullets(s["summary"])
            for s in summaries
        ]

        sections = []
        for idx, title in enumerate(outline):
            blk = bullets[idx] if idx < len(bullets) else ""
            bullet_block = f"{blk}\n\n" if blk else ""

            prompt = SYSTEM_PROMPT + f"\n\nSection: {title}"
            if blk:
                prompt += f"\n\nBullets:\n{blk}"

            try:
                body = chat([{"role": "system", "content": prompt}], temperature=self.temperature).strip()
            except Exception as exc:  # noqa: BLE001
                body = f"[Error generating content: {exc.__class__.__name__}]"

            body = "\n" + body.lstrip()
            body = body.replace("##", "####")
            body = self._strip_title_echoes(body, title)

            sections.append(SECTION_TMPL.format(title=title, bullets=bullet_block, body=body))

        return "# Research Report\n\n" + "\n".join(sections)
