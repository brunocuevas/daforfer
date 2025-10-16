import click
from pathlib import Path
from daforfer import DaforferDB

@click.command()
@click.argument('db_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path())
def db_to_excel(db_path, output_path):
    """
    Convert a DuckDB database to an Excel file.

    DB_PATH: Path to the DuckDB database file.
    OUTPUT_PATH: Path to save the resulting Excel file.
    """
    db = None
    try:
        db = DaforferDB(db_path)
        db.export_to_excel(output_path)
        click.echo(f"Database {db_path} successfully exported to {output_path}")
    except Exception as e:
        click.echo(f"An error occurred: {e}")
    finally:
        if db is not None:
            db.close()

if __name__ == '__main__':
    db_to_excel()