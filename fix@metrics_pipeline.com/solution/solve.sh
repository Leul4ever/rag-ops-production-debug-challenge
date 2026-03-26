#!/bin/bash
set -e

# Fix Bug 1: Downgrade werkzeug to compatible version
sed -i 's/werkzeug==3.0.0/werkzeug==2.3.7/' /app/requirements.txt
pip install --no-cache-dir -r /app/requirements.txt --quiet

# Fix Bug 2: Correct the config file path in app.py
sed -i "s|'./config/settings.yaml'|'./settings.yaml'|" /app/app.py

# Fix Bug 3: Fix off-by-one in aggregate_metrics (range(1,...) -> range(...))
sed -i 's/for i in range(1, len(values)):/for i in range(len(values)):/' /app/app.py

echo "All fixes applied."
