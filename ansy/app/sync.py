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
    def __init__(self, data_items: List[DataItem]):
        self.data_items = data_items
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

        self.app.layout = html.Div(
            [
                html.H1("Time Series Data Synchronization Tool"),
                html.Hr(),
                *generate_item_details(),
            ]
        )

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


def run_dash_app(data_files: List[Path]):
    data_items = load_all_data(data_files)

    SyncApp(data_items).run_app()
