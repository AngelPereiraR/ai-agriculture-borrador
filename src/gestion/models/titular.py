from django.db import models

from ..common import TipoDocumento


class Titular(models.Model):
    nombre = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=200, blank=True, null=True)
    tipo_documento = models.CharField(max_length=20, choices=TipoDocumento.choices)
    documento = models.CharField(max_length=20, unique=True)
    direccion = models.ForeignKey(
        "gestion.Direccion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="titulares",
    )
    cif_explotacion = models.CharField(max_length=50, blank=True, null=True)
    registro_explotacion = models.CharField(max_length=100)
