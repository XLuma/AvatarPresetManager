import json
import os
import time
import copy
from typing import Dict
from pathlib import Path
from FitCheck.avatarPreset import AvatarPreset
from FitCheck.vrcClient import VRCClient
from FitCheck.settings import Settings

class AvatarManager():
    def __init__(self, client: VRCClient):
        self.dataPath = Path(os.getenv("FLET_APP_STORAGE_DATA"))
        self.settings = self.load_settings()
        self.blacklistIndividual: list[str] = self.settings.blacklistIndividual
        self.blacklistPartial: list[str] = self.settings.blacklistPartial
        self.presets: Dict[str, Dict[str, AvatarPreset]] = {}
        self.vrcclient = client
        self.preset_nums = 0
        pass

    def parse_existing_presets(self) -> int:
        """
        Returns the number of parsed presets
        """
        path = self.dataPath / "presets"
        
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
    
    def save_avatar_state(self, presetName: str):
        avatarId = self.vrcclient.get_avatar_id()
        avatarState = self.vrcclient.get_avatar_params()
        preset = AvatarPreset(presetName, avatarId, avatarState)
        self.presets.setdefault(avatarId, {})[presetName] = preset
        path = self.dataPath / "presets" / avatarId
        path.mkdir(parents=True, exist_ok=True)
        presetPath = path / f"{presetName}.json"
        presetPath.write_text(json.dumps(preset.to_dict(), indent=2))
        return preset
    
    def save_avatar_state_from_preset(self, preset: AvatarPreset):
        self.presets.setdefault(preset.avatarId, {})[preset.name] = preset
        path = self.dataPath / "presets" / preset.avatarId
        path.mkdir(parents=True, exist_ok=True)
        presetPath = path / f"{preset.name}.json"
        presetPath.write_text(json.dumps(preset.to_dict(), indent=2))

    def is_in_partial_blacklist(self, paramName: str) -> bool:
        for fix in self.blacklistPartial:
            if paramName.startswith(fix) == True:
                return True
        return False
    
    def find_avatar_preset(self, avatarId: str, presetName: str) -> AvatarPreset: #Ideally here, we throw an error if not found and we handle that properly.
        if avatarId in self.presets:
            if presetName in self.presets[avatarId]:
                return self.presets[avatarId][presetName]
        raise Exception()
    
    def delete_preset_deprecated(self, presetName: str) -> bool:
        preset = self.find_avatar_preset(presetName)
        if not preset.name: 
            raise Exception()
        path = self.dataPath / "presets" / preset.avatarId / f"{preset.name}.json"
        if not path.is_file():
            raise Exception()
        path.unlink()
        del self.presets[preset.avatarId][presetName]
        return True

    def delete_preset(self, preset: AvatarPreset) -> bool:
        if not preset.name: 
            raise Exception()
        path = self.dataPath / "presets" / preset.avatarId / f"{preset.name}.json"
        if not path.is_file():
            raise Exception()
        path.unlink()
        del self.presets[preset.avatarId][preset.name]
        return True
    
    def apply_avatar_state(self, presetName: str):
        currentAvatarId = self.vrcclient.get_avatar_id()
        preset = self.find_avatar_preset(presetName)
        if currentAvatarId != preset.avatarId:
            self.vrcclient.change_avatar(preset.avatarId)
            self.vrcclient.wait_for_avatar_ready(min_params=1) #this is absolutely necessary because the game often sends back avatar id very early
        self.vrcclient.get_root_node() # refresh avi data
        for param in preset.parameters:
            if param.name not in self.blacklistIndividual and not self.is_in_partial_blacklist(param.rawName):
                self.vrcclient.send_param_change(param.path, param.value)
        pass

    def apply_avatar_state_by_preset(self, preset: AvatarPreset):
        currentAvatarId = self.vrcclient.get_avatar_id()
        if currentAvatarId != preset.avatarId:
            self.vrcclient.change_avatar(preset.avatarId)
            self.vrcclient.wait_for_avatar_ready(min_params=1) #this is absolutely necessary because the game often sends back avatar id very early
        self.vrcclient.get_root_node() # refresh avi data
        for param in preset.parameters:
            if param.name not in self.blacklistIndividual and not self.is_in_partial_blacklist(param.rawName):
                self.vrcclient.send_param_change(param.path, param.value)
        pass
    
    def rename_preset(self, avatarId: str, presetName: str, newPresetName: str):
        preset = copy.deepcopy(self.find_avatar_preset(avatarId, presetName))
        self.delete_preset(preset)
        preset.name=newPresetName
        self.save_avatar_state_from_preset(preset)

    def save_settings(self):
        path = self.dataPath / "settings.json"
        settings = self.settings.to_dict()
        print(settings)
        path.write_text(json.dumps(self.settings.to_dict(), indent=2))
    
    def load_settings(self) -> Settings | None:
        path = self.dataPath / "settings.json"
        if not path.exists():
            return Settings(False, {})
        with path.open() as file:
            return Settings.from_dict(json.load(file))