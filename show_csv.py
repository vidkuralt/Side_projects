import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from tkinterdnd2 import DND_FILES, TkinterDnD

class CSVViewer(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("CSV Drag-and-Drop Viewer")
        self.geometry("1000x700")
        self.configure(bg="#2e2e2e")  # Dark background

        # Instructions
        label = tk.Label(
            self, 
            text="Drag and drop CSV files onto this window", 
            font=("Arial", 14),
            bg="#2e2e2e",
            fg="#ffffff"
        )
        label.pack(pady=10)

        # Clear button
        clear_btn = tk.Button(self, text="Clear All", command=self.clear_all, bg="#555555", fg="#ffffff")
        clear_btn.pack(pady=5)

        # Frame for tables with scrollable canvas
        self.canvas = tk.Canvas(self, bg="#2e2e2e")
        self.scroll_frame = tk.Frame(self.canvas, bg="#2e2e2e")
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0,0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Store Treeviews
        self.tables = []

        # Enable drag-and-drop
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop)

        # Dark theme for Treeview
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Dark.Treeview",
                        background="#3e3e3e",
                        foreground="#ffffff",
                        fieldbackground="#3e3e3e",
                        rowheight=25)
        style.map('Dark.Treeview', background=[('selected', '#565656')], foreground=[('selected', '#ffffff')])

        # Mouse wheel scrolling
        self.canvas.bind("<Enter>", lambda e: self.bind_all("<MouseWheel>", self._on_mousewheel_canvas))
        self.canvas.bind("<Leave>", lambda e: self.unbind_all("<MouseWheel>"))

    def drop(self, event):
        files = self.split_filenames(event.data)
        for file_path in files:
            if file_path.lower().endswith('.csv'):
                self.load_csv(file_path)
            else:
                messagebox.showerror("Error", f"{file_path} is not a valid CSV file.")

    def split_filenames(self, data):
        return [f.strip('{}') for f in self.tk.splitlist(data)]

    def load_csv(self, file_path):
        try:
            df = pd.read_csv(file_path)
            self.show_table(df, file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV:\n{e}")

    def show_table(self, df, title):
        frame = tk.Frame(self.scroll_frame, bg="#3e3e3e", bd=2, relief="groove")
        frame.pack(fill="x", pady=10, padx=10)

        label = tk.Label(frame, text=title, font=("Arial", 12, "bold"), bg="#3e3e3e", fg="#ffffff")
        label.pack(pady=5)

        tree = ttk.Treeview(frame, show="headings", style="Dark.Treeview")
        tree.pack(fill="both", expand=True, side="left")

        # Scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        hsb.pack(side="bottom", fill="x")
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Enable mouse wheel for Treeview
        tree.bind("<Enter>", lambda e, t=tree: self.bind_all("<MouseWheel>", lambda event: self._on_mousewheel_tree(event, t)))
        tree.bind("<Leave>", lambda e: self.bind_all("<MouseWheel>", self._on_mousewheel_canvas))

        # Set columns and sortable headers
        tree["columns"] = list(df.columns)
        for col in df.columns:
            tree.heading(col, text=col, command=lambda _col=col, _tree=tree: self.sort_column(_tree, _col, False))
            tree.column(col, width=120, anchor="center")

        # Insert rows
        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))

        self.tables.append(frame)

    def sort_column(self, tree, col, reverse):
        try:
            l = [(tree.set(k, col), k) for k in tree.get_children('')]
            try:
                l.sort(key=lambda t: float(t[0]) if t[0] != '' else float('-inf'), reverse=reverse)
            except:
                l.sort(key=lambda t: t[0], reverse=reverse)
            for index, (_, k) in enumerate(l):
                tree.move(k, '', index)
            tree.heading(col, command=lambda: self.sort_column(tree, col, not reverse))
        except Exception as e:
            messagebox.showerror("Error", f"Cannot sort column {col}:\n{e}")

    def clear_all(self):
        for table in self.tables:
            table.destroy()
        self.tables.clear()

    # Mouse wheel scrolling functions
    def _on_mousewheel_canvas(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_mousewheel_tree(self, event, tree):
        tree.yview_scroll(int(-1*(event.delta/120)), "units")


if __name__ == "__main__":
    app = CSVViewer()
    app.mainloop()
