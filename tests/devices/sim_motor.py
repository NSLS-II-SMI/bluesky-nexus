from ophyd.sim import motor


# Class simulating metadata of SimMotor
class MetadataSimMotor:
    worldPosition: dict = {
        "x": "1.2000000000000003",
        "y": "4.5000000000000006",
        "z": "7.8000000000000009",
    }
    description: str = "I am a simulated motor"
    baseline: bool = True

    def get_attributes(self):
        attributes = {
            "worldPosition": self.worldPosition,
            "description": self.description,
            "baseline": self.baseline,
        }
        return attributes


class SimMotor(motor.__class__):  # or simply: class SimMotor(type(motor)):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.md = MetadataSimMotor()
