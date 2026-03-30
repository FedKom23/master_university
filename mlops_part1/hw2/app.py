from flask import Flask, jsonify
import os
import psycopg2
import numpy as np

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/vector")
def vector():
    arr = np.array([1, 2, 3, 4, 5])
    return jsonify({"vector": arr})


@app.route("/db-check")
def db_check():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "testdb"),
            user=os.getenv("POSTGRES_USER", "test"),
            password=os.getenv("POSTGRES_PASSWORD", "test"),
            host=os.getenv("POSTGRES_HOST", "db"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            connect_timeout=2,
        )
        conn.close()
        return jsonify({"db": "connected"})
    except Exception as e:
        return jsonify({"db": "error", "details": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 9998))
    app.run(host="0.0.0.0", port=port)
