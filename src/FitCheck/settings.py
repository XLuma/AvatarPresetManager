from typing import Dict
from pathlib import Path

class Settings():
    def __init__(self, isLightMode, avatarIdAssociations):
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
            "VRCFaceBlendV",
            "VRMode"
        ]
        self.blacklistPartial = [
            "OGB",
            "VF10",
            "Go",
            "VFH",
            "VF_"
            "FT/v2"
        ]
        self.avatarIdAssociations = avatarIdAssociations #"avId": userProvidedName
        self.isLightMode: bool = isLightMode
        pass
    def from_dict(d: dict) -> "Settings":
        return Settings(isLightMode=d["isLightMode"], avatarIdAssociations=d["avatarIdAssociations"])

    def to_dict(self):
        return {"isLightMode": self.isLightMode, "avatarIdAssociations": self.avatarIdAssociations}

    def associate_name_to_avatar(self, name: str, avatar_id: str):
        self.avatarIdAssociations[avatar_id] = name
    
    def get_name_for_avatar(self, avatar_id: str) -> str:
        name = self.avatarIdAssociations.get(avatar_id)
        if not name: return ""
        return name
    