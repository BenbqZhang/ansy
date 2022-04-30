from typing import Optional
from pathlib import Path

import json

import math
import pandas as pd
from pandas import DataFrame

from dash import Dash, html, Input, Output, dcc
import plotly.express as px

settings = {"labels": ["defualt"], "pagesize": 1000}


def load_data_csv(file_path: Path) -> DataFrame:
    return pd.read_csv(file_path, index_col=0, parse_dates=True)


def color_map(s):
    """
    Get color hex string based on the hash code of string.
    """
    return "#%06X" % (hash(s) % 0x1000000)


def create_figure(dataframe):
    fig = px.line(dataframe)
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="5s", step="second", stepmode="backward"),
                    dict(count=2, label="10s", step="second", stepmode="backward"),
                    dict(count=3, label="15s", step="second", stepmode="backward"),
                    dict(count=5, label="20s", step="second", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        ),
    )
    return fig


class AnnotateApp:
    def __init__(self, datafile: Path, result_path: Path):
        self.datafile = datafile
        self.datadf = load_data_csv(datafile)

        self.result_path = result_path

        self.range_left = 0
        self.range_right = 0
        self.annotate_left = 0
        self.annotate_right = 0
        self.current_page = 0

        self.left_clicks_old = 0
        self.right_clicks_old = 0
        self.submit_clicks_old = 0

        self.current_label = ""
        self.annotated_labels = []

        self.figure_frame = create_figure(self.datadf)

        self.app = Dash(__name__)

        self.init_app_layout()
        self.apply_callback()

    def init_app_layout(self):
        page_number = math.ceil(len(self.datadf) / settings["pagesize"])

        self.app.layout = html.Div(
            [
                html.H1("Time Series Data Annotation Tool"),
                html.Hr(),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="annotation-dropdown", options=settings["labels"]
                        ),
                        html.Button(id="left-btn", children="left"),
                        html.Button(id="right-btn", children="right"),
                        html.Button(id="submit-btn", children="submit"),
                    ]
                ),
                dcc.Graph(id="main-graph"),
                html.P(id="current-range"),
                html.Div(id="hidden-div", style={"display": "none"}),
                dcc.Slider(1, page_number, 1, value=1, id="page-slider"),
            ]
        )

    def run_app(self):
        self.app.run_server(debug=True)

    def save_label(self, label):
        label_str = ",".join([str(lbl) for lbl in label])
        with open(self.result_path, "a") as f:
            f.write(label_str + "\n")

    def apply_callback(self):
        @self.app.callback(
            Output("current-range", "children"),
            Input("main-graph", "relayoutData"),
        )
        def update_range(relayoutData):
            if relayoutData and "xaxis.range[0]" in relayoutData:
                self.range_left, self.range_right = (
                    relayoutData["xaxis.range[0]"],
                    relayoutData["xaxis.range[1]"],
                )
            return f"{self.range_left}, {self.range_right}"

        @self.app.callback(
            Output("hidden-div", "children"), Input("annotation-dropdown", "value")
        )
        def update_current_label(value):
            if value is not None:
                self.current_label = value
            return ""

        @self.app.callback(
            Output("main-graph", "figure"),
            Input("left-btn", "n_clicks"),
            Input("right-btn", "n_clicks"),
            Input("submit-btn", "n_clicks"),
            Input("page-slider", "value"),
        )
        def update_annote(left_clicks, right_clicks, submit_clicks, slider_value):
            fig = self.figure_frame

            if slider_value != self.current_page:
                self.current_page = slider_value
                start = (self.current_page - 1) * settings["pagesize"]
                end = self.current_page * settings["pagesize"]
                df = self.datadf[start:end]
                fig = create_figure(df)

            if left_clicks and left_clicks > 0 and left_clicks != self.left_clicks_old:
                self.annotate_left = self.range_left
                lcolor = color_map(self.current_label)
                fig.add_vline(
                    x=self.annotate_left,
                    line_width=3,
                    line_dash="dash",
                    line_color=lcolor,
                )
                fig.update_xaxes(range=[self.range_left, self.range_right])
                self.left_clicks_old = left_clicks

            if (
                right_clicks
                and right_clicks > 0
                and right_clicks != self.right_clicks_old
            ):
                self.annotate_right = self.range_right
                lcolor = color_map(self.current_label)
                fig.add_vline(
                    x=self.annotate_right,
                    line_width=3,
                    line_dash="dash",
                    line_color=lcolor,
                )
                fig.update_xaxes(range=[self.range_left, self.range_right])
                self.right_clicks_old = right_clicks

            if (
                submit_clicks
                and submit_clicks > 0
                and submit_clicks != self.submit_clicks_old
            ):
                self.annotated_labels.append(
                    (self.annotate_left, self.annotate_right, self.current_label)
                )

                self.save_label(self.annotated_labels[-1])

                fcolor = color_map(self.current_label)
                fig.add_vrect(
                    x0=self.annotate_left,
                    x1=self.annotate_right,
                    annotation_text=self.current_label,
                    annotation_position="top left",
                    fillcolor=fcolor,
                    opacity=0.25,
                    line_width=0,
                )
                fig.update_xaxes(range=[self.range_left, self.range_right])
                self.submit_clicks_old = submit_clicks

            self.figure_frame = fig

            return fig


def load_settings(file_path: Path):
    with open(file_path, "r") as file:
        user_settings = json.load(file)

        # append user setttings to global settings.
        # user settings have higher priority.
        global settings
        settings = {**settings, **user_settings}


def run_dash_app(datafile: Path, result_path: Path, config: Optional[Path]):
    if config:
        load_settings(config)

    AnnotateApp(datafile, result_path).run_app()
