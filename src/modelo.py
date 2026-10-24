import re
from datetime import date

# Expresión regular del código de un puerto de un SR (switch de red).
# Ejemplo: SR02-P02-05
#   ^        inicio del texto
#   SR       las letras SR (de "switch de red")
#   (\d{2})  exactamente dos dígitos: número de SR      (grupo 1)
#   -P       un guion y la letra P
#   (\d{2})  exactamente dos dígitos: número de piso    (grupo 2)
#   -        un guion
#   (\d{2})  exactamente dos dígitos: número de puerto  (grupo 3)
#   $        fin del texto
PATRON_CODIGO = re.compile(r"^SR(\d{2})-P(\d{2})-(\d{2})$")

# Formato de fecha AAAA-MM-DD (solo comprueba la forma, no el calendario)
PATRON_FECHA = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")

ESTADOS_VALIDOS = ["libre", "ocupado", "danado"]
CABLES_VALIDOS = ["Cat5e", "Cat6", "Cat6a"]
PUERTO_MAXIMO = 24
PISO_MINIMO = 1
PISO_MAXIMO = 4


def convertir_a_entero(texto):
    """Convierte un texto a entero. Devuelve None si no es posible."""
    try:
        return int(texto)
    except (ValueError, TypeError):
        return None


class PuertoRed:
    """Representa un puerto de un SR (switch de red)."""

    def __init__(self, codigo, piso, estado, equipo, cable, ultima_revision):
        # Se guardan tal como llegan (texto). La validación decide si sirven.
        self.codigo = codigo
        self.piso = piso
        self.estado = estado
        self.equipo = equipo
        self.cable = cable
        self.ultima_revision = ultima_revision

    # ---- Consultas sobre el código (usan la expresión regular) ----

    def codigo_tiene_formato(self):
        return PATRON_CODIGO.match(self.codigo) is not None

    def piso_del_codigo(self):
        # Solo se llama si el formato es correcto.
        return int(PATRON_CODIGO.match(self.codigo).group(2))

    def numero_de_puerto(self):
        return int(PATRON_CODIGO.match(self.codigo).group(3))

    # ---- Consultas sobre el estado (se usan en el reporte) ----

    def piso_numero(self):
        return int(self.piso)

    def esta_libre(self):
        return self.estado == "libre"

    def esta_ocupado(self):
        return self.estado == "ocupado"

    def esta_danado(self):
        return self.estado == "danado"

    # ---- Validación ----

    def fecha_es_valida(self):
        # La regex comprueba la forma; date() comprueba que exista en el
        # calendario (por ejemplo, rechaza 2026-02-30).
        coincidencia = PATRON_FECHA.match(self.ultima_revision)
        if coincidencia is None:
            return False
        anio = int(coincidencia.group(1))
        mes = int(coincidencia.group(2))
        dia = int(coincidencia.group(3))
        try:
            date(anio, mes, dia)
        except ValueError:
            return False
        return True

    def motivos_de_rechazo(self):
        """Devuelve una lista con los motivos por los que el registro es
        inválido. Si la lista está vacía, el registro es válido."""
        motivos = []

        # 1. Código: primero el formato (regex), después el rango del puerto
        if not self.codigo_tiene_formato():
            motivos.append("codigo con formato invalido: " + self.codigo)
        else:
            puerto = self.numero_de_puerto()
            if puerto < 1 or puerto > PUERTO_MAXIMO:
                motivos.append("puerto fuera de rango (1-" + str(PUERTO_MAXIMO)
                               + "): " + str(puerto))

        # 2. Piso: debe ser entero, estar en rango y coincidir con el código
        piso = convertir_a_entero(self.piso)
        if piso is None:
            motivos.append("piso no es un numero entero: " + self.piso)
        elif piso < PISO_MINIMO or piso > PISO_MAXIMO:
            motivos.append("piso fuera de rango: " + str(piso))
        elif self.codigo_tiene_formato() and piso != self.piso_del_codigo():
            motivos.append("el piso (" + str(piso) + ") no coincide con el piso del codigo ("
                           + str(self.piso_del_codigo()) + ")")

        # 3. Estado
        if self.estado not in ESTADOS_VALIDOS:
            motivos.append("estado desconocido: " + self.estado)

        # 4. Cable: faltante o desconocido
        if self.cable == "":
            motivos.append("cable faltante")
        elif self.cable not in CABLES_VALIDOS:
            motivos.append("tipo de cable desconocido: " + self.cable)

        # 5. Fecha de revisión
        if not self.fecha_es_valida():
            motivos.append("fecha de revision invalida: " + self.ultima_revision)

        # 6. Coherencia entre estado y equipo
        if self.estado == "ocupado" and self.equipo == "":
            motivos.append("puerto ocupado sin equipo asignado")
        if self.estado == "libre" and self.equipo != "":
            motivos.append("puerto libre con equipo asignado")

        return motivos
