import pandas as pd
import duckdb as duck
from pathlib import Path

def hello() -> str:
    return "Hello from daforfer!"


class DaforferDB:
    def __init__(self, db_path="analysis.duckdb"):
        """
        DaforferDB is an object that eases the
        on the fly storage of pandas dataframes

        """

        self.db_path = db_path
        self.conn = duck.connect(database=self.db_path, read_only=False)
        self.conn.sql(
            """
            CREATE TABLE IF NOT EXISTS toc (
                name VARCHAR(255) PRIMARY KEY,
                description VARCHAR(4096)
            )
            """
        )

    def toc(self):

        return self.conn.sql("SELECT * FROM toc")

    def save_dataframe(self, df: pd.DataFrame, table_name: str, description: str, overwrite=True):
        """Save a DataFrame to the database."""
        if overwrite:
            self.conn.execute(f"INSERT OR REPLACE INTO toc (name, description) VALUES (?, ?)", [table_name, description])
        else:
            self.conn.execute(f"INSERT INTO toc (name, description) VALUES (?, ?)", [table_name, description])
                
        self.conn.register(table_name, df)
        if overwrite:
            self.conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM {table_name}")
        else:
            self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM {table_name}")
        print(f"Saved {table_name} to {self.db_path}")

    def export_to_excel(self, output_path="analysis_results.xlsx"):
        """Export all tables to Excel (one sheet per table)."""
        tables = self.conn.execute("SHOW TABLES").fetchdf()
        with pd.ExcelWriter(output_path) as writer:
            for table in tables["name"].values:
                df = self.conn.execute(f"SELECT * FROM {table}").fetchdf()
                df.to_excel(writer, sheet_name=table, index=False)
        print(f"Exported all tables to {output_path}")

    def close(self):
        self.conn.close()
