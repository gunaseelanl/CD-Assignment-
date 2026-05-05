"""
MD INDUSTRIES
Developer: M.DHANESVARAN
Batman-themed local IDE for the portable Python subset compiler.
"""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser

from .compiler import CompileError, ExecutionError, compile_source, execute_source


ROOT = Path(__file__).resolve().parent.parent
DEVELOPER_NAME = "M.DHANESVARAN"
COMPANY_NAME = "MD INDUSTRIES"
CONTACT_EMAIL = "dhanesvarankumaran2006@gmail.com"
GITHUB_URL = "https://github.com/DHANESVARAN"
WEBSITE_URL = "https://dhanesvarankumaran.wixsite.com/dhanesvaran"
LINKEDIN_URL = "https://www.linkedin.com/in/dhanesvaran-m-774ab426b/"
DEFAULT_SOURCE = """x = 10
y = 20
x = x + y * 2
print(x)
print(x - 5)

total = 0
i = 0
while i < 3:
    total += i
    i += 1

if total > 2:
    print(total)
else:
    print(0)
"""


class BatmanIDE:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("PyPortCC IDE | Gotham Mode")
        self.root.geometry("1280x820")
        self.root.minsize(1000, 680)
        self.root.configure(bg="#070707")

        self.current_file: Path | None = None
        self.output_file: Path | None = None

        self._configure_style()
        self._build_layout()
        self.source_editor.insert("1.0", DEFAULT_SOURCE)
        self.status_var.set("Gotham console ready. Load code or compile the sample program.")

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Batman.TFrame", background="#070707")
        style.configure("Panel.TFrame", background="#111111")
        style.configure("Hero.TLabel", background="#070707", foreground="#f5c400", font=("Segoe UI", 22, "bold"))
        style.configure("Sub.TLabel", background="#070707", foreground="#f8e58c", font=("Segoe UI", 10))
        style.configure("Brand.TLabel", background="#070707", foreground="#f5c400", font=("Segoe UI", 10, "bold"))
        style.configure("PanelTitle.TLabel", background="#111111", foreground="#f5c400", font=("Consolas", 12, "bold"))
        style.configure("Footer.TFrame", background="#0d0d0d")
        style.configure("Footer.TLabel", background="#0d0d0d", foreground="#f8e58c", font=("Segoe UI", 9))
        style.configure("Link.TLabel", background="#0d0d0d", foreground="#f5c400", font=("Segoe UI", 9, "underline"))
        style.configure("Status.TLabel", background="#0d0d0d", foreground="#f5c400", font=("Consolas", 10))
        style.configure(
            "Batman.TButton",
            background="#f5c400",
            foreground="#070707",
            borderwidth=0,
            focusthickness=0,
            padding=(14, 8),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Batman.TButton",
            background=[("active", "#ffd84d"), ("pressed", "#d9ab00")],
            foreground=[("disabled", "#4a4a4a")],
        )

    def _build_layout(self) -> None:
        shell = ttk.Frame(self.root, style="Batman.TFrame", padding=20)
        shell.pack(fill="both", expand=True)

        header = ttk.Frame(shell, style="Batman.TFrame")
        header.pack(fill="x")

        ttk.Label(header, text="BATCAVE COMPILER IDE", style="Hero.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Dark-themed local IDE for the restricted Python compiler. Source on the left, generated C on the right.",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(4, 14))
        ttk.Label(
            header,
            text=f"Developer: {DEVELOPER_NAME}  |  Company: {COMPANY_NAME}",
            style="Brand.TLabel",
        ).pack(anchor="w", pady=(0, 14))

        actions = ttk.Frame(shell, style="Batman.TFrame")
        actions.pack(fill="x", pady=(0, 14))

        for label, handler in [
            ("Open", self.open_source),
            ("Save Source", self.save_source),
            ("Compile to C", self.compile_current_source),
            ("Compile + Run", self.compile_and_run_source),
            ("Save C Output", self.save_output),
            ("Load Sample", self.load_sample),
            ("Clear Log", self.clear_log),
        ]:
            ttk.Button(actions, text=label, command=handler, style="Batman.TButton").pack(side="left", padx=(0, 10))

        panes = ttk.Frame(shell, style="Batman.TFrame")
        panes.pack(fill="both", expand=True)
        panes.columnconfigure(0, weight=1)
        panes.columnconfigure(1, weight=1)
        panes.rowconfigure(0, weight=3)
        panes.rowconfigure(1, weight=1)

        source_panel = ttk.Frame(panes, style="Panel.TFrame", padding=14)
        source_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        ttk.Label(source_panel, text="Python Source", style="PanelTitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.source_editor = self._make_textbox(source_panel)
        self.source_editor.pack(fill="both", expand=True)

        right_panel = ttk.Frame(panes, style="Batman.TFrame")
        right_panel.grid(row=0, column=1, sticky="nsew", pady=(0, 10))
        right_panel.rowconfigure(0, weight=2)
        right_panel.rowconfigure(1, weight=1)
        right_panel.columnconfigure(0, weight=1)

        output_panel = ttk.Frame(right_panel, style="Panel.TFrame", padding=14)
        output_panel.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        ttk.Label(output_panel, text="Generated C", style="PanelTitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.output_editor = self._make_textbox(output_panel, readonly=True)
        self.output_editor.pack(fill="both", expand=True)

        runtime_panel = ttk.Frame(right_panel, style="Panel.TFrame", padding=14)
        runtime_panel.grid(row=1, column=0, sticky="nsew")
        ttk.Label(runtime_panel, text="Program Output", style="PanelTitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.runtime_view = self._make_textbox(runtime_panel, height=8, readonly=True)
        self.runtime_view.pack(fill="both", expand=True)

        log_panel = ttk.Frame(panes, style="Panel.TFrame", padding=14)
        log_panel.grid(row=1, column=0, columnspan=2, sticky="nsew")
        ttk.Label(log_panel, text="Compiler Log", style="PanelTitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.log_view = self._make_textbox(log_panel, height=10, readonly=True)
        self.log_view.pack(fill="both", expand=True)

        footer = ttk.Frame(shell, style="Footer.TFrame", padding=(12, 10))
        footer.pack(fill="x", pady=(14, 0))
        ttk.Label(
            footer,
            text=f"{DEVELOPER_NAME} | {COMPANY_NAME} | {CONTACT_EMAIL}",
            style="Footer.TLabel",
        ).pack(anchor="w")

        links = ttk.Frame(footer, style="Footer.TFrame")
        links.pack(anchor="w", pady=(4, 0))
        self._create_link_label(links, "GitHub", GITHUB_URL).pack(side="left", padx=(0, 16))
        self._create_link_label(links, "Website", WEBSITE_URL).pack(side="left", padx=(0, 16))
        self._create_link_label(links, "LinkedIn", LINKEDIN_URL).pack(side="left", padx=(0, 16))
        self._create_link_label(links, "Email", f"mailto:{CONTACT_EMAIL}").pack(side="left")

        self.status_var = tk.StringVar()
        status = ttk.Label(shell, textvariable=self.status_var, style="Status.TLabel", padding=(12, 10))
        status.pack(fill="x", pady=(8, 0))

    def _create_link_label(self, parent: ttk.Frame, text: str, url: str) -> ttk.Label:
        label = ttk.Label(parent, text=text, style="Link.TLabel", cursor="hand2")
        label.bind("<Button-1>", lambda _event, target=url: webbrowser.open_new_tab(target))
        return label

    def _make_textbox(self, parent: ttk.Frame, height: int | None = None, readonly: bool = False) -> tk.Text:
        frame = tk.Frame(parent, bg="#111111", highlightbackground="#f5c400", highlightcolor="#f5c400", highlightthickness=1)
        frame.pack_propagate(False)
        text = tk.Text(
            frame,
            wrap="none",
            bg="#0b0b0b",
            fg="#f3e7a2",
            insertbackground="#f5c400",
            selectbackground="#2c2c2c",
            selectforeground="#f5c400",
            relief="flat",
            font=("Consolas", 11),
            undo=True,
            padx=12,
            pady=12,
            height=height or 20,
        )
        y_scroll = tk.Scrollbar(frame, orient="vertical", command=text.yview, bg="#111111", troughcolor="#0b0b0b", activebackground="#f5c400")
        x_scroll = tk.Scrollbar(frame, orient="horizontal", command=text.xview, bg="#111111", troughcolor="#0b0b0b", activebackground="#f5c400")
        text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        text.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.pack(fill="both", expand=True)
        if readonly:
            text.configure(state="disabled")
        return text

    def _set_text(self, widget: tk.Text, value: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", value)
        widget.configure(state="disabled")

    def _append_log(self, message: str) -> None:
        self.log_view.configure(state="normal")
        self.log_view.insert("end", message.rstrip() + "\n")
        self.log_view.see("end")
        self.log_view.configure(state="disabled")

    def open_source(self) -> None:
        selected = filedialog.askopenfilename(
            title="Open Python Source",
            initialdir=str(ROOT / "test"),
            filetypes=[("Python Source", "*.py"), ("All Files", "*.*")],
        )
        if not selected:
            return
        path = Path(selected)
        self.source_editor.delete("1.0", "end")
        self.source_editor.insert("1.0", path.read_text(encoding="utf-8"))
        self.current_file = path
        self.status_var.set(f"Loaded source: {path.name}")
        self._append_log(f"Loaded {path}")

    def save_source(self) -> None:
        target = self.current_file
        if target is None:
            selected = filedialog.asksaveasfilename(
                title="Save Python Source",
                initialdir=str(ROOT / "test"),
                defaultextension=".py",
                filetypes=[("Python Source", "*.py"), ("All Files", "*.*")],
            )
            if not selected:
                return
            target = Path(selected)
            self.current_file = target
        target.write_text(self.source_editor.get("1.0", "end-1c"), encoding="utf-8", newline="\n")
        self.status_var.set(f"Saved source: {target.name}")
        self._append_log(f"Saved source to {target}")

    def compile_current_source(self) -> bool:
        source = self.source_editor.get("1.0", "end-1c")
        try:
            generated = compile_source(source, filename=str(self.current_file or "<editor>"))
        except CompileError as exc:
            self.status_var.set("Compilation failed.")
            self._append_log(f"Compilation failed: {exc}")
            messagebox.showerror("Compilation Failed", str(exc), parent=self.root)
            return False

        self.output_file = ROOT / "output" / ((self.current_file.stem if self.current_file else "editor_output") + ".c")
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.write_text(generated, encoding="utf-8", newline="\n")
        self._set_text(self.output_editor, generated)
        self.status_var.set(f"Compilation successful. Output: {self.output_file.name}")
        self._append_log(f"Compiled successfully to {self.output_file}")
        return True

    def compile_and_run_source(self) -> None:
        source = self.source_editor.get("1.0", "end-1c")
        if not self.compile_current_source():
            self._set_text(self.runtime_view, "Compilation failed. Fix errors and run again.\n")
            return
        try:
            runtime_output = execute_source(source, filename=str(self.current_file or "<editor>"))
        except (CompileError, ExecutionError) as exc:
            self.status_var.set("Run failed.")
            self._append_log(f"Run failed: {exc}")
            self._set_text(self.runtime_view, f"Error: {exc}\n")
            messagebox.showerror("Run Failed", str(exc), parent=self.root)
            return

        output_text = runtime_output if runtime_output else "(no output)\n"
        self._set_text(self.runtime_view, output_text)
        self.status_var.set("Compilation and run successful.")
        self._append_log("Program executed successfully.")

    def save_output(self) -> None:
        content = self.output_editor.get("1.0", "end-1c")
        if not content.strip():
            messagebox.showinfo("No Output", "Compile the source before saving C output.", parent=self.root)
            return
        selected = filedialog.asksaveasfilename(
            title="Save Generated C",
            initialdir=str(ROOT / "output"),
            defaultextension=".c",
            filetypes=[("C Source", "*.c"), ("All Files", "*.*")],
        )
        if not selected:
            return
        target = Path(selected)
        target.write_text(content, encoding="utf-8", newline="\n")
        self.output_file = target
        self.status_var.set(f"Saved C output: {target.name}")
        self._append_log(f"Saved generated C to {target}")

    def load_sample(self) -> None:
        sample_path = ROOT / "test" / "sample.py"
        self.source_editor.delete("1.0", "end")
        self.source_editor.insert("1.0", sample_path.read_text(encoding="utf-8"))
        self.current_file = sample_path
        self.status_var.set("Sample program loaded.")
        self._append_log(f"Loaded sample program from {sample_path}")

    def clear_log(self) -> None:
        self._set_text(self.log_view, "")
        self.status_var.set("Log cleared.")

    def run(self) -> None:
        self.root.mainloop()


def launch_ide() -> None:
    BatmanIDE().run()
