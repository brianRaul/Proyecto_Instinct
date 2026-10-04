# Módulo que define las configuraciones del mundo, se leen de los archivos .te, .ob y .map.
# Aqui solo guardamos informacion
from dataclasses import dataclass


@dataclass
class ConfigTerreno:
    name: str
    char: str
    resource_max: int
    regen: int


@dataclass
class ConfigObjeto:
    name: str
    char: str
    resource_max: int


@dataclass
class ConfigMapa:
    name: str
    grilla: list[list[str]]
