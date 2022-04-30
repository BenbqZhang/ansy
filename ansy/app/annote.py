from pathlib import Path

import json

settings = {}


def load_settings(file_path: Path):
    with open(file_path, "r") as file:
        user_settings = json.load(file)

        # append user setttings to global settings
        global settings
        settings = {**settings, **user_settings}
