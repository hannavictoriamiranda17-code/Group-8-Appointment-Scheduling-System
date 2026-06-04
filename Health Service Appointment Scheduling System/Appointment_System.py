import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, date

#  Data persistence

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../appointments.json")

def load_appointments():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_appointments(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        messagebox.showerror("Save Error", f"Could not save appointments:\n{e}")

#  Color palette

BG      = "#25046E"
PANEL   = "#170247"
ACCENT  = "#00C841"
ACCENT2 = "#FF0000"
SUCCESS = "#49CC0F"
TEXT    = "#FFFFFF"
SUBTEXT = "#72767D"
BORDER  = "#2E3140"
HOVER   = "#2C2F3E"
WHITE   = "#FFFFFF"

PLACEHOLDER = "Search by name or service…"


class AppointmentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Appointment Scheduler")
        self.geometry("1120x720")
        self.minsize(800, 500)
        self.configure(bg=BG)
        self.appointments = load_appointments()
        self.filter_var = tk.StringVar(value="All")
        self._search_placeholder = True
        self._build_styles()
        self._build_ui()
        self._refresh_list()

    # Styles
    def _build_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")

        s.configure("TFrame",       background=BG)
        s.configure("Panel.TFrame", background=PANEL)

        s.configure("Accent.TButton",
                    background=ACCENT, foreground=WHITE,
                    font=("Segoe UI", 10, "bold"),
                    borderwidth=0, focusthickness=0, padding=(14, 8))
        s.map("Accent.TButton",
              background=[("active", "#4752C4"), ("pressed", "#3B4099")])

        s.configure("Del.TButton",
                    background=ACCENT2, foreground=WHITE,
                    font=("Segoe UI", 10, "bold"),
                    borderwidth=0, focusthickness=0, padding=(14, 8))
        s.map("Del.TButton",
              background=[("active", "#FFABBA"), ("pressed", "#FFCCD5")])

        s.configure("Ghost.TButton",
                    background=HOVER, foreground=TEXT,
                    font=("Segoe UI", 9),
                    borderwidth=0, focusthickness=0, padding=(10, 6))
        s.map("Ghost.TButton",
              background=[("active", BORDER), ("pressed", BORDER)])

        s.configure("Custom.Treeview",
                    background=PANEL, foreground=TEXT,
                    fieldbackground=PANEL, borderwidth=0,
                    rowheight=44, font=("Segoe UI", 10))
        s.configure("Custom.Treeview.Heading",
                    background=BORDER, foreground=WHITE,
                    font=("Segoe UI", 10, "bold"),
                    borderwidth=0, relief="flat", padding=(8, 6))
        s.map("Custom.Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", WHITE)])

        self.option_add("*TCombobox*Listbox.background",      BORDER)
        self.option_add("*TCombobox*Listbox.foreground",      TEXT)
        self.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
        self.option_add("*TCombobox*Listbox.selectForeground", WHITE)

    # Root layout
    def _build_ui(self):
        sidebar = tk.Frame(self, bg=PANEL, width=264)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        self._build_sidebar(sidebar)

        main = tk.Frame(self, bg=BG)
        main.pack(side="left", fill="both", expand=True)
        self._build_header(main)
        self._build_content(main)

    # Sidebar
    def _build_sidebar(self, s):
        logo = tk.Frame(s, bg=PANEL)
        logo.pack(fill="x", padx=24, pady=(28, 4))
        tk.Label(logo, text="📅", font=("Segoe UI Emoji", 26), bg=PANEL, fg=ACCENT).pack(anchor="w")
        tk.Label(logo, text="Scheduler",           font=("Segoe UI", 18, "bold"), bg=PANEL, fg=WHITE).pack(anchor="w")
        tk.Label(logo, text="Appointment Manager", font=("Segoe UI",  9),         bg=PANEL, fg=SUBTEXT).pack(anchor="w")

        tk.Frame(s, bg=BORDER, height=1).pack(fill="x", padx=20, pady=18)

        tk.Label(s, text="OVERVIEW", font=("Segoe UI", 8, "bold"), bg=PANEL, fg=SUBTEXT).pack(anchor="w", padx=24, pady=(0, 8))
        self.stat_total_var  = tk.StringVar(value="0")
        self.stat_today_var  = tk.StringVar(value="0")
        self.stat_coming_var = tk.StringVar(value="0")
        self._stat_card(s, "Total",    self.stat_total_var,  "📋")
        self._stat_card(s, "Today",    self.stat_today_var,  "🗓")
        self._stat_card(s, "Upcoming", self.stat_coming_var, "⏳")

        tk.Frame(s, bg=BORDER, height=1).pack(fill="x", padx=20, pady=18)

        tk.Label(s, text="FILTER BY STATUS", font=("Segoe UI", 8, "bold"), bg=PANEL, fg=SUBTEXT).pack(anchor="w", padx=24, pady=(0, 8))
        for status in ("All", "Scheduled", "Confirmed", "Cancelled"):
            self._filter_btn(s, status)

        tk.Label(s, text=f"© {date.today().year}  Appointment Scheduler",
                 font=("Segoe UI", 8), bg=PANEL, fg=SUBTEXT).pack(side="bottom", pady=16)

    def _stat_card(self, parent, label, var, icon):
        card = tk.Frame(parent, bg=HOVER)
        card.pack(fill="x", padx=20, pady=3, ipady=8)
        tk.Label(card, text=icon, font=("Segoe UI Emoji", 14), bg=HOVER, fg=ACCENT).pack(side="left", padx=(12, 8))
        inner = tk.Frame(card, bg=HOVER)
        inner.pack(side="left")
        tk.Label(inner, text=label,       font=("Segoe UI",  9),         bg=HOVER, fg=SUBTEXT).pack(anchor="w")
        tk.Label(inner, textvariable=var, font=("Segoe UI", 18, "bold"), bg=HOVER, fg=WHITE).pack(anchor="w")

    def _filter_btn(self, parent, status):
        color_map = {"All": TEXT, "Scheduled": ACCENT, "Confirmed": SUCCESS, "Cancelled": ACCENT2}
        btn = tk.Label(parent, text=f"  {status}", font=("Segoe UI", 10),
                       bg=PANEL, fg=color_map.get(status, TEXT), cursor="hand2", anchor="w")
        btn.pack(fill="x", padx=16, pady=2, ipady=6)
        btn.bind("<Button-1>", lambda _e: (self.filter_var.set(status), self._refresh_list()))
        btn.bind("<Enter>",    lambda _e: btn.config(bg=HOVER))
        btn.bind("<Leave>",    lambda _e: btn.config(bg=PANEL))

    # Header
    def _build_header(self, parent):
        header = tk.Frame(parent, bg=BG)
        header.pack(fill="x", padx=30, pady=(24, 0))

        left = tk.Frame(header, bg=BG)
        left.pack(side="left")
        tk.Label(left, text="Appointments",
                 font=("Segoe UI", 22, "bold"), bg=BG, fg=WHITE).pack(anchor="w")
        tk.Label(left, text=datetime.now().strftime("%A, %B %d %Y"),
                 font=("Segoe UI", 10), bg=BG, fg=SUBTEXT).pack(anchor="w")

        tk.Frame(header, bg=BG).pack(side="right", anchor="n")
        ttk.Button(header, text="＋  New Appointment",
                   style="Accent.TButton", command=self._open_form).pack(side="right", anchor="n")

    # Content
    def _build_content(self, parent):
        content = tk.Frame(parent, bg=BG)
        content.pack(fill="both", expand=True, padx=30, pady=16)

        # Search
        search_outer = tk.Frame(content, bg=BORDER)
        search_outer.pack(fill="x", pady=(0, 12))
        tk.Label(search_outer, text="🔍", font=("Segoe UI Emoji", 11),
                 bg=BORDER, fg=SUBTEXT).pack(side="left", padx=(12, 6), pady=8)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_outer, textvariable=self.search_var,
            bg=BORDER, fg=SUBTEXT, insertbackground=TEXT,
            relief="flat", font=("Segoe UI", 11), bd=0)
        self.search_entry.pack(side="left", fill="x", expand=True, pady=10, padx=(0, 12))
        self.search_entry.insert(0, PLACEHOLDER)
        self.search_entry.bind("<FocusIn>",  self._search_focus_in)
        self.search_entry.bind("<FocusOut>", self._search_focus_out)
        self.search_var.trace_add("write", self._on_search_change)

        # Table
        table_frame = tk.Frame(content, bg=PANEL)
        table_frame.pack(fill="both", expand=True)

        cols = ("name", "service", "date", "time", "phone", "status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                                 style="Custom.Treeview", selectmode="browse")
        for col, label, w in [
            ("name",    "Client Name", 185),
            ("service", "Service",     155),
            ("date",    "Date",        115),
            ("time",    "Time",         95),
            ("phone",   "Phone",       135),
            ("status",  "Status",      115),
        ]:
            self.tree.heading(col, text=label,)
            self.tree.column(col, width=w, anchor="w", minwidth=60,)


        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda _e: self._edit_selected())

        # Action bar
        action_bar = tk.Frame(content, bg=BG)
        action_bar.pack(fill="x", pady=(10, 0))
        ttk.Button(action_bar, text="✏  Edit Selected",   style="Ghost.TButton", command=self._edit_selected).pack(side="left", padx=(0, 8))
        ttk.Button(action_bar, text="🗑  Delete Selected", style="Del.TButton",   command=self._delete_selected).pack(side="left")
        self.count_label = tk.Label(action_bar, text="", font=("Segoe UI", 9), bg=BG, fg=SUBTEXT)
        self.count_label.pack(side="right")

    # Search helpers
    def _search_focus_in(self, _event=None):
        if self._search_placeholder:
            self._search_placeholder = False
            self.search_entry.config(fg=TEXT)
            self.search_entry.delete(0, "end")


    def _search_focus_out(self, _event=None):
        if not self.search_var.get().strip():
            self._search_placeholder = True
            self.search_entry.config(fg=SUBTEXT)
            self.search_entry.delete(0, "end")
            self.search_entry.insert(0, PLACEHOLDER)
            self._refresh_list()

    def _on_search_change(self, *_args):
        if not self._search_placeholder:
            self._refresh_list()

    def _get_search_query(self):
        return "" if self._search_placeholder else self.search_var.get().strip().lower()

    # Refresh table
    def _refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        query    = self._get_search_query()
        filt     = self.filter_var.get()
        today_s  = date.today().isoformat()
        shown = upcoming = 0

        for appt in self.appointments:
            status = appt.get("status", "Scheduled")
            if filt != "All" and status != filt:
                continue
            if query and query not in appt.get("name","").lower() \
                     and query not in appt.get("service","").lower():
                continue
            self.tree.insert("", "end", iid=appt["id"],
                             values=(appt.get("name",""), appt.get("service",""),
                                     appt.get("date",""), appt.get("time",""),
                                     appt.get("phone",""), status),
                             tags=(status.lower(),))
            shown += 1
            if appt.get("date","") >= today_s and status != "Cancelled":
                upcoming += 1

        self.tree.tag_configure("scheduled", foreground=TEXT)
        self.tree.tag_configure("confirmed",  foreground=SUCCESS)
        self.tree.tag_configure("cancelled",  foreground=ACCENT2)

        total = len(self.appointments)
        self.stat_total_var.set(str(total))
        self.stat_today_var.set(str(sum(1 for a in self.appointments if a.get("date","") == today_s)))
        self.stat_coming_var.set(str(upcoming))
        self.count_label.config(text=f"Showing {shown} of {total} appointments")

    # Form dialog
    def _open_form(self, appt=None):
        editing = appt is not None
        dlg = tk.Toplevel(self)
        dlg.title("Edit Appointment" if editing else "New Appointment")
        dlg.configure(bg=BG)
        dlg.resizable(False, True)
        dlg.grab_set()
        dlg.transient(self)

        screen_h = self.winfo_screenheight()
        win_h    = min(680, screen_h - 80)
        dlg.geometry(f"500x{win_h}")

        # Outer frame
        outer = tk.Frame(dlg, bg=BG)
        outer.pack(fill="both", expand=True)

        # Canvas
        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0, bd=0)
        vscroll = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)

        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Inner frame
        inner = tk.Frame(canvas, bg=BG)
        inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_inner_configure(_e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(e):
            canvas.itemconfig(inner_id, width=e.width)

        inner.bind("<Configure>", _on_inner_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Mouse-wheel scrolling
        def _on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        dlg.bind("<Destroy>", lambda _e: canvas.unbind_all("<MouseWheel>"))

        # Content inside inner frame
        pad = 28

        tk.Label(inner, text=("Edit Appointment" if editing else "New Appointment"),
                 font=("Segoe UI", 16, "bold"), bg=BG, fg=WHITE).pack(
                 anchor="w", padx=pad, pady=(24, 2))
        tk.Label(inner, text="Fill in the details below.",
                 font=("Segoe UI", 10), bg=BG, fg="white").pack(anchor="w", padx=pad)
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=pad - 4, pady=14)

        form = tk.Frame(inner, bg=BG,)
        form.pack(fill="x", padx=pad, pady=(0, 4))
        form.columnconfigure(0, weight=1)

        def labeled_entry(label_text, row, height=None):
            tk.Label(form, text=label_text, font=("Segoe UI", 9, "bold"),
                     bg=BG, fg="white").grid(row=row, column=0, sticky="w", pady=(10, 2))
            if height:
                # Multi-line Text widget
                t = tk.Text(form, bg=BORDER, fg=TEXT, insertbackground=TEXT,
                            relief="flat", font=("Segoe UI", 11), bd=0,
                            height=height, wrap="word")
                t.grid(row=row + 1, column=0, sticky="ew", pady=(0, 2))
                return t
            else:
                e = tk.Entry(form, bg=BORDER, fg=TEXT, insertbackground=TEXT,
                             relief="flat", font=("Segoe UI", 11), bd=0)
                e.grid(row=row + 1, column=0, sticky="ew", ipady=9)
                return e

        name_e    = labeled_entry("Client Name",            0)
        service_e = labeled_entry("Service",                2)
        phone_e   = labeled_entry("Phone Number",           4)
        date_e    = labeled_entry("Date  (YYYY-MM-DD)",     6)
        time_e    = labeled_entry("Time  (e.g. 10:00 AM)",  8)

        # Status
        tk.Label(form, text="Status", font=("Segoe UI", 9, "bold"),
                 bg=BG, fg=SUBTEXT).grid(row=10, column=0, sticky="w", pady=(10, 2))
        status_var = tk.StringVar(value="Scheduled")
        ttk.Combobox(form, textvariable=status_var,
                     values=["Scheduled", "Confirmed", "Cancelled"],
                     state="readonly", font=("Segoe UI", 11)).grid(
                     row=11, column=0, sticky="ew", ipady=5)

        # Notes
        notes_t = labeled_entry("Notes (optional)", 12, height=4)

        # Separator + buttons
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=pad - 4, pady=14)

        btn_row = tk.Frame(inner, bg=BG)
        btn_row.pack(padx=pad, pady=(0, 24), fill="x")

        def do_save():
            name    = name_e.get().strip()
            service = service_e.get().strip()
            phone   = phone_e.get().strip()
            dt      = date_e.get().strip()
            tm      = time_e.get().strip()
            status  = status_var.get()
            notes   = notes_t.get("1.0", "end-1c").strip()

            if not name:
                messagebox.showwarning("Missing Field", "Client name is required.", parent=dlg)
                name_e.focus_set(); return
            if not service:
                messagebox.showwarning("Missing Field", "Service is required.", parent=dlg)
                service_e.focus_set(); return
            if not dt:
                messagebox.showwarning("Missing Field", "Date is required.", parent=dlg)
                date_e.focus_set(); return
            try:
                datetime.strptime(dt, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Invalid Date",
                    "Date must be in YYYY-MM-DD format.\nExample: 2025-12-31", parent=dlg)
                date_e.focus_set(); return
            if not tm:
                messagebox.showwarning("Missing Field", "Time is required.", parent=dlg)
                time_e.focus_set(); return

            if editing:
                appt.update(name=name, service=service, phone=phone,
                            date=dt, time=tm, status=status, notes=notes)
            else:
                self.appointments.append(dict(
                    id=str(int(datetime.now().timestamp() * 1000)),
                    name=name, service=service, phone=phone,
                    date=dt, time=tm, status=status, notes=notes))

            save_appointments(self.appointments)
            self._refresh_list()
            dlg.destroy()

        ttk.Button(btn_row, text="Cancel",
                   style="Ghost.TButton",  command=dlg.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(btn_row, text="Save Appointment",
                   style="Accent.TButton", command=do_save).pack(side="right")

        # Pre-fill when editing
        if editing:
            name_e.insert(0,      appt.get("name",    ""))
            service_e.insert(0,   appt.get("service", ""))
            phone_e.insert(0,     appt.get("phone",   ""))
            date_e.insert(0,      appt.get("date",    ""))
            time_e.insert(0,      appt.get("time",    ""))
            status_var.set(appt.get("status", "Scheduled"))
            notes_t.insert("1.0", appt.get("notes",   ""))

        dlg.bind("<Return>", lambda _e: do_save())
        dlg.bind("<Escape>", lambda _e: dlg.destroy())
        name_e.focus_set()

    # Edit / Delete
    def _edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Please select an appointment to edit.")
            return
        appt = next((a for a in self.appointments if a["id"] == sel[0]), None)
        if appt:
            self._open_form(appt)
        else:
            messagebox.showerror("Error", "Could not find the selected appointment.")

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Please select an appointment to delete.")
            return
        appt = next((a for a in self.appointments if a["id"] == sel[0]), None)
        if not appt:
            messagebox.showerror("Error", "Could not find the selected appointment.")
            return
        if messagebox.askyesno("Confirm Delete",
                f"Delete appointment for \"{appt.get('name','this client')}\" "
                f"on {appt.get('date','?')}?\n\nThis cannot be undone."):
            self.appointments = [a for a in self.appointments if a["id"] != sel[0]]
            save_appointments(self.appointments)
            self._refresh_list()


if __name__ == "__main__":
    app = AppointmentApp()
    app.mainloop()
