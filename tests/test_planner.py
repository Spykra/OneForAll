import re

from oneforall.agents.planner import PlannerAgent


def test_plan_structure():
    plan = PlannerAgent(temperature=0).run("Edge LLMs 2025")
    assert list(plan) == ["keywords", "sections"]
    assert isinstance(plan["keywords"], list)
    assert isinstance(plan["sections"], list)
    assert all(re.fullmatch(r"[A-Za-z0-9\- ]{2,}", kw) for kw in plan["keywords"])
