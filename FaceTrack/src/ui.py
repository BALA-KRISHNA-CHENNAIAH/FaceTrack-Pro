"""
ui.py — FaceTrack — All window / widget building.
Called from app.py; never run directly.
"""
import sys, os
_src = os.path.dirname(os.path.abspath(__file__))
if _src not in sys.path: sys.path.insert(0, _src)
if __name__ == '__main__': sys.exit(1)

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime

from config  import *
import storage  as db
import theme    as th
import widgets  as W


# ──────────────────────────────────────────────────────────────────
#  LOGIN WINDOW
# ──────────────────────────────────────────────────────────────────

def show_login(check_pw_fn) -> tuple:
    """Returns (success: bool, username: str)."""
    win = tk.Tk()
    win.title(APP_NAME)
    win.geometry("400x480")
    win.resizable(False, False)
    win.configure(bg=th.T["page"])
    win.eval("tk::PlaceWindow . center")

    # Top stripe
    tk.Frame(win, bg=th.T["accent"], height=3).pack(fill="x")

    # Header
    hdr = tk.Frame(win, bg=th.T["nav"], height=150)
    hdr.pack(fill="x"); hdr.pack_propagate(False)
    inner = tk.Frame(hdr, bg=th.T["nav"])
    inner.place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(inner, text="◈", fg=th.T["accent"], bg=th.T["nav"],
             font=("Segoe UI", 28, "bold")).pack()
    tk.Label(inner, text=APP_NAME, fg="white", bg=th.T["nav"],
             font=th.F["app_title"]).pack()
    tk.Label(inner, text=APP_SUBTITLE, fg=th.T["nav_sub"], bg=th.T["nav"],
             font=th.F["sm"]).pack(pady=(2, 0))

    # Body
    body = tk.Frame(win, bg=th.T["card"], padx=40, pady=28)
    body.pack(fill="both", expand=True)

    tk.Label(body, text="SIGN IN", fg=th.T["muted"],
             bg=th.T["card"], font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 14))

    tk.Label(body, text="USERNAME", fg=th.T["muted"],
             bg=th.T["card"], font=th.F["label"]).pack(anchor="w")
    u_e = W.entry(body, val="admin")

    tk.Label(body, text="PASSWORD", fg=th.T["muted"],
             bg=th.T["card"], font=th.F["label"]).pack(anchor="w")
    p_e = W.entry(body, show="*")

    err = tk.Label(body, text="", fg=th.T["red"], bg=th.T["card"], font=th.F["sm"])
    err.pack(pady=(0, 4))

    result = [False, ""]

    def attempt(event=None):
        u = u_e.get().strip(); p = p_e.get().strip()
        if not u or not p:
            err.configure(text="Enter username and password."); return
        if u == "admin" and check_pw_fn(p):
            result[0] = True; result[1] = u; win.destroy()
        else:
            err.configure(text="Incorrect credentials.")

    p_e.bind("<Return>", attempt)
    u_e.bind("<Return>", lambda e: p_e.focus())

    btn_outer = tk.Frame(body, bg=th.T["accent"], pady=1, padx=1)
    btn_outer.pack(fill="x", pady=(4, 0))
    tk.Button(btn_outer, text="SIGN IN", command=attempt,
              fg="white", bg=th.T["accent"], activebackground=th.T["accent2"],
              relief="flat", font=("Segoe UI", 11, "bold"),
              cursor="hand2", pady=11).pack(fill="x")

    win.mainloop()
    return result[0], result[1]


# ──────────────────────────────────────────────────────────────────
#  MAIN WINDOW BUILDER
# ──────────────────────────────────────────────────────────────────

def build_main_window(app):
    """
    Build the entire main window.
    `app` is the AppState object from app.py with callback methods.
    Returns the Tk window.
    """
    A = app
    win = tk.Tk()
    win.geometry("1360x820")
    win.minsize(1100, 660)
    win.title(APP_NAME)
    win.configure(bg=th.T["page"])
    th.apply_ttk_styles()
    A.window = win
    A.views  = {}
    A.nav_btns = {}

    # ══ TOP BAR ═══════════════════════════════════════════════════
    topbar = tk.Frame(win, bg=th.T["nav"], height=62)
    topbar.pack(fill="x"); topbar.pack_propagate(False)

    # Left: logo
    logo_f = tk.Frame(topbar, bg=th.T["nav"])
    logo_f.pack(side="left", padx=(16, 0), pady=4)
    tk.Label(logo_f, text="◈", fg=th.T["accent"], bg=th.T["nav"],
             font=("Segoe UI", 16, "bold")).pack(side="left", padx=(0, 8))
    ttl = tk.Frame(logo_f, bg=th.T["nav"]); ttl.pack(side="left")
    tk.Label(ttl, text=APP_NAME, fg="white", bg=th.T["nav"],
             font=("Segoe UI", 13, "bold")).pack(anchor="w")
    tk.Label(ttl, text=APP_SUBTITLE, fg=th.T["nav_sub"], bg=th.T["nav"],
             font=("Segoe UI", 9)).pack(anchor="w")

    # Center: active period
    ctr = tk.Frame(topbar, bg=th.T["nav"]); ctr.pack(side="left", expand=True)
    A.period_lbl = tk.Label(ctr, text="—", fg=th.T["muted"],
                             bg=th.T["nav"], font=("Segoe UI", 10, "bold"))
    A.period_lbl.pack()

    # Right: cam dot, clock, theme toggle
    right_f = tk.Frame(topbar, bg=th.T["nav"]); right_f.pack(side="right", padx=14, pady=8)

    # Theme button
    theme_btn = tk.Label(right_f, text=f"◑  {th.name().title()}",
                          fg=th.T["nav_sub"], bg=th.T["nav"],
                          font=("Segoe UI", 9), cursor="hand2")
    theme_btn.pack(side="right", padx=(10, 0))
    theme_btn.bind("<Button-1>", lambda e: A.cycle_theme())

    A.cam_dot = tk.Label(right_f, text="⬤  OFFLINE", fg=th.T["cam_offline"],
                          bg=th.T["nav"], font=("Segoe UI", 9, "bold"))
    A.cam_dot.pack(side="right", padx=(10, 0))
    A.clock_lbl = tk.Label(right_f, text="", fg="white", bg=th.T["nav"],
                            font=th.F["clock"])
    A.clock_lbl.pack(side="right")
    tk.Label(right_f, text=datetime.datetime.now().strftime("%a %d %b %Y  "),
             fg=th.T["nav_sub"], bg=th.T["nav"], font=th.F["body"]).pack(side="right")

    tk.Frame(win, bg=th.T["accent"], height=2).pack(fill="x")

    # ══ LAYOUT ════════════════════════════════════════════════════
    layout = tk.Frame(win, bg=th.T["page"]); layout.pack(fill="both", expand=True)

    # ── SIDEBAR ───────────────────────────────────────────────────
    sidebar = tk.Frame(layout, bg=th.T["sidebar"], width=200)
    sidebar.pack(side="left", fill="y"); sidebar.pack_propagate(False)

    def sb_sect(text):
        tk.Label(sidebar, text=text, fg=th.T["sidebar_text"],
                 bg=th.T["sidebar"], font=("Segoe UI", 7, "bold"),
                 anchor="w", padx=18).pack(fill="x", pady=(12, 2))

    def sb_sep():
        tk.Frame(sidebar, bg=th.T["border"], height=1).pack(fill="x", padx=14, pady=5)

    def sb_btn(icon, label, key, modal_fn=None):
        def _cmd():
            if modal_fn:
                # Highlight briefly then call modal
                for n, b in A.nav_btns.items():
                    b.configure(bg=th.T["sidebar"], fg=th.T["sidebar_text"])
                A.nav_btns[key].configure(bg=th.T["sidebar_sel_bg"], fg=th.T["nav_sub"])
                win.after(50, modal_fn)
            else:
                _show_view(key)
        b = tk.Button(sidebar, text=f"  {icon}  {label}", command=_cmd,
                      fg=th.T["sidebar_text"], bg=th.T["sidebar"],
                      activebackground=th.T["sidebar_sel_bg"],
                      activeforeground=th.T["nav_sub"],
                      relief="flat", font=th.F["nav_item"],
                      cursor="hand2", pady=8, anchor="w", padx=10)
        b.pack(fill="x", pady=1)
        A.nav_btns[key] = b
        return b

    sb_sect("MAIN")
    sb_btn("⬛", "Dashboard",   "dashboard")
    sb_btn("👤", "Students",    "students")
    sb_btn("📅", "Timetable",   "timetable")
    sb_sep()
    sb_sect("REPORTS")
    sb_btn("📊", "Analytics",   "analytics",   lambda: _show_analytics(A))
    sb_btn("🗓", "Holidays",    "holidays_v",  lambda: _show_holidays(A))
    sb_btn("❓", "Unknown Faces","gallery_v",  lambda: _show_gallery(A))
    sb_btn("📋", "Audit Log",   "audit_v",     lambda: _show_audit(A))
    sb_sep()
    sb_sect("SYSTEM")
    sb_btn("⚙", "Settings",    "settings_v",  lambda: _show_settings(A))
    sb_btn("💾", "Backup",      "backup_v",    lambda: _show_backup(A))
    sb_btn("ℹ", "About",       "about_v",     lambda: _show_about(A))
    sb_sep()
    tk.Button(sidebar, text="  ◑  Cycle Theme", command=lambda: A.cycle_theme(),
              fg=th.T["cyan"], bg=th.T["sidebar"],
              activebackground=th.T["sidebar_sel_bg"],
              relief="flat", font=th.F["nav_item"],
              cursor="hand2", pady=8, anchor="w", padx=10).pack(fill="x", pady=1)
    tk.Button(sidebar, text="  ⎋  Exit", command=A.safe_quit,
              fg=th.T["red"], bg=th.T["sidebar"],
              activebackground=th.T["red_bg"],
              relief="flat", font=th.F["nav_item"],
              cursor="hand2", pady=8, anchor="w", padx=10).pack(fill="x", pady=1)

    # ── CONTENT AREA ──────────────────────────────────────────────
    content = tk.Frame(layout, bg=th.T["page"]); content.pack(side="left", fill="both", expand=True)

    def _show_view(name):
        for _, (f, _) in A.views.items(): f.pack_forget()
        if name in A.views: A.views[name][0].pack(fill="both", expand=True)
        A.active_view = name
        for n, b in A.nav_btns.items():
            b.configure(bg=th.T["sidebar_sel_bg"] if n==name else th.T["sidebar"],
                        fg=th.T["nav_sub"] if n==name else th.T["sidebar_text"])

    A.show_view = _show_view  # expose to app

    # Create dummy frames for modal views
    for key in ["analytics","holidays_v","gallery_v","audit_v","settings_v","backup_v","about_v"]:
        A.views[key] = (tk.Frame(content, bg=th.T["page"]), {})

    # ══ DASHBOARD ═════════════════════════════════════════════════
    dash_f = tk.Frame(content, bg=th.T["page"])
    _build_dashboard(A, dash_f)
    A.views["dashboard"] = (dash_f, {})

    # ══ STUDENTS ══════════════════════════════════════════════════
    stud_f = tk.Frame(content, bg=th.T["page"])
    refs = _build_students(A, stud_f)
    A.views["students"] = (stud_f, refs)

    # ══ TIMETABLE ═════════════════════════════════════════════════
    tt_f = tk.Frame(content, bg=th.T["page"])
    _build_timetable(A, tt_f)
    A.views["timetable"] = (tt_f, {})

    # ── STATUS BAR ────────────────────────────────────────────────
    sbar = tk.Frame(win, bg=th.T["card2"], height=24)
    sbar.pack(fill="x", side="bottom"); sbar.pack_propagate(False)
    tk.Label(sbar, text="⬤ ", fg=th.T["green"],
             bg=th.T["card2"], font=("Segoe UI", 7)).pack(side="left", padx=(10,0), pady=4)
    A.status_lbl = tk.Label(sbar, text="System ready",
                             fg=th.T["text2"], bg=th.T["card2"], font=th.F["xs"])
    A.status_lbl.pack(side="left", pady=4)
    tk.Label(sbar, text=APP_NAME, fg=th.T["muted"],
             bg=th.T["card2"], font=th.F["xs"]).pack(side="right", padx=12, pady=4)

    _show_view("dashboard")
    return win


# ──────────────────────────────────────────────────────────────────
#  DASHBOARD
# ──────────────────────────────────────────────────────────────────

def _build_dashboard(A, parent):
    # Stats (3 cards: registered, present, late)
    stats_row = tk.Frame(parent, bg=th.T["page"])
    stats_row.pack(fill="x", padx=14, pady=(10, 6))
    stats_row.columnconfigure((0,1,2), weight=1)

    def make_stat(col, icon, label, color):
        c = tk.Frame(stats_row, bg=th.T["card"], padx=16, pady=12)
        c.grid(row=0, column=col, sticky="nsew", padx=(0 if col==0 else 7, 0))
        top = tk.Frame(c, bg=th.T["card"]); top.pack(fill="x")
        tk.Label(top, text=icon, fg=color, bg=th.T["card"],
                 font=("Segoe UI", 14)).pack(side="left")
        tk.Label(top, text=label, fg=th.T["muted"], bg=th.T["card"],
                 font=("Segoe UI", 7, "bold")).pack(side="right")
        val = tk.Label(c, text="0", fg=th.T["text"], bg=th.T["card"],
                       font=("Segoe UI", 28, "bold"))
        val.pack(anchor="w", pady=(2, 0))
        tk.Frame(c, bg=color, height=2).pack(fill="x", pady=(5, 0))
        return val

    A.v_reg  = make_stat(0, "◉", "REGISTERED",    th.T["accent"])
    A.v_att  = make_stat(1, "✓", "PRESENT TODAY", th.T["green"])
    A.v_late = make_stat(2, "⏱", "LATE TODAY",    th.T["orange"])

    # Warning banner — shown when students exist but face embeddings are missing
    warn_f = tk.Frame(parent, bg=th.T["orange"], pady=0)
    A.face_warn_lbl = tk.Label(warn_f,
        text="", fg=th.T["orange"], bg="#3a2200",
        font=("Segoe UI", 9, "bold"), anchor="w", padx=14, pady=6,
        cursor="hand2")
    A.face_warn_lbl.pack(fill="x")
    A.face_warn_lbl.bind("<Button-1>", lambda e: _show_settings(A, tab="facedata"))
    warn_f.pack(fill="x", padx=14, pady=(0, 4))
    warn_f.pack_forget()  # hidden until refresh_stats decides to show it

    # Mid row: camera + period
    mid = tk.Frame(parent, bg=th.T["page"])
    mid.pack(fill="x", padx=14, pady=(0, 6))
    mid.columnconfigure(0, weight=1); mid.columnconfigure(1, weight=1)

    # Camera card
    cam_c = tk.Frame(mid, bg=th.T["card"], padx=16, pady=14)
    cam_c.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
    tk.Label(cam_c, text="Attendance Camera", fg=th.T["text"],
             bg=th.T["card"], font=th.F["h2"]).pack(anchor="w", pady=(0, 10))

    def _toggle():
        A.toggle_auto()
        if A.g_auto:
            A.cam_btn.configure(text="  ■  Stop Camera", bg=th.T["red"],
                                activebackground=th.T["red"])
        else:
            A.cam_btn.configure(text="  ▶  Start Attendance Camera", bg=th.T["green"],
                                activebackground=th.T["green"])

    A.cam_btn = tk.Button(cam_c, text="  ▶  Start Attendance Camera",
                           command=_toggle, fg="white", bg=th.T["green"],
                           activebackground=th.T["green"],
                           relief="flat", font=("Segoe UI", 11, "bold"),
                           cursor="hand2", pady=11)
    A.cam_btn.pack(fill="x")
    tk.Label(cam_c, text="Face recognition camera. Press Q inside camera to stop.",
             fg=th.T["muted"], bg=th.T["card"], font=th.F["xs"],
             justify="left").pack(anchor="w", pady=(8, 0))

    # Period card
    per_c = tk.Frame(mid, bg=th.T["card"], padx=16, pady=14)
    per_c.grid(row=0, column=1, sticky="nsew")
    tk.Label(per_c, text="Current Period", fg=th.T["text"],
             bg=th.T["card"], font=th.F["h2"]).pack(anchor="w", pady=(0, 6))
    A.period_subj_lbl = tk.Label(per_c, text="—", fg=th.T["muted"],
                                  bg=th.T["card"], font=("Segoe UI", 20, "bold"))
    A.period_subj_lbl.pack(anchor="w")
    A.period_time_lbl = tk.Label(per_c, text="No periods scheduled today",
                                  fg=th.T["muted"], bg=th.T["card"], font=th.F["sm"])
    A.period_time_lbl.pack(anchor="w", pady=(4, 0))

    def _refresh_period_card():
        try:
            p = db.current_active_period()
            if p:
                A.period_subj_lbl.configure(text=p.get("Subject","—"), fg=th.T["green"])
                A.period_time_lbl.configure(
                    text=f"{p.get('StartTime','')} – {p.get('EndTime','')}  ●  Attendance Open",
                    fg=th.T["green"])
            else:
                nxt, nxt_t = db.next_upcoming_period()
                if nxt:
                    mins = max(0,int((nxt_t-datetime.datetime.now()).total_seconds()/60))
                    A.period_subj_lbl.configure(text=nxt.get("Subject","—"), fg=th.T["muted"])
                    A.period_time_lbl.configure(
                        text=f"Next in {mins} min  |  {nxt.get('StartTime','')}",
                        fg=th.T["orange"])
                else:
                    A.period_subj_lbl.configure(text="—", fg=th.T["muted"])
                    A.period_time_lbl.configure(text="No periods scheduled today", fg=th.T["muted"])
        except Exception: pass
        try: A.window.after(30000, _refresh_period_card)
        except Exception: pass

    _refresh_period_card()

    # Log
    log_c = tk.Frame(parent, bg=th.T["card"], padx=14, pady=10)
    log_c.pack(fill="both", expand=True, padx=14, pady=(0, 10))
    log_c.columnconfigure(0, weight=1); log_c.rowconfigure(1, weight=1)

    lh = tk.Frame(log_c, bg=th.T["card"]); lh.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    tk.Label(lh, text="Today's Attendance", fg=th.T["text"],
             bg=th.T["card"], font=th.F["h2"]).pack(side="left")
    tk.Button(lh, text="Refresh",
              command=lambda: [A.reload_log(), A.refresh_stats()],
              fg=th.T["text2"], bg=th.T["card2"], activebackground=th.T["hover"],
              relief="flat", font=th.F["xs"], cursor="hand2", padx=8, pady=4).pack(side="right", padx=(4,0))
    tk.Button(lh, text="📋  View Day / Subject Attendance",
              command=lambda: _show_attendance_viewer(A),
              fg="white", bg=th.T["accent"], activebackground=th.T["accent2"],
              relief="flat", font=th.F["xs"], cursor="hand2", padx=10, pady=4).pack(side="right", padx=(0,6))

    A.cls_var = tk.StringVar(value="All")
    cf = tk.Frame(lh, bg=th.T["accent"], pady=1, padx=1); cf.pack(side="right", padx=(0, 4))
    A.cls_btn = tk.Menubutton(cf, textvariable=A.cls_var, fg=th.T["text"],
                               bg=th.T["card2"], activeforeground=th.T["text"],
                               activebackground=th.T["hover"],
                               font=th.F["sm"], relief="flat", width=12,
                               pady=3, padx=8, indicatoron=True, cursor="hand2")
    A.cls_btn.pack()
    tk.Label(lh, text="Filter:", fg=th.T["muted"], bg=th.T["card"],
             font=th.F["xs"]).pack(side="right", padx=(0, 4))

    A.tv_log, ltf = W.treeview(log_c,
        cols=("name","cls","time","subject","note"),
        heads=("  Name","Class","Time","Subject","Note"),
        widths=[220,110,95,170,130], stretch_col="name", height=9)
    ltf.grid(row=1, column=0, sticky="nsew")


# ──────────────────────────────────────────────────────────────────
#  STUDENTS
# ──────────────────────────────────────────────────────────────────

def _build_students(A, parent):
    # Header bar
    sh = tk.Frame(parent, bg=th.T["card"], padx=18, pady=10)
    sh.pack(fill="x", pady=(0, 1))
    tk.Label(sh, text="Student Management", fg=th.T["text"],
             bg=th.T["card"], font=th.F["h1"]).pack(side="left")
    btn_r = tk.Frame(sh, bg=th.T["card"]); btn_r.pack(side="right")
    for txt, cmd, col in [
        ("View All", lambda: _show_all_students(A), th.T["accent"]),
        ("Edit",     lambda: _show_edit_student(A), th.T["cyan"]),
        ("Remove",   lambda: _show_deregister(A),   th.T["red"]),
    ]:
        tk.Button(btn_r, text=txt, command=cmd, fg="white", bg=col,
                  activebackground=col, relief="flat", font=th.F["sm"],
                  cursor="hand2", padx=12, pady=6).pack(side="left", padx=(0,4))

    # Two columns
    cols = tk.Frame(parent, bg=th.T["page"])
    cols.pack(fill="both", expand=True, padx=14, pady=10)
    cols.columnconfigure(0, weight=1); cols.columnconfigure(1, weight=2)
    cols.rowconfigure(0, weight=1)

    # Left: registration form
    reg_outer, reg_inner = W.scrollable_frame(cols, bg=th.T["card"])
    reg_outer.configure(bg=th.T["card"])
    reg_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    reg_card = tk.Frame(reg_inner, bg=th.T["card"], padx=18, pady=14)
    reg_card.pack(fill="x")

    tk.Frame(reg_card, bg=th.T["accent"], height=2).pack(fill="x", pady=(0, 10))
    tk.Label(reg_card, text="Register Student", fg=th.T["text"],
             bg=th.T["card"], font=th.F["h2"]).pack(anchor="w")
    tk.Label(reg_card, text=f"Captures {db.setting('photos','5')} photos for face recognition",
             fg=th.T["muted"], bg=th.T["card"], font=th.F["xs"]).pack(anchor="w", pady=(2,10))

    ents = {}
    for lb, key, dflt in [
        ("STUDENT ID", "id", ""),
        ("FULL NAME",  "name", ""),
        ("CLASS",      "class", ""),
        ("DEPARTMENT", "dept", ""),
        ("ROLE",       "role", "Student"),
        ("EMAIL",      "email", ""),
        ("PHONE",      "phone", ""),
        ("ADDRESS",    "address", ""),
    ]:
        tk.Label(reg_card, text=lb, fg=th.T["muted"],
                 bg=th.T["card"], font=th.F["label"]).pack(anchor="w")
        e = W.entry(reg_card, val=dflt); ents[key] = e

    # Pre-fill ID
    ents["id"].delete(0,"end"); ents["id"].insert(0, db.next_student_id())

    bf = tk.Frame(reg_card, bg=th.T["card"]); bf.pack(fill="x", pady=(8, 0))
    W.btn_primary(bf, "  Register Student",
                  lambda: A.do_register(ents), pack=False).pack(
        side="left", fill="x", expand=True, padx=(0,6))
    tk.Button(bf, text="Clear",
              command=lambda: [
                  [e.delete(0,"end") for e in ents.values()],
                  ents["role"].insert(0,"Student"),
                  ents["id"].insert(0, db.next_student_id())
              ],
              fg=th.T["text2"], bg=th.T["card2"],
              activebackground=th.T["hover"],
              relief="flat", font=th.F["sm"],
              cursor="hand2", pady=9).pack(side="left")

    # Right: student list
    lcard = tk.Frame(cols, bg=th.T["card"], padx=14, pady=14)
    lcard.grid(row=0, column=1, sticky="nsew")
    lcard.columnconfigure(0, weight=1); lcard.rowconfigure(2, weight=1)

    tk.Label(lcard, text="Registered Students", fg=th.T["text"],
             bg=th.T["card"], font=th.F["h2"]).grid(row=0, column=0, sticky="w", pady=(0,8))
    sv = tk.StringVar()
    W.search_entry(lcard, sv).grid(row=1, column=0, sticky="ew", pady=(0,8))

    stv, stf = W.treeview(lcard,
        cols=("id","name","cls","dept","reg"),
        heads=("ID","  Name","Class","Department","Registered"),
        widths=[70,175,100,120,125], stretch_col="name", height=16)
    stf.grid(row=2, column=0, sticky="nsew")

    def populate(q=""):
        stv.delete(*stv.get_children())
        for s in db.students_all():
            if not q or q in s["Name"].lower() or q in s["ID"].lower():
                stv.insert("","end",values=(s["ID"],s["Name"],s.get("Class",""),
                                            s.get("Department",""),s.get("RegisteredOn","")))

    populate()
    sv.trace("w", lambda *_: populate(sv.get().lower().strip()))

    def refresh():
        populate(sv.get().lower().strip())
        ents["id"].delete(0,"end"); ents["id"].insert(0, db.next_student_id())

    return {"refresh": refresh, "ents": ents}


# ──────────────────────────────────────────────────────────────────
#  TIMETABLE
# ──────────────────────────────────────────────────────────────────

def _build_timetable(A, parent):
    hdr = tk.Frame(parent, bg=th.T["card"], padx=18, pady=10)
    hdr.pack(fill="x", pady=(0,1))
    tk.Label(hdr, text="Timetable", fg=th.T["text"],
             bg=th.T["card"], font=th.F["h1"]).pack(side="left")
    tk.Label(hdr,
             text=f"Attendance opens {ATT_BUFFER_BEFORE} min before and closes {ATT_BUFFER_AFTER} min after period start",
             fg=th.T["muted"], bg=th.T["card"], font=th.F["xs"]).pack(side="right")

    content = tk.Frame(parent, bg=th.T["page"], padx=14, pady=10)
    content.pack(fill="both", expand=True)
    content.columnconfigure(0, weight=1); content.rowconfigure(1, weight=1)

    # Day selector
    day_frame = tk.Frame(content, bg=th.T["page"])
    day_frame.grid(row=0, column=0, sticky="ew", pady=(0,8))
    sel_day = tk.StringVar(value="Mon")
    day_btns = {}

    def select_day(d):
        sel_day.set(d)
        for dd, b in day_btns.items():
            b.configure(bg=th.T["accent"] if dd==d else th.T["card2"],
                        fg="white" if dd==d else th.T["text2"])
        reload_periods()

    for day in DAYS_OF_WEEK:
        b = tk.Button(day_frame, text=day,
                      bg=th.T["accent"] if day=="Mon" else th.T["card2"],
                      fg="white" if day=="Mon" else th.T["text2"],
                      relief="flat", font=th.F["sm"], cursor="hand2",
                      padx=14, pady=6, command=lambda d=day: select_day(d))
        b.pack(side="left", padx=(0,3)); day_btns[day] = b

    # Main area
    ma = tk.Frame(content, bg=th.T["page"]); ma.grid(row=1, column=0, sticky="nsew")
    ma.columnconfigure(0, weight=2); ma.columnconfigure(1, weight=1); ma.rowconfigure(0, weight=1)

    # Period list card
    lc = tk.Frame(ma, bg=th.T["card"], padx=12, pady=12)
    lc.grid(row=0, column=0, sticky="nsew", padx=(0,10))
    lc.columnconfigure(0, weight=1); lc.rowconfigure(1, weight=1)
    tk.Label(lc, text="Periods", fg=th.T["text"],
             bg=th.T["card"], font=th.F["h2"]).grid(row=0, column=0, sticky="w", pady=(0,8))

    tv, tf = W.treeview(lc,
        cols=("period","subject","start","end"),
        heads=("No.","Subject","Start","End"),
        widths=[50,220,90,90], stretch_col="subject", height=13)
    tf.grid(row=1, column=0, sticky="nsew")

    def reload_periods():
        tv.delete(*tv.get_children())
        for i, row in enumerate(db.timetable_for_day(sel_day.get())):
            tv.insert("","end", iid=str(i),
                      values=(row.get("Period",""), row.get("Subject",""),
                              row.get("StartTime",""), row.get("EndTime","")))

    reload_periods()

    def delete_period():
        sel = tv.selection()
        if not sel:
            messagebox.showwarning("Select Period","Select a period to delete.", parent=A.window); return
        day_rows = db.timetable_for_day(sel_day.get())
        idx_local = int(sel[0])
        if idx_local >= len(day_rows): return
        target = day_rows[idx_local]
        subject = target.get("Subject","")

        # Check if this subject still exists on any other day after deletion
        other_days = [r for r in db.timetable_all()
                      if r.get("Subject")==subject and not (
                          r.get("Day")==target.get("Day") and
                          r.get("StartTime")==target.get("StartTime"))]
        subject_disappears = len(other_days) == 0

        # Build confirmation message
        if subject_disappears:
            att_count = sum(
                1 for d in db.all_att_dates()
                for r in db.att_read(d) if r.get("Subject","")==subject)
            msg = (f"Delete '{subject}' on {sel_day.get()} "
                   f"({target.get('StartTime','')} - {target.get('EndTime','')})?\n\n"
                   f"This is the only period for '{subject}'.\n"
                   f"{att_count} attendance record(s) for this subject will also be permanently deleted.")
        else:
            msg = (f"Delete '{subject}' on {sel_day.get()} "
                   f"({target.get('StartTime','')} - {target.get('EndTime','')})?\n\n"
                   f"'{subject}' still exists on other day(s) -- attendance records will be kept.")

        if not messagebox.askyesno("Confirm Delete", msg, parent=A.window):
            return

        # Delete the timetable row
        all_rows = db.timetable_all()
        for gi, row in enumerate(all_rows):
            if (row.get("Day")==target.get("Day") and
                row.get("Subject")==target.get("Subject") and
                row.get("StartTime")==target.get("StartTime")):
                db.timetable_delete(gi); break

        # Purge attendance if subject no longer exists anywhere in timetable
        if subject_disappears and subject:
            deleted = db.remove_subject_from_attendance(subject)
            if deleted:
                W.toast(A.window, "Attendance Purged",
                        f"Removed {deleted} record(s) for '{subject}'")

        reload_periods(); A.update_period_display()
        A.reload_log(); A.refresh_stats()


    br = tk.Frame(lc, bg=th.T["card"]); br.grid(row=2, column=0, sticky="ew", pady=(8,0))
    tk.Button(br, text="  Delete Selected", command=delete_period,
              fg=th.T["red"], bg=th.T["card2"], activebackground=th.T["hover"],
              relief="flat", font=th.F["sm"], cursor="hand2", pady=7).pack(side="left")

    # Add period form card
    fc = tk.Frame(ma, bg=th.T["card"], padx=16, pady=16)
    fc.grid(row=0, column=1, sticky="nsew")
    tk.Label(fc, text="Add Period", fg=th.T["text"],
             bg=th.T["card"], font=th.F["h2"]).pack(anchor="w", pady=(0,10))

    form_e = {}
    for lb, key, dflt in [
        ("PERIOD NUMBER","period","1"),
        ("SUBJECT","subject",""),
        ("START (HH:MM)","start","09:00"),
        ("END (HH:MM)","end","10:00"),
    ]:
        tk.Label(fc, text=lb, fg=th.T["muted"],
                 bg=th.T["card"], font=th.F["label"]).pack(anchor="w", pady=(6,0))
        form_e[key] = W.entry(fc, val=dflt)

    def add_period():
        p   = form_e["period"].get().strip()
        sub = form_e["subject"].get().strip()
        st  = form_e["start"].get().strip()
        en  = form_e["end"].get().strip()
        if not sub:
            messagebox.showerror("Error","Subject name is required.",parent=A.window); return
        try:
            st_dt = datetime.datetime.strptime(st,"%H:%M")
            en_dt = datetime.datetime.strptime(en,"%H:%M")
        except ValueError:
            messagebox.showerror("Error","Time must be HH:MM (e.g. 09:30).",parent=A.window); return
        if en_dt <= st_dt:
            messagebox.showerror("Error",
                f"End time ({en}) must be after Start time ({st}).\n"
                "Use 24-hour format — e.g. 13:00 for 1 PM.",parent=A.window); return

        # Check overlap
        overlapping, overlap_subj = db.check_overlap(sel_day.get(), st, en)
        if overlapping:
            messagebox.showerror("Overlap",
                f"This period overlaps with '{overlap_subj}' on {sel_day.get()}.\n"
                "Please choose a different time.",parent=A.window); return

        db.timetable_add(sel_day.get(), p, sub, st, en)
        reload_periods(); A.update_period_display()
        form_e["subject"].delete(0,"end")
        try:
            pn = str(int(p)+1) if p.isdigit() else "1"
            form_e["period"].delete(0,"end"); form_e["period"].insert(0,pn)
        except Exception: pass
        W.toast(A.window,"Period Added",f"{sub} on {sel_day.get()}")

    W.btn_primary(fc,"  + Add Period",add_period)

    info = tk.Frame(fc, bg=th.T["card2"], padx=12, pady=10)
    info.pack(fill="x", pady=(14,0))
    tk.Label(info, text="Attendance Window", fg=th.T["cyan"],
             bg=th.T["card2"], font=th.F["label"]).pack(anchor="w")
    tk.Label(info,
             text=f"Opens {ATT_BUFFER_BEFORE} min before start.\nCloses {ATT_BUFFER_AFTER} min after start.",
             fg=th.T["muted"], bg=th.T["card2"], font=th.F["xs"],
             justify="left").pack(anchor="w",pady=(4,0))
    tk.Label(info,
             text="Overlapping periods are not allowed.",
             fg=th.T["muted"], bg=th.T["card2"], font=th.F["xs"]).pack(anchor="w",pady=(2,0))


# ──────────────────────────────────────────────────────────────────
#  MODAL: ANALYTICS
# ──────────────────────────────────────────────────────────────────

def _show_attendance_viewer(A):
    """Standalone Day-wise / Subject-wise present & absent viewer."""
    m = tk.Toplevel(A.window)
    m.geometry("1100x680"); m.minsize(860,520)
    m.resizable(True, True)
    m.title("FaceTrack Pro — Attendance Viewer")
    m.configure(bg=th.T["page"])
    m.transient(A.window); m.lift(); m.focus_force()
    m.columnconfigure(0, weight=1); m.rowconfigure(2, weight=1)

    # ── Header ────────────────────────────────────────────────────
    hdr = tk.Frame(m, bg=th.T["card"], height=52)
    hdr.grid(row=0, column=0, sticky="ew"); hdr.grid_propagate(False)
    tk.Label(hdr, text="  📋  Attendance Viewer",
             fg=th.T["text"], bg=th.T["card"], font=th.F["h1"]).pack(side="left", padx=14, pady=14)
    tk.Frame(m, bg=th.T["accent"], height=2).grid(row=1, column=0, sticky="ew")

    body = tk.Frame(m, bg=th.T["page"], padx=12, pady=10)
    body.grid(row=2, column=0, sticky="nsew")
    body.columnconfigure(0, weight=1); body.rowconfigure(1, weight=1)

    # ── Toolbar ────────────────────────────────────────────────────
    tb = tk.Frame(body, bg=th.T["page"]); tb.grid(row=0, column=0, sticky="ew", pady=(0,8))

    # Helper: rebuild a dropdown in a frame
    def _dd(parent, var, opts, width=13, cmd=None):
        fr = tk.Frame(parent, bg=th.T["accent"], pady=1, padx=1)
        fr.pack(side="left", padx=(0,6))
        mb = tk.Menubutton(fr, textvariable=var, fg=th.T["text"], bg=th.T["card2"],
                           activeforeground=th.T["text"], activebackground=th.T["hover"],
                           font=th.F["sm"], relief="flat", width=width,
                           pady=3, padx=8, indicatoron=True, cursor="hand2")
        mb.pack()
        mn = tk.Menu(mb, tearoff=0, bg=th.T["card"], fg=th.T["text"],
                     activebackground=th.T["accent"], activeforeground="white",
                     font=th.F["sm"], relief="flat", bd=0)
        _cb = cmd if cmd else lambda: m.after(60, _refresh)
        for o in opts: mn.add_radiobutton(label=o, variable=var, value=o, command=_cb)
        mb.configure(menu=mn); return mb

    all_dates = db.all_att_dates()
    today_str = __import__("datetime").date.today().strftime("%d-%m-%Y")

    date_v  = tk.StringVar(value=today_str if today_str in all_dates else (all_dates[-1] if all_dates else ""))
    subj_v  = tk.StringVar(value="All Subjects")
    cls_v   = tk.StringVar(value="All")
    pa_v    = tk.StringVar(value="present")

    tk.Label(tb, text="Date:", fg=th.T["text2"], bg=th.T["page"], font=th.F["sm"]).pack(side="left", padx=(0,4))
    date_dd_frame = tk.Frame(tb, bg=th.T["page"]); date_dd_frame.pack(side="left", padx=(0,6))

    tk.Label(tb, text="Subject:", fg=th.T["text2"], bg=th.T["page"], font=th.F["sm"]).pack(side="left", padx=(0,4))
    subj_dd_frame = tk.Frame(tb, bg=th.T["page"]); subj_dd_frame.pack(side="left", padx=(0,6))

    tk.Label(tb, text="Class:", fg=th.T["text2"], bg=th.T["page"], font=th.F["sm"]).pack(side="left", padx=(0,4))
    _dd(tb, cls_v, ["All"] + db.class_list(), width=12)

    # Present / Absent toggle
    pa_frame = tk.Frame(tb, bg=th.T["page"]); pa_frame.pack(side="left", padx=(8,0))
    pa_btns  = {}
    def _set_pa(v):
        pa_v.set(v)
        for vv, b in pa_btns.items():
            b.configure(bg=th.T["green"] if vv=="present" else th.T["red"] if vv==v else th.T["card2"],
                        fg="white" if vv==v else th.T["text2"])
            if vv==v:
                b.configure(bg=th.T["green"] if v=="present" else th.T["red"])
        m.after(30, _refresh)
    for pv, pl in [("present","✓  Present"), ("absent","✗  Absent")]:
        pb = tk.Button(pa_frame, text=pl,
                       bg=th.T["green"] if pv=="present" else th.T["card2"],
                       fg="white" if pv=="present" else th.T["text2"],
                       relief="flat", font=th.F["sm"], cursor="hand2",
                       padx=10, pady=4, command=lambda v=pv: _set_pa(v))
        pb.pack(side="left", padx=(0,3)); pa_btns[pv] = pb

    # Summary label (right)
    sum_lbl = tk.Label(tb, text="", fg=th.T["muted"], bg=th.T["page"], font=th.F["xs"])
    sum_lbl.pack(side="right", padx=8)

    tk.Button(tb, text="↻  Refresh", command=lambda: _rebuild_dropdowns() or _refresh(),
              fg="white", bg=th.T["accent"], activebackground=th.T["accent2"],
              relief="flat", font=th.F["sm"], cursor="hand2",
              padx=10, pady=4).pack(side="right", padx=(0,6))

    # ── Content area ───────────────────────────────────────────────
    content = tk.Frame(body, bg=th.T["page"])
    content.grid(row=1, column=0, sticky="nsew")
    content.columnconfigure(0, weight=2); content.columnconfigure(1, weight=3)
    content.rowconfigure(0, weight=1)

    # Left: student list ──────────────────────────────────────────
    left = tk.Frame(content, bg=th.T["card"], padx=10, pady=10)
    left.grid(row=0, column=0, sticky="nsew", padx=(0,8))
    left.columnconfigure(0, weight=1); left.rowconfigure(1, weight=1)

    list_hdr = tk.Frame(left, bg=th.T["card"]); list_hdr.grid(row=0, column=0, sticky="ew", pady=(0,6))
    list_title = tk.Label(list_hdr, text="Students", fg=th.T["text"], bg=th.T["card"], font=th.F["h2"])
    list_title.pack(side="left")
    count_lbl = tk.Label(list_hdr, text="", fg=th.T["muted"], bg=th.T["card"], font=th.F["xs"])
    count_lbl.pack(side="right")

    tv, tf = W.treeview(left,
        cols=("id","name","cls","dept","info"),
        heads=("ID","  Name","Class","Dept","Time / Info"),
        widths=[55,160,90,90,130], stretch_col="name")
    tf.grid(row=1, column=0, sticky="nsew")

    # Right: summary chart ─────────────────────────────────────────
    right = tk.Frame(content, bg=th.T["card"], padx=12, pady=12)
    right.grid(row=0, column=1, sticky="nsew")
    right.columnconfigure(0, weight=1); right.rowconfigure(1, weight=1)
    chart_lbl = tk.Label(right, text="Summary", fg=th.T["text"], bg=th.T["card"], font=th.F["h2"])
    chart_lbl.grid(row=0, column=0, sticky="w", pady=(0,8))
    canvas = tk.Canvas(right, bg=th.T["card2"], highlightthickness=0)
    canvas.grid(row=1, column=0, sticky="nsew")

    _cache = {"present": [], "absent": []}

    def _draw_chart(plist, alist):
        canvas.delete("all")
        m.update_idletasks()
        cw = canvas.winfo_width(); ch = canvas.winfo_height()
        if cw < 10: return
        total = len(plist) + len(alist)
        if total == 0:
            canvas.create_text(cw//2, ch//2, text="No data", fill=th.T["muted"], font=("Segoe UI",11))
            return
        pr_pct = len(plist)/total*100
        ab_pct = 100 - pr_pct
        bx = 90; bh = 52; gap = 18; bw_max = max(cw - bx - 70, 80)
        cy = ch // 3

        for i, (label, count, pct, col) in enumerate([
            ("Present", len(plist), pr_pct, th.T["green"]),
            ("Absent",  len(alist), ab_pct, th.T["red"]),
        ]):
            by = cy + i*(bh + gap)
            canvas.create_text(bx-10, by+bh//2, text=label, fill=col,
                               font=("Segoe UI",10,"bold"), anchor="e")
            bw = int(pct/100*bw_max)
            if bw > 0:
                canvas.create_rectangle(bx, by, bx+bw, by+bh, fill=col, outline="")
            txt = f"{count}  ({pct:.1f}%)"
            canvas.create_text(bx+bw+8, by+bh//2, text=txt,
                               fill=th.T["text"], font=("Segoe UI",9), anchor="w")

        canvas.create_text(cw//2, cy+2*(bh+gap)+16,
                           text=f"Total enrolled: {total}",
                           fill=th.T["muted"], font=("Segoe UI",10))

    def _populate_list(plist, alist):
        _cache["present"] = plist; _cache["absent"] = alist
        which = pa_v.get()
        items = plist if which == "present" else alist
        tv.delete(*tv.get_children())
        icon = "✓" if which == "present" else "✗"
        count_lbl.configure(text=f"{icon} {len(items)} shown   |   P:{len(plist)}  A:{len(alist)}")
        for r in items:
            if which == "present":
                info = r.get("subjects","")
                time_ = r.get("time","")
                late_tag = " ⏱" if r.get("is_late") else ""
                info_str = f"{time_}  {info}{late_tag}".strip()
            else:
                info_str = "—"
            tv.insert("","end", values=(r["id"],r["name"],r["class"],r["dept"],info_str))

    def _refresh():
        date = date_v.get()
        if not date:
            sum_lbl.configure(text="No attendance dates found.")
            tv.delete(*tv.get_children()); canvas.delete("all"); return

        subj = subj_v.get()
        subj_arg = "All" if subj in ("All Subjects","") else subj
        cls_arg  = cls_v.get()

        plist, alist = db.get_day_attendance_detail(
            date, subject_filter=subj_arg, cls_filter=cls_arg)

        # Update panel title
        title = f"{'Present' if pa_v.get()=='present' else 'Absent'} — {date}"
        if subj_arg != "All": title += f"  |  {subj}"
        list_title.configure(text=title)
        chart_lbl.configure(text=f"Summary — {date}")

        sum_lbl.configure(
            text=f"Date: {date}  |  Present: {len(plist)}  |  Absent: {len(alist)}"
                 + (f"  |  {subj}" if subj_arg != "All" else ""))

        _populate_list(plist, alist)
        m.after(80, lambda: _draw_chart(_cache["present"], _cache["absent"]))

    def _rebuild_dropdowns():
        dates = db.all_att_dates()
        if not date_v.get() or date_v.get() not in dates:
            date_v.set(dates[-1] if dates else "")
        for w in date_dd_frame.winfo_children(): w.destroy()
        fr2 = tk.Frame(date_dd_frame, bg=th.T["accent"], pady=1, padx=1); fr2.pack()
        mb2 = tk.Menubutton(fr2, textvariable=date_v, fg=th.T["text"], bg=th.T["card2"],
                            activeforeground=th.T["text"], activebackground=th.T["hover"],
                            font=th.F["sm"], relief="flat", width=13,
                            pady=3, padx=8, indicatoron=True, cursor="hand2"); mb2.pack()
        mn2 = tk.Menu(mb2, tearoff=0, bg=th.T["card"], fg=th.T["text"],
                      activebackground=th.T["accent"], activeforeground="white",
                      font=th.F["sm"], relief="flat", bd=0)
        for d in dates: mn2.add_radiobutton(label=d, variable=date_v, value=d,
                                             command=lambda: m.after(60, _refresh))
        mb2.configure(menu=mn2)

        subjects = ["All Subjects"] + db.subject_list()
        if subj_v.get() not in subjects: subj_v.set("All Subjects")
        for w in subj_dd_frame.winfo_children(): w.destroy()
        fr3 = tk.Frame(subj_dd_frame, bg=th.T["accent"], pady=1, padx=1); fr3.pack()
        mb3 = tk.Menubutton(fr3, textvariable=subj_v, fg=th.T["text"], bg=th.T["card2"],
                            activeforeground=th.T["text"], activebackground=th.T["hover"],
                            font=th.F["sm"], relief="flat", width=14,
                            pady=3, padx=8, indicatoron=True, cursor="hand2"); mb3.pack()
        mn3 = tk.Menu(mb3, tearoff=0, bg=th.T["card"], fg=th.T["text"],
                      activebackground=th.T["accent"], activeforeground="white",
                      font=th.F["sm"], relief="flat", bd=0)
        for s in subjects: mn3.add_radiobutton(label=s, variable=subj_v, value=s,
                                                command=lambda: m.after(60, _refresh))
        mb3.configure(menu=mn3)

    _rebuild_dropdowns()
    _refresh()
    canvas.bind("<Configure>", lambda e: m.after(80,
        lambda: _draw_chart(_cache["present"], _cache["absent"])))

    # Close button
    bf = tk.Frame(body, bg=th.T["page"]); bf.grid(row=2, column=0, sticky="e", pady=(8,0))
    tk.Button(bf, text="Close", command=m.destroy,
              fg=th.T["text2"], bg=th.T["card2"], activebackground=th.T["hover"],
              relief="flat", font=th.F["body"], cursor="hand2", pady=8).pack()


def _show_analytics(A):
    m = tk.Toplevel(A.window)
    m.geometry("1240x760"); m.minsize(960,580)
    m.resizable(True,True); m.title("FaceTrack Pro — Analytics")
    m.configure(bg=th.T["page"]); m.grab_set()
    m.columnconfigure(0,weight=1); m.rowconfigure(2,weight=1)

    hdr=tk.Frame(m,bg=th.T["card"],height=52)
    hdr.grid(row=0,column=0,sticky="ew"); hdr.grid_propagate(False)
    tk.Label(hdr,text="  Attendance Analytics",fg=th.T["text"],
             bg=th.T["card"],font=th.F["h1"]).pack(side="left",padx=14,pady=14)
    tk.Frame(m,bg=th.T["accent"],height=2).grid(row=1,column=0,sticky="ew")

    body=tk.Frame(m,bg=th.T["page"],padx=14,pady=12)
    body.grid(row=2,column=0,sticky="nsew")
    body.columnconfigure(0,weight=1); body.rowconfigure(1,weight=1)

    # ── TOP TOOLBAR ────────────────────────────────────────────────
    tb=tk.Frame(body,bg=th.T["page"]); tb.grid(row=0,column=0,sticky="ew",pady=(0,8))
    cls_v=tk.StringVar(value="All"); srt_v=tk.StringVar(value="Name")
    mode_v=tk.StringVar(value="overall"); subj_v=tk.StringVar(value="All Subjects")
    day_v=tk.StringVar(value=""); dsubj_v=tk.StringVar(value="All Subjects")
    sw_subj_v=tk.StringVar(value=""); sw_date_v=tk.StringVar(value="")
    pa_v=tk.StringVar(value="present")

    def mkdd(parent,var,opts,width=12,cmd=None):
        fr=tk.Frame(parent,bg=th.T["accent"],pady=1,padx=1); fr.pack(side="left",padx=(0,6))
        mb=tk.Menubutton(fr,textvariable=var,fg=th.T["text"],bg=th.T["card2"],
                         activeforeground=th.T["text"],activebackground=th.T["hover"],
                         font=th.F["sm"],relief="flat",width=width,pady=3,padx=8,
                         indicatoron=True,cursor="hand2"); mb.pack()
        mn=tk.Menu(mb,tearoff=0,bg=th.T["card"],fg=th.T["text"],
                   activebackground=th.T["accent"],activeforeground="white",
                   font=th.F["sm"],relief="flat",bd=0)
        _cb=cmd if cmd else lambda:m.after(60,refresh)
        for o in opts:
            mn.add_radiobutton(label=o,variable=var,value=o,command=_cb)
        mb.configure(menu=mn); return mb,fr

    tk.Label(tb,text="Class:",fg=th.T["text2"],bg=th.T["page"],font=th.F["sm"]).pack(side="left",padx=(0,4))
    mkdd(tb,cls_v,["All"]+db.class_list(),14)
    tk.Label(tb,text="Sort:",fg=th.T["text2"],bg=th.T["page"],font=th.F["sm"]).pack(side="left",padx=(0,4))
    mkdd(tb,srt_v,["Name","% High-Low","% Low-High","Most Late"])

    tk.Label(tb,text="  View:",fg=th.T["text2"],bg=th.T["page"],font=th.F["sm"]).pack(side="left",padx=(8,4))
    mode_btns={}

    subj_frame=tk.Frame(tb,bg=th.T["page"])
    day_filter_frame=tk.Frame(tb,bg=th.T["page"])
    sw_filter_frame=tk.Frame(tb,bg=th.T["page"])

    def _rebuild_dd(frame,var,opts,width,cmd):
        for w in frame.winfo_children(): w.destroy()
        fr2=tk.Frame(frame,bg=th.T["accent"],pady=1,padx=1); fr2.pack(side="left")
        mb2=tk.Menubutton(fr2,textvariable=var,fg=th.T["text"],bg=th.T["card2"],
                          activeforeground=th.T["text"],activebackground=th.T["hover"],
                          font=th.F["sm"],relief="flat",width=width,pady=3,padx=8,
                          indicatoron=True,cursor="hand2"); mb2.pack()
        mn2=tk.Menu(mb2,tearoff=0,bg=th.T["card"],fg=th.T["text"],
                    activebackground=th.T["accent"],activeforeground="white",
                    font=th.F["sm"],relief="flat",bd=0)
        for o in opts:
            mn2.add_radiobutton(label=o,variable=var,value=o,command=cmd)
        mb2.configure(menu=mn2)

    def set_mode(v):
        mode_v.set(v)
        for vv,b in mode_btns.items():
            b.configure(bg=th.T["accent"] if vv==v else th.T["card2"],
                        fg="white" if vv==v else th.T["text2"])
        subj_frame.pack_forget(); day_filter_frame.pack_forget(); sw_filter_frame.pack_forget()
        if v=="subject":     subj_frame.pack(side="left",padx=(0,6))
        elif v=="daywise":   day_filter_frame.pack(side="left",padx=(0,6))
        elif v=="subjectwise": sw_filter_frame.pack(side="left",padx=(0,6))
        m.after(60,refresh)

    for vv,lbl in [("overall","Overall"),("subject","By Subject"),
                   ("daywise","Day Wise"),("subjectwise","Subject Wise")]:
        b=tk.Button(tb,text=lbl,
                    bg=th.T["accent"] if vv=="overall" else th.T["card2"],
                    fg="white" if vv=="overall" else th.T["text2"],
                    relief="flat",font=th.F["sm"],cursor="hand2",
                    padx=10,pady=4,command=lambda v=vv:set_mode(v))
        b.pack(side="left",padx=(0,3)); mode_btns[vv]=b

    def refresh_subj_menu():
        subjects=["All Subjects"]+db.subject_list()
        if subj_v.get() not in subjects: subj_v.set(subjects[0])
        _rebuild_dd(subj_frame,subj_v,subjects,16,lambda:m.after(60,refresh))

    def refresh_day_filters():
        dates=db.all_att_dates()
        if not dates: day_v.set(""); return
        if not day_v.get() or day_v.get() not in dates: day_v.set(dates[-1])
        subjects_day=["All Subjects"]+db.subject_list()
        if dsubj_v.get() not in subjects_day: dsubj_v.set("All Subjects")
        for w in day_filter_frame.winfo_children(): w.destroy()
        tk.Label(day_filter_frame,text="Date:",fg=th.T["text2"],bg=th.T["page"],
                 font=th.F["sm"]).pack(side="left",padx=(0,4))
        df=tk.Frame(day_filter_frame,bg=th.T["page"]); df.pack(side="left",padx=(0,6))
        _rebuild_dd(df,day_v,dates,13,lambda:m.after(60,refresh))
        tk.Label(day_filter_frame,text="Subject:",fg=th.T["text2"],bg=th.T["page"],
                 font=th.F["sm"]).pack(side="left",padx=(4,4))
        dsf=tk.Frame(day_filter_frame,bg=th.T["page"]); dsf.pack(side="left",padx=(0,6))
        _rebuild_dd(dsf,dsubj_v,subjects_day,14,lambda:m.after(60,refresh))

    def refresh_sw_filters():
        subjects=db.subject_list()
        if not subjects: sw_subj_v.set(""); return
        if not sw_subj_v.get() or sw_subj_v.get() not in subjects: sw_subj_v.set(subjects[0])
        sess=db.subject_sessions()
        dates_for_subj=sess.get(sw_subj_v.get(),[])
        all_opt=["All Dates"]+dates_for_subj
        if sw_date_v.get() not in all_opt:
            sw_date_v.set(all_opt[-1] if dates_for_subj else "All Dates")
        for w in sw_filter_frame.winfo_children(): w.destroy()
        tk.Label(sw_filter_frame,text="Subject:",fg=th.T["text2"],bg=th.T["page"],
                 font=th.F["sm"]).pack(side="left",padx=(0,4))
        sf3=tk.Frame(sw_filter_frame,bg=th.T["page"]); sf3.pack(side="left",padx=(0,6))
        _rebuild_dd(sf3,sw_subj_v,subjects,16,lambda:m.after(60,refresh))
        tk.Label(sw_filter_frame,text="Date:",fg=th.T["text2"],bg=th.T["page"],
                 font=th.F["sm"]).pack(side="left",padx=(0,4))
        sess2=db.subject_sessions()
        d4=["All Dates"]+sess2.get(sw_subj_v.get(),[])
        if sw_date_v.get() not in d4: sw_date_v.set(d4[-1])
        df3=tk.Frame(sw_filter_frame,bg=th.T["page"]); df3.pack(side="left",padx=(0,6))
        _rebuild_dd(df3,sw_date_v,d4,13,lambda:m.after(60,refresh))

    refresh_subj_menu()

    tk.Button(tb,text="Refresh",bg=th.T["accent"],fg="white",relief="flat",
              font=("Segoe UI",9,"bold"),cursor="hand2",pady=4,padx=10,
              command=lambda:refresh()).pack(side="left",padx=(6,0))
    sum_lbl=tk.Label(tb,text="",fg=th.T["muted"],bg=th.T["page"],font=th.F["xs"])
    sum_lbl.pack(side="right",padx=8)

    # ── CONTENT AREA ───────────────────────────────────────────────
    mf=tk.Frame(body,bg=th.T["page"]); mf.grid(row=1,column=0,sticky="nsew")
    mf.columnconfigure(0,weight=2); mf.columnconfigure(1,weight=3); mf.rowconfigure(0,weight=1)

    # LEFT PANEL ─ multiple sub-frames, swapped per mode
    left_outer=tk.Frame(mf,bg=th.T["card"],padx=10,pady=10)
    left_outer.grid(row=0,column=0,sticky="nsew",padx=(0,10))
    left_outer.columnconfigure(0,weight=1); left_outer.rowconfigure(1,weight=1)

    # Student summary (overall / per-subject)
    sum_hdr=tk.Label(left_outer,text="Student Summary",fg=th.T["text"],
                     bg=th.T["card"],font=th.F["h2"])
    sum_hdr.grid(row=0,column=0,sticky="w",pady=(0,6))
    atv,af=W.treeview(left_outer,
        cols=("name","cls","present","total","pct","late"),
        heads=("  Name","Class","Present","Total","%","Late"),
        widths=[140,90,60,55,65,50])
    af.grid(row=1,column=0,sticky="nsew")

    # Subject overview panel (subject mode – All Subjects)
    sv2_f=tk.Frame(left_outer,bg=th.T["card"])
    sv2_f.grid(row=0,column=0,sticky="nsew",rowspan=2); sv2_f.grid_remove()
    sv2_f.columnconfigure(0,weight=1); sv2_f.rowconfigure(1,weight=1)
    tk.Label(sv2_f,text="Subject Overview",fg=th.T["text"],
             bg=th.T["card"],font=th.F["h2"]).grid(row=0,column=0,sticky="w",pady=(0,6))
    stv,sf2=W.treeview(sv2_f,
        cols=("subject","students","sessions","records"),
        heads=("Subject","Students","Sessions","Total Entries"),
        widths=[180,80,80,100],stretch_col="subject")
    sf2.grid(row=1,column=0,sticky="nsew")

    # Present / Absent panel (Day Wise & Subject Wise modes)
    pa_outer=tk.Frame(left_outer,bg=th.T["card"])
    pa_outer.grid(row=0,column=0,sticky="nsew",rowspan=2); pa_outer.grid_remove()
    pa_outer.columnconfigure(0,weight=1); pa_outer.rowconfigure(2,weight=1)

    pa_hdr_f=tk.Frame(pa_outer,bg=th.T["card"])
    pa_hdr_f.grid(row=0,column=0,sticky="ew",pady=(0,2))
    pa_title=tk.Label(pa_hdr_f,text="",fg=th.T["text"],bg=th.T["card"],font=th.F["h2"])
    pa_title.pack(side="left")
    pa_toggle_f=tk.Frame(pa_hdr_f,bg=th.T["card"]); pa_toggle_f.pack(side="right")
    pa_btns={}

    def set_pa(v):
        pa_v.set(v)
        for vv2,b2 in pa_btns.items():
            if vv2==v: b2.configure(bg=th.T["green"] if v=="present" else th.T["red"],fg="white")
            else: b2.configure(bg=th.T["card2"],fg=th.T["text2"])
        m.after(60,refresh)

    for pv,pl in [("present","✓  Present"),("absent","✗  Absent")]:
        pb2=tk.Button(pa_toggle_f,text=pl,
                      bg=th.T["green"] if pv=="present" else th.T["card2"],
                      fg="white" if pv=="present" else th.T["text2"],
                      relief="flat",font=th.F["sm"],cursor="hand2",padx=10,pady=4,
                      command=lambda v=pv:set_pa(v))
        pb2.pack(side="left",padx=(0,3)); pa_btns[pv]=pb2

    pa_count=tk.Label(pa_outer,text="",fg=th.T["muted"],bg=th.T["card"],font=th.F["xs"])
    pa_count.grid(row=1,column=0,sticky="w",pady=(0,4))
    pa_tv,pa_tf=W.treeview(pa_outer,
        cols=("id","name","cls","dept","info"),
        heads=("ID","  Name","Class","Dept","Info"),
        widths=[55,155,90,95,130],stretch_col="name")
    pa_tf.grid(row=2,column=0,sticky="nsew")

    # RIGHT PANEL – bar / summary chart
    cf2=tk.Frame(mf,bg=th.T["card"],padx=12,pady=12)
    cf2.grid(row=0,column=1,sticky="nsew")
    cf2.columnconfigure(0,weight=1); cf2.rowconfigure(1,weight=1)
    chart_title=tk.Label(cf2,text="Attendance %",fg=th.T["text"],
                         bg=th.T["card"],font=th.F["h2"])
    chart_title.grid(row=0,column=0,sticky="w",pady=(0,8))
    co=tk.Frame(cf2,bg=th.T["card2"]); co.grid(row=1,column=0,sticky="nsew")
    co.columnconfigure(0,weight=1); co.rowconfigure(0,weight=1)
    canvas=tk.Canvas(co,bg=th.T["card2"],highlightthickness=0)
    canvas.grid(row=0,column=0,sticky="nsew")
    vs=ttk.Scrollbar(co,orient="vertical",command=canvas.yview)
    vs.grid(row=0,column=1,sticky="ns")
    canvas.configure(yscrollcommand=vs.set)
    low_thr=float(db.setting("low_att_threshold","75"))

    def bar_col(pct):
        return th.T["green"] if pct>=low_thr else th.T["orange"] if pct>=50 else th.T["red"]

    def get_rows():
        mode=mode_v.get()
        if mode=="overall":
            rows2,tot=db.compute_analytics(cls_v.get())
        else:
            subj=subj_v.get()
            if subj=="All Subjects" or not subj: rows2=[]; tot=0
            else: rows2,tot=db.compute_per_subject_student_analytics(subj,cls_v.get())
        sv2=srt_v.get()
        if sv2=="% High-Low": rows2.sort(key=lambda r:r["pct"],reverse=True)
        elif sv2=="% Low-High": rows2.sort(key=lambda r:r["pct"])
        elif sv2=="Most Late":  rows2.sort(key=lambda r:r["late"],reverse=True)
        else: rows2.sort(key=lambda r:r["name"].lower())
        return rows2,tot

    _last=[None]

    def draw_chart(rows2):
        canvas.delete("all"); m.update_idletasks()
        cw=canvas.winfo_width(); ch=canvas.winfo_height()
        if cw<10 or not rows2: return
        n=len(rows2); pl,pr,pt,pb=185,70,28,14; rh=34
        th2=max(pt+n*rh+pb,ch); bw=max(cw-pl-pr-10,80)
        canvas.configure(scrollregion=(0,0,cw,th2))
        for xv in [0,25,50,75,100]:
            x=pl+int(xv/100*bw)
            canvas.create_line(x,pt-10,x,th2-pb,
                fill=th.T["green"] if xv==low_thr else th.T["border"],
                width=1,dash=(4,4) if xv==low_thr else (2,4) if xv>0 else ())
            canvas.create_text(x,pt-13,text=f"{xv}%",
                fill=th.T["green"] if xv==low_thr else th.T["muted"],
                font=("Segoe UI",7),anchor="s")
        for i,r in enumerate(rows2):
            yc=pt+i*rh+rh//2; yt=pt+i*rh+3; yb=yt+rh-6
            bw2=int(r["pct"]/100*bw); col=bar_col(r["pct"])
            if i%2==0: canvas.create_rectangle(0,yt-2,cw,yb+2,fill=th.T["row_alt"],outline="")
            nm3=(r["name"][:22]+"...") if len(r["name"])>23 else r["name"]
            canvas.create_text(pl-8,yc,text=nm3,fill=th.T["text"],font=("Segoe UI",9),anchor="e")
            if r.get("low",False): canvas.create_text(2,yc,text="!",fill=th.T["red"],font=("Segoe UI",8,"bold"),anchor="w")
            if bw2>0: canvas.create_rectangle(pl,yt,pl+max(bw2,3),yb,fill=col,outline="")
            pt2=f"{r['pct']:.1f}%"
            if bw2>50: canvas.create_text(pl+bw2-5,yc,text=pt2,fill="white",font=("Segoe UI",8,"bold"),anchor="e")
            else: canvas.create_text(pl+bw2+5,yc,text=pt2,fill=col,font=("Segoe UI",8,"bold"),anchor="w")
        canvas.create_line(pl,pt-10,pl,th2-pb,fill=th.T["muted"],width=1)

    def draw_pa_chart(present_list, absent_list):
        """Draw a present/absent summary in the chart panel."""
        canvas.delete("all"); m.update_idletasks()
        cw=canvas.winfo_width(); ch=canvas.winfo_height()
        if cw<10: return
        total=len(present_list)+len(absent_list)
        canvas.configure(scrollregion=(0,0,cw,ch))
        if total==0:
            canvas.create_text(cw//2,ch//2,text="No data for this selection",
                fill=th.T["muted"],font=("Segoe UI",11)); return
        pr_pct=len(present_list)/total*100
        ab_pct=100-pr_pct
        bh=48; gap=14; bx=90; bw2=max(cw-bx-60,80)
        cy=ch//3
        # Present row
        canvas.create_text(bx-10,cy+bh//2,text="Present",
            fill=th.T["green"],font=("Segoe UI",10,"bold"),anchor="e")
        pw=int(pr_pct/100*bw2)
        if pw>0: canvas.create_rectangle(bx,cy,bx+pw,cy+bh,fill=th.T["green"],outline="")
        canvas.create_text(bx+pw+8,cy+bh//2,
            text=f"{len(present_list)} students  ({pr_pct:.1f}%)",
            fill=th.T["text"],font=("Segoe UI",9),anchor="w")
        # Absent row
        by2=cy+bh+gap
        canvas.create_text(bx-10,by2+bh//2,text="Absent",
            fill=th.T["red"],font=("Segoe UI",10,"bold"),anchor="e")
        aw=int(ab_pct/100*bw2)
        if aw>0: canvas.create_rectangle(bx,by2,bx+aw,by2+bh,fill=th.T["red"],outline="")
        canvas.create_text(bx+aw+8,by2+bh//2,
            text=f"{len(absent_list)} students  ({ab_pct:.1f}%)",
            fill=th.T["text"],font=("Segoe UI",9),anchor="w")
        # Total label
        canvas.create_text(cw//2,by2+bh+gap+14,
            text=f"Total Enrolled: {total}",
            fill=th.T["muted"],font=("Segoe UI",10))

    # Store last pa lists for toggle re-render
    _pa_cache=[[], []]

    def _show_pa_list(present_list, absent_list, title):
        _pa_cache[0]=present_list; _pa_cache[1]=absent_list
        pa_title.configure(text=title)
        which=pa_v.get()
        items=present_list if which=="present" else absent_list
        pa_tv.delete(*pa_tv.get_children())
        icon="✓" if which=="present" else "✗"
        col=th.T["green"] if which=="present" else th.T["red"]
        pa_count.configure(
            text=f"{icon} Showing {len(items)}    |    "
                 f"Present: {len(present_list)}   Absent: {len(absent_list)}")
        for r in items:
            if which=="present":
                info=(r.get("subjects","")+" ⏱" if r.get("is_late") else r.get("subjects","")).strip()
                time_=r.get("time","")
                info_str=f"{time_}  {info}".strip() if time_ else info
            else:
                info_str="—"
            pa_tv.insert("","end",values=(r["id"],r["name"],r["class"],r["dept"],info_str))
        # update toggle button colours
        for vv2,b2 in pa_btns.items():
            if vv2==which: b2.configure(bg=th.T["green"] if which=="present" else th.T["red"],fg="white")
            else: b2.configure(bg=th.T["card2"],fg=th.T["text2"])

    # Make pa toggle re-render without full refresh
    def _on_pa_toggle(v):
        pa_v.set(v)
        if _pa_cache[0] or _pa_cache[1]:
            _show_pa_list(_pa_cache[0],_pa_cache[1],pa_title.cget("text"))
        for vv2,b2 in pa_btns.items():
            if vv2==v: b2.configure(bg=th.T["green"] if v=="present" else th.T["red"],fg="white")
            else: b2.configure(bg=th.T["card2"],fg=th.T["text2"])

    for pv2 in pa_btns:
        pa_btns[pv2].configure(command=lambda v=pv2:_on_pa_toggle(v))

    def refresh():
        refresh_subj_menu(); refresh_day_filters(); refresh_sw_filters()
        mode=mode_v.get()

        # ── OVERALL / BY-SUBJECT ───────────────────────────────────
        if mode in ("overall","subject"):
            pa_outer.grid_remove()
            chart_title.configure(text="Attendance %")
            is_overview=(mode=="subject" and subj_v.get()=="All Subjects")
            if is_overview:
                af.grid_remove(); sv2_f.grid()
                sdata=db.compute_subject_analytics(cls_v.get())
                stv.delete(*stv.get_children())
                for row in sdata:
                    stv.insert("","end",values=(row["subject"],row["students"],
                                                row["sessions"],row["total_records"]))
                sum_lbl.configure(text=f"Subjects: {len(sdata)}")
                _last[0]=[]
            else:
                sv2_f.grid_remove(); af.grid()
                rows2,tot=get_rows(); _last[0]=rows2
                atv.delete(*atv.get_children())
                avg=round(sum(r["pct"] for r in rows2)/len(rows2),1) if rows2 else 0
                below=sum(1 for r in rows2 if r.get("low",False))
                sum_lbl.configure(
                    text=f"Average: {avg}%   |   Below {low_thr:.0f}%: {below}/{len(rows2)}   |   Days: {tot}")
                for r in rows2:
                    tag="lo" if r.get("low") else "ok"
                    atv.insert("","end",values=(r["name"],r["class"],r["present"],
                                                r["total"],f"{r['pct']}%",r["late"]),tags=(tag,))
                atv.tag_configure("lo",foreground=th.T["tag_low"])
                atv.tag_configure("ok",foreground=th.T["tag_ok"])
            m.after(100,lambda:draw_chart(_last[0] or []))

        # ── DAY WISE ──────────────────────────────────────────────
        elif mode=="daywise":
            af.grid_remove(); sv2_f.grid_remove(); pa_outer.grid()
            date=day_v.get()
            if not date:
                sum_lbl.configure(text="No attendance records found.")
                pa_tv.delete(*pa_tv.get_children()); canvas.delete("all"); return
            subj_sel=dsubj_v.get()
            subj_arg="All" if subj_sel=="All Subjects" else subj_sel
            plist,alist=db.get_day_attendance_detail(
                date,subject_filter=subj_arg,cls_filter=cls_v.get())
            lbl=f"Day: {date}" + (f"   {subj_sel}" if subj_arg!="All" else "")
            _show_pa_list(plist,alist,lbl)
            sum_lbl.configure(
                text=f"Date: {date}  |  Present: {len(plist)}  |  Absent: {len(alist)}"
                     + (f"  |  Subject: {subj_sel}" if subj_arg!="All" else ""))
            chart_title.configure(text=f"Attendance — {date}")
            _last[0]=None
            m.after(100,lambda pl=plist,al=alist:draw_pa_chart(pl,al))

        # ── SUBJECT WISE ──────────────────────────────────────────
        elif mode=="subjectwise":
            af.grid_remove(); sv2_f.grid_remove(); pa_outer.grid()
            subj=sw_subj_v.get()
            if not subj:
                sum_lbl.configure(text="No subjects in timetable.")
                pa_tv.delete(*pa_tv.get_children()); canvas.delete("all"); return
            date_sel=sw_date_v.get()
            cls_arg=cls_v.get()
            if date_sel=="All Dates" or not date_sel:
                rows2,tot=db.compute_per_subject_student_analytics(subj,cls_arg)
                all_stu=[s for s in db.students_all()
                         if cls_arg=="All" or s.get("Class","")==cls_arg]
                present_ids={r["id"] for r in rows2}
                plist=[{"id":r["id"],"name":r["name"],"class":r["class"],
                        "dept":r["dept"],
                        "subjects":f"{r['present']}/{tot} sessions",
                        "time":"","is_late":r["late"]>0}
                       for r in rows2]
                alist=[{"id":s["ID"],"name":s["Name"],"class":s.get("Class",""),
                        "dept":s.get("Department","")}
                       for s in all_stu if s["ID"] not in present_ids]
                title=f"Subject: {subj}  (All Sessions)"
                sum_lbl.configure(
                    text=f"{subj}  |  Sessions: {tot}  |  Present: {len(plist)}  |  Never attended: {len(alist)}")
            else:
                plist,alist=db.get_day_attendance_detail(
                    date_sel,subject_filter=subj,cls_filter=cls_arg)
                title=f"Subject: {subj}   {date_sel}"
                sum_lbl.configure(
                    text=f"{subj} on {date_sel}  |  Present: {len(plist)}  |  Absent: {len(alist)}")
            _show_pa_list(plist,alist,title)
            chart_title.configure(text=f"{subj} Attendance")
            _last[0]=None
            m.after(100,lambda pl=plist,al=alist:draw_pa_chart(pl,al))

    canvas.bind("<Configure>",
        lambda e: m.after(80,lambda: draw_chart(_last[0]) if _last[0] else None))
    refresh()



# ──────────────────────────────────────────────────────────────────
#  MODAL: HOLIDAYS
# ──────────────────────────────────────────────────────────────────

def _show_holidays(A):
    m,hdr,body=W.modal(A.window,"Holidays",620,460,th.T["orange"])
    body.rowconfigure(0,weight=1)
    tv,tf=W.treeview(body,cols=("date","name","type"),heads=("Date","Holiday Name","Type"),
                     widths=[120,250,130],stretch_col="name",style="OR.Treeview")
    tf.grid(row=0,column=0,sticky="nsew",pady=(0,10))
    def reload():
        tv.delete(*tv.get_children())
        for h in db.holidays_all(): tv.insert("","end",values=(h["Date"],h["Name"],h["Type"]))
    reload()
    ff=tk.Frame(body,bg=th.T["card"],padx=14,pady=10)
    ff.grid(row=1,column=0,sticky="ew",pady=(0,8)); ff.columnconfigure((0,1,2),weight=1)
    for i,lb in enumerate(["DATE (DD-MM-YYYY)","HOLIDAY NAME","TYPE"]):
        tk.Label(ff,text=lb,fg=th.T["muted"],bg=th.T["card"],font=th.F["label"]).grid(row=0,column=i,sticky="w",padx=6)
    dt_e=W.plain_entry(ff); dt_e.grid(row=1,column=0,sticky="ew",padx=6,pady=(2,0))
    nm_e=W.plain_entry(ff); nm_e.grid(row=1,column=1,sticky="ew",padx=6,pady=(2,0))
    ht_v=tk.StringVar(value="General")
    W.combobox(ff,["General","National","Regional","Exam","Other"],textvariable=ht_v,width=12).grid(row=1,column=2,sticky="ew",padx=6,pady=(2,0))
    def add_h():
        dt=dt_e.get().strip(); nm=nm_e.get().strip()
        if not dt or not nm: messagebox.showerror("Error","Date and name required.",parent=m); return
        db.holiday_add(dt,nm,ht_v.get()); reload()
    def del_h():
        sel=tv.selection()
        if not sel: return
        db.holiday_delete(tv.index(sel[0])); reload()
    bf=tk.Frame(body,bg=th.T["page"]); bf.grid(row=2,column=0,sticky="ew")
    W.btn_primary(bf,"  Add Holiday",add_h,bg=th.T["orange"],pack=False).pack(side="left",padx=(0,8))
    tk.Button(bf,text="Delete Selected",command=del_h,fg=th.T["text2"],bg=th.T["card2"],
              activebackground=th.T["hover"],relief="flat",font=th.F["body"],
              cursor="hand2",pady=8).pack(side="left",padx=(0,8))
    tk.Button(bf,text="Close",command=m.destroy,fg=th.T["text2"],bg=th.T["card2"],
              activebackground=th.T["hover"],relief="flat",font=th.F["body"],
              cursor="hand2",pady=8).pack(side="right")


# ──────────────────────────────────────────────────────────────────
#  MODAL: UNKNOWN GALLERY
# ──────────────────────────────────────────────────────────────────

def _show_gallery(A):
    from PIL import Image, ImageTk
    import os as _os

    m,hdr,body=W.modal(A.window,"Unrecognised Faces",980,600,th.T["orange"])
    body.columnconfigure(0,weight=3); body.columnconfigure(1,weight=2); body.rowconfigure(0,weight=1)

    # ── Left: list ────────────────────────────────────────────────
    lf=tk.Frame(body,bg=th.T["card"]); lf.grid(row=0,column=0,sticky="nsew",padx=(0,10))
    lf.columnconfigure(0,weight=1); lf.rowconfigure(1,weight=1)

    # Count label + Refresh row
    top_row=tk.Frame(lf,bg=th.T["card"]); top_row.grid(row=0,column=0,sticky="ew",pady=(0,6))
    count_lbl=tk.Label(top_row,text="",fg=th.T["muted"],bg=th.T["card"],font=th.F["xs"])
    count_lbl.pack(side="left",padx=4)

    tv,tf=W.treeview(lf,cols=("date","time","reviewed","file"),
                     heads=("Date","Time","Reviewed","Filename"),
                     widths=[110,80,90,260],stretch_col="file",style="OR.Treeview",height=16)
    tf.grid(row=1,column=0,sticky="nsew")

    # ── Right: preview ────────────────────────────────────────────
    pf=tk.Frame(body,bg=th.T["card"],padx=14,pady=14); pf.grid(row=0,column=1,sticky="nsew")
    pf.columnconfigure(0,weight=1); pf.rowconfigure(1,weight=1)
    tk.Label(pf,text="Preview",fg=th.T["text"],bg=th.T["card"],font=th.F["h2"]).grid(row=0,column=0,sticky="w",pady=(0,8))
    prev_canvas=tk.Label(pf,text="Select a row to preview",
                         fg=th.T["muted"],bg=th.T["card2"],anchor="center")
    prev_canvas.grid(row=1,column=0,sticky="nsew")
    prev_canvas._p=None
    inf=tk.Label(pf,text="",fg=th.T["text2"],bg=th.T["card"],font=th.F["sm"],
                 wraplength=220,justify="left")
    inf.grid(row=2,column=0,sticky="w",pady=(8,0))

    # ── Resolve photo path (handle relative/absolute) ─────────────
    def _resolve_path(photo_path):
        if _os.path.isabs(photo_path) and _os.path.isfile(photo_path):
            return photo_path
        # Try relative to project base
        from config import BASE_DIR, DIR_UNKNOWN
        candidates = [
            photo_path,
            _os.path.join(BASE_DIR, photo_path),
            _os.path.join(DIR_UNKNOWN, _os.path.basename(photo_path)),
            _os.path.join(DIR_UNKNOWN, photo_path),
        ]
        for p in candidates:
            if _os.path.isfile(p):
                return p
        return None

    _faces_ref = [None]   # mutable ref so refresh can update

    def _populate():
        faces = db.unknown_all()
        _faces_ref[0] = faces
        tv.delete(*tv.get_children())
        for i,f2 in enumerate(faces):
            rv = "✓ Yes" if f2.get("Reviewed","No")=="Yes" else "No"
            resolved = _resolve_path(f2["PhotoPath"])
            exists_mark = "" if resolved else " ✗"
            tv.insert("","end",iid=str(i),
                      values=(f2["Date"],f2["Time"],rv,
                              _os.path.basename(f2["PhotoPath"])+exists_mark),
                      tags=("rv" if rv!="No" else "new",))
        tv.tag_configure("new",foreground=th.T["orange"])
        tv.tag_configure("rv",foreground=th.T["muted"])
        n=len(faces); reviewed=sum(1 for f2 in faces if f2.get("Reviewed","No")=="Yes")
        count_lbl.configure(text=f"Total: {n}   Reviewed: {reviewed}   Pending: {n-reviewed}")

    def _refresh():
        prev_canvas.configure(image="",text="Select a row to preview"); prev_canvas._p=None
        inf.configure(text="")
        _populate()

    # Refresh button
    tk.Button(top_row,text="↻  Refresh",command=_refresh,
              fg="white",bg=th.T["orange"],activebackground=th.T["orange"],
              relief="flat",font=th.F["sm"],cursor="hand2",padx=10,pady=4).pack(side="right",padx=4)

    _populate()

    def on_sel(e):
        sel=tv.selection()
        if not sel: return
        faces=_faces_ref[0]
        try: idx=int(sel[0])
        except ValueError: return
        if idx>=len(faces): return
        f2=faces[idx]
        resolved=_resolve_path(f2["PhotoPath"])
        info_txt=(f"Date:  {f2['Date']}\nTime:  {f2['Time']}\n"
                  f"Reviewed: {'Yes' if f2.get('Reviewed','No')=='Yes' else 'No'}\n"
                  f"File: {_os.path.basename(f2['PhotoPath'])}")
        inf.configure(text=info_txt)
        if resolved:
            try:
                m.update_idletasks()
                pw=max(prev_canvas.winfo_width(),220)
                ph=max(prev_canvas.winfo_height(),200)
                img2=Image.open(resolved)
                img2.thumbnail((pw,ph),Image.LANCZOS)
                ph2=ImageTk.PhotoImage(img2)
                prev_canvas.configure(image=ph2,text="")
                prev_canvas._p=ph2
            except Exception as ex:
                prev_canvas.configure(image="",text=f"Cannot load:\n{ex}")
                prev_canvas._p=None
        else:
            prev_canvas.configure(image="",text="Image file not found\non disk")
            prev_canvas._p=None

    tv.bind("<<TreeviewSelect>>",on_sel)

    def mark_reviewed():
        sel=tv.selection()
        if not sel: return
        faces=_faces_ref[0]
        try: idx=int(sel[0])
        except ValueError: return
        if idx>=len(faces): return
        db.unknown_mark_reviewed(idx,"Reviewed")
        faces[idx]["Reviewed"]="Yes"
        tv.item(sel[0],values=(faces[idx]["Date"],faces[idx]["Time"],"✓ Yes",
                               _os.path.basename(faces[idx]["PhotoPath"])))
        reviewed=sum(1 for f2 in faces if f2.get("Reviewed","No")=="Yes")
        count_lbl.configure(
            text=f"Total: {len(faces)}   Reviewed: {reviewed}   Pending: {len(faces)-reviewed}")

    bf=tk.Frame(body,bg=th.T["page"]); bf.grid(row=1,column=0,columnspan=2,sticky="ew",pady=(8,0))
    tk.Button(bf,text="  ✓  Mark Reviewed",command=mark_reviewed,fg="white",bg=th.T["orange"],
              activebackground=th.T["orange"],relief="flat",font=("Segoe UI",10,"bold"),
              cursor="hand2",pady=8).pack(side="left",padx=(0,8))
    tk.Button(bf,text="Close",command=m.destroy,fg=th.T["text2"],bg=th.T["card2"],
              activebackground=th.T["hover"],relief="flat",font=th.F["body"],
              cursor="hand2",pady=8).pack(side="right")


# ──────────────────────────────────────────────────────────────────
#  MODAL: AUDIT LOG
# ──────────────────────────────────────────────────────────────────

def _show_audit(A):
    logs=db.audit_read()
    m,hdr,body=W.modal(A.window,"Audit Log",900,520,th.T["purple"])
    body.rowconfigure(0,weight=1)
    tv,tf=W.treeview(body,cols=("ts","action","desc","by","result"),
                     heads=("Timestamp","Action","Description","By","Result"),
                     widths=[140,100,290,80,70],stretch_col="desc",style="PU.Treeview",height=14)
    tf.grid(row=0,column=0,sticky="nsew")
    col_map={"REGISTER":th.T["green"],"REMOVE":th.T["red"],"LOGIN":th.T["accent"],
             "LOGOUT":th.T["muted"],"HOLIDAY":th.T["orange"],"BACKUP":th.T["accent"],
             "RESTORE":th.T["orange"],"SETTINGS":th.T["cyan"],"TIMETABLE":th.T["teal"],
             "UPDATE":th.T["cyan"],"LOGIN_FAIL":th.T["red"]}
    for lg in logs:
        c3=col_map.get(lg.get("Action",""),th.T["text2"])
        tv.insert("","end",values=(lg.get("Timestamp",""),lg.get("Action",""),
                  lg.get("Description",""),lg.get("By",""),lg.get("Result","")),
                  tags=(lg.get("Action",""),))
        tv.tag_configure(lg.get("Action",""),foreground=c3)
    tk.Button(body,text="Close",command=m.destroy,fg=th.T["text2"],bg=th.T["card2"],
              activebackground=th.T["hover"],relief="flat",font=th.F["body"],
              cursor="hand2",pady=8).grid(row=1,column=0,sticky="e",pady=(8,0))


# ──────────────────────────────────────────────────────────────────
#  MODAL: SETTINGS
# ──────────────────────────────────────────────────────────────────

def _show_settings(A, tab=None):
    import recognition as rec
    m=tk.Toplevel(A.window); m.geometry("600x640")
    m.resizable(False,False); m.title("FaceTrack Pro — Settings")
    m.configure(bg=th.T["page"]); m.grab_set()
    hdr=tk.Frame(m,bg=th.T["card"],height=52); hdr.pack(fill="x"); hdr.pack_propagate(False)
    tk.Label(hdr,text="  Settings",fg=th.T["text"],bg=th.T["card"],font=th.F["h1"]).pack(side="left",padx=14,pady=14)
    tk.Frame(m,bg=th.T["accent"],height=2).pack(fill="x")
    nb=ttk.Notebook(m); nb.pack(fill="both",expand=True,padx=14,pady=12)

    # Institution tab
    t1=tk.Frame(nb,bg=th.T["card"],padx=20,pady=16); nb.add(t1,text="  Institution  ")
    ents_inst={}
    for lb,key in [("Institution Name","institution_name"),("Address","institution_address")]:
        tk.Label(t1,text=lb.upper(),fg=th.T["muted"],bg=th.T["card"],font=th.F["label"]).pack(anchor="w",pady=(8,0))
        e2=W.plain_entry(t1,val=db.setting(key,"")); e2.pack(fill="x",pady=(2,0)); ents_inst[key]=e2

    # Attendance tab
    t2=tk.Frame(nb,bg=th.T["card"],padx=20,pady=16); nb.add(t2,text="  Attendance  ")
    ents_att={}
    for lb,key in [("Class Start Time (HH:MM)","start_time"),
                   ("Late Threshold (minutes)","late_after"),
                   ("Low Attendance Threshold (%)","low_att_threshold"),
                   ("Cooldown Between Scans (seconds)","cooldown"),
                   ("Frame Skip","frame_skip")]:
        tk.Label(t2,text=lb.upper(),fg=th.T["muted"],bg=th.T["card"],font=th.F["label"]).pack(anchor="w",pady=(8,0))
        e2=W.plain_entry(t2,val=db.setting(key,"")); e2.pack(fill="x",pady=(2,0)); ents_att[key]=e2

    # Security tab
    t3=tk.Frame(nb,bg=th.T["card"],padx=20,pady=16); nb.add(t3,text="  Security  ")
    tk.Label(t3,text="NEW PASSWORD",fg=th.T["muted"],bg=th.T["card"],font=th.F["label"]).pack(anchor="w",pady=(8,0))
    pw_e=W.plain_entry(t3,show="*"); pw_e.pack(fill="x",pady=(2,0))
    tk.Label(t3,text="CONFIRM PASSWORD",fg=th.T["muted"],bg=th.T["card"],font=th.F["label"]).pack(anchor="w",pady=(8,0))
    pw2_e=W.plain_entry(t3,show="*"); pw2_e.pack(fill="x",pady=(2,0))

    # ── FACE DATA TAB ──────────────────────────────────────────────
    import os
    from config import DIR_EMBEDDINGS, DIR_PHOTOS
    t4=tk.Frame(nb,bg=th.T["card"],padx=20,pady=16); nb.add(t4,text="  Face Data  ")

    def _fd_status_text():
        students=db.students_all()
        emb_files={fn.replace(".npy","") for fn in os.listdir(DIR_EMBEDDINGS)
                   if fn.endswith(".npy")} if os.path.isdir(DIR_EMBEDDINGS) else set()
        lines=[]
        ok=0; missing=0
        for s in students:
            has=s["ID"] in emb_files
            ph_dir=os.path.join(DIR_PHOTOS,s["ID"])
            photos=len([f for f in os.listdir(ph_dir) if f.lower().endswith((".jpg",".jpeg",".png"))])\
                   if os.path.isdir(ph_dir) else 0
            icon="✓" if has else "✗"
            lines.append(f"  {icon}  ID {s['ID']:>4}  {s['Name']:<22}  "
                         f"{'Embedding OK' if has else 'NO EMBEDDING':15}  Photos: {photos}")
            if has: ok+=1
            else: missing+=1
        summary=f"Registered: {len(students)}   With face data: {ok}   Missing: {missing}"
        return summary, "\n".join(lines) if lines else "No students registered."

    summary_lbl=tk.Label(t4,text="",fg=th.T["text"],bg=th.T["card"],font=th.F["sm"],anchor="w")
    summary_lbl.pack(fill="x",pady=(0,8))

    # coloured banner
    banner=tk.Frame(t4,bg=th.T["card2"],padx=12,pady=8); banner.pack(fill="x",pady=(0,10))
    banner_lbl=tk.Label(banner,text="",fg=th.T["text"],bg=th.T["card2"],font=th.F["xs"],
                        justify="left",anchor="w"); banner_lbl.pack(fill="x")

    def _refresh_fd():
        summary,detail=_fd_status_text()
        summary_lbl.configure(text=summary)
        banner_lbl.configure(text=detail)
        has_missing="Missing" in detail and "NO EMBEDDING" in detail
        banner.configure(bg=th.T["red_bg"] if has_missing else th.T["card2"])
        banner_lbl.configure(bg=th.T["red_bg"] if has_missing else th.T["card2"],
                             fg=th.T["red"] if has_missing else th.T["text2"])

    _refresh_fd()

    info2=tk.Label(t4,
        text="If a student shows NO EMBEDDING, they must be re-registered so the camera\n"
             "can capture their face. Use Students > Register with the same ID to overwrite.\n\n"
             "If photos exist but embeddings are missing, click Rebuild to regenerate.",
        fg=th.T["muted"],bg=th.T["card"],font=th.F["xs"],justify="left")
    info2.pack(anchor="w",pady=(0,10))

    rb_lbl=tk.Label(t4,text="",fg=th.T["muted"],bg=th.T["card"],font=th.F["xs"],wraplength=520)
    rb_lbl.pack(anchor="w",pady=(0,4))

    def do_rebuild():
        if not rec.model_ready():
            messagebox.showerror("Not Ready",
                "Face recognition engine not loaded.\n"
                "Wait for it to finish loading (check the status bar).",
                parent=m); return
        rb_lbl.configure(text="Rebuilding…",fg=th.T["orange"])
        m.update()
        def _cb(msg): rb_lbl.configure(text=msg)
        ok_c,fail=rec.rebuild_embeddings(db.students_all(),status_cb=_cb)
        rec.enc_load_all()
        _refresh_fd()
        if fail:
            rb_lbl.configure(
                text=f"Done: {ok_c} rebuilt.  Issues: {'; '.join(fail)}",
                fg=th.T["orange"])
        else:
            rb_lbl.configure(text=f"✓ Rebuilt {ok_c} face profile(s) successfully.",fg=th.T["green"])
        if hasattr(A,"refresh_stats"): A.refresh_stats()

    bf4=tk.Frame(t4,bg=th.T["card"]); bf4.pack(fill="x",pady=(4,0))
    tk.Button(bf4,text="  ↻  Rebuild Embeddings from Photos",command=do_rebuild,
              fg="white",bg=th.T["accent"],activebackground=th.T["accent2"],
              relief="flat",font=th.F["sm"],cursor="hand2",padx=14,pady=8).pack(side="left",padx=(0,8))
    tk.Button(bf4,text="Refresh",command=_refresh_fd,
              fg=th.T["text2"],bg=th.T["card2"],activebackground=th.T["hover"],
              relief="flat",font=th.F["sm"],cursor="hand2",padx=10,pady=8).pack(side="left")

    # Jump to face data tab if requested
    if tab=="facedata":
        m.after(100,lambda: nb.select(3))

    def save_all():
        for key,e2 in {**ents_inst,**ents_att}.items(): db.setting_set(key,e2.get().strip())
        np2=pw_e.get().strip(); nc2=pw2_e.get().strip()
        if np2:
            if len(np2)<6: messagebox.showerror("Error","Password must be 6+ characters.",parent=m); return
            if np2!=nc2: messagebox.showerror("Error","Passwords do not match.",parent=m); return
            db.save_password(np2)
        db.audit("SETTINGS","Settings updated")
        messagebox.showinfo("Saved","Settings saved successfully.",parent=m); m.destroy()

    bf=tk.Frame(m,bg=th.T["page"],padx=14,pady=10); bf.pack(fill="x",side="bottom")
    W.btn_primary(bf,"  Save Settings",save_all,pack=False).pack(side="left",fill="x",expand=True,padx=(0,8))
    tk.Button(bf,text="Cancel",command=m.destroy,fg=th.T["text2"],bg=th.T["card2"],
              activebackground=th.T["hover"],relief="flat",font=th.F["body"],cursor="hand2",pady=9).pack(side="right")


# ──────────────────────────────────────────────────────────────────
#  MODAL: BACKUP
# ──────────────────────────────────────────────────────────────────

def _show_backup(A):
    m=tk.Toplevel(A.window); m.geometry("480x280")
    m.resizable(False,False); m.title("FaceTrack Pro — Backup & Restore")
    m.configure(bg=th.T["page"]); m.grab_set()
    hdr=tk.Frame(m,bg=th.T["card"],height=52); hdr.pack(fill="x"); hdr.pack_propagate(False)
    tk.Label(hdr,text="  Backup & Restore",fg=th.T["text"],bg=th.T["card"],font=th.F["h1"]).pack(side="left",padx=14,pady=14)
    tk.Frame(m,bg=th.T["accent"],height=2).pack(fill="x")
    body=tk.Frame(m,bg=th.T["card"],padx=30,pady=20); body.pack(fill="both",expand=True)
    tk.Label(body,text="Backup includes student records, attendance data and face profiles.",
             fg=th.T["muted"],bg=th.T["card"],font=th.F["sm"]).pack(anchor="w",pady=(0,12))
    inf=tk.Label(body,text="",fg=th.T["text2"],bg=th.T["card"],font=th.F["sm"],wraplength=400)
    inf.pack(anchor="w",pady=(0,10))
    def do_bk():
        try: fn=db.create_backup(); inf.configure(text=f"✓  {os.path.basename(fn)}",fg=th.T["green"])
        except Exception as e: inf.configure(text=f"✗  {e}",fg=th.T["red"])
    def do_rs():
        fn=filedialog.askopenfilename(title="Select Backup",filetypes=[("ZIP","*.zip")],parent=m)
        if not fn: return
        if not messagebox.askyesno("Confirm","Replace all current data? Cannot be undone.",parent=m): return
        try:
            db.restore_backup(fn); A.refresh_stats(); A.reload_log()
            inf.configure(text=f"✓  Restored: {os.path.basename(fn)}",fg=th.T["green"])
        except Exception as e: inf.configure(text=f"✗  {e}",fg=th.T["red"])
    W.btn_primary(body,"  Create Backup",do_bk)
    W.btn_primary(body,"  Restore from Backup",do_rs,bg=th.T["orange"])
    tk.Button(body,text="Close",command=m.destroy,fg=th.T["text2"],bg=th.T["card2"],
              activebackground=th.T["hover"],relief="flat",font=th.F["body"],
              cursor="hand2",pady=8).pack(fill="x")


# ──────────────────────────────────────────────────────────────────
#  MODAL: ABOUT
# ──────────────────────────────────────────────────────────────────

def _show_about(A):
    m=tk.Toplevel(A.window)
    m.geometry("560x500")
    m.minsize(480,420)
    m.resizable(True,True)
    m.title("FaceTrack Pro — About")
    m.configure(bg=th.T["page"])
    # Do NOT grab_set — it can interfere with file I/O dialogs on some systems
    m.transient(A.window)
    m.lift(); m.focus_force()

    # ── Header ────────────────────────────────────────────────────
    hdr=tk.Frame(m,bg=th.T["nav"],height=100); hdr.pack(fill="x"); hdr.pack_propagate(False)
    inner=tk.Frame(hdr,bg=th.T["nav"]); inner.place(relx=0.5,rely=0.5,anchor="center")
    tk.Label(inner,text="◈",fg=th.T["accent"],bg=th.T["nav"],
             font=("Segoe UI",22,"bold")).pack(side="left",padx=(0,10))
    ttl=tk.Frame(inner,bg=th.T["nav"]); ttl.pack(side="left")
    tk.Label(ttl,text=APP_NAME,fg="white",bg=th.T["nav"],
             font=("Segoe UI",16,"bold")).pack(anchor="w")
    tk.Label(ttl,text=APP_SUBTITLE,fg=th.T["nav_sub"],bg=th.T["nav"],
             font=th.F["sm"]).pack(anchor="w")
    tk.Frame(m,bg=th.T["accent"],height=3).pack(fill="x")

    # ── Body ──────────────────────────────────────────────────────
    body=tk.Frame(m,bg=th.T["card"],padx=24,pady=16)
    body.pack(fill="both",expand=True)
    body.columnconfigure(0,weight=1)
    body.rowconfigure(1,weight=1)

    tk.Label(body,text="ABOUT THIS PROJECT",fg=th.T["muted"],
             bg=th.T["card"],font=th.F["label"]).grid(row=0,column=0,sticky="w",pady=(0,8))

    # Text area with scrollbar
    tf=tk.Frame(body,bg=th.T["input_border"],padx=1,pady=1)
    tf.grid(row=1,column=0,sticky="nsew",pady=(0,6))
    tf.columnconfigure(0,weight=1); tf.rowconfigure(0,weight=1)
    ti=tk.Frame(tf,bg=th.T["input_bg"]); ti.grid(sticky="nsew",padx=1,pady=1)
    ti.columnconfigure(0,weight=1); ti.rowconfigure(0,weight=1)
    ta=tk.Text(ti,fg=th.T["text"],bg=th.T["input_bg"],
               insertbackground=th.T["accent"],relief="flat",
               font=th.F["body"],bd=8,wrap="word",undo=True)
    ta.grid(row=0,column=0,sticky="nsew")
    sb=tk.Scrollbar(ti,command=ta.yview,bg=th.T["card2"])
    sb.grid(row=0,column=1,sticky="ns")
    ta.configure(yscrollcommand=sb.set)

    # Load existing content
    original=[db.about_read()]   # keep original for cancel
    ta.insert("1.0",original[0])
    ta.edit_reset()  # clear undo history so Ctrl+Z won't erase the loaded text

    # ── Status bar ────────────────────────────────────────────────
    status_var=tk.StringVar(value="")
    status_lbl=tk.Label(body,textvariable=status_var,
                        fg=th.T["muted"],bg=th.T["card"],
                        font=("Segoe UI",9),anchor="w")
    status_lbl.grid(row=2,column=0,sticky="ew",pady=(0,4))

    # ── Button bar ────────────────────────────────────────────────
    bf=tk.Frame(body,bg=th.T["card"])
    bf.grid(row=3,column=0,sticky="ew",pady=(4,0))
    bf.columnconfigure(1,weight=1)

    def _set_status(msg,color):
        status_var.set(msg)
        status_lbl.configure(fg=color)
        m.update_idletasks()

    def do_save():
        txt=ta.get("1.0","end-1c")   # end-1c trims the trailing newline tk always appends
        _set_status("Saving…",th.T["muted"])
        ok=db.about_write(txt)
        m.after(80, lambda: _verify(txt, ok))

    def _verify(txt, write_ok):
        if not write_ok:
            _set_status("✗  Could not write file — check permissions.",th.T["red"])
            return
        verify=db.about_read()
        if verify==txt:
            original[0]=txt
            _set_status("✓  Saved successfully.",th.T["green"])
        else:
            _set_status("✗  Verify failed — please try again.",th.T["red"])

    def do_cancel():
        # Restore original text without saving
        ta.delete("1.0","end")
        ta.insert("1.0",original[0])
        ta.edit_reset()
        _set_status("Changes discarded.",th.T["muted"])

    def do_close():
        # If unsaved changes, warn
        current=ta.get("1.0","end-1c")
        if current!=original[0]:
            from tkinter import messagebox as mb2
            ans=mb2.askyesnocancel("Unsaved Changes",
                "You have unsaved changes.\nSave before closing?",parent=m)
            if ans is True:
                do_save(); m.after(200,m.destroy)
            elif ans is False:
                m.destroy
                m.destroy()
        else:
            m.destroy()

    # Save button — prominent green
    save_btn=tk.Button(bf,text="  💾  Save",command=do_save,
                       fg="white",bg=th.T["green"],
                       activebackground=th.T["green"],
                       relief="flat",font=("Segoe UI",10,"bold"),
                       cursor="hand2",padx=18,pady=9)
    save_btn.grid(row=0,column=0,sticky="w",padx=(0,8))

    # Cancel button — restore to last saved
    tk.Button(bf,text="  ↺  Cancel",command=do_cancel,
              fg=th.T["text2"],bg=th.T["card2"],
              activebackground=th.T["hover"],
              relief="flat",font=th.F["body"],
              cursor="hand2",padx=14,pady=9).grid(row=0,column=1,sticky="w")

    # Close button — right side
    tk.Button(bf,text="Close",command=do_close,
              fg=th.T["text2"],bg=th.T["card2"],
              activebackground=th.T["hover"],
              relief="flat",font=th.F["body"],
              cursor="hand2",padx=14,pady=9).grid(row=0,column=2,sticky="e")

    m.protocol("WM_DELETE_WINDOW",do_close)
    # Bind Ctrl+S to save
    m.bind("<Control-s>",lambda e:do_save())
    m.bind("<Control-S>",lambda e:do_save())


# ──────────────────────────────────────────────────────────────────
#  STUDENT MODALS
# ──────────────────────────────────────────────────────────────────

def _show_all_students(A):
    students=db.students_all()
    m,hdr,body=W.modal(A.window,"All Students",920,560,th.T["accent"])
    body.rowconfigure(1,weight=1)
    sv=tk.StringVar()
    W.search_entry(body,sv).grid(row=0,column=0,sticky="ew",pady=(0,8))
    tv,tf=W.treeview(body,
        cols=("id","name","cls","dept","role","email","phone","reg"),
        heads=("ID","  Name","Class","Dept","Role","Email","Phone","Registered"),
        widths=[70,160,100,100,80,160,100,130],stretch_col="name",height=14)
    tf.grid(row=1,column=0,sticky="nsew")
    def populate(q=""):
        tv.delete(*tv.get_children())
        for s in students:
            if not q or q in s["Name"].lower() or q in s["ID"].lower():
                tv.insert("","end",values=(s["ID"],s["Name"],s.get("Class",""),
                    s.get("Department",""),s.get("Role",""),s.get("Email",""),
                    s.get("Phone",""),s.get("RegisteredOn","")))
    populate()
    sv.trace("w",lambda *_:populate(sv.get().lower().strip()))
    tk.Label(body,text=f"Total: {len(students)} student(s)",
             fg=th.T["muted"],bg=th.T["page"],font=th.F["sm"]).grid(row=2,column=0,sticky="w",pady=(6,0))
    tk.Button(body,text="Close",command=m.destroy,fg=th.T["text2"],bg=th.T["card2"],
              activebackground=th.T["hover"],relief="flat",font=th.F["body"],
              cursor="hand2",pady=8).grid(row=3,column=0,sticky="e",pady=(8,0))

def _show_edit_student(A):
    students=db.students_all()
    if not students:
        messagebox.showinfo("No Students","No students registered yet.",parent=A.window); return
    m,hdr,body=W.modal(A.window,"Edit Student",720,560,th.T["cyan"])
    body.rowconfigure(1,weight=1)
    sv=tk.StringVar()
    W.search_entry(body,sv).grid(row=0,column=0,sticky="ew",pady=(0,8))
    tv,tf=W.treeview(body,cols=("id","name","cls","dept","email","phone"),
                     heads=("ID","  Name","Class","Department","Email","Phone"),
                     widths=[80,160,100,110,160,100],stretch_col="name")
    tf.grid(row=1,column=0,sticky="nsew")
    all_r=[(s["ID"],s["Name"],s.get("Class",""),s.get("Department",""),
            s.get("Email",""),s.get("Phone","")) for s in students]
    def populate(q=""):
        tv.delete(*tv.get_children())
        for sid,nm,cl,dp,em,ph in all_r:
            if not q or q in nm.lower() or q in sid.lower():
                tv.insert("","end",iid=sid,values=(sid,nm,cl,dp,em,ph))
    populate(); sv.trace("w",lambda *_:populate(sv.get().lower().strip()))
    ef=tk.Frame(body,bg=th.T["card"],padx=14,pady=12)
    ef.grid(row=2,column=0,sticky="ew",pady=(10,0)); ef.columnconfigure((0,1,2,3),weight=1)
    efields={}
    for i,(lb,key) in enumerate(zip(["NAME","CLASS","EMAIL","PHONE"],["Name","Class","Email","Phone"])):
        tk.Label(ef,text=lb,fg=th.T["muted"],bg=th.T["card"],font=th.F["label"]).grid(row=0,column=i,sticky="w",padx=6)
        e2=W.plain_entry(ef); e2.config(state="disabled")
        e2.grid(row=1,column=i,sticky="ew",padx=6,pady=(2,0)); efields[key]=e2
    def on_sel(evt):
        sel=tv.selection()
        if not sel: return
        s=db.student_get(tv.item(sel[0],"values")[0])
        if not s: return
        for key,e2 in efields.items():
            e2.config(state="normal"); e2.delete(0,"end"); e2.insert(0,s.get(key,""))
    tv.bind("<<TreeviewSelect>>",on_sel)
    def do_save():
        sel=tv.selection()
        if not sel: messagebox.showwarning("No Selection","Select a student.",parent=m); return
        db.student_update(sel[0],**{k:e2.get().strip() for k,e2 in efields.items()})
        messagebox.showinfo("Saved","Student updated.",parent=m); m.destroy(); A.refresh_stats()
    bf=tk.Frame(body,bg=th.T["page"]); bf.grid(row=3,column=0,sticky="ew",pady=(8,0))
    W.btn_primary(bf,"  Save",do_save,pack=False).pack(side="left",fill="x",expand=True,padx=(0,8))
    tk.Button(bf,text="Close",command=m.destroy,fg=th.T["text2"],bg=th.T["card2"],
              activebackground=th.T["hover"],relief="flat",font=th.F["body"],
              cursor="hand2",pady=9).pack(side="right")

def _show_deregister(A):
    if not db.students_all():
        messagebox.showinfo("No Students","No students registered.",parent=A.window); return
    m,hdr,body=W.modal(A.window,"Remove Student",720,520,th.T["red"])
    body.rowconfigure(1,weight=1)
    sv=tk.StringVar()
    W.search_entry(body,sv).grid(row=0,column=0,sticky="ew",pady=(0,8))
    tv,tf=W.treeview(body,cols=("id","name","cls","dept","reg"),
                     heads=("ID","  Name","Class","Department","Registered"),
                     widths=[80,175,110,120,130],style="RD.Treeview",stretch_col="name")
    tf.grid(row=1,column=0,sticky="nsew")

    # live list pulled from db so it shrinks after each removal
    def _rows(): return [(s["ID"],s["Name"],s.get("Class",""),s.get("Department",""),s.get("RegisteredOn",""))
                         for s in db.students_all()]

    count_lbl=tk.Label(body,text="",fg=th.T["muted"],bg=th.T["page"],font=th.F["xs"])
    count_lbl.grid(row=2,column=0,sticky="w",pady=(4,0))

    def populate(q=""):
        tv.delete(*tv.get_children())
        rows=_rows()
        for sid,nm,cl,dp,rg in rows:
            if not q or q in nm.lower() or q in sid.lower():
                tv.insert("","end",iid=sid,values=(sid,nm,cl,dp,rg))
        count_lbl.configure(text=f"Total registered: {len(rows)}")

    populate(); sv.trace("w",lambda *_:populate(sv.get().lower().strip()))

    info=tk.Label(body,text="Select a student, then click Remove",
                  fg=th.T["muted"],bg=th.T["page"],font=th.F["sm"])
    info.grid(row=3,column=0,sticky="w",pady=(4,0))

    def do_remove():
        sel=tv.selection()
        if not sel: messagebox.showwarning("No Selection","Select a student.",parent=m); return
        sid=sel[0]; nm=tv.item(sid,"values")[1]
        if not messagebox.askyesno("Confirm Remove",
            f"Remove '{nm}'?\n\nThis will also delete ALL their attendance records.\nThis cannot be undone.",
            parent=m): return
        A.do_remove_student(sid,nm)
        tv.delete(sid)
        populate(sv.get().lower().strip())   # refresh count
        info.configure(text=f"\u2713  '{nm}' removed — attendance records deleted.",fg=th.T["green"])

    bf=tk.Frame(body,bg=th.T["page"]); bf.grid(row=4,column=0,sticky="ew",pady=(8,0))
    W.btn_danger(bf,"  Remove Student",do_remove,pack=False).pack(side="left",fill="x",expand=True,padx=(0,8))
    tk.Button(bf,text="Close",command=m.destroy,fg=th.T["text2"],bg=th.T["card2"],
              activebackground=th.T["hover"],relief="flat",font=th.F["body"],
              cursor="hand2",pady=9).pack(side="right")
