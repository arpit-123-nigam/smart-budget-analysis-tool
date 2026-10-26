"""
LOGIN UI MODULE
===============
This module contains the Login and Registration screen.
Features:
- Animated particle background
- Glassmorphism style login card
- Fade-in animation on startup
- Shake animation on wrong password
- Registration form for new users
- Show/Hide password toggle
"""

import customtkinter as ctk
import tkinter as tk
import sys
import os
import math
import random
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.auth import login_user, register_user

# ── Color Scheme ───────────────────────────────────────────
COLORS = {
    "bg"        : "#0A0E1A",
    "card"      : "#111827",
    "card2"     : "#1F2937",
    "accent1"   : "#6366F1",   # Indigo
    "accent2"   : "#8B5CF6",   # Purple
    "accent3"   : "#10B981",   # Green
    "danger"    : "#EF4444",   # Red
    "text"      : "#F9FAFB",
    "subtext"   : "#9CA3AF",
    "border"    : "#374151",
    "input_bg"  : "#1F2937",
}


class Particle:
    """
    Represents a single floating particle on the background canvas.
    Each particle moves slowly and bounces off screen edges.
    """
    def __init__(self, canvas_width, canvas_height):
        self.x      = random.randint(0, canvas_width)
        self.y      = random.randint(0, canvas_height)
        self.size   = random.uniform(1.5, 4.0)
        self.speed  = random.uniform(0.3, 1.0)
        self.angle  = random.uniform(0, 2 * math.pi)
        self.dx     = math.cos(self.angle) * self.speed
        self.dy     = math.sin(self.angle) * self.speed
        self.alpha  = random.uniform(0.3, 0.9)
        colors      = ["#6366F1", "#8B5CF6", "#10B981", "#3B82F6", "#F59E0B"]
        self.color  = random.choice(colors)

    def move(self, canvas_width, canvas_height):
        """Moves the particle and bounces it off screen edges."""
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= canvas_width:
            self.dx *= -1
        if self.y <= 0 or self.y >= canvas_height:
            self.dy *= -1


class LoginUI(ctk.CTkFrame):
    """
    Main Login Screen with animated particle background.
    Handles both login and registration flows.
    """

    def __init__(self, master, on_login_success):
        """
        Initializes the Login UI.

        Parameters:
            master           : Parent window (BudgetApp)
            on_login_success : Callback function called after successful login
        """
        super().__init__(master, fg_color=COLORS["bg"])
        self.master           = master
        self.on_login_success = on_login_success
        self.particles        = []
        self.show_register    = False
        self.password_visible = False
        self._alpha           = 0.0

        self.pack(fill="both", expand=True)
        self._setup_particles()
        self._build_ui()
        self._animate_particles()
        self._fade_in()

    # ── PARTICLE BACKGROUND ────────────────────────────────
    def _setup_particles(self):
        """Creates the particle animation canvas as background."""
        self.canvas = tk.Canvas(
            self,
            bg            = COLORS["bg"],
            highlightthickness = 0
        )
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Create 60 particles
        w = self.master.winfo_width()  or 1100
        h = self.master.winfo_height() or 700
        self.particles = [Particle(w, h) for _ in range(60)]

    def _animate_particles(self):
        """Animates all particles on the canvas continuously."""
        try:
            self.canvas.delete("particle")
            w = self.canvas.winfo_width()  or 1100
            h = self.canvas.winfo_height() or 700

            for p in self.particles:
                p.move(w, h)
                self.canvas.create_oval(
                    p.x - p.size, p.y - p.size,
                    p.x + p.size, p.y + p.size,
                    fill    = p.color,
                    outline = "",
                    tags    = "particle"
                )

            # Draw subtle connection lines between nearby particles
            for i, p1 in enumerate(self.particles):
                for p2 in self.particles[i+1:]:
                    dist = math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
                    if dist < 100:
                        self.canvas.create_line(
                            p1.x, p1.y, p2.x, p2.y,
                            fill  = "#374151",
                            width = 0.5,
                            tags  = "particle"
                        )

            self.after(33, self._animate_particles)   # ~30 FPS
        except Exception:
            pass

    # ── FADE IN ANIMATION ──────────────────────────────────
    def _fade_in(self):
        """Gradually increases window opacity for smooth appearance."""
        try:
            if self._alpha < 1.0:
                self._alpha = min(self._alpha + 0.04, 1.0)
                self.master.attributes("-alpha", self._alpha)
                self.after(16, self._fade_in)
        except Exception:
            pass

    # ── BUILD UI ───────────────────────────────────────────
    def _build_ui(self):
        """Constructs the complete login UI layout."""

        # ── Left Info Panel ──────────────────────────────
        self.left_panel = ctk.CTkFrame(
            self,
            fg_color     = "transparent",
            width        = 320
        )
        self.left_panel.place(relx=0.08, rely=0.5, anchor="w")

        # App logo and name
        ctk.CTkLabel(
            self.left_panel,
            text      = "💰",
            font      = ctk.CTkFont(size=64)
        ).pack(anchor="w")

        ctk.CTkLabel(
            self.left_panel,
            text      = "Smart Budget",
            font      = ctk.CTkFont(size=32, weight="bold"),
            text_color = COLORS["accent1"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            self.left_panel,
            text      = "Analysis Tool",
            font      = ctk.CTkFont(size=32, weight="bold"),
            text_color = COLORS["accent2"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            self.left_panel,
            text      = "with Predictive Analytics",
            font      = ctk.CTkFont(size=13),
            text_color = COLORS["subtext"]
        ).pack(anchor="w", pady=(0, 20))

        # Feature list
        features = [
            "📊  Visual Charts & Analysis",
            "🤖  AI Expense Predictions",
            "🎯  Budget Goal Tracking",
            "🔒  Encrypted & Secure",
            "📁  Multi-format Export",
        ]
        for feat in features:
            ctk.CTkLabel(
                self.left_panel,
                text       = feat,
                font       = ctk.CTkFont(size=12),
                text_color = COLORS["subtext"]
            ).pack(anchor="w", pady=3)

        # Developer credit — subtle and professional
        ctk.CTkLabel(
            self.left_panel,
            text       = "Dev: Arpit Nigam",
            font       = ctk.CTkFont(size=10),
            text_color = "#4B5563"
        ).pack(anchor="w", pady=(30, 0))

        # ── Login Card ───────────────────────────────────
        self.card = ctk.CTkFrame(
            self,
            fg_color     = COLORS["card"],
            corner_radius = 20,
            border_width  = 1,
            border_color  = COLORS["border"],
            width         = 400,
            height        = 480
        )
        self.card.place(relx=0.72, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        self._build_login_form()

    def _build_login_form(self):
        """Builds the login form inside the card."""

        # Clear existing widgets in card
        for widget in self.card.winfo_children():
            widget.destroy()

        # Title
        ctk.CTkLabel(
            self.card,
            text       = "Welcome Back 👋",
            font       = ctk.CTkFont(size=22, weight="bold"),
            text_color = COLORS["text"]
        ).pack(pady=(35, 4))

        ctk.CTkLabel(
            self.card,
            text       = "Sign in to your account",
            font       = ctk.CTkFont(size=12),
            text_color = COLORS["subtext"]
        ).pack(pady=(0, 25))

        # Username field
        ctk.CTkLabel(
            self.card,
            text       = "Username",
            font       = ctk.CTkFont(size=12),
            text_color = COLORS["subtext"],
            anchor     = "w"
        ).pack(fill="x", padx=35)

        self.username_entry = ctk.CTkEntry(
            self.card,
            placeholder_text = "Enter your username",
            height           = 44,
            corner_radius    = 10,
            fg_color         = COLORS["input_bg"],
            border_color     = COLORS["border"],
            font             = ctk.CTkFont(size=13)
        )
        self.username_entry.pack(fill="x", padx=35, pady=(4, 14))

        # Password field
        ctk.CTkLabel(
            self.card,
            text       = "Password",
            font       = ctk.CTkFont(size=12),
            text_color = COLORS["subtext"],
            anchor     = "w"
        ).pack(fill="x", padx=35)

        self.password_entry = ctk.CTkEntry(
            self.card,
            placeholder_text = "Enter your password",
            show             = "●",
            height           = 44,
            corner_radius    = 10,
            fg_color         = COLORS["input_bg"],
            border_color     = COLORS["border"],
            font             = ctk.CTkFont(size=13)
        )
        self.password_entry.pack(fill="x", padx=35, pady=(4, 5))

        # Show/Hide password toggle
        self.show_pass_btn = ctk.CTkButton(
            self.card,
            text         = "Show Password",
            width        = 120,
            height       = 24,
            corner_radius = 6,
            fg_color     = "transparent",
            hover_color  = COLORS["card2"],
            text_color   = COLORS["subtext"],
            font         = ctk.CTkFont(size=10),
            command      = self._toggle_password
        )
        self.show_pass_btn.pack(anchor="e", padx=35)

        # Error message label
        self.error_label = ctk.CTkLabel(
            self.card,
            text       = "",
            font       = ctk.CTkFont(size=11),
            text_color = COLORS["danger"]
        )
        self.error_label.pack(pady=(5, 0))

        # Login button
        self.login_btn = ctk.CTkButton(
            self.card,
            text          = "Sign In  →",
            height        = 46,
            corner_radius = 12,
            fg_color      = COLORS["accent1"],
            hover_color   = COLORS["accent2"],
            font          = ctk.CTkFont(size=14, weight="bold"),
            command       = self._handle_login
        )
        self.login_btn.pack(fill="x", padx=35, pady=(12, 8))

        # Register link
        ctk.CTkButton(
            self.card,
            text         = "Don't have an account? Register",
            height       = 30,
            fg_color     = "transparent",
            hover_color  = COLORS["card2"],
            text_color   = COLORS["accent1"],
            font         = ctk.CTkFont(size=11),
            command      = self._build_register_form
        ).pack()



        # Bind Enter key to login
        self.password_entry.bind("<Return>", lambda e: self._handle_login())
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

    def _build_register_form(self):
        """Builds the registration form inside the card."""

        for widget in self.card.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.card,
            text       = "Create Account 🎉",
            font       = ctk.CTkFont(size=22, weight="bold"),
            text_color = COLORS["text"]
        ).pack(pady=(30, 4))

        ctk.CTkLabel(
            self.card,
            text       = "Fill in the details below",
            font       = ctk.CTkFont(size=12),
            text_color = COLORS["subtext"]
        ).pack(pady=(0, 18))

        # Full Name
        ctk.CTkLabel(self.card, text="Full Name", font=ctk.CTkFont(size=12),
                     text_color=COLORS["subtext"], anchor="w").pack(fill="x", padx=35)
        self.reg_name = ctk.CTkEntry(self.card, placeholder_text="Enter your full name",
                                      height=40, corner_radius=10,
                                      fg_color=COLORS["input_bg"],
                                      border_color=COLORS["border"])
        self.reg_name.pack(fill="x", padx=35, pady=(3, 10))

        # Username
        ctk.CTkLabel(self.card, text="Username", font=ctk.CTkFont(size=12),
                     text_color=COLORS["subtext"], anchor="w").pack(fill="x", padx=35)
        self.reg_username = ctk.CTkEntry(self.card, placeholder_text="Choose a username",
                                          height=40, corner_radius=10,
                                          fg_color=COLORS["input_bg"],
                                          border_color=COLORS["border"])
        self.reg_username.pack(fill="x", padx=35, pady=(3, 10))

        # Password
        ctk.CTkLabel(self.card, text="Password", font=ctk.CTkFont(size=12),
                     text_color=COLORS["subtext"], anchor="w").pack(fill="x", padx=35)
        self.reg_password = ctk.CTkEntry(self.card, placeholder_text="Choose a password",
                                          show="●", height=40, corner_radius=10,
                                          fg_color=COLORS["input_bg"],
                                          border_color=COLORS["border"])
        self.reg_password.pack(fill="x", padx=35, pady=(3, 5))

        # Error label
        self.reg_error = ctk.CTkLabel(self.card, text="",
                                       font=ctk.CTkFont(size=11),
                                       text_color=COLORS["danger"])
        self.reg_error.pack(pady=(3, 0))

        # Register button
        ctk.CTkButton(
            self.card,
            text          = "Create Account  →",
            height        = 44,
            corner_radius = 12,
            fg_color      = COLORS["accent3"],
            hover_color   = "#059669",
            font          = ctk.CTkFont(size=13, weight="bold"),
            command       = self._handle_register
        ).pack(fill="x", padx=35, pady=(8, 6))

        # Back to login
        ctk.CTkButton(
            self.card,
            text        = "← Back to Login",
            height      = 30,
            fg_color    = "transparent",
            hover_color = COLORS["card2"],
            text_color  = COLORS["accent1"],
            font        = ctk.CTkFont(size=11),
            command     = self._build_login_form
        ).pack()

    # ── EVENT HANDLERS ─────────────────────────────────────
    def _handle_login(self):
        """Handles the login button click event."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self._show_error("Please fill in all fields.")
            self._shake_card()
            return

        # Verify credentials against database
        user = login_user(username, password)

        if user:
            self.login_btn.configure(text="✓  Login Successful!", fg_color=COLORS["accent3"])
            self.after(600, lambda: self.on_login_success(user))
        else:
            self._show_error("Invalid username or password.")
            self._shake_card()

    def _handle_register(self):
        """Handles the registration form submission."""
        full_name = self.reg_name.get().strip()
        username  = self.reg_username.get().strip()
        password  = self.reg_password.get().strip()

        if not full_name or not username or not password:
            self.reg_error.configure(text="All fields are required.")
            return

        if len(password) < 6:
            self.reg_error.configure(text="Password must be at least 6 characters.")
            return

        success = register_user(username, password, full_name)

        if success:
            self.reg_error.configure(text="Account created! Please login.", text_color=COLORS["accent3"])
            self.after(1500, self._build_login_form)
        else:
            self.reg_error.configure(text="Username already exists. Try another.", text_color=COLORS["danger"])

    def _toggle_password(self):
        """Toggles password visibility in the password field."""
        if self.password_visible:
            self.password_entry.configure(show="●")
            self.show_pass_btn.configure(text="Show Password")
            self.password_visible = False
        else:
            self.password_entry.configure(show="")
            self.show_pass_btn.configure(text="Hide Password")
            self.password_visible = True

    def _show_error(self, message):
        """Displays an error message below the password field."""
        self.error_label.configure(text=message, text_color=COLORS["danger"])
        self.after(3000, lambda: self.error_label.configure(text=""))

    def _shake_card(self):
        """Applies a horizontal shake animation to the login card."""
        original_x = 0.72
        shakes = [0.01, -0.01, 0.008, -0.008, 0.005, -0.005, 0]
        for i, offset in enumerate(shakes):
            self.after(i * 40, lambda ox=offset: self.card.place(
                relx=original_x + ox, rely=0.5, anchor="center"
            ))


# ── Test Login UI directly ─────────────────────────────────
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Smart Budget Analysis Tool")
    app.geometry("1100x700")
    app.resizable(True, True)

    # Center window on screen
    app.update_idletasks()
    x = (app.winfo_screenwidth()  - 1100) // 2
    y = (app.winfo_screenheight() - 700)  // 2
    app.geometry(f"1100x700+{x}+{y}")

    def on_login(user):
        print(f"Login successful! User: {user['full_name']}")
        app.destroy()

    LoginUI(app, on_login_success=on_login)
    app.mainloop()
