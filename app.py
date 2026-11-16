"""Real-Time Memory Allocation Tracker - Tkinter desktop application."""
import random
import tkinter as tk
from tkinter import ttk, messagebox

from memory_engine import PagingManager, SegmentationManager


class MemoryTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Memory Allocation Tracker")
        self.root.geometry("1120x760")
        self.root.minsize(940, 650)
        self.paging = PagingManager(frame_count=24, page_size=4)
        self.segmentation = SegmentationManager(total_size=100)
        self.auto_running = False
        self.auto_job = None
        self._style()
        self._build_ui()
        self.refresh_all()

    def _style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground="#183153")
        style.configure("Sub.TLabel", font=("Segoe UI", 10), foreground="#53657d")
        style.configure("Metric.TLabel", font=("Segoe UI", 16, "bold"), foreground="#183153")
        style.configure("MetricName.TLabel", font=("Segoe UI", 9), foreground="#53657d")
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=25, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def _build_ui(self):
        header = ttk.Frame(self.root, padding=(18, 14))
        header.pack(fill="x")
        ttk.Label(header, text="Real-Time Memory Allocation Tracker", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Operating Systems • Educational simulation of paging and segmentation",
            style="Sub.TLabel"
        ).pack(anchor="w", pady=(3, 0))

        metric_row = ttk.Frame(self.root, padding=(18, 0, 18, 12))
        metric_row.pack(fill="x")
        self.metric_vars = {}
        for key, label in [
            ("paging", "PAGING UTILIZATION"),
            ("segments", "SEGMENTATION UTILIZATION"),
            ("free_frames", "FREE FRAMES"),
            ("free_memory", "FREE SEGMENT MEMORY"),
        ]:
            card = ttk.LabelFrame(metric_row, text=label, padding=10)
            card.pack(side="left", fill="x", expand=True, padx=(0, 8))
            var = tk.StringVar(value="0")
            self.metric_vars[key] = var
            ttk.Label(card, textvariable=var, style="Metric.TLabel").pack(anchor="w")

        toolbar = ttk.Frame(self.root, padding=(18, 0, 18, 10))
        toolbar.pack(fill="x")
        self.auto_button = ttk.Button(toolbar, text="Start Auto Demo", command=self.toggle_auto)
        self.auto_button.pack(side="left")
        ttk.Button(toolbar, text="Reset Simulation", command=self.reset_all).pack(side="left", padx=8)
        ttk.Label(toolbar, text="Auto demo creates and releases sample processes.", style="Sub.TLabel").pack(side="left", padx=10)

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=18, pady=(0, 12))
        self.paging_tab = ttk.Frame(self.tabs, padding=12)
        self.seg_tab = ttk.Frame(self.tabs, padding=12)
        self.log_tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(self.paging_tab, text="Paging")
        self.tabs.add(self.seg_tab, text="Segmentation")
        self.tabs.add(self.log_tab, text="Event Log")
        self._build_paging_tab()
        self._build_seg_tab()
        self._build_log_tab()

        footer = ttk.Label(
            self.root,
            text="Note: This application simulates memory allocation; it does not read or change actual system RAM.",
            style="Sub.TLabel", padding=(18, 0, 18, 10)
        )
        footer.pack(anchor="w")

    def _build_controls(self, parent, allocate_cmd, free_cmd):
        controls = ttk.LabelFrame(parent, text="Process controls", padding=10)
        controls.pack(fill="x", pady=(0, 10))
        ttk.Label(controls, text="Process ID").grid(row=0, column=0, sticky="w")
        pid = ttk.Entry(controls, width=16)
        pid.grid(row=1, column=0, padx=(0, 10), pady=4, sticky="w")
        ttk.Label(controls, text="Memory size (units)").grid(row=0, column=1, sticky="w")
        size = ttk.Entry(controls, width=16)
        size.grid(row=1, column=1, padx=(0, 10), pady=4, sticky="w")
        ttk.Button(controls, text="Allocate", style="Accent.TButton",
                   command=lambda: allocate_cmd(pid.get(), size.get())).grid(row=1, column=2, padx=4)
        ttk.Button(controls, text="Deallocate by ID",
                   command=lambda: free_cmd(pid.get())).grid(row=1, column=3, padx=4)
        return pid, size

    def _build_paging_tab(self):
        self._build_controls(self.paging_tab, self.allocate_page, self.free_page)
        body = ttk.Frame(self.paging_tab)
        body.pack(fill="both", expand=True)
        left = ttk.LabelFrame(body, text="Physical memory frames (24 frames; 4 units/page)", padding=8)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.page_canvas = tk.Canvas(left, background="white", height=330, highlightthickness=0)
        self.page_canvas.pack(fill="both", expand=True)
        right = ttk.LabelFrame(body, text="Page table", padding=8)
        right.pack(side="left", fill="both", expand=True)
        self.page_tree = ttk.Treeview(right, columns=("pid", "page", "frame"), show="headings", height=13)
        for col, label, width in [("pid", "Process", 100), ("page", "Page no.", 90), ("frame", "Frame no.", 90)]:
            self.page_tree.heading(col, text=label)
            self.page_tree.column(col, width=width, anchor="center")
        self.page_tree.pack(fill="both", expand=True)
        ttk.Label(right, text="Paging uses fixed-size frames. A process's pages can occupy non-adjacent frames.",
                  wraplength=300, style="Sub.TLabel").pack(anchor="w", pady=(8, 0))

    def _build_seg_tab(self):
        self._build_controls(self.seg_tab, self.allocate_segment, self.free_segment)
        body = ttk.Frame(self.seg_tab)
        body.pack(fill="both", expand=True)
        left = ttk.LabelFrame(body, text="Contiguous memory map (100 units)", padding=8)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.seg_canvas = tk.Canvas(left, background="white", height=330, highlightthickness=0)
        self.seg_canvas.pack(fill="both", expand=True)
        right = ttk.LabelFrame(body, text="Allocation details", padding=10)
        right.pack(side="left", fill="both", expand=True)
        self.seg_tree = ttk.Treeview(right, columns=("pid", "start", "size"), show="headings", height=13)
        for col, label in [("pid", "Process"), ("start", "Start"), ("size", "Size")]:
            self.seg_tree.heading(col, text=label)
            self.seg_tree.column(col, width=95, anchor="center")
        self.seg_tree.pack(fill="both", expand=True)
        self.seg_stats = tk.StringVar()
        ttk.Label(right, textvariable=self.seg_stats, style="Sub.TLabel", wraplength=300).pack(anchor="w", pady=10)
        ttk.Label(right, text="Segmentation allocates variable-size contiguous blocks using first fit.",
                  wraplength=300, style="Sub.TLabel").pack(anchor="w")

    def _build_log_tab(self):
        ttk.Label(self.log_tab, text="Latest simulation events", style="Metric.TLabel").pack(anchor="w", pady=(0, 8))
        self.log_text = tk.Text(self.log_tab, height=20, wrap="word", font=("Consolas", 9),
                                background="#f7f9fc", relief="flat", padx=10, pady=10)
        self.log_text.pack(fill="both", expand=True)
        self.log_text.configure(state="disabled")

    def _parse_size(self, raw):
        try:
            value = int(raw)
            if value <= 0:
                raise ValueError
            return value
        except (TypeError, ValueError):
            messagebox.showerror("Invalid size", "Memory size must be a positive whole number.")
            return None

    def allocate_page(self, pid, raw_size):
        size = self._parse_size(raw_size)
        if size is None:
            return
        ok, message = self.paging.allocate(pid, size)
        if not ok:
            messagebox.showwarning("Paging allocation", message)
        self.refresh_all()

    def free_page(self, pid):
        ok, message = self.paging.deallocate(pid)
        if not ok:
            messagebox.showwarning("Paging deallocation", message)
        self.refresh_all()

    def allocate_segment(self, pid, raw_size):
        size = self._parse_size(raw_size)
        if size is None:
            return
        ok, message = self.segmentation.allocate(pid, size)
        if not ok:
            messagebox.showwarning("Segmentation allocation", message)
        self.refresh_all()

    def free_segment(self, pid):
        ok, message = self.segmentation.deallocate(pid)
        if not ok:
            messagebox.showwarning("Segmentation deallocation", message)
        self.refresh_all()

    def _draw_paging(self):
        canvas = self.page_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 420)
        cols, gap, top = 4, 8, 25
        cell_w = (width - 2 * gap - (cols - 1) * gap) / cols
        cell_h = 48
        for i, page in enumerate(self.paging.frames):
            row, col = divmod(i, cols)
            x = gap + col * (cell_w + gap)
            y = top + row * (cell_h + 8)
            color = "#e7edf5" if page is None else "#75b9a6"
            canvas.create_rectangle(x, y, x + cell_w, y + cell_h, fill=color, outline="#9aaabd")
            label = f"Frame {i}\nFREE" if page is None else f"Frame {i}\n{page.process_id} / P{page.page_number}"
            canvas.create_text(x + cell_w / 2, y + cell_h / 2, text=label, font=("Segoe UI", 8), justify="center")

    def _draw_segmentation(self):
        canvas = self.seg_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 420)
        x0, x1, y0, y1 = 24, width - 24, 55, 125
        scale = (x1 - x0) / self.segmentation.total_size
        cursor = 0
        blocks = sorted(self.segmentation.segments, key=lambda b: b["start"])
        for block in blocks:
            if block["start"] > cursor:
                self._draw_hole(canvas, x0 + cursor * scale, x0 + block["start"] * scale, y0, y1)
            xa = x0 + block["start"] * scale
            xb = x0 + (block["start"] + block["size"]) * scale
            canvas.create_rectangle(xa, y0, xb, y1, fill="#75b9a6", outline="#496b66")
            canvas.create_text((xa + xb) / 2, (y0 + y1) / 2,
                               text=f"{block['pid']}\n{block['size']}", font=("Segoe UI", 8))
            cursor = block["start"] + block["size"]
        if cursor < self.segmentation.total_size:
            self._draw_hole(canvas, x0 + cursor * scale, x1, y0, y1)
        canvas.create_text(x0, y0 - 20, text="Address 0", anchor="w", font=("Segoe UI", 8))
        canvas.create_text(x1, y0 - 20, text="Address 100", anchor="e", font=("Segoe UI", 8))
        canvas.create_text(width / 2, y1 + 35, text="Green = allocated block     Grey = free hole",
                           font=("Segoe UI", 9), fill="#53657d")

    def _draw_hole(self, canvas, xa, xb, y0, y1):
        canvas.create_rectangle(xa, y0, xb, y1, fill="#e7edf5", outline="#9aaabd")
        if xb - xa > 35:
            canvas.create_text((xa + xb) / 2, (y0 + y1) / 2, text=f"FREE\n{(xb-xa):.0f}",
                               font=("Segoe UI", 8))

    def refresh_all(self):
        self.metric_vars["paging"].set(f"{self.paging.utilization:.1f}%")
        self.metric_vars["segments"].set(f"{self.segmentation.utilization:.1f}%")
        self.metric_vars["free_frames"].set(str(self.paging.free_frames))
        self.metric_vars["free_memory"].set(f"{self.segmentation.free_size} units")
        self._draw_paging()
        self._draw_segmentation()
        for tree in (self.page_tree, self.seg_tree):
            for item in tree.get_children():
                tree.delete(item)
        for row in self.paging.page_table_rows():
            self.page_tree.insert("", "end", values=row)
        for block in sorted(self.segmentation.segments, key=lambda b: b["start"]):
            self.seg_tree.insert("", "end", values=(block["pid"], block["start"], block["size"]))
        holes = self.segmentation.holes()
        self.seg_stats.set(
            f"Free space: {self.segmentation.free_size} units\n"
            f"Number of free holes: {len(holes)}\n"
            f"External fragmentation indicator: {self.segmentation.external_fragmentation} units"
        )
        self._refresh_log()

    def _refresh_log(self):
        lines = []
        for event in (self.paging.events + self.segmentation.events)[-100:]:
            lines.append(event)
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("end", "\n".join(lines) if lines else "No events yet. Allocate a process to begin.")
        self.log_text.configure(state="disabled")

    def toggle_auto(self):
        self.auto_running = not self.auto_running
        self.auto_button.configure(text="Stop Auto Demo" if self.auto_running else "Start Auto Demo")
        if self.auto_running:
            self._auto_step()

    def _auto_step(self):
        if not self.auto_running:
            return
        # Randomly allocate or release small demo processes in both models.
        for manager, prefix, max_size in [(self.paging, "AUTO-P", 12), (self.segmentation, "AUTO-S", 22)]:
            active = list(manager.process_pages if isinstance(manager, PagingManager) else manager.processes)
            if active and random.random() < 0.35:
                manager.deallocate(random.choice(active))
            else:
                pid = f"{prefix}{random.randint(1, 99)}"
                size = random.randint(1, max_size)
                manager.allocate(pid, size)
        self.refresh_all()
        self.auto_job = self.root.after(1500, self._auto_step)

    def reset_all(self):
        if self.auto_running:
            self.auto_running = False
            if self.auto_job:
                self.root.after_cancel(self.auto_job)
            self.auto_button.configure(text="Start Auto Demo")
        self.paging = PagingManager(frame_count=24, page_size=4)
        self.segmentation = SegmentationManager(total_size=100)
        self.refresh_all()

    def on_close(self):
        self.auto_running = False
        if self.auto_job:
            try:
                self.root.after_cancel(self.auto_job)
            except tk.TclError:
                pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryTrackerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
