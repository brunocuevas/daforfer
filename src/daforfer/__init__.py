import pandas as pd
import duckdb as duck
from pathlib import Path

def hello() -> str:
    """Return a short greeting from the package.

    Returns:
        str: Simple greeting text (e.g. "Hello from daforfer!").
    """
    return "Hello from daforfer!"


class DaforferDB:
    """Lightweight helper around a DuckDB database for storing DataFrames and single values.

    This class manages two metadata tables created automatically on init:
      - toc: table of contents for stored DataFrames (columns: name, description)
      - tov: table of values (columns: name, description, value, type)

    The object exposes convenience methods to save/load DataFrames, export all tables
    to an Excel file, and store/retrieve simple scalar values.
    """

    def __init__(self, db_path="analysis.duckdb"):
        """
        Open or create a DuckDB database and ensure metadata tables are present.

        Args:
            db_path (str | Path): Path to the DuckDB file. If it does not exist it will be created.

        Side effects:
            - Opens a DuckDB connection stored on self.conn
            - Ensures 'toc' and 'tov' tables exist

        Returns:
            None
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
        self.conn.sql(
            """
            CREATE TABLE IF NOT EXISTS tov (
                name VARCHAR(255) PRIMARY KEY,
                description VARCHAR(4096),
                value DOUBLE,
                type VARCHAR(255)
            )
            """
        )

    def toc(self):
        """Return a query relation for the 'toc' (table of contents).

        The returned object is a DuckDB relation-like object (has .df() to fetch a pandas.DataFrame).

        Returns:
            duckdb.DuckDBPyRelation: Relation representing rows in the 'toc' table
                                    (columns: name, description).
        """
        return self.conn.sql("SELECT * FROM toc")
    
    def tov(self):
        """Return a query relation for the 'tov' (table of values).

        Returns:
            duckdb.DuckDBPyRelation: Relation representing rows in the 'tov' table
                                    (columns: name, description, value, type).
        """
        return self.conn.sql("SELECT * FROM tov")

    def save_dataframe(self, df: pd.DataFrame, table_name: str, description: str, overwrite=True):
        """Save a pandas DataFrame into the database as a table and register it in toc.

        This method:
          - Inserts or inserts-or-replaces an entry in the 'toc' metadata table.
          - Registers the provided DataFrame under the provided name and creates a physical
            table with that name in the DuckDB database.
          - Prints a short confirmation message.

        Args:
            df (pandas.DataFrame): DataFrame to persist.
            table_name (str): Target table name in the database.
            description (str): Human readable description stored in toc.
            overwrite (bool): If True, replace existing toc entry and table. If False, an attempt
                              to insert duplicate toc entry or table will raise an exception.

        Returns:
            duckdb.DuckDBPyConnection or duckdb.DuckDBPyResult: Result of the last execute call.

        Raises:
            duckdb.ConstraintException: If overwrite=False and a duplicate toc entry is inserted.
        """
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
        """Export every table in the database to an Excel file, one sheet per table.

        Args:
            output_path (str | Path): Path for the generated .xlsx file.

        Side effects:
            - Writes an Excel workbook with a sheet per table name containing the table contents.

        Returns:
            None
        """
        tables = self.conn.execute("SHOW TABLES").fetchdf()
        with pd.ExcelWriter(output_path) as writer:
            for table in tables["name"].values:
                df = self.conn.execute(f"SELECT * FROM {table}").fetchdf()
                df.to_excel(writer, sheet_name=table, index=False)
        print(f"Exported all tables to {output_path}")

    def get_table(self, table_name):
        """Fetch a table as a pandas DataFrame.

        Args:
            table_name (str): Name of the table to fetch.

        Returns:
            pandas.DataFrame: Contents of the named table.

        Raises:
            duckdb.Error: If the table does not exist or the query fails.
        """
        return self.conn.sql('SELECT * FROM {:s}'.format(table_name)).df()

    def remove_table(self, table_name):
        """Remove a table and its toc entry.

        This deletes the metadata row from 'toc' and drops the physical table.

        Args:
            table_name (str): Name of the table to remove.

        Returns:
            duckdb.DuckDBPyRelation or duckdb.DuckDBPyResult: Result of the DROP TABLE command.
        """
        self.conn.sql("DELETE FROM toc WHERE name = {:s};".format(table_name))
        return self.conn.sql('DROP TABLE {:s}'.format(table_name))
    
    def add_value(self, name: str, description: str, value: float, type: str, overwrite=True):
        """Store a single scalar value in the 'tov' table.

        Args:
            name (str): Unique key name for the value.
            description (str): Description of the value.
            value (float): The numeric value to store.
            type (str): A short string describing the type (e.g. 'float', 'int', 'str').
            overwrite (bool): If True, replace existing entry. If False and a duplicate exists,
                              a duckdb.ConstraintException is caught and a KeyError is raised.

        Returns:
            duckdb.DuckDBPyConnection or duckdb.DuckDBPyResult: Result of the executed insert statement.

        Raises:
            KeyError: If overwrite=False and the name already exists (duplicate).
        """
        if overwrite:
            return self.conn.execute(
            "INSERT OR REPLACE INTO tov (name, description, value, type) VALUES (?, ?, ?, ?)",
            [name, description, value, type],
            )
        else:
            try:
                return self.conn.execute(
                    "INSERT INTO tov (name, description, value, type) VALUES (?, ?, ?, ?)",
                    [name, description, value, type],
                )
            except duck.ConstraintException:
                raise KeyError(f"cannot use duplicated {name} and overwrite {overwrite}")
            
    def get_value(self, name: str): 
        """Retrieve a stored value by name.

        Args:
            name (str): Key name of the stored value.

        Returns:
            pandas.DataFrame: DataFrame with matching rows from 'tov' (columns: name, description, value, type).
        """
        return self.conn.execute('SELECT * FROM tov WHERE name = ?', [name]).df()
        
    def remove_value(self, name: str):
        """Delete a value from 'tov' by name.

        Args:
            name (str): Key name to delete.

        Returns:
            duckdb.DuckDBPyResult: Result of the DELETE operation.
        """
        return self.conn.execute("DELETE FROM tov WHERE name = ?", [name])
            
    
    def close(self):
        """Close the underlying DuckDB connection.

        After calling this method the DaforferDB instance should not be used.

        Returns:
            None
        """
        self.conn.close()
