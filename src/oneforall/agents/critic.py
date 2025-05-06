class CriticAgent:
    """Very light QA: ensure every outline section appears once."""

    @staticmethod
    def run(outline: list[str], markdown: str) -> list[str]:
        missing = [s for s in outline if f"## {s}" not in markdown]
        too_long = len(markdown.split()) > 2_000  # rough cap
        msgs = []
        if missing:
            msgs.append(f"Missing sections: {', '.join(missing)}")
        if too_long:
            msgs.append("Draft exceeds 2 000 words.")
        return msgs
