import sys
import os
import traceback
import logging

# ── Crash logger (runs before anything else) ──────────────────────────────────
LOG_PATH = os.path.join(os.path.expanduser("~"), "dlmongoose_crash.log")
logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")

def _excepthook(exc_type, exc_value, exc_tb):
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logging.critical(msg)
    try:
        import tkinter as tk
        from tkinter import messagebox
        r = tk.Tk(); r.withdraw()
        messagebox.showerror("DL Mongoose — Crash", f"{exc_value}\n\nLog: {LOG_PATH}")
        r.destroy()
    except Exception:
        pass

sys.excepthook = _excepthook

# ── Imports ───────────────────────────────────────────────────────────────────
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import threading
import queue as Queue
import json
import time
import socket
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

# ── App Config ────────────────────────────────────────────────────────────────
APP_NAME     = "DL Mongoose"
APP_VERSION  = "1.0.0"
CONFIG_FILE  = os.path.join(os.path.expanduser("~"), ".dlmongoose_config.json")
HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".dlmongoose_history.json")

# ── Colors ────────────────────────────────────────────────────────────────────
BG_DEEP      = "#050B18"
BG_PANEL     = "#0A1628"
GLASS_BG     = "#0D1E35"
GLASS_BORDER = "#1A3A5C"
BLUE_ACCENT  = "#4B7BEC"
PURPLE_ACC   = "#A855F7"
CYAN_ACC     = "#06B6D4"
TEXT_MAIN    = "#E8F4FD"
TEXT_DIM     = "#7BA7C9"
SUCCESS      = "#10B981"
ERROR_RED    = "#EF4444"
WARNING_ORG  = "#F59E0B"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Config ────────────────────────────────────────────────────────────────────
class Config:
    defaults = {
        "download_path":       str(Path.home() / "Downloads"),
        "remember_path":       True,
        "platform":            "YouTube",
        "video_quality":       "Best",
        "audio_quality":       "320",
        "skip_delete_warning": False,
        "minimize_to_tray":    False,
    }

    def __init__(self):
        self.data = dict(self.defaults)
        self.load()

    def load(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE) as f:
                    self.data.update(json.load(f))
        except Exception:
            pass

    def save(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def get(self, key):
        return self.data.get(key, self.defaults.get(key))

    def set(self, key, value):
        self.data[key] = value
        self.save()

config = Config()

# ── Internet ──────────────────────────────────────────────────────────────────
def check_internet():
    try:
        socket.setdefaulttimeout(3)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("8.8.8.8", 53))
        s.close()
        return True
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════════════
#  SPLASH  (pure tkinter so it works before CTk is fully ready)
# ══════════════════════════════════════════════════════════════════════════════
class SplashScreen(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.overrideredirect(True)
        self.configure(bg="#050B18")
        w, h = 460, 280
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self.attributes("-topmost", True)
        self._build()
        self._animate()

    def _build(self):
        outer = tk.Frame(self, bg="#0D1E35", bd=0,
                         highlightbackground="#1A3A5C", highlightthickness=1)
        outer.pack(fill="both", expand=True, padx=2, pady=2)

        tk.Label(outer, text="🦡", font=("Segoe UI Emoji", 52),
                 bg="#0D1E35", fg="#E8F4FD").pack(pady=(30, 4))
        tk.Label(outer, text=APP_NAME, font=("Georgia", 26, "bold"),
                 bg="#0D1E35", fg="#E8F4FD").pack()
        tk.Label(outer, text="Fast  •  Clean  •  Unstoppable",
                 font=("Segoe UI", 10), bg="#0D1E35", fg="#7BA7C9").pack(pady=(2, 16))

        self.canvas = tk.Canvas(outer, width=320, height=8,
                                bg="#1A3A5C", bd=0, highlightthickness=0)
        self.canvas.pack()
        self.bar = self.canvas.create_rectangle(0, 0, 0, 8, fill="#4B7BEC", outline="")

        self.status = tk.Label(outer, text="Initializing...",
                               font=("Segoe UI", 9), bg="#0D1E35", fg="#7BA7C9")
        self.status.pack(pady=(8, 0))

        tk.Label(outer, text=f"v{APP_VERSION}", font=("Segoe UI", 8),
                 bg="#0D1E35", fg="#1A3A5C").pack(pady=(8, 0))

    def _animate(self):
        steps = [(0.2, "Loading components..."),
                 (0.5, "Checking environment..."),
                 (0.8, "Almost there..."),
                 (1.0, "Ready!")]

        def run(i=0):
            if i < len(steps):
                pct, msg = steps[i]
                self.canvas.coords(self.bar, 0, 0, int(320 * pct), 8)
                self.status.configure(text=msg)
                self.after(500, lambda: run(i + 1))
            else:
                self.after(300, self.destroy)
        run()


# ══════════════════════════════════════════════════════════════════════════════
#  ERROR DIALOG
# ══════════════════════════════════════════════════════════════════════════════
class ErrorDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Error", message="An error occurred."):
        super().__init__(parent)
        self.title(title)
        self.configure(fg_color=BG_DEEP)
        self.resizable(False, False)
        w, h = 460, 260
        try:
            px = parent.winfo_x() + (parent.winfo_width()  - w) // 2
            py = parent.winfo_y() + (parent.winfo_height() - h) // 2
        except Exception:
            px, py = 200, 200
        self.geometry(f"{w}x{h}+{px}+{py}")
        self.attributes("-topmost", True)
        self.grab_set()
        self._build(title, message)

    def _build(self, title, message):
        frame = ctk.CTkFrame(self, fg_color=GLASS_BG, corner_radius=24,
                             border_width=1, border_color=GLASS_BORDER)
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        ctk.CTkLabel(frame, text="⚠️  " + title,
                     font=ctk.CTkFont("Segoe UI", 15, "bold"),
                     text_color=ERROR_RED).pack(pady=(22, 8))

        txt = ctk.CTkTextbox(frame, height=90, corner_radius=12,
                             fg_color=BG_DEEP, border_color=GLASS_BORDER,
                             border_width=1, text_color=TEXT_MAIN,
                             font=ctk.CTkFont("Consolas", 11), wrap="word")
        txt.pack(padx=20, fill="x")
        txt.insert("1.0", message)
        txt.configure(state="disabled")

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(pady=16)

        def copy_err():
            self.clipboard_clear()
            self.clipboard_append(message)
            copy_btn.configure(text="✅ Copied!")
            self.after(1500, lambda: copy_btn.configure(text="📋 Copy Error"))

        copy_btn = ctk.CTkButton(btn_row, text="📋 Copy Error", width=130,
                                 corner_radius=20, fg_color=GLASS_BORDER,
                                 hover_color=BLUE_ACCENT, command=copy_err)
        copy_btn.pack(side="left", padx=8)

        ctk.CTkButton(btn_row, text="Close", width=100, corner_radius=20,
                      fg_color=ERROR_RED, hover_color="#C0392B",
                      command=self.destroy).pack(side="left", padx=8)


# ══════════════════════════════════════════════════════════════════════════════
#  QUEUE ITEM
# ══════════════════════════════════════════════════════════════════════════════
class QueueItem(ctk.CTkFrame):
    def __init__(self, parent, item_id, title, url, on_cancel, on_delete, **kw):
        super().__init__(parent, fg_color=GLASS_BG, corner_radius=16,
                         border_width=1, border_color=GLASS_BORDER, **kw)
        self.item_id   = item_id
        self.url       = url
        self.cancelled = False
        self.on_cancel = on_cancel
        self.on_delete = on_delete
        self._build(title)

    def _build(self, title):
        self.pack(fill="x", padx=10, pady=4)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(10, 4))

        self.title_lbl = ctk.CTkLabel(
            top, text=title[:55] + ("…" if len(title) > 55 else ""),
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=TEXT_MAIN, anchor="w")
        self.title_lbl.pack(side="left", fill="x", expand=True)

        self.status_lbl = ctk.CTkLabel(top, text="Queued",
                                       font=ctk.CTkFont("Segoe UI", 10),
                                       text_color=TEXT_DIM)
        self.status_lbl.pack(side="right")

        self.prog = ctk.CTkProgressBar(self, height=5, corner_radius=4,
                                       fg_color=BG_DEEP, progress_color=BLUE_ACCENT)
        self.prog.set(0)
        self.prog.pack(fill="x", padx=14, pady=(0, 6))

        self.speed_lbl = ctk.CTkLabel(self, text="",
                                      font=ctk.CTkFont("Segoe UI", 10),
                                      text_color=CYAN_ACC)
        self.speed_lbl.pack(anchor="w", padx=14)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(anchor="e", padx=14, pady=(4, 10))

        self.cancel_btn = ctk.CTkButton(
            btn_row, text="Cancel", width=80, height=26, corner_radius=14,
            fg_color=WARNING_ORG, hover_color="#D97706",
            font=ctk.CTkFont("Segoe UI", 11), command=self._cancel)
        self.cancel_btn.pack(side="left", padx=4)

        ctk.CTkButton(btn_row, text="Remove", width=80, height=26,
                      corner_radius=14, fg_color=ERROR_RED, hover_color="#C0392B",
                      font=ctk.CTkFont("Segoe UI", 11),
                      command=lambda: self.on_delete(self.item_id)).pack(side="left", padx=4)

    def _cancel(self):
        self.cancelled = True
        self.on_cancel(self.item_id)
        self.cancel_btn.configure(state="disabled", text="Cancelled")
        self.status_lbl.configure(text="Cancelled", text_color=WARNING_ORG)

    def update_progress(self, pct, speed, status_text, color=BLUE_ACCENT):
        self.prog.configure(progress_color=color)
        self.prog.set(pct / 100)
        self.speed_lbl.configure(text=speed)
        self.status_lbl.configure(text=status_text)

    def mark_done(self):
        self.prog.configure(progress_color=SUCCESS)
        self.prog.set(1.0)
        self.status_lbl.configure(text="✅ Done", text_color=SUCCESS)
        self.speed_lbl.configure(text="")
        self.cancel_btn.configure(state="disabled", text="Done")

    def mark_error(self):
        self.prog.configure(progress_color=ERROR_RED)
        self.status_lbl.configure(text="❌ Error", text_color=ERROR_RED)
        self.cancel_btn.configure(state="disabled")


# ══════════════════════════════════════════════════════════════════════════════
#  HISTORY ITEM
# ══════════════════════════════════════════════════════════════════════════════
class HistoryItem(ctk.CTkFrame):
    def __init__(self, parent, entry, on_delete, **kw):
        super().__init__(parent, fg_color=GLASS_BG, corner_radius=14,
                         border_width=1, border_color=GLASS_BORDER, **kw)
        self.entry     = entry
        self.on_delete = on_delete
        self.check_var = tk.BooleanVar()
        self._build()

    def _build(self):
        self.pack(fill="x", padx=10, pady=3)
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=10)

        ctk.CTkCheckBox(row, text="", variable=self.check_var,
                        width=20, checkbox_width=18, checkbox_height=18,
                        corner_radius=6, fg_color=BLUE_ACCENT,
                        border_color=GLASS_BORDER).pack(side="left", padx=(0, 8))

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        name = os.path.basename(self.entry.get("path", "Unknown"))
        ctk.CTkLabel(info, text=name[:50] + ("…" if len(name) > 50 else ""),
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=TEXT_MAIN, anchor="w").pack(anchor="w")
        ctk.CTkLabel(info, text=self.entry.get("timestamp", ""),
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=TEXT_DIM, anchor="w").pack(anchor="w")

        btn_row = ctk.CTkFrame(row, fg_color="transparent")
        btn_row.pack(side="right")

        ctk.CTkButton(btn_row, text="📂 Open", width=80, height=26,
                      corner_radius=14, fg_color=GLASS_BORDER,
                      hover_color=BLUE_ACCENT, font=ctk.CTkFont("Segoe UI", 11),
                      command=self._open_folder).pack(side="left", padx=3)

        ctk.CTkButton(btn_row, text="🗑 Delete", width=80, height=26,
                      corner_radius=14, fg_color=ERROR_RED, hover_color="#C0392B",
                      font=ctk.CTkFont("Segoe UI", 11),
                      command=lambda: self.on_delete(self)).pack(side="left", padx=3)

    def _open_folder(self):
        path = self.entry.get("path", "")
        folder = os.path.dirname(path)
        if os.path.exists(folder):
            subprocess.Popen(f'explorer /select,"{path}"')

    def is_selected(self):
        return self.check_var.get()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
class DLMongoose(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.configure(fg_color=BG_DEEP)
        self.geometry("840x700")
        self.minsize(760, 600)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.queue_items     = {}
        self.queue_counter   = 0
        self.dl_queue        = Queue.Queue()
        self.cancel_flags    = {}
        self.history         = []
        self.history_widgets = []
        self.internet_ok     = True
        self.no_net_overlay  = None
        self.tray_icon       = None

        self._load_history()
        self._build_ui()
        self._setup_tray()

        threading.Thread(target=self._download_worker, daemon=True).start()
        threading.Thread(target=self._internet_watcher, daemon=True).start()

    # ─────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        topbar = ctk.CTkFrame(self, fg_color=GLASS_BG, corner_radius=0, height=54)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        ctk.CTkLabel(topbar, text="🦡  " + APP_NAME,
                     font=ctk.CTkFont("Georgia", 18, "bold"),
                     text_color=TEXT_MAIN).pack(side="left", padx=20)

        ctk.CTkButton(topbar, text="💛  Support Me", width=130, height=32,
                      corner_radius=20, fg_color=WARNING_ORG, hover_color="#D97706",
                      font=ctk.CTkFont("Segoe UI", 12, "bold"),
                      command=self._open_support).pack(side="right", padx=16, pady=10)

        ctk.CTkButton(topbar, text="⊟  Tray", width=70, height=32,
                      corner_radius=20, fg_color=GLASS_BORDER, hover_color=BLUE_ACCENT,
                      command=self._minimize_to_tray).pack(side="right", padx=4, pady=10)

        self.tabs = ctk.CTkTabview(
            self, corner_radius=20, fg_color=GLASS_BG,
            segmented_button_fg_color=BG_PANEL,
            segmented_button_selected_color=BLUE_ACCENT,
            segmented_button_selected_hover_color="#3A6AD4",
            segmented_button_unselected_color=BG_PANEL,
            segmented_button_unselected_hover_color=GLASS_BORDER,
            text_color=TEXT_MAIN,
            border_color=GLASS_BORDER, border_width=1)
        self.tabs.pack(fill="both", expand=True, padx=14, pady=(10, 14))
        self.tabs.add("⬇  Download")
        self.tabs.add("📋  Queue")
        self.tabs.add("📁  History")

        self._build_download_tab()
        self._build_queue_tab()
        self._build_history_tab()

    # ── Download Tab ──────────────────────────────────────────────────────────
    def _build_download_tab(self):
        tab = self.tabs.tab("⬇  Download")
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # URL card
        url_card = ctk.CTkFrame(scroll, fg_color=GLASS_BG, corner_radius=20,
                                border_width=1, border_color=GLASS_BORDER)
        url_card.pack(fill="x", padx=6, pady=(8, 6))

        ctk.CTkLabel(url_card, text="YouTube URL",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=TEXT_DIM).pack(anchor="w", padx=18, pady=(14, 4))

        row = ctk.CTkFrame(url_card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 14))

        self.url_entry = ctk.CTkEntry(
            row, placeholder_text="Paste YouTube link here...",
            height=42, corner_radius=14,
            fg_color=BG_DEEP, border_color=GLASS_BORDER,
            text_color=TEXT_MAIN, placeholder_text_color=TEXT_DIM,
            font=ctk.CTkFont("Segoe UI", 13))
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.url_entry.bind("<Return>", lambda e: self._add_to_queue())

        ctk.CTkButton(row, text="Add to Queue", width=130, height=42,
                      corner_radius=14, fg_color=BLUE_ACCENT, hover_color="#3A6AD4",
                      font=ctk.CTkFont("Segoe UI", 13, "bold"),
                      command=self._add_to_queue).pack(side="right")

        # Options card
        opt_card = ctk.CTkFrame(scroll, fg_color=GLASS_BG, corner_radius=20,
                                border_width=1, border_color=GLASS_BORDER)
        opt_card.pack(fill="x", padx=6, pady=6)

        ctk.CTkLabel(opt_card, text="Options",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=TEXT_DIM).pack(anchor="w", padx=18, pady=(14, 8))

        grid = ctk.CTkFrame(opt_card, fg_color="transparent")
        grid.pack(fill="x", padx=18, pady=(0, 14))
        grid.columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(grid, text="Platform",
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color=TEXT_DIM).grid(row=0, column=0, sticky="w", pady=4)
        self.platform_var = ctk.StringVar(value=config.get("platform"))
        ctk.CTkOptionMenu(grid, values=["YouTube", "YouTube Music"],
                          variable=self.platform_var, width=200, height=36,
                          corner_radius=12, fg_color=BG_DEEP,
                          button_color=BLUE_ACCENT, button_hover_color="#3A6AD4",
                          text_color=TEXT_MAIN,
                          command=self._on_platform_change).grid(
            row=1, column=0, sticky="w", pady=(0, 10), padx=(0, 10))

        ctk.CTkLabel(grid, text="Quality",
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color=TEXT_DIM).grid(row=0, column=1, sticky="w", pady=4)
        self.quality_var = ctk.StringVar(value=config.get("video_quality"))
        ctk.CTkOptionMenu(
            grid, variable=self.quality_var,
            values=["Best", "1080p", "720p", "480p", "360p", "Audio Only (MP3)"],
            width=200, height=36, corner_radius=12,
            fg_color=BG_DEEP, button_color=BLUE_ACCENT,
            button_hover_color="#3A6AD4", text_color=TEXT_MAIN,
            command=self._on_quality_change).grid(
            row=1, column=1, sticky="w", pady=(0, 10))

        self.audio_lbl = ctk.CTkLabel(grid, text="MP3 Bitrate (kbps)",
                                      font=ctk.CTkFont("Segoe UI", 11),
                                      text_color=TEXT_DIM)
        self.audio_var = ctk.StringVar(value=config.get("audio_quality"))
        self.audio_menu = ctk.CTkOptionMenu(
            grid, values=["320", "256", "192", "128", "96"],
            variable=self.audio_var, width=200, height=36, corner_radius=12,
            fg_color=BG_DEEP, button_color=PURPLE_ACC,
            button_hover_color="#9333EA", text_color=TEXT_MAIN)
        self._opt_grid = grid

        # Path card
        path_card = ctk.CTkFrame(scroll, fg_color=GLASS_BG, corner_radius=20,
                                 border_width=1, border_color=GLASS_BORDER)
        path_card.pack(fill="x", padx=6, pady=6)

        ctk.CTkLabel(path_card, text="Save Location",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=TEXT_DIM).pack(anchor="w", padx=18, pady=(14, 8))

        path_row = ctk.CTkFrame(path_card, fg_color="transparent")
        path_row.pack(fill="x", padx=18, pady=(0, 10))

        self.path_var = tk.StringVar(value=config.get("download_path"))
        ctk.CTkEntry(path_row, textvariable=self.path_var, height=38,
                     corner_radius=12, fg_color=BG_DEEP, border_color=GLASS_BORDER,
                     text_color=TEXT_MAIN,
                     font=ctk.CTkFont("Segoe UI", 11)).pack(
            side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(path_row, text="Browse", width=90, height=38,
                      corner_radius=12, fg_color=GLASS_BORDER, hover_color=BLUE_ACCENT,
                      command=self._browse_path).pack(side="right")

        rem = ctk.CTkFrame(path_card, fg_color="transparent")
        rem.pack(anchor="w", padx=18, pady=(0, 14))

        self.remember_var = tk.BooleanVar(value=config.get("remember_path"))
        ctk.CTkCheckBox(rem, text="Remember this path", variable=self.remember_var,
                        font=ctk.CTkFont("Segoe UI", 11), text_color=TEXT_DIM,
                        fg_color=BLUE_ACCENT, border_color=GLASS_BORDER,
                        corner_radius=6, command=self._on_remember).pack(side="left")

    # ── Queue Tab ─────────────────────────────────────────────────────────────
    def _build_queue_tab(self):
        tab = self.tabs.tab("📋  Queue")
        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(8, 4))

        ctk.CTkLabel(top, text="Download Queue",
                     font=ctk.CTkFont("Segoe UI", 14, "bold"),
                     text_color=TEXT_MAIN).pack(side="left")
        ctk.CTkButton(top, text="Clear Done", width=100, height=30,
                      corner_radius=14, fg_color=GLASS_BORDER, hover_color=BLUE_ACCENT,
                      command=self._clear_done).pack(side="right")

        self.queue_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.queue_scroll.pack(fill="both", expand=True, padx=4, pady=4)

        self.empty_queue_lbl = ctk.CTkLabel(
            self.queue_scroll,
            text="Queue is empty\nAdd links in the Download tab",
            font=ctk.CTkFont("Segoe UI", 13), text_color=TEXT_DIM)
        self.empty_queue_lbl.pack(expand=True, pady=80)

    # ── History Tab ───────────────────────────────────────────────────────────
    def _build_history_tab(self):
        tab = self.tabs.tab("📁  History")
        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(8, 4))

        ctk.CTkLabel(top, text="Recent Downloads",
                     font=ctk.CTkFont("Segoe UI", 14, "bold"),
                     text_color=TEXT_MAIN).pack(side="left")
        ctk.CTkButton(top, text="🗑 Delete Selected", width=130, height=30,
                      corner_radius=14, fg_color=ERROR_RED, hover_color="#C0392B",
                      command=self._delete_selected).pack(side="right")

        self.history_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.history_scroll.pack(fill="both", expand=True, padx=4, pady=4)

        self.empty_hist_lbl = ctk.CTkLabel(
            self.history_scroll, text="No downloads yet",
            font=ctk.CTkFont("Segoe UI", 13), text_color=TEXT_DIM)
        self._refresh_history_ui()

    # ── Internet overlay ──────────────────────────────────────────────────────
    def _show_no_internet(self):
        if self.no_net_overlay:
            return
        self.no_net_overlay = ctk.CTkFrame(self, fg_color="#000000BB", corner_radius=0)
        self.no_net_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        card = ctk.CTkFrame(self.no_net_overlay, fg_color=GLASS_BG,
                            corner_radius=24, border_width=2,
                            border_color=ERROR_RED, width=360, height=230)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="🔴",
                     font=ctk.CTkFont("Segoe UI Emoji", 38)).pack(pady=(28, 4))
        ctk.CTkLabel(card, text="No Internet Connection",
                     font=ctk.CTkFont("Segoe UI", 15, "bold"),
                     text_color=ERROR_RED).pack()
        ctk.CTkLabel(card, text="Please check your connection",
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color=TEXT_DIM).pack(pady=4)
        ctk.CTkButton(card, text="🔄  Retry", width=120, height=36,
                      corner_radius=18, fg_color=BLUE_ACCENT, hover_color="#3A6AD4",
                      command=self._retry_internet).pack(pady=(12, 0))

    def _hide_no_internet(self):
        if self.no_net_overlay:
            self.no_net_overlay.destroy()
            self.no_net_overlay = None

    def _retry_internet(self):
        if check_internet():
            self.internet_ok = True
            self._hide_no_internet()

    def _internet_watcher(self):
        while True:
            status = check_internet()
            if status != self.internet_ok:
                self.internet_ok = status
                if status:
                    self.after(0, self._hide_no_internet)
                else:
                    self.after(0, self._show_no_internet)
            time.sleep(5)

    # ── Download ──────────────────────────────────────────────────────────────
    def _add_to_queue(self):
        if not self.internet_ok:
            return
        url = self.url_entry.get().strip()
        if not url:
            ErrorDialog(self, "No URL", "Please paste a YouTube URL first.")
            return
        if "youtube.com" not in url and "youtu.be" not in url:
            ErrorDialog(self, "Invalid URL",
                        f"This doesn't look like a YouTube link:\n{url}")
            return
        if yt_dlp is None:
            ErrorDialog(self, "Missing Library",
                        "yt-dlp not found.\nRun: pip install yt-dlp")
            return

        self.queue_counter += 1
        item_id = self.queue_counter
        self.cancel_flags[item_id] = False

        widget = QueueItem(self.queue_scroll, item_id,
                           f"Item #{item_id} — fetching...", url,
                           on_cancel=self._cancel_item, on_delete=self._remove_item)
        self.queue_items[item_id] = {"widget": widget, "url": url, "done": False}
        self.empty_queue_lbl.pack_forget()
        self.dl_queue.put(item_id)
        self.url_entry.delete(0, "end")
        self.tabs.set("📋  Queue")

    def _download_worker(self):
        while True:
            item_id = self.dl_queue.get()
            if item_id in self.queue_items and not self.cancel_flags.get(item_id):
                try:
                    self._do_download(item_id)
                except Exception as e:
                    logging.error(traceback.format_exc())
            self.dl_queue.task_done()

    def _do_download(self, item_id):
        info = self.queue_items.get(item_id)
        if not info:
            return
        url      = info["url"]
        widget   = info["widget"]
        out_path = self.path_var.get()
        quality  = self.quality_var.get()
        audio_q  = self.audio_var.get()
        is_audio = (quality == "Audio Only (MP3)" or
                    self.platform_var.get() == "YouTube Music")

        os.makedirs(out_path, exist_ok=True)

        def progress_hook(d):
            if self.cancel_flags.get(item_id):
                raise Exception("Download cancelled by user")
            if d["status"] == "downloading":
                raw = (d.get("_percent_str", "0%")
                         .replace("%", "").replace("\x1b[0;94m", "")
                         .replace("\x1b[0m", "").strip())
                speed = d.get("_speed_str", "").strip()
                eta   = d.get("_eta_str", "").strip()
                try:
                    pct_f = float(raw)
                except Exception:
                    pct_f = 0.0
                spd = f"{speed}  ETA {eta}" if speed else ""
                self.after(0, lambda p=pct_f, s=spd:
                           widget.update_progress(p, s, f"{p:.0f}%"))
            elif d["status"] == "finished":
                self.after(0, lambda: widget.update_progress(
                    99, "", "Processing...", PURPLE_ACC))

        q_map = {
            "Best":  "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best",
            "720p":  "bestvideo[height<=720]+bestaudio/best",
            "480p":  "bestvideo[height<=480]+bestaudio/best",
            "360p":  "bestvideo[height<=360]+bestaudio/best",
        }

        if is_audio:
            ydl_opts = {
                "format": "bestaudio/best",
                "postprocessors": [{"key": "FFmpegExtractAudio",
                                    "preferredcodec": "mp3",
                                    "preferredquality": audio_q}],
                "outtmpl": os.path.join(out_path, "%(title)s.%(ext)s"),
                "progress_hooks": [progress_hook],
                "quiet": True, "no_warnings": True,
            }
        else:
            ydl_opts = {
                "format": q_map.get(quality, "bestvideo+bestaudio/best"),
                "outtmpl": os.path.join(out_path, "%(title)s.%(ext)s"),
                "progress_hooks": [progress_hook],
                "quiet": True, "no_warnings": True,
                "merge_output_format": "mp4",
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                meta  = ydl.extract_info(url, download=False)
                title = meta.get("title", f"Item #{item_id}")
                short = title[:55] + ("…" if len(title) > 55 else "")
                self.after(0, lambda t=short: widget.title_lbl.configure(text=t))
                self.after(0, lambda: widget.status_lbl.configure(text="Downloading..."))

                if not self.cancel_flags.get(item_id):
                    ydl.download([url])

            if not self.cancel_flags.get(item_id):
                self.after(0, widget.mark_done)
                info["done"] = True
                ext  = "mp3" if is_audio else "mp4"
                self._add_history(title, os.path.join(out_path, f"{title}.{ext}"))

        except Exception as e:
            err = str(e)
            if "cancelled" not in err.lower():
                self.after(0, widget.mark_error)
                self.after(0, lambda m=err: ErrorDialog(self, "Download Error", m))

    def _cancel_item(self, item_id):
        self.cancel_flags[item_id] = True

    def _remove_item(self, item_id):
        self.cancel_flags[item_id] = True
        if item_id in self.queue_items:
            try:
                self.queue_items[item_id]["widget"].destroy()
            except Exception:
                pass
            del self.queue_items[item_id]
        if not self.queue_items:
            self.empty_queue_lbl.pack(expand=True, pady=80)

    def _clear_done(self):
        for k in [k for k, v in self.queue_items.items() if v.get("done")]:
            try:
                self.queue_items[k]["widget"].destroy()
            except Exception:
                pass
            del self.queue_items[k]
        if not self.queue_items:
            self.empty_queue_lbl.pack(expand=True, pady=80)

    # ── History ───────────────────────────────────────────────────────────────
    def _load_history(self):
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE) as f:
                    self.history = json.load(f)
        except Exception:
            self.history = []

    def _save_history(self):
        try:
            with open(HISTORY_FILE, "w") as f:
                json.dump(self.history[-200:], f, indent=2)
        except Exception:
            pass

    def _add_history(self, title, path):
        self.history.insert(0, {
            "title": title, "path": path,
            "timestamp": datetime.now().strftime("%d %b %Y  %H:%M"),
        })
        self._save_history()
        self.after(0, self._refresh_history_ui)

    def _refresh_history_ui(self):
        for w in self.history_widgets:
            try:
                w.destroy()
            except Exception:
                pass
        self.history_widgets.clear()

        if not self.history:
            self.empty_hist_lbl.pack(expand=True, pady=80)
            return
        self.empty_hist_lbl.pack_forget()

        for entry in self.history[:100]:
            hw = HistoryItem(self.history_scroll, entry,
                             on_delete=self._delete_history_item)
            self.history_widgets.append(hw)

    def _delete_history_item(self, widget):
        if not config.get("skip_delete_warning"):
            self._show_delete_warning(widget.entry, widget)
        else:
            self._do_delete(widget.entry, widget)

    def _show_delete_warning(self, entry, widget):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Confirm Delete")
        dlg.configure(fg_color=BG_DEEP)
        dlg.resizable(False, False)
        dlg.geometry("400x220")
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        frame = ctk.CTkFrame(dlg, fg_color=GLASS_BG, corner_radius=20,
                             border_width=1, border_color=WARNING_ORG)
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        ctk.CTkLabel(frame, text="🗑  Delete File?",
                     font=ctk.CTkFont("Segoe UI", 14, "bold"),
                     text_color=WARNING_ORG).pack(pady=(20, 6))

        name = os.path.basename(entry.get("path", ""))
        ctk.CTkLabel(frame, text=f"Permanently delete:\n{name[:45]}",
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color=TEXT_DIM, wraplength=350).pack(pady=4)

        skip_var = tk.BooleanVar()
        ctk.CTkCheckBox(frame, text="Don't show this warning again",
                        variable=skip_var, font=ctk.CTkFont("Segoe UI", 10),
                        text_color=TEXT_DIM, fg_color=BLUE_ACCENT,
                        border_color=GLASS_BORDER, corner_radius=5).pack(pady=8)

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack()

        def confirm():
            if skip_var.get():
                config.set("skip_delete_warning", True)
            dlg.destroy()
            self._do_delete(entry, widget)

        ctk.CTkButton(btn_row, text="Delete", width=100, height=32,
                      corner_radius=14, fg_color=ERROR_RED,
                      hover_color="#C0392B", command=confirm).pack(side="left", padx=8)
        ctk.CTkButton(btn_row, text="Cancel", width=100, height=32,
                      corner_radius=14, fg_color=GLASS_BORDER,
                      hover_color=BLUE_ACCENT, command=dlg.destroy).pack(side="left", padx=8)

    def _do_delete(self, entry, widget):
        path = entry.get("path", "")
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            ErrorDialog(self, "Delete Error", str(e))
        if entry in self.history:
            self.history.remove(entry)
        self._save_history()
        try:
            widget.destroy()
        except Exception:
            pass
        if widget in self.history_widgets:
            self.history_widgets.remove(widget)

    def _delete_selected(self):
        selected = [w for w in self.history_widgets if w.is_selected()]
        if not selected:
            return
        if not config.get("skip_delete_warning"):
            self._show_bulk_delete_warning(selected)
        else:
            for w in selected:
                self._do_delete(w.entry, w)

    def _show_bulk_delete_warning(self, widgets):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Confirm Bulk Delete")
        dlg.configure(fg_color=BG_DEEP)
        dlg.resizable(False, False)
        dlg.geometry("380x200")
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        frame = ctk.CTkFrame(dlg, fg_color=GLASS_BG, corner_radius=20,
                             border_width=1, border_color=WARNING_ORG)
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        ctk.CTkLabel(frame, text=f"Delete {len(widgets)} file(s)?",
                     font=ctk.CTkFont("Segoe UI", 14, "bold"),
                     text_color=WARNING_ORG).pack(pady=(20, 6))
        ctk.CTkLabel(frame, text="Files will be permanently deleted from your system.",
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color=TEXT_DIM, wraplength=330).pack(pady=4)

        skip_var = tk.BooleanVar()
        ctk.CTkCheckBox(frame, text="Don't show again", variable=skip_var,
                        font=ctk.CTkFont("Segoe UI", 10), text_color=TEXT_DIM,
                        fg_color=BLUE_ACCENT, border_color=GLASS_BORDER,
                        corner_radius=5).pack(pady=6)

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack()

        def confirm():
            if skip_var.get():
                config.set("skip_delete_warning", True)
            dlg.destroy()
            for w in widgets:
                self._do_delete(w.entry, w)

        ctk.CTkButton(btn_row, text="Delete All", width=110, height=32,
                      corner_radius=14, fg_color=ERROR_RED,
                      hover_color="#C0392B", command=confirm).pack(side="left", padx=8)
        ctk.CTkButton(btn_row, text="Cancel", width=100, height=32,
                      corner_radius=14, fg_color=GLASS_BORDER,
                      hover_color=BLUE_ACCENT, command=dlg.destroy).pack(side="left", padx=8)

    # ── Options ───────────────────────────────────────────────────────────────
    def _on_platform_change(self, val):
        config.set("platform", val)
        if val == "YouTube Music":
            self.quality_var.set("Audio Only (MP3)")
            self._on_quality_change("Audio Only (MP3)")

    def _on_quality_change(self, val):
        config.set("video_quality", val)
        if val == "Audio Only (MP3)":
            self.audio_lbl.grid(row=2, column=0, sticky="w", pady=(4, 0))
            self.audio_menu.grid(row=3, column=0, sticky="w")
        else:
            try:
                self.audio_lbl.grid_remove()
                self.audio_menu.grid_remove()
            except Exception:
                pass

    def _on_remember(self):
        val = self.remember_var.get()
        config.set("remember_path", val)
        if val:
            config.set("download_path", self.path_var.get())

    def _browse_path(self):
        folder = filedialog.askdirectory(initialdir=self.path_var.get())
        if folder:
            self.path_var.set(folder)
            if self.remember_var.get():
                config.set("download_path", folder)

    # ── Tray ──────────────────────────────────────────────────────────────────
    def _setup_tray(self):
        try:
            import pystray
            from PIL import Image, ImageDraw
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            d.ellipse([4, 4, 60, 60], fill=(75, 123, 236, 255))
            menu = pystray.Menu(
                pystray.MenuItem("Show", self._show_from_tray, default=True),
                pystray.MenuItem("Quit", self._quit_app),
            )
            self.tray_icon = pystray.Icon("dlmongoose", img, APP_NAME, menu)
        except Exception:
            self.tray_icon = None

    def _minimize_to_tray(self):
        if self.tray_icon:
            self.withdraw()
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        else:
            self.iconify()

    def _show_from_tray(self, icon=None, item=None):
        try:
            self.tray_icon.stop()
        except Exception:
            pass
        self.after(0, self.deiconify)

    # ── Misc ──────────────────────────────────────────────────────────────────
    def _open_support(self):
        webbrowser.open("https://buymeacoffee.com/dlmongoose")

    def _on_close(self):
        self._quit_app()

    def _quit_app(self, icon=None, item=None):
        try:
            if self.tray_icon:
                self.tray_icon.stop()
        except Exception:
            pass
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        app = DLMongoose()
        app.withdraw()

        splash = SplashScreen(app)
        app.wait_window(splash)

        if not check_internet():
            app.internet_ok = False
            app.after(100, app._show_no_internet)

        app.deiconify()
        app.mainloop()

    except Exception as e:
        msg = traceback.format_exc()
        logging.critical(msg)
        try:
            import tkinter as tk
            from tkinter import messagebox
            r = tk.Tk(); r.withdraw()
            messagebox.showerror("DL Mongoose — Fatal Error",
                                 f"{e}\n\nLog saved to:\n{LOG_PATH}")
            r.destroy()
        except Exception:
            pass
