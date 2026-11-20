import operator

# Un valor del lenguaje es un entero (int) o un texto (str).
def es_numero(valor):
    return type(valor) is int


def nombre_tipo(valor):
    return "número" if es_numero(valor) else "texto"


def es_verdadero(valor):
    """Son falsos el entero 0 y el texto vacío; todo lo demás es verdadero."""
    return valor != 0 and valor != ""


# Tablas: operador -> función de Python que lo calcula (en vez de un if por operador).
ARITMETICA = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.floordiv,   # división entera, como // en Python
    "%": operator.mod,
}
ORDEN = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge}
IGUALDAD = {"==": operator.eq, "!=": operator.ne}
