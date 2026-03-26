
import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path


class ChadDBUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CHAD - Wrist Testing Database")
        self.geometry("1380x860")
        self.minsize(1200, 760)

        self.conn = None
        self.db_path = tk.StringVar()

        self._build_topbar()
        self._build_notebook()
        self._auto_find_database()

    # ---------- UI BUILD ----------
    def _build_topbar(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Database File:").pack(side="left")
        self.db_entry = ttk.Entry(top, textvariable=self.db_path, width=70)
        self.db_entry.pack(side="left", padx=(8, 8), fill="x", expand=True)

        ttk.Button(top, text="Browse", command=self.browse_db).pack(side="left", padx=4)
        ttk.Button(top, text="Connect", command=self.connect_db).pack(side="left", padx=4)
        ttk.Button(top, text="Refresh All", command=self.refresh_all).pack(side="left", padx=4)

        self.status_var = tk.StringVar(value="Choose a SQLite database file to begin.")
        ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x", side="bottom")

    def _build_notebook(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.overview_tab = ttk.Frame(self.nb, padding=12)
        self.participants_tab = ttk.Frame(self.nb, padding=12)
        self.sessions_tab = ttk.Frame(self.nb, padding=12)
        self.results_tab = ttk.Frame(self.nb, padding=12)

        self.nb.add(self.overview_tab, text="Overview")
        self.nb.add(self.participants_tab, text="Participants")
        self.nb.add(self.sessions_tab, text="Sessions")
        self.nb.add(self.results_tab, text="Results Explorer")

        self._build_overview_tab()
        self._build_participants_tab()
        self._build_sessions_tab()
        self._build_results_tab()

    def _build_overview_tab(self):
        summary_frame = ttk.LabelFrame(self.overview_tab, text="Database Summary", padding=12)
        summary_frame.pack(fill="x")

        self.summary_labels = {}
        fields = [
            ("participants", "Participants"),
            ("positions", "Positions"),
            ("sessions", "Sessions"),
            ("test_instances", "Test Instances"),
            ("result_sets", "Result Sets"),
            ("trial_values", "Trial Values"),
        ]

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

        paned = ttk.Panedwindow(self.participants_tab, orient="horizontal")
        paned.pack(fill="both", expand=True, pady=(12, 0))

        left = ttk.Frame(paned)
        right = ttk.Frame(paned)
        paned.add(left, weight=3)
        paned.add(right, weight=2)

        self.participants_tree = ttk.Treeview(
            left,
            columns=("id", "name", "positions"),
            show="headings",
            height=24
        )
        for col, text, width in [
            ("id", "Participant ID", 110),
            ("name", "Full Name", 220),
            ("positions", "Positions", 320),
        ]:
            self.participants_tree.heading(col, text=text)
            self.participants_tree.column(col, width=width, anchor="w")
        self.participants_tree.pack(fill="both", expand=True)
        self.participants_tree.bind("<<TreeviewSelect>>", self.on_participant_select)

        right_top = ttk.LabelFrame(right, text="Participant Details", padding=10)
        right_top.pack(fill="x")

        self.participant_detail = tk.Text(right_top, height=8, wrap="word")
        self.participant_detail.pack(fill="x")
        self.participant_detail.configure(state="disabled")

        right_bottom = ttk.LabelFrame(right, text="Sessions for Selected Participant", padding=10)
        right_bottom.pack(fill="both", expand=True, pady=(12, 0))

        self.participant_sessions_tree = ttk.Treeview(
            right_bottom,
            columns=("session_id", "trial_datetime", "age", "height", "weight"),
            show="headings",
            height=15
        )
        for col, text, width in [
            ("session_id", "Session ID", 90),
            ("trial_datetime", "Trial Datetime", 170),
            ("age", "Age", 60),
            ("height", "Height (cm)", 100),
            ("weight", "Weight (kg)", 100),
        ]:
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

        paned = ttk.Panedwindow(self.sessions_tab, orient="horizontal")
        paned.pack(fill="both", expand=True, pady=(12, 0))

        left = ttk.Frame(paned)
        right = ttk.Frame(paned)
        paned.add(left, weight=4)
        paned.add(right, weight=3)

        self.sessions_tree = ttk.Treeview(
            left,
            columns=("session_id", "participant_id", "name", "trial_datetime", "age", "height", "weight"),
            show="headings",
            height=25
        )
        for col, text, width in [
            ("session_id", "Session ID", 90),
            ("participant_id", "Participant ID", 100),
            ("name", "Participant", 200),
            ("trial_datetime", "Trial Datetime", 170),
            ("age", "Age", 55),
            ("height", "Height", 70),
            ("weight", "Weight", 70),
        ]:
            self.sessions_tree.heading(col, text=text)
            self.sessions_tree.column(col, width=width, anchor="w")
        self.sessions_tree.pack(fill="both", expand=True)
        self.sessions_tree.bind("<<TreeviewSelect>>", self.on_session_select)

        session_detail_frame = ttk.LabelFrame(right, text="Test Instances in Selected Session", padding=10)
        session_detail_frame.pack(fill="both", expand=True)

        self.session_tests_tree = ttk.Treeview(
            session_detail_frame,
            columns=("test_instance_id", "test_name", "run_number", "started_at", "completed_at"),
            show="headings",
            height=18
        )
        for col, text, width in [
            ("test_instance_id", "Test ID", 80),
            ("test_name", "Test Name", 200),
            ("run_number", "Run #", 60),
            ("started_at", "Started", 150),
            ("completed_at", "Completed", 150),
        ]:
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

        results_frame = ttk.Frame(self.results_tab)
        results_frame.pack(fill="both", expand=True, pady=(12, 0))

        self.results_tree = ttk.Treeview(
            results_frame,
            columns=(
                "participant_id", "name", "session_id", "datetime", "test_name", "run_number",
                "measurement_name", "hand", "average_value", "trials"
            ),
            show="headings",
            height=25
        )
        headings = [
            ("participant_id", "PID", 55),
            ("name", "Participant", 170),
            ("session_id", "Session", 70),
            ("datetime", "Trial Datetime", 145),
            ("test_name", "Test Type", 180),
            ("run_number", "Run", 45),
            ("measurement_name", "Measurement", 200),
            ("hand", "Hand", 50),
            ("average_value", "Average", 80),
            ("trials", "Trials", 260),
        ]
        for col, text, width in headings:
            self.results_tree.heading(col, text=text)
            self.results_tree.column(col, width=width, anchor="w")
        self.results_tree.pack(fill="both", expand=True)

    # ---------- DATABASE ----------
    def browse_db(self):
        path = filedialog.askopenfilename(
            title="Select SQLite Database",
            filetypes=[("SQLite Database", "*.db *.sqlite *.sqlite3"), ("All Files", "*.*")]
        )
        if path:
            self.db_path.set(path)

    def _auto_find_database(self):
        candidates = [
            Path("chad_populated.db"),
            Path("chad.db"),
            Path(__file__).with_name("chad_populated.db"),
            Path(__file__).with_name("chad.db"),
        ]
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
        if not Path(path).exists():
            messagebox.showerror("File Not Found", f"Could not find:\n{path}")
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

    # ---------- HELPERS ----------
    def clear_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def set_text(self, widget, text):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    # ---------- LOADERS ----------
    def refresh_all(self):
        if not self.conn:
            return
        self.load_overview()
        self.load_participants()
        self.load_sessions()
        self.load_results()

    def load_overview(self):
        counts = {}
        for table in ["participants", "positions", "sessions", "test_instances", "result_sets", "trial_values"]:
            row = self.q(f"SELECT COUNT(*) AS c FROM {table}")
            counts[table] = row[0]["c"] if row else 0

        for key, label in self.summary_labels.items():
            label.config(text=str(counts.get(key, 0)))

        self.clear_tree(self.tables_tree)
        tables = self.q("""
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        for row in tables:
            self.tables_tree.insert("", "end", values=(row["name"],))

    def load_participants(self):
        if not self.conn:
            return

        search = self.participant_search.get().strip()
        self.clear_tree(self.participants_tree)
        self.clear_tree(self.participant_sessions_tree)
        self.set_text(self.participant_detail, "")

        sql = """
            SELECT
                p.participant_id,
                p.full_name,
                COALESCE(GROUP_CONCAT(pos.position_name, ', '), '') AS positions
            FROM participants p
            LEFT JOIN participant_positions pp ON p.participant_id = pp.participant_id
            LEFT JOIN positions pos ON pp.position_id = pos.position_id
        """
        params = []
        if search:
            sql += " WHERE CAST(p.participant_id AS TEXT) LIKE ? OR p.full_name LIKE ? "
            params.extend([f"%{search}%", f"%{search}%"])
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

        sql = """
            SELECT
                s.session_id,
                s.participant_id,
                p.full_name,
                s.trial_datetime,
                s.age_at_test,
                s.height_cm,
                s.weight_kg,
                COALESCE(s.notes, '') AS notes
            FROM sessions s
            JOIN participants p ON s.participant_id = p.participant_id
        """
        params = []
        if search:
            sql += """
                WHERE CAST(s.session_id AS TEXT) LIKE ?
                   OR CAST(s.participant_id AS TEXT) LIKE ?
                   OR p.full_name LIKE ?
                   OR s.trial_datetime LIKE ?
            """
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])
        sql += " ORDER BY s.trial_datetime DESC, s.session_id DESC"

        for row in self.q(sql, params):
            self.sessions_tree.insert("", "end", values=(
                row["session_id"], row["participant_id"], row["full_name"], row["trial_datetime"],
                row["age_at_test"], row["height_cm"], row["weight_kg"]
            ))

    def populate_test_filter(self):
        rows = self.q("SELECT test_name FROM test_types ORDER BY test_name")
        values = [""] + [r["test_name"] for r in rows]
        self.results_test_combo["values"] = values
        self.results_hand_combo.set("")

    def load_results(self):
        if not self.conn:
            return

        name = self.results_name.get().strip()
        test_name = self.results_test.get().strip()
        hand = self.results_hand.get().strip()

        self.clear_tree(self.results_tree)

        sql = """
            SELECT
                p.participant_id,
                p.full_name,
                s.session_id,
                s.trial_datetime,
                tt.test_name,
                ti.run_number,
                mt.measurement_name,
                rs.hand,
                rs.average_value,
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
            sql += " AND (p.full_name LIKE ? OR CAST(p.participant_id AS TEXT) LIKE ?) "
            params.extend([f"%{name}%", f"%{name}%"])
        if test_name:
            sql += " AND tt.test_name = ? "
            params.append(test_name)
        if hand:
            sql += " AND rs.hand = ? "
            params.append(hand)

        sql += """
            GROUP BY
                p.participant_id, p.full_name, s.session_id, s.trial_datetime,
                tt.test_name, ti.run_number, mt.measurement_name, rs.hand, rs.average_value, rs.result_set_id
            ORDER BY s.trial_datetime DESC, p.participant_id, tt.test_name, ti.run_number, mt.measurement_name, rs.hand
            LIMIT 1000
        """

        for row in self.q(sql, params):
            avg = "" if row["average_value"] is None else f'{row["average_value"]:.2f}'
            self.results_tree.insert("", "end", values=(
                row["participant_id"], row["full_name"], row["session_id"], row["trial_datetime"],
                row["test_name"], row["run_number"], row["measurement_name"], row["hand"], avg, row["trials"] or ""
            ))

    # ---------- EVENTS ----------
    def on_participant_select(self, event=None):
        selected = self.participants_tree.selection()
        if not selected:
            return
        item = self.participants_tree.item(selected[0], "values")
        participant_id = item[0]

        details = self.q("""
            SELECT
                p.participant_id,
                p.full_name,
                COALESCE(GROUP_CONCAT(pos.position_name, ', '), 'None listed') AS positions,
                COUNT(DISTINCT s.session_id) AS session_count
            FROM participants p
            LEFT JOIN participant_positions pp ON p.participant_id = pp.participant_id
            LEFT JOIN positions pos ON pp.position_id = pos.position_id
            LEFT JOIN sessions s ON p.participant_id = s.participant_id
            WHERE p.participant_id = ?
            GROUP BY p.participant_id, p.full_name
        """, (participant_id,))

        if details:
            d = details[0]
            txt = (
                f"Participant ID: {d['participant_id']}\n"
                f"Name: {d['full_name']}\n"
                f"Football Position(s): {d['positions']}\n"
                f"Number of Sessions: {d['session_count']}"
            )
            self.set_text(self.participant_detail, txt)

        self.clear_tree(self.participant_sessions_tree)
        rows = self.q("""
            SELECT session_id, trial_datetime, age_at_test, height_cm, weight_kg
            FROM sessions
            WHERE participant_id = ?
            ORDER BY trial_datetime DESC
        """, (participant_id,))
        for row in rows:
            self.participant_sessions_tree.insert("", "end", values=(
                row["session_id"], row["trial_datetime"], row["age_at_test"], row["height_cm"], row["weight_kg"]
            ))

    def on_session_select(self, event=None):
        selected = self.sessions_tree.selection()
        if not selected:
            return
        item = self.sessions_tree.item(selected[0], "values")
        session_id = item[0]

        self.clear_tree(self.session_tests_tree)
        tests = self.q("""
            SELECT
                ti.test_instance_id,
                tt.test_name,
                ti.run_number,
                ti.started_at,
                ti.completed_at
            FROM test_instances ti
            JOIN test_types tt ON ti.test_type_id = tt.test_type_id
            WHERE ti.session_id = ?
            ORDER BY tt.test_name, ti.run_number
        """, (session_id,))
        for row in tests:
            self.session_tests_tree.insert("", "end", values=(
                row["test_instance_id"], row["test_name"], row["run_number"], row["started_at"], row["completed_at"]
            ))

        notes = self.q("""
            SELECT
                p.full_name,
                s.notes,
                s.trial_datetime,
                s.age_at_test,
                s.height_cm,
                s.weight_kg
            FROM sessions s
            JOIN participants p ON s.participant_id = p.participant_id
            WHERE s.session_id = ?
        """, (session_id,))
        if notes:
            n = notes[0]
            text = (
                f"Participant: {n['full_name']}\n"
                f"Trial Datetime: {n['trial_datetime']}\n"
                f"Age: {n['age_at_test']} | Height: {n['height_cm']} cm | Weight: {n['weight_kg']} kg\n\n"
                f"Session Notes:\n{n['notes'] or 'No notes recorded.'}"
            )
            self.set_text(self.session_notes, text)

    # ---------- CLEAR FILTERS ----------
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


if __name__ == "__main__":
    app = ChadDBUI()
    app.mainloop()
