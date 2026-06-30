# FaceTrack Pro — Classroom Attendance System

A professional, real-world face recognition attendance system designed for schools and colleges. Built entirely in Python with CSV storage — no database required.

---

## ML Models Used

| Component | Model | Accuracy | Details |
|---|---|---|---|
| **Face Detection** | RetinaFace | 96%+ | Multi-scale anchor-free detector, works at angles and in low light |
| **Face Recognition** | ArcFace R100 | 99.83% LFW | 512-dim additive angular margin embeddings |
| **Liveness Detection** | MediaPipe FaceMesh | — | 468 facial landmarks, eye-blink based anti-spoofing |

Both RetinaFace and ArcFace come bundled in InsightFace `buffalo_l` — one install covers both.

---

## Project Structure

```
FaceTrack/
├── app.py              ← Main application — run this
├── src/
│   ├── config.py       ← All constants, paths, model settings
│   ├── storage.py      ← All CSV data operations (zero SQL)
│   ├── recognition.py  ← RetinaFace + ArcFace + MediaPipe
│   ├── theme.py        ← Light / Dark colour palettes + TTK styles
│   └── widgets.py      ← Reusable widget factories
├── requirements.txt    ← All Python dependencies
├── install.bat         ← One-click install (Windows)
├── run.bat             ← Launch the app (Windows)
├── README.md
└── Data/               ← All data stored here (auto-created)
    ├── students.csv
    ├── leaves.csv
    ├── holidays.csv
    ├── audit.csv
    ├── settings.csv
    ├── Attendance/     ← One CSV file per day
    ├── Photos/         ← Registration face photos
    ├── Embeddings/     ← ArcFace .npy embedding files
    ├── UnknownFaces/   ← Saved photos of unrecognised faces
    ├── Reports/        ← Excel export files
    └── Backups/        ← ZIP backup archives
```

---

## Setup

### Step 1 — Install dependencies
```
pip install -r requirements.txt --prefer-binary
```
Or double-click `install.bat` on Windows.

### Step 2 — Run the application
```
python app.py
```
Or double-click `run.bat` on Windows.

**First launch** downloads the ArcFace buffalo_l model (~300 MB). Internet connection required once only.

---

## Default Login

| Username | Password |
|---|---|
| admin | admin123 |

Change via **System → Settings → Security tab**.

---

## Features

### Student Management
- Register students with 5 face photos (configurable 3–10)
- View all students with search and filter
- Edit student details (name, class, email, phone)
- Remove student — deletes record, photos, and face data instantly
- Rebuild face data from existing photos

### Attendance
- **Auto Attendance** — Continuous live camera, marks automatically
- **Manual Scan** — Single session, press Q to stop
- **Late arrival detection** — Configurable class start time and threshold
- **Liveness detection** — Students must blink to be verified (prevents photo spoofing)
- **Cooldown period** — Prevents duplicate marks in same session
- Filter today's log by class

### Analytics & Reports
- Per-student attendance percentage with bar charts (horizontal + vertical)
- Filter by class or date range
- Highlight students below threshold (default 75%)
- Excel export with colour-coded formatting
- Monthly summary

### Leave & Holiday Management
- Add approved leaves (Medical, Casual, Emergency, Study Leave, Other)
- Leave days automatically excluded from attendance percentage
- Holiday calendar — mark holidays to exclude from working days

### Security
- Admin login with hashed password
- Eye blink liveness detection (real faces must blink, photos cannot)
- Full audit log — every action recorded with timestamp
- Change password from Settings

### System
- Light and Dark theme (toggle anytime)
- Settings panel with tabs (Institution, Attendance, Recognition, Security)
- Backup and Restore (ZIP archive of all data)
- All data in plain CSV — open any file in Excel at any time

---

## Key Guarantees

1. **Attendance from live camera only** — `mark_attendance()` is called exclusively inside the live camera loops. Static images cannot trigger attendance.

2. **Liveness required** — A face must blink before attendance is marked. Printed photos and screen recordings are rejected.

3. **5 photos, not 100** — Registration captures exactly 5 face photos (configurable). Face embeddings are extracted immediately from live captures.

4. **Zero database** — Every piece of data is stored in a plain CSV file that can be opened directly in Microsoft Excel.

---

## Configuration

Open **System → Settings** to configure:

| Setting | Default | Description |
|---|---|---|
| Class Start Time | 09:00 | Time after which students are late |
| Late Threshold | 15 min | Grace period before marking late |
| Low Attendance | 75% | Threshold for low attendance alerts |
| Recognition Tolerance | 0.40 | Cosine distance (lower = stricter) |
| Photos per Registration | 5 | Face photos captured during registration |
| Cooldown | 15 sec | Time before same student can be re-marked |
| Frame Skip | 2 | Process every Nth frame (higher = faster but less responsive) |
