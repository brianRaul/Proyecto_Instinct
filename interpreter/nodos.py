from errors.errores import ErrorDeEjecucion
from ejecución import (es_numero, es_verdadero, nombre_tipo,
                          ARITMETICA, ORDEN, IGUALDAD)

# nodos de expresion
class Numero:
    def __init__(self, valor, linea):
        self.valor = valor
        self.linea = linea

    def __repr__(self):
        return str(self.valor)

    def evaluar(self, ctx):
        return self.valor


class Cadena:
    def __init__(self, valor, linea):
        self.valor = valor
        self.linea = linea

    def __repr__(self):
        return f'"{self.valor}"'

    def evaluar(self, ctx):
        return self.valor


class Variable:
    def __init__(self, nombre, linea):
        self.nombre = nombre
        self.linea = linea

    def __repr__(self):
        return self.nombre

    def evaluar(self, ctx):
        # constante, percepción o variable propia: lo decide el contexto
        return ctx.leer(self.nombre, self.linea)


class Unaria:
    def __init__(self, operador, operando, linea):
        self.operador = operador
        self.operando = operando
        self.linea = linea

    def __repr__(self):
        return f"({self.operador} {self.operando})"

    def evaluar(self, ctx):
        valor = self.operando.evaluar(ctx)
        if self.operador == "not":
            return 0 if es_verdadero(valor) else 1
        # menos unario
        if not es_numero(valor):
            raise ErrorDeEjecucion("El menos unario solo acepta números", self.linea)
        return -valor


class Binaria:
    def __init__(self, operador, izquierda, derecha, linea):
        self.operador = operador
        self.izquierda = izquierda
        self.derecha = derecha
        self.linea = linea

    def __repr__(self):
        return f"({self.izquierda} {self.operador} {self.derecha})"

    def evaluar(self, ctx):
        if self.operador in ("and", "or"):
            return self.evaluar_logico(ctx)

        izquierda = self.izquierda.evaluar(ctx)
        derecha = self.derecha.evaluar(ctx)

        # todos los operadores (salvo los lógicos) exigen el mismo tipo en los dos lados
        if type(izquierda) is not type(derecha):
            raise ErrorDeEjecucion(
                f"No se puede usar '{self.operador}' entre un {nombre_tipo(izquierda)} "
                f"y un {nombre_tipo(derecha)}", self.linea)

        if self.operador in IGUALDAD:                 # == y != valen para números y texto
            return int(IGUALDAD[self.operador](izquierda, derecha))

        if not es_numero(izquierda):                  # el resto solo acepta números
            raise ErrorDeEjecucion(f"El operador '{self.operador}' solo acepta números",
                                   self.linea)
        if self.operador in ORDEN:
            return int(ORDEN[self.operador](izquierda, derecha))

        if self.operador in ("/", "%") and derecha == 0:
            raise ErrorDeEjecucion("División por cero", self.linea)
        return ARITMETICA[self.operador](izquierda, derecha)

    def evaluar_logico(self, ctx):
        # and / or no comparan tipos: solo miran si cada lado es verdadero o falso.
        # Cortocircuito: si el izquierdo ya decide, el derecho no se evalúa.
        izquierda = es_verdadero(self.izquierda.evaluar(ctx))
        if self.operador == "and":
            return int(izquierda and es_verdadero(self.derecha.evaluar(ctx)))
        return int(izquierda or es_verdadero(self.derecha.evaluar(ctx)))


class Llamada:
    def __init__(self, nombre, argumentos, linea):
        self.nombre = nombre
        self.argumentos = argumentos
        self.linea = linea

    def __repr__(self):
        args = ", ".join(repr(a) for a in self.argumentos)
        return f"{self.nombre}({args})"

    def evaluar(self, ctx):
        valores = [argumento.evaluar(ctx) for argumento in self.argumentos]
        return ctx.llamar(self.nombre, valores, self.linea)

# nodos de instrucción
class Asignacion:
    def __init__(self, nombre, expresion, linea):
        self.nombre = nombre
        self.expresion = expresion
        self.linea = linea

    def __repr__(self):
        return f"{self.nombre} = {self.expresion}"


class Goto:
    def __init__(self, etiqueta, linea):
        self.etiqueta = etiqueta
        self.linea = linea

    def __repr__(self):
        return f"goto {self.etiqueta}"
    

class IfGoto:
    def __init__(self, condicion, etiqueta, linea):
        self.condicion = condicion
        self.etiqueta = etiqueta
        self.linea = linea

    def __repr__(self):
        return f"if {self.condicion} goto {self.etiqueta}"


class Accion:
    def __init__(self, nombre, argumentos, linea):
        self.nombre = nombre
        self.argumentos = argumentos
        self.linea = linea

    def __repr__(self):
        args = ", ".join(repr(a) for a in self.argumentos)
        return f"{self.nombre}({args})"


class Programa:
    def __init__(self, nombre, faccion, vida, vision, esperanza_vida,
                 instrucciones, etiquetas):
        self.nombre = nombre
        self.faccion = faccion
        self.vida = vida
        self.vision = vision
        self.esperanza_vida = esperanza_vida
        self.instrucciones = instrucciones   # lista de Asignacion/Goto/IFGoto/Accion
        self.etiquetas = etiquetas           # dict: nombre : índice en instrucciones

    def __repr__(self):
        lineas = [
            f"criatura {self.nombre} | facción={self.faccion} | vida={self.vida} "
            f"| visión={self.vision} | esperanza_vida={self.esperanza_vida}"
        ]

        # índice : nombres de las etiquetas que apuntan a él
        inverso = {}
        for nombre, indice in self.etiquetas.items():
            inverso.setdefault(indice, []).append(nombre)

        for i, instruccion in enumerate(self.instrucciones):
            for nombre in inverso.get(i, []):
                lineas.append(f"{nombre}:")
            lineas.append(f"  [{i:2}] (línea {instruccion.linea}) {instruccion}")

        # etiquetas que quedaron al final, sin instrucción después
        for nombre in inverso.get(len(self.instrucciones), []):
            lineas.append(f"{nombre}:")

        return "\n".join(lineas)