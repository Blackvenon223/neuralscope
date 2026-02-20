"""NeuralScope CLI — powered by Typer + Rich."""

import asyncio

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from neuralscope import __version__
from neuralscope.sdk.client import NeuralScope

app = typer.Typer(
    name="neuralscope",
    help="🧠🔬 NeuralScope — AI-powered code analysis toolkit",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()

MODEL_OPTION = typer.Option(None, "--model", "-m", help="LLM model (e.g. openai/gpt-5.2)")
PROFILE_OPTION = typer.Option("default", "--profile", "-p", help="Prompt profile name")


def _run(coro):
    return asyncio.run(coro)


def _client(model: str | None = None, profile: str = "default") -> NeuralScope:
    return NeuralScope(model=model, profile=profile)


def version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold cyan]NeuralScope[/bold cyan] v{__version__}")
        raise typer.Exit


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """🧠🔬 NeuralScope — AI-powered code analysis toolkit."""


@app.command()
def review(
    path: str = typer.Argument(..., help="File to review"),
    diff: bool = typer.Option(False, "--diff", "-d", help="Review as diff"),
    model: str | None = MODEL_OPTION,
    profile: str = PROFILE_OPTION,
) -> None:
    """AI-powered code review."""
    console.print(f"[bold]Reviewing[/bold] {path}...")
    result = _run(_client(model, profile).review(path, diff=diff))
    console.print_json(data=result)


@app.command()
def docs(
    path: str = typer.Argument(..., help="File to document"),
    fmt: str = typer.Option("markdown", "--format", "-f", help="Output format"),
    model: str | None = MODEL_OPTION,
) -> None:
    """Generate documentation for a file."""
    console.print(f"[bold]Documenting[/bold] {path}...")
    result = _run(_client(model).docs(path, fmt=fmt))
    console.print_json(data=result)


@app.command()
def graph(
    path: str = typer.Argument(..., help="Project root path"),
    output: str = typer.Option("json", "--output", "-o", help="Output format (json/dot/svg)"),
    mode: str = typer.Option("ast", "--mode", help="Analysis mode: ast or llm"),
    model: str | None = MODEL_OPTION,
) -> None:
    """Build dependency graph (AST or LLM-powered)."""
    console.print(f"[bold]Building graph[/bold] for {path} (mode={mode})...")
    result = _run(_client(model).build_graph(path, output=output, mode=mode))
    console.print_json(data=result)


@app.command()
def impact(
    path: str = typer.Argument(..., help="Project root path"),
    diff: str = typer.Option("HEAD~1", "--diff", help="Git diff reference"),
) -> None:
    """Analyze change impact."""
    console.print(f"[bold]Analyzing impact[/bold] for {path}...")
    result = _run(_client().impact(path, diff=diff))
    console.print_json(data=result)


@app.command()
def scan(
    path: str = typer.Argument(..., help="Project path to scan"),
    model: str | None = MODEL_OPTION,
) -> None:
    """Scan for security vulnerabilities."""
    console.print(f"[bold]Scanning[/bold] {path}...")
    result = _run(_client(model).scan(path))
    console.print_json(data=result)


@app.command(name="test-gen")
def test_gen(
    path: str = typer.Argument(..., help="Source file to generate tests for"),
    model: str | None = MODEL_OPTION,
) -> None:
    """Generate unit tests for a file."""
    console.print(f"[bold]Generating tests[/bold] for {path}...")
    result = _run(_client(model).generate_tests(path))
    console.print_json(data=result)


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question about the codebase"),
    project: str = typer.Option(".", "--project", help="Project root"),
    model: str | None = MODEL_OPTION,
) -> None:
    """Ask a question about the codebase (RAG-powered)."""
    console.print(f"[bold]Asking:[/bold] {question}")
    result = _run(_client(model).ask(question, project=project))
    console.print_json(data=result)


@app.command()
def health(
    path: str = typer.Argument(".", help="Project path"),
) -> None:
    """Show project health dashboard."""
    console.print(f"[bold]Analyzing health[/bold] of {path}...")
    result = _run(_client().health(path))
    console.print_json(data=result)


@app.command(name="pr-summary")
def pr_summary(
    diff: str = typer.Option("HEAD~1", "--diff", help="Git diff reference"),
    model: str | None = MODEL_OPTION,
) -> None:
    """Generate PR description from diff."""
    console.print("[bold]Generating PR summary[/bold]...")
    result = _run(_client(model).pr_summary(diff=diff))
    console.print_json(data=result)


@app.command(name="validate")
def validate(
    path: str = typer.Argument(..., help="Project root path"),
    rules: str | None = typer.Option(None, "--rules", "-r", help="Rules file path"),
    model: str | None = MODEL_OPTION,
) -> None:
    """Validate architecture rules."""
    console.print(f"[bold]Validating architecture[/bold] of {path}...")
    result = _run(_client(model).validate_arch(path, rules=rules))
    console.print_json(data=result)


@app.command(name="profile-create")
def profile_create(
    name: str = typer.Argument(..., help="Profile name"),
    description: str = typer.Option("", "--desc", help="Profile description"),
    system_prompt: str = typer.Option("", "--prompt", help="System prompt"),
    temperature: float = typer.Option(0.7, "--temp", help="Temperature"),
) -> None:
    """Create a new prompt profile."""
    _run(
        _client().create_profile(
            name,
            config={
                "description": description,
                "system_prompt": system_prompt,
                "temperature": temperature,
            },
        )
    )
    console.print(Panel(f"[green]Profile '{name}' created[/green]"))


@app.command(name="profile-list")
def profile_list() -> None:
    """List prompt profiles."""
    result = _run(_client().list_profiles())
    table = Table(title="Prompt Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    for p in result:
        table.add_row(p.get("name", ""), p.get("description", ""))
    console.print(table)


@app.command()
def models() -> None:
    """List available LLM providers and models."""
    ns = _client()
    providers = ns.list_models()
    table = Table(title="LLM Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Models")
    for p in providers:
        table.add_row(p.get("provider", ""), p.get("status", ""), p.get("models", ""))
    console.print(table)


if __name__ == "__main__":
    app()
