from django.db import models

from ..common import TipoRepresentacion


class Explotacion(models.Model):
    """Datos generales de la explotación / unidad de producción."""

    nombre = models.CharField("nombre explotación / comercial", max_length=250)
    nif = models.CharField("NIF explotación", max_length=30, blank=True, db_index=True)
    numero_registro_nacional = models.CharField(
        "nº registro nacional", max_length=100, blank=True
    )
    numero_registro_autonomico = models.CharField(
        "nº registro autonómico", max_length=100, blank=True
    )
    direccion = models.ForeignKey(
        "gestion.Direccion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="explotaciones",
    )
    titular = models.ForeignKey(
        "gestion.Persona",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="explotaciones_titular",
    )
    tipo_representacion = models.CharField(
        "tipo de representación",
        max_length=50,
        choices=TipoRepresentacion.choices,
        blank=True,
    )

    class Meta:
        verbose_name = "Explotación"
        verbose_name_plural = "Explotaciones"

    def __str__(self):
        return f"{self.nombre} ({self.nif})" if self.nif else self.nombre


class Parcela(models.Model):
    """Parcelas identificadas con SIGPAC u otra referencia."""

    explotacion = models.ForeignKey(
        "gestion.Explotacion", on_delete=models.CASCADE, related_name="parcelas"
    )
    referencia_sigpac = models.CharField(
        "referencia SIGPAC", max_length=100, blank=True, db_index=True
    )
    poligono = models.CharField("polígono", max_length=50, blank=True)
    parcela = models.CharField("parcela", max_length=50, blank=True)
    recinto = models.CharField("recinto", max_length=50, blank=True)
    uso_sigpac = models.CharField("uso SIGPAC", max_length=100, blank=True)
    superficie_sigpac = models.DecimalField(
        "superficie SIGPAC (ha)", max_digits=10, decimal_places=4, null=True, blank=True
    )
    superficie_cultivada = models.DecimalField(
        "superficie cultivada (ha)",
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
    )
    especie = models.CharField("especie", max_length=150, blank=True)
    variedad = models.CharField("variedad", max_length=150, blank=True)
    secano_regadio = models.CharField("secano/regadío", max_length=20, blank=True)
    aire_protegido = models.CharField(
        "aire libre / protegido", max_length=20, blank=True
    )
