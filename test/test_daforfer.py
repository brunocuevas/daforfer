import unittest

class TestDaforfer(unittest.TestCase):

    def test_declaration(self):

        from daforfer import DaforferDB
        d = DaforferDB("test.db")
        self.assertIsInstance(d, DaforferDB)


    def test_register(self):

        import pandas as pd
        from daforfer import DaforferDB
        import duckdb
        db = DaforferDB(db_path="test.db")
        df = pd.DataFrame.from_records(
            [
                {"field_1": 1, "field_2": 2},
                {"field_1": 3, "field_2": 4},
                {"field_1": 5, "field_2": 6},

            ]
        )
        db.save_dataframe(df, "table1", "This is an example table", overwrite=True)
        db.save_dataframe(df, "table1", "This is an example table", overwrite=True)
        table_of_contents = db.toc().df().set_index("name")
        self.assertEqual(table_of_contents.loc["table1"].description, "This is an example table")

        with self.assertRaises(duckdb.ConstraintException):
            db.save_dataframe(df, "table1", "tasdasdsa", overwrite=False)
        


    def test_dump(self):

        import pandas as pd
        from daforfer import DaforferDB
        import duckdb
        db = DaforferDB(db_path="test.db")
        df = pd.DataFrame.from_records(
            [
                {"field_1": 1, "field_2": 2},
                {"field_1": 3, "field_2": 4},
                {"field_1": 5, "field_2": 6},

            ]
        )
        db.save_dataframe(df, "table1", "This is an example table", overwrite=True)
        db.export_to_excel(
            "test.xlsx"
        )
        u = pd.read_excel("test.xlsx")
        self.assertIsInstance(u, pd.DataFrame)

if __name__ == "__main__":
    unittest.main()
