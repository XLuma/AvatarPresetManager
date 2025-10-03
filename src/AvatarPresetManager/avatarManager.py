import json
import os
from AvatarPresetManager.avatarPreset import AvatarPreset
from AvatarPresetManager.vrcClient import VRCClient

class AvatarManager():
    def __init__(self, client: VRCClient):
        self.blacklistIndividual: list[str] = config['blacklist']['individual']
        self.blacklistPartial: list[str] = config['blacklist']['partial']
        self.presets: list[AvatarPreset] = [] 
        self.vrcclient = client
        if os.path.isdir(os.getcwd() + "/presets"):
            os.mkdir(os.getcwd() + "/presets")
        # todo: finish code to load presets from disk
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
    def is_in_partial_blacklist(self, paramName: str) -> bool:
        for fix in self.blacklistPartial:
            if paramName.find(fix) != -1:
                return True
        return False
    def check_if_preset_exists(self, presetName: str) -> bool:
        for preset in self.presets:
            if preset.name == presetName:
                return True
        return False
    def find_avatar_preset(self, presetName: str, avatarId: str) -> AvatarPreset | object: #Ideally here, we throw an error if not found and we handle that properly.
        for preset in self.presets:
            if preset.name == presetName and preset.avatarId == avatarId:
                return preset
        return {}
    def apply_avatar_state(self, avId: str):
        #Ideally here we NEVER read the file, we fetch from self.prests. Will be done eventually,this is just for testing
        with open(avId + ".json", "r") as file:
            data = json.load(file)
            loaded_preset: AvatarPreset = AvatarPreset.from_dict(data)
            for param in loaded_preset.parameters:
                if param.name not in self.blacklistIndividual:
                    self.vrcclient.send_param_change(param.path, param.value)
        pass