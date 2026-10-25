from world.element import WorldElement
from world.configs import ConfigTerrain


class Terrain(WorldElement):

    def __init__(self, config: ConfigTerrain, x: int, y: int):
        super().__init__(config.name, config.resource_max)
        self.config = config
        self.x = x
        self.y = y

    def is_alive(self) -> bool:
        # El terreno siempre se mantiene vivo
        return True
    
    def heal(self, amount: int) -> None:
      
        self.points = min(self.points + amount, self.config.resource_max)

    def regenerate(self) -> None:
        self.points = min(self.points + self.config.regen, self.config.resource_max)

    def __repr__(self) -> str:
        return (
            f"Terrain(name='{self.name}', pos=({self.x}, {self.y}), "
            f"points={self.points}/{self.config.resource_max})"
        )