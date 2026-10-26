"""
DASHBOARD UI MODULE
===================
This module contains the main dashboard interface after login.
Features:
- Animated sidebar navigation
- Stats cards with count-up animation
- Recent expenses list
- Budget status bars
- AI insights panel
- Live clock
- Dark theme throughout
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import sys
import os
import datetime
import threading
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.expense_manager  import (get_all_expenses, add_expense,
                                       delete_expense, get_category_totals,
                                       get_monthly_totals, get_dashboard_stats,
                                       search_expenses, CATEGORIES, PAYMENT_METHODS)
from modules.budget_goals     import (set_budget_goal, get_budget_goals,
                                       check_budget_status, get_alert_messages,
                                       delete_budget_goal)
from modules.ml_predictor     import (predict_next_3_months, get_spending_trend,
                                       get_prediction_insights)
from modules.export_manager   import (export_to_csv, export_to_json,
                                       export_to_txt, export_to_pdf)

# ── Color Scheme ───────────────────────────────────────────
COLORS = {
    "bg"       : "#0A0E1A",
    "sidebar"  : "#0F1629",
    "card"     : "#111827",
    "card2"    : "#1F2937",
    "accent1"  : "#6366F1",
    "accent2"  : "#8B5CF6",
    "accent3"  : "#10B981",
    "accent4"  : "#F59E0B",
    "danger"   : "#EF4444",
    "text"     : "#F9FAFB",
    "subtext"  : "#9CA3AF",
    "border"   : "#374151",
    "input_bg" : "#1F2937",
    "hover"    : "#1F2937",
}

CAT_COLORS = [
    "#6366F1","#8B5CF6","#10B981","#F59E0B",
    "#EF4444","#3B82F6","#EC4899","#14B8A6","#F97316"
]


class DashboardUI(ctk.CTkFrame):
    """
    Main Dashboard UI containing sidebar navigation and all pages.
    """

    def __init__(self, master, user, on_logout):
        """
        Initializes the Dashboard.

        Parameters:
            master    : Parent window
            user      : Logged-in user dictionary
            on_logout : Callback function for logout
        """
        super().__init__(master, fg_color=COLORS["bg"])
        self.master    = master
        self.user      = user
        self.on_logout = on_logout
        self.pack(fill="both", expand=True)
        self._build()
        self.after(100, lambda: self._navigate("home"))

    # ── CARD HELPER ────────────────────────────────────────
    def _card(self, parent, **kwargs):
        """Creates a styled card frame."""
        return ctk.CTkFrame(
            parent,
            fg_color      = COLORS["card"],
            corner_radius = 14,
            border_width  = 1,
            border_color  = COLORS["border"],
            **kwargs
        )

    # ── BUILD LAYOUT ───────────────────────────────────────
    def _build(self):
        """Builds the main layout with sidebar and content area."""

        # ── Sidebar ──────────────────────────────────────
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color      = COLORS["sidebar"],
            corner_radius = 0,
            width         = 220,
            border_width  = 1,
            border_color  = COLORS["border"]
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo area
        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color      = COLORS["accent1"],
            corner_radius = 0,
            height        = 70
        )
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)

        ctk.CTkLabel(
            logo_frame,
            text       = "💰  BudgetPro",
            font       = ctk.CTkFont(size=18, weight="bold"),
            text_color = "white"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # User badge
        user_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color      = COLORS["card2"],
            corner_radius = 10
        )
        user_frame.pack(fill="x", padx=12, pady=12)

        ctk.CTkLabel(
            user_frame,
            text = "👤",
            font = ctk.CTkFont(size=20)
        ).pack(side="left", padx=10, pady=8)

        info = ctk.CTkFrame(user_frame, fg_color="transparent")
        info.pack(side="left")

        ctk.CTkLabel(
            info,
            text       = self.user["full_name"],
            font       = ctk.CTkFont(size=12, weight="bold"),
            text_color = COLORS["accent1"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            info,
            text       = f"@{self.user['username']}",
            font       = ctk.CTkFont(size=10),
            text_color = COLORS["subtext"]
        ).pack(anchor="w")

        # Navigation buttons
        self.nav_btns = {}
        nav_items = [
            ("🏠   Home",              "home"),
            ("➕   Add Expense",        "add"),
            ("📋   All Expenses",       "list"),
            ("📊   Charts",             "charts"),
            ("🎯   Budget Goals",       "goals"),
            ("🤖   AI Predictions",     "predictions"),
            ("📁   Export Data",        "export"),
            ("ℹ️    About",             "about"),
        ]

        ctk.CTkLabel(
            self.sidebar,
            text       = "NAVIGATION",
            font       = ctk.CTkFont(size=9),
            text_color = COLORS["subtext"]
        ).pack(anchor="w", padx=15, pady=(5, 3))

        for label, key in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text          = label,
                anchor        = "w",
                height        = 40,
                corner_radius = 8,
                fg_color      = "transparent",
                hover_color   = COLORS["hover"],
                text_color    = COLORS["subtext"],
                font          = ctk.CTkFont(size=13),
                command       = lambda k=key: self._navigate(k)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_btns[key] = btn

        # Developer credit in sidebar — subtle
        ctk.CTkLabel(
            self.sidebar,
            text       = "Dev: Arpit Nigam",
            font       = ctk.CTkFont(size=9),
            text_color = "#374151"
        ).pack(side="bottom", pady=(0, 5))

        # Logout button
        ctk.CTkButton(
            self.sidebar,
            text          = "🚪   Logout",
            anchor        = "w",
            height        = 40,
            corner_radius = 8,
            fg_color      = "transparent",
            hover_color   = "#2D1B1B",
            text_color    = COLORS["danger"],
            font          = ctk.CTkFont(size=13),
            command       = self._logout
        ).pack(side="bottom", fill="x", padx=10, pady=(0, 8))

        # ── Main Content ─────────────────────────────────
        self.content = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        self.content.pack(side="right", fill="both", expand=True)

        # Top bar
        topbar = ctk.CTkFrame(
            self.content,
            fg_color     = COLORS["sidebar"],
            corner_radius = 0,
            height        = 55,
            border_width  = 1,
            border_color  = COLORS["border"]
        )
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        self.page_title = ctk.CTkLabel(
            topbar,
            text       = "Dashboard",
            font       = ctk.CTkFont(size=16, weight="bold"),
            text_color = COLORS["text"]
        )
        self.page_title.pack(side="left", padx=20)

        self.clock_lbl = ctk.CTkLabel(
            topbar,
            text       = "",
            font       = ctk.CTkFont(size=11),
            text_color = COLORS["subtext"]
        )
        self.clock_lbl.pack(side="right", padx=20)
        self._update_clock()

        # Scrollable page frame
        self.page = ctk.CTkScrollableFrame(
            self.content,
            fg_color               = COLORS["bg"],
            scrollbar_button_color = COLORS["border"]
        )
        self.page.pack(fill="both", expand=True)

    # ── CLOCK ──────────────────────────────────────────────
    def _update_clock(self):
        """Updates the live clock in the top bar every second."""
        now = datetime.datetime.now().strftime("%d %b %Y   %H:%M:%S")
        self.clock_lbl.configure(text=now)
        self.after(1000, self._update_clock)

    # ── NAVIGATION ─────────────────────────────────────────
    def _navigate(self, key):
        """Handles sidebar navigation and page switching."""

        # Update button highlight states
        for k, btn in self.nav_btns.items():
            if k == key:
                btn.configure(fg_color=COLORS["accent1"], text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["subtext"])

        # Clear current page content
        for w in self.page.winfo_children():
            w.destroy()

        # Load selected page
        pages = {
            "home"        : self._page_home,
            "add"         : self._page_add,
            "list"        : self._page_list,
            "charts"      : self._page_charts,
            "goals"       : self._page_goals,
            "predictions" : self._page_predictions,
            "export"      : self._page_export,
            "about"       : self._page_about,
        }
        self.page_title.configure(text={
            "home"        : "🏠  Dashboard",
            "add"         : "➕  Add Expense",
            "list"        : "📋  All Expenses",
            "charts"      : "📊  Charts & Analysis",
            "goals"       : "🎯  Budget Goals",
            "predictions" : "🤖  AI Predictions",
            "export"      : "📁  Export Data",
            "about"       : "ℹ️   About",
        }.get(key, "Dashboard"))

        pages[key]()

    # ══════════════════════════════════════════════════════
    # PAGE: HOME
    # ══════════════════════════════════════════════════════
    def _page_home(self):
        """Renders the home dashboard page."""
        p     = self.page
        uid   = self.user["id"]
        stats = get_dashboard_stats(uid)

        # Welcome message
        ctk.CTkLabel(
            p,
            text       = f"Welcome back, {self.user['full_name']}! 👋",
            font       = ctk.CTkFont(size=20, weight="bold"),
            text_color = COLORS["accent1"]
        ).pack(anchor="w", padx=25, pady=(20, 2))

        ctk.CTkLabel(
            p,
            text       = datetime.datetime.now().strftime("Today is %A, %d %B %Y"),
            font       = ctk.CTkFont(size=12),
            text_color = COLORS["subtext"]
        ).pack(anchor="w", padx=25, pady=(0, 15))

        # Alert messages
        alerts = get_alert_messages(uid)
        for alert in alerts:
            alert_frame = ctk.CTkFrame(p, fg_color="#2D1B1B", corner_radius=8,
                                        border_width=1, border_color=COLORS["danger"])
            alert_frame.pack(fill="x", padx=20, pady=3)
            ctk.CTkLabel(alert_frame, text=f"⚠  {alert}",
                         font=ctk.CTkFont(size=11),
                         text_color=COLORS["danger"]).pack(anchor="w", padx=12, pady=8)

        # Stats cards row
        stats_row = ctk.CTkFrame(p, fg_color="transparent")
        stats_row.pack(fill="x", padx=20, pady=5)

        cards_data = [
            ("💰", "Total Spent",    f"Rs. {stats['total_spent']:,.0f}",  COLORS["accent1"]),
            ("📅", "This Month",     f"Rs. {stats['month_spent']:,.0f}",  COLORS["accent2"]),
            ("📝", "Transactions",   str(stats["total_count"]),            COLORS["accent3"]),
            ("📊", "Avg / Entry",    f"Rs. {stats['avg_expense']:,.0f}",  COLORS["accent4"]),
        ]

        for icon, title, value, color in cards_data:
            card = self._card(stats_row)
            card.pack(side="left", fill="both", expand=True, padx=6)
            ctk.CTkLabel(card, text=icon,
                         font=ctk.CTkFont(size=26)).pack(pady=(18, 0))
            ctk.CTkLabel(card, text=value,
                         font=ctk.CTkFont(size=20, weight="bold"),
                         text_color=color).pack()
            ctk.CTkLabel(card, text=title,
                         font=ctk.CTkFont(size=11),
                         text_color=COLORS["subtext"]).pack(pady=(0, 18))

        # Bottom row — Recent expenses + AI insights
        bottom = ctk.CTkFrame(p, fg_color="transparent")
        bottom.pack(fill="both", expand=True, padx=20, pady=10)

        # Recent Expenses
        recent_card = self._card(bottom)
        recent_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        ctk.CTkLabel(recent_card, text="🕐  Recent Expenses",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=15, pady=(15, 8))

        recent = stats.get("recent_expenses", [])
        if not recent:
            ctk.CTkLabel(recent_card, text="No expenses yet.\nAdd your first expense!",
                         font=ctk.CTkFont(size=12),
                         text_color=COLORS["subtext"],
                         justify="center").pack(pady=30)
        else:
            for e in recent:
                row = ctk.CTkFrame(recent_card, fg_color=COLORS["hover"],
                                    corner_radius=8)
                row.pack(fill="x", padx=12, pady=3)
                ctk.CTkLabel(row, text=e["category"][0],
                             font=ctk.CTkFont(size=14),
                             width=35).pack(side="left", padx=8, pady=6)
                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="both", expand=True)
                ctk.CTkLabel(info, text=e["description"][:22],
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=COLORS["text"],
                             anchor="w").pack(anchor="w")
                ctk.CTkLabel(info, text=f"{e['date']}  •  {e['category']}",
                             font=ctk.CTkFont(size=9),
                             text_color=COLORS["subtext"],
                             anchor="w").pack(anchor="w")
                ctk.CTkLabel(row, text=f"Rs.{e['amount']:,.0f}",
                             font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=COLORS["accent3"]).pack(side="right", padx=12)

        # AI Insights
        ai_card = self._card(bottom)
        ai_card.pack(side="right", fill="both", expand=True, padx=(8, 0))
        ctk.CTkLabel(ai_card, text="🤖  AI Insights",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=15, pady=(15, 8))

        insights = get_prediction_insights(uid)
        for insight in insights:
            row = ctk.CTkFrame(ai_card, fg_color=COLORS["hover"], corner_radius=8)
            row.pack(fill="x", padx=12, pady=4)
            ctk.CTkLabel(row, text=f"  {insight}",
                         font=ctk.CTkFont(size=11),
                         text_color=COLORS["subtext"],
                         wraplength=260,
                         justify="left",
                         anchor="w").pack(anchor="w", padx=8, pady=8)

    # ══════════════════════════════════════════════════════
    # PAGE: ADD EXPENSE
    # ══════════════════════════════════════════════════════
    def _page_add(self):
        """Renders the Add Expense form page."""
        p   = self.page
        uid = self.user["id"]

        card = self._card(p)
        card.pack(padx=60, pady=25, fill="x")

        ctk.CTkLabel(card, text="Add New Expense",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS["accent1"]).pack(pady=(28, 4))
        ctk.CTkLabel(card, text="Fill in the details below",
                     font=ctk.CTkFont(size=12),
                     text_color=COLORS["subtext"]).pack(pady=(0, 20))

        def field_label(txt):
            ctk.CTkLabel(card, text=txt, font=ctk.CTkFont(size=12),
                         text_color=COLORS["subtext"], anchor="w").pack(fill="x", padx=40)

        def entry():
            return ctk.CTkEntry(card, height=42, corner_radius=10,
                                fg_color=COLORS["input_bg"],
                                border_color=COLORS["border"],
                                font=ctk.CTkFont(size=13))

        # Amount
        field_label("💵  Amount (Rs.)")
        amt_entry = entry()
        amt_entry.pack(fill="x", padx=40, pady=(3, 12))

        # Category
        field_label("🏷️  Category")
        cat_var  = ctk.StringVar(value=CATEGORIES[0])
        cat_menu = ctk.CTkOptionMenu(card, values=CATEGORIES,
                                      variable=cat_var, height=42,
                                      corner_radius=10,
                                      fg_color=COLORS["input_bg"],
                                      button_color=COLORS["accent1"],
                                      font=ctk.CTkFont(size=13))
        cat_menu.pack(fill="x", padx=40, pady=(3, 12))

        # Description
        field_label("📝  Description")
        desc_entry = entry()
        desc_entry.pack(fill="x", padx=40, pady=(3, 12))

        # Date
        field_label("📅  Date (YYYY-MM-DD)")
        date_entry = entry()
        date_entry.insert(0, datetime.date.today().isoformat())
        date_entry.pack(fill="x", padx=40, pady=(3, 12))

        # Payment
        field_label("💳  Payment Method")
        pay_var  = ctk.StringVar(value="Cash")
        pay_menu = ctk.CTkOptionMenu(card, values=PAYMENT_METHODS,
                                      variable=pay_var, height=42,
                                      corner_radius=10,
                                      fg_color=COLORS["input_bg"],
                                      button_color=COLORS["accent1"],
                                      font=ctk.CTkFont(size=13))
        pay_menu.pack(fill="x", padx=40, pady=(3, 12))

        status_lbl = ctk.CTkLabel(card, text="",
                                   font=ctk.CTkFont(size=12),
                                   text_color=COLORS["accent3"])
        status_lbl.pack()

        def save_expense():
            try:
                amount = float(amt_entry.get())
                if amount <= 0:
                    raise ValueError
            except ValueError:
                status_lbl.configure(text="Enter a valid positive amount.",
                                     text_color=COLORS["danger"])
                return

            desc = desc_entry.get().strip()
            if not desc:
                status_lbl.configure(text="Description cannot be empty.",
                                     text_color=COLORS["danger"])
                return

            try:
                datetime.date.fromisoformat(date_entry.get())
            except ValueError:
                status_lbl.configure(text="Invalid date format. Use YYYY-MM-DD.",
                                     text_color=COLORS["danger"])
                return

            result = add_expense(
                user_id     = uid,
                amount      = amount,
                category    = cat_var.get(),
                description = desc,
                date        = date_entry.get(),
                payment     = pay_var.get()
            )

            if result:
                status_lbl.configure(text="Expense added successfully!",
                                     text_color=COLORS["accent3"])
                amt_entry.delete(0, "end")
                desc_entry.delete(0, "end")
                date_entry.delete(0, "end")
                date_entry.insert(0, datetime.date.today().isoformat())
            else:
                status_lbl.configure(text="Failed to add expense. Try again.",
                                     text_color=COLORS["danger"])

        ctk.CTkButton(card, text="➕  Add Expense",
                      height=46, corner_radius=12,
                      fg_color=COLORS["accent1"],
                      hover_color=COLORS["accent2"],
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=save_expense).pack(fill="x", padx=40, pady=(10, 28))

    # ══════════════════════════════════════════════════════
    # PAGE: EXPENSE LIST
    # ══════════════════════════════════════════════════════
    def _page_list(self):
        """Renders the All Expenses list page with search and filter."""
        p   = self.page
        uid = self.user["id"]

        # Search and filter bar
        ctrl = self._card(p)
        ctrl.pack(fill="x", padx=20, pady=(15, 5))

        row = ctk.CTkFrame(ctrl, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=12)

        self.search_var = ctk.StringVar()
        search = ctk.CTkEntry(row, placeholder_text="🔍  Search expenses...",
                               textvariable=self.search_var,
                               height=38, corner_radius=10,
                               fg_color=COLORS["input_bg"],
                               border_color=COLORS["border"],
                               font=ctk.CTkFont(size=12), width=260)
        search.pack(side="left", padx=(0, 10))

        self.filter_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(row, values=["All"] + CATEGORIES,
                          variable=self.filter_var, height=38,
                          corner_radius=10,
                          fg_color=COLORS["input_bg"],
                          button_color=COLORS["accent1"],
                          font=ctk.CTkFont(size=12),
                          width=160,
                          command=lambda _: self._refresh_list(table_frame, uid)
                          ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(row, text="🔄  Refresh", height=38,
                      corner_radius=10,
                      fg_color=COLORS["accent3"],
                      font=ctk.CTkFont(size=12),
                      command=lambda: self._refresh_list(table_frame, uid)
                      ).pack(side="left")

        self.search_var.trace("w", lambda *a: self._refresh_list(table_frame, uid))

        # Table
        table_card = self._card(p)
        table_card.pack(fill="both", expand=True, padx=20, pady=5)

        # Header row
        header = ctk.CTkFrame(table_card, fg_color=COLORS["hover"], corner_radius=8)
        header.pack(fill="x", padx=12, pady=(12, 5))

        for h, w in [("#", 35), ("Date", 95), ("Category", 130),
                     ("Description", 230), ("Amount", 100),
                     ("Payment", 95), ("Action", 70)]:
            ctk.CTkLabel(header, text=h,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=COLORS["accent1"],
                         width=w, anchor="w").pack(side="left", padx=4, pady=8)

        table_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=12, pady=5)

        self._refresh_list(table_frame, uid)

    def _refresh_list(self, frame, uid):
        """Refreshes the expense list based on search and filter."""
        for w in frame.winfo_children():
            w.destroy()

        query    = self.search_var.get().lower()
        cat_filt = self.filter_var.get()

        all_exp  = get_all_expenses(uid)
        filtered = [
            e for e in all_exp
            if (query in e["description"].lower()
                or query in e["category"].lower()
                or query in str(e["amount"]))
            and (cat_filt == "All" or e["category"] == cat_filt)
        ]

        if not filtered:
            ctk.CTkLabel(frame, text="No expenses found.",
                         font=ctk.CTkFont(size=13),
                         text_color=COLORS["subtext"]).pack(pady=30)
            return

        for i, e in enumerate(filtered):
            row_color = COLORS["hover"] if i % 2 == 0 else COLORS["card"]
            row = ctk.CTkFrame(frame, fg_color=row_color, corner_radius=6)
            row.pack(fill="x", pady=2)

            vals = [str(i+1), e["date"], e["category"],
                    e["description"][:26],
                    f"Rs.{e['amount']:,.0f}", e.get("payment", "Cash")]
            widths = [35, 95, 130, 230, 100, 95]
            colors = [COLORS["subtext"], COLORS["text"], COLORS["accent4"],
                      COLORS["text"], COLORS["accent3"], COLORS["subtext"]]

            for v, w, c in zip(vals, widths, colors):
                ctk.CTkLabel(row, text=v, font=ctk.CTkFont(size=11),
                             text_color=c, width=w,
                             anchor="w").pack(side="left", padx=4, pady=7)

            def make_del(eid=e["id"]):
                def _del():
                    if messagebox.askyesno("Delete", "Delete this expense?"):
                        delete_expense(eid, uid)
                        self._refresh_list(frame, uid)
                return _del

            ctk.CTkButton(row, text="🗑", width=50, height=28,
                          corner_radius=6,
                          fg_color=COLORS["danger"],
                          hover_color="#B91C1C",
                          font=ctk.CTkFont(size=13),
                          command=make_del()).pack(side="left", padx=4)

    # ══════════════════════════════════════════════════════
    # PAGE: CHARTS
    # ══════════════════════════════════════════════════════
    def _page_charts(self):
        """Renders the Charts and Analysis page."""
        p   = self.page
        uid = self.user["id"]

        cat_totals = get_category_totals(uid)
        mon_totals = get_monthly_totals(uid)

        if not cat_totals:
            ctk.CTkLabel(p, text="No data to display.\nAdd some expenses first!",
                         font=ctk.CTkFont(size=16),
                         text_color=COLORS["subtext"],
                         justify="center").pack(pady=100)
            return

        charts_row = ctk.CTkFrame(p, fg_color="transparent")
        charts_row.pack(fill="both", expand=True, padx=15, pady=10)

        # Pie Chart
        fig1, ax1 = plt.subplots(figsize=(5, 4))
        fig1.patch.set_facecolor("#111827")
        ax1.set_facecolor("#111827")

        cats  = list(cat_totals.keys())
        vals  = list(cat_totals.values())
        clrs  = CAT_COLORS[:len(cats)]

        wedges, _, autotexts = ax1.pie(
            vals, colors=clrs, autopct="%1.1f%%",
            startangle=140,
            pctdistance=0.8,
            wedgeprops=dict(width=0.6, edgecolor="#0A0E1A", linewidth=2)
        )
        for at in autotexts:
            at.set_color("white")
            at.set_fontsize(8)

        ax1.legend(cats, loc="center left",
                   bbox_to_anchor=(-0.3, 0.5),
                   fontsize=7, frameon=False,
                   labelcolor="white")
        ax1.set_title("Expenses by Category",
                      color=COLORS["accent1"], fontsize=11, pad=10)
        plt.tight_layout()

        for fig in [fig1]:
            card = self._card(charts_row)
            card.pack(side="left", fill="both", expand=True, padx=6)
            canvas = FigureCanvasTkAgg(fig, master=card)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        # Bar Chart
        if mon_totals:
            fig2, ax2 = plt.subplots(figsize=(5, 4))
            fig2.patch.set_facecolor("#111827")
            ax2.set_facecolor("#111827")

            months = sorted(mon_totals.keys())
            m_vals = [mon_totals[m] for m in months]

            bars = ax2.bar(months, m_vals,
                           color=CAT_COLORS[:len(months)],
                           width=0.5, edgecolor="#0A0E1A")
            for bar, val in zip(bars, m_vals):
                ax2.text(bar.get_x() + bar.get_width()/2,
                         bar.get_height() + max(m_vals)*0.02,
                         f"Rs.{val:.0f}",
                         ha="center", color="white", fontsize=8)

            ax2.tick_params(colors="white")
            ax2.spines[:].set_color(COLORS["border"])
            ax2.set_title("Monthly Spending",
                          color=COLORS["accent2"], fontsize=11)
            plt.xticks(rotation=20, color="white", fontsize=8)
            plt.tight_layout()

            card2 = self._card(charts_row)
            card2.pack(side="left", fill="both", expand=True, padx=6)
            canvas2 = FigureCanvasTkAgg(fig2, master=card2)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    # ══════════════════════════════════════════════════════
    # PAGE: BUDGET GOALS
    # ══════════════════════════════════════════════════════
    def _page_goals(self):
        """Renders the Budget Goals management page."""
        p   = self.page
        uid = self.user["id"]

        # Set Goal Form
        form_card = self._card(p)
        form_card.pack(padx=30, pady=(20, 10), fill="x")

        ctk.CTkLabel(form_card, text="Set Monthly Budget Goal",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLORS["accent1"]).pack(pady=(20, 5))

        row = ctk.CTkFrame(form_card, fg_color="transparent")
        row.pack(fill="x", padx=30, pady=10)

        cat_var = ctk.StringVar(value=CATEGORIES[0])
        ctk.CTkOptionMenu(row, values=CATEGORIES, variable=cat_var,
                          height=40, corner_radius=10,
                          fg_color=COLORS["input_bg"],
                          button_color=COLORS["accent1"],
                          font=ctk.CTkFont(size=13),
                          width=200).pack(side="left", padx=(0, 10))

        amt_entry = ctk.CTkEntry(row, placeholder_text="Budget amount (Rs.)",
                                  height=40, corner_radius=10,
                                  fg_color=COLORS["input_bg"],
                                  border_color=COLORS["border"],
                                  font=ctk.CTkFont(size=13),
                                  width=200)
        amt_entry.pack(side="left", padx=(0, 10))

        status_lbl = ctk.CTkLabel(form_card, text="",
                                   font=ctk.CTkFont(size=11),
                                   text_color=COLORS["accent3"])
        status_lbl.pack()

        def save_goal():
            try:
                amount = float(amt_entry.get())
                if amount <= 0:
                    raise ValueError
            except ValueError:
                status_lbl.configure(text="Enter a valid amount.",
                                     text_color=COLORS["danger"])
                return
            result = set_budget_goal(uid, cat_var.get(), amount)
            if result:
                status_lbl.configure(text="Budget goal saved successfully!",
                                     text_color=COLORS["accent3"])
                amt_entry.delete(0, "end")
                self._refresh_goals(goals_frame, uid)
            else:
                status_lbl.configure(text="Failed to save goal.",
                                     text_color=COLORS["danger"])

        ctk.CTkButton(row, text="Save Goal", height=40,
                      corner_radius=10,
                      fg_color=COLORS["accent1"],
                      hover_color=COLORS["accent2"],
                      font=ctk.CTkFont(size=13),
                      command=save_goal).pack(side="left")

        ctk.CTkFrame(form_card, fg_color="transparent", height=10).pack()

        # Goals Status
        status_card = self._card(p)
        status_card.pack(fill="x", padx=30, pady=5)
        ctk.CTkLabel(status_card, text="Current Month Budget Status",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=15, pady=(15, 8))

        goals_frame = ctk.CTkFrame(status_card, fg_color="transparent")
        goals_frame.pack(fill="x", padx=15, pady=(0, 15))
        self._refresh_goals(goals_frame, uid)

    def _refresh_goals(self, frame, uid):
        """Refreshes the budget goals status display."""
        for w in frame.winfo_children():
            w.destroy()

        status_list = check_budget_status(uid)

        if not status_list:
            ctk.CTkLabel(frame, text="No budget goals set yet.",
                         font=ctk.CTkFont(size=12),
                         text_color=COLORS["subtext"]).pack(pady=20)
            return

        status_colors = {
            "Safe"     : COLORS["accent3"],
            "Warning"  : COLORS["accent4"],
            "Exceeded" : COLORS["danger"],
        }

        for s in status_list:
            row = ctk.CTkFrame(frame, fg_color=COLORS["hover"], corner_radius=8)
            row.pack(fill="x", pady=4)

            ctk.CTkLabel(row, text=s["category"],
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=COLORS["text"],
                         width=130, anchor="w").pack(side="left", padx=12, pady=10)

            # Progress bar
            bar_bg = ctk.CTkFrame(row, fg_color=COLORS["card2"],
                                   corner_radius=5, height=14)
            bar_bg.pack(side="left", fill="x", expand=True, padx=8)
            pct = min(s["percentage"] / 100, 1.0)
            bar = ctk.CTkFrame(bar_bg,
                                fg_color=status_colors[s["status"]],
                                corner_radius=5, height=14)
            bar.place(relx=0, rely=0, relwidth=pct, relheight=1)

            ctk.CTkLabel(row, text=f"{s['percentage']}%",
                         font=ctk.CTkFont(size=10),
                         text_color=status_colors[s["status"]],
                         width=50).pack(side="left")

            ctk.CTkLabel(row,
                         text=f"Rs.{s['spent']:,.0f} / Rs.{s['goal']:,.0f}",
                         font=ctk.CTkFont(size=10),
                         text_color=COLORS["subtext"],
                         width=150).pack(side="left")

            ctk.CTkLabel(row, text=s["status"],
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=status_colors[s["status"]],
                         width=80).pack(side="left", padx=(0, 12))

    # ══════════════════════════════════════════════════════
    # PAGE: AI PREDICTIONS
    # ══════════════════════════════════════════════════════
    def _page_predictions(self):
        """Renders the AI Predictions page."""
        p   = self.page
        uid = self.user["id"]

        ctk.CTkLabel(p, text="🤖  AI Expense Predictions",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=COLORS["accent1"]).pack(anchor="w", padx=25, pady=(20, 5))
        ctk.CTkLabel(p, text="Based on your spending history using Linear Regression",
                     font=ctk.CTkFont(size=12),
                     text_color=COLORS["subtext"]).pack(anchor="w", padx=25, pady=(0, 15))

        # Trend card
        trend = get_spending_trend(uid)
        trend_colors = {
            "Increasing"        : COLORS["danger"],
            "Decreasing"        : COLORS["accent3"],
            "Stable"            : COLORS["accent4"],
            "Insufficient Data" : COLORS["subtext"],
        }
        trend_card = self._card(p)
        trend_card.pack(fill="x", padx=25, pady=5)
        ctk.CTkLabel(trend_card,
                     text=f"Spending Trend:  {trend}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=trend_colors.get(trend, COLORS["subtext"])
                     ).pack(pady=15)

        # 3 Month predictions
        pred_card = self._card(p)
        pred_card.pack(fill="x", padx=25, pady=10)
        ctk.CTkLabel(pred_card, text="Next 3 Months Predicted Spending",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=15, pady=(15, 8))

        predictions = predict_next_3_months(uid)

        if not predictions:
            ctk.CTkLabel(pred_card,
                         text="Not enough data for predictions.\nAdd expenses for at least 2 months.",
                         font=ctk.CTkFont(size=12),
                         text_color=COLORS["subtext"],
                         justify="center").pack(pady=20)
        else:
            pred_row = ctk.CTkFrame(pred_card, fg_color="transparent")
            pred_row.pack(fill="x", padx=15, pady=(0, 15))

            colors = [COLORS["accent1"], COLORS["accent2"], COLORS["accent3"]]
            for i, (month, amount) in enumerate(predictions.items()):
                card = ctk.CTkFrame(pred_row,
                                     fg_color=COLORS["card2"],
                                     corner_radius=12,
                                     border_width=1,
                                     border_color=colors[i])
                card.pack(side="left", fill="both", expand=True, padx=6)
                ctk.CTkLabel(card, text=month,
                             font=ctk.CTkFont(size=12),
                             text_color=COLORS["subtext"]).pack(pady=(15, 2))
                ctk.CTkLabel(card, text=f"Rs. {amount:,.0f}",
                             font=ctk.CTkFont(size=20, weight="bold"),
                             text_color=colors[i]).pack(pady=(0, 15))

        # AI Insights
        insights_card = self._card(p)
        insights_card.pack(fill="x", padx=25, pady=10)
        ctk.CTkLabel(insights_card, text="AI Generated Insights",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=15, pady=(15, 8))

        insights = get_prediction_insights(uid)
        for insight in insights:
            row = ctk.CTkFrame(insights_card,
                                fg_color=COLORS["hover"],
                                corner_radius=8)
            row.pack(fill="x", padx=12, pady=4)
            ctk.CTkLabel(row, text=f"  💡  {insight}",
                         font=ctk.CTkFont(size=12),
                         text_color=COLORS["subtext"],
                         anchor="w",
                         wraplength=700,
                         justify="left").pack(anchor="w", padx=8, pady=10)

        ctk.CTkFrame(insights_card, height=10, fg_color="transparent").pack()

    # ══════════════════════════════════════════════════════
    # PAGE: EXPORT
    # ══════════════════════════════════════════════════════
    def _page_export(self):
        """Renders the Export Data page."""
        p        = self.page
        uid      = self.user["id"]
        username = self.user["username"]

        card = self._card(p)
        card.pack(padx=60, pady=30, fill="x")

        ctk.CTkLabel(card, text="Export Your Data",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS["accent1"]).pack(pady=(28, 5))
        ctk.CTkLabel(card, text="Save your expense data in different formats",
                     font=ctk.CTkFont(size=12),
                     text_color=COLORS["subtext"]).pack(pady=(0, 20))

        self.export_status = ctk.CTkLabel(card, text="",
                                           font=ctk.CTkFont(size=12),
                                           text_color=COLORS["accent3"])
        self.export_status.pack()

        def do_export(func, label):
            path = func(uid, username)
            if path:
                self.export_status.configure(
                    text=f"Exported successfully!\nSaved to: {path}",
                    text_color=COLORS["accent3"]
                )
            else:
                self.export_status.configure(
                    text="Export failed. No expenses found.",
                    text_color=COLORS["danger"]
                )

        export_options = [
            ("📊  Export as CSV",     export_to_csv,  COLORS["accent1"]),
            ("📄  Export as JSON",    export_to_json, COLORS["accent2"]),
            ("📋  Export as TXT",     export_to_txt,  COLORS["accent3"]),
            ("📰  Export as PDF",     export_to_pdf,  COLORS["accent4"]),
        ]

        for label, func, color in export_options:
            ctk.CTkButton(card, text=label, height=46,
                          corner_radius=12,
                          fg_color=color,
                          font=ctk.CTkFont(size=13, weight="bold"),
                          command=lambda f=func, l=label: do_export(f, l)
                          ).pack(fill="x", padx=50, pady=5)

        ctk.CTkFrame(card, height=20, fg_color="transparent").pack()

    # ══════════════════════════════════════════════════════
    # PAGE: ABOUT
    # ══════════════════════════════════════════════════════
    def _page_about(self):
        """Renders the About page with app and developer info."""
        p = self.page

        card = self._card(p)
        card.pack(padx=50, pady=25, fill="x")

        ctk.CTkLabel(card, text="💰",
                     font=ctk.CTkFont(size=55)).pack(pady=(28, 4))
        ctk.CTkLabel(card, text="Smart Budget Analysis Tool",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=COLORS["accent1"]).pack()
        ctk.CTkLabel(card, text="with Predictive Analytics",
                     font=ctk.CTkFont(size=14),
                     text_color=COLORS["accent2"]).pack(pady=(2, 20))

        sep = ctk.CTkFrame(card, height=1, fg_color=COLORS["border"])
        sep.pack(fill="x", padx=30, pady=5)

        # Features grid
        features = [
            ("🔐", "Secure Login",       "Bcrypt encrypted authentication",  COLORS["accent2"]),
            ("➕", "Expense Tracking",   "Add, view, filter and delete",     COLORS["accent1"]),
            ("📊", "Visual Charts",      "Pie and bar charts",               COLORS["accent3"]),
            ("🎯", "Budget Goals",       "Category wise monthly limits",     COLORS["accent4"]),
            ("🤖", "AI Predictions",     "ML based spending forecast",       "#EC4899"),
            ("📁", "Export Data",        "CSV, JSON, TXT, PDF formats",      "#3B82F6"),
        ]

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=30, pady=10)

        for i, (icon, title, desc, color) in enumerate(features):
            col = i % 2
            row_num = i // 2
            fc = ctk.CTkFrame(grid, fg_color=COLORS["card2"],
                               corner_radius=10,
                               border_width=1,
                               border_color=COLORS["border"])
            fc.grid(row=row_num, column=col, padx=6, pady=6, sticky="nsew")
            grid.grid_columnconfigure(col, weight=1)

            top = ctk.CTkFrame(fc, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=(12, 4))

            pill = ctk.CTkFrame(top, fg_color=color,
                                 corner_radius=8, width=34, height=34)
            pill.pack(side="left")
            pill.pack_propagate(False)
            ctk.CTkLabel(pill, text=icon,
                         font=ctk.CTkFont(size=15)).place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(top, text=title,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=COLORS["text"]).pack(side="left", padx=10)

            ctk.CTkLabel(fc, text=desc,
                         font=ctk.CTkFont(size=10),
                         text_color=COLORS["subtext"],
                         anchor="w").pack(anchor="w", padx=12, pady=(0, 12))

        sep2 = ctk.CTkFrame(card, height=1, fg_color=COLORS["border"])
        sep2.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(card,
                     text="Tech Stack:  Python 3  •  CustomTkinter  •  SQLite  •  Pandas  •  Scikit-learn  •  Matplotlib",
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS["subtext"]).pack(pady=(0, 6))

        ctk.CTkLabel(card, text="© 2026  Arpit Nigam",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["accent4"]).pack(pady=(0, 25))

    # ── LOGOUT ─────────────────────────────────────────────
    def _logout(self):
        """Handles logout with confirmation."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.on_logout()
