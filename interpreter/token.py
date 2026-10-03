from dataclasses import dataclass
from typing import Any

@dataclass
class Token:
    tipo: str
    valor: Any
    linea: int
