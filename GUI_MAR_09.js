import React, { useMemo, useState } from "react";

const proceduralSequence = [
  { test: "Flexion / Extension", hand: "Left", direction: "Down" },
  { test: "Flexion / Extension", hand: "Left", direction: "Up" },
  { test: "Flexion / Extension", hand: "Right", direction: "Down" },
  { test: "Flexion / Extension", hand: "Right", direction: "Up" },

  { test: "Radial / Ulnar Deviation", hand: "Left", direction: "Clockwise" },
  { test: "Radial / Ulnar Deviation", hand: "Left", direction: "Counterclockwise" },
  { test: "Radial / Ulnar Deviation", hand: "Right", direction: "Clockwise" },
  { test: "Radial / Ulnar Deviation", hand: "Right", direction: "Counterclockwise" },

  { test: "Pinch Testing", hand: "Left", pattern: "Index to Thumb" },
  { test: "Pinch Testing", hand: "Left", pattern: "Middle to Thumb" },
  { test: "Pinch Testing", hand: "Left", pattern: "Ring to Thumb" },
  { test: "Pinch Testing", hand: "Left", pattern: "Pinky to Thumb" },
  { test: "Pinch Testing", hand: "Left", pattern: "Thumb Press" },

  { test: "Pinch Testing", hand: "Right", pattern: "Index to Thumb" },
  { test: "Pinch Testing", hand: "Right", pattern: "Middle to Thumb" },
  { test: "Pinch Testing", hand: "Right", pattern: "Ring to Thumb" },
  { test: "Pinch Testing", hand: "Right", pattern: "Pinky to Thumb" },
  { test: "Pinch Testing", hand: "Right", pattern: "Thumb Press" },

  { test: "Pronation / Supination", hand: "Left", subtype: "Torque Test" },
  { test: "Pronation / Supination", hand: "Right", subtype: "Torque Test" },
  { test: "Pronation / Supination", hand: "Left", subtype: "Angle Achieved Test" },
  { test: "Pronation / Supination", hand: "Right", subtype: "Angle Achieved Test" },
];

const initialDatabases = [
  {
    id: "db-001",
    name: "Western Football 2026",
    createdAt: "2026-03-01",
    athletes: [
      { id: "FB-014", name: "Jordan Lee", age: 21, sport: "Football", dominantHand: "Right" },
      { id: "FB-021", name: "Avery Smith", age: 19, sport: "Football", dominantHand: "Left" },
      { id: "FB-033", name: "Cameron Patel", age: 23, sport: "Football", dominantHand: "Right" },
    ],
    sessions: [
      {
        id: "S-1001",
        athleteId: "FB-014",
        date: "2026-03-09",
        summary: "Completed full wrist assessment",
        notes: "ROM normal, pinch stable.",
      },
      {
        id: "S-1002",
        athleteId: "FB-021",
        date: "2026-03-08",
        summary: "Completed full wrist assessment",
        notes: "Pinch slightly reduced on left side.",
      },
    ],
  },
  {
    id: "db-002",
    name: "Clinic Demo Set",
    createdAt: "2026-02-15",
    athletes: [
      { id: "CL-010", name: "Taylor Brooks", age: 24, sport: "Football", dominantHand: "Right" },
      { id: "CL-011", name: "Morgan Cruz", age: 20, sport: "Football", dominantHand: "Left" },
    ],
    sessions: [
      {
        id: "S-2001",
        athleteId: "CL-010",
        date: "2026-02-22",
        summary: "Demo procedural run",
        notes: "Test dataset only.",
      },
    ],
  },
];

function getSequenceLabel(step) {
  if (step.pattern) return `${step.hand} • ${step.pattern}`;
  if (step.subtype) return `${step.hand} • ${step.subtype}`;
  if (step.direction) return `${step.hand} • ${step.direction}`;
  return step.hand;
}

function getTodayString() {
  return new Date().toISOString().slice(0, 10);
}

function getTheme(theme) {
  return theme === "dark"
    ? {
        bg: "#020617",
        panel: "#0f172a",
        panelSoft: "#111827",
        text: "#e5e7eb",
        subtext: "#94a3b8",
        border: "#334155",
        primary: "#e5e7eb",
        primaryText: "#020617",
        secondary: "#1e293b",
        secondaryText: "#e5e7eb",
        outlineBg: "#0f172a",
        outlineText: "#e5e7eb",
        nav: "#000814",
        navActive: "#1e293b",
        inputBg: "#0f172a",
        tagBg: "#1e293b",
        tagText: "#cbd5e1",
        successBg: "#052e16",
        successBorder: "#166534",
        currentBg: "#172554",
        currentBorder: "#1d4ed8",
      }
    : {
        bg: "#f1f5f9",
        panel: "#ffffff",
        panelSoft: "#f8fafc",
        text: "#0f172a",
        subtext: "#64748b",
        border: "#cbd5e1",
        primary: "#0f172a",
        primaryText: "#ffffff",
        secondary: "#e2e8f0",
        secondaryText: "#0f172a",
        outlineBg: "#ffffff",
        outlineText: "#0f172a",
        nav: "#020617",
        navActive: "#1e293b",
        inputBg: "#ffffff",
        tagBg: "#e2e8f0",
        tagText: "#334155",
        successBg: "#f0fdf4",
        successBorder: "#bbf7d0",
        currentBg: "#eff6ff",
        currentBorder: "#93c5fd",
      };
}

function Panel({ title, subtitle, children, s }) {
  return (
    <div style={s.card}>
      {title && <h3 style={{ marginTop: 0, marginBottom: 8 }}>{title}</h3>}
      {subtitle && <p style={s.subtext}>{subtitle}</p>}
      {children}
    </div>
  );
}

function Sidebar({ page, setPage, s }) {
  const items = ["dashboard", "database", "assessment", "history", "settings"];

  return (
    <div style={s.sidebar}>
      <h2 style={{ margin: 0 }}>Wrist Assess</h2>
      <p style={s.sidebarSub}>Clinical testing prototype</p>

      <div style={{ marginTop: 20 }}>
        {items.map((item) => (
          <button
            key={item}
            onClick={() => setPage(item)}
            style={{
              ...s.sideButton,
              background: page === item ? s.c.navActive : "transparent",
            }}
          >
            {item === "dashboard" && "Dashboard"}
            {item === "database" && "Database"}
            {item === "assessment" && "Assessment"}
            {item === "history" && "History"}
            {item === "settings" && "Settings"}
          </button>
        ))}
      </div>
    </div>
  );
}

function Dashboard({
  setPage,
  selectedAthlete,
  selectedDatabase,
  totalAthletes,
  theme,
  s,
}) {
  return (
    <div>
      <h1>Dashboard</h1>
      <p style={s.subtext}>Wrist medical assessment workflow for athletes and patients.</p>

      <div style={s.grid4}>
        <div style={s.card}><b>Device</b><p>Connected</p></div>
        <div style={s.card}><b>Recent Database</b><p>{selectedDatabase?.name || "None selected"}</p></div>
        <div style={s.card}><b>Current Athlete</b><p>{selectedAthlete?.name || "None selected"}</p></div>
        <div style={s.card}><b>Theme</b><p>{theme === "dark" ? "Dark" : "Light"} Mode</p></div>
      </div>

      <div style={s.grid2}>
        <Panel title="Start" s={s}>
          <div style={s.buttonRow}>
            <button style={s.primaryButton} onClick={() => setPage("database")}>Open Database</button>
            <button style={s.secondaryButton} onClick={() => setPage("assessment")}>Start Assessment</button>
          </div>
        </Panel>

        <Panel title="Quick Info" s={s}>
          <div style={s.statusItem}><span>Total Athletes</span><span>{totalAthletes}</span></div>
          <div style={s.statusItem}><span>Sensor Status</span><span>OK</span></div>
          <div style={s.statusItem}><span>Motor Status</span><span>OK</span></div>
          <div style={s.statusItem}><span>Emergency Stop</span><span>OK</span></div>
        </Panel>
      </div>
    </div>
  );
}

function DatabasePage({
  mode,
  setMode,
  databases,
  recentDatabaseId,
  setRecentDatabaseId,
  selectedDatabaseId,
  setSelectedDatabaseId,
  selectedAthleteId,
  setSelectedAthleteId,
  setPage,
  setDatabases,
  setAssessmentComplete,
  s,
}) {
  const [search, setSearch] = useState("");
  const [newDbName, setNewDbName] = useState("");
  const [importSourceId, setImportSourceId] = useState("");
  const [newAthlete, setNewAthlete] = useState({
    id: "",
    name: "",
    age: "",
    sport: "Football",
    dominantHand: "Right",
  });

  const recentDb = databases.find((db) => db.id === recentDatabaseId) || databases[0];
  const selectedDb =
    databases.find((db) => db.id === selectedDatabaseId) ||
    databases.find((db) => db.id === recentDatabaseId) ||
    databases[0];

  const filteredAthletes = useMemo(() => {
    if (!selectedDb) return [];
    return selectedDb.athletes.filter(
      (athlete) =>
        athlete.name.toLowerCase().includes(search.toLowerCase()) ||
        athlete.id.toLowerCase().includes(search.toLowerCase())
    );
  }, [search, selectedDb]);

  const selectedAthlete =
    selectedDb?.athletes.find((a) => a.id === selectedAthleteId) || null;

  const selectedAthleteSessions = selectedDb
    ? selectedDb.sessions.filter((session) => session.athleteId === selectedAthleteId)
    : [];

  const chooseRecent = () => {
    setMode("recent");
    if (recentDb) {
      setSelectedDatabaseId(recentDb.id);
    }
  };

  const chooseFree = () => {
    setMode("free");
    setSelectedDatabaseId(null);
    setSelectedAthleteId(null);
  };

  const chooseNew = () => {
    setMode("new");
    setSelectedAthleteId(null);
  };

  const deleteSession = (sessionId) => {
    setDatabases((prev) =>
      prev.map((db) =>
        db.id === selectedDb.id
          ? { ...db, sessions: db.sessions.filter((sesh) => sesh.id !== sessionId) }
          : db
      )
    );
  };

  const removeAthlete = (athleteId) => {
    setDatabases((prev) =>
      prev.map((db) =>
        db.id === selectedDb.id
          ? {
              ...db,
              athletes: db.athletes.filter((a) => a.id !== athleteId),
              sessions: db.sessions.filter((sesh) => sesh.athleteId !== athleteId),
            }
          : db
      )
    );
    if (selectedAthleteId === athleteId) {
      setSelectedAthleteId(null);
    }
  };

  const createDatabase = () => {
    if (!newDbName.trim()) return;
    const sourceDb = databases.find((db) => db.id === importSourceId);
    const newId = `db-${Date.now()}`;

    const createdDb = {
      id: newId,
      name: newDbName.trim(),
      createdAt: getTodayString(),
      athletes: sourceDb ? [...sourceDb.athletes] : [],
      sessions: [],
    };

    setDatabases((prev) => [createdDb, ...prev]);
    setRecentDatabaseId(newId);
    setSelectedDatabaseId(newId);
    setMode("new");
    setNewDbName("");
    setImportSourceId("");
  };

  const addAthleteToSelectedDb = () => {
    if (!selectedDb) return;
    if (!newAthlete.id.trim() || !newAthlete.name.trim()) return;

    const exists = selectedDb.athletes.some(
      (a) => a.id.toLowerCase() === newAthlete.id.trim().toLowerCase()
    );
    if (exists) return;

    const athleteRecord = {
      id: newAthlete.id.trim(),
      name: newAthlete.name.trim(),
      age: Number(newAthlete.age) || 0,
      sport: newAthlete.sport || "Football",
      dominantHand: newAthlete.dominantHand,
    };

    setDatabases((prev) =>
      prev.map((db) =>
        db.id === selectedDb.id ? { ...db, athletes: [...db.athletes, athleteRecord] } : db
      )
    );

    setNewAthlete({
      id: "",
      name: "",
      age: "",
      sport: "Football",
      dominantHand: "Right",
    });
  };

  const continueWithSelected = () => {
    setAssessmentComplete(false);
    setPage("assessment");
  };

  return (
    <div>
      <h1>Database</h1>
      <p style={s.subtext}>Choose how you want to work with patient data.</p>

      <div style={s.grid3}>
        <button onClick={chooseFree} style={{ ...s.card, textAlign: "left", cursor: "pointer", border: mode === "free" ? `2px solid ${s.c.text}` : `1px solid ${s.c.border}` }}>
          <h3 style={{ marginTop: 0 }}>Free Use Mode</h3>
          <p style={s.subtextSmall}>Run an assessment without saving patient data.</p>
        </button>

        <button onClick={chooseRecent} style={{ ...s.card, textAlign: "left", cursor: "pointer", border: mode === "recent" ? `2px solid ${s.c.text}` : `1px solid ${s.c.border}` }}>
          <h3 style={{ marginTop: 0 }}>Recent</h3>
          <p style={s.subtextSmall}>{recentDb ? recentDb.name : "No recent database selected"}</p>
        </button>

        <button onClick={chooseNew} style={{ ...s.card, textAlign: "left", cursor: "pointer", border: mode === "new" ? `2px solid ${s.c.text}` : `1px solid ${s.c.border}` }}>
          <h3 style={{ marginTop: 0 }}>Create New Database</h3>
          <p style={s.subtextSmall}>Create a dataset and optionally import patients.</p>
        </button>
      </div>

      {mode === "free" && (
        <Panel
          title="Free Use"
          subtitle="No patient data will be saved in this mode."
          s={s}
        >
          <button style={s.primaryButton} onClick={() => setPage("assessment")}>
            Continue in Free Use Mode
          </button>
        </Panel>
      )}

      {mode === "recent" && selectedDb && (
        <div style={s.grid2}>
          <Panel
            title="Select Athlete"
            subtitle={`Database: ${selectedDb.name}`}
            s={s}
          >
            <input
              style={s.input}
              placeholder="Search athlete name or ID"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />

            <div style={{ marginTop: 12 }}>
              {filteredAthletes.map((athlete) => (
                <button
                  key={athlete.id}
                  onClick={() => setSelectedAthleteId(athlete.id)}
                  style={{
                    ...s.listButton,
                    backgroundColor: selectedAthleteId === athlete.id ? s.c.currentBg : s.c.panel,
                    border: `1px solid ${selectedAthleteId === athlete.id ? s.c.currentBorder : s.c.border}`,
                  }}
                >
                  <div><b>{athlete.name}</b></div>
                  <div style={s.subtextSmall}>
                    {athlete.id} • {athlete.age} • {athlete.dominantHand}-hand dominant
                  </div>
                </button>
              ))}
            </div>
          </Panel>

          <Panel
            title="Selected Athlete Data"
            subtitle={selectedAthlete ? `${selectedAthlete.name} history` : "Pick an athlete to view recorded data"}
            s={s}
          >
            {!selectedAthlete && <p style={s.subtextSmall}>No patient selected yet.</p>}

            {selectedAthlete && (
              <>
                <div style={s.detailBox}>
                  <div><b>ID:</b> {selectedAthlete.id}</div>
                  <div><b>Age:</b> {selectedAthlete.age}</div>
                  <div><b>Dominant Hand:</b> {selectedAthlete.dominantHand}</div>
                </div>

                <h4 style={{ marginBottom: 8 }}>Recorded Sessions</h4>
                {selectedAthleteSessions.length === 0 && (
                  <p style={s.subtextSmall}>No saved data for this athlete yet.</p>
                )}

                {selectedAthleteSessions.map((session) => (
                  <div key={session.id} style={s.listRow}>
                    <div>
                      <div><b>{session.date}</b></div>
                      <div style={s.subtextSmall}>{session.summary}</div>
                      <div style={s.subtextSmall}>{session.notes}</div>
                    </div>
                    <button style={s.outlineButton} onClick={() => deleteSession(session.id)}>
                      Delete Data
                    </button>
                  </div>
                ))}

                <div style={s.buttonRow}>
                  <button style={s.outlineButton} onClick={() => removeAthlete(selectedAthlete.id)}>
                    Remove Patient
                  </button>
                  <button style={s.primaryButton} onClick={continueWithSelected}>
                    Continue Assessment
                  </button>
                </div>
              </>
            )}
          </Panel>
        </div>
      )}

      {mode === "new" && (
        <>
          <div style={s.grid2}>
            <Panel
              title="Create New Database"
              subtitle="You can import patients from another dataset or start empty."
              s={s}
            >
              <input
                style={s.input}
                placeholder="New database name"
                value={newDbName}
                onChange={(e) => setNewDbName(e.target.value)}
              />

              <select
                style={s.input}
                value={importSourceId}
                onChange={(e) => setImportSourceId(e.target.value)}
              >
                <option value="">Do not import patients</option>
                {databases.map((db) => (
                  <option key={db.id} value={db.id}>
                    Import patients from: {db.name}
                  </option>
                ))}
              </select>

              <button style={s.primaryButton} onClick={createDatabase}>
                Create Database
              </button>
            </Panel>

            <Panel
              title="Current Working Database"
              subtitle={selectedDb ? selectedDb.name : "No database created/selected yet"}
              s={s}
            >
              {selectedDb ? (
                <>
                  <div style={s.detailBox}>
                    <div><b>Created:</b> {selectedDb.createdAt}</div>
                    <div><b>Patients:</b> {selectedDb.athletes.length}</div>
                  </div>
                </>
              ) : (
                <p style={s.subtextSmall}>Create a database first.</p>
              )}
            </Panel>
          </div>

          {selectedDb && (
            <div style={s.grid2}>
              <Panel
                title="Add New Patient"
                subtitle="Add a patient not already in the system."
                s={s}
              >
                <input
                  style={s.input}
                  placeholder="Patient ID"
                  value={newAthlete.id}
                  onChange={(e) => setNewAthlete({ ...newAthlete, id: e.target.value })}
                />
                <input
                  style={s.input}
                  placeholder="Full Name"
                  value={newAthlete.name}
                  onChange={(e) => setNewAthlete({ ...newAthlete, name: e.target.value })}
                />
                <input
                  style={s.input}
                  placeholder="Age"
                  value={newAthlete.age}
                  onChange={(e) => setNewAthlete({ ...newAthlete, age: e.target.value })}
                />
                <input
                  style={s.input}
                  placeholder="Sport"
                  value={newAthlete.sport}
                  onChange={(e) => setNewAthlete({ ...newAthlete, sport: e.target.value })}
                />

                <div style={s.buttonRow}>
                  <button
                    style={newAthlete.dominantHand === "Right" ? s.primaryButton : s.outlineButton}
                    onClick={() => setNewAthlete({ ...newAthlete, dominantHand: "Right" })}
                  >
                    Right
                  </button>
                  <button
                    style={newAthlete.dominantHand === "Left" ? s.primaryButton : s.outlineButton}
                    onClick={() => setNewAthlete({ ...newAthlete, dominantHand: "Left" })}
                  >
                    Left
                  </button>
                </div>

                <button style={s.primaryButton} onClick={addAthleteToSelectedDb}>
                  Add Patient
                </button>
              </Panel>

              <Panel
                title="Patients in This Database"
                subtitle="Imported and newly added patients appear here."
                s={s}
              >
                {selectedDb.athletes.map((athlete) => (
                  <div key={athlete.id} style={s.listRow}>
                    <div>
                      <div><b>{athlete.name}</b></div>
                      <div style={s.subtextSmall}>
                        {athlete.id} • {athlete.age} • {athlete.dominantHand}
                      </div>
                    </div>
                    <button style={s.outlineButton} onClick={() => removeAthlete(athlete.id)}>
                      Remove
                    </button>
                  </div>
                ))}
              </Panel>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function AssessmentPage({
  selectedDatabase,
  selectedAthlete,
  mode,
  proceduralStep,
  setProceduralStep,
  assessmentComplete,
  setAssessmentComplete,
  setDatabases,
  setPage,
  setMode,
  setSelectedAthleteId,
  s,
}) {
  const [notes, setNotes] = useState("");
  const currentStep = proceduralSequence[proceduralStep];

  if (!selectedAthlete && mode !== "free") {
    return (
      <Panel
        title="Assessment"
        subtitle="Select a patient from the Database tab before starting."
        s={s}
      >
        <button style={s.primaryButton} onClick={() => setPage("database")}>
          Go to Database
        </button>
      </Panel>
    );
  }

  const finishAssessment = () => {
    if (mode !== "free" && selectedDatabase && selectedAthlete) {
      const newSession = {
        id: `S-${Date.now()}`,
        athleteId: selectedAthlete.id,
        date: getTodayString(),
        summary: "Completed full wrist assessment",
        notes: notes || "Assessment completed.",
      };

      setDatabases((prev) =>
        prev.map((db) =>
          db.id === selectedDatabase.id
            ? { ...db, sessions: [newSession, ...db.sessions] }
            : db
        )
      );
    }

    setAssessmentComplete(true);
  };

  const live = {
    primaryLabel:
      currentStep.test === "Pinch Testing"
        ? "Pinch Force"
        : currentStep.test === "Pronation / Supination" && currentStep.subtype === "Torque Test"
        ? "Measured Torque"
        : currentStep.test === "Pronation / Supination" && currentStep.subtype === "Angle Achieved Test"
        ? "Rotation Angle"
        : currentStep.test === "Radial / Ulnar Deviation"
        ? "Rotation Position"
        : "Bar Position",
    primaryValue:
      currentStep.test === "Pinch Testing"
        ? "31.4 N"
        : currentStep.test === "Pronation / Supination" && currentStep.subtype === "Torque Test"
        ? "1.8 Nm"
        : currentStep.test === "Pronation / Supination" && currentStep.subtype === "Angle Achieved Test"
        ? "24.1°"
        : "Max reached",
  };

  if (assessmentComplete) {
    return (
      <Panel
        title="Assessment Complete"
        subtitle="All tests are done. What would you like to do next?"
        s={s}
      >
        <div style={s.detailBox}>
          <div><b>Athlete:</b> {selectedAthlete?.name || "Free Use Mode"}</div>
          <div><b>Date:</b> {getTodayString()}</div>
          <div><b>Tests Completed:</b> {proceduralSequence.length}</div>
        </div>

        <div style={s.buttonRow}>
          <button
            style={s.primaryButton}
            onClick={() => {
              setAssessmentComplete(false);
              setProceduralStep(0);
              setPage("dashboard");
            }}
          >
            Return to Dashboard
          </button>

          <button
            style={s.secondaryButton}
            onClick={() => {
              setAssessmentComplete(false);
              setProceduralStep(0);
              setSelectedAthleteId(null);
              setMode("recent");
              setPage("database");
            }}
          >
            Select Another Patient
          </button>
        </div>
      </Panel>
    );
  }

  return (
    <div>
      <h1>Assessment</h1>
      <p style={s.subtext}>
        {mode === "free"
          ? "Free use assessment"
          : `${selectedAthlete.name} • ${selectedAthlete.dominantHand}-hand dominant`}
      </p>

      <div style={s.assessmentSplit}>
        <Panel title="Checklist" subtitle="Click any step to jump to it." s={s}>
          <div style={s.sequenceList}>
            {proceduralSequence.map((step, index) => {
              const status =
                index < proceduralStep ? "done" : index === proceduralStep ? "current" : "upcoming";

              return (
                <button
                  key={index}
                  type="button"
                  onClick={() => setProceduralStep(index)}
                  style={{
                    ...s.sequenceItem,
                    ...(status === "done" ? s.sequenceItemDone : {}),
                    ...(status === "current" ? s.sequenceItemCurrent : {}),
                  }}
                >
                  <div
                    style={{
                      ...s.sequenceNumber,
                      ...(status === "done" ? s.sequenceNumberDone : {}),
                      ...(status === "current" ? s.sequenceNumberCurrent : {}),
                    }}
                  >
                    {status === "done" ? "✓" : index + 1}
                  </div>

                  <div style={{ flex: 1 }}>
                    <div style={s.sequenceTitle}>{step.test}</div>
                    <div style={s.sequenceSubtitle}>{getSequenceLabel(step)}</div>
                  </div>
                </button>
              );
            })}
          </div>
        </Panel>

        <Panel
          title="Current Step"
          subtitle={`Step ${proceduralStep + 1} of ${proceduralSequence.length}`}
          s={s}
        >
          <div style={{ marginBottom: 12 }}>
            <div style={s.progressTrack}>
              <div
                style={{
                  ...s.progressFill,
                  width: `${((proceduralStep + 1) / proceduralSequence.length) * 100}%`,
                }}
              />
            </div>
          </div>

          <div style={s.stepBox}>
            <h3 style={{ marginTop: 0 }}>{currentStep.test}</h3>

            <div style={s.tagRow}>
              <span style={s.tag}>Hand: {currentStep.hand}</span>
              {currentStep.direction && <span style={s.tag}>Direction: {currentStep.direction}</span>}
              {currentStep.pattern && <span style={s.tag}>Pattern: {currentStep.pattern}</span>}
              {currentStep.subtype && <span style={s.tag}>Subtype: {currentStep.subtype}</span>}
              {selectedAthlete?.dominantHand && <span style={s.tag}>Dominant: {selectedAthlete.dominantHand}</span>}
            </div>

            <p style={s.subtextSmall}>
              {currentStep.test === "Flexion / Extension" &&
                `Move fully ${currentStep.direction.toLowerCase()} for the ${currentStep.hand.toLowerCase()} hand.`}
              {currentStep.test === "Radial / Ulnar Deviation" &&
                `Rotate fully ${currentStep.direction.toLowerCase()} for the ${currentStep.hand.toLowerCase()} hand.`}
              {currentStep.test === "Pinch Testing" &&
                `Record ${currentStep.pattern.toLowerCase()} for the ${currentStep.hand.toLowerCase()} hand.`}
              {currentStep.test === "Pronation / Supination" &&
                currentStep.subtype === "Torque Test" &&
                `Collect pronation and supination torque data for the ${currentStep.hand.toLowerCase()} hand.`}
              {currentStep.test === "Pronation / Supination" &&
                currentStep.subtype === "Angle Achieved Test" &&
                `Record angle achieved for the ${currentStep.hand.toLowerCase()} hand.`}
            </p>
          </div>

          <div style={s.grid2}>
            <div style={s.liveCard}>
              <div style={s.liveLabel}>{live.primaryLabel}</div>
              <div style={s.liveValue}>{live.primaryValue}</div>
            </div>

            <div style={s.liveCard}>
              <div style={s.liveLabel}>Hand</div>
              <div style={s.liveValueSmall}>{currentStep.hand}</div>
            </div>
          </div>

          <div style={{ marginTop: 14 }}>
            <label>Notes</label>
            <textarea
              style={s.textarea}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add observations or trial notes"
            />
          </div>

          <div style={s.buttonRowBetween}>
            <div style={s.buttonRow}>
              <button style={s.outlineButton}>Start Test</button>
              <button style={s.secondaryButton}>Redo Trial</button>
            </div>

            <div style={s.buttonRow}>
              <button
                style={s.outlineButton}
                disabled={proceduralStep === 0}
                onClick={() => setProceduralStep((p) => Math.max(0, p - 1))}
              >
                Back
              </button>

              {proceduralStep < proceduralSequence.length - 1 ? (
                <button
                  style={s.primaryButton}
                  onClick={() => setProceduralStep((p) => Math.min(proceduralSequence.length - 1, p + 1))}
                >
                  Continue
                </button>
              ) : (
                <button style={s.primaryButton} onClick={finishAssessment}>
                  Finish Assessment
                </button>
              )}
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}

function HistoryPage({ databases, s }) {
  const allSessions = databases.flatMap((db) =>
    db.sessions.map((session) => {
      const athlete = db.athletes.find((a) => a.id === session.athleteId);
      return {
        ...session,
        databaseName: db.name,
        athleteName: athlete?.name || session.athleteId,
      };
    })
  );

  return (
    <div>
      <h1>History</h1>
      <p style={s.subtext}>All saved sessions across databases.</p>

      <Panel title="Recent Sessions" s={s}>
        {allSessions.map((session) => (
          <div key={session.id} style={s.listRow}>
            <div>
              <div><b>{session.athleteName}</b> • {session.date}</div>
              <div style={s.subtextSmall}>{session.databaseName}</div>
              <div style={s.subtextSmall}>{session.summary}</div>
            </div>
          </div>
        ))}
      </Panel>
    </div>
  );
}

function SettingsPage({
  theme,
  setTheme,
  databases,
  recentDatabaseId,
  setRecentDatabaseId,
  s,
}) {
  return (
    <div>
      <h1>Settings</h1>
      <p style={s.subtext}>Theme and database preferences.</p>

      <div style={s.grid2}>
        <Panel title="Appearance" subtitle="Switch between light and dark mode." s={s}>
          <div style={s.buttonRow}>
            <button
              style={theme === "light" ? s.primaryButton : s.outlineButton}
              onClick={() => setTheme("light")}
            >
              Light Mode
            </button>
            <button
              style={theme === "dark" ? s.primaryButton : s.outlineButton}
              onClick={() => setTheme("dark")}
            >
              Dark Mode
            </button>
          </div>
        </Panel>

        <Panel title="Database Settings" subtitle="Choose which database appears as Recent." s={s}>
          <select
            style={s.input}
            value={recentDatabaseId}
            onChange={(e) => setRecentDatabaseId(e.target.value)}
          >
            {databases.map((db) => (
              <option key={db.id} value={db.id}>
                {db.name}
              </option>
            ))}
          </select>
        </Panel>
      </div>
    </div>
  );
}

export default function App() {
  const [theme, setTheme] = useState("light");
  const [page, setPage] = useState("dashboard");
  const [mode, setMode] = useState("recent");
  const [databases, setDatabases] = useState(initialDatabases);
  const [recentDatabaseId, setRecentDatabaseId] = useState(initialDatabases[0].id);
  const [selectedDatabaseId, setSelectedDatabaseId] = useState(initialDatabases[0].id);
  const [selectedAthleteId, setSelectedAthleteId] = useState(null);
  const [proceduralStep, setProceduralStep] = useState(0);
  const [assessmentComplete, setAssessmentComplete] = useState(false);

  const c = getTheme(theme);

  const s = {
    c,
    app: {
      display: "flex",
      minHeight: "100vh",
      fontFamily: "Arial, sans-serif",
      backgroundColor: c.bg,
      color: c.text,
    },
    sidebar: {
      width: "250px",
      backgroundColor: c.nav,
      color: "#fff",
      padding: "20px",
    },
    sidebarSub: {
      color: "#94a3b8",
      marginTop: 6,
    },
    main: {
      flex: 1,
      padding: "28px",
    },
    sideButton: {
      width: "100%",
      padding: "12px",
      marginBottom: "8px",
      border: "none",
      borderRadius: "12px",
      color: "white",
      textAlign: "left",
      cursor: "pointer",
    },
    card: {
      backgroundColor: c.panel,
      border: `1px solid ${c.border}`,
      borderRadius: "18px",
      padding: "18px",
      boxShadow: theme === "dark" ? "none" : "0 1px 4px rgba(0,0,0,0.06)",
      marginBottom: "16px",
      color: c.text,
    },
    subtext: {
      color: c.subtext,
      marginTop: "-6px",
      marginBottom: "18px",
    },
    subtextSmall: {
      color: c.subtext,
      fontSize: "14px",
      lineHeight: 1.4,
    },
    grid4: {
      display: "grid",
      gridTemplateColumns: "repeat(4, 1fr)",
      gap: "16px",
      marginBottom: "16px",
    },
    grid3: {
      display: "grid",
      gridTemplateColumns: "repeat(3, 1fr)",
      gap: "16px",
      marginBottom: "16px",
    },
    grid2: {
      display: "grid",
      gridTemplateColumns: "repeat(2, 1fr)",
      gap: "16px",
    },
    assessmentSplit: {
      display: "grid",
      gridTemplateColumns: "320px 1fr",
      gap: "16px",
    },
    buttonRow: {
      display: "flex",
      gap: "10px",
      flexWrap: "wrap",
      marginTop: "12px",
    },
    buttonRowBetween: {
      display: "flex",
      justifyContent: "space-between",
      gap: "10px",
      flexWrap: "wrap",
      marginTop: "16px",
    },
    primaryButton: {
      backgroundColor: c.primary,
      color: c.primaryText,
      border: "none",
      padding: "12px 16px",
      borderRadius: "12px",
      cursor: "pointer",
    },
    secondaryButton: {
      backgroundColor: c.secondary,
      color: c.secondaryText,
      border: "none",
      padding: "12px 16px",
      borderRadius: "12px",
      cursor: "pointer",
    },
    outlineButton: {
      backgroundColor: c.outlineBg,
      color: c.outlineText,
      border: `1px solid ${c.border}`,
      padding: "12px 16px",
      borderRadius: "12px",
      cursor: "pointer",
    },
    input: {
      width: "100%",
      padding: "10px 12px",
      borderRadius: "10px",
      border: `1px solid ${c.border}`,
      marginTop: "6px",
      boxSizing: "border-box",
      backgroundColor: c.inputBg,
      color: c.text,
    },
    textarea: {
      width: "100%",
      minHeight: "100px",
      padding: "10px 12px",
      borderRadius: "10px",
      border: `1px solid ${c.border}`,
      marginTop: "6px",
      boxSizing: "border-box",
      backgroundColor: c.inputBg,
      color: c.text,
    },
    listButton: {
      width: "100%",
      textAlign: "left",
      padding: "12px",
      borderRadius: "12px",
      marginBottom: "10px",
      cursor: "pointer",
      backgroundColor: c.panel,
      color: c.text,
    },
    listRow: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      gap: "12px",
      padding: "12px",
      border: `1px solid ${c.border}`,
      borderRadius: "12px",
      marginBottom: "10px",
      backgroundColor: c.panelSoft,
    },
    detailBox: {
      padding: "12px",
      borderRadius: "12px",
      border: `1px solid ${c.border}`,
      backgroundColor: c.panelSoft,
      marginBottom: "12px",
      display: "grid",
      gap: "6px",
    },
    sequenceList: {
      display: "flex",
      flexDirection: "column",
      gap: "10px",
    },
    sequenceItem: {
      width: "100%",
      display: "flex",
      gap: "12px",
      alignItems: "flex-start",
      padding: "10px",
      borderRadius: "12px",
      border: `1px solid ${c.border}`,
      backgroundColor: c.panel,
      textAlign: "left",
      cursor: "pointer",
      color: c.text,
    },
    sequenceItemDone: {
      backgroundColor: c.successBg,
      border: `1px solid ${c.successBorder}`,
    },
    sequenceItemCurrent: {
      backgroundColor: c.currentBg,
      border: `1px solid ${c.currentBorder}`,
    },
    sequenceNumber: {
      minWidth: "28px",
      height: "28px",
      borderRadius: "999px",
      backgroundColor: c.tagBg,
      color: c.tagText,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontSize: "12px",
      fontWeight: 700,
    },
    sequenceNumberDone: {
      backgroundColor: "#16a34a",
      color: "white",
    },
    sequenceNumberCurrent: {
      backgroundColor: "#2563eb",
      color: "white",
    },
    sequenceTitle: {
      fontWeight: 700,
      fontSize: "14px",
      marginBottom: "2px",
    },
    sequenceSubtitle: {
      fontSize: "13px",
      color: c.subtext,
    },
    progressTrack: {
      width: "100%",
      height: "10px",
      backgroundColor: c.tagBg,
      borderRadius: "999px",
      overflow: "hidden",
    },
    progressFill: {
      height: "100%",
      backgroundColor: c.primary,
    },
    stepBox: {
      border: `1px solid ${c.border}`,
      borderRadius: "14px",
      padding: "14px",
      backgroundColor: c.panelSoft,
      marginBottom: "14px",
    },
    tagRow: {
      display: "flex",
      gap: "8px",
      flexWrap: "wrap",
      marginBottom: "12px",
    },
    tag: {
      backgroundColor: c.tagBg,
      color: c.tagText,
      padding: "6px 10px",
      borderRadius: "999px",
      fontSize: "13px",
    },
    liveCard: {
      backgroundColor: c.panelSoft,
      border: `1px solid ${c.border}`,
      borderRadius: "14px",
      padding: "14px",
    },
    liveLabel: {
      color: c.subtext,
      fontSize: "14px",
      marginBottom: "8px",
    },
    liveValue: {
      fontSize: "24px",
      fontWeight: 700,
      color: c.text,
    },
    statusItem: {
      display: "flex",
      justifyContent: "space-between",
      padding: "10px 12px",
      border: `1px solid ${c.border}`,
      borderRadius: "12px",
      marginBottom: "10px",
      backgroundColor: c.panelSoft,
    },
  };

  const selectedDatabase =
    databases.find((db) => db.id === selectedDatabaseId) ||
    databases.find((db) => db.id === recentDatabaseId) ||
    null;

  const selectedAthlete =
    selectedDatabase?.athletes.find((a) => a.id === selectedAthleteId) || null;

  const totalAthletes = databases.reduce((sum, db) => sum + db.athletes.length, 0);

  return (
    <div style={s.app}>
      <Sidebar page={page} setPage={setPage} s={s} />
      <main style={s.main}>
        {page === "dashboard" && (
          <Dashboard
            setPage={setPage}
            selectedAthlete={selectedAthlete}
            selectedDatabase={selectedDatabase}
            totalAthletes={totalAthletes}
            theme={theme}
            s={s}
          />
        )}

        {page === "database" && (
          <DatabasePage
            mode={mode}
            setMode={setMode}
            databases={databases}
            recentDatabaseId={recentDatabaseId}
            setRecentDatabaseId={setRecentDatabaseId}
            selectedDatabaseId={selectedDatabaseId}
            setSelectedDatabaseId={setSelectedDatabaseId}
            selectedAthleteId={selectedAthleteId}
            setSelectedAthleteId={setSelectedAthleteId}
            setPage={setPage}
            setDatabases={setDatabases}
            setAssessmentComplete={setAssessmentComplete}
            s={s}
          />
        )}

        {page === "assessment" && (
          <AssessmentPage
            selectedDatabase={selectedDatabase}
            selectedAthlete={selectedAthlete}
            mode={mode}
            proceduralStep={proceduralStep}
            setProceduralStep={setProceduralStep}
            assessmentComplete={assessmentComplete}
            setAssessmentComplete={setAssessmentComplete}
            setDatabases={setDatabases}
            setPage={setPage}
            setMode={setMode}
            setSelectedAthleteId={setSelectedAthleteId}
            s={s}
          />
        )}

        {page === "history" && <HistoryPage databases={databases} s={s} />}

        {page === "settings" && (
          <SettingsPage
            theme={theme}
            setTheme={setTheme}
            databases={databases}
            recentDatabaseId={recentDatabaseId}
            setRecentDatabaseId={setRecentDatabaseId}
            s={s}
          />
        )}
      </main>
    </div>
  );
}