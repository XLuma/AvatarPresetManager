from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
import os
import AvatarPresetManager.xsnotif as xsnotif
import sys
from AvatarPresetManager.oscq_discovery import OscQueryDiscovery
from AvatarPresetManager.avatarManager import AvatarManager
from AvatarPresetManager.vrcClient import VRCClient
#from AvatarPresetManager.boostrapui import PresetManagerUI
from AvatarPresetManager.fletui import FletPresetManagerUI

def main():
    #os.system('cls' if os.name == 'nt' else 'clear')
    oscqService = OscQueryDiscovery()
    try:
        if not oscqService.wait(10):
            print("bruh")
            sys.exit(1)
        print(oscqService.ip)
        print(oscqService.port)
        client = VRCClient(oscqService.port)
        avatarManager = AvatarManager(client=client)
        ui = FletPresetManagerUI(avatarManager)
        ui.run()
    except Exception as e:
        os._exit(1)
    finally:
        oscqService.stop()

if __name__ == "__main__":
    main()