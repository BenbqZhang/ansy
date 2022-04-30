from typing import Optional
from pathlib import Path

import typer

from ansy.app import sync as syncapp
from ansy.app import align as alignapp
from ansy.app import annotate as annotateapp

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


@cliapp.command()
def align(
    data_dir: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=True,
        readable=True,
        help="The data directory. Contains csv files which want to be aligned.",
    ),
    output_dir: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=True,
        writable=True,
        help="The output directory. The aligned data will saved in this directory.",
    ),
    sync_file: Path = typer.Option(
        ...,
        "--sync-file",
        "-s",
        exists=True,
        file_okay=True,
        readable=True,
        help="The sync result file. data files will be aligned based on this file.",
    ),
):
    alignapp.align_data(data_dir, output_dir, sync_file)


@cliapp.command()
def annotate(
    datafile: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        readable=True,
        help="The data file which want to be annotated.",
    ),
    result_path: Path = typer.Argument(..., help="The annotation result file."),
    config: Optional[Path] = typer.Option(
        None, help="The user settings file. Only json format is supported at present."
    ),
):
    annotateapp.run_dash_app(datafile, result_path, config)


@cliapp.callback()
def callback():
    """
    ansy is a tool for ANnnotating and SYnchronizing wearable sensor data.
    """
