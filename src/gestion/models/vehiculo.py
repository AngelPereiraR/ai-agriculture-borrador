from django.db import models

from ..common import TipoVehiculo


class Vehiculo(models.Model):
    tipo = models.CharField(max_length=20, choices=TipoVehiculo.choices)
    matricula = models.CharField(max_length=20, unique=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
