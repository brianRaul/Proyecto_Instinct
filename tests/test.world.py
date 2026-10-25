import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from world.configs import ConfigTerrain, ConfigObject
from world.world import World
from world.creature import Creature
from world.objects import WorldObject

def run_tests():
    print("Iniciando pruebas de la clase World...\n")

    # Preparamos la receta base
    c_grass = ConfigTerrain(name="Grass", char=".", resource_max=100, regen=2)
    
    # --- Test 1: Creación del mapa ---
    print("1. Probando creación de World (5x4)...")
    world = World(width=5, height=4, default_terrain_config=c_grass)
    assert world.width == 5
    assert world.height == 4
    assert len(world.grid) == 4          # 4 filas
    assert len(world.grid[0]) == 5       # 5 columnas
    print(" Mapa 5x4 creado correctamente.\n")

    # --- Test 2: Límites del mapa ---
    print("2. Probando límites del mapa...")
    assert world.is_valid_position(0, 0) == True
    assert world.is_valid_position(4, 3) == True
    assert world.is_valid_position(5, 0) == False # Fuera de ancho
    assert world.is_valid_position(0, 4) == False # Fuera de alto
    assert world.get_cell(-1, 0) is None
    print("Los límites funcionan correctamente.\n")

    # --- Test 3: Obtener casillas ---
    print("3. Probando obtener casillas...")
    cell = world.get_cell(2, 2)
    assert cell is not None
    assert cell.x == 2 and cell.y == 2
    assert cell.terrain.name == "Grass"
    print("Obtención de casillas correcta.\n")

    # --- Test 4: Regeneración de terrenos ---
    print("4. Probando regeneración global de terrenos...")
    # Dañamos el terreno de la casilla (0,0) y (1,1)
    world.get_cell(0, 0).terrain.receive_damage(50)
    world.get_cell(1, 1).terrain.receive_damage(50)
    
    world.regenerate_terrains()
    
    # Como regen es 2, debería haber subido de 50 a 52
    assert world.get_cell(0, 0).terrain.points == 52
    assert world.get_cell(1, 1).terrain.points == 52
    print("Regeneración de terrenos correcta.\n")

    # --- Test 5: Limpieza de muertos ---
    print("5. Probando eliminación de entidades muertas...")
    # Ponemos una criatura y le quitamos toda la vida
    c_uruk = Creature(species="Uruk", faction="isengard", x=0, y=0, health=10, vision=5, lifespan=100)
    c_uruk.receive_damage(10) # Muere
    world.get_cell(0, 0).creature = c_uruk
    
    # Ponemos un objeto y le quitamos toda la vida
    c_rock = ConfigObject(name="Rock", char="#", resource_max=10)
    obj = WorldObject(config=c_rock, x=0, y=0)
    obj.receive_damage(10) # Muere
    world.get_cell(0, 0).world_object = obj

    # Al principio están en la casilla
    assert world.get_cell(0, 0).creature is not None
    assert world.get_cell(0, 0).world_object is not None

    # El mundo limpia los muertos
    world.remove_dead_entities()

    # Ahora deben ser None
    assert world.get_cell(0, 0).creature is None
    assert world.get_cell(0, 0).world_object is None
    print("Eliminación de entidades muertas correcta.\n")

    print("¡TODAS LAS PRUEBAS DE WORLD PASARON CON ÉXITO!")

if __name__ == "__main__":
    run_tests()