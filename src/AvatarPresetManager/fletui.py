# flet_preset_manager.py
from __future__ import annotations
import sys
from typing import List, Tuple
import flet as ft
from AvatarPresetManager.avatarManager import AvatarManager


class FletPresetManagerUI:
    """Flet-based UI for managing avatar presets."""

    def __init__(self, manager: AvatarManager) -> None:
        self.manager = manager

        self._preset_items: List[Tuple[str, List[str]]] = []  # list of (avatar_id, [presets])
        self.page: ft.Page | None = None
        self.vrchat_online: bool = False
        self.status_chip: ft.Container | None = None
        self.drawer: ft.Control | None = None
        self.vrchat_online: bool = False

    def _load_presets(self):
        try:
            self.manager.parse_existing_presets()
            self._preset_items = [
                (avatar_id, sorted(list(presets.keys())))
                for avatar_id, presets in sorted(self.manager.presets.items())
            ]
        except Exception as exc:
            print("Error loading presets:", exc)
            self._preset_items = []


    def mount(self, page: ft.Page):
        self.page = page
        page.title = "Avatar Preset Manager"
        page.theme_mode = ft.ThemeMode.DARK

        # Sidebar
        drawer = ft.NavigationDrawer(
            controls=[
                ft.NavigationDrawerDestination(icon=ft.Icons.SETTINGS, label="Settings"),
                ft.NavigationDrawerDestination(icon=ft.Icons.INFO, label="About"),
            ]
        )

        self.status_chip = ft.Container(
            padding=ft.padding.symmetric(6, 8),
            border_radius=16,
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.RED_400),
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CIRCLE, size=10, color=ft.Colors.RED_400),
                    ft.Text("VRChat: Offline", size=12),
                ],
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        page.appbar = ft.AppBar(
            leading=ft.IconButton(ft.Icons.MENU, on_click=lambda e: page.open(drawer)),
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Text("Avatar Preset Manager"), 
                        self.status_chip,
                    ], 
                    spacing=16
                )
            ),
            actions=[
                ft.TextButton("Create Preset", on_click=self._on_create),
                ft.TextButton("Refresh", on_click=lambda e: self._refresh(page)),
                ft.TextButton("Close with logs", on_click=lambda e: self._force_quit())
            ],
        )

        self.drawer = drawer
        page.add(drawer)

        self._load_presets()
        self._render_main(page)

    def _force_quit(self):
        self.page.window.destroy()
        sys.exit(100)

    def set_vrchat_online(self, is_online: bool, ip: str | None = None, port: int | None = None):
        self.vrchat_online = is_online
        if not self.page or not self.status_chip:
            return
        if is_online:
            label = f"VRChat: Online{f' ({ip}:{port})' if ip and port else ''}"
            self.status_chip.bgcolor = ft.Colors.with_opacity(0.15, ft.Colors.GREEN_400)
            self.status_chip.content.controls[0].color = ft.Colors.GREEN_400
            self.status_chip.content.controls[1].value = label
        else:
            self.status_chip.bgcolor = ft.Colors.with_opacity(0.15, ft.Colors.RED_400)
            self.status_chip.content.controls[0].color = ft.Colors.RED_400
            self.status_chip.content.controls[1].value = "VRChat: Offline"
        self.page.update()

    def _avatar_tile(self, avatar_id: str, presets: list[str]) -> ft.ExpansionTile:
        return ft.Container(
            border=ft.border.all(1.5, ft.Colors.with_opacity(0.08, ft.Colors.ON_SURFACE)),
            border_radius=8,
            content=ft.ExpansionTile(
                title=ft.Text(avatar_id),
                #collapsed_bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.ON_SURFACE),
                shape=ft.RoundedRectangleBorder(radius=5),
                collapsed_shape=ft.RoundedRectangleBorder(radius=5),
                
                controls=[
                    ft.Container(
                        padding=ft.padding.all(12),
                        border=ft.border.only(top=ft.BorderSide(1.5, ft.Colors.with_opacity(0.08, ft.Colors.ON_SURFACE))),
                        #border_radius=ft.border_radius.only(0,0,8,8),
                        bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.ON_SURFACE),
                        content=ft.Column(
                            [
                                #ft.Container(height=6),
                                ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Text(p, expand=True),
                                                ft.TextButton("Apply", on_click=lambda e, n=p: self._apply_preset(n)),
                                                ft.TextButton(
                                                    "Delete",
                                                    style=ft.ButtonStyle(color=ft.Colors.RED_400),
                                                    on_click=lambda e, n=p: self._delete_preset(n),
                                                ),
                                            ],
                                        )
                                        for p in presets
                                    ],
                                    spacing=4,
                                ),
                            ],
                            spacing=10,
                        ),
                    )
                ],
            )
        )
    
    def _render_main(self, page: ft.Page):
        tiles = [self._avatar_tile(aid, presets) for aid, presets in self._preset_items]
        list_view = ft.ListView(controls=tiles, spacing=6, padding=10, auto_scroll=False)
        page.controls.clear()
        page.add(self.drawer, list_view)
        page.update()

    def _refresh(self, page: ft.Page):
        self._load_presets()
        self._render_main(page)

    # ----- Actions -----
    def _notify(self, msg: str, duration: int, level: str = "info"):
        if not self.page:
            return
        color = {
            "info": ft.Colors.BLUE_300,
            "success": ft.Colors.GREEN_300,
            "warning": ft.Colors.AMBER_300,
            "error": ft.Colors.RED_300,
        }.get(level, ft.Colors.BLUE_300)
        self.page.open(ft.SnackBar(ft.Text(msg), bgcolor=color, duration=duration))

    def _apply_preset(self, name: str):
        try:
            preset = self.manager.find_avatar_preset(presetName=name, avatarId="")
            self._notify(f'Applying preset {name} to avatar with id {preset.avatarId}', duration=2000)
            self.manager.apply_avatar_state(name)
            #something here to wait a full two second
            self._notify(f'Preset {name} has been applied !',duration=2000, level="success")
        except Exception as exc:
            print("Error applying:", exc)

    def _create_preset(self, name: str):
        try:
            self.manager.save_avatar_state(name)
        except Exception as exc:
            print("Error creating preset:", exc)

    def _delete_preset(self, name: str):
        try:
            self.manager.delete_preset(name)
        except Exception as exc:
            print("Error deleting preset:", exc)

    def _on_create(self, e):
        # Simple textfield dialog for preset name
        tf = ft.TextField(label="Preset name", autofocus=True)

        def on_ok(ev):
            val = (tf.value or "").strip()
            if val:
                self._create_preset(val)
            dlg.open = False
            e.page.update()
            self._refresh(e.page)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Create Preset"),
            content=tf,
            actions=[
                ft.TextButton("Cancel", on_click=lambda ev: setattr(dlg, "open", False)),
                ft.ElevatedButton("OK", on_click=on_ok),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(dlg)


# -------- entrypoint --------
    def run(self, page):
        self.mount(page)

