import csv
import json
import random

random.seed(42)

EQUIPOS = ["PC-Administracion", "Impresora", "Telefono-IP", "Access-Point", "Camara-IP"]
CABLES = ["Cat5e", "Cat6", "Cat6a"]
CAMPOS = ["codigo", "piso", "estado", "equipo", "cable", "ultima_revision"]


def armar_codigo(piso, puerto):

    return "SR" + str(piso).zfill(2) + "-P" + str(piso).zfill(2) + "-" + str(puerto).zfill(2)


def armar_fecha():
   
    mes = random.randint(1, 10)
    dia = random.randint(1, 28)
    return "2026-" + str(mes).zfill(2) + "-" + str(dia).zfill(2)


def generar_filas():
    filas = []
    for piso in range(1, 5):          
        for puerto in range(1, 25):   
            numero = random.random()  
            if numero < 0.6:
                estado = "ocupado"
                equipo = random.choice(EQUIPOS)
            elif numero < 0.9:
                estado = "libre"
                equipo = ""
            else:
                estado = "danado"
                equipo = ""
            fila = {
                "codigo": armar_codigo(piso, puerto),
                "piso": str(piso),
                "estado": estado,
                "equipo": equipo,
                "cable": random.choice(CABLES),
                "ultima_revision": armar_fecha(),
            }
            filas.append(fila)
    return filas


def agregar_errores(filas):
    
    filas.append(dict(filas[0]))
    
    filas.append({"codigo": "SR1-P1-5", "piso": "1", "estado": "libre",
                  "equipo": "", "cable": "Cat6", "ultima_revision": "2026-03-10"})
    
    filas.append({"codigo": "SR01-P01-30", "piso": "1", "estado": "libre",
                  "equipo": "", "cable": "Cat6", "ultima_revision": "2026-03-11"})
    
    filas[10]["estado"] = "ocupado"
    filas[10]["equipo"] = ""
    
    filas[50]["ultima_revision"] = "2026-02-30"
    
    filas[30]["piso"] = "4"
    
    filas[70]["cable"] = ""
    return filas


def guardar_csv(filas, ruta):
    archivo = open(ruta, "w", newline="", encoding="utf-8")
    escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
    escritor.writeheader()
    for fila in filas:
        escritor.writerow(fila)
    archivo.close()


def guardar_json(filas, ruta):
    archivo = open(ruta, "w", encoding="utf-8")
    json.dump(filas, archivo, indent=2, ensure_ascii=False)
    archivo.close()


if __name__ == "__main__":
    filas = generar_filas()
    filas = agregar_errores(filas)
    guardar_csv(filas, "data/puertos.csv")
    guardar_json(filas, "data/puertos.json")
    print("Filas generadas:", len(filas))
