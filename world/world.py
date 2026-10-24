from typing import List, Optional
from world.cell import Cell
from world.terrain import Terrain
from world.creature import Creature
from world.objects import WorldObject
from world.configs import ConfigTerrain


class World:

    def __init__(self, width: int, height: int, default_terrain_config: ConfigTerrain):

        self.width = width
        self.height = height
        
        # Creamos una matriz bidimensional  de Casillas
        self.grid: List[List[Cell]] = []
        
        for y in range(height):
            row = []
            for x in range(width):
                # Creamos un terreno nuevo para cada casilla (con su propia reserva)
                terrain = Terrain(config=default_terrain_config, x=x, y=y)
                # Creamos la casilla con ese terreno
                cell = Cell(terrain=terrain, x=x, y=y)
                row.append(cell)
            self.grid.append(row)

    def is_valid_position(self, x: int, y: int) -> bool:
        
        #Comprueba si una coordenada está dentro de los límites del mapa.
        
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        
        #Devuelve la casilla en (x, y). 
        #Si la posición está fuera del mapa, devuelve None.
        
        if self.is_valid_position(x, y):
            return self.grid[y][x]
        return None

    def get_all_creatures(self) -> List[Creature]:
        
        #Recorre el mapa y devuelve una lista con todas las criaturas vivas.
        #(El simulador usará esto para darles el turno).
        
        creatures = []
        for row in self.grid:
            for cell in row:
                if cell.creature is not None:
                    creatures.append(cell.creature)
        return creatures

    def regenerate_terrains(self) -> None:
        
        #Recorre todas las casillas y hace que los terrenos regeneren puntos.
        #(Se llama al final de cada tick).
        
        for row in self.grid:
            for cell in row:
                cell.terrain.regenerate()

    def remove_dead_entities(self) -> None:
        
        #Limpia el mapa: elimina criaturas y objetos que ya no están vivos.
        #(Se llama al final de cada tick).
        
        for row in self.grid:
            for cell in row:
                # Si hay una criatura y está muerta, la borramos de la casilla
                if cell.creature is not None and not cell.creature.is_alive():
                    cell.creature = None
                
                # Si hay un objeto y está muerto, lo borramos
                if cell.world_object is not None and not cell.world_object.is_alive():
                    cell.world_object = None

    def __repr__(self) -> str:
        return f"World(width={self.width}, height={self.height})"