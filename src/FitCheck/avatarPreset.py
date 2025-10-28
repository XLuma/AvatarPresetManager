from FitCheck.avatarParameter import AvatarParameter

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