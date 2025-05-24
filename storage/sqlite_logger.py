import sqlite3
from datetime import datetime, timezone

DB_PATH = "telemetry.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS sensor_data (
        timestamp    DATETIME PRIMARY KEY,
        rpm          INTEGER,
        speed        INTEGER,
        gear         INTEGER,
        lean_angle   REAL
    );
    CREATE TABLE IF NOT EXISTS gps_path (
        lap_id       INTEGER,
        timestamp    DATETIME,
        latitude     REAL,
        longitude    REAL,
        FOREIGN KEY(lap_id) REFERENCES laps(id)
    );
    CREATE TABLE IF NOT EXISTS laps (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time   DATETIME,
        end_time     DATETIME,
        best         BOOLEAN,
        track_name   TEXT
    );
    CREATE TABLE IF NOT EXISTS checkpoints (
        lap_id           INTEGER,
        checkpoint_name  TEXT,
        timestamp        DATETIME,
        delta_vs_best    REAL,
        FOREIGN KEY(lap_id) REFERENCES laps(id)
    );
    """
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        conn.commit()

def log_sensor_data(rpm, speed, gear, lean_angle, timestamp=None):
    timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO sensor_data (timestamp, rpm, speed, gear, lean_angle) VALUES (?, ?, ?, ?, ?)",
            (timestamp, rpm, speed, gear, lean_angle)
        )
        conn.commit()

def log_gps_point(lap_id, timestamp, lat, lon):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO gps_path (lap_id, timestamp, latitude, longitude) VALUES (?, ?, ?, ?)",
            (lap_id, timestamp, lat, lon)
        )
        conn.commit()

def start_lap(track_name, start_time=None):
    start_time = start_time or datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO laps (start_time, best, track_name) VALUES (?, ?, ?)",
            (start_time, False, track_name)
        )
        lap_id = cursor.lastrowid
        conn.commit()
        return lap_id

def end_lap(lap_id, end_time=None):
    end_time = end_time or datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            "UPDATE laps SET end_time = ? WHERE id = ?",
            (end_time, lap_id)
        )
        conn.commit()

# Optionally, call create_tables() on import to ensure DB is ready
create_tables()
