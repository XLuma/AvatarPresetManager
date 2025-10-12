import sys
from AvatarPresetManager.oscq_discovery import OscQueryDiscovery
from AvatarPresetManager.avatarManager import AvatarManager
from AvatarPresetManager.vrcClient import VRCClient
from AvatarPresetManager.fletui import FletPresetManagerUI
import flet as ft

def main(page: ft.Page):
    #os.system('cls' if os.name == 'nt' else 'clear')
    oscqService = OscQueryDiscovery()
    if not oscqService.wait(10):
        print("bruh")
        sys.exit(100)
    page.add(ft.Text("somehow we here"))
    print(oscqService.ip)
    print(oscqService.port)
    client = VRCClient(oscqService.port)
    avatarManager = AvatarManager(client=client)
    ui = FletPresetManagerUI(avatarManager)
    ui.run(page)
    oscqService.stop()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)