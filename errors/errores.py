class ErrorDeEjecucion(Exception):
    #Error que ocurre mientras la criatura ejecuta (la criatura muere).
    def __init__(self, mensaje, linea=None):
        self.mensaje = mensaje
        self.linea = linea
        super().__init__(f"Línea {linea}: {mensaje}" if linea is not None else mensaje)

class ErrorDeCompilacion(Exception):
    #Error en un archivo .ins (léxico, sintáctico o semántico).
    def __init__(self, mensaje, linea=None):
        self.mensaje = mensaje
        self.linea = linea

        if linea is None:
            super().__init__(mensaje)
        else:
            super().__init__(f"Línea {linea}: {mensaje}")