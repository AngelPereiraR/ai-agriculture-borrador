from django.db import models

from ..common import Sexo, phone_validator, postal_validator


class Direccion(models.Model):
    """Dirección postal y de contacto."""

    tipo_via = models.CharField("tipo vía", max_length=50, blank=True)
    nombre_via = models.CharField("nombre vía", max_length=200, blank=True)
    numero = models.CharField("número", max_length=20, blank=True)
    bloque = models.CharField("bloque", max_length=50, blank=True)
    portal = models.CharField("portal", max_length=50, blank=True)
    escalera = models.CharField("escalera", max_length=50, blank=True)
    planta = models.CharField("planta", max_length=20, blank=True)
    puerta = models.CharField("puerta", max_length=20, blank=True)
    entidad_poblacion = models.CharField(
        "entidad población", max_length=150, blank=True
    )
    localidad = models.CharField(
        "localidad / municipio", max_length=150, blank=True, db_index=True
    )
    provincia = models.CharField("provincia", max_length=150, blank=True, db_index=True)
    pais = models.CharField("país", max_length=100, blank=True, default="ES")
    codigo_postal = models.CharField(
        "código postal", max_length=10, blank=True, validators=[postal_validator]
    )

    telefono = models.CharField(
        "teléfono fijo", max_length=20, blank=True, validators=[phone_validator]
    )
    movil = models.CharField(
        "móvil", max_length=20, blank=True, validators=[phone_validator]
    )
    email = models.EmailField("correo electrónico", blank=True)


class Persona(models.Model):
    """Persona física o jurídica."""

    nombre = models.CharField("nombre / razón social", max_length=250)
    nif = models.CharField("DNI/NIE/NIF", max_length=30, blank=True, db_index=True)
    sexo = models.CharField("sexo", max_length=1, choices=Sexo.choices, blank=True)
    direccion = models.ForeignKey(
        "Direccion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="personas",
    )
    telefono = models.CharField(
        "teléfono", max_length=20, blank=True, validators=[phone_validator]
    )
    movil = models.CharField(
        "móvil", max_length=20, blank=True, validators=[phone_validator]
    )
    email = models.EmailField("correo electrónico", blank=True)
