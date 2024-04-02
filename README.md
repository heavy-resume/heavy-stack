# The Heavy Stack
The Heavy Stack is the stack used by Heavy Resume. This is a point in time fork of the tech stack and syncing between Heavy Resume and this fork will be done periodically. This is intended to be treated like a starting template.


## Features That Work "Out of the Box"
- Pre-made dev container, docker files
- Top to Bottom Python (Sanic, custom ReactPy, Brython)
- PostgreSQL, PG Vector, CockroachDB
- SQL Model (SQLAlchemy + Pydantic)
- Hot reloading, both server and tests
- User action recording and playback for load testing
- Time tracking
- Established patterns and examples


## Renaming the project
After checking out the repo, you should rename the project. Run `python rename_project.py` and follow the prompts.

Note that this isn't well tested at the moment and may be incomplete. Remember to delete the `.git` directory if things look good.

If using github codespaces, you may not see the workspace directory rename until after you create a fresh codespace. Since you're renaming everything you would need to create and push a new repo.


## Prescribed Running Method
- The Heavy Stack was built with Github Codespaces or similar in mind. Running locally using docker can create complications such as poor performance, failure to detect changes, or I/O failures if the container is misconfigured or Docker has become unstable.


## Quickstart - Server
- Go to "Run and Debug", select "Hot Reload Heavy Stack', then click the play button.

  ![VS Code UI - how to run](docs/images/heavy-stack-how-to-run.png)


## Quickstart - Tests
- Go to "Run and Debug", select "Pytest Daemon", then click the play button. This will start the daemon with debugging enabled.
- Find a test and run it without debugging. The daemon will run the test and will stop on breakpoints.


## Resetting the Databases
- Go to "Run and Debug", select "Run Pave DB", then click the play button. This will rebuild the database tables.


## Hot reloading tips
If something doesn't make sense, restart the server rather than wasting time debugging an issue that doesn't exist. This
applies to both running the primary application and running the pytest daemon.


## VS Code tips
- `Ctrl / Cmd + Shift + P` - Open the command palette
- `Ctrl / Cmd + .` - Open the quick fix menu
- `Ctrl / Cmd + click` - Go to definition / find references


## Structure
The project is structured as follows:
- `alembic` - Database migrations are automatically generated by the "Create and test migrations" profile and will show up here.
- `brython` - Brython (Python executed in the browser) code goes here.
- `dockerfiles` - Contains the Dockerfiles for the production and development images.=
- `heavy_stack` - Contains the main code for the project.
    - `heavy_stack/backend` - Contains most backend logic
    - `heavy_stack/frontend` - Contains the ReactPy logic
    - `heavy_stack/shared_models` - Shared models are domain objects that are used by both the frontend and backend. They're usually used by the frontend.
- `static` - static files such as CSS and images are found here
- `tests` - Contains the tests for the project, including unit and integration tests.


## Class responsibilities
- `SQL Models` - These are used for database access and are the "raw" data. If you have encrypted values, this class is what would handle the encryption / decryption.
- `Shared Models` - These are domain objects and typically used by the frontend (ReactPy).
    There is no requirement that shared models match the SQL Model, but they often are close.
    The shared models should structure data like you would intuitively expect, and not just mirror the database schema.
    Shared models probably shouldn't do any encryption or decryption, and are typically just Pydantic objects.
- `Model Mungers` - These are used to take the output of an operation (usually a SQL Model) and convert it to the appropriate output model.
- `Model Managers` - These handle the business logic around a model. They usually take in at least one munger as an argument.
- `Repositories` - These handle the database operations and work with SQL Models. Managers frequently have at least one repository.

### Add Table Script
- `dev_scripts/add_table.py` - Walks you through adding a new table, creating the SQL Model, Shared Model, Model Munger, Model Manager, and Repository.
- This script is not required and some database tables or domain objects may not fit into this paradigm. That said, you can always delete what isn't used.
- Using the script helps continue existing naming conventions.

### Managing Database Connections
- This shouldn't be needed for typical use cases. Repository classes should be the classes that access the
  database, and the `SQLRepositoryBase` class will grab the current database connection, which is stored
  in a thread local. If you need a second connection (for example, to connect to the vector database),
  you can look in `db_connection.py` to see how its done.
- If you're getting an error about the `db_session` variable not being set, then it means you're probably attempting
  to do database access in the wrong place. Logic called inside an async function from `heavy_use_effect` or `heavy_event`
  should set the `db_session` variable. Tests will also have the variable set automatically if you use the `db_session: AsyncSession` fixture.

Test Example:
```python
from sqlmodel.ext.asyncio.session import AsyncSession

...

class TestAClass:
    class TestAMethod:
        async def test_something(self, db_session: AsyncSession) -> None:
          ...
```


## Adding and updating dependencies
- `poetry lock` - Updates the lock file with the latest versions.
- `poetry add <package>` - Adds a package to the project.
- `poetry add <package> --group=dev` - Adds a package to the project as a dev dependency.
- `poetry install` - Install from the lock file.
- `pip install --no-cache-dir <package>` - Install a package without caching. Sometimes needed.


## Environment Variables
When the codespace is generated, the `.env` file is created. Note that VS Code frequently requires that you reload the window
in order for changes to the `.env` file to take effect.


## Database Migrations
- Migrations are not part of the regular development flow. Pave DB and tests bypass migrations.
- Create and test migrations:
  - Go to "Run and Debug", select "Create and test migrations", then click the play button.
  - This will generate a new migration and place it in the alembic/versions directory
- Check if any migrations are needed:
  - Run "Create and test migrations" and see if the generated migration simply has a "pass" statement
- Delete or recreate a migration:
  - Simply delete the file
- Prune old migrations:
  - See https://alembic.sqlalchemy.org/en/latest/cookbook.html#building-an-up-to-date-database-from-scratch
  - TLDR: You just delete the old files and modify the oldest migration to not have a previous revision. Recreating a database from scratch via migrations is an antipattern.


## Executing Frontend Code via Brython
- Brython is a Python interpreter that runs in the browser. It is used to execute Python code in the browser.
- Brython code is found in the `brython` directory. When you want to execute code on the client, you import the
  the Brython module on the server. This means that imports to `browser` inside a Byrthon module
  need to be inside a `try/catch` because they are also executed on the server.
- Brython code is executed in ReactPy like this:

Example (server):
```python
from heavy_stack_brython.navigate import open_new_tab

from heavy_stack.frontend.brython_executors import BrythonExecutorContext
from heavy_stack.frontend.reactpy_util import heavy_use_effect
from heavy_stack.frontend.types import Component


@component
def MyComponent() -> Component:
  brython_executor = use_context(BrythonExecutorContext)

  def my_effect_func():
    brython_executor.call(open_new_tab, url=to)

  heavy_use_effect(my_effect_func, [])

  ...
```

From the Brython side:
```python
from reactpy_bridge import called_from_reactpy

try:
    from browser import window  # type: ignore
except ImportError:
    pass


@called_from_reactpy
def navigate_to(url: str):
    window.location.href = url


@called_from_reactpy
def open_new_tab(url: str):
    window.open(url, "_blank")
```

You can also retrieve data from the client by providing a callback function that takes the return value.
Remember to keep in the mind that the client could manipulate the result.

Example:
```python
brython_executor.call(
    get_timezone_name_and_offset,
    lambda v: assign_user_timezone(*(json.loads(v[:200]))),
)
```

### Brython Limitations:
- Changes to Brython code will not take effect until the user refreshes the page.
- Brython code can't be debugged via the browser, you'll need to use `print` statements and look at the console.
  - For this reason, its recommended that Brython logic is kept light and simple.
- All arguments passed to the Brython function must be keyword arguments.


### Suggestion
When working with the DOM, have ChatGPT write Brython code for you. It knows how!


## Custom Component Type
The Heavy Stack uses `from heavy_stack.frontend.types import Component` as the return type for component objects.
This is because the current typing of ReactPy results in erroenous type checking errors since there are many types
that are valid. Likewise, it's a common pattern to build a list of children objects in a component. This would
be used there as well.

Example:
```python
from reactpy import component, html

from heavy_stack.frontend.types import Component


@component
def MyComponent() -> Component:
    children: list[Component] = []

    if something:
        children.append(SomeComponent())
    if something_else:
        children.append(html.p("Hello"))

    return html.div(*children)
```


## Custom Classes for SQLModel
To avoid creating a table class but accidentally forgetting to tell `SQLModel` it is a table, use `HeavyModel` as the base class for tables.
If you use the `dev_scripts/add_table.py` script, `HeavyModel` will already be the base class. This will save you your hair when you can't
figure out why your table isn't getting generated, and you have `Table=True` instead of `table=True` in the code.


## Wrapped Logic Around ReactPy
The heavy stack has logic wrappers around `use_effect`, `event`, and `use_context`.
They are `heavy_use_effect`, `heavy_event`, and `heavy_use_context` respectively.

These provide opportunities to inject additional context, specifically a new database connection. You can
modify the logic to provide your own values for your project in `heavy_wrapper_common`. For example,
Heavy Resume uses `heavy_wrapper_common` to add more user information and classes that manage decryption
for the user to the `HeavyContext` object. Heavy Resume also uses a caching layer here to reduce database calls.
This is recommended but you will need to come up with your own implementation.

Note that `async` functions will get a `HeavyContext` object passed in. Regular functions will not. All database
calls need to be done within an `async` function.


## Time Tracking
The heavy stack dev container comes with ptyme-track already installed. This does time tracking for you by detecting file changes.

The tracking is done in the background in a file that's ignored by git. To get it recorded you need to cement it in a file with your username (so you properly get credit). Please see https://github.com/JamesHutchison/ptyme-track?tab=readme-ov-file#cementing-work for more information. You would then git commit this file.

If Taco Bell suddenly hits you, and you need to step away, it'll stop tracking time after 5 minutes of inactivity. It also does padding around start / stop times, and is explained in the repo's readme.


## Load Testing
- Load testing uses Locust to stress test the system.
  - Step 1: Start a server with data recording on
  - Step 2: Start the server normally
  - Step 3: Update the locust file to use your data recording
  - Step 4: Run locust, pointing it at your file

### Step 1
- Go to "Run and Debug", select "Data Record Heavy Stack"
- Open your page and start doing the user actions you want to loop
- When you are done, go back to the terminal and press Ctrl+C to stop the recording
- Move your recording to where you feel it is appropriate. The locust file is under `tests/load_testing/data_recorder_locust.py`.
  - A demo file is in the same directory.

### Step 2
- Go to "Run and Debug", select "Run Heavy Stack", and under the `Run` menu select `Run without debugging`

### Step 3
- Open `tests/load_testing/data_recorder_locust.py` and update the `data_recording_file` attribute to point to your new file.
- Open your recording file and find the connection that corresponds to your activity. You can usually just jump to the bottom.
  If you need to, format the file in VS Code to make it easier. The structure of the recording file is just a list with each item as follows:
  - `send` / `recv` (server perspective)
  - `connection_id`
  - `timestamp`
  - `payload`
- Simply copy the `connection_id` and update `connection_id` attribute in the `data_recorder_locust.py` file with the value.
  You know you got the right one because it should be duplicated a lot.

### Step 4
- Open the VS Code Tasks menu, select `Tasks: Run Task`, then select `load test heavy-stack`
- Open the browser window at `localhost:8089` and configure the max users and step amount. You do not need to populate the host.


### Load Testing Notes
- This is very new and immature. It was made for testing locally and was not made for CI testing, so just keep that in mind when it applying to other use cases. It should be 100% capable of doing CI and production load testing, it just may require some code changes to get there.
- Keep in mind that when you have a browser window open, it will attempt to reconnect. It is recommended you start with no browser
  windows open.
- The locust should, in a loop, connect, play out the actions, and disconnect. When making changes, start with 1 user to easily confirm that is happening.
- You can debug things by enabling printing messages. This is done in the locust file by simply uncommenting the appropriate lines of code.


## Custom ReactPy
This is currently using a custom version of ReactPy found here: https://github.com/JamesHutchison/reactpy/tree/hot-reloading

It has features that are in this draft PR on the original repo:
https://github.com/reactive-python/reactpy/pull/1204

It also has additional hot reloading features that were kept out of that PR.

When the codespace is created, a clone of the repo is made in `/workspaces/reactpy`

When the codespace starts, a copy of the files necessary for building production are made in `custom_reactpy`.

When you run Heavy Resume in the codespace, it actually uses softlinks to `/workspaces/reactpy`. The `custom_reactpy` directory is only needed for testing docker builds of the production image. This is because docker does not support softlinks that point to directories outside of the build context.

It is important to note that whatever version of ReactPy is installed, IS NOT USED AT THIS TIME.


## External Links
 - [ReactPy](https://github.com/reactive-python/reactpy)
 - [ReactPy GPT](https://chat.openai.com/g/g-OXia9CHNG-reactpy-gpt)
 - [Sanic](https://github.com/sanic-org/sanic)
 - [SQLModel](https://github.com/tiangolo/sqlmodel)
   - [Pydantic](https://github.com/pydantic/pydantic)
   - [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy)
   - [Alembic](https://github.com/alembic/alembic)
 - [MegaMock](https://github.com/JamesHutchison/megamock)
 - [PyTest Hot Reloading](https://github.com/JamesHutchison/pytest-hot-reloading)
 - [Heavy Resume Discord](https://discord.gg/f8AsGpUjKM)
