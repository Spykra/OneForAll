import json

import typer

from oneforall.agents.critic import CriticAgent
from oneforall.agents.planner import PlannerAgent
from oneforall.agents.searcher import SearcherAgent
from oneforall.agents.summarizer import SummarizerAgent
from oneforall.agents.writer import WriterAgent

app = typer.Typer(add_completion=False, help="OneForAll CLI")


@app.command("plan", help="Return a JSON research plan for TOPIC.")
def plan_cmd(topic: str) -> None:
    plan = PlannerAgent().run(topic)
    typer.echo(json.dumps(plan, indent=2))


@app.command("search", help="Planner ➜ Searcher cascade.")
def search_cmd(topic: str) -> None:
    plan = PlannerAgent().run(topic)
    hits = SearcherAgent().run(plan["keywords"])
    typer.echo(json.dumps(hits, indent=2))


@app.command("summarize", help="Planner → Searcher → Summarizer end-to-end.")
def summarize_cmd(topic: str) -> None:
    plan = PlannerAgent().run(topic)
    hits = SearcherAgent().run(plan["keywords"])
    summaries = SummarizerAgent().run(hits)
    typer.echo(json.dumps(summaries, indent=2))


@app.command("draft", help="End-to-end report draft.")
def draft_cmd(topic: str) -> None:
    plan = PlannerAgent().run(topic)
    hits = SearcherAgent().run(plan["keywords"])
    summaries = SummarizerAgent().run(hits)
    draft_md = WriterAgent().run(plan["sections"], summaries)
    issues = CriticAgent().run(plan["sections"], draft_md)
    if issues:
        typer.secho("⚠ Critic feedback:\n" + "\n".join(issues), fg=typer.colors.YELLOW)
    else:
        typer.secho("✓ Draft passes basic QA.", fg=typer.colors.GREEN)
    typer.echo(draft_md)


if __name__ == "__main__":
    app()
