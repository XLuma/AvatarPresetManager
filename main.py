from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
import requests
import os
import threading
import schedule
import time
import json
import xsnotif
import pytimedinput
import sys
from oscq_discovery import OscQueryDiscovery

def walk_node(node, prefix=""):
    """Recursively walk the OSCQuery tree and yield parameter info."""
    if "CONTENTS" in node:
        for name, sub in node["CONTENTS"].items():
            yield from walk_node(sub, prefix + name)
    else:
        # Leaf node: should have TYPE/DEFAULT/etc.
        info = {
            "path": prefix,
            "type": node.get("TYPE"),
            "default": node.get("DEFAULT"),
            "range": node.get("RANGE"),
            "tags": node.get("TAGS"),
            "value": node.get("VALUE")
        }
        yield info

class AvatarParameter():
    def __init__(self, name, path, value):
        self.name = name
        self.path = path
        self.value = value[0] #since its passed as an array from osc
        pass

class VRCClient():
    def __init__(self, oscqPort):
        self.ip = "127.0.0.1"
        self.port = 9000 #vrchat expects messages over there
        self.client = SimpleUDPClient(self.ip, self.port)
        self.oscqport = oscqPort
        self.currentAvatarRaw = {}
        #some code to get the config ? maybe ?
    def send_param_change(self, path, param):
        """
        Will send a message to VRChat with OSC. Returns nothing.
        """
        self.client.send_message(path, param) #should work for any type of parameter
    def get_root_node(self):
        """
        Gets the current avatar state, and returns it. Can be retrieved with the currentAvatarRaw attribute
        """
        req = requests.get(f'http://{self.ip}:{self.oscqport}')
        req.raise_for_status()
        data = req.json()
        self.currentAvatarRaw = data
        return data
    def get_avatar_id(self):
        """
        Returns the current avatar ID, name, author, etc. from OSCQuery root.
        """
        print(self.currentAvatarRaw)
        avatarChange = self.currentAvatarRaw["CONTENTS"]["avatar"]["CONTENTS"]["change"]
        avatarId = avatarChange.get("VALUE")[0]
        return avatarId
    def get_avatar_params(self) -> list[AvatarParameter]:
        """
        Returns the
        """
        self.get_root_node() # Refresh data
        avatar_node = self.currentAvatarRaw["CONTENTS"]["avatar"]["CONTENTS"]["parameters"]
        params = list(walk_node(avatar_node, "/avatar/parameters/"))
        paramList: list[AvatarParameter] = []
        for p in params:
            paramName = p['path'].split("/", 3)[-1] #strip /avatar/parameters/
            param = AvatarParameter(paramName, p['path'], p['value'])
            paramList.append(param)
        return paramList

class AvatarPreset():
    def __init__(self, name, avatarId, data):
        self.name = name
        self.avatarId = avatarId
        self.uniqueKey = ""
        self.parameters: list[AvatarParameter] = data
        pass
    def output(self):
        pass

# we could save shit like. avatar: object, then key: paramname, then
class AvatarManager():
    def __init__(self):
        self.paramBlacklist = []
        pass
    def save_avatar_state(self, avatarId, presetName, parameters):
        
        pass
    def apply_avatar_state(self):
        pass

def main():
    oscqService = OscQueryDiscovery()
    try:
        if not oscqService.wait(10):
            print("bruh")
            sys.exit(1)
        print(oscqService.ip)
        print(oscqService.port)
        client = VRCClient(oscqPort=oscqService.port)
        pass
    finally:
        oscqService.stop()

if __name__ == "__main__":
    main()