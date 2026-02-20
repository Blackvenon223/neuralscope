# 🧪 Руководство по тестированию NeuralScope

Подробный гайд для локального тестирования перед публикацией на GitHub.

---

## Содержание

1. [Подготовка окружения](#1-подготовка-окружения)
2. [Запуск тестов](#2-запуск-тестов)
3. [Линтинг и проверка стиля](#3-линтинг-и-проверка-стиля)
4. [Тестирование CLI](#4-тестирование-cli)
5. [Тестирование SDK](#5-тестирование-sdk)
6. [Тестирование с LLM (нужен API ключ)](#6-тестирование-с-llm)
7. [Docker](#7-docker)
8. [Документация](#8-документация)
9. [Pre-publish чеклист](#9-pre-publish-чеклист)
10. [Публикация на GitHub](#10-публикация-на-github)

---

## 1. Подготовка окружения

### Требования

- Python 3.12+
- Poetry
- Git
- (опционально) Docker + Docker Compose
- (опционально) Graphviz (для SVG графов)

### Установка

```powershell
# Клонировать/перейти в проект
cd d:\ai_pet_project

# Проверить Python
python --version  # 3.12+

# Установить Poetry (если нет)
pip install poetry

# Установить все зависимости: dev + docs
poetry install --with dev,docs

# Проверить что всё работает
poetry run python -c "from neuralscope import NeuralScope; print('OK')"
```

### Структура тестов

```
tests/
├── unit/
│   ├── features/
│   │   ├── code_review/        # 10 тестов
│   │   ├── codebase_qa/        # 7 тестов
│   │   ├── dependency_graph/   # 16 тестов
│   │   ├── documentation/      # 3 теста
│   │   ├── health_dashboard/   # 4 теста
│   │   ├── pr_summary/         # 2 теста
│   │   ├── prompt_studio/      # 4 теста
│   │   ├── test_generator/     # 2 теста
│   │   ├── vulnerability_scan/ # 6 тестов
│   │   └── architecture_validator/ # 2 теста
│   ├── core/
│   │   └── test_mlops.py       # 6 тестов (cache + tracing)
│   ├── cli/
│   │   └── test_cli.py         # 3 теста
│   ├── mcp/
│   │   └── test_mcp_server.py  # 4 теста (skipped без mcp)
│   └── test_sdk_wiring.py      # 4 теста (импорт всех фич)
```

---

## 2. Запуск тестов

### Все тесты

```powershell
poetry run pytest tests/ -v --tb=short
```

Ожидаемый результат: **84 passed, 4 skipped, 2 warnings**

### С отчётом покрытия

```powershell
# В терминал
poetry run pytest tests/ --cov=src/neuralscope --cov-report=term-missing

# HTML отчёт (откроется в браузере)
poetry run pytest tests/ --cov=src/neuralscope --cov-report=html
# Открыть htmlcov/index.html
```

### Тестирование отдельных фич

```powershell
# Code Review
poetry run pytest tests/unit/features/code_review/ -v

# Codebase QA (RAG pipeline)
poetry run pytest tests/unit/features/codebase_qa/ -v

# Dependency Graph (AST + LLM)
poetry run pytest tests/unit/features/dependency_graph/ -v

# Security Scanner (LLM)
poetry run pytest tests/unit/features/vulnerability_scan/ -v

# Health Dashboard
poetry run pytest tests/unit/features/health_dashboard/ -v

# Prompt Studio
poetry run pytest tests/unit/features/prompt_studio/ -v

# SDK Wiring (импорт всех модулей)
poetry run pytest tests/unit/test_sdk_wiring.py -v

# CLI
poetry run pytest tests/unit/cli/ -v

# Cache + Tracing
poetry run pytest tests/unit/core/ -v
```

### Быстрая проверка (только быстрые тесты)

```powershell
poetry run pytest tests/ -q --tb=line
```

---

## 3. Линтинг и проверка стиля

### Ruff (линтер + формататор)

```powershell
# Проверить ошибки
poetry run ruff check src/ tests/

# Проверить форматирование
poetry run ruff format --check src/ tests/

# Автоматически исправить
poetry run ruff check --fix src/ tests/
poetry run ruff format src/ tests/
```

### Mypy (type checking)

```powershell
poetry run mypy src/neuralscope/ --ignore-missing-imports
```

---

## 4. Тестирование CLI

### Базовые команды (не нужен LLM)

```powershell
# Версия
poetry run neuralscope --version
# Ожидание: neuralscope, version X.X.X

# Помощь (должны быть видны все 14 команд)
poetry run neuralscope --help

# Список LLM провайдеров
poetry run neuralscope models
# Ожидание: таблица с 7+ провайдерами

# Health Dashboard (работает без LLM, использует radon)
poetry run neuralscope health ./src
# Ожидание: JSON с health_score, файлами, hotspots

# Dependency Graph — AST режим
poetry run neuralscope graph ./src --output json
# Ожидание: JSON с nodes и edges

# Dependency Graph — указать режим
poetry run neuralscope graph ./src --output json --mode ast
```

### Команды с LLM (нужен API ключ)

```powershell
# Установить API ключ
$env:OPENAI_API_KEY = "sk-..."

# Code Review
poetry run neuralscope review ./src/neuralscope/core/settings.py --model openai/gpt-4o-mini

# Documentation
poetry run neuralscope docs ./src/neuralscope/core/settings.py --model openai/gpt-4o-mini

# Security Scan
poetry run neuralscope scan ./src/neuralscope/core --model openai/gpt-4o-mini

# Test Generation
poetry run neuralscope test-gen ./src/neuralscope/core/settings.py --model openai/gpt-4o-mini

# Codebase Q&A
poetry run neuralscope ask "What LLM providers are supported?" --project ./src --model openai/gpt-4o-mini

# PR Summary (нужен git history)
poetry run neuralscope pr-summary --diff HEAD~1 --model openai/gpt-4o-mini

# Graph с LLM анализом
poetry run neuralscope graph ./src/neuralscope/core --mode llm --model openai/gpt-4o-mini

# Architecture Validation
poetry run neuralscope validate ./src --model openai/gpt-4o-mini

# Prompt Profile
poetry run neuralscope profile-create "my-profile" --model openai/gpt-4o-mini
poetry run neuralscope profile-list
```

---

## 5. Тестирование SDK

### Импорт и базовые операции

```powershell
poetry run python -c "from neuralscope import NeuralScope; ns = NeuralScope(); print('Model:', ns.model); print('Providers:', len(ns.list_models()))"
```

### Полноценный тест SDK (с LLM)

Создайте файл `test_manual_sdk.py`:

```python
import asyncio
from neuralscope import NeuralScope

async def main():
    ns = NeuralScope(model="openai/gpt-4o-mini")

    # 1. Health (без LLM)
    health = await ns.health("./src")
    print("Health score:", health.get("health_score"))

    # 2. Graph (AST)
    graph = await ns.build_graph("./src", output="json", mode="ast")
    print("Graph nodes:", graph.get("nodes"))

    # 3. Review (LLM)
    review = await ns.review("./src/neuralscope/core/settings.py")
    print("Review score:", review.get("score"))

    # 4. Ask (LLM + RAG)
    answer = await ns.ask("How does the LLM registry work?", project="./src")
    print("Answer:", answer.get("answer", "")[:200])

asyncio.run(main())
```

```powershell
$env:OPENAI_API_KEY = "sk-..."
poetry run python test_manual_sdk.py
```

---

## 6. Тестирование с LLM

### Минимальный набор (нужен 1 API ключ)

Для полноценного тестирования LLM-фич достаточно OpenAI API ключа:

```powershell
$env:OPENAI_API_KEY = "sk-..."

# Тест на маленьком файле (экономим токены)
poetry run neuralscope review ./src/neuralscope/__init__.py --model openai/gpt-4o-mini
poetry run neuralscope docs ./src/neuralscope/__init__.py --model openai/gpt-4o-mini
poetry run neuralscope scan ./src/neuralscope/core --model openai/gpt-4o-mini
```

### Тестирование с локальным Ollama (бесплатно)

```powershell
# Установить Ollama: https://ollama.ai
ollama pull llama3.2

# Использовать в NeuralScope
poetry run neuralscope review ./src/neuralscope/__init__.py --model ollama/llama3.2
```

---

## 7. Docker

### Сборка образа

```powershell
docker build -t neuralscope .
```

### Запуск с Qdrant

```powershell
docker compose up -d

# Проверить статус
docker compose ps

# Логи
docker compose logs neuralscope
docker compose logs qdrant

# Остановить
docker compose down
```

### Проверка внутри контейнера

```powershell
docker compose exec neuralscope neuralscope --version
docker compose exec neuralscope neuralscope models
docker compose exec neuralscope neuralscope health /app/src
```

---

## 8. Документация

### Локальный сервер

```powershell
poetry run mkdocs serve
# Открыть http://127.0.0.1:8000
```

### Проверить что всё рендерится

- `http://127.0.0.1:8000` — главная страница
- `http://127.0.0.1:8000/getting-started/` — гайд по установке
- `http://127.0.0.1:8000/sdk-reference/` — API документация
- `http://127.0.0.1:8000/cli-reference/` — CLI команды
- `http://127.0.0.1:8000/mcp-server/` — MCP сервер
- `http://127.0.0.1:8000/features/code-review/` — все 10 фич

### Билд статического сайта

```powershell
poetry run mkdocs build
# Результат в site/
```

---

## 9. Pre-publish чеклист

Выполни каждый пункт и убедись что всё зелёное:

```powershell
# ✅ 1. Тесты проходят
poetry run pytest tests/ --tb=short -q
# Ожидание: 84 passed, 4 skipped

# ✅ 2. Линтинг чистый
poetry run ruff check src/ tests/
poetry run ruff format --check src/ tests/

# ✅ 3. CLI работает
poetry run neuralscope --version
poetry run neuralscope models
poetry run neuralscope health ./src

# ✅ 4. SDK импортируется
poetry run python -c "from neuralscope import NeuralScope; print('OK')"

# ✅ 5. Граф строится (AST)
poetry run neuralscope graph ./src --output json

# ✅ 6. Документация рендерится
poetry run mkdocs build

# ✅ 7. Docker собирается
docker build -t neuralscope .

# ✅ 8. .gitignore проверен
# Убедись что .env, __pycache__, .venv, dist/, htmlcov/ исключены
```

---

## 10. Публикация на GitHub

```powershell
# 1. Инициализировать git
git init
git add .

# 2. Проверить что лишнего нет
git status
# Не должно быть: .env, __pycache__, .venv, node_modules

# 3. Первый коммит
git commit -m "feat: NeuralScope v0.1.0 — 10 AI features, SDK, CLI, MCP"

# 4. Создать репозиторий на GitHub и добавить remote
git remote add origin https://github.com/YOUR_USER/neuralscope.git
git branch -M main
git push -u origin main
```

### После пуша

- Проверь GitHub Actions CI (вкладка Actions)
- Проверь что README рендерится красиво
- Проверь что badges показывают статус
