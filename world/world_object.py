from world.element import ElementoMundo
from world.configs import ConfigObjeto


class WorldObject(ElementoMundo):


    def __init__(self, config: ConfigObjeto, x: int, y: int):

        # El padre crea nombre y puntos
        super().__init__(config.name, config.resource_max)

        # La receta (no cambia)
        self.config = config

        # La posición (no cambia)
        self.x = x
        self.y = y

    def esta_vivo(self) -> bool:

        return self.puntos > 0

    def __repr__(self) -> str:
        return (
            f"WorldObject(nombre='{self.nombre}', "
            f"pos=({self.x}, {self.y}), "
            f"puntos={self.puntos}/{self.config.resource_max})"
        )