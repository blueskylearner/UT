"""
UT Knowledge Quiz (Tkinter) — UL styling (complete file)
- Forces UL navy window background (#052264) with white “card” content
- Question prompt font = 16 pt (Calibri if present, else Segoe UI)
- No score shown; completion message instead
- Timezone-aware timestamps
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.simpledialog as simpledialog
from tkinter import font as tkfont
from datetime import datetime, timezone

from engine import QuizEngine
from storage import ResultStore, hash_identifier
from models import Result, Question
from validators import is_valid_email, non_empty


# ── Brand colours & typography (UL Style Guide) ───────────────────────────────
BRAND_BG = "#052264"     # Pantone 275 (navy)
BRAND_ACCENT = "#0079BC" # Pantone 285 (accent) – available if you want a banner
CARD_BG = "#FFFFFF"      # content “card”
TEXT_ON_BRAND = "#FFFFFF"
TEXT_ON_CARD = "#000000"

APP_SALT = "rotate-me-regularly"


def _choose_base_font() -> str:
    """Use Calibri if installed (UL fallback when Frutiger unavailable), else Segoe UI."""
    try:
        families = set(tkfont.families())
        if "Calibri" in families:
            return "Calibri"
    except Exception:
        pass
    return "Segoe UI"


def _apply_named_fonts(root: tk.Tk, base_family: str) -> None:
    """Nudge Tk’s named fonts so menus/labels/buttons inherit the family."""
    try:
        tkfont.nametofont("TkDefaultFont").configure(family=base_family, size=11)
        tkfont.nametofont("TkTextFont").configure(family=base_family, size=11)
        tkfont.nametofont("TkFixedFont").configure(family=base_family, size=11)
        tkfont.nametofont("TkMenuFont").configure(family=base_family, size=11)
        tkfont.nametofont("TkHeadingFont").configure(family=base_family, size=16, weight="bold")
        tkfont.nametofont("TkCaptionFont").configure(family=base_family, size=11)
        tkfont.nametofont("TkSmallCaptionFont").configure(family=base_family, size=10)
        tkfont.nametofont("TkIconFont").configure(family=base_family, size=11)
        tkfont.nametofont("TkTooltipFont").configure(family=base_family, size=10)
    except Exception:
        # Named fonts not available on some Tk builds; OK to skip.
        pass


class App(tk.Tk):
    def __init__(self, engine: QuizEngine, store: ResultStore):
        super().__init__()

        print("DEBUG app running from:", __file__)
        print("DEBUG working dir:", os.getcwd())

        self.title("UT Knowledge Quiz")
        self.geometry("720x520")
        self.engine, self.store, self.salt = engine, store, APP_SALT
        self.user_hash = ""

        # Global fonts and colours
        base_family = _choose_base_font()
        _apply_named_fonts(self, base_family)
        self.HEADER_FONT   = (base_family, 16, "bold")
        self.QUESTION_FONT = (base_family, 16)      # << question prompt @16 pt
        self.OPTION_FONT   = (base_family, 12)
        self.BUTTON_FONT   = (base_family, 11)

        # Window background (UL navy)
        self.configure(bg=BRAND_BG)

        # Root cover – guarantees navy even if ttk theme fights us
        root_cover = tk.Frame(self, bg=BRAND_BG)
        root_cover.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Container for frames (classic Tk so bg sticks)
        container = tk.Frame(self, bg=BRAND_BG)
        container.pack(fill="both", expand=True)

        # Register frames
        self.frames: dict[str, tk.Frame] = {}
        for F in (WelcomeFrame, QuizFrame, ResultFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self._build_menu()
        self.show_frame("WelcomeFrame")

        # Correct binding (no HTML entities)
        self.bind_all("<Control-Shift-A>", lambda e: self._open_admin())

    # ── Menu / Admin ─────────────────────────────────────────────────────────
    def _build_menu(self):
        menubar = tk.Menu(self)
        admin_menu = tk.Menu(menubar, tearoff=0)
        admin_menu.add_command(label="Admin…", command=self._open_admin)
        menubar.add_cascade(label="Settings", menu=admin_menu)
        self.config(menu=menubar)

    def show_frame(self, name: str):
        self.frames[name].tkraise()

    def _open_admin(self):
        key = simpledialog.askstring("Admin", "Enter admin key:")
        if key and len(key) >= 6:
            try:
                messagebox.showinfo(
                    "Export",
                    "Results are stored at ./data/attempts.csv\n"
                    "Rotate the hashing salt before a new cycle."
                )
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Admin", "Invalid admin key.")


# ── Frames (classic Tk so bg colours always apply) ────────────────────────────
class BaseFrame(tk.Frame):
    def __init__(self, master, app, **kw):
        kw.setdefault("bg", BRAND_BG)
        super().__init__(master, **kw)
        self.app = app


class WelcomeFrame(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)

        # Brand header directly on navy
        tk.Label(
            self,
            text="United Teaching Knowledge Check",
            bg=BRAND_BG,
            fg=TEXT_ON_BRAND,
            font=self.app.HEADER_FONT
        ).pack(pady=12)

        # White card for inputs
        card = tk.Frame(self, bg=CARD_BG)
        card.pack(fill="x", expand=False, padx=16, pady=16)

        tk.Label(card, text="Work email (preferred) or initials:", bg=CARD_BG, fg=TEXT_ON_CARD).pack(anchor="w")
        self.ident_var = tk.StringVar()
        ttk.Entry(card, textvariable=self.ident_var, width=40).pack(fill="x", pady=(2, 8))

        self.consent = tk.BooleanVar(value=True)
        ttk.Checkbutton(card, text="I consent to store my attempt", variable=self.consent).pack(anchor="w", pady=(0, 10))

        ttk.Button(card, text="Start", command=self._start).pack()

    def _start(self):
        ident = self.ident_var.get().strip()
        if not (non_empty(ident) and (is_valid_email(ident) or len(ident) >= 2)):
            messagebox.showerror("Invalid input", "Enter a valid work email or initials.")
            return
        if not self.consent.get():
            messagebox.showwarning("Consent required", "Consent is needed to proceed.")
            return
        self.app.user_hash = hash_identifier(ident, self.app.salt)
        self.app.show_frame("QuizFrame")


class QuizFrame(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)

        # White card for readable quiz content
        card = tk.Frame(self, bg=CARD_BG)
        card.pack(fill="both", expand=True, padx=16, pady=16)

        # Question prompt @16 pt
        self.prompt = tk.Label(card, text="", bg=CARD_BG, fg=TEXT_ON_CARD,
                               font=self.app.QUESTION_FONT, wraplength=640, justify="left")
        self.prompt.pack(pady=(0, 10), anchor="w")

        self.var = tk.StringVar()
        self.opts_frame = tk.Frame(card, bg=CARD_BG)
        self.opts_frame.pack(fill="x", pady=(0, 4))

        nav = tk.Frame(card, bg=CARD_BG)
        nav.pack(fill="x", pady=10)
        ttk.Button(nav, text="Back", command=self._back).pack(side="left")
        ttk.Button(nav, text="Next", command=self._next).pack(side="right")

        self._render()

    def _render(self):
        q = self.app.engine.current()
        self.prompt.config(text=f"Q{self.app.engine._index + 1}. {q.prompt}")

        for c in self.opts_frame.winfo_children():
            c.destroy()
        self.var.set("")

        if q.options:
            for opt in q.options:
                ttk.Radiobutton(self.opts_frame, text=opt, value=opt, variable=self.var).pack(anchor="w")
        else:
            entry = ttk.Entry(self.opts_frame, textvariable=self.var, width=45)
            entry.pack(anchor="w")
            entry.focus_set()

    def _back(self):
        self.app.engine.submit(self.var.get())
        if self.app.engine.prev():
            self._render()

    def _next(self):
        self.app.engine.submit(self.var.get())
        if not self.app.engine.next():
            # Save result (do not show score to user)
            score, details = self.app.engine.score()
            ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
            r = Result(self.app.user_hash, ts, score, len(details), details)
            try:
                self.app.store.save(r)
            except Exception as e:
                messagebox.showerror("Save error", str(e))
            self.app.show_frame("ResultFrame")
        else:
            self._render()


class ResultFrame(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)

        tk.Label(
            self,
            text="Thanks! The quiz is complete.\nYou will receive your results via email shortly.",
            bg=BRAND_BG,
            fg=TEXT_ON_BRAND,
            font=self.app.HEADER_FONT,
            justify="center"
        ).pack(pady=36)

        btns = tk.Frame(self, bg=BRAND_BG)
        btns.pack(pady=8)
        ttk.Button(btns, text="New attempt", command=self._retry).pack(side="left", padx=6)
        ttk.Button(btns, text="Close", command=self.app.destroy).pack(side="left", padx=6)

    def _retry(self):
        self.app.engine.reset()
        self.app.show_frame("QuizFrame")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("[UT-Quiz] Starting…")
    print(f"[UT-Quiz] Python: {os.sys.executable}")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    qfile = os.path.join(base_dir, "data", "questions.csv")
    attempts_file = os.path.join(base_dir, "data", "attempts.csv")
    print(f"[UT-Quiz] Loading questions from: {qfile}")

    try:
        questions = QuizEngine.load_from_csv(qfile)
        print(f"[UT-Quiz] Loaded {len(questions)} questions.")
    except Exception as e:
        print("[UT-Quiz] Failed to load questions.csv; using a 1-item fallback.")
        import traceback; traceback.print_exc()
        questions = [Question("q1", "Smoke test: can you see this?", ["Yes", "No"], "Yes", "Test")]

    engine = QuizEngine(questions)
    store = ResultStore(attempts_file)

    print("[UT-Quiz] Creating window…")
    app = App(engine, store)

    # Bring window to front briefly
    try:
        app.attributes("-topmost", True)
        app.after(250, lambda: app.attributes("-topmost", False))
    except Exception:
        pass

    print("[UT-Quiz] Entering Tk mainloop.")
    app.mainloop()