from world.element import WorldElement
from world.configs import ConfigObject


class WorldObject(WorldElement):

    def __init__(self, config: ConfigObject, x: int, y: int):
        super().__init__(config.name, config.resource_max)
        self.config = config
        self.x = x
        self.y = y

    def is_alive(self) -> bool:
        return self.points > 0

    def __repr__(self) -> str:
        return (
            f"WorldObject(name='{self.name}', pos=({self.x}, {self.y}), "
            f"points={self.points}/{self.config.resource_max})"
        )