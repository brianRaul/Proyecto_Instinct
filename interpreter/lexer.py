from errores import ErrorDeCompilacion

class Token:
    def __init__(self, tipo, valor, linea):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea

    def __repr__(self):
        return f"Token({self.tipo}, {self.valor}, línea {self.linea})"

PALABRAS_RESERVADAS = {
    "if",
    "goto",
    "and",
    "or",
    "not"
}

OPERADORES = {
    "+",
    "-",
    "*",
    "/",
    "%",
    "<",
    "<=",
    ">",
    ">=",
    "==",
    "!="
}

class Lexer:
    def __init__(self, codigo):
        self.codigo = codigo
        self.posicion = 0
        self.linea = 1

    def leer_identificador(self):
        inicio = self.posicion

        while (self.posicion < len(self.codigo)
               and ((self.codigo[self.posicion].isalpha() or self.codigo[self.posicion] == "_")
                    or self.codigo[self.posicion].isdigit())):
            self.posicion += 1

        palabra = self.codigo[inicio:self.posicion]

        if palabra in PALABRAS_RESERVADAS:
            tipo_token = palabra.upper()
        else:
            tipo_token = "IDENTIFICADOR"

        return Token(tipo_token, palabra, self.linea)

    def leer_numero(self):
        inicio = self.posicion

        while (self.posicion < len(self.codigo)
               and self.codigo[self.posicion].isdigit()):
            self.posicion += 1

        numero = int(self.codigo[inicio:self.posicion])

        return Token("NUMERO", numero, self.linea)

    def leer_cadena(self):
        self.posicion += 1  # Saltar la comilla de apertura
        inicio = self.posicion

        while (self.posicion < len(self.codigo)
               and self.codigo[self.posicion] != '"'):

            if self.codigo[self.posicion] == "\n":
                raise ErrorDeCompilacion("Cadena de texto sin cerrar", self.linea)

            self.posicion += 1

        if self.posicion >= len(self.codigo):
            raise ErrorDeCompilacion("Cadena de texto sin cerrar", self.linea)

        texto = self.codigo[inicio:self.posicion]
        self.posicion += 1  # Saltar la comilla de cierre

        return Token("CADENA", texto, self.linea)

    def leer_operador(self):
        operador = self.codigo[self.posicion:self.posicion + 2]

        # Primero se comprueban los operadores de dos caracteres
        if operador in OPERADORES:
            self.posicion += 2
            return Token("OPERADOR", operador, self.linea)

        # Luego los de un carácter
        operador = self.codigo[self.posicion]

        if operador == "=":
            token = Token("ASIGNACION", operador, self.linea)
        elif operador in OPERADORES:
            token = Token("OPERADOR", operador, self.linea)
        else:
            raise ErrorDeCompilacion(f"Operador desconocido: {operador}", self.linea)

        self.posicion += 1
        return token

    def tokenizar(self):
        tokens = []

        while self.posicion < len(self.codigo):
            caracter = self.codigo[self.posicion]

            # 1. Ignorar espacios y tabuladores
            if caracter in " \t":
                self.posicion += 1

            # 2. Manejar saltos de línea
            elif caracter == "\n":
                tokens.append(Token("NUEVA_LINEA", None, self.linea))
                self.posicion += 1
                self.linea += 1

            # 3. Ignorar comentarios
            elif caracter == "#":
                while (self.posicion < len(self.codigo)
                       and self.codigo[self.posicion] != "\n"):
                    self.posicion += 1

            # 4. Leer identificadores
            elif caracter.isalpha() or caracter == "_":
                tokens.append(self.leer_identificador())

            # 5. Leer números
            elif caracter.isdigit():
                tokens.append(self.leer_numero())

            # 6. Leer cadenas de texto
            elif caracter == '"':
                tokens.append(self.leer_cadena())

            # 7. Leer operadores
            elif caracter in "+-*/%<>=!":
                tokens.append(self.leer_operador())

            # 8. Leer símbolos especiales
            elif caracter in "(),:":
                tokens.append(Token("SIMBOLO", caracter, self.linea))
                self.posicion += 1

            # 9. Carácter inesperado
            else:
                raise ErrorDeCompilacion(
                    f"Caracter inesperado: {caracter}", self.linea
                )

        tokens.append(Token("FIN", None, self.linea))
        return tokens


def tokenizar(codigo):
    return Lexer(codigo).tokenizar()