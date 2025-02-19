import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)
db = "KOHVIKUD.db"
time_format = "%H:%M"

def get_db_connection():
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn

def get_cafe(cafe_id):
    return fetch_one("SELECT * FROM SOOKLA WHERE id = ?", (cafe_id,))

def cafe_is_valid(data):
    return set(["name", "location", "time_open", "time_closed"]).issubset(data)

@app.route('/cafes', methods=['GET'])
def get_all_cafes():
    return jsonify(fetch_all("SELECT * FROM SOOKLA")), 200

@app.route('/cafes/time', methods=['GET'])
def get_cafes_by_time():
    start_time = request.args.get('start')
    end_time = request.args.get('end')

    if not start_time or not end_time:
        return jsonify({"error": "start ja end peavad olema antud (HH:MM)"}), 400

    try:
        start_time = datetime.strptime(start_time, time_format).time()
        end_time = datetime.strptime(end_time, time_format).time()
    except ValueError:
        return jsonify({"error": "Aja formaat peab olema HH:MM"}), 400

    cafes = fetch_all("SELECT * FROM SOOKLA")
    filtered = [cafe for cafe in cafes if start_time >= datetime.strptime(cafe["time_open"], time_format).time() and end_time <= datetime.strptime(cafe["time_closed"], time_format).time()]

    return jsonify(filtered), 200

@app.route('/cafes', methods=['POST'])
def add_cafe():
    data = request.get_json()
    if not data or not cafe_is_valid(data):
        return jsonify({"error": "Puuduvad vajalikud väljad"}), 400

    execute_query("""
        INSERT INTO SOOKLA (name, location, service_provider, time_open, time_closed)
        VALUES (?, ?, ?, ?, ?)
    """, (data["name"], data["location"], data.get("service_provider"), data["time_open"], data["time_closed"]))

    return jsonify({"message": "Uus kohvik lisatud"}), 201


@app.route('/cafes/<int:cafe_id>', methods=['PUT'])
def update_cafe(cafe_id):
    row = get_cafe(cafe_id)
    if not row:
        return jsonify({"error": "Sellise ID-ga kohvikut ei leitud"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    updated_values = {key: data.get(key, row[key]) for key in ["name", "location", "service_provider", "time_open", "time_closed"]}

    execute_query("""
        UPDATE SOOKLA SET name=?, location=?, service_provider=?, time_open=?, time_closed=?
        WHERE id=?
    """, (*updated_values.values(), cafe_id))

    return jsonify({"message": "Kohvik uuendatud"}), 200


@app.route('/cafes/<int:cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    row = get_cafe(cafe_id)
    if not row:
        return jsonify({"error": "Sellise ID-ga kohvikut ei leitud"}), 404

    conn = get_db_connection()
    conn.execute("DELETE FROM SOOKLA WHERE id = ?", (cafe_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Kohvik kustutatud"}), 200


def fetch_all(query, params=()):
    conn = get_db_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def fetch_one(query, params=()):
    conn = get_db_connection()
    row = conn.execute(query, params).fetchone()
    conn.close()
    return dict(row) if row else None

def execute_query(query, params=(), commit=True):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(query, params)
    if commit:
        conn.commit()
    conn.close()


if __name__ == '__main__':
    app.run(port=5000)