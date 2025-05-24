import sqlite3

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

def create_tables(db_path=":memory:"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(SCHEMA)
    conn.commit()
    conn.close()

# Example usage:
# create_tables("telemetry.db")