# Working with SQL databases

Live demo. Students connect with the shared read-only `ds2022` account (password on Canvas). Schema setup and writes are done by the instructor.

## Command line tools for SQL

### CLI Setup

Confirm that `uv` is installed.

```bash
uv --version
```

If you receive an error message, follow the [uv setup instructions](../../class/03-scripting/README.md#setup).

```bash
uv tool install mycli
```

This installs `mycli` under `~/.local/bin/`. Confirm:

```bash
ls -ltr ~/.local/bin
```

To run `mycli` from any directory, check that `~/.local/bin` is on your `$PATH`:

```bash
echo $PATH
```

If it is missing, add it:

**Bash:**

```bash
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

**Zsh:**

```bash
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.zshrc
source ~/.zshrc
```

Confirm `mycli` works:

```bash
mycli --help
```

### Connecting to a database instance

```bash
mycli -h ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com -P 3306 -u ds2022 -p
```

The `ds2022` account can run read operations (`SHOW`, `DESCRIBE`, `SELECT`, joins). It cannot create databases or insert, update, or delete rows.

### Show existing databases

```sql
SHOW DATABASES;
```

### Create a database

```sql
CREATE DATABASE restaurant;
```

### Switch to database & create a table

```sql
USE restaurant;
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    name VARCHAR(50),
    state_id INT
);
```

### Show tables

```sql
SHOW FULL TABLES;
```

```text
┌──────────────────────┬────────────┐
│ Tables_in_restaurant │ Table_type │
├──────────────────────┼────────────┤
│ employees            │ BASE TABLE │
└──────────────────────┴────────────┘
```

### Describe table

```sql
DESCRIBE employees;
```

```text
┌─────────────┬─────────────┬──────┬─────┬─────────┬───────┐
│ Field       │ Type        │ Null │ Key │ Default │ Extra │
├─────────────┼─────────────┼──────┼─────┼─────────┼───────┤
│ employee_id │ int         │ NO   │ PRI │ <null>  │       │
│ name        │ varchar(50) │ YES  │     │ <null>  │       │
│ state_id    │ int         │ YES  │     │ <null>  │       │
└─────────────┴─────────────┴──────┴─────┴─────────┴───────┘
```

### Create new records

```sql
INSERT INTO employees (employee_id, name, state_id)
VALUES (1, 'Alice', 26);

INSERT INTO employees (employee_id, name, state_id)
VALUES (2, 'Bob', 56);
```

### Read records

```sql
SELECT * FROM employees
WHERE name = 'Alice';
```

### Update records

```sql
UPDATE employees SET state_id = 56
WHERE name = 'Alice';
```

### Delete records

```sql
DELETE FROM employees
WHERE state_id = 56;
```

### Drop table

```sql
DROP TABLE employees;
```

```sql
DROP TABLE IF EXISTS employees;
```
The `IF EXISTS` is convenient to avoid errors when the drop operation is executed on a table that doesn't exist.

### SQL Scripts

A `.sql` file is a sequence of statements MySQL can execute in order. [restaurant.sql](./restaurant.sql) creates the four demo tables and their sample rows **in the current database**. It does not create the database, so `restaurant` must already exist and be selected before you run it. [create_view.sql](./create_view.sql) adds the `employees_states` view the same way. Run them from `demos/04-sql/` (or use a full path to the file). Both require a write-capable account (not `ds2022`).

**Option A: `source` inside `mycli`**

Already connected in an interactive session, with `restaurant` selected (either connect with `mycli ... restaurant` or run `USE restaurant;` first):

```sql
source restaurant.sql
```

`source` reads the file and runs each statement in the current session. If the database is not selected, every statement fails with `ERROR 1046 (No database selected)`.

**Option B: redirect from the shell**

No interactive session needed; `mycli` runs the file and exits. Pass the database name as the final argument so the statements have a target:

```bash
mycli -h ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com -P 3306 -u USER -p restaurant < restaurant.sql
```

Same statements as Option A; the shell feeds the file on stdin instead of using `source`.

The script is not safe to re-run as-is: the tables are created with `IF NOT EXISTS`, so a second run leaves them in place and the `INSERT` statements fail with duplicate-key errors. Run `drop_tables.sql` first to reset the demo to a clean state.

```sql
SHOW FULL TABLES;
```

### Join

```sql
SELECT *
FROM employees
LEFT JOIN states ON employees.state_id = states.state_code;
```

### Join and filter

```sql
SELECT employees.name, states.home_state
FROM employees
LEFT JOIN states ON employees.state_id = states.state_code
WHERE employees.name = 'Alice';
```

### Creating a View

```sql
CREATE OR REPLACE VIEW employees_states AS
SELECT e.name, s.home_state
FROM employees e
JOIN states s ON e.state_id = s.state_code;
```

A view is a saved query with a name. It stores no rows of its own: every time you select from it, MySQL re-runs the query above against the current contents of `employees` and `states`. 
- Tables hold the data,
- Views give you a reusable shape of that data. 

Once the view exists, you query it exactly like a table, which lets you hide a repeated join behind one simple `SELECT`.

```sql
SELECT * FROM employees_states;
```

## Python and SQL

### Python Setup

```bash
mkdir -p ~/ds2022-fall-26
cd ~/ds2022-fall-26
uv init sql-class --description "SQL class examples"
cd sql-class
uv add mysql-connector-python pandas matplotlib
```


### A basic Python script

See [basic-sql.py](../../class/04-sql/basic-sql.py) (same examples as [basic-sql.ipynb](../../class/04-sql/basic-sql.ipynb), against `media.MOCK_DATA`).

Copy that example script into this project (from your clone of the course repo):

```bash
cp /path/to/DS2022/class/04-sql/basic-sql.py .
```

Set connection environment variables (password on Canvas), then run:

```bash
export DBHOST='ds2022.cgls84scuy1e.us-east-1.rds.amazonaws.com'
export DBUSER='ds2022'
export DBPASS='YOUR_PASSWORD'
export DBNAME='media'

uv run python basic-sql.py
```

`uv run` uses the project’s virtual environment (including `mysql-connector-python`). The script must live in the current project directory, or you pass a path: `uv run python /path/to/basic-sql.py`.

### Python notebook

Example: [basic-sql.ipynb](../../class/04-sql/basic-sql.ipynb)

The notebook queries the `media` database (`MOCK_DATA`), so use the same `sql-class` project and add the extra packages it imports:

```bash
cd ~/ds2022-fall-26/sql-class
uv add mysql-connector-python pandas matplotlib jupyter
cp /path/to/DS2022/class/04-sql/basic-sql.ipynb .
uv run jupyter lab basic-sql.ipynb
```

In the notebook’s connection cell, set `DBUSER` / `DBPASS` for the read-only `ds2022` account and `DBNAME = "media"`. Then run the cells in order.
