# Inventario y ocupación de puertos de switches de red

**Autor:** Leonori Seara Francisco

## Problema
En un edificio, la red se distribuye desde switches de red (SR) alojados en
gabinetes (racks). El estado de los puertos de cada SR suele llevarse en
planillas editadas a mano, con códigos mal escritos, puertos duplicados, fechas
imposibles y puertos "ocupados" sin equipo asignado. Con datos así no se puede
saber con confianza cuánta capacidad libre queda en cada piso.

## Usuario
Personal técnico que mantiene la red de un edificio.

## Solución propuesta
Un programa que lee el inventario de puertos (CSV o JSON), valida cada
registro, separa los inválidos con su motivo y genera un reporte de ocupación
por piso.

## Alcance de la primera versión
Incluye: lectura CSV/JSON, validación, reporte por piso, archivo de rechazos.
Queda fuera: edición de datos, base de datos, login, planos del edificio y la
relación de cada puerto con la boca de red de destino.
