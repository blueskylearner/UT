# smoke.py
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Tkinter smoke test")
ttk.Label(root, text="If you can see this, Tkinter is working.").pack(padx=20, pady=20)
root.mainloop()