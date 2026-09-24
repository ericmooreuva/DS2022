# Scripting with Python and Bash

This module covers Bash and Python scripting. In the lab you will be using the [uv](https://docs.astral.sh/uv/) package manager for isolated Python environments; the tutorial below prepares you for that.

**Work through the following sections:**

- [Setup](#setup)
- [Managing Python environments with uv](#managing-python-environments-with-uv)
- [Scripting best practices](#scripting-best-practices)
- [Start Lab 03](https://github.com/ksiller/lab-03-scripting)

> **Note:** Use [Scripting best practices](#scripting-best-practices) as a reference while you work through Lab 03.



## Setup

For the Python examples in this module (and for [Lab 03](https://github.com/ksiller/lab-03-scripting)), you need **Python 3** and **[uv](https://docs.astral.sh/uv/)** on your computer.

**Confirm that both are installed.** Open a terminal (on Windows, use a WSL bash terminal, not PowerShell):

```bash
which python3
python3 -V
```

The path should look like `/usr/bin/python3` (or similar). Prefer **Python 3.11 or newer**.

```bash
uv --version
```

If `uv --version` fails, install `uv` from the official docs: [Installing uv](https://docs.astral.sh/uv/getting-started/installation/). On macOS or Linux you can run:

```bash
curl -LsSf https://astral.sh/uv/install.sh -o uv-installer.sh
sh uv-installer.sh
```

After installing, close and reopen the terminal (or run `source ~/.bashrc` / `source ~/.zshrc`), then confirm with `uv --version` again.

Work in `~/ds2022-fall-26` for the hands-on steps below. Do **not** nest a new Git repository inside this course repository unless you are intentionally creating a separate practice folder outside it.

## Managing Python environments with `uv`



### Why isolate environments?

Different projects often need different versions of the same package (library). Historically, the `pip install` command has been widely used to install Python packages. The problem is that one global `pip install` cannot satisfy every project at once.

Here is a realistic clash between **two packages that do not depend on each other**, but that both require the shared library `protobuf` with **non-overlapping** version ranges:

- `dbt-core` — runs analytics transformations (dbt models) against a data warehouse.
- `google-cloud-pubsub` — publishes and subscribes to messages on Google Cloud Pub/Sub.

**Try this conflict** (it should fail — that is the point):

```bash
python3 -m pip install dbt-core==1.7.14 google-cloud-pubsub==2.40.0
```

You should see a resolver error similar to:

```text
ERROR: Cannot install dbt-core==1.7.14 and google-cloud-pubsub==2.40.0 because these package versions have conflicting dependencies.

The conflict is caused by:
    dbt-core 1.7.14 depends on protobuf<5 and >=4.0.0
    google-cloud-pubsub 2.40.0 depends on protobuf<8.0.0 and >=6.33.5
```

Neither package lists the other as a dependency. Both need `protobuf`, but one requires version 4.x and the other requires 6.x — no single version can satisfy both. The clean solution is **separate environments**: one project gets `dbt-core`, another gets `google-cloud-pubsub`. `uv` creates and manages those environments for you.

### Core ideas


| Piece             | Role                                                                               |
| ----------------- | ---------------------------------------------------------------------------------- |
| `.venv/`          | Local virtual environment (installed packages live here). **Do not commit it.**    |
| `pyproject.toml`  | Declares your project and its dependencies (what you want).                        |
| `uv.lock`         | Pins the exact versions `uv` resolved (what you got). Makes installs reproducible. |
| `.python-version` | Records which Python version this project expects.                                 |


Typical workflow:

1. Edit dependencies with `uv add` / `uv rm`.
2. That updates `pyproject.toml` and `uv.lock`.
3. Run `uv sync` to (re)create or update `.venv`.
4. Run code with `uv run`.



### Hands-on: a tiny `uv` project

Create a practice folder and a first project inside it:

```bash
mkdir -p ~/ds2022-fall-26/uv-practice
cd ~/ds2022-fall-26/uv-practice
uv init project-1 --name project-1 --description "Practice project for uv"
cd project-1
```



#### 1. Inspect what `uv init` created

```bash
ls -la
cat pyproject.toml
cat .python-version
```

You should see `pyproject.toml`, `.python-version`, and usually a small starter layout. Open `pyproject.toml` and notice that `dependencies` starts empty.

#### 2. `uv add`

Add a single package:

```bash
uv add requests
```

Check:

- `pyproject.toml` — `requests` is listed under `dependencies`
- `uv.lock` — the exact version (and its dependencies) are pinned
- `.venv/` — packages were installed into an isolated environment

```bash
ls .venv
grep -A5 '^dependencies' pyproject.toml   # or open pyproject.toml in an editor
```

```bash
uv tree
```

This shows the hierarchy of package dependencies in your current project.
#### 3. `uv run`

Run Python **through** the project environment (no need to `source .venv/bin/activate` first):

```bash
uv run python -c "import requests; print(requests.__version__)"
```

Or start an interactive shell in that environment:

```bash
uv run python
```



#### 4. `uv rm`

```bash
uv rm requests
uv run python -c "import requests"
```

The last command should fail: `requests` is gone from the project environment. `pyproject.toml` and `uv.lock` were updated for you.

Add it back:

```bash
uv add requests
```



#### 5. `uv sync`

`uv sync` installs whatever `pyproject.toml` + `uv.lock` describe into `.venv`. Use it when you clone a project that already has those files, or after pulling lockfile changes:

```bash
uv sync
```

On a fresh machine (or HPC), you typically clone the repo, then run `uv sync` or `uv run ...` (which can sync as needed). Do **not** copy `.venv` between computers.

#### 6. Relationship: `pyproject.toml` and `uv.lock`

- `pyproject.toml` — human-oriented declaration (`requests`, without listing every sub-dependency).
- `uv.lock` — machine-oriented snapshot of the full resolved dependency tree.

Both belong in Git. Together they let someone else recreate the same environment with `uv sync`.

### Using a `requirements.txt` with `uv`

Many community Python projects still ship a `requirements.txt`. That older format lists needed packages one per line. You can import it into a `uv` project:

```bash
echo "requests>=2.31.0" > requirements.txt
uv add -r requirements.txt
```

That adds those packages to `pyproject.toml` / `uv.lock`. You may keep `requirements.txt` for documentation, but for a `uv` project the source of truth is `pyproject.toml` + `uv.lock`.

If another tool only knows how to install from a `requirements.txt` (and not from `uv.lock`), you can ask `uv` to write one that lists the exact versions currently locked for this project:

```bash
uv export -o requirements-locked.txt
```

You do **not** need this for Lab 03. The lab (and this course) treat `pyproject.toml` + `uv.lock` as enough: someone else runs `uv sync` or `uv run` and gets the same environment. Use `uv export` only when you must hand a classic `requirements.txt` to a system that cannot use `uv`.

### Setting up separate projects

The conflict example earlier showed that `dbt-core==1.7.14` and `google-cloud-pubsub==2.40.0` cannot be installed in one environment. Put each in its own project instead.

Your first project is already at `~/ds2022-fall-26/uv-practice/project-1`. From there:

```bash
cd ~/ds2022-fall-26/uv-practice/project-1
uv add dbt-core==1.7.14
uv run python -c "import dbt; print('dbt-core is importable')"
```

Create a second project and install the other package:

```bash
cd ~/ds2022-fall-26/uv-practice
uv init project-2 --name project-2 --description "Google Cloud practice project"
cd project-2
uv add google-cloud-pubsub==2.40.0
```

Typical layout:

```text
~/ds2022-fall-26/uv-practice/
|-- project-1/
|   |-- pyproject.toml      # includes dbt-core==1.7.14
|   |-- uv.lock
|   |-- .python-version
|   `-- .venv/
`-- project-2/
    |-- pyproject.toml      # includes google-cloud-pubsub==2.40.0
    |-- uv.lock
    |-- .python-version
    `-- .venv/
```

In `project-2`, Pub/Sub imports work; `dbt` does not (it was never installed here):

```bash
uv run python -c "from google.cloud import pubsub_v1; print('pubsub ok')"
uv run python -c "import dbt"
```

The second command should fail. Switch back to `project-1` and the opposite is true:

```bash
cd ../project-1
uv run python -c "import dbt; print('dbt ok')"
uv run python -c "from google.cloud import pubsub_v1"
```

Each project has its own `.venv`, so the packages no longer fight over `protobuf`.

### Advanced: try a package once with `uv run --with`

**Intention:** run a command that needs an extra package **today**, without making that package a permanent dependency of the project.

`uv add` updates `pyproject.toml` and `uv.lock` and installs into `.venv`. That is what you want for libraries your project actually relies on. `--with` is for a temporary tryout: “borrow” a package for this one command only.

```bash
uv run --with rich python -c "from rich import print; print('[bold green]hello[/]')"
```

For that command, `uv` makes `rich` available so the import works. It does **not** add `rich` to `pyproject.toml` or `uv.lock`. The next plain `uv run python ...` will not have `rich` unless you `uv add rich`.

Use `--with` for quick experiments. If you will keep using the package in this project, `uv add` it instead.

### Version control

**Commit:**

- `pyproject.toml`
- `uv.lock`
- `.python-version`
- `.gitignore` (include `.venv/`)

**Do not commit:**

- `.venv/` (recreate with `uv sync` / `uv run`)

**Do not hand-edit:**

- `uv.lock` (let `uv add`, `uv rm`, and `uv sync` maintain it)
- Prefer changing dependencies with `uv add` / `uv rm` instead of hand-editing `pyproject.toml` dependency lists (avoids lockfile drift)

Quick `.gitignore` line (run in each project directory):

```bash
echo ".venv/" >> .gitignore
```



## Scripting Best Practices

All scripts should adhere to [coding best practices](../../best-practices.md). Specifically, they should be written in a way that takes into account several factors:

1. Use the shebang / make the script executable
2. Error out gracefully --> set -e / error codes --> || exit 1;
3. Use input parameters
4. Conditional logic
5. Environment / full paths / env variables
6. Logging
7. Use comments



## bash



### shebang

A well-formatted `bash` script begins with a "shebang" line:

```
#!/bin/bash
```

that points to the full path of the `bash` shell. This may differ from one environment
to the next.

To make any bit of code executable, use `chmod 755` against it.

### Use full paths

Any binary executables used in a shell script should be invoked using their full
paths. This is to avoid any ambiguity and preempt any errors of a shell not being
able to find the command.

For example, when invoking the `aws` command-line in a script you would normally call

```
/usr/local/bin/aws
```

To determine the full path of an executable in a given system, use the `which` command:

```
which aws
```



### Graceful Errors

Near the top of most `bash` scripts, put:

```bash
set -euo pipefail
```

- `-e` — stop the script as soon as any command fails. Continuing past an error can produce bad results or unintended side effects.
- `-u` — stop if the script uses a variable that was never set (typos and missing arguments show up immediately).
- `-o pipefail` — a pipeline fails if **any** command in it fails. Without this, only the last command's exit status counts, so an early failure can be hidden.

See `strict-mode.sh` for a short example. Try:

```bash
chmod 755 strict-mode.sh
./strict-mode.sh /etc/hosts
./strict-mode.sh no-such-file.txt
```

Another option is a conditional so that when a specific line fails, the script `exit`s with a non-zero code. That can be useful when debugging.

### Sleep

If you need a deliberate pause in the middle of a script, use `sleep 5` for a 5-second pause (change the number as needed). This can help when waiting for a service or file to become ready.

### Input parameters

Remember that `$0`, `$1`, `$2`, etc. are reserved parameters `bash` understands as positional
arguments when invoking from the command-line:

- `$0` is the invoking script itself
- `$1` is the first parameter after the script name
- `$2` is the second parameter, and so on.

`positional-args.sh`

```
#!/bin/bash

echo "$0 <-- invoking script"
echo "$1 <-- first parameter"
echo "$2 <-- second parameter"
```

returns the following output:

```
$ ./positional-args.sh bananas blueberries

./positional-args.sh <-- invoking script
bananas <-- first parameter
blueberries <-- second parameter
```



### If/Else conditional logic

Start your `if` with a comparison, end with `fi`.

```bash
if [[ $VAR -gt 10 ]]
then
  echo "That number is greater than 10."
else
  echo "Your number is pretty small!"
  exit 0;
fi
```



### Loops

Start with `for`, put the body between `do` and `done`:

```bash
names=("alice" "bob" "carol")
for name in "${names[@]}"; do
    echo "Name: $name"
done
```



### Environment

`env` gives you all environment variables for your session. This may vary
for an unattended script (without you around).

Add environment variables in `bash`:

```
export VARIABLE=value-of-variable
```

Use full paths to your binaries to avoid your unattended script being unable
to locate a binary. Just because you can run it by hand does not mean it can
run without you around.

### Storing a command's output in a variable

```bash
# general format
VAR=$(command_to_execute)
```

Example:

```bash
TODAY=$(date)
echo "$TODAY"
```

This runs `date`, stores the output in `TODAY`, then prints it.

You are not limited to a single command. You can also put a pipeline inside `$( )`.

### Logging

A simple-yet-valuable step in your scripting is to log. You can log every action
taken by the script, or limit logging to successes or failures.

A common format for logging might be a snippet like this:

```
# First establish the datetime:
NOW=$(date +"%m-%d-%Y-%H:%M:%SEDT")
echo "$NOW OK - Successfully processed $FILENAME" >> /var/log/output.log
```

The result would be a single file building with each row as it is logged.
Note the `>>` to append to a file instead of overwriting it!

### Comment

One of the most useful habits you can develop as a programmer is adding comments
to your code. This explains each chunk of code but might also justify why a particular
choice has been made. This will be invaluable to you, when you come back to the code
two years later, or when your code is shared with others.

Comments start with a `#`; all characters following the `#` on that line are ignored. Here's an example demonstrating good commenting practice:

```bash
#!/bin/bash
# This script greets a user by name
# Usage: ./greet.sh <name>

# Exit immediately if any command fails
set -e

# Check if a name was provided as an argument
if [ $# -eq 0 ]; then
    echo "Error: Please provide a name"
    exit 1
fi

# Store the first argument in a variable
NAME=$1

# Display a personalized greeting
echo "Hello, $NAME! Welcome to bash scripting."
```



## Python3

Scripting in Python is similar in spirit to bash, but Python offers more built-in structure (libraries, classes, functions). A few things to note:

- Unlike bash, command-line arguments are not automatic `$1`, `$2` variables. See the [Python tutorial on command-line arguments](https://docs.python.org/3/tutorial/stdlib.html#command-line-arguments), or this [Stack Abuse walkthrough](https://stackabuse.com/command-line-arguments-in-python/).
- Python can invoke shell scripts in other languages.
- Python has many options for conditional logic, error handling, and logging.
- Whereas bash and other low-level tools (`grep`, `sed`, `awk`, `tr`, `perl`, etc.) can parse plain-text "flat" files fairly efficiently, Python can load a data file into memory for more complex transformations. A library like `pandas` can use dataframes like a staging table you query and reshape. Start with the official [pandas getting started](https://pandas.pydata.org/docs/getting_started/index.html) guide.

> **Note:** Also review the course [coding best practices](../../best-practices.md).



## Resources

- [Bash Scripting Tutorial (video)](https://www.youtube.com/watch?v=tK9Oc6AEnR4)
- [Bash Guide for Beginners (TLDP)](https://tldp.org/LDP/Bash-Beginners-Guide/html/)
- [uv documentation](https://docs.astral.sh/uv/)
- [Lab 03: Scripting](https://github.com/ksiller/lab-03-scripting)

