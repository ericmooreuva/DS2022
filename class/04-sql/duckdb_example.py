#!/usr/bin/env python3
"""Load a small in-memory DataFrame into a local DuckDB database.

DuckDB is an in-process SQL engine: it runs inside your Python process (no
server) and can store tables in a local file such as demo.duckdb.
"""

import duckdb
import pandas as pd

DB_FILE = "demo.duckdb"
TABLE = "demo"


def main():
    """Build a DataFrame in memory and write it into a DuckDB file."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "name": ["Alice", "Bob", "Carol", "Dave"],
            "group": ["A", "B", "A", "C"],
            "score": [88, 72, 95, 81],
        }
    )
    print(f"Built DataFrame with {len(df)} rows")
    print(df)

    con = duckdb.connect(DB_FILE)
    try:
        # DuckDB can create a table directly from a pandas DataFrame
        con.execute(f"CREATE OR REPLACE TABLE {TABLE} AS SELECT * FROM df")

        count = con.execute(f"SELECT COUNT(*) FROM {TABLE}").fetchone()[0]
        print(f"{count} rows found in {DB_FILE} table '{TABLE}'")

        print("Reading table back into a pandas DataFrame")
        new_df = con.execute(f"SELECT * FROM {TABLE}").fetchdf()
        print(new_df)
    finally:
        con.close()


if __name__ == "__main__":
    main()
