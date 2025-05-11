ONEFORALL -- LOCAL MULTI-AGENT RESEARCH CREW
===========================================

A tiny stack of cooperating "agents" that takes a research topic and
turns it into a Markdown report, completely on your own machine
(no cloud calls once pages are cached).

* * * * *

AGENTS (PIPELINE ORDER)
-----------------------

1.  PlannerAgent
    - Takes the raw topic.
    - Returns: keywords (for search) and a section outline.

2.  SearcherAgent
    - Uses the keywords to query DuckDuckGo.
    - Saves the top results in a local Chroma (SQLite) cache.

3.  SummarizerAgent
    - Downloads each hit, extracts readable text (BeautifulSoup),
    asks your local LLM to give 3-4 bullet-point highlights.
    - Caches each summary in Chroma.

4.  WriterAgent
    - Combines the outline + bullet summaries into a Markdown draft
    (one section per outline heading, ≤200 words each).

5.  CriticAgent
    - Quick QA pass: makes sure every outline heading appears once and
    that the draft is under ~2 000 words.
    - Prints warnings but does not abort the run.

* * * * *

COMMAND-LINE (all via the Typer CLI `oneforall ...`)
--------------------------------------------------

- plan TOPIC -> JSON (keywords + outline)
- search TOPIC -> JSON (raw search hits)
- summarize TOPIC -> JSON (hits + "summary" field)
- draft TOPIC -> Markdown (full report, critic feedback)

Every stage writes to the same Chroma cache (.chroma), so
re-running a command is instant and fully offline once the data
is cached.

* * * * *

QUICK START (HOST)
------------------

- poetry install
- ollama pull llama3 # once
- just summarize "Edge LLMs 2025" # planner → searcher → summarizer
- just draft "Edge LLMs 2025" # full report

* * * * *

RUN INSIDE DOCKER
-----------------

- just up # builds and starts
- docker compose exec oneforall oneforall draft "Topic"
- just down # stop stack

The container starts with `sleep infinity`, so it stays alive
until you `exec` into it.

* * * * *

DEVELOPMENT TASKS
-----------------

- just format -- Ruff formatter\
- just lint -- Ruff linter\
- just test -- All unit tests (they run offline; no Ollama / web)

* * * * *

DEPENDENCIES (PINNED IN pyproject.toml)
---------------------------------------

- Python 3.12 - poetry 2.1
- Ruff, pytest, mypy - DuckDuckGo-Search 8.x
- ChromaDB 1.x (SQLite) - BeautifulSoup4 4.12
- httpx 0.27 - Ollama (model: llama3)

* * * * *

ENVIRONMENTAL VARIABLES (loaded from .env or docker-compose):
---------------------------------------

OLLAMA_BASE_URL  default http://localhost:11434
OLLAMA_MODEL     default llama3
CHROMA_PATH      default .chroma`
