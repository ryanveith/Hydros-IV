class Team:
    def __init__(self, name: str, color: str | None = None):
        self.name = name
        self.color = color
        self.units: list = []

    def add_unit(self, unit):
        self.units.append(unit)
        unit.team = self
        if hasattr(unit, "shadow_image"):
            unit.shadow_image.tint_color = self.color

    def contains(self, unit) -> bool:
        return unit in self.units
