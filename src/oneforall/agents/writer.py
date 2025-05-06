from __future__ import annotations

from typing import List

from oneforall.llm.ollama_client import chat

SYSTEM_PROMPT = """
You are a technical writer. Using the provided outline and bullet-point
summaries, write a Markdown report.

Rules
1. Keep each section ≤ 200 words.
2. Use the outline order exactly.
3. Embed the summary bullets verbatim before you elaborate.
"""

SECTION_TEMPLATE = "## {title}\n\n{bullets}\n\n{body}\n"


class WriterAgent:
    """Compose a Markdown draft from outline & summaries."""

    def __init__(self, *, temperature: float = 0.3) -> None:
        self.temperature = temperature

    def run(self, outline: List[str], summaries: List[dict]) -> str:
        # NEW: take bullets in order of appearance
        bullets_lists = [s["summary"] for s in summaries]

        sections_md: List[str] = []
        for idx, title in enumerate(outline):
            bullets_raw = bullets_lists[idx] if idx < len(bullets_lists) else ""
            bullets = (
                "\n".join(
                    f"- {line.lstrip('- ').strip()}"
                    for line in bullets_raw.splitlines()
                    if line.strip().startswith("-")
                )
                or "- (no summary available)"
            )

            prompt = SYSTEM_PROMPT + f"\n\n### Outline title\n{title}\n\n### Bullets\n{bullets}\n"
            body = chat([{"role": "system", "content": prompt}], temperature=self.temperature).strip()

            sections_md.append(SECTION_TEMPLATE.format(title=title, bullets=bullets, body=body))

        return "# Research Report\n\n" + "\n".join(sections_md)
