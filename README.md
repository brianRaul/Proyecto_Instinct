# Proyecto Instinct

Simulador de criaturas programadas en el lenguaje Instinct.

## Descripción

Este proyecto implementa:

1. Un compilador e intérprete del lenguaje Instinct.
2. Un mundo simulado en una grilla 2D con criaturas, terrenos y objetos.
3. Una aplicación visual para observar y controlar la simulación.

## Estructura

- `data/` → Archivos de datos (.te, .ob, .map, .ins).
- `interpreter/` → Compilador e intérprete de Instinct.
- `world/` → Mundo simulado (grilla, criaturas, ticks).
- `ui/` → Interfaz visual.
- `tests/` → Pruebas.

## Cómo ejecutar

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py

## Autor

- Brian R. López Pérez
- Leonardo 