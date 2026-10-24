import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interpreter.token import Token
from world.configs import ConfigTerrain, ConfigObject, ConfigMap
from world.element import WorldElement
from world.terrain import Terrain
from world.objects import WorldObject
from world.creature import Creature

def run_tests():
    # --- 1. Probar Token ---
    print("1. Probando Token...")
    tok = Token(type="NUMBER", value=42, line=1)
    assert tok.type == "NUMBER"
    assert tok.value == 42
    assert tok.line == 1
    print("Token creado correctamente.\n")

    # --- 2. Probar Configuraciones ---
    print("2. Probando Configuraciones...")
    c_terrain = ConfigTerrain(name="Grass", char=".", resource_max=100, regen=2)
    c_object = ConfigObject(name="Rock", char="#", resource_max=100)
    c_map = ConfigMap(name="Plain", grid=[['.', '#'], ['.', '.']])
    assert c_terrain.name == "Grass"
    assert c_object.resource_max == 100
    assert len(c_map.grid) == 2
    print("Configuraciones creadas correctamente.\n")

    # --- 3. Probar Clase Abstracta ---
    print("3. Probando WorldElement (Clase Abstracta)...")
    try:
        elem = WorldElement(name="Test", points=10)
        assert False, "¡Error! WorldElement no debería poder instanciarse."
    except TypeError:
        print(" WorldElement no se puede instanciar (correcto).\n")

    # --- 4. Probar Terreno ---
    print("4. Probando Terrain...")
    t = Terrain(config=c_terrain, x=0, y=0)
    assert t.points == 100
    assert t.is_alive() == True
    
    t.receive_damage(30)
    assert t.points == 70
    
    t.regenerate()
    assert t.points == 72 # 70 + 2 de regen
    
    t.receive_damage(200) # Le quitamos muchísima vida
    assert t.is_alive() == True # El terreno nunca muere
    print("Terrain funciona correctamente.\n")

    # --- 5. Probar Objeto ---
    print("5. Probando WorldObject...")
    o = WorldObject(config=c_object, x=1, y=0)
    assert o.points == 100
    assert o.is_alive() == True
    
    o.receive_damage(100)
    assert o.points == 0
    assert o.is_alive() == False # El objeto SÍ muere
    print("WorldObject funciona correctamente.\n")

    # --- 6. Probar Criatura ---
    print("6. Probando Creature...")
    # Creamos una criatura de prueba
    uruk = Creature(
        species="Uruk", faction="isengard", x=2, y=2, 
        health=80, vision=6, lifespan=400
    )
    assert uruk.points == 80
    assert uruk.age == 0
    assert uruk.is_alive() == True
    
    # Probamos daño letal
    uruk.receive_damage(80)
    assert uruk.is_alive() == False # Muere por daño
    
    # Probamos muerte por vejez
    orc = Creature(
        species="Orc", faction="isengard", x=3, y=3, 
        health=100, vision=4, lifespan=10
    )
    orc.age = 10
    assert orc.is_alive() == False # Muere de viejo
    print("Creature funciona correctamente.\n")

    print("¡TODAS LAS PRUEBAS PASARON CON ÉXITO!")

if __name__ == "__main__":
    run_tests()