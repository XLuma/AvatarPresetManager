import requests
from AvatarPresetManager.avatarParameter import AvatarParameter
from pythonosc.udp_client import SimpleUDPClient

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
    def get_avatar_id(self) -> str:
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