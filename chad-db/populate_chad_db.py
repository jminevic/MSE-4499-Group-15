
import sqlite3
import random
import datetime
from pathlib import Path

DB_PATH = Path("wrist_device_populated.db")

SCHEMA = """
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
"""

TEST_TYPES = [
    ('Pronation/Supination ROM',),
    ('Pronation/Supination Torque',),
    ('Pinch Grip',),
    ('Radial/Ulnar Deviation ROM',),
    ('Wrist Flexion/Extension ROM',),
]

POSITIONS = [
    'Quarterback','Running Back','Wide Receiver','Tight End','Offensive Lineman',
    'Defensive Lineman','Linebacker','Cornerback','Safety','Kicker','Punter'
]

MEASUREMENT_TYPES = [
    (1, 'Pronation Angle', 'deg'),
    (1, 'Supination Angle', 'deg'),
    (2, 'Pronation Torque', 'N·m'),
    (2, 'Supination Torque', 'N·m'),
    (3, 'Thumb-Index Pinch Force', 'N'),
    (3, 'Thumb-Middle Pinch Force', 'N'),
    (3, 'Thumb-Ring Pinch Force', 'N'),
    (3, 'Thumb-Pinky Pinch Force', 'N'),
    (4, 'Radial Deviation Angle', 'deg'),
    (4, 'Ulnar Deviation Angle', 'deg'),
    (5, 'Wrist Flexion Angle', 'deg'),
    (5, 'Wrist Extension Angle', 'deg'),
]

POSITION_PROFILE = {
    'Quarterback': {'h': (191, 5), 'w': (100, 7)},
    'Running Back': {'h': (180, 5), 'w': (96, 8)},
    'Wide Receiver': {'h': (185, 6), 'w': (90, 7)},
    'Tight End': {'h': (196, 5), 'w': (114, 7)},
    'Offensive Lineman': {'h': (196, 5), 'w': (141, 12)},
    'Defensive Lineman': {'h': (193, 5), 'w': (129, 10)},
    'Linebacker': {'h': (188, 5), 'w': (111, 8)},
    'Cornerback': {'h': (180, 5), 'w': (86, 6)},
    'Safety': {'h': (184, 5), 'w': (94, 7)},
    'Kicker': {'h': (183, 5), 'w': (85, 6)},
    'Punter': {'h': (188, 5), 'w': (91, 6)},
}

METRIC_PROFILES = {
    'Pronation Angle': 84, 'Supination Angle': 88,
    'Pronation Torque': 9.8, 'Supination Torque': 10.1,
    'Thumb-Index Pinch Force': 81, 'Thumb-Middle Pinch Force': 76,
    'Thumb-Ring Pinch Force': 71, 'Thumb-Pinky Pinch Force': 63,
    'Radial Deviation Angle': 20, 'Ulnar Deviation Angle': 33,
    'Wrist Flexion Angle': 74, 'Wrist Extension Angle': 71
}

FORCE_MULT = {
    'Quarterback': 1.03, 'Running Back': 1.04, 'Wide Receiver': 1.00, 'Tight End': 1.08,
    'Offensive Lineman': 1.18, 'Defensive Lineman': 1.15, 'Linebacker': 1.10,
    'Cornerback': 0.97, 'Safety': 1.00, 'Kicker': 0.94, 'Punter': 0.95
}

ROM_MULT = {
    'Quarterback': 1.06, 'Running Back': 1.00, 'Wide Receiver': 1.02, 'Tight End': 0.98,
    'Offensive Lineman': 0.93, 'Defensive Lineman': 0.95, 'Linebacker': 0.97,
    'Cornerback': 1.01, 'Safety': 1.00, 'Kicker': 1.00, 'Punter': 1.01
}

FIRST_NAMES = ["Liam","Noah","Ethan","Mason","Logan","Lucas","Aiden","Carter","Owen","Wyatt","Jack","Leo","Julian","Hudson","Grayson","Ezra","Caleb","Isaac","Nathan","Jaxon",
               "Gabriel","Hunter","Roman","Levi","Aaron","Connor","Jude","Miles","Cole","Asher","Blake","Eli","Samuel","Adam","Dominic","Jordan","Parker","Tyler","Xavier","Micah",
               "Ryan","Jason","Dylan","Austin","Chase","Colin","Brody","Zachary","Nolan","Evan"]
LAST_NAMES = ["Smith","Johnson","Williams","Brown","Jones","Miller","Davis","Garcia","Rodriguez","Wilson","Martinez","Anderson","Taylor","Thomas","Hernandez","Moore","Martin","Jackson","Thompson","White",
              "Lopez","Lee","Gonzalez","Harris","Clark","Lewis","Young","Allen","King","Wright","Scott","Green","Baker","Adams","Nelson","Hill","Ramirez","Campbell","Mitchell","Roberts",
              "Carter","Phillips","Evans","Turner","Torres","Parker","Collins","Edwards","Stewart","Morris"]

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def gen_name(used):
    while True:
        full = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        if full not in used:
            used.add(full)
            return full

def trial_triplet(avg, sd):
    values = [round(random.gauss(avg, sd), 1) for _ in range(3)]
    return values, round(sum(values) / 3, 1)

def build_db():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    cur.executemany("INSERT INTO test_types (test_name) VALUES (?)", TEST_TYPES)
    cur.executemany("INSERT INTO positions (position_name) VALUES (?)", [(p,) for p in POSITIONS])
    cur.executemany(
        "INSERT INTO measurement_types (test_type_id, measurement_name, unit) VALUES (?, ?, ?)",
        MEASUREMENT_TYPES,
    )
    conn.commit()
    return conn

def generate_measurement(position, dominant_hand, measurement_name, session_index):
    base = METRIC_PROFILES[measurement_name]
    if 'Torque' in measurement_name or 'Force' in measurement_name:
        mean = base * FORCE_MULT[position]
        sd = 2.0 if 'Force' in measurement_name else 0.5
    else:
        mean = base * ROM_MULT[position]
        sd = 3.0

    mean += random.gauss(0, sd * 0.25)

    def values_for_hand(hand):
        hand_mult = 1.0 if hand == dominant_hand else (0.96 if ('Force' in measurement_name or 'Torque' in measurement_name) else 0.98)
        session_mult = 1.0 + (session_index - 1) * random.uniform(-0.01, 0.015)
        hand_mean = mean * hand_mult * session_mult
        values, _ = trial_triplet(hand_mean, sd * 0.55)

        if 'Angle' in measurement_name:
            lo, hi = 5, 110
        elif 'Torque' in measurement_name:
            lo, hi = 4, 18
        else:
            lo, hi = 35, 140

        values = [round(clamp(v, lo, hi), 1) for v in values]
        avg = round(sum(values) / 3, 1)
        return values, avg

    return values_for_hand

def populate():
    random.seed(7)
    conn = build_db()
    cur = conn.cursor()

    pos_id = {name: pid for pid, name in cur.execute("SELECT position_id, position_name FROM positions")}
    test_id = {name: tid for tid, name in cur.execute("SELECT test_type_id, test_name FROM test_types")}

    meas_by_test = {}
    for mid, tid, name in cur.execute("SELECT measurement_type_id, test_type_id, measurement_name FROM measurement_types"):
        meas_by_test.setdefault(tid, []).append((mid, name))

    position_pool = (
        ['Offensive Lineman'] * 8 + ['Defensive Lineman'] * 6 + ['Linebacker'] * 6 +
        ['Wide Receiver'] * 7 + ['Running Back'] * 5 + ['Cornerback'] * 5 +
        ['Safety'] * 4 + ['Tight End'] * 3 + ['Quarterback'] * 3 +
        ['Kicker'] * 2 + ['Punter'] * 1
    )
    random.shuffle(position_pool)
    position_pool = position_pool[:50]

    used_names = set()

    for i in range(50):
        position = position_pool[i]
        name = gen_name(used_names)
        dominant_hand = random.choice(['L', 'R']) if position in ['Quarterback', 'Punter'] else ('R' if random.random() < 0.88 else 'L')
        age = random.randint(18, 24)

        h_mean, h_sd = POSITION_PROFILE[position]['h']
        w_mean, w_sd = POSITION_PROFILE[position]['w']

        height = round(clamp(random.gauss(h_mean, h_sd), 170, 210), 1)
        weight = round(clamp(random.gauss(w_mean, w_sd), 72, 180), 1)

        cur.execute("INSERT INTO participants (full_name) VALUES (?)", (name,))
        participant_id = cur.lastrowid
        cur.execute(
            "INSERT INTO participant_positions (participant_id, position_id) VALUES (?, ?)",
            (participant_id, pos_id[position]),
        )

        if random.random() < 0.18:
            secondary_options = [p for p in POSITIONS if p != position and abs(POSITION_PROFILE[p]['h'][0] - h_mean) < 12]
            secondary = random.choice(secondary_options)
            try:
                cur.execute(
                    "INSERT INTO participant_positions (participant_id, position_id) VALUES (?, ?)",
                    (participant_id, pos_id[secondary]),
                )
            except sqlite3.IntegrityError:
                pass

        num_sessions = 2 if random.random() < 0.28 else 1

        for session_index in range(1, num_sessions + 1):
            dt = datetime.datetime(2026, random.randint(1, 3), random.randint(1, 22), random.randint(8, 17), random.choice([0, 15, 30, 45]), 0)
            height_session = round(height + random.uniform(-0.4, 0.4), 1)
            weight_session = round(weight + random.uniform(-2.0, 2.0), 1)
            note = random.choice([
                "Baseline screening",
                "Return-to-play screen",
                "Pre-practice capture",
                "Post-lift follow-up",
                "Routine wrist performance check"
            ])

            cur.execute(
                """INSERT INTO sessions (participant_id, trial_datetime, age_at_test, height_cm, weight_kg, notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (participant_id, dt.isoformat(sep=' '), age, height_session, weight_session, note),
            )
            session_id = cur.lastrowid

            selected_tests = random.sample(list(test_id.keys()), random.randint(3, 5))

            for test_name in selected_tests:
                runs = 2 if random.random() < 0.16 else 1
                for run_number in range(1, runs + 1):
                    started_at = dt + datetime.timedelta(minutes=random.randint(0, 60))
                    completed_at = started_at + datetime.timedelta(minutes=random.randint(2, 8))

                    cur.execute(
                        """INSERT INTO test_instances (session_id, test_type_id, run_number, started_at, completed_at, notes)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (session_id, test_id[test_name], run_number, started_at.isoformat(sep=' '), completed_at.isoformat(sep=' '), f"{test_name} run {run_number}"),
                    )
                    test_instance_id = cur.lastrowid

                    for measurement_type_id, measurement_name in meas_by_test[test_id[test_name]]:
                        value_fn = generate_measurement(position, dominant_hand, measurement_name, session_index)

                        for hand in ['L', 'R']:
                            values, average = value_fn(hand)
                            cur.execute(
                                """INSERT INTO result_sets (test_instance_id, measurement_type_id, hand, average_value)
                                   VALUES (?, ?, ?, ?)""",
                                (test_instance_id, measurement_type_id, hand, average),
                            )
                            result_set_id = cur.lastrowid

                            for trial_number, trial_value in enumerate(values, start=1):
                                cur.execute(
                                    """INSERT INTO trial_values (result_set_id, trial_number, trial_value)
                                       VALUES (?, ?, ?)""",
                                    (result_set_id, trial_number, trial_value),
                                )

    conn.commit()

    for table in ['participants', 'participant_positions', 'sessions', 'test_instances', 'result_sets', 'trial_values']:
        total = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {total}")

    conn.close()
    print(f"\nCreated {DB_PATH.resolve()}")

if __name__ == "__main__":
    populate()
