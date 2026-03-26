import yaml
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

# BUG 2: Wrong path. File is at './settings.yaml', not './config/settings.yaml'
with open('./config/settings.yaml', 'r') as f:
    config = yaml.safe_load(f)

DB_PATH = config.get('db_path', '/app/metrics.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT    NOT NULL,
            value     REAL    NOT NULL,
            timestamp INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def aggregate_metrics(values):
    """Compute total and average of metric values."""
    total = 0.0
    count = 0
    # BUG 3: range(1, len(values)) skips the first element
    for i in range(1, len(values)):
        total += values[i]
        count += 1
    if count == 0:
        return 0.0, 0.0
    return total, total / count


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/ingest', methods=['POST'])
def ingest():
    data = request.json
    name = data.get('name')
    value = float(data.get('value'))
    timestamp = int(data.get('timestamp'))
    conn = get_db()
    conn.execute(
        'INSERT INTO metrics (name, value, timestamp) VALUES (?, ?, ?)',
        (name, value, timestamp)
    )
    conn.commit()
    conn.close()
    return jsonify({'status': 'ingested'}), 201


@app.route('/metrics/aggregate')
def metrics_aggregate():
    conn = get_db()
    cur = conn.execute('SELECT value FROM metrics')
    rows = cur.fetchall()
    conn.close()
    values = [r[0] for r in rows]
    total, avg = aggregate_metrics(values)
    return jsonify({'total': total, 'average': avg, 'count': len(values)})


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000)
