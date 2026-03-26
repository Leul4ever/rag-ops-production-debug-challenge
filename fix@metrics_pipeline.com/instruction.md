# Fix the Broken Metrics Aggregation Service

You are a DevOps engineer on-call. The metrics aggregation service has broken
after a dependency update and is failing in production. Your job is to diagnose
all issues and fix the service so it works correctly.

## The Service

The service is located in `/app`. It is a Python Flask application that:
- Accepts metric events via POST `/ingest`
- Stores them in a SQLite database at `/app/metrics.db`
- Exposes `/metrics/aggregate` to return total, average, and count of all stored values

## Your Task

1. Fix all issues so the service starts successfully.
2. Ensure the service can ingest data and return correct aggregation results.

## Running the Service

Start the service with:
```bash
cd /app && python start.sh
```

Or directly:
```bash
cd /app && python app.py
```

The service listens on port 8000.

## API Reference

**POST /ingest**
```json
{"name": "cpu_usage", "value": 42.5, "timestamp": 1711000000}
```
Response: `{"status": "ingested"}`

**GET /metrics/aggregate**
Response: `{"total": 550.0, "average": 55.0, "count": 10}`

**GET /health**
Response: `{"status": "ok"}`

> Note: Do not hardcode any expected values. Fix the underlying code bugs.
