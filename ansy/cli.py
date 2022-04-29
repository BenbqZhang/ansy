from pathlib import Path

import typer

app = typer.Typer()


@app.command()
def sync(
    input_dir: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=True,
        readable=True,
        help="The input directory. Contains csv files which want to be synchronized.",
    )
):
    data_files = input_dir.glob("*.csv")
    for file in data_files:
        typer.echo(file.name)


@app.callback()
def callback():
    """
    ansy is a tool for ANnnotating and SYnchronizing wearable sensor data.
    """
