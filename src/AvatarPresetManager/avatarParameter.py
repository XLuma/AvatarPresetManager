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