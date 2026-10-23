# Inventario y ocupación de puertos de switches de red

**Autor:** Leonori Seara Francisco
**Materia:** Programación Orientada a Datos, Licenciatura en Ciencia de Datos, UCA (2026)
**Trabajo:** TP2 individual

## Problema, usuario y solución

**Problema.** En un edificio, la red se distribuye desde switches de red (SR)
alojados en gabinetes (racks). El estado de los puertos de cada SR suele llevarse
en planillas editadas a mano. Con el tiempo aparecen códigos mal escritos, puertos
duplicados, fechas imposibles y puertos "ocupados" sin equipo asignado. Con datos así
no se puede saber con confianza cuánta capacidad libre queda en cada piso.

**Usuario.** Personal técnico que mantiene la red de un edificio. Usa el resultado
para decidir en qué piso hay capacidad disponible y qué registros hay que corregir.

**Solución.** Un programa de consola que lee el inventario de puertos (CSV o JSON),
valida cada registro, separa los inválidos con su motivo y genera un reporte de
ocupación por piso.

**Modelo del dominio.** El gabinete (rack) aloja el SR. Desde los puertos del SR el
servicio llega a las bocas de red donde los usuarios toman servicio, a veces mediante
una extensión. Esta versión modela los **puertos del SR**.

## Funcionalidades

- Lee el inventario desde un archivo CSV o JSON (se elige por la extensión).
- Inspecciona que el archivo tenga las columnas necesarias.
- Valida cada puerto con reglas de formato, rango y coherencia.
- Detecta duplicados y valores faltantes.
- Genera un reporte por piso con puertos libres, ocupados, dañados y porcentaje de ocupación.
- Guarda el reporte y los registros rechazados (con sus motivos) en archivos CSV.

**Fuera de la primera versión:** edición de datos, base de datos, usuarios y login,
planos del edificio, interfaz web y la relación de cada puerto con la boca de red de destino.

## Datos

- **Fuente:** datos simulados, generados con `src/generar_datos.py` (semilla fija 42).
- **Licencia:** uso libre; son datos sintéticos, sin información real ni sensible.
- **Unidad de análisis:** cada fila es un puerto de un SR.
- **Tamaño:** 99 observaciones y 6 variables.
- **Variables:** `codigo`, `piso`, `estado`, `equipo`, `cable`, `ultima_revision`.
- **Formato del código:** `SRss-Ppp-nn` (ss = número de SR, pp = piso, nn = puerto).
  Ejemplo: `SR02-P02-05`.

El detalle completo está en [`data/README.md`](data/README.md). Los archivos
`data/puertos.csv` y `data/puertos.json` contienen **los mismos registros** en dos
formatos, lo que permite comprobar que ambas lecturas son equivalentes.

## Instalación

Requiere Python 3.8 o superior. Solo usa la biblioteca estándar, así que no hay
nada que instalar (`requirements.txt` solo lo deja documentado). En Linux o Mac, si
el comando `python` no existe, usar `python3`.

```bash
git https://github.com/franleonori/POD-TP2
```

## Uso

Generar los datos de ejemplo (opcional, ya están incluidos en `data/`):

```bash
python src/generar_datos.py
```

Ejecutar la aplicación:

```bash
python src/main.py data/puertos.csv
python src/main.py data/puertos.json
```

Opciones:

```bash
python src/main.py data/puertos.csv --salida outputs/reporte_pisos.csv --rechazos outputs/rechazos.csv
python src/main.py --help
```

Ejecutar las pruebas (24 pruebas):

```bash
python -m unittest discover -s tests -v
```

## Organización del código

```
src/
  generar_datos.py   genera los datos simulados (CSV y JSON) con errores intencionales
  fuentes.py         FuenteDatos (clase base), FuenteCSV, FuenteJSON y elegir_fuente()
  modelo.py          clase PuertoRed: reglas de validación de un registro
  pipeline.py        validación de esquema, normalización, limpieza, reporte y guardado
  main.py            coordina el flujo y define la línea de comandos
tests/
  test_aplicacion.py pruebas con unittest
data/                datos de ejemplo y su documentación
outputs/             archivos generados por la aplicación (no se versionan)
```

Flujo de procesamiento:

```
leer (fuentes) → validar esquema → normalizar → limpiar (modelo) → reporte → verificar → guardar
```

- `fuentes.py` aísla el formato de entrada: el resto del programa recibe siempre una
  lista de diccionarios, sin importar si vino de un CSV o de un JSON.
- `modelo.py` concentra las reglas de **un** registro; `pipeline.py` aplica esas reglas
  a **todos** los registros y hace las comprobaciones que requieren comparar entre ellos
  (duplicados).
- `main.py` es el único módulo que conoce a los demás.

## Ejemplo de resultado

Salida de `python src/main.py data/puertos.csv`:

```
Registros leidos:     99
Registros validos:    92
Registros rechazados: 7

Ocupacion por piso
Piso    Total   Libres  Ocupados  Danados  Ocupacion
1       23      8       15        0        65.2%
2       23      9       14        0        60.9%
3       22      5       14        3        73.7%
4       24      9       12        3        57.1%
total   92      31      55        6        64.0%

Reporte guardado en:   outputs/reporte_pisos.csv
Rechazos guardados en: outputs/rechazos.csv
```

Contenido de `outputs/rechazos.csv` (los 7 registros rechazados, con su motivo):

```
registro,codigo,motivo
11,SR01-P01-11,puerto ocupado sin equipo asignado
31,SR02-P02-07,el piso (4) no coincide con el piso del codigo (2)
51,SR03-P03-03,fecha de revision invalida: 2026-02-30
71,SR03-P03-23,cable faltante
97,SR01-P01-01,codigo duplicado (ya aparece en el registro 1)
98,SR1-P1-5,codigo con formato invalido: SR1-P1-5
99,SR01-P01-30,puerto fuera de rango (1-24): 30
```

## Decisiones de limpieza

Los registros inválidos **no se corrigen ni se descartan en silencio**: se separan y se
guardan en `outputs/rechazos.csv` con su número de registro, su código y todos sus motivos.

| Regla | Qué comprueba | Cómo |
|---|---|---|
| Formato del código | que sea `SRss-Ppp-nn` | expresión regular |
| Puerto en rango | que el puerto esté entre 1 y 24 | comparación (la regex no lo puede resolver) |
| Piso | entero entre 1 y 4, y que coincida con el piso del código | conversión y comparación |
| Estado | `libre`, `ocupado` o `danado` | lista de valores permitidos |
| Cable | no vacío y uno de `Cat5e`, `Cat6`, `Cat6a` | lista de valores permitidos |
| Fecha de revisión | formato `AAAA-MM-DD` y que exista en el calendario | regex + `datetime.date` |
| Estado y equipo | un puerto ocupado debe tener equipo y uno libre no | comparación |
| Duplicados | se conserva la primera aparición de cada código; las siguientes se rechazan | diccionario de códigos |

**La expresión regular** `^SR(\d{2})-P(\d{2})-(\d{2})$` valida únicamente la *forma*
del código. No sabe si el puerto existe ni si el piso coincide con el campo `piso`,
por eso esas reglas se comprueban aparte. Lo mismo ocurre con las fechas: `2026-02-30`
tiene la forma correcta pero no existe.

## Interpretación y limitaciones

**Cómo leer el reporte.** `porcentaje_ocupacion = ocupados / (libres + ocupados) × 100`.
Los puertos dañados no se pueden usar, así que no cuentan como capacidad y se informan en
su propia columna. Si un piso no tiene puertos utilizables, el porcentaje se informa como
`n/d` y no como 0, porque 0 significaría "hay capacidad y nadie la usa".

**Verificación.** Antes de guardar, el programa comprueba que libres + ocupados +
dañados sea igual al total de cada piso, que los porcentajes estén entre 0 y 100 y que la
suma de los pisos coincida con la cantidad de registros válidos.

**Limitaciones.**
- Los datos son simulados y no reflejan la distribución real de un edificio.
- Los límites (4 pisos, 24 puertos por SR, tipos de cable) y la regla de un SR por piso
  están fijos en `modelo.py`.
- La validación de duplicados solo compara el código del puerto.
- El programa no modela la boca de red de destino de cada puerto ni las extensiones.
- El programa informa el estado del inventario, pero no lo corrige.
