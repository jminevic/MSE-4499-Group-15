PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS participants (
    participant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS positions (
    position_id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS participant_positions (
    participant_id INTEGER NOT NULL,
    position_id INTEGER NOT NULL,
    PRIMARY KEY (participant_id, position_id),
    FOREIGN KEY (participant_id) REFERENCES participants(participant_id) ON DELETE CASCADE,
    FOREIGN KEY (position_id) REFERENCES positions(position_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id INTEGER NOT NULL,
    trial_datetime TEXT NOT NULL,
    age_at_test INTEGER,
    height_cm REAL,
    weight_kg REAL,
    notes TEXT,
    FOREIGN KEY (participant_id) REFERENCES participants(participant_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS test_types (
    test_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS measurement_types (
    measurement_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_type_id INTEGER NOT NULL,
    measurement_name TEXT NOT NULL,
    unit TEXT,
    FOREIGN KEY (test_type_id) REFERENCES test_types(test_type_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS test_instances (
    test_instance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    test_type_id INTEGER NOT NULL,
    run_number INTEGER NOT NULL DEFAULT 1,
    started_at TEXT,
    completed_at TEXT,
    notes TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (test_type_id) REFERENCES test_types(test_type_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS result_sets (
    result_set_id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_instance_id INTEGER NOT NULL,
    measurement_type_id INTEGER NOT NULL,
    hand TEXT NOT NULL CHECK (hand IN ('L', 'R')),
    average_value REAL,
    FOREIGN KEY (test_instance_id) REFERENCES test_instances(test_instance_id) ON DELETE CASCADE,
    FOREIGN KEY (measurement_type_id) REFERENCES measurement_types(measurement_type_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trial_values (
    trial_value_id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_set_id INTEGER NOT NULL,
    trial_number INTEGER NOT NULL CHECK (trial_number IN (1,2,3)),
    trial_value REAL NOT NULL,
    FOREIGN KEY (result_set_id) REFERENCES result_sets(result_set_id) ON DELETE CASCADE,
    UNIQUE (result_set_id, trial_number)
);