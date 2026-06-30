"""
widgets.py — FaceTrack Pro
Reusable widget factory functions.
All widgets read from theme.T so they update automatically on theme toggle.
"""

import sys, os
_src = os.path.dirname(os.path.abspath(__file__))
if _src not in sys.path:
    sys.path.insert(0, _src)
if __name__ == '__main__':
    print('Run app.py instead:  python app.py')
    sys.exit(1)

import tkinter as tk
from tkinter import ttk
from theme import T, F


# ══════════════════════════════════════════════════════════════════
#  BASIC WIDGETS
# ══════════════════════════════════════════════════════════════════

def label(parent, text, fg=None, font=None, bg=None, anchor="w", **kw):
    return tk.Label(parent,
        text=text,
        fg=fg or T["text"],
        bg=bg or T["card"],
        font=font or F["body"],
        anchor=anchor, **kw)

def muted_label(parent, text, font=None, bg=None, **kw):
    return tk.Label(parent,
        text=text,
        fg=T["muted"],
        bg=bg or T["card"],
        font=font or F["xs"], **kw)

def field_label(parent, text, bg=None):
    """Uppercase field label above an input."""
    lbl = tk.Label(parent,
        text=text,
        fg=T["muted"],
        bg=bg or T["card"],
        font=F["label"])
    lbl.pack(anchor="w", pady=(6,0))
    return lbl

def divider(parent, bg=None, pady=(8,6)):
    tk.Frame(parent,
        bg=bg or T["divider"],
        height=1).pack(fill="x", pady=pady)

def spacer(parent, h=8):
    tk.Frame(parent, bg=T["card"], height=h).pack(fill="x")


# ══════════════════════════════════════════════════════════════════
#  INPUT WIDGETS
# ══════════════════════════════════════════════════════════════════

def entry(parent, show=None, val="", width=None, bg=None):
    """Styled entry with coloured bottom border."""
    container = tk.Frame(parent, bg=T["input_border"], pady=1)
    container.pack(fill="x", pady=(2, 8))
    inner = tk.Frame(container, bg=bg or T["input_bg"])
    inner.pack(fill="x", padx=1, pady=1)
    kw = dict(
        fg=T["text"], bg=bg or T["input_bg"],
        insertbackground=T["accent"],
        relief="flat", font=F["body"], bd=8)
    if show:
        kw["show"] = show
    if width:
        kw["width"] = width
    e = tk.Entry(inner, **kw)
    e.pack(fill="x")
    if val:
        e.insert(0, val)
    return e

def plain_entry(parent, show=None, val="", bg=None):
    """Entry without the border wrapper (for use inside grids)."""
    kw = dict(
        fg=T["text"], bg=bg or T["card2"],
        insertbackground=T["accent"],
        relief="flat", font=F["body"], bd=8)
    if show:
        kw["show"] = show
    e = tk.Entry(parent, **kw)
    if val:
        e.insert(0, val)
    return e

def combobox(parent, values, textvariable=None, width=14):
    sty = ttk.Style()
    sty.configure("FT.TCombobox",
        fieldbackground = T["input_bg"],
        background      = T["input_bg"],
        foreground      = T["text"],
        selectbackground= T["accent"],
        relief          = "flat")
    cb = ttk.Combobox(parent,
        values=values,
        textvariable=textvariable,
        style="FT.TCombobox",
        width=width,
        state="readonly",
        font=F["body"])
    return cb

def search_entry(parent, textvariable, placeholder="Search…"):
    """Search box with placeholder text.
    Returns the outer border frame — the caller places it via .pack()/.grid().
    """
    fr = tk.Frame(parent, bg=T["border"], pady=1)
    # Do NOT pack here — the caller decides the geometry manager.
    inner = tk.Frame(fr, bg=T["card"])
    inner.pack(fill="x", padx=1, pady=1)
    tk.Label(inner, text="🔍", fg=T["muted"],
             bg=T["card"], font=F["sm"]).pack(side="left", padx=(8,0))
    e = tk.Entry(inner, textvariable=textvariable,
                 fg=T["text"], bg=T["card"],
                 insertbackground=T["accent"],
                 relief="flat", font=F["body"], bd=6)
    e.pack(side="left", fill="x", expand=True)
    e.insert(0, placeholder)
    e.config(fg=T["muted"])
    def _fi(ev):
        if e.get() == placeholder:
            e.delete(0,"end"); e.config(fg=T["text"])
    def _fo(ev):
        if not e.get():
            e.insert(0,placeholder); e.config(fg=T["muted"])
    e.bind("<FocusIn>",  _fi)
    e.bind("<FocusOut>", _fo)
    return fr  # Return the outer frame, not the inner Entry


# ══════════════════════════════════════════════════════════════════
#  BUTTONS
# ══════════════════════════════════════════════════════════════════

def btn_primary(parent, text, cmd, bg=None, fg="white",
                pady=9, font=None, pack=True, **kw):
    b = tk.Button(parent, text=text, command=cmd,
                  fg=fg, bg=bg or T["accent"],
                  activebackground=bg or T["accent2"],
                  activeforeground=fg,
                  relief="flat",
                  font=font or ("Segoe UI",10,"bold"),
                  cursor="hand2", pady=pady, **kw)
    if pack:
        b.pack(fill="x", pady=(0,5))
    return b

def btn_secondary(parent, text, cmd, pady=8):
    b = tk.Button(parent, text=text, command=cmd,
                  fg=T["text2"], bg=T["card2"],
                  activebackground=T["hover"],
                  activeforeground=T["text"],
                  relief="flat", font=F["sm"],
                  cursor="hand2", pady=pady)
    b.pack(fill="x", pady=(0,4))
    return b

def btn_icon(parent, text, cmd, bg=None, fg=None, font=None, pady=7, pack=True):
    b = tk.Button(parent, text=text, command=cmd,
                  fg=fg or T["text2"],
                  bg=bg or T["card2"],
                  activebackground=T["hover"],
                  activeforeground=T["text"],
                  relief="flat",
                  font=font or F["sm"],
                  cursor="hand2", pady=pady,
                  anchor="w", padx=12)
    if pack:
        b.pack(fill="x", pady=(0,2))
    return b

def btn_danger(parent, text, cmd, pady=9, pack=True):
    return btn_primary(parent, text, cmd,
                       bg=T["red"], pack=pack, pady=pady)

def btn_success(parent, text, cmd, pady=9, pack=True):
    return btn_primary(parent, text, cmd,
                       bg=T["green"], pack=pack, pady=pady)


# ══════════════════════════════════════════════════════════════════
#  CARDS & SECTIONS
# ══════════════════════════════════════════════════════════════════

def card(parent, padx=16, pady=12, pack=True, **kw):
    f = tk.Frame(parent, bg=T["card"], padx=padx, pady=pady, **kw)
    if pack:
        f.pack(fill="x", pady=(0,8))
    return f

def section_header(parent, title, subtitle=None, accent=None):
    """Section title with optional coloured left accent bar."""
    f = tk.Frame(parent, bg=T["card"])
    f.pack(fill="x", pady=(0,10))

    if accent:
        tk.Frame(f, bg=accent, width=4).pack(side="left", fill="y", padx=(0,10))

    right = tk.Frame(f, bg=T["card"])
    right.pack(side="left", fill="x", expand=True)
    tk.Label(right, text=title, fg=T["text"],
             bg=T["card"], font=F["h1"]).pack(anchor="w")
    if subtitle:
        tk.Label(right, text=subtitle, fg=T["muted"],
                 bg=T["card"], font=F["xs"]).pack(anchor="w", pady=(2,0))
    return f

def stat_card(parent, icon, title, accent):
    """Dashboard stat card. Returns the value label for updating."""
    f = tk.Frame(parent, bg=T["stat_bg"], padx=16, pady=13)
    f.pack(fill="x", pady=(0,8))
    top = tk.Frame(f, bg=T["stat_bg"])
    top.pack(fill="x")
    tk.Label(top, text=icon,  fg=accent,    bg=T["stat_bg"],
             font=("Segoe UI",14)).pack(side="left")
    tk.Label(top, text=title, fg=T["muted"],bg=T["stat_bg"],
             font=F["stat_lbl"]).pack(side="right")
    val = tk.Label(f, text="0", fg=T["text"], bg=T["stat_bg"],
                   font=F["stat_num"])
    val.pack(anchor="w", pady=(2,0))
    tk.Frame(f, bg=accent, height=3).pack(fill="x", pady=(6,0))
    return val

def info_badge(parent, text, bg, fg="white"):
    """Small coloured badge label."""
    return tk.Label(parent, text=f"  {text}  ",
                    fg=fg, bg=bg,
                    font=F["xs"],
                    padx=6, pady=2)


# ══════════════════════════════════════════════════════════════════
#  TREEVIEW
# ══════════════════════════════════════════════════════════════════

def treeview(parent, cols, heads, widths,
             style="FT.Treeview", stretch_col=None,
             height=8, show_scrollbar=True):
    """Treeview with optional vertical scrollbar. Returns (tv, frame).
    NOTE: The caller is responsible for placing the returned frame
    (via .pack() or .grid()), allowing both geometry managers to coexist.
    """
    fr = tk.Frame(parent, bg=T["card"])
    # Do NOT pack/grid here — the caller decides the geometry manager.
    fr.columnconfigure(0, weight=1)
    fr.rowconfigure(0, weight=1)

    tv = ttk.Treeview(fr, style=style, height=height,
                      columns=cols, show="headings")
    for c, h, w in zip(cols, heads, widths):
        st = (c == stretch_col)
        tv.column(c, width=w, anchor="w" if st else "center", stretch=st)
        tv.heading(c, text=h)
    tv.grid(row=0, column=0, sticky="nsew")

    if show_scrollbar:
        sb = ttk.Scrollbar(fr, orient="vertical", command=tv.yview)
        sb.grid(row=0, column=1, sticky="ns")
        tv.configure(yscrollcommand=sb.set)

    return tv, fr


# ══════════════════════════════════════════════════════════════════
#  MODAL WINDOWS
# ══════════════════════════════════════════════════════════════════

def modal(parent, title, width=700, height=520, accent=None):
    """
    Standard modal dialog.
    Returns (modal_window, header_frame, body_frame).
    """
    m = tk.Toplevel(parent)
    m.geometry(f"{width}x{height}")
    m.resizable(True, True)
    m.title(title)
    m.configure(bg=T["page"])
    m.grab_set()
    m.focus_set()
    m.columnconfigure(0, weight=1)
    m.rowconfigure(1, weight=1)

    # Header
    hdr = tk.Frame(m, bg=T["card"], height=52)
    hdr.grid(row=0, column=0, sticky="ew")
    hdr.grid_propagate(False)
    tk.Label(hdr, text=f"  {title}",
             fg=T["text"], bg=T["card"],
             font=F["h1"]).pack(side="left", padx=14, pady=14)
    tk.Frame(m, bg=accent or T["accent"], height=2).grid(
        row=0, column=0, sticky="sew")

    # Body
    body = tk.Frame(m, bg=T["page"], padx=14, pady=12)
    body.grid(row=1, column=0, sticky="nsew")
    body.columnconfigure(0, weight=1)

    return m, hdr, body


# ══════════════════════════════════════════════════════════════════
#  TOAST NOTIFICATIONS
# ══════════════════════════════════════════════════════════════════

def toast(parent, title, subtitle,
          is_success=True, duration_ms=4000):
    """
    Slide-in toast notification at top centre of parent window.
    """
    try:
        bg_outer = T["green"]   if is_success else T["red"]
        bg_inner = T["green_bg"] if is_success else T["red_bg"]
        fg_title = "#064e3b"    if is_success else "#9b1c1c"
        fg_sub   = "#047857"    if is_success else "#b91c1c"
        icon     = "✓"          if is_success else "✗"

        t = tk.Toplevel(parent)
        t.overrideredirect(True)
        t.attributes("-topmost", True)

        tw, th = 460, 70
        wx = parent.winfo_x()
        wy = parent.winfo_y()
        ww = parent.winfo_width()
        t.geometry(f"{tw}x{th}+{wx+ww//2-tw//2}+{wy+18}")

        outer = tk.Frame(t, bg=bg_outer, padx=2, pady=2)
        outer.pack(fill="both", expand=True)
        inner = tk.Frame(outer, bg=bg_inner, padx=16, pady=10)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text=icon, fg=bg_outer, bg=bg_inner,
                 font=("Segoe UI",16,"bold")).pack(side="left", padx=(0,12))

        tf = tk.Frame(inner, bg=bg_inner)
        tf.pack(side="left")
        tk.Label(tf, text=title,    fg=fg_title, bg=bg_inner,
                 font=("Segoe UI",11,"bold")).pack(anchor="w")
        tk.Label(tf, text=subtitle, fg=fg_sub,   bg=bg_inner,
                 font=F["xs"]).pack(anchor="w")

        t.after(duration_ms, t.destroy)
        for w in [t, outer, inner, tf]:
            w.bind("<Button-1>", lambda e: t.destroy())
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════
#  SCROLLABLE FRAME
# ══════════════════════════════════════════════════════════════════

def scrollable_frame(parent, bg=None):
    """
    Returns a frame whose content scrolls vertically via mousewheel.
    Returns (outer_frame, inner_frame).
    """
    bg = bg or T["page"]
    outer = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0, bd=0)
    canvas.pack(side="left", fill="both", expand=True)

    inner = tk.Frame(canvas, bg=bg)
    win_id = canvas.create_window((0,0), window=inner, anchor="nw")

    inner.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>",
                lambda e: canvas.itemconfig(win_id, width=e.width))

    def _scroll(e):
        canvas.yview_scroll(int(-1*(e.delta/120)), "units")

    inner.bind("<Enter>",  lambda e: canvas.bind_all("<MouseWheel>", _scroll))
    inner.bind("<Leave>",  lambda e: canvas.unbind_all("<MouseWheel>"))

    return outer, inner


# ══════════════════════════════════════════════════════════════════
#  STATUS BAR
# ══════════════════════════════════════════════════════════════════

def status_bar(parent, height=28):
    """Bottom status bar. Returns the message label."""
    bar = tk.Frame(parent, bg=T["card2"], height=height)
    bar.pack(fill="x", side="bottom")
    bar.pack_propagate(False)

    tk.Label(bar, text="⬤ ", fg=T["green"],
             bg=T["card2"], font=("Segoe UI",7)
             ).pack(side="left", padx=(10,0), pady=6)
    msg = tk.Label(bar, text="System ready",
                   fg=T["text2"], bg=T["card2"], font=F["xs"])
    msg.pack(side="left", pady=6)

    ver = tk.Label(bar, text="FaceTrack Pro v1.0",
                   fg=T["muted"], bg=T["card2"], font=F["xs"])
    ver.pack(side="right", padx=12, pady=6)

    return msg
