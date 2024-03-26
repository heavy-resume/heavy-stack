# The Heavy Stack
The Heavy Stack is the stack used by Heavy Resume. This is a point in time fork of the tech stack and syncing between Heavy Resume and this fork will be done periodically. This is intended to be treated like a starting template.


## Features
- Pre-made dev container, docker files
- Top to Bottom Python (Sanic, custom ReactPy, Brython)
- PostgreSQL, PG Vector, CockroachDB
- SQL Model (SQLAlchemy + Pydantic)
- Hot reloading, both server and tests
- Action recording and load testing
- Time tracking
- Established patterns and examples


## Renaming the project
After checking out the repo, you should rename the project. Run `python rename_project.py` and follow the prompts.

Note that this isn't well tested at the moment and may be incomplete. Remember to delete the `.git` directory if things look good.

If using github codespaces, you may not see the workspace directory rename until after you create a fresh codespace.


## Prescribed Running Method
- The Heavy Stack was built with Github Codespaces or similar in mind. Running locally using docker can create complications such as poor performance, failure to detect changes, or I/O failures if the container is misconfigured or Docker has become unstable.


## Quickstart - Server
- Go to "Run and Debug", select "Hot Reload Heavy Stack', then click the play button.


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
- `certs` - Contain the SSL certs used by the client. These are not private.
- `demo_data` - Contains data that is used for testing and development.
- `dockerfiles` - Contains the Dockerfiles for the production and development images.
- `dragons` - Contains txt files with warnings about different gotchas.
- `heavy_stack` - Contains the main code for the project.
    - `heavy_stack/backend` - Contains most backend logic
    - `heavy_stack/frontend` - Contains the ReactPy logic
    - `heavy_stack/shared_models` - Shared models are domain objects that are used by both the frontend and backend. They're usually used by the frontend.
- `static` - static files such as CSS and images are found here
- `tests` - Contains the tests for the project, including unit and integration tests.


## Class responsibilities
- `SQL Models` - These are used for database access and are the "raw" data. Encryption operations are handled by the model via methods that take a data key.
- `Shared Models` - These are domain objects and typically used by the frontend (ReactPy).
    There is no requirement that shared models match the SQL Model, but they often are close.
    The shared models should structure data like you would intuitively expect, and not just mirror the database schema.
- `Model Mungers` - These are used to take the output of an operation (usually a SQL Model) and convert it to the appropriate output model.
- `Model Managers` - These handle the business logic around a model. They usually take in at least one munger as an argument.
- `Repositories` - These handle the database operations and work with SQL Models. Managers frequently have at least one repository.

### Add Table Script
- `dev_scripts/add_table.py` - Walks you through adding a new table, creating the SQL Model, Shared Model, Model Munger, Model Manager, and Repository.
- This script is not required and some database tables or domain objects may not fit into this paradigm. That said, you can always delete what isn't used.


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
- Move your recording where you feel it is appropriate. The locust file is under `tests/load_testing/data_recorder_locust.py`

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
  You know you got the right one bcause it should be duplicated a lot.

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
This is currently using a custom version of ReactPy found here: https://github.com/JamesHutchison/reactpy

It has features that are in this draft PR on the original repo:
https://github.com/reactive-python/reactpy/pull/1204

When the codespace is created, a clone of the repo is made in `/workspaces/reactpy`

When the codespace starts, a copy of the files necessary for building production are made in `custom_reactpy`.

When you run Heavy Resume in the codespace, it actually uses softlinks to `/workspaces/reactpy`. The `custom_reactpy` directory is only needed for testing docker builds of the production image. This is because docker does not support softlinks that point to directories outside of the build context.

It is important to note that whatever version of ReactPy is installed, IS NOT USED AT THIS TIME.
