from pathlib import Path

class ErrorDeCarga(Exception):  #clase propia para errores
    def __init__(self, ruta, mensaje, linea=None):
        if linea is not None:
            texto = f"{ruta}, línea {linea}: {mensaje}"
        else:
            texto = f"{ruta}: {mensaje}"

        super().__init__(texto)

        self.ruta = ruta
        self.linea = linea
        self.mensaje = mensaje

#seccion 1, aqui se lee un archivo terreno, objeto o mapa y se valida

def leer_terreno(ruta):
    with open(ruta, 'r') as archivo:
        lineas = archivo.readlines()

    claves_obligatorias = ["terrain", "char", "resource_max", "regen"]
    claves_numericas = ["resource_max", "regen"]

    datos = {}

    for numero, linea in enumerate(lineas, start=1):
        linea = linea.strip()

        if linea == '' or linea.startswith('#'):
            continue

        partes = linea.split()
        if len(partes) != 2:
            raise ErrorDeCarga(ruta, f"se esperaba 'clave valor', se encontró: '{linea}'",linea=numero)

        clave, valor = partes[0], partes[1]

        if clave not in claves_obligatorias:
            raise ErrorDeCarga(ruta, f"la clave '{clave}' no está permitida",linea=numero)

        if clave in claves_numericas:
            try:
                valor = int(valor)
            except ValueError:
                raise ErrorDeCarga(ruta, f"'{valor}' no es un número válido para '{clave}'", linea=numero)

        datos[clave] = valor

    for clave in claves_obligatorias:
        if clave not in datos:
            raise ErrorDeCarga(ruta, f"falta la clave obligatoria '{clave}'")

    return datos

def leer_objeto(ruta):
    with open(ruta, 'r') as archivo:
        lineas = archivo.readlines()

    claves_obligatorias = ["object", "char", "resource_max"]
    claves_numericas = ["resource_max"]

    datos = {}

    for numero, linea in enumerate(lineas, start=1):
        linea = linea.strip()

        if linea == '' or linea.startswith('#'):
            continue

        partes = linea.split()
        if len(partes) != 2:
            raise ErrorDeCarga(ruta, f"se esperaba 'clave valor', se encontró: '{linea}'", linea=numero)

        clave, valor = partes[0], partes[1]

        if clave not in claves_obligatorias:
            raise ErrorDeCarga(ruta, f"la clave '{clave}' no está permitida", linea=numero)

        if clave in claves_numericas:
            try:
                valor = int(valor)
            except ValueError:
                raise ErrorDeCarga(ruta, f"'{valor}' no es un número válido para '{clave}'", linea=numero)

        datos[clave] = valor

    for clave in claves_obligatorias:
        if clave not in datos:
            raise ErrorDeCarga(ruta, f"falta la clave obligatoria '{clave}'")

    return datos

def leer_mapa(ruta, catalogo):
    with open(ruta, 'r') as archivo:
        lineas = archivo.readlines()

    if not lineas:
        raise ErrorDeCarga(ruta, f"el archivo está vacío")

    nombre = lineas[0].strip()
    lineas = lineas[1:]

    if not lineas:
        raise ErrorDeCarga(ruta, f"el mapa no tiene ninguna fila de casillas")

    largo_de_mapa = None
    grilla = []

    for numero, linea in enumerate(lineas, start=2):
        linea = linea.rstrip('\n')

        if linea == '':
            raise ErrorDeCarga(ruta, f"no se permiten líneas vacías dentro del mapa", linea=numero)

        if largo_de_mapa != None and len(linea) != largo_de_mapa:
            raise ErrorDeCarga(ruta, f"todas las filas deben tener la misma cantidad de caracteres", linea=numero)

        largo_de_mapa = len(linea)

        for char in linea:
            if char not in catalogo:
                raise ErrorDeCarga(ruta, f"hay un char inválido ('{char}')", linea=numero)

        grilla.append(linea)

    return {"nombre": nombre, "grilla": grilla}

#seccion 2, aqui se leen todos los terrenos y objetos y se recopilan los que pasan la seccion 1

def leer_terrenos(carpeta):
    carpeta = Path(carpeta)
    candidatos = []

    for archivo in sorted(carpeta.glob('*.te')):
        try:
            datos = leer_terreno(archivo)
            candidatos.append((archivo.name, datos))
        except ErrorDeCarga as error:
            print(f"Error en {archivo.name}: {error}")

    return candidatos

def leer_objetos(carpeta):
    carpeta = Path(carpeta)
    candidatos = []

    for archivo in sorted(carpeta.glob('*.ob')):
        try:
            datos = leer_objeto(archivo)
            candidatos.append((archivo.name, datos))
        except ErrorDeCarga as error:
            print(f"Error en {archivo.name}: {error}")

    return candidatos


#seccion 3, se define grass y rock con sus respectivos valores como base, se hace un proceso de seleccion para descartar archivos invalidos, se mantienen los q pasan y la base(aunque no hayan archivos que la definan)

BASE_TERRENO = {"terrain": "Grass", "char": ".", "resource_max": 100, "regen": 2}
BASE_OBJETO = {"object": "Rock", "char": "#", "resource_max": 100}

NOMBRES_RESERVADOS = {"Grass", "Rock"}
CHARS_RESERVADOS = {".", "#"}


# 1er filtro. deja pasar la base y lo que no se relacione con ella en nombre o char

def verificar_base(nombre_archivo, datos):   # Juzga un candidato. Si pasa, no hace nada, si no, lanza ErrorDeCarga.
    
    if "terrain" in datos:
        base = BASE_TERRENO
    else:
        base = BASE_OBJETO

    if datos == base:
        return  # es la base exacta: se acepta y la función termina aquí

    if "terrain" in datos:
        nombre=datos["terrain"]
    else:
        nombre=datos["object"]

    # No es la base exacta, pero usa el nombre Grass o Rock
    if nombre in NOMBRES_RESERVADOS:
        raise ErrorDeCarga(nombre_archivo, f"'{nombre}' es un nombre de la base y sus valores no coinciden con los oficiales")

    # No usa un nombre reservado, pero quiere el char de la base (. o #).
    if datos["char"] in CHARS_RESERVADOS:
        raise ErrorDeCarga(nombre_archivo, f"el char '{datos['char']}' está reservado para la base")


def filtrar_base(candidatos):    # Aplica verificar_base a cada candidato, descarta los archivos que usan un nombre o char de una base y no son base
     
    sobrevivientes = []

    for nombre_archivo, datos in candidatos:
        try:
            verificar_base(nombre_archivo, datos)
            sobrevivientes.append((nombre_archivo, datos))
        except ErrorDeCarga as error:
            print(f"Error: {error}")

    return sobrevivientes


# 2do filtro. lidia con duplicados exactos

def quitar_duplicados_identicos(candidatos):  # Si dos archivos declaran exactamente lo mismo, es el mismo elemento dos veces. Se conserva uno y el otro se descarta dando un aviso(no hay conflicto)
    
    vistos = []
    sobrevivientes = []

    for nombre_archivo, datos in candidatos:
        if datos in vistos:  # compara por contenido con cada diccionario ya visto
            print(f"Aviso: {nombre_archivo} repite exactamente la definición de otro archivo; se ignora")
            continue

        vistos.append(datos)
        sobrevivientes.append((nombre_archivo, datos))

    return sobrevivientes


# 3er filtro. rechaza archivos con mismo nombre o mismo char

def quitar_conflictos(candidatos):  
    # Primera pasada: agrupar. Para cada nombre y cada char, qué archivos lo declaran.    
    por_nombre = {}
    por_char = {}

    for nombre_archivo, datos in candidatos:

        if "terrain" in datos:
            nombre=datos["terrain"]
        else:
            nombre=datos["object"]

        char = datos["char"]

        if nombre not in por_nombre:
            por_nombre[nombre] = []
        por_nombre[nombre].append(nombre_archivo)

        if char not in por_char:
            por_char[char] = []
        por_char[char].append(nombre_archivo)

    # Segunda pasada: si un nombre o un char lo declaran 2 o más archivos, se rechazan todos.
    # Se reporta una vez por grupo, no una vez por archivo.
    rechazados = set()

    for nombre, archivos in por_nombre.items():
        if len(archivos) > 1:
            print(f"Conflicto: el nombre '{nombre}' lo declaran {', '.join(archivos)}; se rechazan todos")
            rechazados.update(archivos)  

    for char, archivos in por_char.items():
        if len(archivos) > 1:
            print(f"Conflicto: el char '{char}' lo declaran {', '.join(archivos)}; se rechazan todos")
            rechazados.update(archivos)

    # Se queda solo el que no fue rechazado.
    sobrevivientes = []
    for nombre_archivo, datos in candidatos:
        if nombre_archivo not in rechazados:
            sobrevivientes.append((nombre_archivo, datos))

    return sobrevivientes


# asegurar base, si no existen archivos grass o rock validos, se usan los valores incorporados(avisando por supuesto)

def existe(candidatos, clave, nombre):  # se usa mas adelante para comprobar si hay algún candidato cuya clave sea "terrain" u "object"
    
    for nombre_archivo, datos in candidatos:
        if clave in datos and datos[clave] == nombre:
            return True
    return False


def asegurar_base(candidatos):  
    resultado = list(candidatos)  # copia, para no modificar la lista que nos pasaron

    if not existe(resultado, "terrain", "Grass"):
        print("Aviso: no hay un terreno Grass válido; se usa la versión incorporada")
        resultado.append(("(incorporado)", dict(BASE_TERRENO)))  # dict(...) copia la constante

    if not existe(resultado, "object", "Rock"):
        print("Aviso: no hay un objeto Rock válido; se usa la versión incorporada")
        resultado.append(("(incorporado)", dict(BASE_OBJETO)))

    return resultado


# seccion 4 se cargan terrenos, objetos y mapas validos

def armar(candidatos):  # devuelve los terrenos y objetos ya filtrados

    terrenos = {}
    objetos = {}

    for nombre_archivo, datos in candidatos:
        if "terrain" in datos:
            terrenos[datos["terrain"]] = datos
        else:
            objetos[datos["object"]] = datos

    return terrenos, objetos


def catalogo_chars(terrenos, objetos):

    catalogo = {}

    for datos in terrenos.values():
        catalogo[datos["char"]] = ("terrain", datos["terrain"])

    for datos in objetos.values():
        catalogo[datos["char"]] = ("object", datos["object"])

    return catalogo


def cargar_mapas(carpeta, catalogo):
    carpeta = Path(carpeta)
    mapas = {}

    for archivo in sorted(carpeta.glob("*.map")):      
        try:
            datos = leer_mapa(archivo, catalogo)
            if datos["nombre"] in mapas:
                print(f"Error en {archivo.name}: Ya existe un mapa con el nombre '{datos['nombre']}'")
                continue
            mapas[datos["nombre"]] = datos      
        except ErrorDeCarga as error:
            print(f"Error en {archivo.name}: {error}")

    return mapas



# seccion 5 cargar terrenos, objetos y mapas

def cargar_repositorio(carpeta_base):
    carpeta_base = Path(carpeta_base)

    # 1. Leer, cada archivo se valida solo y se guarda en candidatos
    candidatos_terrenos = leer_terrenos(carpeta_base / "terrains")
    candidatos_objetos = leer_objetos(carpeta_base / "objects")
    candidatos = candidatos_terrenos + candidatos_objetos  

    # 2. Filtrar, en el orden previsto
    candidatos = filtrar_base(candidatos)
    candidatos = quitar_duplicados_identicos(candidatos)
    candidatos = quitar_conflictos(candidatos)
    candidatos = asegurar_base(candidatos)

    # 3. Armar con lo que sobrevivió
    terrenos, objetos = armar(candidatos)
    catalogo = catalogo_chars(terrenos, objetos)
    mapas = cargar_mapas(carpeta_base / "maps", catalogo)

    return terrenos, objetos, mapas


# t, o, m = cargar_repositorio('')
# print(t, o, m)