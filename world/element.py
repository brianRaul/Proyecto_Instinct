# Todo lo que ocupa una casilla del mundo (terrenos, objetos, criaturas)
# hereda de esta clase.

from abc import ABC, abstractmethod

class WorldElement(ABC): 
    def __init__(self, name: str, points: int):
        self.name = name
        self.points = points

    def receive_damage(self, amount: int) -> None:
        self.points -= amount

    @abstractmethod
    def is_alive(self) -> bool:
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', points={self.points})"