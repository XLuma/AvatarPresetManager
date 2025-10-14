from typing import Dict
from pathlib import Path

class Settings():
    def __init__(self):
        self.blacklistIndividual = [
            "TrackingTypeProxy",
            "CgeSmiling",
            "VRModeProxy",
            "VelocityX",
            "VelocityY",
            "VelocityZ",
            "AngularY",
            "Grounded",
            "AFK",
            "Upright",
            "TrackingType",
            "VRMode",
            "MuteSelf",
            "Voice",
            "Earmuffs",
            "VelocityMagnitude",
            "ScaleFactor",
            "ScaleFactorInverse",
            "ScaleModified",
            "EyeHeightAsPercent",
            "EyeHeightAsMeters",
            "IsOnFriendsList",
            "IsAnimatorEnabled",
            "Viseme",
            "GestureLeft",
            "GestureRight",
            "GestureLeftWeight",
            "GestureRightWeight",
            "Seated",
            "InStation",
            "PreviewMode",
            "VRCEmote",
            "VRCFaceBlendH",
            "VRCFaceBlendV"
        ]
        self.blacklistPartial = [
            "OGB",
            "VF10",
            "Go",
            "VFH",
            "VF_"
        ]
        self.avatarIdAssociations = {} #"avId": userProvidedName
        self.isLightMode: bool = False
        pass
    def from_dict():
        pass

    def to_dict():
        pass

    def associate_name_to_avatar(self, name: str, avatar_id: str):
        self.avatarIdAssociations[avatar_id] = name
        print(self.avatarIdAssociations)
    
    def get_name_for_avatar(self, avatar_id: str) -> str:
        name = self.avatarIdAssociations.get(avatar_id)
        if not name: return ""
        return name
    