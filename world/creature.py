from world.element import WorldElement


class Creature(WorldElement):

    def __init__(
        self, 
        species: str, 
        faction: str, 
        x: int, 
        y: int, 
        health: int, 
        vision: int, 
        lifespan: int,
        ast=None 
    ):
        super().__init__(species, health)

        self.faction = faction
        self.x = x
        self.y = y

        self.age = 0
        self.lifespan = lifespan
        self.vision = vision

        self.ast = ast
        self.pc = 0                # Program counter
        self.variables = {}        # Memory

    def is_alive(self) -> bool:
        has_health = self.points > 0
        is_young = self.age < self.lifespan
        return has_health and is_young

    def __repr__(self) -> str:
        return (
            f"Creature(species='{self.name}', pos=({self.x}, {self.y}), "
            f"health={self.points}, age={self.age}/{self.lifespan})"
        )