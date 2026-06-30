"""
recognition.py — FaceTrack Pro

ML Models
─────────
1. Face Detection    : RetinaFace   (part of InsightFace buffalo_l)
   • Multi-scale anchor-free detector
   • Works at angles, low light, partial occlusion
   • ~96% detection rate vs Haar's ~70%

2. Face Recognition  : ArcFace R100 (part of InsightFace buffalo_l)
   • 512-dimensional face embeddings
   • 99.83% accuracy on LFW benchmark
   • Cosine similarity matching

3. Liveness Detection: Eye-Aspect-Ratio via MediaPipe FaceMesh
   • 468 facial landmarks at 30fps on CPU
   • Detects real eye blink vs printed photo
   • Works offline, no download required

No GPU required. All CPU inference.
"""

import os, cv2, threading, time, pickle, sys
import numpy as np

# ── Path fix: always works regardless of how the file is invoked ──
_src = os.path.dirname(os.path.abspath(__file__))
if _src not in sys.path:
    sys.path.insert(0, _src)
if __name__ == '__main__':
    print('Run app.py instead:  python app.py')
    sys.exit(1)

from config import *

# ── Suppress logs ──────────────────────────────────────────────────
os.environ["TF_CPP_MIN_LOG_LEVEL"]  = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# ── InsightFace ────────────────────────────────────────────────────
try:
    from insightface.app import FaceAnalysis
    IF_OK = True
except ImportError:
    IF_OK = False

# ── MediaPipe ─────────────────────────────────────────────────────
try:
    import mediapipe as mp
    MP_OK = True
except ImportError:
    MP_OK = False

# ─────────────────────────────────────────────────────────────────
#  GLOBALS
# ─────────────────────────────────────────────────────────────────
_face_app     = None          # InsightFace FaceAnalysis instance
_enc_cache    = {}            # {sid: np.ndarray shape (N,512)}
_enc_lock     = threading.Lock()
_mp_mesh      = None          # MediaPipe FaceMesh

# MediaPipe landmark indices for eyes
_LEFT_EYE  = [362, 385, 387, 263, 373, 380]
_RIGHT_EYE = [33,  160, 158, 133, 153, 144]


# ══════════════════════════════════════════════════════════════════
#  MODEL LOADING
# ══════════════════════════════════════════════════════════════════

def load_model(status_cb=None) -> bool:
    """
    Load InsightFace buffalo_l (ArcFace + RetinaFace).
    Downloads ~300 MB on first run, cached locally after that.
    Returns True on success.
    """
    global _face_app
    if not IF_OK:
        return False
    try:
        if status_cb:
            status_cb("Loading face recognition engine…")
        _face_app = FaceAnalysis(name=INSIGHTFACE_MODEL)
        _face_app.prepare(ctx_id=0, det_size=(640, 640))
        if status_cb:
            status_cb("Face recognition engine ready.")
        return True
    except Exception as e:
        print(f"[Recognition] Load error: {e}")
        return False

def model_ready() -> bool:
    return _face_app is not None

def _get_mp_mesh():
    """Lazy-load MediaPipe FaceMesh."""
    global _mp_mesh
    if _mp_mesh is None and MP_OK:
        _mp_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode    = False,
            max_num_faces        = 8,
            refine_landmarks     = True,
            min_detection_confidence = 0.5,
            min_tracking_confidence  = 0.5)
    return _mp_mesh


# ══════════════════════════════════════════════════════════════════
#  FACE DETECTION  —  RetinaFace
# ══════════════════════════════════════════════════════════════════

def detect_faces(bgr_frame: np.ndarray) -> list:
    """
    Detect all faces in a BGR frame using RetinaFace.
    Returns list of dicts: {bbox:(x1,y1,x2,y2), embedding:np.ndarray}
    Returns empty list if model not loaded.
    """
    if _face_app is None:
        return []
    try:
        faces = _face_app.get(bgr_frame)
        result = []
        for f in faces:
            bx = f.bbox.astype(int)
            result.append({
                "bbox"      : (bx[0], bx[1], bx[2], bx[3]),
                "embedding" : _normalise(f.embedding),
                "det_score" : float(f.det_score),
            })
        return result
    except Exception as e:
        print(f"[Detection] Error: {e}")
        return []


# ══════════════════════════════════════════════════════════════════
#  LIVENESS DETECTION  —  MediaPipe Eye Blink
# ══════════════════════════════════════════════════════════════════

def _ear(landmarks, indices, w, h) -> float:
    """Eye Aspect Ratio from MediaPipe landmarks."""
    pts = np.array([(landmarks[i].x * w, landmarks[i].y * h)
                    for i in indices])
    A = np.linalg.norm(pts[1] - pts[5])
    B = np.linalg.norm(pts[2] - pts[4])
    C = np.linalg.norm(pts[0] - pts[3])
    return (A + B) / (2.0 * C + 1e-6)

class LivenessChecker:
    """
    Per-face blink-based liveness checker.
    Tracks EAR over time; real faces blink, photos do not.
    """
    def __init__(self):
        self._ear_history  = []    # recent EAR values
        self._blink_count  = 0
        self._below_thresh = 0
        self._is_live      = False
        self._checked      = False  # True once liveness confirmed

    def update(self, bgr_frame: np.ndarray, bbox: tuple) -> tuple:
        """
        Process one frame. Returns (is_live: bool, ear: float).
        Once liveness is confirmed it stays True for the session.
        """
        if self._is_live:
            return True, 1.0

        mesh = _get_mp_mesh()
        if mesh is None:
            # MediaPipe not installed — fail open (trust all faces)
            self._is_live = True
            return True, 1.0

        x1, y1, x2, y2 = bbox
        h, w = bgr_frame.shape[:2]
        x1 = max(0, x1 - 20); y1 = max(0, y1 - 20)
        x2 = min(w, x2 + 20); y2 = min(h, y2 + 20)
        roi = bgr_frame[y1:y2, x1:x2]
        if roi.size == 0:
            return False, 0.0

        rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        res = mesh.process(rgb)
        if not res.multi_face_landmarks:
            return False, 0.0

        lm   = res.multi_face_landmarks[0].landmark
        rh,rw = roi.shape[:2]
        ear_l = _ear(lm, _LEFT_EYE,  rw, rh)
        ear_r = _ear(lm, _RIGHT_EYE, rw, rh)
        ear   = (ear_l + ear_r) / 2.0

        self._ear_history.append(ear)
        if len(self._ear_history) > 30:
            self._ear_history.pop(0)

        if ear < LIVENESS_EAR_THRESH:
            self._below_thresh += 1
        else:
            if self._below_thresh >= LIVENESS_BLINK_FRAMES:
                self._blink_count += 1
            self._below_thresh = 0

        if self._blink_count >= 1:
            self._is_live = True

        return self._is_live, round(ear, 3)

# Global liveness tracker per face ID
_liveness_trackers: dict = {}

def get_liveness_tracker(face_id: str) -> LivenessChecker:
    if face_id not in _liveness_trackers:
        _liveness_trackers[face_id] = LivenessChecker()
    return _liveness_trackers[face_id]

def clear_liveness_trackers():
    _liveness_trackers.clear()


# ══════════════════════════════════════════════════════════════════
#  FACE RECOGNITION  —  ArcFace
# ══════════════════════════════════════════════════════════════════

def _normalise(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > 0 else v

def _cosine_dist(a, b) -> float:
    return float(1.0 - np.dot(_normalise(a), _normalise(b)))

def match_face(embedding: np.ndarray) -> tuple:
    """
    Match an ArcFace embedding against all stored encodings.
    Returns (student_id, confidence_pct) or (None, 0).
    Uses cosine distance; threshold from settings.
    """
    with _enc_lock:
        cache = dict(_enc_cache)

    if not cache:
        return None, 0

    tol      = float(_settings_tol())
    best_sid = None
    best_d   = float("inf")

    for sid, embs in cache.items():
        for e in embs:
            d = _cosine_dist(embedding, e)
            if d < best_d:
                best_d   = d
                best_sid = sid

    if best_sid and best_d <= tol:
        conf = round((1.0 - best_d) * 100, 1)
        return best_sid, conf

    return None, 0

def _settings_tol() -> str:
    """Import here to avoid circular imports."""
    try:
        from storage import setting
        return setting("tolerance", str(RECOGNITION_THRESH))
    except Exception:
        return str(RECOGNITION_THRESH)


# ══════════════════════════════════════════════════════════════════
#  EMBEDDING STORAGE
# ══════════════════════════════════════════════════════════════════

def enc_load_all():
    """Load all .npy embedding files into memory cache."""
    with _enc_lock:
        _enc_cache.clear()
        if not os.path.isdir(DIR_EMBEDDINGS):
            return
        for fn in os.listdir(DIR_EMBEDDINGS):
            if fn.endswith(".npy"):
                sid = fn.replace(".npy","")
                try:
                    arr = np.load(os.path.join(DIR_EMBEDDINGS, fn))
                    _enc_cache[sid] = arr
                except Exception as e:
                    print(f"[Embeddings] Could not load {fn}: {e}")
    print(f"[Embeddings] Loaded {len(_enc_cache)} student(s).")

def enc_save(sid: str, embeddings: list):
    os.makedirs(DIR_EMBEDDINGS, exist_ok=True)
    path = os.path.join(DIR_EMBEDDINGS, f"{sid}.npy")
    arr  = np.array(embeddings, dtype=np.float32)
    np.save(path, arr)
    with _enc_lock:
        _enc_cache[str(sid)] = arr

def enc_remove(sid: str):
    path = os.path.join(DIR_EMBEDDINGS, f"{sid}.npy")
    if os.path.isfile(path):
        os.remove(path)
    with _enc_lock:
        _enc_cache.pop(str(sid), None)

def enc_count() -> int:
    with _enc_lock:
        return len(_enc_cache)


# ══════════════════════════════════════════════════════════════════
#  REGISTRATION  —  capture photos & extract embeddings
# ══════════════════════════════════════════════════════════════════

def register_student(sid: str, name: str, status_cb=None) -> tuple:
    """
    Open webcam, capture PHOTOS_PER_STUDENT face photos,
    extract ArcFace embeddings, save to .npy file.
    Returns (success, photos_saved, embs_saved, error_msg)

    FIX: Detection runs in a background thread so the camera
    window always stays live and responsive on screen.
    """
    if not model_ready():
        return False, 0, 0, "Face recognition engine not loaded yet."

    target    = int(_settings_photos())
    photo_dir = os.path.join(DIR_PHOTOS, str(sid))
    os.makedirs(photo_dir, exist_ok=True)

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        return False, 0, 0, "Cannot open webcam."

    cam.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cam.set(cv2.CAP_PROP_FPS, 30)

    font         = cv2.FONT_HERSHEY_SIMPLEX
    photos_saved = 0
    embeddings   = []
    last_cap     = 0.0
    interval     = 1.5      # seconds between captures
    cancelled    = [False]

    # ── Background detection thread ───────────────────────────────
    # InsightFace is slow (~200-500ms on CPU). Running it in the
    # main loop blocks imshow → window never appears.
    # Solution: detect in background, draw last result on screen.
    det_faces   = [None]   # latest list of detected faces
    det_busy    = [False]
    det_request = [None]   # frame queued for detection

    def _det_worker():
        while not cancelled[0]:
            if det_request[0] is not None and not det_busy[0]:
                det_busy[0]    = True
                frame_copy     = det_request[0]
                det_request[0] = None
                try:
                    if _face_app is not None:
                        raw = _face_app.get(frame_copy)
                        results = []
                        for face in raw:
                            bx = face.bbox.astype(int)
                            results.append({
                                "bbox"     : (bx[0], bx[1], bx[2], bx[3]),
                                "embedding": _normalise(face.embedding),
                            })
                        det_faces[0] = results
                except Exception:
                    det_faces[0] = []
                det_busy[0] = False
            time.sleep(0.01)

    t = threading.Thread(target=_det_worker, daemon=True)
    t.start()

    # ── Create and force the camera window to the foreground ────────
    _wname = f"FaceTrack Pro — Register: {name}  [Face must be large & centred]"
    cv2.namedWindow(_wname, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(_wname, 800, 600)

    # Read one frame first so the window has content before we raise it
    _ok, _first = cam.read()
    if _ok:
        cv2.imshow(_wname, _first)
        cv2.waitKey(1)

    # ── Force camera window to foreground (works from background thread) ──
    # Step 1: Use cv2's own always-on-top property (most reliable cross-version)
    try:
        cv2.setWindowProperty(_wname, cv2.WND_PROP_TOPMOST, 1)
    except Exception:
        pass

    # Step 2: Win32 — AttachThreadInput trick (required because we're on a bg thread)
    import sys as _sys, subprocess as _sub
    _plat = _sys.platform
    try:
        if _plat == "win32":
            import ctypes, ctypes.wintypes, time as _tw
            _tw.sleep(0.3)   # give cv2 time to register the HWND with the OS

            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            # Win32 API references
            _EnumWindows      = user32.EnumWindows
            _EnumWindowsProc  = ctypes.WINFUNCTYPE(ctypes.c_bool,
                                    ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
            _GetWindowText    = user32.GetWindowTextW
            _GetWindowTextLen = user32.GetWindowTextLengthW
            _ShowWindow       = user32.ShowWindow
            _SetWindowPos     = user32.SetWindowPos
            _SetForeground    = user32.SetForegroundWindow
            _GetForeground    = user32.GetForegroundWindow
            _AttachThread     = user32.AttachThreadInput
            _GetWinThread     = user32.GetWindowThreadProcessId
            _GetCurThread     = kernel32.GetCurrentThreadId
            _HWND_TOPMOST     = ctypes.wintypes.HWND(-1)
            _SWP_NOMOVE       = 0x0002
            _SWP_NOSIZE       = 0x0001

            # Find the OpenCV window HWND by title match
            _found = [None]
            def _ecb(hwnd, lp):
                n = _GetWindowTextLen(hwnd) + 1
                buf = ctypes.create_unicode_buffer(n)
                _GetWindowText(hwnd, buf, n)
                # Match first 25 chars (title may be truncated by OS)
                if _wname[:25] in buf.value:
                    _found[0] = hwnd; return False
                return True
            _EnumWindows(_EnumWindowsProc(_ecb), 0)

            if _found[0]:
                hwnd = _found[0]
                # AttachThreadInput lets a bg-thread call SetForegroundWindow
                fg_hwnd   = _GetForeground()
                fg_thread = _GetWinThread(fg_hwnd, None)
                our_thread= _GetCurThread()
                if fg_thread != our_thread:
                    _AttachThread(fg_thread, our_thread, True)

                _ShowWindow(hwnd, 9)             # SW_RESTORE (un-minimise)
                # Make TOPMOST so it pops above the Tkinter window
                _SetWindowPos(hwnd, _HWND_TOPMOST, 0, 0, 0, 0,
                              _SWP_NOMOVE | _SWP_NOSIZE)
                _SetForeground(hwnd)

                if fg_thread != our_thread:
                    _AttachThread(fg_thread, our_thread, False)

        elif _plat == "darwin":
            import subprocess as _sp
            _sp.Popen(["osascript", "-e",
                'tell application "System Events" to set frontmost of '
                'every process whose unix id is ' +
                str(__import__("os").getpid()) + ' to true'],
                stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)
        else:
            import time as _tl; _tl.sleep(0.2)
            _sub.Popen(["wmctrl", "-a", _wname[:25]],
                       stdout=_sub.DEVNULL, stderr=_sub.DEVNULL)
    except Exception:
        pass   # silently ignore — window still opens, just may not be on top

    if status_cb:
        status_cb(f"Camera open — look at the registration window for {name}")

    fc = 0
    while photos_saved < target and not cancelled[0]:
        ret, frame = cam.read()
        if not ret:
            break
        fc += 1

        # Submit every 5th frame to background detector
        if fc % 5 == 0 and not det_busy[0]:
            det_request[0] = frame.copy()

        disp = frame.copy()
        faces_now = det_faces[0] or []

        face_found    = False
        face_quality_ok = False
        quality_msg   = ""

        # Minimum face size: must cover at least 6% of frame area OR 80×80 px
        fh_fr, fw_fr  = frame.shape[:2]
        min_face_area = max(80*80, int(fw_fr * fh_fr * 0.06))

        for fd in faces_now[:1]:
            x1, y1, x2, y2 = fd["bbox"]
            x1 = max(0, x1); y1 = max(0, y1)
            x2 = min(fw_fr, x2); y2 = min(fh_fr, y2)
            if x2 <= x1 or y2 <= y1:
                continue

            face_found  = True
            face_w      = x2 - x1
            face_h      = y2 - y1
            face_area   = face_w * face_h

            # Quality checks
            too_small   = face_area < min_face_area
            too_close   = face_w > int(fw_fr * 0.85)  # face fills >85% width
            out_of_frame= (x1 < 5 or y1 < 5 or x2 > fw_fr-5 or y2 > fh_fr-5)

            if too_small:
                quality_msg = f"Move closer — face too small ({face_w}x{face_h}px, need {int(min_face_area**0.5)}x{int(min_face_area**0.5)})"
                face_quality_ok = False
            elif too_close:
                quality_msg = "Move back slightly — face too close"
                face_quality_ok = False
            elif out_of_frame:
                quality_msg = "Centre your face in the frame"
                face_quality_ok = False
            else:
                face_quality_ok = True
                quality_msg = ""

            now   = time.time()
            ready = (now - last_cap) >= interval
            # Green = ready to capture, Blue = cooling down, Orange = quality issue
            if not face_quality_ok:
                color = (0, 140, 255)   # orange — quality not met
            elif ready:
                color = (0, 200, 60)    # green — capturing
            else:
                color = (26, 86, 219)   # blue — wait
            thickness = 3 if (ready and face_quality_ok) else 2
            cv2.rectangle(disp, (x1,y1), (x2,y2), color, thickness)

            # Corner accent lines
            llen = 20
            for (cx,cy,dx,dy) in [(x1,y1,1,1),(x2,y1,-1,1),(x1,y2,1,-1),(x2,y2,-1,-1)]:
                cv2.line(disp,(cx,cy),(cx+dx*llen,cy),color,3)
                cv2.line(disp,(cx,cy),(cx,cy+dy*llen),color,3)

            # Face size indicator (bottom-left of box)
            cv2.putText(disp, f"{face_w}x{face_h}", (x1, y2+14),
                        font, 0.4, color, 1)

            if ready and face_quality_ok and photos_saved < target:
                crop = frame[y1:y2, x1:x2]
                if crop.size > 0:
                    save_path = os.path.join(photo_dir, f"{photos_saved+1}.jpg")
                    cv2.imwrite(save_path, crop)
                    emb = fd.get("embedding")
                    if emb is not None:
                        embeddings.append(emb)
                    photos_saved += 1
                    last_cap = now
                    if status_cb:
                        status_cb(
                            f"Captured {photos_saved}/{target} for {name}  "
                            f"({len(embeddings)} face profile(s) so far)")

        # Progress bar at bottom
        bar_w = frame.shape[1]
        prog  = int((photos_saved / target) * bar_w)
        cv2.rectangle(disp, (0, frame.shape[0]-8), (bar_w, frame.shape[0]), (30,30,30), -1)
        if prog > 0:
            cv2.rectangle(disp, (0, frame.shape[0]-8), (prog, frame.shape[0]), (0,200,60), -1)

        # Top HUD
        cv2.rectangle(disp, (0,0), (frame.shape[1], 54), (13,40,71), -1)
        cv2.putText(disp,
            f"FaceTrack Pro — Register: {name}   [{photos_saved}/{target} photos]   Q / ESC = cancel",
            (8,18), font, 0.52, (180,210,255), 1)

        if not face_found:
            msg    = "No face detected — look directly at the camera & improve lighting"
            color2 = (60, 120, 255)
        elif not face_quality_ok:
            msg    = quality_msg
            color2 = (0, 140, 255)
        elif (time.time() - last_cap) < interval:
            rem    = interval - (time.time() - last_cap)
            msg    = f"Hold still — next photo in {rem:.1f}s   (vary angle slightly between shots)"
            color2 = (0, 200, 200)
        else:
            msg    = "Face clear & well-positioned — capturing now!"
            color2 = (0, 230, 80)

        cv2.putText(disp, msg, (8, 42), font, 0.46, color2, 1)

        cv2.imshow(_wname, disp)
        key = cv2.waitKey(30) & 0xFF
        if key in (ord("q"), 27):   # Q or Escape
            cancelled[0] = True
            break

    cancelled[0] = True
    cam.release()
    cv2.destroyAllWindows()

    if photos_saved == 0:
        return False, 0, 0, (
            "No face detected.\n"
            "Tips:\n"
            "  • Ensure good lighting (face should be well lit)\n"
            "  • Move closer to the camera\n"
            "  • Remove glasses if possible for first registration")

    if not embeddings:
        return False, photos_saved, 0, (
            "Photos captured but face profiles could not be computed.\n"
            "Ensure InsightFace is correctly installed.")

    enc_save(str(sid), embeddings)
    return True, photos_saved, len(embeddings), ""


def _settings_photos() -> str:
    try:
        from storage import setting
        return setting("photos", str(PHOTOS_PER_STUDENT))
    except Exception:
        return str(PHOTOS_PER_STUDENT)

def _settings_interval() -> str:
    return str(PHOTO_INTERVAL_SEC)


# ══════════════════════════════════════════════════════════════════
#  REBUILD  —  recompute embeddings from saved photos
# ══════════════════════════════════════════════════════════════════

def rebuild_embeddings(students: list, status_cb=None) -> tuple:
    """
    Re-derive embeddings from existing registration photos.
    Returns (ok_count, fail_list).
    """
    if not model_ready():
        return 0, ["Model not loaded"]

    ok = 0; fail = []
    for s in students:
        sid   = s["ID"]; name = s["Name"]
        pdir  = os.path.join(DIR_PHOTOS, sid)
        if not os.path.isdir(pdir):
            fail.append(f"{name} — no photos found"); continue

        embs = []
        for fn in sorted(os.listdir(pdir)):
            if not fn.lower().endswith((".jpg",".jpeg",".png")):
                continue
            img = cv2.imread(os.path.join(pdir, fn))
            if img is None:
                continue
            faces = detect_faces(img)
            if faces:
                embs.append(faces[0]["embedding"])

        if embs:
            enc_save(sid, embs); ok += 1
            if status_cb:
                status_cb(f"Rebuilt {name} — {len(embs)} profile(s)")
        else:
            fail.append(f"{name} — no face in saved photos")

    return ok, fail
