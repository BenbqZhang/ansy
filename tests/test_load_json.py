from pathlib import Path


from ansy.app import annote as annoteapp


def test_load_settings():
    config_file = Path("testData/subject1/config.json")
    annoteapp.load_settings(config_file)

    assert "labels" in annoteapp.settings
    assert "pagesize" in annoteapp.settings
    assert len(annoteapp.settings["labels"]) == 3
    assert annoteapp.settings["pagesize"] == 50000
