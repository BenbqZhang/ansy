from typing import List
from pathlib import Path

from collections import namedtuple

import pandas as pd

from dash import Dash, html, Input, Output, dcc
import plotly.express as px

DataItem = namedtuple("DataItem", ["id", "filename", "dataframe"])


def create_figure(dataframe):
    fig = px.line(dataframe)
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=3, label="3s", step="second", stepmode="backward"),
                    dict(count=5, label="5s", step="second", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        ),
    )
    return fig


class SyncApp:
    def __init__(self, data_items: List[DataItem], data_dir: Path):
        self.data_items = data_items
        self.data_dir = data_dir
        self.curr_xaxis = {item.id: 0 for item in data_items}
        self.app = Dash(__name__)

        self.init_app_layout()

    def init_app_layout(self):
        def apply_callback(data_item):
            @self.app.callback(
                Output(f"{data_item.id}-x-axis-info", "children"),
                Input(f"{data_item.id}-graph", "relayoutData"),
            )
            def update_xaxis(relayoutData):
                if relayoutData and "xaxis.range[0]" in relayoutData:
                    self.curr_xaxis[data_item.id] = relayoutData["xaxis.range[0]"]
                return f"x-axis: {str(self.curr_xaxis[data_item.id])}"

        def generate_item_details():
            for item in self.data_items:
                detail_component = html.Details(
                    children=[
                        html.Summary(item.filename),
                        html.P(id=f"{item.id}-x-axis-info"),
                        html.Br(),
                        dcc.Graph(
                            id=f"{item.id}-graph", figure=create_figure(item.dataframe)
                        ),
                    ]
                )

                apply_callback(item)

                yield detail_component

        @self.app.callback(
            Output("save-btn-msg", "children"), Input("save-sync-res-btn", "n_clicks")
        )
        def save_sync_result(n_clicks):
            if n_clicks and n_clicks > 0:
                msg = self.write_sync_result_to_file()
                return msg
            return ""

        self.app.layout = html.Div(
            [
                html.H1("Time Series Data Synchronization Tool"),
                html.Hr(),
                *generate_item_details(),
                html.Hr(),
                html.Button(id="save-sync-res-btn", children="save sync result"),
                html.P(id="save-btn-msg"),
            ]
        )

    def write_sync_result_to_file(self) -> str:
        result_filename = "sync_result.txt"
        result_file_path = self.data_dir / result_filename

        with open(result_file_path, "w") as res_file:
            for item in self.data_items:
                line = f"{item.filename},{self.curr_xaxis[item.id]}\n"
                res_file.write(line)

        message = f"written result to file {result_filename}"
        return message

    def run_app(self):
        self.app.run_server(debug=True)


def load_all_data(data_files: List[Path]) -> List[DataItem]:
    data_items = []

    counter = 1
    for path in data_files:
        id = f"{path.stem}-{str(counter)}"
        counter += 1
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        data_items.append(DataItem(id, path.name, df))

    return data_items


def run_dash_app(data_files: List[Path], data_dir: Path):
    data_items = load_all_data(data_files)

    SyncApp(data_items, data_dir).run_app()
