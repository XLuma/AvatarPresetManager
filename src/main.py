import sys
import time
import threading
from FitCheck.oscq_discovery import OscQueryDiscovery
from FitCheck.avatarManager import AvatarManager
from FitCheck.vrcClient import VRCClient
from FitCheck.fletui import FletPresetManagerUI
import flet as ft

def main(page: ft.Page):
    avatarManager = AvatarManager(client=None)
    ui = FletPresetManagerUI(avatarManager)
    stop_evt = threading.Event()
    def discovery_worker():
        oscq = OscQueryDiscovery()
        last_state = None
        while not stop_evt.is_set():
            found = oscq.wait(2)
            if found and last_state is not True:
                ip, port = oscq.ip, oscq.port
                client = VRCClient(port)
                avatarManager.vrcclient = client
                ui.set_vrchat_online(True, ip, port)
                last_state = True
                page.update()
                ui._notify("VRChat is running !", 2000, "success")
            elif not found and last_state is not False:
                avatarManager.vrcclient = None
                ui.set_vrchat_online(False)
                last_state = False
                page.update()
                ui._notify("VRChat is offline !", 2000, "error")
            time.sleep(0.5)
            oscq.stop()
            oscq = OscQueryDiscovery()
  
    page.add(ft.Text("somehow we here"))
    ui.run(page)
    t = threading.Thread(target=discovery_worker, daemon=True)
    t.start()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
    