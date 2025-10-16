# Daforfer

## Summary

Too many times, big analysis in Python end up a pile of
many different jupyter-notebooks with another pile of
data files around them. Ideally, we would like to have
a way to keep the data all together (specially when we
are talking about data that powers important figures
and statistical tests).

´Daforfer´ comes to ease addressing some of these
issues. The idea is very simple:

1. Do you analysis in regular Pandas
2. When you are very happy with one table (e.g. before
making a plot), save it into a DuckDB instance together
with a small explanation of what's the table.
3. At the end of the analysis, simply dump it into an
excel spreadsheet.

This way, you will be able to have access to all the data
of your analysis without having to navigate an endless
maze of files.

## Installation

Just clone it somewhere and run.

  pip install .

## Example

You might have an Jupyter-notebook looking like this.

```{python}
  DB = daforfer("2025-10-16") # We declare the database
  df = pd.read_csv("data.csv") # this could be also a SQL query
  df['number'] = df['another_number'].some_function()
  df_agg = df.groupby(['factor']).sum()
  DB.add_table(db, df_agg, name="groupby-factor", description="aggregation of some number by factor on data.csv")
  DB.contents() # This should show a dataframe that contains groupby-factor
```

We might keep adding tables and so on, and if we want to,
querying them. Finally, once we are done, we might run
a dump command to generate a single excel file that contains all data.

```{shell}
  daforfer-dump 2025-10-16 -o dump.2025-10-16.xlsx
```


## FAQ

For any question
