#!/bin/bash
set -e

mkdir -p /logs/verifier
touch /logs/verifier/reward.txt

# Ensure test requirements are installed
pip install -r /tests/requirements-test.txt --quiet

# Start the app in the background
cd /app
python app.py &
APP_PID=$!

# Wait for app to be ready
sleep 3

# Run functional tests
pytest /tests/test_outputs.py -v

TEST_EXIT=$?

# Stop app
kill $APP_PID 2>/dev/null || true

if [ $TEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit $TEST_EXIT
