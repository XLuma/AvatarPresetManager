from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
import os
import AvatarPresetManager.xsnotif as xsnotif
import sys
from AvatarPresetManager.oscq_discovery import OscQueryDiscovery
from AvatarPresetManager.avatarManager import AvatarManager

# we could save shit like. avatar: object, then key: paramname, then

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    oscqService = OscQueryDiscovery()
    try:
        if not oscqService.wait(10):
            print("bruh")
            sys.exit(1)
        print(oscqService.ip)
        print(oscqService.port)
        while(True):
            print("What to do ?\n")
            userInput = input("[1]: Save avatar state\n[2]: Load preset\n")
            os.system('cls' if os.name == 'nt' else 'clear')
            if int(userInput) == 1:
                presetName = input("What is the name of the preset ?\n")
                if presetName == "":
                    presetName = "default"
                pass
            elif int(userInput) == 2:
                pass
            else:
                os.system('cls' if os.name == 'nt' else 'clear')
        
        client = VRCClient(oscqPort=oscqService.port)
        avatarManager = AvatarManager(client=client)
        avId = client.get_avatar_id()
        preset = AvatarPreset("testPreset1", client.get_avatar_id(), client.get_avatar_params())
        #avatarManager.save_avatar_state(preset)
        avatarManager.apply_avatar_state(avId)

        pass
    finally:
        oscqService.stop()

if __name__ == "__main__":
    main()