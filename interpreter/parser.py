from errores import ErrorDeCompilacion
from nodos import (Numero, Cadena, Variable, Unaria, Binaria, Llamada,
                   Asignacion, Accion, Goto, SiGoto, Programa)

# GRAMÁTICA DEL LENGUAJE INSTINCT 
#
# Notación:  'texto' = palabra o símbolo literal
#            MAYÚSCULAS = tipo de token que entrega el lexer
#            [ x ] = opcional      { x } = se repite 0 o más veces
#            a | b = a o b
#
#   1. ESTRUCTURA DEL ARCHIVO
#
#   archivo        := cabecera cuerpo FIN
#
#   cabecera       := { NUEVA_LINEA | linea_cabecera }
#                     (la cabecera termina al aparecer 'start' ':')
#   linea_cabecera := clave valor fin_linea
#   clave          := 'creature' | 'faction' | 'health' | 'vision' | 'lifespan'
#   valor          := IDENTIFICADOR     (para creature y faction)
#                   | NUMERO            (para health, vision y lifespan; >= 1)
#
#   Reglas de la cabecera: la primera línea no vacía es 'creature Nombre';
#   las otras cuatro claves van en cualquier orden; las cinco son
#   obligatorias y ninguna puede repetirse.
#
#   2. EL CUERPO: una instrucción por línea
#
#   cuerpo         := 'start' ':' fin_linea { linea }
#   linea          := fin_linea                              (línea vacía)
#                   | etiqueta | salto | salto_cond | asignacion | accion
#
#   etiqueta       := IDENTIFICADOR ':' fin_linea
#   salto          := 'goto' IDENTIFICADOR fin_linea
#   salto_cond     := 'if' expresion 'goto' IDENTIFICADOR fin_linea
#   asignacion     := IDENTIFICADOR '=' expresion fin_linea
#   accion         := IDENTIFICADOR '(' [ expresion { ',' expresion } ] ')'
#                     fin_linea
#   fin_linea      := NUEVA_LINEA | FIN
#
#   (los comentarios '#' ya los eliminó el lexer)
#
#   3. EXPRESIONES: siete niveles, de MENOR a MAYOR precedencia 
#
#   nivel  operadores        regla                                  función
#   -----  ----------------  -------------------------------------  ----------------------
#     1    or                or_expr  := and_expr { 'or' and_expr }   parsear_or
#     2    and               and_expr := comp { 'and' comp }         parsear_and
#     3    < <= > >= == !=   comp     := suma { OP_COMP suma }       parsear_comparacion
#     4    + -               suma     := producto { ('+'|'-') producto }
#                                                                     parsear_suma
#     5    * / %             producto := unario { ('*'|'/'|'%') unario }
#                                                                     parsear_producto
#     6    - (unario), not   unario   := ('-' | 'not') unario | primario
#                                                                     parsear_unario
#     7    (base)            primario := NUMERO | CADENA | IDENTIFICADOR
#                                      | IDENTIFICADOR '(' [args] ')'
#                                      | '(' expresion ')'           parsear_primario
#
#   expresion := or_expr       (parsear_expresion, la puerta de entrada)
#
#   Todos los operadores binarios agrupan de izquierda a derecha.
#   Cada nivel pide sus operandos al nivel inmediatamente más fuerte:
#   por eso lo que tiene mayor precedencia queda más abajo en el árbol.
#
#   QUÉ COMPRUEBA ESTE PARSER (errores de compilación) 
#   * línea que no encaja en ninguna forma válida
#   * expresión mal formada
#   * etiqueta duplicada o etiqueta usada que no existe
#   * falta alguna de las cinco claves de la cabecera, o falta 'start:'
#   * valor inválido en la cabecera
#
#   QUÉ QUEDA PARA EL ANÁLISIS SEMÁNTICO (necesita el catálogo)
#   * asignación a una percepción o a una constante
#   * acción o función con nombre desconocido
#   * acción o función con un número de argumentos distinto del esperado


CLAVES_CABECERA = ("creature", "faction", "health", "vision", "lifespan")
CLAVES_CON_NOMBRE = ("creature", "faction")  

def describir(token):
    #Texto legible de un token, para armar mensajes de error.
    if token.tipo == "FIN":
        return "el fin del archivo"
    if token.tipo == "NUEVA_LINEA":
        return "el fin de la línea"
    if token.tipo == "CADENA":
        return f'"{token.valor}"'
    return f"'{token.valor}'"

# el parser
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

        # estado que se va llenando al parsear el cuerpo
        self.instrucciones = []
        self.etiquetas = {}      # nombre : índice de la instrucción que le sigue
        self.saltos = []         # (nombre, línea) de cada goto, para validar al final

    # utilidades 

    def actual(self):
        #token que toca mirar ahora, sin consumirlo.
        return self.tokens[self.pos]

    def mirar(self, adelante=1):
        #token que está 'adelante' posiciones más allá, sin consumir nada.
        indice = min(self.pos + adelante, len(self.tokens) - 1)
        return self.tokens[indice]

    def avanzar(self):
        #devuelve el token actual y pasa al siguiente, nunca pasa del FIN.
        token = self.tokens[self.pos]
        if token.tipo != "FIN":
            self.pos += 1
        return token

    def es_tipo(self, *tipos):
        # El token actual es de alguno de estos tipos? 
        return self.actual().tipo in tipos

    def es_operador(self, *valores):
        # El token actual es un OPERADOR con alguno de estos valores?
        token = self.actual()
        return token.tipo == "OPERADOR" and token.valor in valores

    def es_simbolo(self, valor, token=None):
        # El token (por defecto el actual) es el SIMBOLO '(' , ')' , ',' o ':'?
        if token is None:
            token = self.actual()
        return token.tipo == "SIMBOLO" and token.valor == valor

    def esperar_simbolo(self, valor):
        #Consume el símbolo indicado o lanza error si no está.
        token = self.actual()
        if not self.es_simbolo(valor):
            raise ErrorDeCompilacion(
                f"Se esperaba '{valor}', pero se encontró {describir(token)}",
                token.linea
            )
        return self.avanzar()

    def esperar_tipo(self, tipo, que_se_esperaba):
        #Consume un token del tipo indicado o lanza error si no es de ese tipo.
        token = self.actual()
        if token.tipo != tipo:
            raise ErrorDeCompilacion(
                f"Se esperaba {que_se_esperaba}, pero se encontró {describir(token)}",
                token.linea
            )
        return self.avanzar()

    def esperar_fin_linea(self):
        #Una instrucción debe terminar en salto de línea o fin de archivo.
        token = self.actual()
        if token.tipo not in ("NUEVA_LINEA", "FIN"):
            raise ErrorDeCompilacion(
                f"Línea que no encaja en ninguna forma válida: sobra {describir(token)}",
                token.linea
            )
        self.avanzar()

   
    # estructura del archivo
    def parsear_archivo(self):
        valores = self.parsear_cabecera()
        self.parsear_cuerpo()
        self.validar_saltos()

        return Programa(
            valores["creature"],
            valores["faction"],
            valores["health"],
            valores["vision"],
            valores["lifespan"],
            self.instrucciones,
            self.etiquetas
        )

    # cabecera

    def es_inicio_del_cuerpo(self):
        # Lo que viene es 'start' seguido de ':'?
        token = self.actual()
        siguiente = self.mirar()
        return (token.tipo == "IDENTIFICADOR"
                and token.valor == "start"
                and self.es_simbolo(":", siguiente))

    def parsear_cabecera(self):
        #Lee las líneas 'clave valor' hasta llegar a 'start:'. Devuelve un diccionario.
        valores = {}
        es_la_primera = True

        while not self.es_inicio_del_cuerpo():
            token = self.actual()

            if token.tipo == "NUEVA_LINEA":      # línea vacía o solo comentario
                self.avanzar()
                continue

            if token.tipo == "FIN":
                raise ErrorDeCompilacion("Falta la etiqueta 'start:'", token.linea)

            if token.tipo != "IDENTIFICADOR" or token.valor not in CLAVES_CABECERA:
                raise ErrorDeCompilacion(
                    f"Línea que no encaja en la cabecera: {describir(token)} no es una "
                    f"clave válida ({', '.join(CLAVES_CABECERA)})",
                    token.linea
                )

            if es_la_primera and token.valor != "creature":
                raise ErrorDeCompilacion(
                    "La primera línea debe ser 'creature Nombre'", token.linea
                )
            es_la_primera = False

            if token.valor in valores:
                raise ErrorDeCompilacion(
                    f"La clave '{token.valor}' está repetida", token.linea
                )

            self.avanzar()                                   # consume la clave
            valores[token.valor] = self.parsear_valor_cabecera(token)
            self.esperar_fin_linea()

        # Aquí el token actual es 'start': ya se puede comprobar que estén las cinco
        faltan = [clave for clave in CLAVES_CABECERA if clave not in valores]
        if faltan:
            raise ErrorDeCompilacion(
                f"Faltan claves en la cabecera: {', '.join(faltan)}",
                self.actual().linea
            )

        return valores

    def parsear_valor_cabecera(self, token_clave):
        clave = token_clave.valor
        valor = self.actual()

        if clave in CLAVES_CON_NOMBRE:
            if valor.tipo != "IDENTIFICADOR":
                raise ErrorDeCompilacion(
                    f"Valor inválido para '{clave}': se esperaba un nombre, "
                    f"pero se encontró {describir(valor)}",
                    valor.linea
                )
            self.avanzar()
            return valor.valor

        # health > 0, vision >= 1, lifespan > 0: con enteros, las tres son "al menos 1"
        if valor.tipo != "NUMERO":
            raise ErrorDeCompilacion(
                f"Valor inválido para '{clave}': se esperaba un entero, "
                f"pero se encontró {describir(valor)}",
                valor.linea
            )
        if valor.valor < 1:
            raise ErrorDeCompilacion(
                f"Valor inválido para '{clave}': debe ser al menos 1", valor.linea
            )
        self.avanzar()
        return valor.valor

    # cuerpo 

    def parsear_cuerpo(self):
        #Lee línea por línea hasta el FIN. Llena self.instrucciones y self.etiquetas.
        while not self.es_tipo("FIN"):
            if self.es_tipo("NUEVA_LINEA"):      # línea vacía o solo comentario
                self.avanzar()
                continue

            instruccion = self.parsear_linea()

            # Las etiquetas devuelven None: ya se registraron solas
            if instruccion is not None:
                self.instrucciones.append(instruccion)

    def parsear_linea(self):
        #Decide qué forma de línea es mirando cómo empieza.
        token = self.actual()

        if token.tipo == "IF":
            return self.parsear_if_goto()

        if token.tipo == "GOTO":
            return self.parsear_goto()

        if token.tipo == "IDENTIFICADOR":
            # Hay que mirar el SIGUIENTE token para distinguir las tres formas
            siguiente = self.mirar()

            if self.es_simbolo(":", siguiente):
                return self.parsear_etiqueta()

            if siguiente.tipo == "ASIGNACION":
                return self.parsear_asignacion()

            if self.es_simbolo("(", siguiente):
                return self.parsear_accion()

        raise ErrorDeCompilacion(
            f"Línea que no encaja en ninguna forma válida (empieza con {describir(token)})",
            token.linea
        )

    def parsear_etiqueta(self):
        nombre = self.avanzar()          # el identificador
        self.avanzar()                   # el ':'

        if nombre.valor in self.etiquetas:
            raise ErrorDeCompilacion(
                f"Etiqueta duplicada: '{nombre.valor}'", nombre.linea
            )

        # La etiqueta apunta a la PRÓXIMA instrucción que se agregue
        self.etiquetas[nombre.valor] = len(self.instrucciones)

        self.esperar_fin_linea()
        return None

    def parsear_goto(self):
        palabra = self.avanzar()         # 'goto'
        destino = self.esperar_tipo("IDENTIFICADOR", "el nombre de una etiqueta")
        self.esperar_fin_linea()

        self.saltos.append((destino.valor, destino.linea))
        return Goto(destino.valor, palabra.linea)

    def parsear_if_goto(self):
        palabra = self.avanzar()         # 'if'
        condicion = self.parsear_expresion()
        self.esperar_tipo("GOTO", "'goto' después de la condición")
        destino = self.esperar_tipo("IDENTIFICADOR", "el nombre de una etiqueta")
        self.esperar_fin_linea()

        self.saltos.append((destino.valor, destino.linea))
        return SiGoto(condicion, destino.valor, palabra.linea)

    def parsear_asignacion(self):
        nombre = self.avanzar()          # el identificador
        self.avanzar()                   # el '='
        expresion = self.parsear_expresion()
        self.esperar_fin_linea()

        return Asignacion(nombre.valor, expresion, nombre.linea)

    def parsear_accion(self):
        nombre = self.avanzar()          # el identificador
        llamada = self.parsear_llamada(nombre)
        self.esperar_fin_linea()

        return Accion(llamada.nombre, llamada.argumentos, llamada.linea)

    def validar_saltos(self):
        #Todo goto debe apuntar a una etiqueta que exista en el archivo.
        for nombre, linea in self.saltos:
            if nombre not in self.etiquetas:
                raise ErrorDeCompilacion(f"La etiqueta '{nombre}' no existe", linea)

    
    # EXPRESIONES  (sección 3 de la gramática: siete niveles)
    def parsear_expresion(self):
        # El nivel más débil es la puerta de entrada
        return self.parsear_or()

    # nivel 1: or 
    def parsear_or(self):
        izquierda = self.parsear_and()

        while self.es_tipo("OR"):
            operador = self.avanzar()
            derecha = self.parsear_and()
            izquierda = Binaria(operador.valor, izquierda, derecha, operador.linea)

        return izquierda

    #  nivel 2: and 
    def parsear_and(self):
        izquierda = self.parsear_comparacion()

        while self.es_tipo("AND"):
            operador = self.avanzar()
            derecha = self.parsear_comparacion()
            izquierda = Binaria(operador.valor, izquierda, derecha, operador.linea)

        return izquierda

    #  nivel 3: < <= > >= == != 
    def parsear_comparacion(self):
        izquierda = self.parsear_suma()

        while self.es_operador("<", "<=", ">", ">=", "==", "!="):
            operador = self.avanzar()
            derecha = self.parsear_suma()
            izquierda = Binaria(operador.valor, izquierda, derecha, operador.linea)

        return izquierda

    #  nivel 4: + - 
    def parsear_suma(self):
        izquierda = self.parsear_producto()

        while self.es_operador("+", "-"):
            operador = self.avanzar()
            derecha = self.parsear_producto()
            izquierda = Binaria(operador.valor, izquierda, derecha, operador.linea)

        return izquierda

    #  nivel 5: * / % 
    def parsear_producto(self):
        izquierda = self.parsear_unario()

        while self.es_operador("*", "/", "%"):
            operador = self.avanzar()
            derecha = self.parsear_unario()
            izquierda = Binaria(operador.valor, izquierda, derecha, operador.linea)

        return izquierda

    #  nivel 6: menos unario y not 
    def parsear_unario(self):
        # Si hay un prefijo (- o not), se consume y se vuelve a llamar a
        # esta misma función: así se permiten varios seguidos (- - 3, not not a)
        if self.es_operador("-") or self.es_tipo("NOT"):
            operador = self.avanzar()
            operando = self.parsear_unario()
            return Unaria(operador.valor, operando, operador.linea)

        return self.parsear_primario()

    #  nivel 7: lo que ya no se descompone 
    def parsear_primario(self):
        token = self.actual()

        if token.tipo == "NUMERO":
            self.avanzar()
            return Numero(token.valor, token.linea)

        if token.tipo == "CADENA":
            self.avanzar()
            return Cadena(token.valor, token.linea)

        if token.tipo == "IDENTIFICADOR":
            self.avanzar()

            # Si lo siguiente es '(' es una llamada: see(...), name(...)
            if self.es_simbolo("("):
                return self.parsear_llamada(token)

            return Variable(token.valor, token.linea)

        if self.es_simbolo("("):
            self.avanzar()                        # consume '('
            expresion = self.parsear_expresion()  # vuelve a empezar desde el nivel más débil
            self.esperar_simbolo(")")             # exige el ')'
            return expresion

        raise ErrorDeCompilacion(
            f"Expresión mal formada: no se esperaba {describir(token)}", token.linea
        )

    def parsear_llamada(self, token_nombre):
        # El nombre ya se consumió; aquí el token actual debe ser '('
        self.esperar_simbolo("(")
        argumentos = []

        if not self.es_simbolo(")"):
            argumentos.append(self.parsear_expresion())

            while self.es_simbolo(","):
                self.avanzar()
                argumentos.append(self.parsear_expresion())

        self.esperar_simbolo(")")
        return Llamada(token_nombre.valor, argumentos, token_nombre.linea)

def parsear_programa(codigo_tokenizado):
    #Compila el texto de un archivo .ins completo y devuelve un Programa.
    return Parser(codigo_tokenizado).parsear_archivo()