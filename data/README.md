# Datos

- **Fuente:** datos simulados, generados con `src/generar_datos.py` (semilla fija 42).
- **Responsable:** el autor del trabajo.
- **Licencia:** uso libre; son datos sintéticos, sin información real ni sensible.
- **Fecha de generación:** COMPLETAR con la fecha del día.
- **Unidad de análisis:** cada fila es un puerto de un SR (switch de red).
- **Tamaño:** 99 observaciones y 6 variables.
- **Variables:**
  - `codigo`: identifica el puerto. Formato `SRss-Ppp-nn` (ss = número de SR, pp = piso, nn = puerto). Ejemplo: `SR02-P02-05`.
  - `piso`: piso donde está el SR (1 a 4).
  - `estado`: `libre`, `ocupado` o `danado`.
  - `equipo`: equipo conectado al puerto (vacío si no hay ninguno).
  - `cable`: tipo de cable (`Cat5e`, `Cat6` o `Cat6a`).
  - `ultima_revision`: fecha de la última revisión, formato `AAAA-MM-DD`.
- **Formatos:** `puertos.csv` y `puertos.json` contienen los mismos registros.
- **Errores intencionales (7 registros):** duplicado, formato de código, puerto fuera de rango, ocupado sin equipo, fecha inexistente, piso incoherente con el código y valor faltante.
- **Limitaciones:** al ser simulados, no reflejan la distribución real de un edificio. Se asume un SR por piso.
