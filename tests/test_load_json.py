from pathlib import Path


from ansy.app import annotate as annotateapp


def test_load_settings():
    config_file = Path("testData/subject1/config.json")
    annotateapp.load_settings(config_file)

    assert "labels" in annotateapp.settings
    assert "pagesize" in annotateapp.settings
    assert len(annotateapp.settings["labels"]) == 3
    assert annotateapp.settings["pagesize"] == 50000
