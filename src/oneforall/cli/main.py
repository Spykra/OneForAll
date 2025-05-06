import json

import typer

from oneforall.agents.planner import PlannerAgent
from oneforall.agents.searcher import SearcherAgent
from oneforall.agents.summarizer import SummarizerAgent

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


if __name__ == "__main__":
    app()
