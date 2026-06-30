"""theme.py — FaceTrack — Four themes with instant switching."""
import sys, os
_src = os.path.dirname(os.path.abspath(__file__))
if _src not in sys.path: sys.path.insert(0, _src)
if __name__ == '__main__': sys.exit(1)
from tkinter import ttk

THEMES = {
"dark": {
    "page":"#0b0f1a","card":"#111827","card2":"#1a2235","hover":"#1e2d47",
    "nav":"#060d1f","nav_sub":"#60a5fa",
    "sidebar":"#080d18","sidebar_text":"#94a3b8","sidebar_sel":"#1d4ed8","sidebar_sel_bg":"#1a2540",
    "accent":"#2563eb","accent2":"#1d4ed8","green":"#10b981","green_bg":"#052e1c",
    "red":"#ef4444","red_bg":"#1f0808","orange":"#f59e0b","orange_bg":"#1f1400",
    "purple":"#8b5cf6","cyan":"#06b6d4","teal":"#14b8a6",
    "text":"#f1f5f9","text2":"#cbd5e1","muted":"#475569",
    "border":"#1e293b","divider":"#1e293b","row_alt":"#0d1520",
    "stat_bg":"#111827","input_bg":"#1a2235","input_border":"#2563eb",
    "tag_late":"#f59e0b","tag_ok":"#10b981","tag_low":"#ef4444",
    "cam_online":"#10b981","cam_offline":"#ef4444",
    "period_active":"#10b981",
},
"light": {
    "page":"#f8fafc","card":"#ffffff","card2":"#f1f5f9","hover":"#e8f0fb",
    "nav":"#1e3a5f","nav_sub":"#bfdbfe",
    "sidebar":"#1e3a5f","sidebar_text":"#93c5fd","sidebar_sel":"#2563eb","sidebar_sel_bg":"#1e40af",
    "accent":"#2563eb","accent2":"#1d4ed8","green":"#059669","green_bg":"#ecfdf5",
    "red":"#dc2626","red_bg":"#fef2f2","orange":"#d97706","orange_bg":"#fffbeb",
    "purple":"#7c3aed","cyan":"#0891b2","teal":"#0f766e",
    "text":"#0f172a","text2":"#334155","muted":"#64748b",
    "border":"#e2e8f0","divider":"#e2e8f0","row_alt":"#f8fafc",
    "stat_bg":"#ffffff","input_bg":"#ffffff","input_border":"#2563eb",
    "tag_late":"#d97706","tag_ok":"#059669","tag_low":"#dc2626",
    "cam_online":"#059669","cam_offline":"#dc2626",
    "period_active":"#059669",
},
"ocean": {
    "page":"#0a1628","card":"#0f2040","card2":"#122448","hover":"#1a3060",
    "nav":"#071020","nav_sub":"#38bdf8",
    "sidebar":"#07111e","sidebar_text":"#7dd3fc","sidebar_sel":"#0284c7","sidebar_sel_bg":"#0c2a44",
    "accent":"#0ea5e9","accent2":"#0284c7","green":"#34d399","green_bg":"#022c22",
    "red":"#fb7185","red_bg":"#1f0a14","orange":"#fbbf24","orange_bg":"#1c1200",
    "purple":"#a78bfa","cyan":"#22d3ee","teal":"#2dd4bf",
    "text":"#e0f2fe","text2":"#bae6fd","muted":"#4e7a9e",
    "border":"#1e3a5f","divider":"#1e3a5f","row_alt":"#0a1e36",
    "stat_bg":"#0f2040","input_bg":"#122448","input_border":"#0ea5e9",
    "tag_late":"#fbbf24","tag_ok":"#34d399","tag_low":"#fb7185",
    "cam_online":"#34d399","cam_offline":"#fb7185",
    "period_active":"#34d399",
},
"slate": {
    "page":"#1e2530","card":"#252d3a","card2":"#2c3547","hover":"#354060",
    "nav":"#161d28","nav_sub":"#94a3b8",
    "sidebar":"#141b25","sidebar_text":"#64748b","sidebar_sel":"#3b82f6","sidebar_sel_bg":"#1e2d45",
    "accent":"#3b82f6","accent2":"#2563eb","green":"#22c55e","green_bg":"#142010",
    "red":"#f87171","red_bg":"#1c0f0f","orange":"#fb923c","orange_bg":"#1c1008",
    "purple":"#c084fc","cyan":"#67e8f9","teal":"#5eead4",
    "text":"#e2e8f0","text2":"#cbd5e1","muted":"#64748b",
    "border":"#334155","divider":"#334155","row_alt":"#1e2837",
    "stat_bg":"#252d3a","input_bg":"#2c3547","input_border":"#3b82f6",
    "tag_late":"#fb923c","tag_ok":"#22c55e","tag_low":"#f87171",
    "cam_online":"#22c55e","cam_offline":"#f87171",
    "period_active":"#22c55e",
},
}

THEME_NAMES = list(THEMES.keys())
_current = "dark"
T = dict(THEMES["dark"])

def apply(name: str):
    global T, _current
    if name in THEMES:
        _current = name; T.clear(); T.update(THEMES[name])

def name() -> str: return _current

def cycle() -> str:
    idx = THEME_NAMES.index(_current) if _current in THEME_NAMES else 0
    new = THEME_NAMES[(idx+1) % len(THEME_NAMES)]
    apply(new); return new

def toggle() -> str: return cycle()

F = {
    "app_title": ("Segoe UI",14,"bold"),
    "h1":        ("Segoe UI",12,"bold"),
    "h2":        ("Segoe UI",11,"bold"),
    "h3":        ("Segoe UI",10,"bold"),
    "body":      ("Segoe UI",10),
    "sm":        ("Segoe UI", 9),
    "xs":        ("Segoe UI", 8),
    "label":     ("Segoe UI", 8,"bold"),
    "clock":     ("Segoe UI",13,"bold"),
    "stat_num":  ("Segoe UI",26,"bold"),
    "nav_item":  ("Segoe UI",10),
    "sidebar_h": ("Segoe UI", 7,"bold"),
}

def apply_ttk_styles():
    try:
        sty = ttk.Style()
        try: sty.theme_use("clam")
        except Exception: pass
        for nm,hfg,sel in [
            ("FT",T["accent"],T["accent"]),
            ("RD",T["red"],  T["red_bg"] if T["red_bg"] else "#3a0000"),
            ("GN",T["green"],T["green_bg"] if T["green_bg"] else "#003a1a"),
            ("OR",T["orange"],T["orange_bg"] if T["orange_bg"] else "#3a1a00"),
            ("PU",T["purple"],"#2a0050"),
        ]:
            sty.configure(f"{nm}.Treeview",
                background=T["card2"],foreground=T["text"],rowheight=30,
                fieldbackground=T["card2"],borderwidth=0,font=F["body"])
            sty.configure(f"{nm}.Treeview.Heading",
                background=T["page"],foreground=hfg,relief="flat",
                font=("Segoe UI",9,"bold"))
            sty.map(f"{nm}.Treeview",
                background=[("selected",sel)],foreground=[("selected","white")])
        for orient in ("Vertical","Horizontal"):
            sty.configure(f"{orient}.TScrollbar",
                background=T["card2"],troughcolor=T["page"],
                arrowcolor=T["muted"],borderwidth=0)
        sty.configure("TNotebook",background=T["page"],borderwidth=0)
        sty.configure("TNotebook.Tab",
            background=T["card2"],foreground=T["muted"],
            padding=[14,7],font=F["sm"])
        sty.map("TNotebook.Tab",
            background=[("selected",T["card"])],
            foreground=[("selected",T["accent"])],
            font=[("selected",("Segoe UI",9,"bold"))])
    except Exception: pass
