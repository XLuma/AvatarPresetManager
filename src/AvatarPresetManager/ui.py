"""Tkinter-based user interface for managing avatar presets."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import List, Tuple

from AvatarPresetManager.avatarManager import AvatarManager


class PresetManagerUI:
    """Simple Tk UI for viewing, applying, and creating avatar presets."""

    def __init__(self, manager: AvatarManager) -> None:
        self.manager = manager
        self.root = tk.Tk()
        self.root.title("Avatar Preset Manager")
        self.root.geometry("420x320")

        self._preset_items: List[Tuple[str, str]] = []

        self._build_widgets()
        self._load_presets()

    # ------------------------------------------------------------------
    def _build_widgets(self) -> None:
        """Create and place Tk widgets for the main window."""

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        label = tk.Label(main_frame, text="Available Presets")
        label.grid(row=0, column=0, sticky="w")

        self.preset_list = tk.Listbox(main_frame, activestyle="dotbox")
        self.preset_list.grid(row=1, column=0, sticky="nsew", pady=(4, 8))
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=self.preset_list.yview)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(4, 8))
        self.preset_list.configure(yscrollcommand=scrollbar.set)

        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        button_frame.columnconfigure((0, 1), weight=1)

        self.apply_button = tk.Button(button_frame, text="Apply Preset", command=self._apply_selected)
        self.apply_button.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.create_button = tk.Button(button_frame, text="Create Preset", command=self._create_preset)
        self.create_button.grid(row=0, column=1, padx=(6, 0), sticky="ew")

    # ------------------------------------------------------------------
    def _load_presets(self) -> None:
        """Populate the preset list from the avatar manager."""

        try:
            self.manager.parse_existing_presets()
        except Exception as exc:  # pragma: no cover - UI level feedback
            messagebox.showerror("Preset Manager", f"Failed to load presets:\n{exc}")
            self._preset_items = []
        else:
            self._preset_items = self._extract_presets()

        self._refresh_listbox()

    # ------------------------------------------------------------------
    def _extract_presets(self) -> List[Tuple[str, str]]:
        """Return a sorted list of (avatar_id, preset_name) tuples."""

        items: List[Tuple[str, str]] = []
        for avatar_id, presets in sorted(self.manager.presets.items()):
            for preset_name in sorted(presets.keys()):
                items.append((avatar_id, preset_name))
        return items

    # ------------------------------------------------------------------
    def _refresh_listbox(self) -> None:
        """Refresh listbox contents to match the cached preset items."""

        self.preset_list.delete(0, tk.END)
        if not self._preset_items:
            self.preset_list.insert(tk.END, "No presets available")
            self.preset_list.configure(state=tk.DISABLED)
            self.apply_button.configure(state=tk.DISABLED)
        else:
            self.preset_list.configure(state=tk.NORMAL)
            for avatar_id, preset_name in self._preset_items:
                self.preset_list.insert(tk.END, f"{preset_name} ({avatar_id})")
            self.apply_button.configure(state=tk.NORMAL)

    # ------------------------------------------------------------------
    def _apply_selected(self) -> None:
        """Apply the preset currently selected in the list."""

        if not self._preset_items:
            return

        selection = self.preset_list.curselection()
        if not selection:
            messagebox.showinfo("Apply Preset", "Please select a preset to apply.")
            return

        idx = selection[0]
        avatar_id, preset_name = self._preset_items[idx]
        try:
            self.manager.apply_avatar_state(preset_name)
        except Exception as exc:  # pragma: no cover - UI level feedback
            messagebox.showerror("Apply Preset", f"Failed to apply '{preset_name}':\n{exc}")
        else:
            messagebox.showinfo("Apply Preset", f"Applied preset '{preset_name}' for avatar {avatar_id}.")

    # ------------------------------------------------------------------
    def _create_preset(self) -> None:
        """Prompt for a preset name and save the current avatar state."""

        preset_name = simpledialog.askstring("Create Preset", "Enter a preset name:")
        if preset_name is None:
            return
        preset_name = preset_name.strip()
        if not preset_name:
            messagebox.showwarning("Create Preset", "Preset name cannot be empty.")
            return

        try:
            self.manager.save_avatar_state(preset_name)
        except Exception as exc:  # pragma: no cover - UI level feedback
            messagebox.showerror("Create Preset", f"Failed to create preset:\n{exc}")
            return

        self._preset_items = self._extract_presets()
        self._refresh_listbox()
        messagebox.showinfo("Create Preset", f"Preset '{preset_name}' has been created.")

    # ------------------------------------------------------------------
    def run(self) -> None:
        """Start the Tkinter main loop."""

        self.root.mainloop()


def launch_ui(manager: AvatarManager) -> None:
    """Convenience helper to launch the preset manager UI."""

    ui = PresetManagerUI(manager)
    ui.run()
