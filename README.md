# Daforfer

Lightweight, reproducible data snapshots for analysis projects.

## Overview

Daforfer helps you keep the important intermediary tables and single numeric values produced during an analysis together in a small DuckDB database. The idea is to make it easy to:

- Save DataFrames (with a short description) into a single, versionable DuckDB file.
- Record single scalar values (metrics, statistics) with descriptions.
- Export all stored artifacts to a single Excel workbook for sharing or archival.

This repository provides the core Python helper `DaforferDB` plus a small CLI entrypoint to export a DuckDB file into Excel. The server/web UI component is under development and intentionally excluded from this README because it's not ready for deployment.

## Features

- Persist pandas.DataFrame objects into DuckDB tables and keep a human-readable "table of contents" (toc) with descriptions.
- Persist scalar values (named metrics) into a separate metadata table (tov) with types and descriptions.
- Export all tables as an Excel workbook (one sheet per table).
- Simple Python API and a command line utility (`daforfer-dump`) for exporting a DB file to Excel.

## Why use Daforfer

- Avoid scattered CSV/Excel files across notebooks and scripts.
- Keep analysis artifacts and short text descriptions together alongside your code.
- Make reproducible snapshots easy to export and share.

## Installation

Install from the project root (recommended in a virtualenv):

```bash
pip install .
```

Requirements (from pyproject.toml): duckdb, pandas, click, openpyxl, streamlit (streamlit used by the server UI, optional for now).

## Quickstart (Python API)

The main entrypoint is the `DaforferDB` class which wraps a DuckDB connection and provides convenience methods.

Example usage in a notebook or script:

```python
from daforfer import DaforferDB
import pandas as pd

# Create or open a database file
db = DaforferDB(db_path="analysis.duckdb")

# Create a DataFrame
df = pd.DataFrame({"group": ["A", "B", "A"], "value": [1, 2, 3]})

# Save the DataFrame into the DB and register it in the table-of-contents
db.save_dataframe(df, table_name="example_group", description="Example aggregation input", overwrite=True)

# List tables (returns a DuckDB relation with .df())
toc_df = db.toc().df()
print(toc_df)

# Read a table back to a pandas DataFrame
df_loaded = db.get_table("example_group")

# Store a single scalar value (e.g. a statistic)
db.add_value("example-metric", "Mean value of groups", 2.0, "float", overwrite=True)

# Export everything to an Excel workbook
db.export_to_excel("analysis_snapshot.xlsx")

# Close when done
db.close()
```

## CLI: Export a DuckDB file to Excel

The package exposes a small CLI entrypoint `daforfer-dump` which wraps the same export functionality. Usage:

```bash
daforfer-dump path/to/analysis.duckdb path/to/output.xlsx
```

On success it prints a confirmation message. The CLI is defined in `pyproject.toml` as `daforfer-dump = "daforfer.scripts:db_to_excel"`.

## API Reference (summary)

The public API surface is intentionally small.

- `hello() -> str` — tiny helper returning a greeting string.

- `DaforferDB(db_path: str | Path)` — main class. On initialization it opens (or creates) a DuckDB database and ensures two metadata tables exist:
  - `toc` (table-of-contents): columns (name, description)
  - `tov` (table-of-values): columns (name, description, value, type)

Core methods on `DaforferDB`:

- `save_dataframe(df: pandas.DataFrame, table_name: str, description: str, overwrite: bool = True)`
  - Registers the DataFrame under `table_name` and creates a physical table in DuckDB.
  - Inserts or replaces the `toc` entry when `overwrite=True`.

- `get_table(table_name: str) -> pandas.DataFrame`
  - Returns the contents of the named table as a pandas.DataFrame.

- `remove_table(table_name: str)`
  - Deletes the `toc` entry and drops the physical table.

- `toc()` / `tov()`
  - Return DuckDB relation objects for the metadata tables. Call `.df()` on them to get pandas DataFrames.

- `add_value(name: str, description: str, value: float, type: str, overwrite: bool = True)`
  - Insert or replace a scalar value in `tov`. When `overwrite=False` a duplicate may raise and be translated to a KeyError.

- `get_value(name: str)` / `remove_value(name: str)`
  - Retrieve or delete scalar values from `tov`.

- `export_to_excel(output_path: str | Path)`
  - Exports every table in the database to an Excel workbook (one sheet per table). Uses pandas + openpyxl.

- `close()`
  - Close the underlying DuckDB connection.

For more details refer to the code in `src/daforfer/__init__.py`.

## Examples and patterns

- Keep a single `analysis.duckdb` file per project or experiment run (date-stamped files are useful).
- Use descriptive `table_name` and `description` values so the exported workbook is self-documenting.
- Use `tov` to store final numeric results to display on dashboards or to assert in tests.

## Tests

There are unit tests under `test/` that exercise basic behaviors: creating a DB instance, saving/reading tables, exporting to Excel, and the `tov` value storage. Run them with the standard Python `unittest` runner or with `pytest` if installed:

```bash
python -m unittest discover -v
# or, using pytest if available
pytest -q
```

Note: Tests create local files like `test.db` and `test.xlsx` in the working directory — cleaning them after runs is a good idea in automated CI jobs.

## Development & Contributing

- Fork and make a branch for each feature or bugfix.
- Keep changes small and include tests for new behaviors.
- Run the test suite locally before opening a pull request.

Planned/optional items (roadmap — server excluded)

- Improve metadata schema to store author/creation timestamps.
- Add utilities for dataset versioning and simple diffs between tables.
- The server/UI component (streamlit) is in early development and will be documented once it's ready for deployment.

## Security and privacy

The DuckDB files may contain sensitive data. Treat them like any other dataset: store them securely and avoid committing them to public repositories.

## License

This project does not include an explicit license file in the repository. If you intend to open-source it, add a LICENSE (for example MIT) and update `pyproject.toml` accordingly.

## Contact

For bugs or feature requests, please open an issue in the repository.

