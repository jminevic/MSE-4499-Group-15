
import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class ParticipantDialog(tk.Toplevel):
    def __init__(self, master, conn, participant_id=None):
        super().__init__(master)
        self.conn = conn
        self.participant_id = participant_id
        self.result = None
        self.title("Participant")
        self.geometry("520x460")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.name_var = tk.StringVar()
        ttk.Label(self, text="Full Name").pack(anchor="w", padx=12, pady=(12, 4))
        ttk.Entry(self, textvariable=self.name_var, width=50).pack(fill="x", padx=12)

        frame = ttk.LabelFrame(self, text="Football Positions", padding=10)
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        self.positions_list = tk.Listbox(frame, selectmode="multiple", height=14, exportselection=False)
        self.positions_list.pack(fill="both", expand=True)

        cur = self.conn.cursor()
        cur.execute("SELECT position_id, position_name FROM positions ORDER BY position_name")
        self.positions = cur.fetchall()
        for _, name in self.positions:
            self.positions_list.insert("end", name)

        if participant_id is not None:
            self._load_existing()

        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Button(btns, text="Save", command=self.save).pack(side="right", padx=4)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right")

    def _load_existing(self):
        cur = self.conn.cursor()
        cur.execute("SELECT full_name FROM participants WHERE participant_id = ?", (self.participant_id,))
        row = cur.fetchone()
        if row:
            self.name_var.set(row["full_name"])
        cur.execute("SELECT position_id FROM participant_positions WHERE participant_id = ?", (self.participant_id,))
        selected_ids = {r["position_id"] for r in cur.fetchall()}
        for idx, (pid, _) in enumerate(self.positions):
            if pid in selected_ids:
                self.positions_list.selection_set(idx)

    def save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Missing Data", "Full name is required.", parent=self)
            return
        chosen = [self.positions[i][0] for i in self.positions_list.curselection()]
        cur = self.conn.cursor()
        if self.participant_id is None:
            cur.execute("INSERT INTO participants (full_name) VALUES (?)", (name,))
            pid = cur.lastrowid
        else:
            pid = self.participant_id
            cur.execute("UPDATE participants SET full_name = ? WHERE participant_id = ?", (name, pid))
            cur.execute("DELETE FROM participant_positions WHERE participant_id = ?", (pid,))
        for pos_id in chosen:
            cur.execute("INSERT INTO participant_positions (participant_id, position_id) VALUES (?, ?)", (pid, pos_id))
        self.conn.commit()
        self.result = pid
        self.destroy()


class SessionDialog(tk.Toplevel):
    def __init__(self, master, conn, session_id=None, preset_participant_id=None):
        super().__init__(master)
        self.conn = conn
        self.session_id = session_id
        self.result = None
        self.title("Session")
        self.geometry("620x420")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.participant_var = tk.StringVar()
        self.datetime_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.weight_var = tk.StringVar()

        form = ttk.Frame(self, padding=12)
        form.pack(fill="both", expand=True)
        ttk.Label(form, text="Participant").grid(row=0, column=0, sticky="w", pady=4)
        self.participant_combo = ttk.Combobox(form, textvariable=self.participant_var, width=46, state="readonly")
        self.participant_combo.grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Label(form, text="Trial Datetime").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.datetime_var, width=48).grid(row=1, column=1, sticky="ew", pady=4)
        ttk.Label(form, text="Format: YYYY-MM-DD HH:MM:SS").grid(row=2, column=1, sticky="w")
        ttk.Label(form, text="Age at Test").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.age_var, width=18).grid(row=3, column=1, sticky="w", pady=4)
        ttk.Label(form, text="Height (cm)").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.height_var, width=18).grid(row=4, column=1, sticky="w", pady=4)
        ttk.Label(form, text="Weight (kg)").grid(row=5, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.weight_var, width=18).grid(row=5, column=1, sticky="w", pady=4)
        ttk.Label(form, text="Notes").grid(row=6, column=0, sticky="nw", pady=4)
        self.notes_text = tk.Text(form, width=48, height=8)
        self.notes_text.grid(row=6, column=1, sticky="ew", pady=4)
        form.columnconfigure(1, weight=1)

        cur = self.conn.cursor()
        cur.execute("SELECT participant_id, full_name FROM participants ORDER BY participant_id")
        self.participants = cur.fetchall()
        self.participant_combo["values"] = [f"{r['participant_id']} - {r['full_name']}" for r in self.participants]

        if session_id is not None:
            self._load_existing()
        elif preset_participant_id is not None:
            for idx, r in enumerate(self.participants):
                if r["participant_id"] == preset_participant_id:
                    self.participant_combo.current(idx)
                    break

        btns = ttk.Frame(self, padding=(12, 0, 12, 12))
        btns.pack(fill="x")
        ttk.Button(btns, text="Save", command=self.save).pack(side="right", padx=4)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right")

    def _load_existing(self):
        cur = self.conn.cursor()
        cur.execute("SELECT participant_id, trial_datetime, age_at_test, height_cm, weight_kg, notes FROM sessions WHERE session_id = ?", (self.session_id,))
        row = cur.fetchone()
        if not row:
            return
        for idx, p in enumerate(self.participants):
            if p["participant_id"] == row["participant_id"]:
                self.participant_combo.current(idx)
                break
        self.datetime_var.set(row["trial_datetime"] or "")
        self.age_var.set("" if row["age_at_test"] is None else str(row["age_at_test"]))
        self.height_var.set("" if row["height_cm"] is None else str(row["height_cm"]))
        self.weight_var.set("" if row["weight_kg"] is None else str(row["weight_kg"]))
        self.notes_text.insert("1.0", row["notes"] or "")

    def save(self):
        if not self.participant_combo.get().strip() or not self.datetime_var.get().strip():
            messagebox.showerror("Missing Data", "Participant and trial datetime are required.", parent=self)
            return
        participant_id = int(self.participant_combo.get().split(" - ", 1)[0])
        try:
            age = None if self.age_var.get().strip() == "" else int(self.age_var.get().strip())
            height = None if self.height_var.get().strip() == "" else float(self.height_var.get().strip())
            weight = None if self.weight_var.get().strip() == "" else float(self.weight_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Data", "Age must be an integer. Height and weight must be numeric.", parent=self)
            return
        notes = self.notes_text.get("1.0", "end").strip()
        cur = self.conn.cursor()
        if self.session_id is None:
            cur.execute(
                "INSERT INTO sessions (participant_id, trial_datetime, age_at_test, height_cm, weight_kg, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (participant_id, self.datetime_var.get().strip(), age, height, weight, notes)
            )
            self.result = cur.lastrowid
        else:
            cur.execute(
                "UPDATE sessions SET participant_id = ?, trial_datetime = ?, age_at_test = ?, height_cm = ?, weight_kg = ?, notes = ? WHERE session_id = ?",
                (participant_id, self.datetime_var.get().strip(), age, height, weight, notes, self.session_id)
            )
            self.result = self.session_id
        self.conn.commit()
        self.destroy()


class TestInstanceDialog(tk.Toplevel):
    def __init__(self, master, conn, test_instance_id=None, preset_session_id=None):
        super().__init__(master)
        self.conn = conn
        self.test_instance_id = test_instance_id
        self.result = None
        self.title("Test Instance")
        self.geometry("640x360")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.session_var = tk.StringVar()
        self.test_type_var = tk.StringVar()
        self.run_var = tk.StringVar(value="1")
        self.started_var = tk.StringVar()
        self.completed_var = tk.StringVar()

        form = ttk.Frame(self, padding=12)
        form.pack(fill="both", expand=True)
        ttk.Label(form, text="Session").grid(row=0, column=0, sticky="w", pady=4)
        self.session_combo = ttk.Combobox(form, textvariable=self.session_var, width=52, state="readonly")
        self.session_combo.grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Label(form, text="Test Type").grid(row=1, column=0, sticky="w", pady=4)
        self.test_combo = ttk.Combobox(form, textvariable=self.test_type_var, width=52, state="readonly")
        self.test_combo.grid(row=1, column=1, sticky="ew", pady=4)
        ttk.Label(form, text="Run Number").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.run_var, width=18).grid(row=2, column=1, sticky="w", pady=4)
        ttk.Label(form, text="Started At").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.started_var, width=38).grid(row=3, column=1, sticky="w", pady=4)
        ttk.Label(form, text="Completed At").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.completed_var, width=38).grid(row=4, column=1, sticky="w", pady=4)
        ttk.Label(form, text="Notes").grid(row=5, column=0, sticky="nw", pady=4)
        self.notes_text = tk.Text(form, width=52, height=8)
        self.notes_text.grid(row=5, column=1, sticky="ew", pady=4)
        form.columnconfigure(1, weight=1)

        cur = self.conn.cursor()
        cur.execute("SELECT s.session_id, s.participant_id, p.full_name, s.trial_datetime FROM sessions s JOIN participants p ON s.participant_id = p.participant_id ORDER BY s.trial_datetime DESC, s.session_id DESC")
        self.sessions = cur.fetchall()
        cur.execute("SELECT test_type_id, test_name FROM test_types ORDER BY test_name")
        self.tests = cur.fetchall()
        self.session_combo["values"] = [f"{r['session_id']} - P{r['participant_id']} - {r['full_name']} - {r['trial_datetime']}" for r in self.sessions]
        self.test_combo["values"] = [f"{r['test_type_id']} - {r['test_name']}" for r in self.tests]

        if test_instance_id is not None:
            self._load_existing()
        elif preset_session_id is not None:
            for idx, s in enumerate(self.sessions):
                if s["session_id"] == preset_session_id:
                    self.session_combo.current(idx)
                    break

        btns = ttk.Frame(self, padding=(12, 0, 12, 12))
        btns.pack(fill="x")
        ttk.Button(btns, text="Save", command=self.save).pack(side="right", padx=4)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right")

    def _load_existing(self):
        cur = self.conn.cursor()
        cur.execute("SELECT session_id, test_type_id, run_number, started_at, completed_at, notes FROM test_instances WHERE test_instance_id = ?", (self.test_instance_id,))
        row = cur.fetchone()
        if not row:
            return
        for idx, s in enumerate(self.sessions):
            if s["session_id"] == row["session_id"]:
                self.session_combo.current(idx)
                break
        for idx, t in enumerate(self.tests):
            if t["test_type_id"] == row["test_type_id"]:
                self.test_combo.current(idx)
                break
        self.run_var.set(str(row["run_number"]))
        self.started_var.set(row["started_at"] or "")
        self.completed_var.set(row["completed_at"] or "")
        self.notes_text.insert("1.0", row["notes"] or "")

    def save(self):
        if not self.session_combo.get().strip() or not self.test_combo.get().strip():
            messagebox.showerror("Missing Data", "Session and test type are required.", parent=self)
            return
        try:
            run_number = int(self.run_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Data", "Run number must be an integer.", parent=self)
            return
        session_id = int(self.session_combo.get().split(" - ", 1)[0])
        test_type_id = int(self.test_combo.get().split(" - ", 1)[0])
        started = self.started_var.get().strip() or None
        completed = self.completed_var.get().strip() or None
        notes = self.notes_text.get("1.0", "end").strip()
        cur = self.conn.cursor()
        if self.test_instance_id is None:
            cur.execute("INSERT INTO test_instances (session_id, test_type_id, run_number, started_at, completed_at, notes) VALUES (?, ?, ?, ?, ?, ?)",
                        (session_id, test_type_id, run_number, started, completed, notes))
            self.result = cur.lastrowid
        else:
            cur.execute("UPDATE test_instances SET session_id = ?, test_type_id = ?, run_number = ?, started_at = ?, completed_at = ?, notes = ? WHERE test_instance_id = ?",
                        (session_id, test_type_id, run_number, started, completed, notes, self.test_instance_id))
            self.result = self.test_instance_id
        self.conn.commit()
        self.destroy()


class ResultSetDialog(tk.Toplevel):
    def __init__(self, master, conn, result_set_id=None, preset_test_instance_id=None):
        super().__init__(master)
        self.conn = conn
        self.result_set_id = result_set_id
        self.result = None
        self.title("Result Set")
        self.geometry("640x320")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.test_instance_var = tk.StringVar()
        self.measurement_var = tk.StringVar()
        self.hand_var = tk.StringVar()
        self.avg_var = tk.StringVar()

        form = ttk.Frame(self, padding=12)
        form.pack(fill="both", expand=True)
        ttk.Label(form, text="Test Instance").grid(row=0, column=0, sticky="w", pady=4)
        self.test_instance_combo = ttk.Combobox(form, textvariable=self.test_instance_var, width=54, state="readonly")
        self.test_instance_combo.grid(row=0, column=1, sticky="ew", pady=4)
        self.test_instance_combo.bind("<<ComboboxSelected>>", self.on_test_instance_change)
        ttk.Label(form, text="Measurement Type").grid(row=1, column=0, sticky="w", pady=4)
        self.measurement_combo = ttk.Combobox(form, textvariable=self.measurement_var, width=54, state="readonly")
        self.measurement_combo.grid(row=1, column=1, sticky="ew", pady=4)
        ttk.Label(form, text="Hand").grid(row=2, column=0, sticky="w", pady=4)
        hand_combo = ttk.Combobox(form, textvariable=self.hand_var, width=12, state="readonly")
        hand_combo["values"] = ("L", "R")
        hand_combo.grid(row=2, column=1, sticky="w", pady=4)
        ttk.Label(form, text="Average Value").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.avg_var, width=18).grid(row=3, column=1, sticky="w", pady=4)
        form.columnconfigure(1, weight=1)

        cur = self.conn.cursor()
        cur.execute("SELECT ti.test_instance_id, ti.session_id, ti.run_number, tt.test_name, ti.test_type_id FROM test_instances ti JOIN test_types tt ON ti.test_type_id = tt.test_type_id ORDER BY ti.test_instance_id DESC")
        self.test_instances = cur.fetchall()
        self.test_instance_combo["values"] = [f"{r['test_instance_id']} - {r['test_name']} - Session {r['session_id']} - Run {r['run_number']}" for r in self.test_instances]
        self.measurements = []

        if result_set_id is not None:
            self._load_existing()
        elif preset_test_instance_id is not None:
            for idx, t in enumerate(self.test_instances):
                if t["test_instance_id"] == preset_test_instance_id:
                    self.test_instance_combo.current(idx)
                    self.on_test_instance_change()
                    break

        btns = ttk.Frame(self, padding=(12, 0, 12, 12))
        btns.pack(fill="x")
        ttk.Button(btns, text="Save", command=self.save).pack(side="right", padx=4)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right")

    def on_test_instance_change(self, event=None):
        if not self.test_instance_combo.get():
            return
        test_instance_id = int(self.test_instance_combo.get().split(" - ", 1)[0])
        cur = self.conn.cursor()
        test_type_id = None
        for row in self.test_instances:
            if row["test_instance_id"] == test_instance_id:
                test_type_id = row["test_type_id"]
                break
        cur.execute("SELECT measurement_type_id, measurement_name FROM measurement_types WHERE test_type_id = ? ORDER BY measurement_name", (test_type_id,))
        self.measurements = cur.fetchall()
        self.measurement_combo["values"] = [f"{r['measurement_type_id']} - {r['measurement_name']}" for r in self.measurements]
        if self.measurements:
            self.measurement_combo.current(0)

    def _load_existing(self):
        cur = self.conn.cursor()
        cur.execute("SELECT test_instance_id, measurement_type_id, hand, average_value FROM result_sets WHERE result_set_id = ?", (self.result_set_id,))
        row = cur.fetchone()
        if not row:
            return
        for idx, t in enumerate(self.test_instances):
            if t["test_instance_id"] == row["test_instance_id"]:
                self.test_instance_combo.current(idx)
                self.on_test_instance_change()
                break
        for idx, m in enumerate(self.measurements):
            if m["measurement_type_id"] == row["measurement_type_id"]:
                self.measurement_combo.current(idx)
                break
        self.hand_var.set(row["hand"])
        self.avg_var.set("" if row["average_value"] is None else str(row["average_value"]))

    def save(self):
        if not self.test_instance_combo.get().strip() or not self.measurement_combo.get().strip() or self.hand_var.get().strip() not in ("L", "R"):
            messagebox.showerror("Missing Data", "Test instance, measurement type, and hand are required.", parent=self)
            return
        try:
            avg = None if self.avg_var.get().strip() == "" else float(self.avg_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Data", "Average value must be numeric.", parent=self)
            return
        test_instance_id = int(self.test_instance_combo.get().split(" - ", 1)[0])
        measurement_type_id = int(self.measurement_combo.get().split(" - ", 1)[0])
        cur = self.conn.cursor()
        if self.result_set_id is None:
            cur.execute("INSERT INTO result_sets (test_instance_id, measurement_type_id, hand, average_value) VALUES (?, ?, ?, ?)",
                        (test_instance_id, measurement_type_id, self.hand_var.get().strip(), avg))
            self.result = cur.lastrowid
        else:
            cur.execute("UPDATE result_sets SET test_instance_id = ?, measurement_type_id = ?, hand = ?, average_value = ? WHERE result_set_id = ?",
                        (test_instance_id, measurement_type_id, self.hand_var.get().strip(), avg, self.result_set_id))
            self.result = self.result_set_id
        self.conn.commit()
        self.destroy()


class TrialDialog(tk.Toplevel):
    def __init__(self, master, conn, trial_value_id=None, preset_result_set_id=None):
        super().__init__(master)
        self.conn = conn
        self.trial_value_id = trial_value_id
        self.result = None
        self.title("Trial Value")
        self.geometry("580x260")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.result_set_var = tk.StringVar()
        self.trial_num_var = tk.StringVar()
        self.trial_val_var = tk.StringVar()

        form = ttk.Frame(self, padding=12)
        form.pack(fill="both", expand=True)
        ttk.Label(form, text="Result Set").grid(row=0, column=0, sticky="w", pady=4)
        self.result_combo = ttk.Combobox(form, textvariable=self.result_set_var, width=48, state="readonly")
        self.result_combo.grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Label(form, text="Trial Number").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.trial_num_var, width=18).grid(row=1, column=1, sticky="w", pady=4)
        ttk.Label(form, text="Trial Value").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.trial_val_var, width=18).grid(row=2, column=1, sticky="w", pady=4)
        form.columnconfigure(1, weight=1)

        cur = self.conn.cursor()
        cur.execute("""
            SELECT rs.result_set_id, p.full_name AS participant_name, mt.measurement_name, rs.hand
            FROM result_sets rs
            JOIN test_instances ti ON rs.test_instance_id = ti.test_instance_id
            JOIN sessions s ON ti.session_id = s.session_id
            JOIN participants p ON s.participant_id = p.participant_id
            JOIN measurement_types mt ON rs.measurement_type_id = mt.measurement_type_id
            ORDER BY rs.result_set_id DESC
        """)
        self.result_sets = cur.fetchall()
        self.result_combo["values"] = [f"{r['result_set_id']} - {r['participant_name']} - {r['measurement_name']} - {r['hand']}" for r in self.result_sets]

        if trial_value_id is not None:
            self._load_existing()
        elif preset_result_set_id is not None:
            for idx, r in enumerate(self.result_sets):
                if r["result_set_id"] == preset_result_set_id:
                    self.result_combo.current(idx)
                    break

        btns = ttk.Frame(self, padding=(12, 0, 12, 12))
        btns.pack(fill="x")
        ttk.Button(btns, text="Save", command=self.save).pack(side="right", padx=4)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right")

    def _load_existing(self):
        cur = self.conn.cursor()
        cur.execute("SELECT result_set_id, trial_number, trial_value FROM trial_values WHERE trial_value_id = ?", (self.trial_value_id,))
        row = cur.fetchone()
        if not row:
            return
        for idx, r in enumerate(self.result_sets):
            if r["result_set_id"] == row["result_set_id"]:
                self.result_combo.current(idx)
                break
        self.trial_num_var.set(str(row["trial_number"]))
        self.trial_val_var.set(str(row["trial_value"]))

    def save(self):
        if not self.result_combo.get().strip():
            messagebox.showerror("Missing Data", "Result set is required.", parent=self)
            return
        try:
            result_set_id = int(self.result_combo.get().split(" - ", 1)[0])
            trial_num = int(self.trial_num_var.get().strip())
            trial_val = float(self.trial_val_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Data", "Trial number must be an integer and trial value must be numeric.", parent=self)
            return
        cur = self.conn.cursor()
        try:
            if self.trial_value_id is None:
                cur.execute("INSERT INTO trial_values (result_set_id, trial_number, trial_value) VALUES (?, ?, ?)",
                            (result_set_id, trial_num, trial_val))
                self.result = cur.lastrowid
            else:
                cur.execute("UPDATE trial_values SET result_set_id = ?, trial_number = ?, trial_value = ? WHERE trial_value_id = ?",
                            (result_set_id, trial_num, trial_val, self.trial_value_id))
                self.result = self.trial_value_id
            self.conn.commit()
            self.destroy()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Constraint Error", str(e), parent=self)


class ChadDBUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CHAD - Wrist Testing Database")
        self.geometry("1480x920")
        self.minsize(1300, 820)
        self.conn = None
        self.db_path = tk.StringVar()
        self._build_topbar()
        self._build_notebook()
        self._auto_find_database()

    def _build_topbar(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Database File:").pack(side="left")
        ttk.Entry(top, textvariable=self.db_path, width=72).pack(side="left", padx=8, fill="x", expand=True)
        ttk.Button(top, text="Browse", command=self.browse_db).pack(side="left", padx=4)
        ttk.Button(top, text="Connect", command=self.connect_db).pack(side="left", padx=4)
        ttk.Button(top, text="Refresh All", command=self.refresh_all).pack(side="left", padx=4)
        ttk.Button(top, text="Quit", command=self.destroy).pack(side="right", padx=4)
        self.status_var = tk.StringVar(value="Choose a SQLite database file to begin.")
        ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x", side="bottom")

    def _build_notebook(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.overview_tab = ttk.Frame(self.nb, padding=12)
        self.participants_tab = ttk.Frame(self.nb, padding=12)
        self.sessions_tab = ttk.Frame(self.nb, padding=12)
        self.results_tab = ttk.Frame(self.nb, padding=12)
        self.nb.add(self.participants_tab, text="Participants")
        self.nb.add(self.sessions_tab, text="Sessions")
        self.nb.add(self.results_tab, text="Results Explorer")
        self.nb.add(self.overview_tab, text="Overview")
        self._build_overview_tab()
        self._build_participants_tab()
        self._build_sessions_tab()
        self._build_results_tab()

    def _build_overview_tab(self):
        summary_frame = ttk.LabelFrame(self.overview_tab, text="Database Summary", padding=12)
        summary_frame.pack(fill="x")
        self.summary_labels = {}
        fields = [("participants", "Participants"), ("positions", "Positions"), ("sessions", "Sessions"), ("test_instances", "Test Instances"), ("result_sets", "Result Sets"), ("trial_values", "Trial Values")]
        for i, (key, label) in enumerate(fields):
            box = ttk.Frame(summary_frame, padding=10)
            box.grid(row=0, column=i, padx=6, pady=6, sticky="nsew")
            summary_frame.columnconfigure(i, weight=1)
            ttk.Label(box, text=label, font=("Arial", 10, "bold")).pack()
            value = ttk.Label(box, text="—", font=("Arial", 18))
            value.pack(pady=(6, 0))
            self.summary_labels[key] = value
        schema_frame = ttk.LabelFrame(self.overview_tab, text="Tables in Database", padding=12)
        schema_frame.pack(fill="both", expand=True, pady=(12, 0))
        self.tables_tree = ttk.Treeview(schema_frame, columns=("name",), show="headings", height=12)
        self.tables_tree.heading("name", text="Table Name")
        self.tables_tree.column("name", width=300, anchor="w")
        self.tables_tree.pack(fill="both", expand=True)

    def _build_participants_tab(self):
        top = ttk.Frame(self.participants_tab)
        top.pack(fill="x")
        self.participant_search = tk.StringVar()
        ttk.Label(top, text="Search name or ID:").pack(side="left")
        ttk.Entry(top, textvariable=self.participant_search, width=35).pack(side="left", padx=6)
        ttk.Button(top, text="Search", command=self.load_participants).pack(side="left", padx=4)
        ttk.Button(top, text="Clear", command=self.clear_participant_search).pack(side="left", padx=4)
        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Button(top, text="Add Participant", command=self.add_participant).pack(side="left", padx=4)
        ttk.Button(top, text="Edit Selected", command=self.edit_participant).pack(side="left", padx=4)
        ttk.Button(top, text="Delete Selected", command=self.delete_participant).pack(side="left", padx=4)
        paned = ttk.Panedwindow(self.participants_tab, orient="horizontal")
        paned.pack(fill="both", expand=True, pady=(12, 0))
        left = ttk.Frame(paned)
        right = ttk.Frame(paned)
        paned.add(left, weight=3)
        paned.add(right, weight=2)
        self.participants_tree = ttk.Treeview(left, columns=("id", "name", "positions"), show="headings", height=24)
        for col, text, width in [("id", "Participant ID", 110), ("name", "Full Name", 220), ("positions", "Positions", 320)]:
            self.participants_tree.heading(col, text=text)
            self.participants_tree.column(col, width=width, anchor="w")
        self.participants_tree.pack(fill="both", expand=True)
        self.participants_tree.bind("<<TreeviewSelect>>", self.on_participant_select)
        right_top = ttk.LabelFrame(right, text="Participant Details", padding=10)
        right_top.pack(fill="x")
        self.participant_detail = tk.Text(right_top, height=8, wrap="word")
        self.participant_detail.pack(fill="x")
        self.participant_detail.configure(state="disabled")
        right_btns = ttk.Frame(right)
        right_btns.pack(fill="x", pady=(8, 0))
        ttk.Button(right_btns, text="Add Session for Selected Participant", command=self.add_session_from_participant).pack(side="left")
        right_bottom = ttk.LabelFrame(right, text="Sessions for Selected Participant", padding=10)
        right_bottom.pack(fill="both", expand=True, pady=(12, 0))
        self.participant_sessions_tree = ttk.Treeview(right_bottom, columns=("session_id", "trial_datetime", "age", "height", "weight"), show="headings", height=15)
        for col, text, width in [("session_id", "Session ID", 90), ("trial_datetime", "Trial Datetime", 170), ("age", "Age", 60), ("height", "Height (cm)", 100), ("weight", "Weight (kg)", 100)]:
            self.participant_sessions_tree.heading(col, text=text)
            self.participant_sessions_tree.column(col, width=width, anchor="w")
        self.participant_sessions_tree.pack(fill="both", expand=True)

    def _build_sessions_tab(self):
        top = ttk.Frame(self.sessions_tab)
        top.pack(fill="x")
        self.session_search = tk.StringVar()
        ttk.Label(top, text="Search participant / date / session ID:").pack(side="left")
        ttk.Entry(top, textvariable=self.session_search, width=40).pack(side="left", padx=6)
        ttk.Button(top, text="Search", command=self.load_sessions).pack(side="left", padx=4)
        ttk.Button(top, text="Clear", command=self.clear_session_search).pack(side="left", padx=4)
        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Button(top, text="Add Session", command=self.add_session).pack(side="left", padx=4)
        ttk.Button(top, text="Edit Selected Session", command=self.edit_session).pack(side="left", padx=4)
        ttk.Button(top, text="Delete Selected Session", command=self.delete_session).pack(side="left", padx=4)
        paned = ttk.Panedwindow(self.sessions_tab, orient="horizontal")
        paned.pack(fill="both", expand=True, pady=(12, 0))
        left = ttk.Frame(paned)
        right = ttk.Frame(paned)
        paned.add(left, weight=4)
        paned.add(right, weight=3)
        self.sessions_tree = ttk.Treeview(left, columns=("session_id", "participant_id", "name", "trial_datetime", "age", "height", "weight"), show="headings", height=25)
        for col, text, width in [("session_id", "Session ID", 90), ("participant_id", "Participant ID", 100), ("name", "Participant", 200), ("trial_datetime", "Trial Datetime", 170), ("age", "Age", 55), ("height", "Height", 70), ("weight", "Weight", 70)]:
            self.sessions_tree.heading(col, text=text)
            self.sessions_tree.column(col, width=width, anchor="w")
        self.sessions_tree.pack(fill="both", expand=True)
        self.sessions_tree.bind("<<TreeviewSelect>>", self.on_session_select)
        session_detail_frame = ttk.LabelFrame(right, text="Test Instances in Selected Session", padding=10)
        session_detail_frame.pack(fill="both", expand=True)
        test_btns = ttk.Frame(session_detail_frame)
        test_btns.pack(fill="x", pady=(0, 8))
        ttk.Button(test_btns, text="Add Test", command=self.add_test_instance).pack(side="left", padx=4)
        ttk.Button(test_btns, text="Edit Selected Test", command=self.edit_test_instance).pack(side="left", padx=4)
        ttk.Button(test_btns, text="Delete Selected Test", command=self.delete_test_instance).pack(side="left", padx=4)
        self.session_tests_tree = ttk.Treeview(session_detail_frame, columns=("test_instance_id", "test_name", "run_number", "started_at", "completed_at"), show="headings", height=18)
        for col, text, width in [("test_instance_id", "Test ID", 80), ("test_name", "Test Name", 200), ("run_number", "Run #", 60), ("started_at", "Started", 150), ("completed_at", "Completed", 150)]:
            self.session_tests_tree.heading(col, text=text)
            self.session_tests_tree.column(col, width=width, anchor="w")
        self.session_tests_tree.pack(fill="both", expand=True, pady=(0, 10))
        self.session_notes = tk.Text(session_detail_frame, height=7, wrap="word")
        self.session_notes.pack(fill="x")
        self.session_notes.configure(state="disabled")

    def _build_results_tab(self):
        filters = ttk.LabelFrame(self.results_tab, text="Filters", padding=10)
        filters.pack(fill="x")
        self.results_name = tk.StringVar()
        self.results_test = tk.StringVar()
        self.results_hand = tk.StringVar()
        ttk.Label(filters, text="Participant:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(filters, textvariable=self.results_name, width=26).grid(row=0, column=1, sticky="w", padx=4, pady=4)
        ttk.Label(filters, text="Test Type:").grid(row=0, column=2, sticky="w", padx=4, pady=4)
        self.results_test_combo = ttk.Combobox(filters, textvariable=self.results_test, width=28, state="readonly")
        self.results_test_combo.grid(row=0, column=3, sticky="w", padx=4, pady=4)
        ttk.Label(filters, text="Hand:").grid(row=0, column=4, sticky="w", padx=4, pady=4)
        self.results_hand_combo = ttk.Combobox(filters, textvariable=self.results_hand, width=8, state="readonly")
        self.results_hand_combo["values"] = ("", "L", "R")
        self.results_hand_combo.grid(row=0, column=5, sticky="w", padx=4, pady=4)
        ttk.Button(filters, text="Search", command=self.load_results).grid(row=0, column=6, padx=8)
        ttk.Button(filters, text="Clear", command=self.clear_results_filters).grid(row=0, column=7, padx=4)
        ttk.Separator(filters, orient="vertical").grid(row=0, column=8, sticky="ns", padx=8)
        ttk.Button(filters, text="Add Result Set", command=self.add_result_set).grid(row=0, column=9, padx=4)
        ttk.Button(filters, text="Edit Selected Result", command=self.edit_result_set).grid(row=0, column=10, padx=4)
        ttk.Button(filters, text="Delete Selected Result", command=self.delete_result_set).grid(row=0, column=11, padx=4)

        main = ttk.Panedwindow(self.results_tab, orient="vertical")
        main.pack(fill="both", expand=True, pady=(12, 0))
        top_frame = ttk.Frame(main)
        bottom_frame = ttk.LabelFrame(main, text="Trials for Selected Result Set", padding=10)
        main.add(top_frame, weight=4)
        main.add(bottom_frame, weight=2)

        self.results_tree = ttk.Treeview(top_frame, columns=("result_set_id", "test_instance_id", "participant_id", "name", "session_id", "datetime", "test_name", "run_number", "measurement_name", "hand", "average_value", "trials"), show="headings", height=20)
        headings = [("result_set_id", "Result ID", 70), ("test_instance_id", "Test ID", 60), ("participant_id", "PID", 55), ("name", "Participant", 150), ("session_id", "Session", 60), ("datetime", "Trial Datetime", 140), ("test_name", "Test Type", 170), ("run_number", "Run", 45), ("measurement_name", "Measurement", 180), ("hand", "Hand", 50), ("average_value", "Average", 80), ("trials", "Trials", 240)]
        for col, text, width in headings:
            self.results_tree.heading(col, text=text)
            self.results_tree.column(col, width=width, anchor="w")
        self.results_tree.pack(fill="both", expand=True)
        self.results_tree.bind("<<TreeviewSelect>>", self.on_result_select)

        trial_btns = ttk.Frame(bottom_frame)
        trial_btns.pack(fill="x", pady=(0, 8))
        ttk.Button(trial_btns, text="Add Trial", command=self.add_trial).pack(side="left", padx=4)
        ttk.Button(trial_btns, text="Edit Selected Trial", command=self.edit_trial).pack(side="left", padx=4)
        ttk.Button(trial_btns, text="Delete Selected Trial", command=self.delete_trial).pack(side="left", padx=4)
        ttk.Button(trial_btns, text="Recalculate Average", command=self.recalculate_average).pack(side="left", padx=16)

        self.trials_tree = ttk.Treeview(bottom_frame, columns=("trial_value_id", "result_set_id", "trial_number", "trial_value"), show="headings", height=8)
        for col, text, width in [("trial_value_id", "Trial ID", 80), ("result_set_id", "Result ID", 80), ("trial_number", "Trial #", 80), ("trial_value", "Trial Value", 120)]:
            self.trials_tree.heading(col, text=text)
            self.trials_tree.column(col, width=width, anchor="w")
        self.trials_tree.pack(fill="both", expand=True)

    def browse_db(self):
        path = filedialog.askopenfilename(title="Select SQLite Database", filetypes=[("SQLite Database", "*.db *.sqlite *.sqlite3"), ("All Files", "*.*")])
        if path:
            self.db_path.set(path)

    def _auto_find_database(self):
        from pathlib import Path
        candidates = [Path("chad_populated.db"), Path("chad.db"), Path("wrist_device_populated.db"), Path("wrist_device.db"), Path(__file__).with_name("chad_populated.db"), Path(__file__).with_name("chad.db"), Path(__file__).with_name("wrist_device_populated.db"), Path(__file__).with_name("wrist_device.db")]
        for candidate in candidates:
            if candidate.exists():
                self.db_path.set(str(candidate.resolve()))
                self.connect_db()
                return

    def connect_db(self):
        path = self.db_path.get().strip()
        if not path:
            messagebox.showwarning("No File Selected", "Please choose a database file.")
            return
        try:
            if self.conn:
                self.conn.close()
            self.conn = sqlite3.connect(path)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON;")
            self.status_var.set(f"Connected to: {path}")
            self.populate_test_filter()
            self.refresh_all()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def q(self, sql, params=()):
        if not self.conn:
            return []
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()

    def clear_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def set_text(self, widget, text):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def refresh_all(self):
        if not self.conn:
            return
        self.load_overview()
        self.load_participants()
        self.load_sessions()
        self.populate_test_filter()
        self.load_results()
        self.clear_tree(self.trials_tree)

    def load_overview(self):
        for table in ["participants", "positions", "sessions", "test_instances", "result_sets", "trial_values"]:
            row = self.q(f"SELECT COUNT(*) AS c FROM {table}")
            self.summary_labels[table].config(text=str(row[0]["c"] if row else 0))
        self.clear_tree(self.tables_tree)
        for row in self.q("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
            self.tables_tree.insert("", "end", values=(row["name"],))

    def load_participants(self):
        if not self.conn:
            return
        search = self.participant_search.get().strip()
        self.clear_tree(self.participants_tree)
        self.clear_tree(self.participant_sessions_tree)
        self.set_text(self.participant_detail, "")
        sql = "SELECT p.participant_id, p.full_name, COALESCE(GROUP_CONCAT(pos.position_name, ', '), '') AS positions FROM participants p LEFT JOIN participant_positions pp ON p.participant_id = pp.participant_id LEFT JOIN positions pos ON pp.position_id = pos.position_id"
        params = []
        if search:
            sql += " WHERE CAST(p.participant_id AS TEXT) LIKE ? OR p.full_name LIKE ?"
            params = [f"%{search}%", f"%{search}%"]
        sql += " GROUP BY p.participant_id, p.full_name ORDER BY p.participant_id"
        for row in self.q(sql, params):
            self.participants_tree.insert("", "end", values=(row["participant_id"], row["full_name"], row["positions"]))

    def load_sessions(self):
        if not self.conn:
            return
        search = self.session_search.get().strip()
        self.clear_tree(self.sessions_tree)
        self.clear_tree(self.session_tests_tree)
        self.set_text(self.session_notes, "")
        sql = "SELECT s.session_id, s.participant_id, p.full_name, s.trial_datetime, s.age_at_test, s.height_cm, s.weight_kg FROM sessions s JOIN participants p ON s.participant_id = p.participant_id"
        params = []
        if search:
            sql += " WHERE CAST(s.session_id AS TEXT) LIKE ? OR CAST(s.participant_id AS TEXT) LIKE ? OR p.full_name LIKE ? OR s.trial_datetime LIKE ?"
            params = [f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"]
        sql += " ORDER BY s.trial_datetime DESC, s.session_id DESC"
        for row in self.q(sql, params):
            self.sessions_tree.insert("", "end", values=(row["session_id"], row["participant_id"], row["full_name"], row["trial_datetime"], row["age_at_test"], row["height_cm"], row["weight_kg"]))

    def populate_test_filter(self):
        rows = self.q("SELECT test_name FROM test_types ORDER BY test_name")
        self.results_test_combo["values"] = [""] + [r["test_name"] for r in rows]
        self.results_hand_combo.set("")

    def load_results(self):
        if not self.conn:
            return
        name = self.results_name.get().strip()
        test_name = self.results_test.get().strip()
        hand = self.results_hand.get().strip()
        self.clear_tree(self.results_tree)
        sql = """
            SELECT rs.result_set_id, ti.test_instance_id, p.participant_id, p.full_name, s.session_id, s.trial_datetime,
                   tt.test_name, ti.run_number, mt.measurement_name, rs.hand, rs.average_value,
                   GROUP_CONCAT(tv.trial_number || ': ' || printf('%.2f', tv.trial_value), ' | ') AS trials
            FROM result_sets rs
            JOIN test_instances ti ON rs.test_instance_id = ti.test_instance_id
            JOIN sessions s ON ti.session_id = s.session_id
            JOIN participants p ON s.participant_id = p.participant_id
            JOIN test_types tt ON ti.test_type_id = tt.test_type_id
            JOIN measurement_types mt ON rs.measurement_type_id = mt.measurement_type_id
            LEFT JOIN trial_values tv ON rs.result_set_id = tv.result_set_id
            WHERE 1=1
        """
        params = []
        if name:
            sql += " AND (p.full_name LIKE ? OR CAST(p.participant_id AS TEXT) LIKE ?)"
            params += [f"%{name}%", f"%{name}%"]
        if test_name:
            sql += " AND tt.test_name = ?"
            params.append(test_name)
        if hand:
            sql += " AND rs.hand = ?"
            params.append(hand)
        sql += " GROUP BY rs.result_set_id, ti.test_instance_id, p.participant_id, p.full_name, s.session_id, s.trial_datetime, tt.test_name, ti.run_number, mt.measurement_name, rs.hand, rs.average_value ORDER BY s.trial_datetime DESC, p.participant_id, tt.test_name, ti.run_number, mt.measurement_name, rs.hand LIMIT 1000"
        for row in self.q(sql, params):
            avg = "" if row["average_value"] is None else f"{row['average_value']:.2f}"
            self.results_tree.insert("", "end", values=(row["result_set_id"], row["test_instance_id"], row["participant_id"], row["full_name"], row["session_id"], row["trial_datetime"], row["test_name"], row["run_number"], row["measurement_name"], row["hand"], avg, row["trials"] or ""))

    def load_trials_for_result(self, result_set_id):
        self.clear_tree(self.trials_tree)
        for row in self.q("SELECT trial_value_id, result_set_id, trial_number, trial_value FROM trial_values WHERE result_set_id = ? ORDER BY trial_number", (result_set_id,)):
            self.trials_tree.insert("", "end", values=(row["trial_value_id"], row["result_set_id"], row["trial_number"], row["trial_value"]))

    def on_participant_select(self, event=None):
        selected = self.participants_tree.selection()
        if not selected:
            return
        participant_id = self.participants_tree.item(selected[0], "values")[0]
        details = self.q("""
            SELECT p.participant_id, p.full_name, COALESCE(GROUP_CONCAT(pos.position_name, ', '), 'None listed') AS positions, COUNT(DISTINCT s.session_id) AS session_count
            FROM participants p
            LEFT JOIN participant_positions pp ON p.participant_id = pp.participant_id
            LEFT JOIN positions pos ON pp.position_id = pos.position_id
            LEFT JOIN sessions s ON p.participant_id = s.participant_id
            WHERE p.participant_id = ?
            GROUP BY p.participant_id, p.full_name
        """, (participant_id,))
        if details:
            d = details[0]
            self.set_text(self.participant_detail, f"Participant ID: {d['participant_id']}\nName: {d['full_name']}\nFootball Position(s): {d['positions']}\nNumber of Sessions: {d['session_count']}")
        self.clear_tree(self.participant_sessions_tree)
        for row in self.q("SELECT session_id, trial_datetime, age_at_test, height_cm, weight_kg FROM sessions WHERE participant_id = ? ORDER BY trial_datetime DESC", (participant_id,)):
            self.participant_sessions_tree.insert("", "end", values=(row["session_id"], row["trial_datetime"], row["age_at_test"], row["height_cm"], row["weight_kg"]))

    def on_session_select(self, event=None):
        selected = self.sessions_tree.selection()
        if not selected:
            return
        session_id = self.sessions_tree.item(selected[0], "values")[0]
        self.clear_tree(self.session_tests_tree)
        for row in self.q("SELECT ti.test_instance_id, tt.test_name, ti.run_number, ti.started_at, ti.completed_at FROM test_instances ti JOIN test_types tt ON ti.test_type_id = tt.test_type_id WHERE ti.session_id = ? ORDER BY tt.test_name, ti.run_number", (session_id,)):
            self.session_tests_tree.insert("", "end", values=(row["test_instance_id"], row["test_name"], row["run_number"], row["started_at"], row["completed_at"]))
        notes = self.q("SELECT p.full_name, s.notes, s.trial_datetime, s.age_at_test, s.height_cm, s.weight_kg FROM sessions s JOIN participants p ON s.participant_id = p.participant_id WHERE s.session_id = ?", (session_id,))
        if notes:
            n = notes[0]
            self.set_text(self.session_notes, f"Participant: {n['full_name']}\nTrial Datetime: {n['trial_datetime']}\nAge: {n['age_at_test']} | Height: {n['height_cm']} cm | Weight: {n['weight_kg']} kg\n\nSession Notes:\n{n['notes'] or 'No notes recorded.'}")

    def on_result_select(self, event=None):
        selected = self.results_tree.selection()
        if not selected:
            self.clear_tree(self.trials_tree)
            return
        result_set_id = self.results_tree.item(selected[0], "values")[0]
        self.load_trials_for_result(result_set_id)

    def add_participant(self):
        dlg = ParticipantDialog(self, self.conn)
        self.wait_window(dlg)
        if dlg.result:
            self.refresh_all()

    def edit_participant(self):
        selected = self.participants_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a participant first.")
            return
        participant_id = int(self.participants_tree.item(selected[0], "values")[0])
        dlg = ParticipantDialog(self, self.conn, participant_id=participant_id)
        self.wait_window(dlg)
        if dlg.result:
            self.refresh_all()

    def delete_participant(self):
        selected = self.participants_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a participant first.")
            return
        pid, name = self.participants_tree.item(selected[0], "values")[0:2]
        if messagebox.askyesno("Confirm Delete", f"Delete participant {pid} - {name}?\n\nThis will also delete related sessions, test instances, results, and trials."):
            self.conn.execute("DELETE FROM participants WHERE participant_id = ?", (pid,))
            self.conn.commit()
            self.refresh_all()

    def add_session_from_participant(self):
        selected = self.participants_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a participant first.")
            return
        participant_id = int(self.participants_tree.item(selected[0], "values")[0])
        dlg = SessionDialog(self, self.conn, preset_participant_id=participant_id)
        self.wait_window(dlg)
        if dlg.result:
            self.refresh_all()

    def add_session(self):
        dlg = SessionDialog(self, self.conn)
        self.wait_window(dlg)
        if dlg.result:
            self.refresh_all()

    def edit_session(self):
        selected = self.sessions_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a session first.")
            return
        session_id = int(self.sessions_tree.item(selected[0], "values")[0])
        dlg = SessionDialog(self, self.conn, session_id=session_id)
        self.wait_window(dlg)
        if dlg.result:
            self.refresh_all()

    def delete_session(self):
        selected = self.sessions_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a session first.")
            return
        session_id = int(self.sessions_tree.item(selected[0], "values")[0])
        if messagebox.askyesno("Confirm Delete", f"Delete session {session_id}?\n\nThis will also delete related test instances, results, and trials."):
            self.conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            self.conn.commit()
            self.refresh_all()

    def add_test_instance(self):
        selected = self.sessions_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a session first.")
            return
        session_id = int(self.sessions_tree.item(selected[0], "values")[0])
        dlg = TestInstanceDialog(self, self.conn, preset_session_id=session_id)
        self.wait_window(dlg)
        if dlg.result:
            self.refresh_all()

    def edit_test_instance(self):
        selected = self.session_tests_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a test instance first.")
            return
        test_instance_id = int(self.session_tests_tree.item(selected[0], "values")[0])
        dlg = TestInstanceDialog(self, self.conn, test_instance_id=test_instance_id)
        self.wait_window(dlg)
        if dlg.result:
            self.refresh_all()

    def delete_test_instance(self):
        selected = self.session_tests_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a test instance first.")
            return
        test_instance_id = int(self.session_tests_tree.item(selected[0], "values")[0])
        if messagebox.askyesno("Confirm Delete", f"Delete test instance {test_instance_id}?\n\nThis will also delete related result sets and trial values."):
            self.conn.execute("DELETE FROM test_instances WHERE test_instance_id = ?", (test_instance_id,))
            self.conn.commit()
            self.refresh_all()

    def add_result_set(self):
        preset_test_instance_id = None
        sel_test = self.session_tests_tree.selection()
        if sel_test:
            preset_test_instance_id = int(self.session_tests_tree.item(sel_test[0], "values")[0])
        dlg = ResultSetDialog(self, self.conn, preset_test_instance_id=preset_test_instance_id)
        self.wait_window(dlg)
        if dlg.result:
            self.refresh_all()

    def edit_result_set(self):
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a result set first.")
            return
        result_set_id = int(self.results_tree.item(selected[0], "values")[0])
        dlg = ResultSetDialog(self, self.conn, result_set_id=result_set_id)
        self.wait_window(dlg)
        if dlg.result:
            self.refresh_all()

    def delete_result_set(self):
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a result set first.")
            return
        result_set_id = int(self.results_tree.item(selected[0], "values")[0])
        if messagebox.askyesno("Confirm Delete", f"Delete result set {result_set_id}?\n\nThis will also delete related trial values."):
            self.conn.execute("DELETE FROM result_sets WHERE result_set_id = ?", (result_set_id,))
            self.conn.commit()
            self.refresh_all()

    def add_trial(self):
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a result set first.")
            return
        result_set_id = int(self.results_tree.item(selected[0], "values")[0])
        dlg = TrialDialog(self, self.conn, preset_result_set_id=result_set_id)
        self.wait_window(dlg)
        if dlg.result:
            self.refresh_all()
            self.load_trials_for_result(result_set_id)

    def edit_trial(self):
        selected = self.trials_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a trial first.")
            return
        trial_value_id = int(self.trials_tree.item(selected[0], "values")[0])
        result_set_id = int(self.trials_tree.item(selected[0], "values")[1])
        dlg = TrialDialog(self, self.conn, trial_value_id=trial_value_id)
        self.wait_window(dlg)
        if dlg.result:
            self.refresh_all()
            self.load_trials_for_result(result_set_id)

    def delete_trial(self):
        selected = self.trials_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a trial first.")
            return
        trial_value_id, result_set_id = self.trials_tree.item(selected[0], "values")[0:2]
        if messagebox.askyesno("Confirm Delete", f"Delete trial value {trial_value_id}?"):
            self.conn.execute("DELETE FROM trial_values WHERE trial_value_id = ?", (trial_value_id,))
            self.conn.commit()
            self.refresh_all()
            self.load_trials_for_result(result_set_id)

    def recalculate_average(self):
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a result set first.")
            return
        result_set_id = int(self.results_tree.item(selected[0], "values")[0])
        rows = self.q("SELECT AVG(trial_value) AS avg_val FROM trial_values WHERE result_set_id = ?", (result_set_id,))
        avg_val = rows[0]["avg_val"] if rows else None
        self.conn.execute("UPDATE result_sets SET average_value = ? WHERE result_set_id = ?", (avg_val, result_set_id))
        self.conn.commit()
        self.refresh_all()
        self.load_trials_for_result(result_set_id)
        messagebox.showinfo("Average Updated", f"Average recalculated for result set {result_set_id}.")

    def clear_participant_search(self):
        self.participant_search.set("")
        self.load_participants()

    def clear_session_search(self):
        self.session_search.set("")
        self.load_sessions()

    def clear_results_filters(self):
        self.results_name.set("")
        self.results_test.set("")
        self.results_hand.set("")
        self.load_results()
        self.clear_tree(self.trials_tree)


if __name__ == "__main__":
    app = ChadDBUI()
    app.mainloop()
