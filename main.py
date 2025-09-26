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
            # ensure separator
            new_prefix = f"{prefix}/{name}" if prefix else name
            yield from walk_node(sub, new_prefix)
    else:
        # Leaf node
        info = {
            "path": prefix,
            "type": node.get("TYPE"),
            "default": node.get("DEFAULT"),
            "range": node.get("RANGE"),
            "tags": node.get("TAGS"),
            "value": node.get("VALUE"),
        }
        yield info

class AvatarParameter():
    def __init__(self, name, path, value):
        self.name = name
        self.path = path
        if type(value) is list:
            self.value = value[0] #since its passed as an array from osc
        else:
            self.value = value
        pass
    def __repr__(self):
        return f"AvatarParameter(name={self.name!r}, value={self.value}, path={self.path})"
    def to_dict(self):
        return {"name": self.name, "path": self.path, "value": self.value}
    def from_dict(d: dict) -> "AvatarParameter":
        return AvatarParameter(name=d["name"], value=d["value"], path=d["path"])

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
        self.get_root_node()
        avatarChange = self.currentAvatarRaw["CONTENTS"]["avatar"]["CONTENTS"]["change"]
        avatarId = avatarChange.get("VALUE")[0]
        return avatarId
    def get_avatar_params(self) -> list[AvatarParameter]:
        """
        Returns a list of avatar parameters
        """
        self.get_root_node() # Refresh data
        avatar_node = self.currentAvatarRaw["CONTENTS"]["avatar"]["CONTENTS"]["parameters"]
        params = list(walk_node(avatar_node, "/avatar/parameters"))
        paramList: list[AvatarParameter] = []
        for p in params:
            paramName = str(p['path']).split("/")[-1] #strip path prefix
            param = AvatarParameter(paramName, p['path'], p['value'])
            paramList.append(param)
        return paramList

class AvatarPreset():
    def __init__(self, name, avatarId, parameters):
        self.name = name
        self.avatarId = avatarId
        self.uniqueKey = ""
        self.parameters: list[AvatarParameter] = parameters
        pass
    def to_dict(self):
        return {
            "name": self.name,
            "avatarId": self.avatarId,
            "uniqueKey": self.uniqueKey,
            "parameters": [p.to_dict() for p in self.parameters],
        }
    def from_dict(d: dict) -> "AvatarPreset":
        params = [AvatarParameter.from_dict(p) for p in d.get("parameters", [])]
        return AvatarPreset(
            name=d["name"],
            avatarId=d["avatarId"],
            parameters=params,
        )
        

# we could save shit like. avatar: object, then key: paramname, then
class AvatarManager():
    def __init__(self, client: VRCClient):
        config = self.read_config()
        self.blacklistIndividual: list[str] = config['blacklist']['individual']
        self.blacklistPartial: list[str] = config['blacklist']['partial']
        self.presets: list[AvatarPreset] = [] 
        self.vrcclient = client
        pass
    def read_config(self):
        file = open("config.json", "r")
        config = json.load(file)
        file.close()
        return config
    def save_avatar_state(self, preset: AvatarPreset):
        with open(preset.avatarId + ".json", 'w') as file:
            json.dump(preset.to_dict(), file, indent=2)
        pass
    def is_in_partial_blacklist(self, paramName: str):
        for fix in self.blacklistPartial:
            if paramName.find(fix) != -1:
                return True
        return False
    def apply_avatar_state(self, avId: str):
        #Ideally here we NEVER read the file, we fetch from self.prests. Will be done eventually,this is just for testing
        with open(avId + ".json", "r") as file:
            data = json.load(file)
            loaded_preset: AvatarPreset = AvatarPreset.from_dict(data)
            for param in loaded_preset.parameters:
                if param.name not in self.blacklistIndividual:
                    self.vrcclient.send_param_change(param.path, param.value)
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