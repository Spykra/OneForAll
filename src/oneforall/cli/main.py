import json
import logging

import typer

from oneforall.agents.citation import CitationAgent
from oneforall.agents.critic import CriticAgent
from oneforall.agents.planner import PlannerAgent
from oneforall.agents.searcher import SearcherAgent
from oneforall.agents.summarizer import SummarizerAgent
from oneforall.agents.writer import WriterAgent

log = logging.getLogger(__name__)
app = typer.Typer(add_completion=False, help="OneForAll CLI")


@app.command(help="Return a JSON research plan for TOPIC.")
def plan(topic: str) -> None:
    plan_obj = PlannerAgent().run(topic)
    typer.echo(json.dumps(plan_obj, indent=2))


@app.command(help="Planner ➜ Searcher cascade.")
def search(topic: str) -> None:
    plan_obj = PlannerAgent().run(topic)
    hits = SearcherAgent().run(plan_obj["keywords"])
    typer.echo(json.dumps(hits, indent=2))


@app.command(help="Planner → Searcher → Summarizer.")
def summarize(topic: str) -> None:
    plan_obj = PlannerAgent().run(topic)
    hits = SearcherAgent().run(plan_obj["keywords"])
    summaries = SummarizerAgent().run(hits)
    typer.echo(json.dumps(summaries, indent=2))


@app.command(help="Generate APA-style reference list.")
def references(topic: str) -> None:
    plan_obj = PlannerAgent().run(topic)
    hits = SearcherAgent().run(plan_obj["keywords"])
    summaries = SummarizerAgent().run(hits)
    refs = CitationAgent().run(summaries)
    typer.echo("\n".join(refs))


@app.command(help="Full pipeline: draft + references + basic QA.")
def draft(topic: str) -> None:
    plan_obj = PlannerAgent().run(topic)
    hits = SearcherAgent().run(plan_obj["keywords"])
    summaries = SummarizerAgent().run(hits)

    draft_md = WriterAgent().run(plan_obj["sections"], summaries)

    refs = CitationAgent().run(summaries)
    if refs:
        draft_md += "\n\n## References\n\n" + "\n".join(f"- {c}" for c in refs)

    issues = CriticAgent().run(plan_obj["sections"], draft_md)
    if issues:
        typer.secho("⚠ Critic feedback:\n- " + "\n- ".join(issues), fg=typer.colors.YELLOW)
    else:
        typer.secho("✓ Draft passes basic QA.", fg=typer.colors.GREEN)

    typer.echo(draft_md)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    app()
