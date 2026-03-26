import argparse
import json
import sqlite3
import serial
import threading
import time


def connect_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def get_session(conn, session_id: int):
    cur = conn.cursor()
    cur.execute("SELECT session_id FROM sessions WHERE session_id = ?", (session_id,))
    return cur.fetchone()


def get_test_type_id(conn, test_name: str) -> int:
    cur = conn.cursor()
    cur.execute("SELECT test_type_id FROM test_types WHERE test_name = ?", (test_name,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"Test type not found: {test_name}")
    return row["test_type_id"]


def get_measurement_type_id(conn, test_type_id: int, measurement_name: str) -> int:
    cur = conn.cursor()
    cur.execute("""
        SELECT measurement_type_id
        FROM measurement_types
        WHERE test_type_id = ? AND measurement_name = ?
    """, (test_type_id, measurement_name))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"Measurement type not found: {measurement_name}")
    return row["measurement_type_id"]


def next_run_number(conn, session_id: int, test_type_id: int) -> int:
    cur = conn.cursor()
    cur.execute("""
        SELECT COALESCE(MAX(run_number), 0) + 1 AS next_run
        FROM test_instances
        WHERE session_id = ? AND test_type_id = ?
    """, (session_id, test_type_id))
    return cur.fetchone()["next_run"]


def insert_result_packet(conn, packet: dict):
    session_id = int(packet["session_id"])
    test_name = packet["test_name"]
    measurement_name = packet["measurement_name"]
    hand = packet["hand"]
    trials = [float(packet["trial1"]), float(packet["trial2"]), float(packet["trial3"])]
    average = float(packet["average"])

    if hand not in ("L", "R"):
        raise ValueError(f"Invalid hand: {hand}")

    if not get_session(conn, session_id):
        raise ValueError(f"Session does not exist: {session_id}")

    test_type_id = get_test_type_id(conn, test_name)
    measurement_type_id = get_measurement_type_id(conn, test_type_id, measurement_name)
    run_number = next_run_number(conn, session_id, test_type_id)

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO test_instances (
            session_id, test_type_id, run_number, started_at, completed_at, notes
        )
        VALUES (?, ?, ?, datetime('now'), datetime('now'), ?)
    """, (
        session_id,
        test_type_id,
        run_number,
        "Inserted from CHAD serial bridge"
    ))
    test_instance_id = cur.lastrowid

    cur.execute("""
        INSERT INTO result_sets (
            test_instance_id, measurement_type_id, hand, average_value
        )
        VALUES (?, ?, ?, ?)
    """, (
        test_instance_id,
        measurement_type_id,
        hand,
        average
    ))
    result_set_id = cur.lastrowid

    for i, value in enumerate(trials, start=1):
        cur.execute("""
            INSERT INTO trial_values (
                result_set_id, trial_number, trial_value
            )
            VALUES (?, ?, ?)
        """, (result_set_id, i, value))

    conn.commit()
    print(f"\nSaved -> session={session_id}, test='{test_name}', measurement='{measurement_name}', hand={hand}, avg={average:.2f}")


def serial_reader(ser, conn):
    while True:
        try:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            print(f"\nSERIAL: {line}")

            if line.startswith("{"):
                try:
                    packet = json.loads(line)
                    if packet.get("type") == "result":
                        insert_result_packet(conn, packet)
                except Exception as e:
                    print("Packet/database error:", e)

        except Exception as e:
            print("Serial read error:", e)
            break


def keyboard_writer(ser):
    print("\nType menu choices here and press Enter. Example: 1, 2, 3, x")
    while True:
        try:
            user_in = input("> ").strip()
            if user_in:
                ser.write((user_in + "\n").encode("utf-8"))
        except EOFError:
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            print("Keyboard write error:", e)
            break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True)
    parser.add_argument("--baud", type=int, default=9600)
    parser.add_argument("--db", required=True)
    parser.add_argument("--session", type=int, required=True)
    args = parser.parse_args()

    conn = connect_db(args.db)

    if not get_session(conn, args.session):
        raise ValueError(f"Session {args.session} does not exist in database.")

    ser = serial.Serial(args.port, args.baud, timeout=1)
    time.sleep(2)

    ser.write(f"SESSION,{args.session}\n".encode("utf-8"))

    print(f"Connected to CHAD on {args.port}")
    print(f"Active session set to {args.session}")
    print("Listening for results... Press Ctrl+C to stop.")

    reader = threading.Thread(target=serial_reader, args=(ser, conn), daemon=True)
    reader.start()

    try:
        keyboard_writer(ser)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            ser.write(b"CLEAR_SESSION\n")
        except Exception:
            pass
        ser.close()
        conn.close()
        print("\nStopped.")


if __name__ == "__main__":
    main()