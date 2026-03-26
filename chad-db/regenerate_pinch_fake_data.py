
import random
import sqlite3
import sys
from datetime import datetime, timedelta


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def get_id_map(conn, table, key_col, val_col):
    cur = conn.cursor()
    cur.execute(f"SELECT {key_col}, {val_col} FROM {table}")
    return {row[val_col]: row[key_col] for row in cur.fetchall()}


def clamp(x, low, high):
    return max(low, min(high, x))


def pinch_base_from_position(position_names):
    pos = " / ".join(position_names).lower()
    # Approximate sport-specific hand strength trends
    if any(k in pos for k in ["offensive lineman", "defensive lineman"]):
        return {"Lateral": 118, "Three-Point": 102, "Two-Point": 88}
    if any(k in pos for k in ["linebacker", "tight end", "running back"]):
        return {"Lateral": 108, "Three-Point": 94, "Two-Point": 82}
    if any(k in pos for k in ["quarterback", "wide receiver", "cornerback", "safety"]):
        return {"Lateral": 96, "Three-Point": 84, "Two-Point": 73}
    if any(k in pos for k in ["kicker", "punter"]):
        return {"Lateral": 92, "Three-Point": 80, "Two-Point": 70}
    return {"Lateral": 100, "Three-Point": 87, "Two-Point": 76}


def participant_positions(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT p.participant_id, pos.position_name
        FROM participants p
        LEFT JOIN participant_positions pp ON p.participant_id = pp.participant_id
        LEFT JOIN positions pos ON pp.position_id = pos.position_id
        ORDER BY p.participant_id
    """)
    out = {}
    for row in cur.fetchall():
        out.setdefault(row["participant_id"], [])
        if row["position_name"]:
            out[row["participant_id"]].append(row["position_name"])
    return out


def generate_trials(avg_target, spread=4.0):
    vals = []
    for _ in range(3):
        vals.append(round(random.gauss(avg_target, spread), 2))
    avg = round(sum(vals) / 3.0, 2)
    return vals, avg


def ensure_pinch_test_structure(conn):
    cur = conn.cursor()

    # Rename Pinch Grip to Pinch Test if needed
    cur.execute("SELECT test_type_id FROM test_types WHERE test_name = 'Pinch Test'")
    row = cur.fetchone()
    if row:
        pinch_test_id = row["test_type_id"]
    else:
        cur.execute("SELECT test_type_id FROM test_types WHERE test_name = 'Pinch Grip'")
        old = cur.fetchone()
        if old:
            pinch_test_id = old["test_type_id"]
            cur.execute("UPDATE test_types SET test_name = 'Pinch Test' WHERE test_type_id = ?", (pinch_test_id,))
        else:
            cur.execute("INSERT INTO test_types (test_name) VALUES ('Pinch Test')")
            pinch_test_id = cur.lastrowid

    desired = [
        ("Lateral Pinch Force", "N"),
        ("Three-Point Pinch Force", "N"),
        ("Two-Point Pinch Force", "N"),
    ]

    # Remove old pinch measurement definitions not in desired set
    cur.execute("""
        DELETE FROM measurement_types
        WHERE test_type_id = ?
          AND measurement_name NOT IN (?, ?, ?)
    """, (pinch_test_id, desired[0][0], desired[1][0], desired[2][0]))

    # Ensure desired exist
    for name, unit in desired:
        cur.execute("""
            INSERT INTO measurement_types (test_type_id, measurement_name, unit)
            SELECT ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM measurement_types
                WHERE test_type_id = ? AND measurement_name = ?
            )
        """, (pinch_test_id, name, unit, pinch_test_id, name))

    conn.commit()
    return pinch_test_id


def delete_existing_pinch_data(conn, pinch_test_id):
    cur = conn.cursor()
    # Delete all result/trial data attached to pinch test instances, then test instances
    cur.execute("""
        SELECT test_instance_id
        FROM test_instances
        WHERE test_type_id = ?
    """, (pinch_test_id,))
    ids = [row["test_instance_id"] for row in cur.fetchall()]
    if not ids:
        return 0

    qmarks = ",".join("?" for _ in ids)
    cur.execute(f"""
        DELETE FROM trial_values
        WHERE result_set_id IN (
            SELECT result_set_id FROM result_sets
            WHERE test_instance_id IN ({qmarks})
        )
    """, ids)
    cur.execute(f"DELETE FROM result_sets WHERE test_instance_id IN ({qmarks})", ids)
    cur.execute(f"DELETE FROM test_instances WHERE test_instance_id IN ({qmarks})", ids)
    conn.commit()
    return len(ids)


def repopulate_pinch_data(conn):
    cur = conn.cursor()
    pinch_test_id = ensure_pinch_test_structure(conn)
    deleted = delete_existing_pinch_data(conn, pinch_test_id)

    mtypes = get_id_map(conn, "measurement_types", "measurement_type_id", "measurement_name")
    pos_map = participant_positions(conn)

    cur.execute("""
        SELECT s.session_id, s.participant_id, s.trial_datetime
        FROM sessions s
        ORDER BY s.session_id
    """)
    sessions = cur.fetchall()

    created_instances = 0
    created_results = 0
    created_trials = 0

    for session in sessions:
        participant_id = session["participant_id"]
        positions = pos_map.get(participant_id, [])
        bases = pinch_base_from_position(positions)

        # Not every session necessarily has pinch data
        if random.random() < 0.18:
            continue

        # Sometimes repeated run on same day
        num_runs = 2 if random.random() < 0.14 else 1

        # Small hand dominance asymmetry
        dominant = random.choice(["L", "R"])

        dt = datetime.fromisoformat(str(session["trial_datetime"]).replace("Z", ""))

        for run in range(1, num_runs + 1):
            started = dt + timedelta(minutes=4 * run)
            completed = started + timedelta(minutes=2)

            cur.execute("""
                INSERT INTO test_instances
                (session_id, test_type_id, run_number, started_at, completed_at, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session["session_id"],
                pinch_test_id,
                run,
                started.strftime("%Y-%m-%d %H:%M:%S"),
                completed.strftime("%Y-%m-%d %H:%M:%S"),
                "Synthetic pinch-test data regenerated after pinch-structure update."
            ))
            test_instance_id = cur.lastrowid
            created_instances += 1

            for measurement_name, base in bases.items():
                measurement_full = f"{measurement_name} Pinch Force"
                measurement_type_id = mtypes[measurement_full]

                for hand in ["L", "R"]:
                    # dominant hand slightly stronger, second run slightly less variable
                    hand_adjust = 3.5 if hand == dominant else 0.0
                    run_adjust = random.uniform(-2.0, 2.0)
                    avg_target = clamp(base + hand_adjust + run_adjust, 45, 160)
                    spread = 3.0 if run > 1 else 4.0

                    trials, avg = generate_trials(avg_target, spread=spread)

                    cur.execute("""
                        INSERT INTO result_sets
                        (test_instance_id, measurement_type_id, hand, average_value)
                        VALUES (?, ?, ?, ?)
                    """, (test_instance_id, measurement_type_id, hand, avg))
                    result_set_id = cur.lastrowid
                    created_results += 1

                    for idx, val in enumerate(trials, start=1):
                        cur.execute("""
                            INSERT INTO trial_values
                            (result_set_id, trial_number, trial_value)
                            VALUES (?, ?, ?)
                        """, (result_set_id, idx, val))
                        created_trials += 1

    conn.commit()
    return {
        "pinch_test_id": pinch_test_id,
        "deleted_test_instances": deleted,
        "created_test_instances": created_instances,
        "created_result_sets": created_results,
        "created_trial_values": created_trials,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python regenerate_pinch_fake_data.py <database_path>")
        sys.exit(1)

    db_path = sys.argv[1]
    conn = connect(db_path)
    try:
        stats = repopulate_pinch_data(conn)
        print(f"Updated database: {db_path}")
        print(f"Pinch test type ID: {stats['pinch_test_id']}")
        print(f"Deleted old pinch test instances: {stats['deleted_test_instances']}")
        print(f"Created new pinch test instances: {stats['created_test_instances']}")
        print(f"Created new pinch result sets: {stats['created_result_sets']}")
        print(f"Created new pinch trial values: {stats['created_trial_values']}")
    finally:
        conn.close()


if __name__ == "__main__":
    random.seed(42)
    main()
