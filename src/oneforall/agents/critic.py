class CriticAgent:
    """Quick structural QA."""

    WORD_LIMIT = 2_000

    @staticmethod
    def run(outline: list[str], markdown: str) -> list[str]:
        issues = []
        if missing := [s for s in outline if f"## {s}" not in markdown]:
            issues.append(f"Missing sections: {', '.join(missing)}")
        if len(markdown.split()) > CriticAgent.WORD_LIMIT:
            issues.append(f"Draft exceeds {CriticAgent.WORD_LIMIT:,} words.")
        return issues
