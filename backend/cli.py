#!/usr/bin/env python3
"""
Command-line interface for Conclave.

Usage:
    python cli.py "What is the current state of fusion energy research?"
"""

import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from app.core.config import get_settings
from app.core.graph import run_research

console = Console()


def main() -> None:
    if len(sys.argv) < 2:
        console.print("[bold red]Usage:[/] python cli.py \"<your research question>\"")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    settings = get_settings()

    console.print(
        Panel(
            f"[bold]{question}[/]",
            title="[bold yellow]Conclave — Multi-Agent Research[/]",
            subtitle=f"provider: {settings.llm_provider} · search: {settings.search_provider}",
        )
    )

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Planning subtasks, researching, and critiquing...", total=None)
        result = run_research(question)
        progress.update(task, completed=True)

    console.print()
    console.print(f"[bold cyan]Subtasks identified ({len(result['subtasks'])}):[/]")
    for i, s in enumerate(result["subtasks"], 1):
        console.print(f"  {i}. {s}")

    console.print()
    console.print(f"[bold cyan]Critique rounds used:[/] {result['round']}")

    console.print()
    table = Table(title="Findings", show_lines=True)
    table.add_column("Subtask", style="cyan", no_wrap=False)
    table.add_column("Summary", no_wrap=False)
    table.add_column("Sources", style="dim", no_wrap=False)
    for f in result["findings"]:
        table.add_row(f["subtask"], f["summary"][:200], "\n".join(f["sources"][:2]) or "—")
    console.print(table)

    console.print()
    console.print(Panel(Markdown(result["report"]), title="[bold green]Final Report[/]"))


if __name__ == "__main__":
    main()
