import csv

from modelo import PuertoRed, PISO_MINIMO, PISO_MAXIMO

CAMPOS_REQUERIDOS = ["codigo", "piso", "estado", "equipo", "cable", "ultima_revision"]


def validar_esquema(filas):
    """Inspecciona la estructura: que haya datos y estén todas las columnas."""
    if len(filas) == 0:
        raise ValueError("El archivo no contiene registros")

    primera = filas[0]
    faltantes = []
    for campo in CAMPOS_REQUERIDOS:
        if campo not in primera:
            faltantes.append(campo)
    if len(faltantes) > 0:
        raise ValueError("Faltan columnas obligatorias: " + ", ".join(faltantes))


def normalizar_campos(filas):
    """Deja todos los campos como texto limpio, para que las reglas
    trabajen siempre con el mismo tipo de dato."""
    normalizadas = []
    for fila in filas:
        nueva = {}
        for campo in CAMPOS_REQUERIDOS:
            valor = fila.get(campo)      
            if valor is None:
                valor = ""               
            nueva[campo] = str(valor).strip()   
        nueva["estado"] = nueva["estado"].lower()
        normalizadas.append(nueva)
    return normalizadas


def limpiar_datos(filas):
    """Separa los registros en válidos (objetos PuertoRed) y rechazos.
    Criterio de duplicados: se conserva la primera aparición válida de
    cada código y las siguientes se rechazan."""
    validos = []
    rechazos = []
    codigos_aceptados = {}   
    numero_registro = 0

    for fila in filas:
        numero_registro = numero_registro + 1
        puerto = PuertoRed(fila["codigo"], fila["piso"], fila["estado"],
                           fila["equipo"], fila["cable"], fila["ultima_revision"])

        motivos = puerto.motivos_de_rechazo()
        if fila["codigo"] in codigos_aceptados:
            motivos.append("codigo duplicado (ya aparece en el registro "
                           + str(codigos_aceptados[fila["codigo"]]) + ")")

        if len(motivos) == 0:
            validos.append(puerto)
            codigos_aceptados[fila["codigo"]] = numero_registro
        else:
            rechazo = {
                "registro": numero_registro,
                "codigo": fila["codigo"],
                "motivo": "; ".join(motivos),
            }
            rechazos.append(rechazo)

    return validos, rechazos


def generar_reporte(validos):
    """Cuenta los puertos libres, ocupados y danados de cada piso y calcula el
    porcentaje de ocupación. Devuelve una lista de diccionarios: una fila por
    piso y una última fila con el total del edificio."""
    reporte = []
    total_libres = 0
    total_ocupados = 0
    total_danados = 0

    for piso in range(PISO_MINIMO, PISO_MAXIMO + 1):
        libres = 0
        ocupados = 0
        danados = 0
        for puerto in validos:
            if puerto.piso_numero() == piso:
                if puerto.esta_libre():
                    libres = libres + 1
                elif puerto.esta_ocupado():
                    ocupados = ocupados + 1
                elif puerto.esta_danado():
                    danados = danados + 1
        reporte.append(armar_fila_reporte(piso, libres, ocupados, danados))
        total_libres = total_libres + libres
        total_ocupados = total_ocupados + ocupados
        total_danados = total_danados + danados

    reporte.append(armar_fila_reporte("total", total_libres, total_ocupados, total_danados))
    return reporte


def armar_fila_reporte(piso, libres, ocupados, danados):
    """Arma una fila del reporte. La ocupación se calcula sobre los puertos
    utilizables (libres + ocupados): los danados no se pueden usar, así que
    se informan aparte y no cuentan como capacidad."""
    utilizables = libres + ocupados
    if utilizables == 0:
        porcentaje = None    
    else:
        porcentaje = round(100 * ocupados / utilizables, 1)
    fila = {
        "piso": piso,
        "total": libres + ocupados + danados,
        "libres": libres,
        "ocupados": ocupados,
        "danados": danados,
        "porcentaje_ocupacion": porcentaje,
    }
    return fila


def verificar_resultado(reporte, validos):
    """Comprueba que el reporte sea coherente antes de guardarlo."""
    suma_de_pisos = 0
    for fila in reporte:
        if fila["piso"] == "total":
            continue    
        if fila["libres"] + fila["ocupados"] + fila["danados"] != fila["total"]:
            raise ValueError("Reporte incoherente en el piso " + str(fila["piso"]))
        porcentaje = fila["porcentaje_ocupacion"]
        if porcentaje is not None and (porcentaje < 0 or porcentaje > 100):
            raise ValueError("Porcentaje fuera de rango en el piso " + str(fila["piso"]))
        suma_de_pisos = suma_de_pisos + fila["total"]

    if suma_de_pisos != len(validos):
        raise ValueError("Los puertos del reporte (" + str(suma_de_pisos)
                         + ") no coinciden con los puertos validos (" + str(len(validos)) + ")")


def guardar_resultado(reporte, ruta):
    """Guarda el reporte en un CSV. El porcentaje no disponible se escribe n/d."""
    campos = ["piso", "total", "libres", "ocupados", "danados", "porcentaje_ocupacion"]
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        for fila in reporte:
            copia = dict(fila)
            if copia["porcentaje_ocupacion"] is None:
                copia["porcentaje_ocupacion"] = "n/d"
            escritor.writerow(copia)


def guardar_rechazos(rechazos, ruta):
    """Guarda los registros rechazados con su número, código y motivos."""
    campos = ["registro", "codigo", "motivo"]
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        for rechazo in rechazos:
            escritor.writerow(rechazo)
