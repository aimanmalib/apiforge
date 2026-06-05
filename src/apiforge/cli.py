"""Click CLI for APIForge."""

from __future__ import annotations
import asyncio
from pathlib import Path
import click
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from .pipeline import APIForgePipeline
from .token_tracker import TokenTracker

console = Console()


@click.group()
def main():
    """APIForge -- 8-Agent API Scaffolding Engine for any OpenAI-compatible LLM."""


@main.command()
@click.argument("description")
@click.option("--output", "-o", default="./output", help="Output directory")
def generate(description: str, output: str):
    """Generate a complete API from natural language description."""

    async def _run():
        pipeline = APIForgePipeline()
        result = await pipeline.generate(description)
        out = Path(output)
        out.mkdir(parents=True, exist_ok=True)
        (out / "openapi.json").write_text(str(result.openapi_spec))
        (out / "routes.py").write_text(result.router_code)
        (out / "models.py").write_text(result.model_code)
        (out / "auth.py").write_text(result.auth_code)
        (out / "test_api.py").write_text(result.test_code)
        (out / "API.md").write_text(result.docs)
        console.print(f"[green]Generated API files in {out}[/]")
        console.print(Syntax(result.router_code[:500], "python"))
        v = result.validation
        color = "green" if v.valid else "red"
        console.print(
            f"[{color}]Validation: {v.score}/100[/] ({len(v.errors)} errors, {len(v.warnings)} warnings)"
        )

    asyncio.run(_run())


@main.command()
def stats():
    """Show token usage statistics."""
    table = Table(title="APIForge -- Daily Token Estimates")
    table.add_column("Agent", style="cyan")
    table.add_column("Est. Tokens/Day", justify="right", style="green")
    total = sum(TokenTracker.DAILY_ESTIMATES.values())
    for agent, tokens in TokenTracker.DAILY_ESTIMATES.items():
        share = tokens / total * 100
        table.add_row(agent, f"{tokens:.2f}M ({share:.0f}%)")
    table.add_row("[bold]TOTAL[/]", f"[bold]{total:.2f}M[/]")
    console.print(table)


@main.command()
@click.argument("spec_file", type=click.Path(exists=True))
def validate(spec_file: str):
    """Validate an OpenAPI spec file."""
    import json

    content = Path(spec_file).read_text()
    try:
        spec = json.loads(content)
    except json.JSONDecodeError:
        console.print("[red]Invalid JSON[/]")
        return

    async def _run():
        pipeline = APIForgePipeline()
        result = await pipeline.validator.validate(spec=spec)
        console.print(f"Valid: {result.valid} | Score: {result.score}/100")
        for e in result.errors:
            console.print(f"  [red]ERROR:[/] {e}")
        for w in result.warnings:
            console.print(f"  [yellow]WARN:[/] {w}")
        await pipeline.client.close()

    asyncio.run(_run())


if __name__ == "__main__":
    main()
