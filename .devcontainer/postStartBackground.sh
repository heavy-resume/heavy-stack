#!/usr/bin/env bash
set -a; source /workspaces/heavy-stack/.env; set +a

docker compose up --wait

sleep 30

poetry run python dev_scripts/pave_db.py

ptyme-track --standalone &
