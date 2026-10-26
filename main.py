"""
MAIN APPLICATION FILE
=====================
This is the entry point of the Smart Budget Analysis Tool.
It initializes the database, shows the splash screen,
handles login, and launches the main dashboard.

Run this file to start the application:
    python main.py
"""

import customtkinter as ctk
import tkinter as tk
import sys
import os
import math
import random
import threading
import time

# Add current directory to path for all module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_setup      import initialize_database
from modules.login_ui       import LoginUI
from modules.dashboard_ui   import DashboardUI

# ── App Appearance Settings ────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Color Scheme ───────────────────────────────────────────
COLORS = {
    "bg"      : "#0A0E1A",
    "accent1" : "#6366F1",
    "accent2" : "#8B5CF6",
    "accent3" : "#10B981",
    "text"    : "#F9FAFB",
    "subtext" : "#9CA3AF",
}


# ══════════════════════════════════════════════════════════
# SPLASH SCREEN
# ══════════════════════════════════════════════════════════
class SplashScreen(ctk.CTkToplevel):
    """
    Animated splash screen displayed when the application starts.
    Shows app name with typewriter effect and animated progress bar.
    """

    def __init__(self, master):
        super().__init__(master)
        self.title("")
        self.geometry("520x300")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        self.overrideredirect(True)

        # Center the splash screen on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 520) // 2
        y = (self.winfo_screenheight() - 300) // 2
        self.geometry(f"520x300+{x}+{y}")

        # Canvas for drawing
        self.canvas = tk.Canvas(
            self,
            bg                 = COLORS["bg"],
            highlightthickness = 0,
            width              = 520,
            height             = 300
        )
        self.canvas.pack()

        # App icon and title
        self.canvas.create_text(
            260, 80,
            text = "💰",
            font = ("Segoe UI", 42),
            fill = COLORS["accent1"]
        )

        self.title_text = self.canvas.create_text(
            260, 140,
            text = "",
            font = ("Segoe UI", 22, "bold"),
            fill = COLORS["accent1"]
        )

        self.subtitle_text = self.canvas.create_text(
            260, 168,
            text = "with Predictive Analytics",
            font = ("Segoe UI", 11),
            fill = COLORS["subtext"]
        )

        # Progress bar background
        self.canvas.create_rectangle(
            60, 210, 460, 228,
            fill    = "#1F2937",
            outline = ""
        )

        # Progress bar fill
        self.bar = self.canvas.create_rectangle(
            60, 210, 60, 228,
            fill    = COLORS["accent1"],
            outline = ""
        )

        # Status message
        self.status = self.canvas.create_text(
            260, 250,
            text = "Initializing...",
            font = ("Segoe UI", 10),
            fill = COLORS["subtext"]
        )

        # Developer credit
        self.canvas.create_text(
            260, 285,
            text = "Developed by Arpit Nigam",
            font = ("Segoe UI", 9),
            fill = "#374151"
        )

        self.progress   = 0
        self.title_str  = "Smart Budget Analysis Tool"
        self.title_idx  = 0

        self._animate_title()

    def _animate_title(self):
        """Typewriter animation for the app title."""
        if self.title_idx <= len(self.title_str):
            self.canvas.itemconfig(
                self.title_text,
                text = self.title_str[:self.title_idx]
            )
            self.title_idx += 1
            self.after(45, self._animate_title)
        else:
            self._animate_progress()

    def _animate_progress(self):
        """Animates the loading progress bar."""
        messages = [
            "Initializing database...",
            "Loading modules...",
            "Setting up interface...",
            "Ready!  🚀"
        ]

        if self.progress <= 400:
            self.canvas.coords(self.bar, 60, 210, 60 + self.progress, 228)
            idx = min(int(self.progress / 100), 3)
            self.canvas.itemconfig(self.status, text=messages[idx])
            self.progress += 5
            self.after(12, self._animate_progress)
        else:
            self.after(300, self.destroy)


# ══════════════════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════════════════
class BudgetApp(ctk.CTk):
    """
    Root application window controller.
    Manages transitions between splash screen, login, and dashboard.
    """

    def __init__(self):
        super().__init__()

        # Window settings
        self.title("Smart Budget Analysis Tool")
        self.geometry("1150x720")
        self.minsize(950, 620)
        self.configure(fg_color=COLORS["bg"])
        self.attributes("-alpha", 0.0)

        # Center window on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 1150) // 2
        y = (self.winfo_screenheight() - 720)  // 2
        self.geometry(f"1150x720+{x}+{y}")

        self.current_frame = None

        # Initialize database and show splash screen
        self.after(100, self._initialize)

    def _initialize(self):
        """Initializes database and shows splash screen."""

        # Initialize database silently
        initialize_database()

        # Show splash screen
        splash = SplashScreen(self)
        self.wait_window(splash)

        # Show login page
        self.show_login()

    def show_login(self):
        """Destroys current frame and shows the login screen."""
        if self.current_frame:
            self.current_frame.destroy()

        self.attributes("-alpha", 0.0)
        self.current_frame = LoginUI(
            self,
            on_login_success = self.show_dashboard
        )

    def show_dashboard(self, user):
        """Destroys login frame and loads the main dashboard."""
        if self.current_frame:
            self.current_frame.destroy()

        self.attributes("-alpha", 1.0)
        self.current_frame = DashboardUI(
            self,
            user      = user,
            on_logout = self.show_login
        )


# ══════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = BudgetApp()
    app.mainloop()
