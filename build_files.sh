#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Building the project..."

# Install Python dependencies
pip install -r requirements.txt

# Run Django database migrations
# This applies any changes from your models to the live database schema.
python manage.py migrate

# Collect static files
# This gathers all static files (CSS, JS, images) into a single directory
# that Vercel can serve efficiently.
python manage.py collectstatic --noinput --clear

echo "Build finished."