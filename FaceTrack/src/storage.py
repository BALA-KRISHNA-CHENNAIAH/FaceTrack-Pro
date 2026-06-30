"""storage.py — FaceTrack — Pure CSV data persistence."""
import os, csv, datetime, hashlib, zipfile, sys
_src = os.path.dirname(os.path.abspath(__file__))
if _src not in sys.path: sys.path.insert(0,_src)
if __name__ == '__main__': sys.exit(1)
from config import *

def init():
    for d in [DIR_DATA,DIR_PHOTOS,DIR_ATTENDANCE,DIR_EMBEDDINGS,
              DIR_UNKNOWN,DIR_REPORTS,DIR_BACKUPS,DIR_MODELS]:
        os.makedirs(d,exist_ok=True)
    _init_csv(FILE_STUDENTS,COLS_STUDENTS)
    _init_csv(FILE_HOLIDAYS,COLS_HOLIDAYS)
    _init_csv(FILE_AUDIT,COLS_AUDIT)
    _init_csv(FILE_UNKNOWN_LOG,COLS_UNKNOWN)
    _init_csv(FILE_TIMETABLE,COLS_TIMETABLE)
    if not os.path.isfile(FILE_SETTINGS): _write_raw(FILE_SETTINGS,DEFAULT_SETTINGS)
    if not os.path.isfile(FILE_PASSWORD): _write_text(FILE_PASSWORD,_hash("admin123"))

def _hash(t): return hashlib.sha256(t.encode()).hexdigest()
def _init_csv(path,cols):
    if not os.path.isfile(path):
        with open(path,"w",newline="",encoding="utf-8") as f: csv.writer(f).writerow(cols)
def _read_csv(path):
    if not os.path.isfile(path): return []
    try:
        with open(path,newline="",encoding="utf-8") as f: return list(csv.DictReader(f))
    except Exception: return []
def _append_csv(path,row):
    with open(path,"a",newline="",encoding="utf-8") as f: csv.writer(f).writerow(row)
def _write_raw(path,rows):
    with open(path,"w",newline="",encoding="utf-8") as f: csv.writer(f).writerows(rows)
def _write_dicts(path,cols,rows):
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(rows)
def _read_text(path):
    try: return open(path,encoding="utf-8").read().strip()
    except Exception: return ""
def _write_text(path,text): open(path,"w",encoding="utf-8").write(text)

# Settings
def setting(key,default=""):
    try:
        with open(FILE_SETTINGS,newline="",encoding="utf-8") as f:
            for row in csv.reader(f):
                if row and row[0]==key: return row[1] if len(row)>1 else default
    except Exception: pass
    return default

def setting_set(key,value):
    rows=[]; found=False
    try:
        with open(FILE_SETTINGS,newline="",encoding="utf-8") as f: rows=list(csv.reader(f))
    except Exception: pass
    for i,r in enumerate(rows):
        if r and r[0]==key: rows[i]=[key,value]; found=True; break
    if not found: rows.append([key,value])
    _write_raw(FILE_SETTINGS,rows)

# Auth
def check_password(pw): return _read_text(FILE_PASSWORD)==_hash(pw)
def save_password(pw): _write_text(FILE_PASSWORD,_hash(pw))

# About text (stored in a plain .txt file to avoid CSV newline issues)
def about_read():
    try:
        with open(FILE_ABOUT, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "Developed by: \nInstitution: \nContact: "

def about_write(text):
    try:
        with open(FILE_ABOUT, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            import os as _os
            _os.fsync(f.fileno())
        return True
    except Exception:
        return False

# Audit
def audit(action,description,by="admin",result="OK"):
    _append_csv(FILE_AUDIT,[datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                             action,description,by,result])
def audit_read(limit=500): return list(reversed(_read_csv(FILE_AUDIT)[-limit:]))

# Students
def students_all(): return _read_csv(FILE_STUDENTS)
def student_get(sid): return next((s for s in students_all() if s["ID"]==str(sid)),None)
def student_exists(sid): return student_get(sid) is not None
def student_count(): return len(students_all())

def next_student_id():
    existing={s["ID"] for s in students_all()}
    i=1
    while str(i) in existing: i+=1
    return str(i)

def student_add(sid,name,cls,dept,role,email,phone,address=""):
    now=datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    _append_csv(FILE_STUDENTS,[sid,name,cls,dept,role,email,phone,address,now])
    audit("REGISTER",f"Registered {name} (ID:{sid})")

def student_update(sid,**kwargs):
    rows=students_all()
    for r in rows:
        if r["ID"]==str(sid): r.update(kwargs); break
    _write_dicts(FILE_STUDENTS,COLS_STUDENTS,rows)
    audit("UPDATE",f"Updated student ID:{sid}")

def student_remove(sid):
    rows=[s for s in students_all() if s["ID"]!=str(sid)]
    _write_dicts(FILE_STUDENTS,COLS_STUDENTS,rows)
    audit("REMOVE",f"Removed student ID:{sid}")

def remove_student_from_attendance(sid):
    """Delete all attendance records for a student across every attendance CSV."""
    sid=str(sid); changed=0
    for date_str in all_att_dates():
        path=att_filepath(date_str)
        rows=_read_csv(path)
        filtered=[r for r in rows if r.get("ID")!=sid]
        if len(filtered)!=len(rows):
            _write_dicts(path,COLS_ATTENDANCE,filtered); changed+=1
    if changed:
        audit("REMOVE_ATT",f"Removed attendance records for ID:{sid} from {changed} file(s)")

def class_list(): return sorted({s["Class"] for s in students_all() if s.get("Class","")})
def department_list(): return sorted({s["Department"] for s in students_all() if s.get("Department","")})

# Attendance
def att_filepath(date_str=None):
    d=date_str or datetime.date.today().strftime("%d-%m-%Y")
    return os.path.join(DIR_ATTENDANCE,f"Attendance_{d}.csv")

def att_read(date_str=None): return _read_csv(att_filepath(date_str))
def att_today(): return att_read()
def marked_ids_today(): return {r["ID"] for r in att_today()}
def att_count_today(): return len(marked_ids_today())
def late_count_today(): return sum(1 for r in att_today() if r.get("IsLate","0")=="1")
def all_att_dates():
    if not os.path.isdir(DIR_ATTENDANCE): return []
    return sorted([fn.replace("Attendance_","").replace(".csv","")
                   for fn in os.listdir(DIR_ATTENDANCE)
                   if fn.startswith("Attendance_") and fn.endswith(".csv")])

def marked_ids_for_subject_today(subject):
    today=datetime.date.today().strftime("%d-%m-%Y")
    return {r["ID"] for r in att_read(today) if r.get("Subject","General")==subject}

def mark_attendance(sid,name,cls,confidence,method="Auto",subject="General"):
    now=datetime.datetime.now()
    date_str=now.strftime("%d-%m-%Y"); time_str=now.strftime("%H:%M:%S")
    is_late=0; late_min=0
    try:
        start=setting("start_time","09:00"); thresh=int(setting("late_after","15"))
        sdt=datetime.datetime.strptime(f"{date_str} {start}","%d-%m-%Y %H:%M")
        ldt=sdt+datetime.timedelta(minutes=thresh)
        if now>ldt: is_late=1; late_min=int((now-sdt).total_seconds()/60)
    except Exception: pass
    path=att_filepath(date_str); new_file=not os.path.isfile(path)
    with open(path,"a",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        if new_file: w.writerow(COLS_ATTENDANCE)
        w.writerow([sid,name,cls,date_str,time_str,round(confidence,1),is_late,late_min,method,subject])
    return bool(is_late),late_min

# Timetable
def timetable_all(): return _read_csv(FILE_TIMETABLE)

def timetable_for_day(day_abbr):
    rows=[r for r in timetable_all() if r.get("Day","")==day_abbr]
    try: rows.sort(key=lambda r:r.get("StartTime",""))
    except Exception: pass
    return rows

def _time_to_minutes(t):
    """Convert HH:MM to minutes since midnight."""
    try:
        h,m=t.strip().split(":")
        return int(h)*60+int(m)
    except Exception: return -1

def check_overlap(day, start_time, end_time, exclude_index=None):
    """Return True if the proposed period overlaps any existing one on that day."""
    new_s=_time_to_minutes(start_time); new_e=_time_to_minutes(end_time)
    if new_s<0 or new_e<0 or new_e<=new_s: return False, None
    for i,row in enumerate(timetable_all()):
        if row.get("Day","")!=day: continue
        if exclude_index is not None and i==exclude_index: continue
        ex_s=_time_to_minutes(row.get("StartTime",""))
        ex_e=_time_to_minutes(row.get("EndTime",""))
        if ex_s<0 or ex_e<0: continue
        # Overlap if not (new_e<=ex_s or new_s>=ex_e)
        if not (new_e<=ex_s or new_s>=ex_e):
            return True, row.get("Subject","")
    return False, None

def timetable_add(day,period,subject,start_time,end_time):
    _append_csv(FILE_TIMETABLE,[day,period,subject,start_time,end_time])
    audit("TIMETABLE",f"Added {subject} on {day} {start_time}-{end_time}")

def timetable_delete(index):
    rows=timetable_all()
    if 0<=index<len(rows):
        rows.pop(index); _write_dicts(FILE_TIMETABLE,COLS_TIMETABLE,rows)

def subject_list():
    return sorted({r.get("Subject","") for r in timetable_all() if r.get("Subject","")})

def current_active_period():
    """Return period currently within [start-ATT_BUFFER_BEFORE, start+ATT_BUFFER_AFTER]."""
    now=datetime.datetime.now()
    day_abbr=now.strftime("%A")[:3]; date_str=now.strftime("%Y-%m-%d")
    for p in timetable_all():
        if p.get("Day","")!=day_abbr: continue
        try:
            start=datetime.datetime.strptime(f"{date_str} {p['StartTime']}","%Y-%m-%d %H:%M")
            win_open =start-datetime.timedelta(minutes=ATT_BUFFER_BEFORE)
            win_close=start+datetime.timedelta(minutes=ATT_BUFFER_AFTER)
            if win_open<=now<=win_close: return p
        except Exception: pass
    return None

def next_upcoming_period():
    now=datetime.datetime.now()
    day_abbr=now.strftime("%A")[:3]; date_str=now.strftime("%Y-%m-%d")
    upcoming=[]
    for p in timetable_all():
        if p.get("Day","")!=day_abbr: continue
        try:
            start=datetime.datetime.strptime(f"{date_str} {p['StartTime']}","%Y-%m-%d %H:%M")
            win_open=start-datetime.timedelta(minutes=ATT_BUFFER_BEFORE)
            if win_open>now: upcoming.append((start,p))
        except Exception: pass
    if upcoming:
        upcoming.sort(key=lambda x:x[0]); return upcoming[0][1],upcoming[0][0]
    return None,None

# Holidays
def holidays_all(): return _read_csv(FILE_HOLIDAYS)
def holiday_dates(): return {h["Date"] for h in holidays_all()}
def holiday_add(date,name,htype="General"):
    _append_csv(FILE_HOLIDAYS,[date,name,htype])
    audit("HOLIDAY",f"Added holiday: {name} on {date}")
def holiday_delete(index):
    rows=holidays_all()
    if 0<=index<len(rows):
        rows.pop(index); _write_dicts(FILE_HOLIDAYS,COLS_HOLIDAYS,rows)

# Unknown faces
def unknown_log(photo_path):
    now=datetime.datetime.now()
    _append_csv(FILE_UNKNOWN_LOG,[photo_path,now.strftime("%d-%m-%Y"),now.strftime("%H:%M:%S"),"No",""])
def unknown_all(): return _read_csv(FILE_UNKNOWN_LOG)
def unknown_mark_reviewed(index,note=""):
    rows=unknown_all()
    if 0<=index<len(rows):
        rows[index]["Reviewed"]="Yes"; rows[index]["Note"]=note
        _write_dicts(FILE_UNKNOWN_LOG,COLS_UNKNOWN,rows)

# Analytics
def compute_analytics(cls_filter="All"):
    all_dates=all_att_dates(); holidays=holiday_dates()
    working=[d for d in all_dates if d not in holidays]
    total=len(working); low_thr=float(setting("low_att_threshold","75"))
    rows=[]
    for s in students_all():
        if cls_filter!="All" and s.get("Class","")!=cls_filter: continue
        sid=s["ID"]; present=0; late_c=0
        for d in working:
            seen=set()
            for r in att_read(d):
                if r["ID"]==sid and d not in seen:
                    present+=1; seen.add(d)
                    if r.get("IsLate","0")=="1": late_c+=1
                    break
        pct=round(present/total*100,1) if total>0 else 0.0
        rows.append({"id":sid,"name":s["Name"],"class":s.get("Class",""),
                     "dept":s.get("Department",""),"present":present,
                     "total":total,"pct":pct,"late":late_c,"low":pct<low_thr})
    return rows,total

def compute_per_subject_student_analytics(subject,cls_filter="All"):
    all_dates=all_att_dates(); student_counts={}; session_dates=set()
    for d in all_dates:
        day_marked=set()
        for r in att_read(d):
            if r.get("Subject","General")!=subject: continue
            if cls_filter!="All" and r.get("Class","")!=cls_filter: continue
            sid=r["ID"]; key=f"{d}_{sid}"
            if key not in day_marked:
                session_dates.add(d); day_marked.add(key)
                if sid not in student_counts:
                    s=student_get(sid)
                    student_counts[sid]={"name":s["Name"] if s else sid,
                                         "class":s.get("Class","") if s else "",
                                         "present":0,"late":0}
                student_counts[sid]["present"]+=1
                if r.get("IsLate","0")=="1": student_counts[sid]["late"]+=1
    total=len(session_dates); low_thr=float(setting("low_att_threshold","75"))
    rows=[]
    for sid,d in student_counts.items():
        pct=round(d["present"]/total*100,1) if total>0 else 0.0
        rows.append({"id":sid,"name":d["name"],"class":d["class"],
                     "dept":"","present":d["present"],"total":total,
                     "pct":pct,"late":d["late"],"low":pct<low_thr})
    return rows,total

def compute_subject_analytics(cls_filter="All"):
    all_dates=all_att_dates(); subjects={}
    for d in all_dates:
        for r in att_read(d):
            if cls_filter!="All" and r.get("Class","")!=cls_filter: continue
            subj=r.get("Subject","General") or "General"
            if subj not in subjects: subjects[subj]={}
            sid=r["ID"]; subjects[subj][sid]=subjects[subj].get(sid,0)+1
    result=[]
    for subj,counts in sorted(subjects.items()):
        result.append({"subject":subj,"students":len(counts),
                        "sessions":max(counts.values()) if counts else 0,
                        "total_records":sum(counts.values())})
    return result

def get_day_attendance_detail(date_str, subject_filter="All", cls_filter="All"):
    """Return present/absent lists for a given day (and optional subject/class filter).
    Returns (present_list, absent_list) where each item is a dict with id,name,class,dept,subjects,time,is_late.
    """
    records = att_read(date_str)
    all_students = students_all()
    # Build a map: sid -> list of records
    sid_records = {}
    for r in records:
        subj = r.get("Subject","General") or "General"
        if subject_filter != "All" and subj != subject_filter: continue
        sid = r["ID"]
        if sid not in sid_records: sid_records[sid] = []
        sid_records[sid].append(r)
    present = []
    for sid, recs in sid_records.items():
        s = student_get(sid)
        name = s["Name"] if s else sid
        cls  = s.get("Class","") if s else recs[0].get("Class","")
        dept = s.get("Department","") if s else ""
        if cls_filter != "All" and cls != cls_filter: continue
        subjects = ", ".join(sorted({r.get("Subject","General") or "General" for r in recs}))
        times = ", ".join(sorted({r.get("Time","")[:5] for r in recs}))
        is_late = any(r.get("IsLate","0")=="1" for r in recs)
        present.append({"id":sid,"name":name,"class":cls,"dept":dept,
                        "subjects":subjects,"time":times,"is_late":is_late})
    present.sort(key=lambda r:r["name"].lower())
    # Absent = all students not in present
    present_ids = {p["id"] for p in present}
    absent = []
    for s in all_students:
        if cls_filter != "All" and s.get("Class","") != cls_filter: continue
        if s["ID"] not in present_ids:
            absent.append({"id":s["ID"],"name":s["Name"],"class":s.get("Class",""),
                           "dept":s.get("Department","")})
    absent.sort(key=lambda r:r["name"].lower())
    return present, absent

def get_subject_day_detail(subject, date_str, cls_filter="All"):
    """Return (present_list, absent_list) for a specific subject on a specific day."""
    return get_day_attendance_detail(date_str, subject_filter=subject, cls_filter=cls_filter)

def subject_sessions():
    """Return dict of subject -> sorted list of dates when that subject had attendance."""
    all_dates = all_att_dates(); result = {}
    for d in all_dates:
        for r in att_read(d):
            subj = r.get("Subject","General") or "General"
            if subj not in result: result[subj] = set()
            result[subj].add(d)
    return {k: sorted(v) for k,v in result.items()}

# Backup
def create_backup():
    os.makedirs(DIR_BACKUPS,exist_ok=True)
    ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fn=os.path.join(DIR_BACKUPS,f"backup_{ts}.zip")
    with zipfile.ZipFile(fn,"w",zipfile.ZIP_DEFLATED) as zf:
        for root,_,files in os.walk(DIR_DATA):
            if DIR_BACKUPS in root: continue
            for f in files:
                full=os.path.join(root,f); zf.write(full,os.path.relpath(full,BASE_DIR))
    audit("BACKUP",f"Created {os.path.basename(fn)}"); return fn

def restore_backup(zip_path):
    with zipfile.ZipFile(zip_path,"r") as zf: zf.extractall(BASE_DIR)
    audit("RESTORE",f"Restored from {os.path.basename(zip_path)}")

def remove_subject_from_attendance(subject):
    """Delete all attendance records for a subject across every attendance CSV.
    Returns the total number of records deleted."""
    deleted=0; changed_files=0
    for date_str in all_att_dates():
        path=att_filepath(date_str)
        rows=_read_csv(path)
        filtered=[r for r in rows if r.get("Subject","")!=subject]
        removed=len(rows)-len(filtered)
        if removed>0:
            _write_dicts(path,COLS_ATTENDANCE,filtered)
            deleted+=removed; changed_files+=1
    if deleted:
        audit("REMOVE_SUBJ_ATT",
              f"Deleted {deleted} attendance record(s) for subject '{subject}' from {changed_files} file(s)")
    return deleted
