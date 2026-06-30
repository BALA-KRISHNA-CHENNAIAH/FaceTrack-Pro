"""
app.py — FaceTrack
Main entry point. Contains AppState and all business logic.
UI is built by src/ui.py.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import tkinter as tk
from tkinter import messagebox
import cv2, time, datetime, threading

from config  import *
import storage   as db
import recognition as rec
import theme     as th
import widgets   as W
import ui        as UI


# ══════════════════════════════════════════════════════════════════
#  APP STATE
# ══════════════════════════════════════════════════════════════════

class AppState:
    window        = None
    g_auto        = False
    g_cooldown    = {}
    _model_ready  = False
    _session_user = "admin"
    _tick_job     = None
    _period_job   = None
    # UI widget refs (set by ui.py builder)
    status_lbl    = None
    clock_lbl     = None
    period_lbl    = None
    period_subj_lbl = None
    period_time_lbl = None
    cam_dot       = None
    cam_btn       = None
    tv_log        = None
    cls_var       = None
    cls_btn       = None
    v_reg = v_att = v_late = None
    views         = {}
    active_view   = None
    nav_btns      = {}
    show_view     = None  # injected by ui.py

    def set_status(self, msg, color=None):
        try: self.status_lbl.configure(text=msg, fg=color or th.T["text2"])
        except Exception: pass

    def refresh_stats(self):
        try:
            sc = db.student_count()
            self.v_reg.configure(text=str(sc))
            self.v_att.configure(text=str(db.att_count_today()))
            self.v_late.configure(text=str(db.late_count_today()))
            # Show / hide face-data warning banner on dashboard
            missing = sc - rec.enc_count()
            if hasattr(self, "face_warn_lbl") and self.face_warn_lbl:
                if missing > 0 and sc > 0:
                    self.face_warn_lbl.configure(
                        text=f"  ⚠  {missing} student(s) have no face data — "
                             f"go to Settings > Face Data to fix   ",
                        fg=th.T["orange"])
                    self.face_warn_lbl.pack(fill="x")
                else:
                    self.face_warn_lbl.pack_forget()
        except Exception: pass

    def reload_log(self):
        try:
            self.tv_log.delete(*self.tv_log.get_children())
            cf = self.cls_var.get() if self.cls_var else "All"
            for r in reversed(db.att_today()):
                if cf != "All" and r.get("Class","") != cf: continue
                lt = f"  Late +{r.get('LateMinutes','0')} min" if r.get("IsLate","0")=="1" else ""
                tag = "late" if r.get("IsLate","0")=="1" else "ok"
                self.tv_log.insert("","end",
                    values=(r["Name"], r["Class"], r["Time"], r.get("Subject",""), lt),
                    tags=(tag,))
            self.tv_log.tag_configure("late", foreground=th.T["tag_late"])
            self.tv_log.tag_configure("ok",   foreground=th.T["tag_ok"])
        except Exception: pass

    def refresh_class_menu(self):
        try:
            opts = ["All"] + db.class_list()
            m2 = tk.Menu(self.cls_btn, tearoff=0,
                         bg=th.T["card"], fg=th.T["text"],
                         activebackground=th.T["accent"],
                         activeforeground="white",
                         font=th.F["sm"], relief="flat")
            for o in opts:
                m2.add_radiobutton(label=o, variable=self.cls_var, value=o,
                                   command=lambda:(self.reload_log(), self.refresh_stats()))
            self.cls_btn.configure(menu=m2)
        except Exception: pass

    def update_period_display(self):
        try:
            p = db.current_active_period()
            if p:
                s  = p.get("Subject","")
                st = p.get("StartTime","")
                en = p.get("EndTime","")
                self.period_lbl.configure(text=f"● {s}   {st}–{en}", fg=th.T["period_active"])
            else:
                nxt, nxt_t = db.next_upcoming_period()
                if nxt:
                    mins = max(0,int((nxt_t-datetime.datetime.now()).total_seconds()/60))
                    self.period_lbl.configure(
                        text=f"Next: {nxt.get('Subject','')} in {mins}m", fg=th.T["muted"])
                else:
                    self.period_lbl.configure(text="No active period", fg=th.T["muted"])
        except Exception: pass
        try: self._period_job = self.window.after(20000, self.update_period_display)
        except Exception: pass

    def safe_quit(self):
        self.g_auto = False
        try:
            if self._tick_job:   self.window.after_cancel(self._tick_job)
            if self._period_job: self.window.after_cancel(self._period_job)
        except Exception: pass
        self.window.after(150, self._quit_finish)

    def _quit_finish(self):
        db.audit("LOGOUT","Logged out",self._session_user)
        try: self.window.destroy()
        except Exception: pass

    def cycle_theme(self):
        """Instant theme switch — rebuild window."""
        self.g_auto = False
        try:
            if self._tick_job:   self.window.after_cancel(self._tick_job)
            if self._period_job: self.window.after_cancel(self._period_job)
        except Exception: pass
        prev = self.active_view or "dashboard"
        new = th.cycle()
        db.setting_set("theme", new)
        th.apply_ttk_styles()
        try: self.window.destroy()
        except Exception: pass
        self._build_and_run(start_view=prev)

    def _build_and_run(self, start_view="dashboard"):
        win = UI.build_main_window(self)
        self._tick(); win.after(100, lambda: [
            self.refresh_stats(), self.reload_log(),
            self.refresh_class_menu(), self.update_period_display()])
        win.after(200, lambda: self.show_view(start_view))
        win.protocol("WM_DELETE_WINDOW", self.safe_quit)
        win.mainloop()

    def _tick(self):
        try:
            self.clock_lbl.config(text=datetime.datetime.now().strftime("%I:%M:%S %p"))
            self._tick_job = self.window.after(500, self._tick)
        except Exception: pass


# ══════════════════════════════════════════════════════════════════
#  REGISTRATION
# ══════════════════════════════════════════════════════════════════

    def do_register(self, fields):
        sid   = fields["id"].get().strip()
        name  = fields["name"].get().strip()
        cls   = fields["class"].get().strip()
        dept  = fields["dept"].get().strip()
        role  = fields["role"].get().strip() or "Student"
        email = fields["email"].get().strip()
        phone = fields["phone"].get().strip()
        addr  = fields["address"].get().strip()

        if not sid:
            sid = db.next_student_id()
            fields["id"].delete(0,"end"); fields["id"].insert(0,sid)

        if not name: messagebox.showerror("Error","Full name is required.",parent=self.window); return
        if not cls:  messagebox.showerror("Error","Class is required.",parent=self.window); return

        if db.student_exists(sid):
            next_id = db.next_student_id()
            if messagebox.askyesno("ID Exists",
                f"Student ID '{sid}' is already registered.\n\n"
                f"Use next available ID '{next_id}' instead?", parent=self.window):
                sid = next_id
                fields["id"].delete(0,"end"); fields["id"].insert(0,sid)
            else: return

        if not self._model_ready:
            messagebox.showerror("Not Ready",
                "Face recognition engine is still loading.\nPlease wait.",
                parent=self.window); return

        self.set_status(f"Opening camera for {name}…", th.T["orange"])

        def _run():
            def _s(m): self.window.after(0, lambda msg=m: self.set_status(msg, th.T["orange"]))
            ok, photos, embs, err = rec.register_student(sid, name, status_cb=_s)
            self.window.after(0, lambda: self._reg_done(
                ok, photos, embs, err, fields, sid, name, cls, dept, role, email, phone, addr))

        threading.Thread(target=_run, daemon=True).start()

    def _reg_done(self, ok, photos, embs, err, fields, sid, name, cls, dept, role, email, phone, addr):
        if not ok:
            messagebox.showerror("Registration Failed", err, parent=self.window)
            self.set_status("Registration failed — try again", th.T["red"]); return
        db.student_add(sid, name, cls, dept, role, email, phone, addr)
        self.refresh_stats(); self.reload_log(); self.refresh_class_menu()
        self.set_status(f"✓  {name} registered (ID:{sid})", th.T["green"])
        W.toast(self.window,"Student Registered",f"{name} — ID:{sid}")
        messagebox.showinfo("Registered",
            f"'{name}' registered successfully!\n\nID: {sid}\nPhotos: {photos}\nFace profiles: {embs}",
            parent=self.window)
        for e in fields.values(): e.delete(0,"end")
        fields["role"].insert(0,"Student")
        fields["id"].insert(0, db.next_student_id())
        if "students" in self.views:
            try: self.views["students"][1].get("refresh",lambda:None)()
            except Exception: pass

    def do_remove_student(self, sid, name):
        db.student_remove(sid); rec.enc_remove(sid)
        db.remove_student_from_attendance(sid)   # purge from all attendance CSVs
        pdir = os.path.join(DIR_PHOTOS, sid)
        if os.path.exists(pdir):
            for fn in os.listdir(pdir):
                try: os.remove(os.path.join(pdir,fn))
                except Exception: pass
            try: os.rmdir(pdir)
            except Exception: pass
        # Reload today's attendance log so the removed student disappears immediately
        self.reload_log()
        self.refresh_stats()
        self.refresh_class_menu()
        # Refresh the students-view list if it is open
        if "students" in self.views:
            refs = self.views["students"][1]
            if "refresh" in refs:
                try: refs["refresh"]()
                except Exception: pass
        self.set_status(f"✓  '{name}' removed & attendance records purged", th.T["green"])


# ══════════════════════════════════════════════════════════════════
#  CAMERA LOOP
# ══════════════════════════════════════════════════════════════════

    def toggle_auto(self):
        if self.g_auto:
            self.g_auto = False
            self.set_status("Stopping camera…", th.T["orange"])
            return
        if not self._model_ready:
            messagebox.showerror("Not Ready","Face recognition engine is still loading.",
                                  parent=self.window); return
        if rec.enc_count() == 0:
            sc = db.student_count()
            if sc > 0:
                ans = messagebox.askyesno(
                    "Face Data Missing",
                    f"{sc} student(s) are registered in the system, but NO face data\n"
                    f"(embeddings) were found in the Embeddings folder.\n\n"
                    f"This usually means:\n"
                    f"  • Registration was done without the face-capture step\n"
                    f"  • The face recognition model was not loaded at registration time\n"
                    f"  • Embedding files were moved or deleted\n\n"
                    f"Would you like to open Settings > Face Data to rebuild or re-register?",
                    parent=self.window)
                if ans:
                    from src import ui as UI2
                    UI2._show_settings(self, tab="facedata")
            else:
                messagebox.showerror("No Students",
                    "No students are registered.\nGo to Students and register first.",
                    parent=self.window)
            return
        self.g_auto = True
        self.set_status("Attendance camera active — press Q to stop", th.T["green"])
        threading.Thread(target=self._camera_loop, daemon=True).start()

    def _camera_loop(self):
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            self.window.after(0, lambda: messagebox.showerror("Camera","Cannot open webcam.",parent=self.window))
            self.window.after(0, self._stop_auto); return

        wname = "FaceTrack Pro — Attendance Camera  [Q to stop]"
        cv2.namedWindow(wname, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(wname, 1100, 700)

        # ── Bring attendance camera window to foreground ──────────
        try:
            cv2.setWindowProperty(wname, cv2.WND_PROP_TOPMOST, 1)
        except Exception:
            pass
        import sys as _s2, ctypes as _c2, time as _t2
        if _s2.platform == "win32":
            try:
                import ctypes.wintypes as _w2
                _t2.sleep(0.3)
                u32 = _c2.windll.user32; k32 = _c2.windll.kernel32
                _EW = u32.EnumWindows
                _EWP= _c2.WINFUNCTYPE(_c2.c_bool,_w2.HWND,_w2.LPARAM)
                _GWT= u32.GetWindowTextW; _GWL= u32.GetWindowTextLengthW
                _fh=[None]
                def _acb(hwnd,lp):
                    n=_GWL(hwnd)+1; buf=_c2.create_unicode_buffer(n)
                    _GWT(hwnd,buf,n)
                    if wname[:25] in buf.value: _fh[0]=hwnd; return False
                    return True
                _EW(_EWP(_acb),0)
                if _fh[0]:
                    fg = u32.GetForegroundWindow()
                    fgt= u32.GetWindowThreadProcessId(fg,None)
                    ourt=k32.GetCurrentThreadId()
                    if fgt!=ourt: u32.AttachThreadInput(fgt,ourt,True)
                    u32.ShowWindow(_fh[0],9)
                    u32.SetWindowPos(_fh[0],_w2.HWND(-1),0,0,0,0,0x0002|0x0001)
                    u32.SetForegroundWindow(_fh[0])
                    if fgt!=ourt: u32.AttachThreadInput(fgt,ourt,False)
            except Exception: pass

        skip  = int(db.setting("frame_skip", str(FRAME_SKIP)))
        cool  = int(db.setting("cooldown",   str(COOLDOWN_SECONDS)))
        font  = cv2.FONT_HERSHEY_SIMPLEX
        fc    = 0; cached = []
        rec.clear_liveness_trackers()

        active_period   = None
        current_subject = "General"
        marked_for_subj = set()
        last_day = datetime.date.today().strftime("%d-%m-%Y")

        self.window.after(0, lambda: (
            self.cam_dot.configure(text="⬤  LIVE", fg=th.T["cam_online"])
            if self.cam_dot else None))

        while self.g_auto:
            today = datetime.date.today().strftime("%d-%m-%Y")
            if today != last_day:
                marked_for_subj.clear(); self.g_cooldown.clear()
                last_day = today; rec.clear_liveness_trackers()

            new_period = db.current_active_period()
            timetable_exists = len(db.timetable_all()) > 0

            if new_period != active_period or (
               new_period and new_period.get("Subject") != current_subject):
                active_period = new_period
                if active_period:
                    current_subject = active_period.get("Subject","General")
                    marked_for_subj = db.marked_ids_for_subject_today(current_subject)
                else:
                    # No active period — always block marking regardless of timetable state
                    current_subject = None
                    marked_for_subj = set()

            ret, frame = cam.read()
            if not ret: time.sleep(0.05); continue
            fc += 1

            if fc % skip == 0:
                faces = rec.detect_faces(frame); cached = []
                for fd in faces:
                    x1,y1,x2,y2 = fd["bbox"]
                    face_id = f"{x1//30}_{y1//30}"
                    checker = rec.get_liveness_tracker(face_id)
                    is_live, ear = checker.update(frame, fd["bbox"])
                    sid, conf = rec.match_face(fd["embedding"])
                    cached.append((fd["bbox"], sid, conf, is_live, ear))

            for bx, sid, conf, is_live, ear in cached:
                x1,y1,x2,y2 = bx

                if not is_live:
                    cv2.rectangle(frame,(x1,y1),(x2,y2),(60,60,200),2)
                    cv2.putText(frame,"Blink to verify",(x1,y1-8),font,0.62,(60,60,200),2)
                    continue

                if sid:
                    s  = db.student_get(sid)
                    nm = s["Name"] if s else sid
                    cls= s.get("Class","") if s else ""
                    in_cool = (time.time()-self.g_cooldown.get(sid,0)) < cool

                    can_mark = False
                    # Always require an active scheduled period to mark attendance
                    if active_period and current_subject and sid not in marked_for_subj and not in_cool:
                        can_mark = True

                    if can_mark:
                        il,lm = db.mark_attendance(sid,nm,cls,conf,"Auto",current_subject or "General")
                        marked_for_subj.add(sid); self.g_cooldown[sid] = time.time()
                        row_data = [sid,nm,time.strftime("%H:%M:%S"),il,lm,current_subject]
                        self.window.after(0, lambda r=row_data: self._on_mark(r))
                        col=(30,160,80)
                        cv2.rectangle(frame,(x1,y1),(x2,y2),col,3)
                        ts_str=datetime.datetime.now().strftime("%H:%M:%S")
                        self._draw_banner(frame,
                            [f"MARKED", nm, f"Subject: {current_subject}", f"Time: {ts_str}"],
                            (10,100,45),x1,y1,x2,y2)
                        cv2.putText(frame,f"{conf:.0f}% match",(x1,y2+18),font,0.48,col,1)

                    elif sid in marked_for_subj:
                        col=(30,160,200)
                        cv2.rectangle(frame,(x1,y1),(x2,y2),col,2)
                        self._draw_banner(frame,
                            ["ALREADY MARKED", nm, f"Subject: {current_subject}"],
                            (20,100,140),x1,y1,x2,y2)

                    elif not active_period:
                        col=(80,80,80)
                        cv2.rectangle(frame,(x1,y1),(x2,y2),col,2)
                        cv2.putText(frame,nm,(x1,y1-8),font,0.68,col,2)
                        self._draw_banner(frame,["No active period right now"],
                            (50,50,50),x1,y1,x2,y2)
                    else:
                        col=(180,130,0)
                        cv2.rectangle(frame,(x1,y1),(x2,y2),col,2)
                        cv2.putText(frame,nm,(x1,y1-8),font,0.7,col,2)
                else:
                    # Unrecognised — do NOT save/count; just draw a box
                    cv2.rectangle(frame,(x1,y1),(x2,y2),(180,30,30),2)
                    cv2.putText(frame,"Unrecognised",(x1,y1-8),font,0.65,(180,30,30),2)

            # HUD
            fh2, fw = frame.shape[:2]
            cv2.rectangle(frame,(0,0),(fw,44),(8,15,35),-1)
            cv2.putText(frame,
                f"  FaceTrack Pro  |  {datetime.datetime.now().strftime('%H:%M:%S')}  |  Marked: {len(marked_for_subj)}",
                (8,18), font, 0.57, (160,200,255), 1)
            period_txt = (f"  Subject: {current_subject}" if (active_period and current_subject) else
                          "  No active period — attendance BLOCKED")
            cv2.putText(frame, period_txt, (8,38), font, 0.5,
                        (80,220,120) if (active_period and current_subject) else (120,120,120), 1)
            cv2.putText(frame,"  Press Q to stop",(fw-170,18),font,0.5,(160,200,255),1)

            cv2.imshow(wname, frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.g_auto = False; break

        cam.release(); cv2.destroyAllWindows()
        self.window.after(0, self._stop_auto)

    @staticmethod
    def _draw_banner(frame, lines, bg_color, x1, y1, x2, y2):
        font=cv2.FONT_HERSHEY_SIMPLEX; fh=26; pad=8
        max_w=max((cv2.getTextSize(l,font,0.62,2)[0][0] for l in lines),default=60)
        bw=max(max_w+pad*2,x2-x1); bx1,bx2=x1,x1+bw
        by2=max(y1-4,len(lines)*fh+pad); by1=max(by2-len(lines)*fh-pad,0)
        h,w=frame.shape[:2]
        bx1=max(0,min(bx1,w-1));bx2=max(0,min(bx2,w-1))
        by1=max(0,min(by1,h-1));by2=max(0,min(by2,h-1))
        ov=frame.copy()
        cv2.rectangle(ov,(bx1,by1),(bx2,by2),bg_color,-1)
        cv2.addWeighted(ov,0.78,frame,0.22,0,frame)
        ty=by1+fh
        for line in lines:
            cv2.putText(frame,line,(bx1+pad,ty),font,0.62,(255,255,255),2); ty+=fh

    def _on_mark(self, r):
        sid,nm,ts,il,lm,subject=r
        try:
            s = db.student_get(sid)
            self.tv_log.insert("",0,
                values=(nm, s["Class"] if s else "", ts, subject,
                        f"  Late +{lm} min" if il else ""),
                tags=("late" if il else "ok",))
            self.tv_log.tag_configure("late",foreground=th.T["tag_late"])
            self.tv_log.tag_configure("ok",  foreground=th.T["tag_ok"])
        except Exception: pass
        self.refresh_stats()
        self.set_status(f"✓  {nm} marked for '{subject}' at {ts}", th.T["green"])

    def _stop_auto(self):
        self.g_auto = False
        try:
            if self.cam_dot:
                self.cam_dot.configure(text="⬤  OFFLINE", fg=th.T["cam_offline"])
            if self.cam_btn:
                self.cam_btn.configure(text="  ▶  Start Attendance Camera",
                                        bg=th.T["green"], activebackground=th.T["green"])
            self.set_status("Attendance session stopped", th.T["text2"])
        except Exception: pass


# ══════════════════════════════════════════════════════════════════
#  STARTUP
# ══════════════════════════════════════════════════════════════════

    def startup(self):
        rec.enc_load_all()
        n = rec.enc_count()
        self.refresh_stats(); self.reload_log()
        self.refresh_class_menu(); self.update_period_display()

        sc = db.student_count()
        if n == 0 and sc == 0:
            self.set_status("System ready — register your first student to begin", th.T["cyan"])
        elif n == 0 and sc > 0:
            self.set_status(
                f"⚠  {sc} student(s) registered but NO face data found — "
                f"go to Settings > Face Data to fix this", th.T["orange"])
        else:
            self.set_status(f"Loading face recognition engine…", th.T["orange"])

        def load_bg():
            ok = rec.load_model(
                status_cb=lambda msg: self.window.after(0, lambda: self.set_status(msg, th.T["orange"])))
            if ok:
                self._model_ready = True
                n2 = rec.enc_count(); sc2 = db.student_count()
                if n2 == 0 and sc2 > 0:
                    self.window.after(0, lambda: self.set_status(
                        f"⚠  Engine ready but NO face data for {sc2} student(s) — "
                        f"Settings > Face Data to rebuild", th.T["orange"]))
                    self.window.after(600, lambda: W.toast(
                        self.window, "Face Data Missing",
                        f"{sc2} student(s) registered but no embeddings found",
                        is_success=False))
                else:
                    self.window.after(0, lambda: self.set_status(
                        f"✓  System ready  —  {n2} face profile(s) loaded", th.T["green"]))
                    self.window.after(600, lambda: W.toast(
                        self.window,"System Ready",f"Face recognition active  •  {n2} profile(s)"))
            else:
                self.window.after(0, lambda: self.set_status(
                    "✗  InsightFace not found  —  pip install insightface onnxruntime",
                    th.T["red"]))
                self.window.after(600, lambda: W.toast(
                    self.window,"Engine Not Found",
                    "pip install insightface onnxruntime",is_success=False))

        threading.Thread(target=load_bg, daemon=True).start()


# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    db.init()
    th.apply(db.setting("theme","dark"))

    ok, uname = UI.show_login(db.check_password)
    if not ok: return

    A = AppState()
    A._session_user = uname
    db.audit("LOGIN","User logged in",uname)

    win = UI.build_main_window(A)
    A.window = win
    A._tick()
    win.after(300, A.startup)
    win.protocol("WM_DELETE_WINDOW", A.safe_quit)
    win.mainloop()


if __name__ == "__main__":
    main()
