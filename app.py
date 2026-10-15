
from flask import Flask, jsonify
from psycopg.rows import dict_row
from database import get_db_connection

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "application": "DevOps Task Manager",
        "status": "running",
        "version": "2.1"
    })


@app.route("/tasks")
def get_tasks():
    with get_db_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT id, title, completed FROM tasks ORDER BY id"
            )
            tasks = cur.fetchall()

    return jsonify(tasks)


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
