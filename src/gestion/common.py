"""
Utilidades comunes, validadores y opciones compartidas entre modelos.
"""

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

# Validadores
phone_validator = RegexValidator(
    regex=r"^\+?[\d\s\-]{6,20}$", message="Teléfono inválido"
)

postal_validator = RegexValidator(
    regex=r"^[0-9A-Z\-]{3,10}$", message="Código postal inválido"
)


# Enums / Choices
class Sexo(models.TextChoices):
    HOMBRE = "H", "Hombre"
    MUJER = "M", "Mujer"
    OTRO = "O", "Otro"


class TipoDocumento(models.TextChoices):
    DNI = "DNI", "DNI"
    NIE = "NIE", "NIE"
    PASAPORTE = "PASAPORTE", "Pasaporte"


class TipoVehiculo(models.TextChoices):
    TRACTOR = "TRACTOR", "Tractor"
    COCHE = "COCHE", "Coche"
    REMOLQUE = "REMOLQUE", "Remolque"
    FURGONETA = "FURGONETA", "Furgoneta"
    OTRO = "OTRO", "Otro"


class TipoRepresentacion(models.TextChoices):
    PROPIETARIO = "PROPIETARIO", "Propietario"
    REPRESENTANTE = "REPRESENTANTE", "Representante"


class TipoActividad(models.TextChoices):
    SIEMBRA = "SIEMBRA", "Siembra"
    RIEGO = "RIEGO", "Riego"
    ABONADO = "ABONADO", "Abonado"
    TRATAMIENTO = "TRATAMIENTO", "Tratamiento fitosanitario"
    COSECHA = "COSECHA", "Cosecha"
    OTRO = "OTRO", "Otro"


class RespuestaSiNo(models.TextChoices):
    SI = "S", "Sí"
    NO = "N", "No"


__all__ = [
    # Validadores
    "phone_validator",
    "postal_validator",
    "MinValueValidator",
    # Enums
    "Sexo",
    "TipoDocumento",
    "TipoVehiculo",
    "TipoRepresentacion",
    "TipoActividad",
    "RespuestaSiNo",
]
