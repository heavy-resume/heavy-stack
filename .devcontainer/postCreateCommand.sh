#!/usr/bin/env bash
set -e

# git settings
git config --global pull.rebase true
git config --global remote.origin.prune true

# install shell-ai
pipx install shell-ai

# install ptyme-track
pipx install ptyme-track
ptyme-track --ensure-secret

# if the .venv directory was mounted as a named volume, it needs the ownership changed
sudo chown vscode .venv || true

# make the python binary location predictable
poetry config virtualenvs.in-project true
poetry install --with=dev || true

mkdir -p .dev_container_logs
echo "*" > .dev_container_logs/.gitignore

# create .env
if [ ! -f ".env" ]; then
  cp .devcontainer/template.env .env
fi

# installing reactpy if its not already cloned
if [ ! -d "/workspaces/reactpy" ]; then
  git clone -b add-jurigged-decorator-workaround https://github.com/JamesHutchison/reactpy.git /workspaces/reactpy
  rm -rf .venv/lib/python3.11/site-packages/reactpy
  ln -s /workspaces/reactpy/src/py/reactpy/reactpy .venv/lib/python3.11/site-packages/reactpy
  ln -s /workspaces/reactpy/src/js /workspaces/reactpy/src/py/reactpy/reactpy/_static
  cd /workspaces/reactpy/src/js
  npm install
  cd app/node_modules/@reactpy/client
  rm -rf dist
  ln -s ../../../../packages/@reactpy/client/dist dist
  cd ../../../..
  npm run build
  cd /workspaces/heavy-stack
fi
