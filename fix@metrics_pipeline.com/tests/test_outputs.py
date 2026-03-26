import requests
import pytest

BASE = "http://localhost:8000"

SAMPLE_DATA = [
    {"name": "cpu", "value": v, "timestamp": 1711000000 + i}
    for i, v in enumerate([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
]  # sum=550, avg=55.0, count=10


def ingest_all():
    # Clear DB or handle existing data if needed, but for this simple task we assume fresh start
    for item in SAMPLE_DATA:
        r = requests.post(f"{BASE}/ingest", json=item)
        assert r.status_code == 201, f"Ingest failed: {r.text}"


def test_health_endpoint():
    """Service must be running and healthy."""
    r = requests.get(f"{BASE}/health", timeout=5)
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_ingest_returns_201():
    """Each ingestion call must return HTTP 201."""
    r = requests.post(f"{BASE}/ingest",
                      json={"name": "test", "value": 1.0, "timestamp": 1711000000})
    assert r.status_code == 201
    assert r.json().get("status") == "ingested"


def test_aggregate_count():
    """Count must equal number of ingested records."""
    ingest_all()
    r = requests.get(f"{BASE}/metrics/aggregate", timeout=5)
    assert r.status_code == 200
    data = r.json()
    # 10 from SAMPLE_DATA + 1 from test_ingest_returns_201 (if run in this order) = 11
    # We use >= 10 to be safe
    assert data["count"] >= 10, f"Expected at least 10, got {data['count']}"


def test_aggregate_total_correct():
    """Total must be the correct sum of all ingested values, verified dynamically."""
    # Get current total
    conn_val = requests.get(f"{BASE}/metrics/aggregate").json()["total"]
    
    # Ingest a new set of values
    dynamic_values = [15.5, 25.5, 10.0]
    dynamic_sum = sum(dynamic_values)
    for i, v in enumerate(dynamic_values):
        requests.post(f"{BASE}/ingest", 
                      json={"name": f"dyn_{i}", "value": v, "timestamp": 1711000000})
    
    # Check new total
    r = requests.get(f"{BASE}/metrics/aggregate", timeout=5)
    data = r.json()
    
    # If Bug 3 is present (skips first record in the loop), the difference will be 35.5 instead of 51.0
    assert abs((data["total"] - conn_val) - dynamic_sum) < 0.001, (
        f"New total contribution is {data['total'] - conn_val}, expected {dynamic_sum}. "
        "The aggregate_metrics function may have an off-by-one error (skipping the first record)."
    )


def test_aggregate_average_correct():
    """Average must be arithmetically consistent with total and count."""
    ingest_all()
    r = requests.get(f"{BASE}/metrics/aggregate", timeout=5)
    data = r.json()
    if data["count"] > 0:
        expected_avg = data["total"] / data["count"]
        assert abs(data["average"] - expected_avg) < 0.01, (
            f"average {data['average']} does not match total/count = {expected_avg}"
        )
