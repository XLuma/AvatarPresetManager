import json
import os
import time
from typing import Dict
from pathlib import Path
from AvatarPresetManager.avatarPreset import AvatarPreset
from AvatarPresetManager.vrcClient import VRCClient

class AvatarManager():
    def __init__(self, client: VRCClient):
        config = self.read_config()
        self.blacklistIndividual: list[str] = config['blacklist']['individual']
        self.blacklistPartial: list[str] = config['blacklist']['partial']
        self.presets: Dict[str, Dict[str, AvatarPreset]] = {}
        self.vrcclient = client
        self.preset_nums = 0
        pass
    def parse_existing_presets(self) -> int:
        """
        Returns the number of parsed presets
        """
        path = Path.cwd() / "presets"
        self.presets.clear()
        if not path.exists():
            path.mkdir()
            return 0
        for avatar_dir in sorted(p for p in path.iterdir() if p.is_dir() and not p.name.startswith(".")):
            avatar_id = avatar_dir.name
            presets: Dict[str, AvatarPreset] = {}
            for blob in sorted(avatar_dir.glob("*.json")):
                preset_name = blob.stem # test this
                with blob.open() as file:
                    data = json.load(file)
                    presets[preset_name] = AvatarPreset.from_dict(data)
                    self.preset_nums += 1
            if presets:
                self.presets[avatar_id] = presets
        print(self.presets)
        return self.preset_nums
    def read_config(self):
        print(os.getcwd())
        file = open("src/config.json", "r")
        config = json.load(file)
        file.close()
        return config
    def save_avatar_state(self, presetName: str):
        avatarId = self.vrcclient.get_avatar_id()
        avatarState = self.vrcclient.get_avatar_params()
        preset = AvatarPreset(presetName, avatarId, avatarState)
        self.presets.setdefault(avatarId, {})[presetName] = preset
        path = Path.cwd() / "presets" / avatarId
        path.mkdir(parents=True, exist_ok=True)
        presetPath = path / f"{presetName}.json"
        presetPath.write_text(json.dumps(preset.to_dict(), indent=2))
        pass
    def is_in_partial_blacklist(self, paramName: str) -> bool:
        for fix in self.blacklistPartial:
            if paramName.startswith(fix) == True:
                return True
        return False
    def find_avatar_preset(self, presetName: str, avatarId: str) -> AvatarPreset: #Ideally here, we throw an error if not found and we handle that properly.
        ##figure out overloads for avId or whatever
        for avatarId, presets in self.presets.items():
            for savedPresetName, preset in presets.items():
                if presetName == savedPresetName:
                    return preset
        raise Exception()
    def delete_preset(self, presetName: str) -> bool:
        preset = self.find_avatar_preset(presetName=presetName, avatarId="")
        if not preset.name: 
            raise Exception()
        path = Path.cwd() / "presets" / preset.avatarId / f"{preset.name}.json"
        if not path.is_file():
            raise Exception()
        path.unlink()
        del self.presets[preset.avatarId][presetName]
        return True
    def apply_avatar_state(self, presetName: str):
        currentAvatarId = self.vrcclient.get_avatar_id()
        preset = self.find_avatar_preset(presetName=presetName, avatarId="")
        if currentAvatarId != preset.avatarId:
            self.vrcclient.change_avatar(preset.avatarId)
            self.vrcclient.wait_for_avatar_ready(min_params=1) #this is absolutely necessary because the game often sends back avatar id very early
        self.vrcclient.get_root_node() # refresh avi data
        for param in preset.parameters:
            if param.name not in self.blacklistIndividual and not self.is_in_partial_blacklist(param.rawName):
                self.vrcclient.send_param_change(param.path, param.value)
        pass