import json

import typer

from oneforall.agents.planner import PlannerAgent

app = typer.Typer(add_completion=False, help="OneForAll CLI")


@app.command("plan", help="Return a JSON research plan for TOPIC.")
def plan_cmd(topic: str) -> None:
    """Generate a planner-agent outline for the given topic."""
    result = PlannerAgent().run(topic)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    app()
