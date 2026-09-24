# Working with Relational Databases and SQL

The goal of this activity is to familiarize you with SQL (Structured Query Language) for data science. SQL is essential for querying relational databases, extracting insights from structured data, and managing data stored in database systems.

Work through the following sections in sequence:
1. [Setup](#setup): make sure `uv` and `mycli` are installed.
2. [Viewing SQL Databases in Cursor IDE](#viewing-sql-databases-in-cursor-ide): optional SQLTools setup
3. [Warmup](#warmup): Connecting and basic queries
4. [Start Lab 04](#lab-04-working-with-sql)

In addition, check out these sections for reference materials. They may come in handy for Lab 04:
* [Reference: CRUD Operations](#reference-crud-operations)
* [SQL Queries Using Python](#sql-queries-using-python) (includes [pandas and SQLAlchemy](#pandas-and-sqlalchemy) and [DuckDB](#duckdb))
* [SQL in Jupyter Notebooks](#sql-in-jupyter-notebooks)
* [Optional] Explore the [Advanced Concepts](#advanced-concepts-optional) if you wish to explore SQL in more depth.
* [Resources](#resources)

## Setup

For using SQL from the command line we are using [mycli](https://www.mycli.net/), which is fully compatible with the `mysql` command line tool. `mycli` also provides handy auto-completion features and, unlike `mysql`, it can be installed via `uv` or `pip` package managers.

Confirm that `uv` is installed.
```bash
uv --version
```

If you receive an error message, follow the [uv setup instructions](../03-scripting/README.md#setup).

```bash
uv tool install mycli
```

This will install the mycli tool in `~/.local/bin/`. Confirm:

```bash
ls -ltr ~/.local/bin
```

In order to execute `mycli` from any location on your filesystem, check if `~/.local/bin` is in your `$PATH` variable.

```bash
echo $PATH
```

If not, run one of the following commands:

**Bash shell:**

```bash
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
```

**Alternatively, Z Shell:**

```bash
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.zshrc
```

Confirm `mycli` is functional:

```bash
mycli --help
```

If you see the help text, you are good to go.

## Viewing SQL Databases in Cursor IDE

You can browse tables and run queries inside Cursor (or VS Code) instead of only using `mycli`.

Install two extensions from the Extensions view (`Cmd+Shift+X` / `Ctrl+Shift+X`):

1. **[SQLTools](https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools)** (`mtxr.sqltools`): the main SQL client UI (connections sidebar, query editor, result grid).
2. **[SQLTools MySQL/MariaDB](https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools-driver-mysql)** (`mtxr.sqltools-driver-mysql`): the driver that lets SQLTools talk to MySQL.

Then add a connection to the course RDS instance:

1. Open the SQLTools sidebar (database icon) and choose **Add New Connection**.
2. Select the **MySQL** driver.
3. Fill in:
   - **Server:** `ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com`
   - **Port:** `3306`
   - **Database:** your section DB, e.g. `restaurant_003` (or `restaurant_001` / `restaurant_002`)
   - **Username:** `ds2022`
   - **Password:** leave blank and enable **ask for password** (use the Canvas credentials when prompted)
   - **SSL:** Disabled (same as the class `mycli` setup)
4. Test and save the connection, then connect.

You can expand the connection to inspect tables, or open a `.sql` file / SQLTools notebook and run `SELECT` statements. The `ds2022` account is still read-only here.

## Warmup

Connect to the MySQL instance in AWS RDS

```bash
mycli -h ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com -P 3306 -u ds2022 -p
```

The shared `ds2022` account is **read-only**: you can run `SHOW`, `DESCRIBE`, `SELECT`, and joins, but not `CREATE`, `INSERT`, `UPDATE`, or `DELETE`. Schema setup and writes are done by the instructor. You will have full read-write access for databases in Lab 04.

**Command options explained:**
- `-h`: Specifies the server hosting the database
- `-P`: Specifies the port for communication with the DBMS on the host server (3306 is the default for MySQL)
- `-u`: Username to connect to the DBMS
- `-p`: Triggers a prompt for password (you'll enter it securely after pressing Enter)

When prompted, enter the password from **Canvas > Modules > Week 05 SQL & Relational Databases > DS2022_AWS_RDS_credentials.txt**.

**Success indicator:** You should see output like this:
```text
MySQL 8.4.9
mycli 2.25.3
Home: https://mycli.net
Bug tracker: https://github.com/dbcli/mycli/issues
Tip: use /bug to file a bug on GitHub!
ds2022@ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com
```

And the last line is your prompt. 
```text
(MySQL):(none)>
```
This indicates that you are now connected to the database instance and ready to execute SQL commands. Notice the `(none)` in the prompt. It indicates that you have not switched to any particular database yet.

### Explore the Existing Databases and Tables

```sql
SHOW DATABASES;
```

You should see `restaurant_001`, `restaurant_002`, `restaurant_003`, one for each course section. There are additional databases that are used internally by the MySQL DBMS, but we can ignore those for now.

Choose the one, for example:
```sql
USE restaurant_003;
```
Notice how the prompt switches to `(MySQL):(restaurant_003)>`.

```sql
SHOW FULL TABLES;
```

```sql
DESCRIBE employees;
```

Example output:
```text
+-------------+-------------+------+-----+---------+-------+
| Field       | Type        | Null | Key | Default | Extra |
+-------------+-------------+------+-----+---------+-------+
| employee_id | int         | NO   | PRI | NULL    |       |
| name        | varchar(50) | YES  |     | NULL    |       |
| state_id    | int         | YES  |     | NULL    |       |
+-------------+-------------+------+-----+---------+-------+
```

**Understanding NULL values:**

The `Null` column in the `DESCRIBE` output indicates whether each field allows NULL values:
- **`YES`**: The column can contain NULL values (the field is optional)
- **`NO`**: The column cannot contain NULL values (the field is required)

In this table, `employee_id` shows `NO` because it is a primary key, which must always have a value. Other columns like `name` and `state_id` show `YES`, meaning they can be left empty (NULL).

If you want to *require* a value for a non-primary-key column, use the `NOT NULL` constraint (MySQL does **not** have a `REQUIRED` keyword). For example:

```sql
ALTER TABLE employees MODIFY COLUMN name VARCHAR(50) NOT NULL;
```

You can also set a `DEFAULT` value so new rows get a non-NULL value automatically.

**Important distinction:** `NULL` represents the absence of a value and is different from:
- An empty string (`''`): which is an actual value (an empty text)
- Zero (`0`): which is an actual numeric value
- An empty date: which would be `'0000-00-00'` or similar, not NULL

When querying, use `IS NULL` or `IS NOT NULL` to check for NULL values, not `= NULL` or `!= NULL`.

**Basic queries**

```sql
-- all rows, all fields
SELECT * FROM employees;

-- count all rows
SELECT COUNT(*) FROM employees;

-- limit rows
SELECT * FROM employees LIMIT 2;

-- select specific fields
SELECT employee_id, name FROM employees;

-- filter with WHERE
SELECT * FROM employees WHERE employee_id > 1;
```

**Joins**

```sql
-- employees with home state
SELECT employees.employee_id, employees.name, states.home_state
FROM employees
LEFT JOIN states ON employees.state_id = states.state_code;
```

```sql
-- employees with state and job titles
SELECT e.employee_id, e.name, s.home_state, j.job
FROM employees_jobs AS ej
LEFT JOIN employees e ON ej.employee_id = e.employee_id
LEFT JOIN states s ON e.state_id = s.state_code
LEFT JOIN jobs j ON ej.job_code = j.job_code;
```

**Group by**

`GROUP BY` collapses rows that share a value and lets you compute an aggregate per group (`COUNT`, `SUM`, `AVG`, …). Here we join first, then count how many employee-job assignments each job title has:

```sql
SELECT j.job, COUNT(*) AS num_assignments
FROM employees_jobs AS ej
JOIN jobs j ON ej.job_code = j.job_code
GROUP BY j.job
ORDER BY num_assignments DESC;
```

Use `HAVING` when you want to filter **after** aggregation (unlike `WHERE`, which filters rows before grouping):

```sql
SELECT j.job, COUNT(*) AS num_assignments
FROM employees_jobs AS ej
JOIN jobs j ON ej.job_code = j.job_code
GROUP BY j.job
HAVING COUNT(*) >= 2;
```

## Lab 04: Working with SQL

When you're ready, start with [Lab 04: Working with SQL](https://github.com/ksiller/lab-04-sql/)

## Reference: CRUD Operations

### `CREATE`

**Create a database**
```sql
CREATE DATABASE my_db;
```

**Create a table**
```sql
use my_db;
CREATE TABLE nem2p_continents (
	continent_id VARCHAR(5),
	continent_name VARCHAR(30)
);
```

### `SELECT`
Get all rows from table `nem2p_continents`
```sql
SELECT * FROM nem2p_continents;
```

Count rows
```sql
SELECT COUNT(*) FROM nem2p_continents;
```

```sql
SELECT * FROM customer LIMIT 10;
```
```sql
SELECT * FROM nem2p_continents WHERE continent_id = 'AS';
```
```sql
SELECT * FROM nem2p_continents WHERE id > 2 AND id < 4;
```

### `INSERT`
```
INSERT INTO nem2p_continents (continent_id, continent_name) VALUES ('NA', 'North America');
INSERT INTO nem2p_continents (continent_id, continent_name) VALUES ('AS', 'Asia');
INSERT INTO nem2p_continents (continent_id, continent_name) VALUES ('SA', 'South America');
INSERT INTO nem2p_continents (continent_id, continent_name) VALUES ('AF', 'Africa');
INSERT INTO nem2p_continents (continent_id, continent_name) VALUES ('EU', 'Europe');
INSERT INTO nem2p_continents (continent_id, continent_name) VALUES ('OC', 'Oceania');
```
### `UPDATE`
```
UPDATE nem2p_continents SET continent_name = "Oceania and Beyond" WHERE continent_id = 'OC';
UPDATE customer SET store_id = 1 WHERE store_id IS NULL;
UPDATE customer SET store_id = 1 WHERE store_id = '';

```
### `DELETE`

```sql
DELETE FROM nem2p_continents WHERE continent_id = 'EU';
DELETE FROM customer WHERE customer_id = '';
```

More conditional deletes:

```sql
-- Delete a single customer
DELETE FROM customers WHERE customer_key = '12345';

-- Delete customer records that are missing a value
DELETE FROM customers WHERE dob IS NULL OR dob = '';

-- Delete old customers who have not visited your app recently
DELETE FROM customers WHERE last_visit < '2015-12-31 00:00:00';

-- Delete records that meet more complex conditions
DELETE FROM customers
WHERE
    mfa_auth = 0 AND
    last_visit < '2015-12-31 00:00:00' AND
    password_age > 90;
```

### `DROP`

```sql
DROP TABLE IF EXISTS employees;
DROP DATABASE IF EXISTS my_db;
```

`IF EXISTS` avoids an error when the target is already gone. Prefer dropping tables before dropping the database that contains them.

### `JOIN`
```
SELECT nem2p.first_name, nem2p.last_name, nem2p_continents.continent_name
FROM nem2p JOIN nem2p_continents 
  WHERE nem2p.continent = nem2p_continents.continent_id;
```

### `ALTER`: Updating Table Schema

```sql
ALTER TABLE employees ADD COLUMN email VARCHAR(100);
ALTER TABLE employees MODIFY COLUMN name VARCHAR(100) NOT NULL;
ALTER TABLE employees DROP COLUMN email;
```

### Creating Views

A view is a named, saved query. It stores no rows; each `SELECT` re-runs the underlying query against the live tables.

```sql
CREATE OR REPLACE VIEW employees_states AS
SELECT e.name, s.home_state
FROM employees e
JOIN states s ON e.state_id = s.state_code;

SELECT * FROM employees_states;
```

### Executing SQL Scripts

A `.sql` file is a sequence of statements. Select the database first (or pass it to `mycli`), then run the file. Demo scripts live under [`demos/04-sql/`](../../demos/04-sql/) (for example [`restaurant.sql`](../../demos/04-sql/restaurant.sql)). They require a write-capable account (not `ds2022`).

**Inside `mycli`:**

```sql
source ../../demos/04-sql/restaurant.sql
```

(Use a full path if your current directory is elsewhere.)

**From the shell:**

```bash
mycli -h ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com -P 3306 -u USER -p restaurant_003 < ../../demos/04-sql/restaurant.sql
```

**From the shell: redirecting output**

```bash
mycli -h ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com -P 3306 -u USER -p restaurant_003 < ../../demos/04-sql/restaurant.sql > results.txt
```

## SQL Queries Using Python

There are many Python packages for interacting with SQL databases or databases in general. Below we'll be using the `mysql-connector` package. One of its benefits is that it's easy to install and easy to learn if you are familiar with SQL.

### Env Variables

In your terminal, define the following environment variables:

```bash
export DBHOST='ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com'
export DBUSER='ds2022'
export DBPASS='YOUR_PASSWORD'  # from Canvas
export DBNAME='restaurant_003'  # or restaurant_001 / restaurant_002
```

### Imports

```python
import json
import os
import mysql.connector
```

### Read the Env Variables

```python
DBHOST = os.environ.get("DBHOST")
DBUSER = os.environ.get("DBUSER")
DBPASS = os.environ.get("DBPASS")
DBNAME = os.environ.get("DBNAME", "restaurant_003")  # or restaurant_001 / restaurant_002
```

### Connection Strings

```python
db = mysql.connector.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME)
```

### Cursor

Create the cursor. You can create one with or without dictionary output.

**Without dictionary (default):**
```python
cursor = db.cursor()
```
- Returns results as **tuples** (ordered sequences)
- Access values by **index position**: `row[0]`, `row[1]`, etc.
- Example: `(1, 'Alice', 26)`
- Access: `row[0]` for `employee_id`, `row[1]` for `name`, etc.

**With dictionary output:**
```python
cursor = db.cursor(dictionary=True)
```
- Returns results as **dictionaries** (key-value pairs)
- Access values by **column name**: `row['name']`, `row['state_id']`, etc.
- Example: `{'employee_id': 1, 'name': 'Alice', 'state_id': 26}`
- Access: `row['employee_id']`, `row['name']`, etc.
- **Benefits**: More readable, self-documenting code; column order doesn't matter

### Query

```python
query = "SELECT * FROM employees ORDER BY name"
cursor.execute(query)
results = cursor.fetchall()
```

### Complete SELECT Example

```python
import os
import mysql.connector

DBHOST = os.environ.get("DBHOST")
DBUSER = os.environ.get("DBUSER")
DBPASS = os.environ.get("DBPASS")
DBNAME = os.environ.get("DBNAME", "restaurant_003")

db = mysql.connector.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME)
cursor = db.cursor(dictionary=True)

query = "SELECT * FROM employees ORDER BY name"
cursor.execute(query)
results = cursor.fetchall()

for row in results:
    print(f"ID: {row['employee_id']}, Name: {row['name']}, State: {row['state_id']}")

cursor.close()
db.close()
```

See also [`basic-sql.py`](./basic-sql.py) / [`basic-sql.ipynb`](./basic-sql.ipynb) for more SELECT patterns (including parameterized filters) against `media.MOCK_DATA`.

### Insert (Parameterized)

`INSERT` needs a write-capable account (Lab 04). The shared `ds2022` user cannot insert. Always use `%s` placeholders and pass values as a tuple; never build SQL with f-strings.

```python
query = (
    "INSERT INTO mock_data "
    "(id, first_name, last_name, email, gender, ip_address) "
    "VALUES (%s, %s, %s, %s, %s, %s)"
)
record_data = (1001, "Mickey", "Mouse", "mickey@disney.com", "Non-binary", "1.2.3.4")
cursor.execute(query, record_data)
db.commit()
```

Full working script: [`insert_data.py`](./insert_data.py).

For production code, use an `if __name__ == "__main__":` block, break the code into functions, and prefer logging over `print`.

### pandas and SQLAlchemy

`mysql-connector` is great for row-at-a-time queries. For loading a whole DataFrame into MySQL in one step, use pandas with a SQLAlchemy engine and [`DataFrame.to_sql()`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html).

```bash
uv add pandas sqlalchemy mysql-connector-python
```

```python
import os
import pandas as pd
from sqlalchemy import create_engine

DBHOST = os.environ.get("DBHOST")
DBUSER = os.environ.get("DBUSER")
DBPASS = os.environ.get("DBPASS")
DBNAME = os.environ.get("DBNAME")

df = pd.read_csv("MOCK_DATA.csv")

url = f"mysql+mysqlconnector://{DBUSER}:{DBPASS}@{DBHOST}:3306/{DBNAME}"
engine = create_engine(url)

# if_exists='replace' recreates the table; use 'append' to add rows
df.to_sql("mock", con=engine, if_exists="replace", index=False)
engine.dispose()
```

Full working script: [`pandas_sqlalchemy.py`](./pandas_sqlalchemy.py).

### DuckDB

[DuckDB](https://duckdb.org/) is an in-process SQL engine. It stores data in a local file (no server) and can create tables directly from a pandas DataFrame: useful for analysis on your laptop without touching RDS.

```bash
uv add pandas duckdb
```

```python
import duckdb
import pandas as pd

df = pd.DataFrame(
    {
        "id": [1, 2, 3, 4],
        "name": ["Alice", "Bob", "Carol", "Dave"],
        "group": ["A", "B", "A", "C"],
        "score": [88, 72, 95, 81],
    }
)

con = duckdb.connect("mock.duckdb")
con.execute("CREATE OR REPLACE TABLE mock AS SELECT * FROM df")
print(con.execute("SELECT COUNT(*) FROM mock").fetchone())
print(con.execute("SELECT * FROM mock").fetchdf())
con.close()
```

Full working script: [`duckdb_example.py`](./duckdb_example.py).

Reference files:

- [`basic-sql.py`](./basic-sql.py) | [`basic-sql.ipynb`](./basic-sql.ipynb)
- [`ConnectToRds.ipynb`](./ConnectToRds.ipynb)
- [`insert_data.py`](./insert_data.py) | [`select-query.py`](./select-query.py)
- [`pandas_sqlalchemy.py`](./pandas_sqlalchemy.py) | [`duckdb_example.py`](./duckdb_example.py)
- [`logistics.sql`](./logistics.sql) | [`logistics_query.py`](./logistics_query.py)
- [`data.sql`](./data.sql) | [`mock_data.sql`](./mock_data.sql)
- Demo SQL scripts: [`demos/04-sql/`](../../demos/04-sql/)

## SQL in Jupyter Notebooks

For interactive exploration of the restaurant databases (read-only `ds2022` account), use [`ConnectToRds.ipynb`](./ConnectToRds.ipynb). For examples against `media.MOCK_DATA`, see [`basic-sql.ipynb`](./basic-sql.ipynb).

## Advanced Concepts (Optional)

Warmup already covers basic `GROUP BY` / `HAVING` on the restaurant schema. The examples below go further. Several need write access (indexes, inserts); use your Lab 04 database for those.

### SQL CLI: Subqueries and Nested Queries

Subqueries let you use the result of one query as input to another (`SELECT`, `FROM`, `WHERE`, or `HAVING`).

```sql
-- Employees in states that appear more than once in the employees table
SELECT e.name, e.state_id
FROM employees e
WHERE e.state_id IN (
    SELECT state_id
    FROM employees
    GROUP BY state_id
    HAVING COUNT(*) > 1
);
```

### SQL CLI: Indexes for Performance Optimization

Indexes speed lookups on frequently filtered or joined columns. Creating an index requires write access.

```sql
-- Index the join key used in employees <-> states
CREATE INDEX idx_employees_state_id ON employees(state_id);

-- Composite index for lookups that filter on both columns
CREATE INDEX idx_ej_employee_job ON employees_jobs(employee_id, job_code);

SHOW INDEXES FROM employees;
```

### Python: Connection Context Managers and Error Handling

Use context managers (`with`) so connections close even when errors occur.

```python
import os
import mysql.connector
from mysql.connector import Error

DBHOST = os.environ.get("DBHOST")
DBUSER = os.environ.get("DBUSER")
DBPASS = os.environ.get("DBPASS")
DBNAME = os.environ.get("DBNAME", "restaurant_003")

try:
    with mysql.connector.connect(
        host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME
    ) as connection:
        with connection.cursor(dictionary=True) as cursor:
            query = "SELECT * FROM employees WHERE employee_id = %s"
            cursor.execute(query, (1,))
            result = cursor.fetchone()
            print(result)
except Error as e:
    print(f"Error connecting to MySQL: {e}")
```

### Python: Batch Inserts with executemany()

`executemany()` inserts many rows in one round trip. Requires write access (Lab 04).

```python
import os
import mysql.connector

DBHOST = os.environ.get("DBHOST")
DBUSER = os.environ.get("DBUSER")
DBPASS = os.environ.get("DBPASS")
DBNAME = os.environ.get("DBNAME")  # e.g. COMPUTING_ID_mock

connection = mysql.connector.connect(
    host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME
)
cursor = connection.cursor()

rows = [
    (2001, "Alice", "Smith", "alice@example.com", "Female", "10.0.0.1"),
    (2002, "Bob", "Jones", "bob@example.com", "Male", "10.0.0.2"),
]

query = (
    "INSERT INTO mock_data "
    "(id, first_name, last_name, email, gender, ip_address) "
    "VALUES (%s, %s, %s, %s, %s, %s)"
)
cursor.executemany(query, rows)
connection.commit()

print(f"Inserted {cursor.rowcount} rows")
cursor.close()
connection.close()
```

### Python: Connection Pooling for Production Applications

Connection pooling reuses connections instead of opening a new one for every request.

```python
import os
from mysql.connector import pooling

DBHOST = os.environ.get("DBHOST")
DBUSER = os.environ.get("DBUSER")
DBPASS = os.environ.get("DBPASS")
DBNAME = os.environ.get("DBNAME", "restaurant_003")

pool_config = {
    "pool_name": "mypool",
    "pool_size": 5,
    "pool_reset_session": True,
    "host": DBHOST,
    "user": DBUSER,
    "password": DBPASS,
    "database": DBNAME,
}

connection_pool = pooling.MySQLConnectionPool(**pool_config)
connection = connection_pool.get_connection()

if connection.is_connected():
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees LIMIT 10")
    print(cursor.fetchall())
    cursor.close()
    connection.close()  # returns the connection to the pool
```

## Resources

[SQL Cheatsheet](https://media.geeksforgeeks.org/wp-content/uploads/20240328180119/SQL-Cheat-Sheet-PDF.pdf)
[SQL Tutorial](https://www.geeksforgeeks.org/sql/sql-tutorial/)
[SQL Commands](https://www.geeksforgeeks.org/sql/sql-ddl-dql-dml-dcl-tcl-commands/)
[SQL Data Types](https://www.geeksforgeeks.org/sql/sql-data-types/)
[SQL Operators](https://www.geeksforgeeks.org/sql/sql-operators/)
[Joins in SQL](https://www.geeksforgeeks.org/sql/sql-join-set-1-inner-left-right-and-full-joins/)
