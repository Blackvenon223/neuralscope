FROM python:3.12-slim AS base

WORKDIR /app

# System deps for graphviz
RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry==1.8.5

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --without dev,docs

# Copy source
COPY src/ src/
COPY README.md .

# Install package
RUN poetry install --no-interaction --no-ansi --only-root

EXPOSE 8000

ENTRYPOINT ["neuralscope"]
CMD ["serve", "--transport", "sse", "--port", "8000"]
