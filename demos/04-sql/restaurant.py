#!/usr/bin/env python3
"""Read-only queries against the demos/04-sql restaurant schema."""

import os

import mysql.connector

DBHOST = os.environ.get("DBHOST", "ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com")
DBUSER = os.environ.get("DBUSER", "ds2022")  # shared account
DBPASS = os.environ.get("DBPASS", "")  # password on Canvas
DBNAME = os.environ.get("DBNAME", "restaurant_003")  # or restaurant_001 / _002


def main():
    """Connect, list employees with home state, then close."""
    conn = mysql.connector.connect(
        host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME
    )
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM employees ORDER BY employee_id")
        print("=== employees ===")
        for row in cursor.fetchall():
            print(row)

        query = """
            SELECT e.employee_id, e.name, s.home_state
            FROM employees e
            LEFT JOIN states s ON e.state_id = s.state_code
            ORDER BY e.employee_id
        """
        cursor.execute(query)
        print("=== employees with home state ===")
        for row in cursor.fetchall():
            print(row)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
