FROM python:3.12-slim
WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./
COPY src ./src

RUN pip install poetry && poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT ["oneforall"]
