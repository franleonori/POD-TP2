import csv
import json


class FuenteDatos:
    """Clase base: define el contrato que cumplen todas las fuentes."""

    def cargar(self, ruta):
        
        raise NotImplementedError("Cada fuente debe implementar cargar()")


class FuenteCSV(FuenteDatos):
    """Lee un archivo CSV y devuelve una lista de diccionarios."""

    def cargar(self, ruta):
        filas = []
        try:
            with open(ruta, "r", newline="", encoding="utf-8") as archivo:
                lector = csv.DictReader(archivo)
                for fila in lector:
                    filas.append(dict(fila))
        except FileNotFoundError:
            raise FileNotFoundError("No se encontró el archivo CSV: " + ruta)
        return filas


class FuenteJSON(FuenteDatos):
    """Lee un archivo JSON (lista de objetos) y devuelve una lista de diccionarios."""

    def cargar(self, ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                contenido = json.load(archivo)
        except FileNotFoundError:
            raise FileNotFoundError("No se encontró el archivo JSON: " + ruta)
        except json.JSONDecodeError:
            raise ValueError("El archivo JSON está mal formado: " + ruta)

    
        if not isinstance(contenido, list):
            raise ValueError("El JSON debe ser una lista de objetos: " + ruta)

        filas = []
        for elemento in contenido:
            if not isinstance(elemento, dict):
                raise ValueError("Cada elemento del JSON debe ser un objeto con campos")
            filas.append(elemento)
        return filas


def elegir_fuente(ruta):
    """Devuelve la fuente adecuada según la extensión del archivo."""
    ruta_minuscula = ruta.lower()
    if ruta_minuscula.endswith(".csv"):
        return FuenteCSV()
    if ruta_minuscula.endswith(".json"):
        return FuenteJSON()
    raise ValueError("Formato no soportado (use .csv o .json): " + ruta)
