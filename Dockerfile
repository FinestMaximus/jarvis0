FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base

WORKDIR /app
ARG ENV

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl build-essential graphviz plantuml pandoc && \
    rm -rf /var/lib/apt/lists/* && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    uv venv

COPY pyproject.toml .

RUN uv sync

COPY . .

EXPOSE 8051

ENTRYPOINT ["/bin/sh", "-c", ". .venv/bin/activate && streamlit run main.py --server.port=8051 --server.address=0.0.0.0"]
