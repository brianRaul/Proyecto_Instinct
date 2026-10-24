# Módulo que define las configuraciones del mundo, se leen de los archivos .te, .ob y .map.
# Aqui solo guardamos informacion
from dataclasses import dataclass


@dataclass
class ConfigTerrain:
    name: str
    char: str
    resource_max: int
    regen: int


@dataclass
class ConfigObject:
    name: str
    char: str
    resource_max: int


@dataclass
class ConfigMap:
    name: str
    grid: list[list[str]]
