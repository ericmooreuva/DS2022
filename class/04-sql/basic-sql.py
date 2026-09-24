#!/usr/bin/env python3

"""Basic MySQL examples matching basic-sql.ipynb (media.MOCK_DATA)."""

import json
import os

import matplotlib.pyplot as plt
import mysql.connector
import pandas as pd

# Same defaults as basic-sql.ipynb; override with env vars if set.
DBHOST = os.environ.get("DBHOST", "ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com")
DBUSER = os.environ.get("DBUSER", "ds2022")
DBPASS = os.environ.get("DBPASS", "")  # password on Canvas
DBNAME = os.environ.get("DBNAME", "people")  # MOCK_DATA lives here

db = mysql.connector.connect(user=DBUSER, host=DBHOST, password=DBPASS, database=DBNAME)
cur = db.cursor()


def get_people_list():
    """Return MOCK_DATA rows with id between 6 and 19 as a list of tuples."""
    query = "SELECT * FROM MOCK_DATA WHERE id > 5 AND id < 20 ORDER BY last_name;"
    try:
        cur.execute(query)
        results = cur.fetchall()
        output = []
        for r in results:
            output.append(r)
        return output
    except mysql.connector.Error as e:
        print("MySQL Error: ", str(e))
        return None


def get_people_json():
    """Return the same id-filtered MOCK_DATA rows as a JSON string of objects."""
    query = "SELECT * FROM MOCK_DATA WHERE id > 5 AND id < 20 ORDER BY last_name;"
    try:
        cur.execute(query)
        headers = [x[0] for x in cur.description]
        results = cur.fetchall()
        json_data = []
        for result in results:
            json_data.append(dict(zip(headers, result)))
        return json.dumps(json_data)
    except mysql.connector.Error as e:
        print("MySQL Error: ", str(e))
        return None


def get_people_by_lastname(lname):
    """Return MOCK_DATA rows whose last_name matches ``lname`` (list of tuples)."""
    query = "SELECT * FROM MOCK_DATA WHERE last_name = %s;"
    try:
        cur.execute(query, (lname,))
        results = cur.fetchall()
        output = []
        for r in results:
            output.append(r)
        return output
    except mysql.connector.Error as e:
        print("MySQL Error: ", str(e))
        return None


def get_people_dataframe():
    """Load up to 200 MOCK_DATA rows into a pandas DataFrame, ordered by last_name."""
    query = "SELECT * FROM MOCK_DATA ORDER BY last_name LIMIT 200;"
    try:
        cur.execute(query)
        results = cur.fetchall()
        output = []
        for result in results:
            output.append(result)
        columns = ["ID", "Fname", "Lname", "Email", "IP", "Continent"]
        return pd.DataFrame(output, columns=columns)
    except mysql.connector.Error as e:
        print(e)
        return None


def plot_continent_counts():
    """Count people per continent, show a bar chart, and return the DataFrame."""
    query = "SELECT continent, COUNT(continent) FROM MOCK_DATA GROUP BY continent;"
    try:
        cur.execute(query)
        results = cur.fetchall()
        output = []
        for r in results:
            output.append(r)
        df = pd.DataFrame(output)
        df.plot.bar(x=0, y=1)
        plt.tight_layout()
        plt.show()
        return df
    except mysql.connector.Error as e:
        print("MySQL Error: ", str(e))
        return None


def main():
    """Run the demo queries and close the database connection."""
    print("=== list ===")
    print(get_people_list())

    print("=== json ===")
    print(get_people_json())

    print("=== by last name ===")
    print(get_people_by_lastname("Abate"))

    print("=== dataframe ===")
    df = get_people_dataframe()
    if df is not None:
        print(df)
        print(df[df["Lname"] == "Danels"])
        print(df[df["ID"] > 100].sort_values(by=["ID"]))

    print("=== plot ===")
    plot_continent_counts()

    cur.close()
    db.close()


if __name__ == "__main__":
    main()
