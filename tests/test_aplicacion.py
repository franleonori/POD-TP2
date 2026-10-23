import os
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))

import fuentes
import main
import modelo
import pipeline

RUTA_CSV = os.path.join(RAIZ, "data", "puertos.csv")
RUTA_JSON = os.path.join(RAIZ, "data", "puertos.json")




def crear_puerto(codigo="SR01-P01-05", piso="1", estado="libre",
                 equipo="", cable="Cat6", ultima_revision="2026-03-10"):
    """Crea un PuertoRed válido. Cada prueba cambia solo el dato que quiere
    probar, usando los valores por defecto para el resto."""
    return modelo.PuertoRed(codigo, piso, estado, equipo, cable, ultima_revision)


def crear_fila(codigo="SR01-P01-05", piso="1", estado="libre",
               equipo="", cable="Cat6", ultima_revision="2026-03-10"):
    """Igual que crear_puerto, pero devuelve un diccionario (una fila ya leída)."""
    return {"codigo": codigo, "piso": piso, "estado": estado,
            "equipo": equipo, "cable": cable, "ultima_revision": ultima_revision}


def escribir_archivo(ruta, texto):
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(texto)


def procesar_archivo(ruta):
    """Corre lectura, validación y limpieza sobre un archivo real."""
    filas = fuentes.elegir_fuente(ruta).cargar(ruta)
    pipeline.validar_esquema(filas)
    filas = pipeline.normalizar_campos(filas)
    validos, rechazos = pipeline.limpiar_datos(filas)
    return filas, validos, rechazos



class TestPuertoRed(unittest.TestCase):

    def test_registro_normal_es_valido(self):
        puerto = crear_puerto()
        self.assertEqual(puerto.motivos_de_rechazo(), [])

    def test_codigo_con_formato_invalido(self):
        puerto = crear_puerto(codigo="SR1-P1-5")
        self.assertFalse(puerto.codigo_tiene_formato())
        self.assertIn("formato invalido", " ".join(puerto.motivos_de_rechazo()))

    def test_puerto_fuera_de_rango(self):
    
        puerto = crear_puerto(codigo="SR01-P01-30")
        self.assertTrue(puerto.codigo_tiene_formato())
        self.assertIn("fuera de rango", " ".join(puerto.motivos_de_rechazo()))

    def test_fecha_inexistente_se_rechaza(self):
        
        puerto = crear_puerto(ultima_revision="2026-02-30")
        self.assertFalse(puerto.fecha_es_valida())

    def test_fecha_real_se_acepta(self):
        self.assertTrue(crear_puerto(ultima_revision="2026-02-28").fecha_es_valida())
        # 2024 fue bisiesto, así que el 29 de febrero sí existió.
        self.assertTrue(crear_puerto(ultima_revision="2024-02-29").fecha_es_valida())

    def test_ocupado_sin_equipo(self):
        puerto = crear_puerto(estado="ocupado", equipo="")
        self.assertIn("sin equipo", " ".join(puerto.motivos_de_rechazo()))

    def test_piso_no_coincide_con_codigo(self):
        
        puerto = crear_puerto(codigo="SR01-P01-05", piso="4")
        self.assertIn("no coincide", " ".join(puerto.motivos_de_rechazo()))

    def test_varios_motivos_se_acumulan(self):
        puerto = crear_puerto(codigo="SR1-P1-5", cable="")
        self.assertEqual(len(puerto.motivos_de_rechazo()), 2)



class TestFuentes(unittest.TestCase):

    def test_csv_y_json_son_equivalentes(self):
        filas_csv = fuentes.FuenteCSV().cargar(RUTA_CSV)
        filas_json = fuentes.FuenteJSON().cargar(RUTA_JSON)
        self.assertEqual(len(filas_csv), 99)
        self.assertEqual(filas_csv, filas_json)

    def test_archivo_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            fuentes.FuenteCSV().cargar("data/no_existe.csv")

    def test_json_invalido(self):
        with tempfile.TemporaryDirectory() as carpeta:
            mal_formado = os.path.join(carpeta, "roto.json")
            escribir_archivo(mal_formado, "{esto no es json")
            with self.assertRaises(ValueError):
                fuentes.FuenteJSON().cargar(mal_formado)

            no_es_lista = os.path.join(carpeta, "objeto.json")
            escribir_archivo(no_es_lista, '{"codigo": "SR01-P01-01"}')
            with self.assertRaises(ValueError):
                fuentes.FuenteJSON().cargar(no_es_lista)

    def test_formato_no_soportado(self):
        with self.assertRaises(ValueError):
            fuentes.elegir_fuente("datos.txt")

    def test_elegir_fuente_segun_extension(self):
        self.assertIsInstance(fuentes.elegir_fuente("a.csv"), fuentes.FuenteCSV)
        self.assertIsInstance(fuentes.elegir_fuente("a.JSON"), fuentes.FuenteJSON)



class TestPipeline(unittest.TestCase):

    def test_esquema_sin_registros(self):
        with self.assertRaises(ValueError):
            pipeline.validar_esquema([])

    def test_esquema_con_columna_faltante(self):
        with self.assertRaises(ValueError):
            pipeline.validar_esquema([{"codigo": "SR01-P01-01"}])

    def test_duplicado_se_rechaza_y_se_conserva_el_primero(self):
        fila = crear_fila()
        validos, rechazos = pipeline.limpiar_datos([fila, dict(fila)])
        self.assertEqual(len(validos), 1)
        self.assertEqual(len(rechazos), 1)
        self.assertEqual(rechazos[0]["registro"], 2)
        self.assertIn("duplicado", rechazos[0]["motivo"])

    def test_limpieza_de_datos_de_ejemplo(self):
        filas, validos, rechazos = procesar_archivo(RUTA_CSV)
        self.assertEqual(len(validos), 92)
        self.assertEqual(len(rechazos), 7)

    def test_validos_mas_rechazados_igual_a_leidos(self):

        filas, validos, rechazos = procesar_archivo(RUTA_CSV)
        self.assertEqual(len(validos) + len(rechazos), len(filas))

    def test_reporte_con_valores_conocidos(self):
        puertos = [
            crear_puerto("SR01-P01-01", "1", "libre"),
            crear_puerto("SR01-P01-02", "1", "libre"),
            crear_puerto("SR01-P01-03", "1", "ocupado", "Impresora"),
            crear_puerto("SR01-P01-04", "1", "danado"),
        ]
        reporte = pipeline.generar_reporte(puertos)
        piso1 = reporte[0]
        self.assertEqual(piso1["total"], 4)
        self.assertEqual(piso1["libres"], 2)
        self.assertEqual(piso1["ocupados"], 1)
        self.assertEqual(piso1["danados"], 1)
        self.assertEqual(piso1["porcentaje_ocupacion"], 33.3)
        total = reporte[4]
        self.assertEqual(total["piso"], "total")
        self.assertEqual(total["total"], 4)

    def test_piso_sin_puertos_utilizables_da_none(self):
        reporte = pipeline.generar_reporte([crear_puerto("SR01-P01-01", "1", "danado")])
        self.assertIsNone(reporte[0]["porcentaje_ocupacion"])   # piso 1: solo un danado
        self.assertIsNone(reporte[1]["porcentaje_ocupacion"])   # piso 2: sin puertos

    def test_verificar_resultado_detecta_incoherencia(self):
        filas, validos, rechazos = procesar_archivo(RUTA_CSV)
        reporte = pipeline.generar_reporte(validos)
        pipeline.verificar_resultado(reporte, validos)   # el reporte correcto pasa sin error
        reporte[0]["libres"] = reporte[0]["libres"] + 1  # lo alteramos a propósito
        with self.assertRaises(ValueError):
            pipeline.verificar_resultado(reporte, validos)

    def test_suma_de_pisos_conserva_los_validos(self):
        filas, validos, rechazos = procesar_archivo(RUTA_CSV)
        reporte = pipeline.generar_reporte(validos)
        suma = 0
        for indice in range(4):
            suma = suma + reporte[indice]["total"]
        self.assertEqual(suma, len(validos))


class TestFlujoCompleto(unittest.TestCase):

    def test_csv_y_json_producen_el_mismo_reporte(self):
        with tempfile.TemporaryDirectory() as carpeta:
            leidos_c, validos_c, rechazos_c, reporte_c = main.ejecutar(
                RUTA_CSV, os.path.join(carpeta, "a.csv"), os.path.join(carpeta, "ra.csv"))
            leidos_j, validos_j, rechazos_j, reporte_j = main.ejecutar(
                RUTA_JSON, os.path.join(carpeta, "b.csv"), os.path.join(carpeta, "rb.csv"))
        self.assertEqual(reporte_c, reporte_j)
        self.assertEqual(rechazos_c, rechazos_j)

    def test_se_guardan_los_archivos_de_salida(self):
        with tempfile.TemporaryDirectory() as carpeta:
            salida = os.path.join(carpeta, "nueva", "reporte.csv")
            rechazos = os.path.join(carpeta, "nueva", "rechazos.csv")
            main.ejecutar(RUTA_CSV, salida, rechazos)
            self.assertTrue(os.path.exists(salida))
            self.assertTrue(os.path.exists(rechazos))
            with open(rechazos, "r", encoding="utf-8") as archivo:
                lineas = archivo.readlines()
            # 1 línea de encabezado + 7 registros rechazados
            self.assertEqual(len(lineas), 8)


if __name__ == "__main__":
    unittest.main()
