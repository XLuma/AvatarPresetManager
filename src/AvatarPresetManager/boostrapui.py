from __future__ import annotations
from typing import Dict, List
import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from AvatarPresetManager.avatarManager import AvatarManager

# from AvatarPresetManager.avatarManager import AvatarManager  # <-- your import


class CollapsibleSection(tb.Frame):
    """Simple collapsible container: header row with a toggle, content frame below."""
    def __init__(self, master, title: str, *, opened: bool = False, padding=(8,8), **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)

        self._open = opened

        # header
        self.header = tb.Frame(self)
        self.header.grid(row=0, column=0, sticky=EW)

        self.chev = tb.Label(self.header, text="▸", font=("", 12))
        self.chev.pack(side=LEFT, padx=(4, 6))
        self.title = tb.Label(self.header, text=title, font=tb.font.Font(size=11, weight="bold"))
        self.title.pack(side=LEFT)
        self.title.bind("<Button-1>", lambda e:self.toggle())
        self.title.configure(cursor="hand2")

        # content
        self.body = tb.Frame(self, padding=padding)
        if opened:
            self._open_body()
        else:
            self._close_body()

    def toggle(self):
        if self._open:
            self._close_body()
        else:
            self._open_body()

    def _open_body(self):
        self.body.grid(row=1, column=0, sticky=EW)
        self.chev.configure(text="▾")
        self._open = True

    def _close_body(self):
        self.body.grid_forget()
        self.chev.configure(text="▸")
        self._open = False


class PresetManagerUI:
    def __init__(self, manager: AvatarManager):
        self.manager = manager

        self.root = tb.Window(themename="darkly")
        self.root.title("Avatar Preset Manager")
        self.root.geometry("900x600")

        # state
        self._avatar_sections: Dict[str, CollapsibleSection] = {}

        # layout
        self._build_shell()
        self._refresh_all()

    # ---------------- Shell ----------------
    def _build_shell(self):
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)

        # Left sidebar (hidden by default)
        self.sidebar = tb.Frame(self.root, padding=10)
        self._sidebar_visible = False

        # Top bar
        top = tb.Frame(self.root, padding=8)
        top.grid(row=0, column=1, sticky=EW)
        top.columnconfigure(3, weight=1)

        tb.Button(top, text="☰", width=3, bootstyle=SECONDARY, command=self._toggle_sidebar)\
            .grid(row=0, column=0, padx=(0,8))

        tb.Button(top, text="Create Preset", bootstyle=PRIMARY, command=self._create_preset)\
            .grid(row=0, column=1, padx=4)
        tb.Button(top, text="Refresh", bootstyle=INFO, command=self._refresh_all)\
            .grid(row=0, column=2, padx=4)

        # Main scrolled area
        self.scroll = ScrolledFrame(self.root, autohide=True, padding=(12,8))
        self.scroll.grid(row=1, column=1, sticky=NSEW)
        self.root.rowconfigure(1, weight=1)

        # Sidebar contents
        tb.Label(self.sidebar, text="Settings", font=tb.font.Font(size=12, weight="bold")).pack(anchor="w")
        tb.Separator(self.sidebar).pack(fill=X, pady=6)
        tb.Checkbutton(self.sidebar, text="Dark Mode (follows theme)").pack(anchor="w", pady=2)
        tb.Button(self.sidebar, text="About", bootstyle=SECONDARY).pack(anchor="w", pady=8)

    def _toggle_sidebar(self):
        if self._sidebar_visible:
            self.sidebar.grid_forget()
            self._sidebar_visible = False
        else:
            self.sidebar.grid(row=0, column=0, rowspan=2, sticky=NS)
            self._sidebar_visible = True

    # ---------------- Data ----------------
    def _refresh_all(self):
        try:
            self.manager.parse_existing_presets()
        except Exception as exc:
            messagebox.showerror("Preset Manager", f"Failed to load presets:\n{exc}")
            return

        # Clear current avatar sections
        for child in self.scroll.winfo_children():
            child.destroy()
        self._avatar_sections.clear()

        # Build sections in sorted order
        for avatar_id in sorted(self.manager.presets.keys()):
            presets = sorted(self.manager.presets[avatar_id].keys())
            self._build_avatar_section(avatar_id, presets)

        # stretch at bottom
        tb.Frame(self.scroll).pack(fill=BOTH, expand=True)

    def _build_avatar_section(self, avatar_id: str, presets: List[str]):
        sec = CollapsibleSection(self.scroll, title=avatar_id, opened=False)
        sec.pack(fill=X, pady=(0, 10))
        self._avatar_sections[avatar_id] = sec

        # right column: presets list
        right = tb.Frame(sec.body)
        right.grid(row=0, column=0, sticky=EW)
        right.columnconfigure(0, weight=1)

        if presets:
            for name in presets:
                row = tb.Frame(right)
                row.grid_columnconfigure(1, weight=1)
                row.pack(fill=X, pady=2)

                bullet = tb.Label(row, text="•")
                bullet.grid(row=0, column=0, sticky=W, padx=(0,6))
                tb.Label(row, text=name).grid(row=0, column=1, sticky=W)
                tb.Button(row, text="Apply", bootstyle=SECONDARY,
                          command=lambda n=name: self._apply_preset(n)).grid(row=0, column=2, padx=4)
                tb.Button(row, text="Delete", bootstyle=DANGER,
                          command=lambda n=name: self._delete_preset(n)).grid(row=0, column=3, padx=4)
        else:
            tb.Label(right, text="No presets found.", bootstyle=SECONDARY).pack(anchor="w")

        # separator
        tb.Separator(sec.body).grid(row=1, column=0, columnspan=2, sticky=EW, pady=(10,0))

    # ---------------- Actions ----------------
    def _apply_avatar_default(self, avatar_id: str):
        """Example: you might define what 'Apply' on the avatar block means in your app.
        Here we no-op or you could choose a convention (e.g., 'Default')."""
        # Optionally pick a special preset if present:
        presets = self.manager.presets.get(avatar_id, {})
        name = "Default" if "Default" in presets else next(iter(presets), None)
        if not name:
            messagebox.showinfo("Apply Preset", f"No presets to apply for avatar {avatar_id}.")
            return
        self._apply_preset(name)

    def _apply_preset(self, preset_name: str):
        try:
            self.manager.apply_avatar_state(preset_name)
        except Exception as exc:
            messagebox.showerror("Apply Preset", f"Failed to apply '{preset_name}':\n{exc}")
            return
        messagebox.showinfo("Apply Preset", f"Applied preset '{preset_name}'.")

    def _create_preset(self):
        top = tk.Toplevel(self.root)
        top.title("Create Preset"); top.transient(self.root); top.grab_set()
        v = tk.StringVar()
        frm = tb.Frame(top, padding=10); frm.pack(fill=BOTH, expand=True)
        tb.Label(frm, text="Preset name:").pack(anchor="w")
        ent = tb.Entry(frm, textvariable=v, width=28); ent.pack(anchor="w", pady=(4,8)); ent.focus_set()
        def ok():
            name = (v.get() or "").strip()
            if not name:
                messagebox.showwarning("Create Preset", "Preset name cannot be empty.")
                return
            try:
                self.manager.save_avatar_state(name)
            except Exception as exc:
                messagebox.showerror("Create Preset", f"Failed to create preset:\n{exc}")
                return
            top.destroy()
            self._refresh_all()
            messagebox.showinfo("Create Preset", f"Preset '{name}' has been created.")
        def cancel():
            top.destroy()
        btns = tb.Frame(frm); btns.pack(fill=X)
        tb.Button(btns, text="Cancel", bootstyle=SECONDARY, command=cancel).pack(side=RIGHT, padx=4)
        tb.Button(btns, text="OK", bootstyle=PRIMARY, command=ok).pack(side=RIGHT)

    def _delete_preset(self, name: str):
        if not messagebox.askyesno("Delete Preset", f"Delete preset '{name}'?"):
            return
        try:
            self.manager.delete_preset(name)
        except Exception as exc:
            messagebox.showerror("Delete Preset", f"Failed to delete preset:\n{exc}")
            return
        self._refresh_all()
        messagebox.showinfo("Delete Preset", f"Preset '{name}' has been deleted.")

    def run(self):
        self.root.mainloop()


# --- demo runner with a stub manager ---
if __name__ == "__main__":
    class StubManager:
        def __init__(self):
            self.presets = {
                "avtr_111": {"Default": {}, "Photo": {}, "VRChat": {}},
                "avtr_222": {"Comfy": {}, "Battle": {}},
                "avtr_333": {},
            }
        def parse_existing_presets(self): pass
        def apply_avatar_state(self, name): print("apply:", name)
        def save_avatar_state(self, name):
            self.presets.setdefault("avtr_111", {})[name] = {}
        def delete_preset(self, name):
            for aid, ps in self.presets.items():
                if name in ps: del ps[name]; break

    PresetManagerUI(StubManager()).run()