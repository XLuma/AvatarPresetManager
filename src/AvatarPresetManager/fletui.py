# flet_preset_manager.py
from __future__ import annotations
import sys
from typing import List, Tuple
import flet as ft
from AvatarPresetManager.avatarManager import AvatarManager
from pathlib import Path
import os

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
    
    def _open_preset_location(self):
        os.startfile(str(self.manager.dataPath))
    
    def _open_settings(self):
        self.page.controls.clear()
        container = ft.Container(
            content=ft.Column(controls=[
                ft.Text("Settings"),
            ]),
            padding=ft.padding.all(10),
            border_radius=8,
            border=ft.border.all(1.5, ft.Colors.with_opacity(0.08, ft.Colors.ON_SURFACE)),
        )
        self.page.add(container)
        self.page.update()
        print("settings")
        pass

    def _open_about(self):
        self.page.controls.clear()
        container = ft.Container(content=ft.Column(
            controls=[
                ft.Text("Avatar Preset Manager is a tool that allows you to save an avatar's state in its entirery, and restore that state at any time while playing VRChat."),
                ft.Text("If you like this project, consider supporting me and the development of this tool by buying a license here: link"),
                ft.Text("Source code to this project can be found here: github link"),
                ft.Text("Need help ? Join our Discord for support: discord link"),
                ft.Text("This project is not affiliated with VRChat."),
                ft.Text("Author: XLuma"),
                ]
            ),
            padding=ft.padding.all(16)
        )
        self.page.add(container)
        pass

    def _open_presets(self):
        self.page.controls.clear()
        self._refresh(self.page)

    def _handle_sidebar(self, e: ft.ControlEvent):
        selected_index = e.control.selected_index
        print(selected_index)
        actions = {
            0: self._open_presets,
           # 1: self._open_settings,      
            1: self._open_preset_location,
            2: self._open_about,
        }
        handler = actions.get(selected_index)
        print(handler)
        self.page.close(self.drawer)
        handler()
        pass
    
    def _handle_avatar_rename(self, avatar_name: str, avatar_id: str):
        self.manager.settings.associate_name_to_avatar(avatar_name, avatar_id)
        self._refresh(self.page)

    def _show_avatar_menu(self, avatar_id, e: ft.TapEvent):
        current_name = self.manager.settings.get_name_for_avatar(avatar_id)
        ctx_menu = ft.AlertDialog(
            title="Parent configuration",
            actions=[
                ft.Column(
                    controls=[
                        ft.Text(f'Targeting avatar id {avatar_id}'),
                        ft.TextField(
                            value=current_name,
                            label="Associate a name",
                            max_length=30,
                            on_blur=lambda e: self._handle_avatar_rename(e.control.value, avatar_id)
                        ),
                        ft.TextButton(
                            "Delete all presets",
                            style=ft.ButtonStyle(color=ft.Colors.RED_400),
                            on_click=lambda e: print("Delete all not implemented"),
                        ),
                    ]
                )
            ]
        )
        # put them on top of everything
        self.page.open(ctx_menu)
        print("hello")
        pass
    def mount(self, page: ft.Page):
        self.page = page
        page.title = "Avatar Preset Manager"
        page.theme_mode = ft.ThemeMode.DARK

        drawer = ft.NavigationDrawer(
            controls=[
                ft.Divider(),
                ft.NavigationDrawerDestination(icon=ft.Icons.PERSON, label="Presets"),
                ft.Divider(),
                ft.NavigationDrawerDestination(icon=ft.Icons.FOLDER, label="Open presets location"),
                ft.Divider(),
                ft.NavigationDrawerDestination(icon=ft.Icons.INFO, label="About"),
            ],
            selected_index=0,
            on_change=self._handle_sidebar
        )
        self.drawer = drawer

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
            ],
        )

        self._load_presets()
        self._render_main(page)

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
        avatar_name = self.manager.settings.get_name_for_avatar(avatar_id)
        return ft.Container(
            border=ft.border.all(1.5, ft.Colors.with_opacity(0.08, ft.Colors.ON_SURFACE)),
            border_radius=8,
            content=ft.GestureDetector(
                    content=ft.ExpansionTile(
                    title=ft.Text(avatar_name if avatar_name != "" else avatar_id),
                    shape=ft.RoundedRectangleBorder(radius=5),
                    collapsed_shape=ft.RoundedRectangleBorder(radius=5),               
                    controls=[
                        ft.Container(
                            padding=ft.padding.all(12),
                            border=ft.border.only(top=ft.BorderSide(1.5, ft.Colors.with_opacity(0.08, ft.Colors.ON_SURFACE))),
                            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.ON_SURFACE),
                            content=ft.Column(
                                [
                                    ft.Column(
                                        [
                                            ft.Row(
                                                [
                                                    ft.Text(p, expand=True),
                                                    ft.TextButton("Apply", on_click=lambda e, n=p: self._apply_preset(n)),
                                                    ft.TextButton("Rename", on_click=lambda e, n=p: self._rename_preset(n)),
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
                ),
                on_long_press_end=lambda e: self._show_avatar_menu(avatar_id=avatar_id, e=e)
            ) 
        )
    
    def _render_main(self, page: ft.Page):
        tiles = [self._avatar_tile(aid, presets) for aid, presets in self._preset_items]
        list_view = ft.ListView(controls=tiles, spacing=6, padding=10, auto_scroll=False)
        page.controls.clear()
        page.add(list_view)
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
            preset = self.manager.find_avatar_preset(name)
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
            self._refresh(self.page)
        except Exception as exc:
            print("Error deleting preset:", exc)

    def _rename_preset(self, name: str):
        try:
            nameInput = ft.TextField(
                label="Enter a name",
                max_length=30,
            )
            def on_save(ev: ft.ControlEvent):
                val = nameInput.value
                if val and val != "":
                    self.manager.rename_preset(name, val)
                self.page.close(ctx_menu)
                self._refresh(self.page)

            ctx_menu = ft.AlertDialog(
            title="Rename preset",
            modal=True,
            actions=[
                nameInput,
                ft.Container(height=6),
                ft.Row(
                    controls= [
                            ft.TextButton("Cancel", on_click=lambda e: self.page.close(ctx_menu)),
                            ft.TextButton("Save", on_click=lambda ev: on_save(ev)),
                        ]
                    ),
                ]
            )

            self.page.open(ctx_menu)
        except Exception as exc:
            self._notify(f'Failed to rename preset {name}: {exc}', 2000, "error")

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
                ft.TextButton("Cancel", on_click=lambda ev: self.page.close(dlg)),
                ft.ElevatedButton("OK", on_click=on_ok),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(dlg)
    
    def _on_program_close(self, e: ft.AppLifecycleStateChangeEvent):
        if e.state == ft.AppLifecycleState.HIDE or e.state == ft.AppLifecycleState.DETACH:
            print("Program close")  
            self.manager.save_settings()
    


# -------- entrypoint --------
    def run(self, page: ft.Page):
        self.mount(page)
        page.on_app_lifecycle_state_change = self._on_program_close
