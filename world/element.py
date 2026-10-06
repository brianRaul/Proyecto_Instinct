# Todo lo que ocupa una casilla del mundo (terrenos, objetos, criaturas)
# hereda de esta clase.


from abc import ABC, abstractmethod


class ElementoMundo(ABC):

    def __init__(self, nombre: str, puntos: int):
        self.nombre = nombre
        self.puntos = puntos

    def recibir_dano(self, cantidad: int) -> None:
        self.puntos -= cantidad

    @abstractmethod
    def esta_vivo(self) -> bool:

        pass

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(nombre='{self.nombre}', puntos={self.puntos})"
        )
