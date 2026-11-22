import os
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_NAME = os.getenv("DB_NAME", "aceest_fitness.db")
APP_VERSION = os.getenv("APP_VERSION", "3.2.4")

PROGRAMS = {
    "Fat Loss (FL)": {"factor": 22, "desc": "Full-body fat loss"},
    "Muscle Gain (MG)": {"factor": 35, "desc": "Hypertrophy split"},
    "Beginner (BG)": {"factor": 26, "desc": "Simple beginner full-body"},
}


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT,
            calories INTEGER,
            membership_status TEXT DEFAULT 'Active'
        )
        """
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return jsonify(
        {
            "service": "ACEest Fitness & Gym",
            "version": APP_VERSION,
            "status": "running",
        }
    ), 200


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/programs", methods=["GET"])
def get_programs():
    return jsonify(PROGRAMS), 200


@app.route("/clients", methods=["POST"])
def create_or_update_client():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    program = str(data.get("program", "")).strip()
    weight = data.get("weight")
    age = data.get("age")
    height = data.get("height")

    if not name or program not in PROGRAMS:
        return jsonify({"error": "Valid name and program are required"}), 400

    calories = int(weight * PROGRAMS[program]["factor"]) if weight else None

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO clients (name, age, height, weight, program, calories)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name, age, height, weight, program, calories),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": f"Client {name} saved", "calories": calories}), 201


@app.route("/clients/<name>", methods=["GET"])
def get_client(name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE name=?", (name,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Client not found"}), 404
    return jsonify(dict(row)), 200


@app.route("/bmi", methods=["POST"])
def compute_bmi():
    data = request.get_json(silent=True) or {}
    height = data.get("height", 0)
    weight = data.get("weight", 0)
    if not height or not weight or height <= 0 or weight <= 0:
        return jsonify({"error": "Height and weight must be positive numbers"}), 400

    bmi = round(weight / ((height / 100.0) ** 2), 1)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return jsonify({"bmi": bmi, "category": category}), 200


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
