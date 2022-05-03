# ansy

ansy is a tool for **AN**nnotating and **SY**nchronizing wearable sensor data

**WIP**!

## Usage

run `poetry run ansy --help`:

```
Usage: ansy [OPTIONS] COMMAND [ARGS]...

  ansy is a tool for ANnnotating and SYnchronizing wearable sensor data.

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.
  --help                Show this message and exit.

Commands:
  align
  annotate
  sync
```

### Synchronization

run `poetry run ansy sync --help`:

```
Usage: ansy sync [OPTIONS] INPUT_DIR

Arguments:
  INPUT_DIR  The input directory. Contains csv files which want to be
             synchronized.  [required]

Options:
  --help  Show this message and exit.
```

### Alignment

run `poetry run ansy align --help`:

```
Usage: ansy align [OPTIONS] DATA_DIR OUTPUT_DIR

Arguments:
  DATA_DIR    The data directory. Contains csv files which want to be aligned.
              [required]
  OUTPUT_DIR  The output directory. The aligned data will saved in this
              directory.  [required]

Options:
  -s, --sync-file PATH  The sync result file. data files will be aligned based
                        on this file.  [required]
  --help                Show this message and exit.
```

### Annotation

run `poetry run ansy annotate --help`:

```
Usage: ansy annotate [OPTIONS] DATAFILE RESULT_PATH

Arguments:
  DATAFILE     The data file which want to be annotated.  [required]
  RESULT_PATH  The annotation result file.  [required]

Options:
  --config PATH  The user settings file. Only json format is supported at
                 present.
  --help         Show this message and exit.
```
