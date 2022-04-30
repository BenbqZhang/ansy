from pathlib import Path
from typing import List

from datetime import timedelta

from collections import namedtuple

import pandas as pd

sync_file_xaxis = {}

FileDataFrame = namedtuple("FileDataFrame", ["filename", "dataframe"])


def load_sync_file(sync_file: Path):
    with open(sync_file, "r") as f:
        lines = (line.rstrip() for line in f)
        lines = (line for line in lines if line)  # Non-blank lines
        for line in lines:
            filename, xaxis = line.split(",")
            xaxis = pd.to_datetime(xaxis)
            sync_file_xaxis[filename] = xaxis


def load_data_files(data_dir: Path):
    data_files = data_dir.glob("*.csv")
    for file in data_files:
        df = pd.read_csv(file, index_col=0, parse_dates=True)
        yield FileDataFrame(file.name, df)


def align_dataframe(base: FileDataFrame, to_aligned: FileDataFrame) -> FileDataFrame:
    getxaxis = lambda *dfs: [sync_file_xaxis[df.filename] for df in dfs]
    base_xaxis, to_aligned_xaxis = getxaxis(base, to_aligned)

    origin_offset = (
        to_aligned.dataframe.index[0] - base.dataframe.index[0]
    ).to_pytimedelta()
    origin_offset = int(origin_offset / timedelta(milliseconds=1))

    manual_sync_offset = int(
        (to_aligned_xaxis - base_xaxis) / timedelta(milliseconds=1)
    )

    offset = manual_sync_offset - ((manual_sync_offset % 10) - (origin_offset % 10))

    aligned_df = to_aligned.dataframe.copy()
    aligned_df.index = to_aligned.dataframe.index.shift(-offset, freq="ms")

    return FileDataFrame(to_aligned.filename, aligned_df)


def truncate_datas(datas: List[FileDataFrame]) -> List[FileDataFrame]:
    get_index_start = lambda data: data.dataframe.index[0]
    get_index_end = lambda data: data.dataframe.index[-1]

    trun_start = max(map(get_index_start, datas))
    trun_end = min(map(get_index_end, datas))

    return [
        FileDataFrame(
            data.filename, data.dataframe.truncate(before=trun_start, after=trun_end)
        )
        for data in datas
    ]


def save_aligned_data(output_dir: Path, datas: List[FileDataFrame]):
    for data in datas:
        saved_path = output_dir / data.filename
        data.dataframe.to_csv(saved_path)


def align_data(data_dir: Path, output_dir: Path, sync_file: Path):
    load_sync_file(sync_file)

    filedataframes = list(load_data_files(data_dir))

    base_data = filedataframes[0]
    to_aligned_datas = filedataframes[1:]

    aligned_datas = [base_data]

    for to_aligned in to_aligned_datas:
        aligned_datas.append(align_dataframe(base_data, to_aligned))

    truncated_aligned_datas = truncate_datas(aligned_datas)

    save_aligned_data(output_dir, truncated_aligned_datas)
