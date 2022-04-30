from pathlib import Path

import typer

from ansy.app import sync as syncapp

cliapp = typer.Typer()


@cliapp.command()
def sync(
    input_dir: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=True,
        readable=True,
        help="The input directory. Contains csv files which want to be synchronized.",
    )
):
    data_files = list(input_dir.glob("*.csv"))
    syncapp.run_dash_app(data_files, input_dir)


@cliapp.callback()
def callback():
    """
    ansy is a tool for ANnnotating and SYnchronizing wearable sensor data.
    """
