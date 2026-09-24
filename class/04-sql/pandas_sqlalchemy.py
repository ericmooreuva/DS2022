#!/usr/bin/env python3
"""Bulk-load a CSV into MySQL with pandas + SQLAlchemy (Lab 04 approach B).

#In your terminal, define the following environment variables:
#  export DBHOST='...'
#  export DBUSER='COMPUTING_ID'
#  export DBPASS='COMPUTING_ID'
#  export DBNAME='COMPUTING_ID_mock'

Put MOCK_DATA.csv in the current directory, then:
  uv run python pandas_sqlalchemy.py
"""

import os

import pandas as pd
from sqlalchemy import create_engine, text

DBHOST = os.environ.get("DBHOST")
DBUSER = os.environ.get("DBUSER")
DBPASS = os.environ.get("DBPASS")
DBNAME = os.environ.get("DBNAME")
CSV_FILE = "MOCK_DATA.csv"
TABLE = "mock"


def main():
    """Read CSV file and upload to MySQL via to_sql()."""
    if not all([DBHOST, DBUSER, DBPASS, DBNAME]):
        raise SystemExit("Set DBHOST, DBUSER, DBPASS, and DBNAME before running.")

    df = pd.read_csv(CSV_FILE)
    print(f"Loaded {len(df)} rows from {CSV_FILE}")

    # mysql+mysqlconnector://USER:PASS@HOST:PORT/DBNAME
    url = f"mysql+mysqlconnector://{DBUSER}:{DBPASS}@{DBHOST}:3306/{DBNAME}"
    engine = create_engine(url)

    try:
        # if_exists='replace' recreates the table; use 'append' to add rows
        df.to_sql(TABLE, con=engine, if_exists="replace", index=False)
        with engine.connect() as conn:
            count = conn.execute(text(f"SELECT COUNT(*) FROM `{TABLE}`")).scalar()
        print(f"Uploaded {count} rows to {DBNAME}.{TABLE}")
    except Exception as e:
        print(f"Upload failed: {e}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
