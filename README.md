# The Heavy Stack
The Heavy Stack is the stack used by Heavy Resume. This is a point in time fork of the tech stack and syncing between Heavy Resume and this fork will be done periodically. This is intended to be treated like a starting template.

## Features
- Pre-made dev container, docker files
- Top to Bottom Python (Sanic, custom ReactPy, Brython)
- PostgreSQL, PG Vector, CockroachDB
- SQL Model (SQLAlchemy + Pydantic)
- Hot reloading, both server and tests
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

## Migrations
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
  - TLDR: You just delete the old files and modify the oldest migration to not have a previous revision. Recreating a database from scratch via migrations is an antipattern. If you really need to start fresh you

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

## Notes
- This is very new and immature. It was made for testing locally and was not made for CI testing, so just keep that in mind when it applying to other use cases. It should be 100% capable of doing CI and production load testing, it just may require some code changes to get there.
- Keep in mind that when you have a browser window open, it will attempt to reconnect. It is recommended you start with no browser
  windows open.
- The locust should, in a loop, connect, play out the actions, and disconnect. When making changes, start with 1 user to easily confirm that is happening.
- You can debug things by enabling printing messages. This is done in the locust file by simply uncommenting the appropriate lines of code.
