from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from ..common import TipoActividad


class DiarioActividad(models.Model):
    """Registro de actividad del cuaderno."""

    explotacion = models.ForeignKey(
        "gestion.Explotacion",
        on_delete=models.CASCADE,
        related_name="diario_actividades",
    )
    fecha = models.DateField(db_index=True)
    tipo = models.CharField(
        "tipo actividad",
        max_length=30,
        choices=TipoActividad.choices,
        default=TipoActividad.OTRO,
    )
    parcela = models.ForeignKey(
        "gestion.Parcela",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="diario_actividades",
    )

    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)

    superficie_tratada_ha = models.DecimalField(
        "superficie tratada (ha)",
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )

    problema_fitosanitario = models.CharField(
        "problema fitosanitario", max_length=250, blank=True
    )

    aplicador = models.ForeignKey(
        "gestion.Persona",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="actividades_aplicadas",
    )
    equipo = models.ForeignKey(
        "gestion.EquipoAplicacion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="actividades",
    )

    producto_nombre = models.CharField(
        "producto - nombre comercial", max_length=250, blank=True
    )
    producto_numero_registro = models.CharField(
        "nº registro", max_length=100, blank=True
    )

    dosis = models.DecimalField(
        "dosis",
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    dosis_text = models.CharField(
        "dosis (texto)", max_length=100, blank=True, help_text="Formato libre si aplica"
    )

    eficacia = models.CharField("eficacia", max_length=50, blank=True)
    observaciones = models.TextField(blank=True)
    insumos = models.JSONField("insumos / composición", null=True, blank=True)

    documentos = models.ManyToManyField(
        "gestion.DocumentoDAT", blank=True, related_name="documentos_diario"
    )
    datos_extra = models.JSONField(null=True, blank=True)

    estado_validacion = models.CharField(max_length=30, blank=True, default="pendiente")
    aprobado_por = models.ForeignKey(
        "gestion.Persona",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="aprobaciones_diario",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)


class SemillaTratada(models.Model):
    """Registro de uso de semilla tratada."""

    explotacion = models.ForeignKey(
        "gestion.Explotacion",
        on_delete=models.CASCADE,
        related_name="semillas_tratadas",
    )
    fecha_siembra = models.DateField(db_index=True)
    parcela = models.ForeignKey(
        "gestion.Parcela",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="siembras",
    )
    cultivo = models.CharField("cultivo", max_length=150, blank=True)
    superficie_sembrada_ha = models.DecimalField(
        "superficie sembrada (ha)",
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    cantidad_semilla_kg = models.DecimalField(
        "cantidad semilla (kg)",
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    producto_fitosanitario = models.CharField(
        "producto fitosanitario", max_length=250, blank=True
    )
    numero_registro = models.CharField("nº registro", max_length=100, blank=True)
    observaciones = models.TextField(blank=True)
