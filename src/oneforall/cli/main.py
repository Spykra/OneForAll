import typer

app = typer.Typer()


@app.command()
def demo(topic: str) -> None:  # noqa: D401
    """Print a placeholder message."""
    print(f"OneForAll demo: received topic='{topic}'")
