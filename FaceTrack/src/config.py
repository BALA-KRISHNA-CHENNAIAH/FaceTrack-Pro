"""config.py — FaceTrack — Application constants and paths."""
import os

APP_NAME        = "FaceTrack Pro"
APP_SUBTITLE    = "Classroom Attendance System"

INSIGHTFACE_MODEL     = "buffalo_l"
RECOGNITION_THRESH    = 0.40
LIVENESS_EAR_THRESH   = 0.22
LIVENESS_BLINK_FRAMES = 2
PHOTOS_PER_STUDENT    = 5
PHOTO_INTERVAL_SEC    = 1.0
COOLDOWN_SECONDS      = 15
FRAME_SKIP            = 2

# Attendance window: opens ATT_BUFFER_BEFORE min before start,
# closes ATT_BUFFER_AFTER min after start
ATT_BUFFER_BEFORE = 5
ATT_BUFFER_AFTER  = 5

DAYS_OF_WEEK = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_DATA       = os.path.join(BASE_DIR,"Data")
DIR_PHOTOS     = os.path.join(DIR_DATA,"Photos")
DIR_ATTENDANCE = os.path.join(DIR_DATA,"Attendance")
DIR_EMBEDDINGS = os.path.join(DIR_DATA,"Embeddings")
DIR_UNKNOWN    = os.path.join(DIR_DATA,"UnknownFaces")
DIR_REPORTS    = os.path.join(DIR_DATA,"Reports")
DIR_BACKUPS    = os.path.join(DIR_DATA,"Backups")
DIR_MODELS     = os.path.join(BASE_DIR,"Models")

FILE_STUDENTS    = os.path.join(DIR_DATA,"students.csv")
FILE_HOLIDAYS    = os.path.join(DIR_DATA,"holidays.csv")
FILE_AUDIT       = os.path.join(DIR_DATA,"audit.csv")
FILE_SETTINGS    = os.path.join(DIR_DATA,"settings.csv")
FILE_PASSWORD    = os.path.join(DIR_DATA,"password.txt")
FILE_TIMETABLE   = os.path.join(DIR_DATA,"timetable.csv")
FILE_UNKNOWN_LOG = os.path.join(DIR_DATA,"unknown_log.csv")
FILE_ABOUT       = os.path.join(DIR_DATA,"about.txt")

COLS_STUDENTS   = ["ID","Name","Class","Department","Role","Email","Phone","Address","RegisteredOn"]
COLS_ATTENDANCE = ["ID","Name","Class","Date","Time","Confidence","IsLate","LateMinutes","Method","Subject"]
COLS_HOLIDAYS   = ["Date","Name","Type"]
COLS_AUDIT      = ["Timestamp","Action","Description","By","Result"]
COLS_TIMETABLE  = ["Day","Period","Subject","StartTime","EndTime"]
COLS_UNKNOWN    = ["PhotoPath","Date","Time","Reviewed","Note"]

DEFAULT_SETTINGS = [
    ["institution_name","My Institution"],
    ["institution_address",""],
    ["start_time","09:00"],
    ["late_after","15"],
    ["tolerance","0.40"],
    ["cooldown","15"],
    ["frame_skip","2"],
    ["photos","5"],
    ["low_att_threshold","75"],
    ["theme","dark"],
    ["about_text","Developed by: \nInstitution: \nContact: "],
]

HAAR_URL = ("https://raw.githubusercontent.com/opencv/opencv/master"
            "/data/haarcascades/haarcascade_frontalface_default.xml")
