from django.db import models

from ..common import TipoDocumento


class Destinatario(models.Model):
    nombre = models.CharField(max_length=200)
    tipo_documento = models.CharField(
        max_length=20, choices=TipoDocumento.choices, blank=True, null=True
    )
    documento = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.ForeignKey(
        "gestion.Direccion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="destinatarios",
    )
    transporte_asignado = models.ForeignKey(
        "gestion.Vehiculo",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="destinatarios_que_usan",
    )
