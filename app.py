from flask import Flask, jsonify

app = Flask(__name__)

tasks = [
    {"id": 1, "title": "Configure Docker", "completed": True},
    {"id": 2, "title": "Write automated tests", "completed": False},
    {"id": 3, "title": "Set up CI/CD pipeline", "completed": False},
]


@app.route("/")
def home():
    return jsonify({
        "application": "DevOps Task Manager",
        "status": "running"
    })


@app.route("/tasks")
def get_tasks():
    return jsonify(tasks)


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)