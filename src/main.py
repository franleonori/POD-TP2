import argparse
import os
import sys

import fuentes
import pipeline


def crear_carpeta_de_salida(ruta):
    """Si la ruta incluye una carpeta que no existe (por ejemplo outputs/),
    la crea. Así el programa no falla la primera vez que se ejecuta."""
    carpeta = os.path.dirname(ruta)
    if carpeta != "":
        os.makedirs(carpeta, exist_ok=True)


def ejecutar(ruta_entrada, ruta_salida, ruta_rechazos):
    """Recorre todo el flujo: leer, validar, limpiar, analizar y guardar.
    Devuelve los datos que main() necesita para mostrar el resumen."""
    fuente = fuentes.elegir_fuente(ruta_entrada)
    filas = fuente.cargar(ruta_entrada)

    pipeline.validar_esquema(filas)
    filas = pipeline.normalizar_campos(filas)
    validos, rechazos = pipeline.limpiar_datos(filas)

    reporte = pipeline.generar_reporte(validos)
    pipeline.verificar_resultado(reporte, validos)

    crear_carpeta_de_salida(ruta_salida)
    crear_carpeta_de_salida(ruta_rechazos)
    pipeline.guardar_resultado(reporte, ruta_salida)
    pipeline.guardar_rechazos(rechazos, ruta_rechazos)

    return len(filas), validos, rechazos, reporte


def mostrar_resumen(leidos, validos, rechazos, reporte, ruta_salida, ruta_rechazos):
    """Muestra en pantalla el resultado para quien usa el programa."""
    print("Registros leidos:     " + str(leidos))
    print("Registros validos:    " + str(len(validos)))
    print("Registros rechazados: " + str(len(rechazos)))
    print("")
    print("Ocupacion por piso")
    print("Piso".ljust(8) + "Total".ljust(8) + "Libres".ljust(8)
          + "Ocupados".ljust(10) + "Danados".ljust(9) + "Ocupacion")
    for fila in reporte:
        if fila["porcentaje_ocupacion"] is None:
            texto_porcentaje = "n/d"
        else:
            texto_porcentaje = str(fila["porcentaje_ocupacion"]) + "%"
        print(str(fila["piso"]).ljust(8) + str(fila["total"]).ljust(8)
              + str(fila["libres"]).ljust(8) + str(fila["ocupados"]).ljust(10)
              + str(fila["danados"]).ljust(9) + texto_porcentaje)
    print("")
    print("Reporte guardado en:   " + ruta_salida)
    print("Rechazos guardados en: " + ruta_rechazos)


def main():
    parser = argparse.ArgumentParser(
        description="Reporte de ocupacion de puertos de SR por piso")
    parser.add_argument("entrada", help="archivo de entrada (.csv o .json)")
    parser.add_argument("--salida", default="outputs/reporte_pisos.csv",
                        help="archivo donde se guarda el reporte")
    parser.add_argument("--rechazos", default="outputs/rechazos.csv",
                        help="archivo donde se guardan los registros rechazados")
    argumentos = parser.parse_args()

    try:
        leidos, validos, rechazos, reporte = ejecutar(
            argumentos.entrada, argumentos.salida, argumentos.rechazos)
    except (FileNotFoundError, ValueError) as error:
        print("Error: " + str(error))
        sys.exit(1)

    mostrar_resumen(leidos, validos, rechazos, reporte,
                    argumentos.salida, argumentos.rechazos)


if __name__ == "__main__":
    main()
