from django.db import models

from ..common import Sexo, TipoDocumento


class Personal(models.Model):
    nombre = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=150)
    sexo = models.CharField(max_length=1, choices=Sexo.choices)
    tipo_documento = models.CharField(max_length=20, choices=TipoDocumento.choices)
    documento = models.CharField(max_length=20, unique=True)
    cargo = models.CharField(max_length=150)
    habilitado_fitosanitarios = models.BooleanField(default=False)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
