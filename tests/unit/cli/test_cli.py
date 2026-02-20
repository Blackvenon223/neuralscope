"""Tests for CLI app registration."""

from typer.testing import CliRunner

from neuralscope.cli.app import app

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "NeuralScope" in result.stdout


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "review" in result.stdout
    assert "scan" in result.stdout
    assert "models" in result.stdout


def test_cli_models_command():
    result = runner.invoke(app, ["models"])
    assert result.exit_code == 0
    assert "LLM Providers" in result.stdout
