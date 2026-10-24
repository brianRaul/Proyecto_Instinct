from world.terrain import Terrain
from world.objects import WorldObject
from world.creature import Creature


class Cell:

    def __init__(self, terrain: Terrain, x: int, y: int):
        
        #Crea una casilla. Nace con un terreno obligatorio.
        self.x = x
        self.y = y
        self.terrain = terrain
        
        # Inicialmente no hay ni objeto ni criatura
        self.world_object = None
        self.creature = None

    def can_place_object(self) -> bool:
        
        # Devuelve True si se puede colocar un objeto.
        # Solo se puede si la casilla NO tiene ya un objeto o una criatura.
        
        return self.world_object is None and self.creature is None

    def can_place_creature(self) -> bool:
        
        # Devuelve True si se puede colocar una criatura.
        # Solo se puede si la casilla NO tiene ya un objeto o una criatura.
        
        return self.world_object is None and self.creature is None

    def is_walkable(self) -> bool:

        # Devuelve True si una criatura puede caminar hacia/sobre esta casilla.
        # No se puede caminar si hay un objeto o si ya hay otra criatura.
        
        
        return self.world_object is None and self.creature is None

    def __repr__(self) -> str:
        return (
            f"Cell(pos=({self.x}, {self.y}), "
            f"terrain='{self.terrain.name}', "
            f"object={self.world_object.name if self.world_object else None}, "
            f"creature={self.creature.name if self.creature else None})"
        )