#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Building the project..."

# Use python3.9 -m pip to ensure we use the correct installer
# for the runtime specified in vercel.json
python3.9 -m pip install -r requirements.txt

# Run Django database migrations
python3.9 manage.py migrate

# Collect static files
python3.9 manage.py collectstatic --noinput --clear

echo "Build finished."