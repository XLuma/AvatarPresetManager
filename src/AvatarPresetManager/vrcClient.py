import requests
from AvatarPresetManager.avatarParameter import AvatarParameter
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import time

class VRCClient():
    def __init__(self, oscqPort: int):
        self.ip = "127.0.0.1"
        self.port = 9000 #vrchat expects messages over there
        self.client = SimpleUDPClient(self.ip, self.port)
        self.oscqport: int = oscqPort
        self.currentAvatarRaw = {}
        #some code to get the config ? maybe ?
    def send_param_change(self, path, param):
        """
        Will send a message to VRChat with OSC. Returns nothing.
        """
        self.client.send_message(path, param) #should work for any type of parameter
    def change_avatar(self, avatarId: str):
        self.send_param_change("/avatar/change", avatarId)
    def get_root_node(self):
        """
        Gets the current avatar state, and returns it. Can be retrieved with the currentAvatarRaw attribute
        """
        self.currentAvatarRaw.clear()
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
    def wait_for_avatar_ready(self, timeout=25, min_params=25, quiet_ms=400, required_params=None):
        """
        Wait for: /avatar/change -> enough distinct /avatar/parameters/*
        -> no *new* parameter names for quiet_ms.
        Returns avatar_id, raises TimeoutError on timeout.
        """
        required = set(required_params or [])
        state = {
            "avatar_id": None,
            "seen": set(),                # distinct parameter names
            "last_new_name_ts": 0.0,      # only updated when a *new* name is observed
            "change_ts": 0.0,
        }

        def on_change(addr, *args):
            if not args:
                return
            avatar_id = args[0]
            # reset state
            state["avatar_id"] = avatar_id
            state["seen"].clear()
            state["last_new_name_ts"] = 0.0
            state["change_ts"] = time.monotonic()
            print(f"[osc] /avatar/change {avatar_id}")

        def on_param(addr, *args):
            # only track after we've seen /avatar/change
            if not state["avatar_id"]:
                return
            # param name = last path segment
            pname = addr.rsplit("/", 1)[-1]
            if pname not in state["seen"]:
                state["seen"].add(pname)
                state["last_new_name_ts"] = time.monotonic()
                # print(f"[osc] new param: {pname} (count={len(state['seen'])})")

        disp = Dispatcher()
        disp.map("/avatar/change", on_change)
        disp.map("/avatar/parameters/*", on_param)

        server = BlockingOSCUDPServer(("127.0.0.1", 9001), disp)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()

        deadline = time.monotonic() + timeout
        try:
            # 1) wait for /avatar/change
            while not state["avatar_id"]:
                if time.monotonic() > deadline:
                    raise TimeoutError("No /avatar/change received within timeout")
                time.sleep(0.01)

            # 2) wait until enough distinct params have appeared
            while True:
                if time.monotonic() > deadline:
                    raise TimeoutError("Avatar did not expose enough parameters in time")

                seen = state["seen"]
                enough = (required and required.issubset(seen)) or (len(seen) >= min_params)
                if not enough:
                    time.sleep(0.02)
                    continue

                # 3) debounce: no *new* names for quiet_ms
                last_new = state["last_new_name_ts"]
                if last_new and (time.monotonic() - last_new) * 1000.0 >= quiet_ms:
                    print(state["seen"])
                    return state["avatar_id"]

                time.sleep(0.02)
        finally:
            server.shutdown()
    
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