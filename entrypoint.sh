#!/bin/sh
# This script ensures the application starts correctly.
# The 'exec' command replaces the shell process with the python process,
# which is a best practice for container entrypoints.
exec python app.py