#!/usr/bin/env bash

# run in the background at startup
nohup bash -c ".devcontainer/postStartBackground.sh &" > ".dev_container_logs/postStartBackground.out"

# note: do NOT have the last command run in the background else it won't really run!
sudo sysctl fs.inotify.max_user_instances=4096

# rebuild the latest reactpy JIC it changed
# unfortunately this is needed for docker and docker won't use a softlink because it leaves the build context
rm -rf custom_reactpy
mkdir custom_reactpy
cp -r /workspaces/reactpy/src/js/app/dist/ custom_reactpy/dist
cp -r /workspaces/reactpy/src/py/reactpy/reactpy custom_reactpy/reactpy
