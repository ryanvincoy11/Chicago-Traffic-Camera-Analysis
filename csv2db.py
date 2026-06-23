import pandas as pd
import sqlite3

# -----------------------------
# 1. Load CSVs
# -----------------------------
red = pd.read_csv("Red_Light_Camera_Violations_20260415.csv")
speed = pd.read_csv("Speed_Camera_Violations_20260415.csv")

# -----------------------------
# 2. Normalize column names
# -----------------------------
red.columns = red.columns.str.strip().str.upper()
speed.columns = speed.columns.str.strip().str.upper()

rename_map = {
    "INTERSECTION": "Intersection",
    "CAMERA ID": "Camera_ID",
    "ADDRESS": "Address",
    "VIOLATION DATE": "Violation_Date",
    "VIOLATIONS": "Num_Violations",
    "X COORDINATE": "X_Coordinate",
    "Y COORDINATE": "Y_Coordinate",
    "LATITUDE": "Latitude",
    "LONGITUDE": "Longitude",
    "LOCATION": "Location"
}

red = red.rename(columns=rename_map)
speed = speed.rename(columns=rename_map)

print("RED COLUMNS:", red.columns.tolist())
print("SPEED COLUMNS:", speed.columns.tolist())

print("Missing Camera_ID in RED:", red["Camera_ID"].isna().sum())
print("Missing Camera_ID in SPEED:", speed["Camera_ID"].isna().sum())

# -----------------------------
# 3. Connect to SQLite
# -----------------------------
conn = sqlite3.connect("cameras.sqlite")
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

# -----------------------------
# 4. Create tables
# -----------------------------
cur.executescript("""
CREATE TABLE IF NOT EXISTS Intersections (
    Intersection_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Intersection TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS RedCameras (
    Camera_ID TEXT PRIMARY KEY,
    Intersection_ID INTEGER NOT NULL,
    Address TEXT,
    X_Coordinate REAL,
    Y_Coordinate REAL,
    Latitude REAL,
    Longitude REAL,
    Location TEXT,
    FOREIGN KEY (Intersection_ID) REFERENCES Intersections(Intersection_ID)
);

CREATE TABLE IF NOT EXISTS SpeedCameras (
    Camera_ID TEXT PRIMARY KEY,
    Intersection_ID INTEGER NOT NULL,
    Address TEXT,
    X_Coordinate REAL,
    Y_Coordinate REAL,
    Latitude REAL,
    Longitude REAL,
    Location TEXT,
    FOREIGN KEY (Intersection_ID) REFERENCES Intersections(Intersection_ID)
);

CREATE TABLE IF NOT EXISTS RedViolations (
    Violation_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Camera_ID TEXT NOT NULL,
    Violation_Date TEXT NOT NULL,
    Num_Violations INTEGER NOT NULL,
    FOREIGN KEY (Camera_ID) REFERENCES RedCameras(Camera_ID)
);

CREATE TABLE IF NOT EXISTS SpeedViolations (
    Violation_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Camera_ID TEXT NOT NULL,
    Violation_Date TEXT NOT NULL,
    Num_Violations INTEGER NOT NULL,
    FOREIGN KEY (Camera_ID) REFERENCES SpeedCameras(Camera_ID)
);
""")

# -----------------------------
# 5. Helper: Insert or get intersection ID
# -----------------------------
def get_intersection_id(name: str) -> int:
    cur.execute("SELECT Intersection_ID FROM Intersections WHERE Intersection = ?", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO Intersections (Intersection) VALUES (?)", (name,))
    return cur.lastrowid

# -----------------------------
# 6. Insert Red Cameras (skip rows with missing Camera_ID)
# -----------------------------
red_cameras = red.dropna(subset=["Camera_ID"]).drop_duplicates(subset=["Camera_ID"])

for _, row in red_cameras.iterrows():
    inter_id = get_intersection_id(row["Intersection"])
    cur.execute("""
        INSERT OR IGNORE INTO RedCameras
        (Camera_ID, Intersection_ID, Address, X_Coordinate, Y_Coordinate, Latitude, Longitude, Location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["Camera_ID"], inter_id, row["Address"],
        row["X_Coordinate"], row["Y_Coordinate"],
        row["Latitude"], row["Longitude"], row["Location"]
    ))

# -----------------------------
# 7. Insert Speed Cameras (no Intersection column → use Address)
#    Skip rows with missing Camera_ID
# -----------------------------
speed_cameras = speed.dropna(subset=["Camera_ID"]).drop_duplicates(subset=["Camera_ID"])

for _, row in speed_cameras.iterrows():
    inter_id = get_intersection_id(row["Address"])
    cur.execute("""
        INSERT OR IGNORE INTO SpeedCameras
        (Camera_ID, Intersection_ID, Address, X_Coordinate, Y_Coordinate, Latitude, Longitude, Location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["Camera_ID"], inter_id, row["Address"],
        row["X_Coordinate"], row["Y_Coordinate"],
        row["Latitude"], row["Longitude"], row["Location"]
    ))

# -----------------------------
# 8. Insert Red Violations (skip missing Camera_ID)
# -----------------------------
for _, row in red.dropna(subset=["Camera_ID"]).iterrows():
    cur.execute("""
        INSERT INTO RedViolations (Camera_ID, Violation_Date, Num_Violations)
        VALUES (?, ?, ?)
    """, (
        row["Camera_ID"], row["Violation_Date"], row["Num_Violations"]
    ))

# -----------------------------
# 9. Insert Speed Violations (skip missing Camera_ID)
# -----------------------------
for _, row in speed.dropna(subset=["Camera_ID"]).iterrows():
    cur.execute("""
        INSERT INTO SpeedViolations (Camera_ID, Violation_Date, Num_Violations)
        VALUES (?, ?, ?)
    """, (
        row["Camera_ID"], row["Violation_Date"], row["Num_Violations"]
    ))

# -----------------------------
# 10. Commit and close
# -----------------------------
conn.commit()
conn.close()

print("Import complete.")
