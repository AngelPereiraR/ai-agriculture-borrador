from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Transportista(models.Model):
    """Empresa o persona transportista."""

    nombre = models.CharField(max_length=250)
    nif = models.CharField(max_length=30, blank=True, db_index=True)
    direccion = models.ForeignKey(
        "gestion.Direccion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transportistas",
    )
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)


class DocumentoDAT(models.Model):
    """Documento de acompañamiento al transporte (DAT)."""

    numero = models.CharField(max_length=150, unique=True, db_index=True)
    fecha_emision = models.DateField(db_index=True)
    explotacion = models.ForeignKey(
        "gestion.Explotacion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="documentos_dat",
    )
    producto = models.CharField(max_length=200, blank=True)
    cantidad = models.DecimalField(
        max_digits=14, decimal_places=6, null=True, blank=True
    )
    unidad = models.CharField(max_length=20, blank=True)
    observaciones = models.TextField(blank=True)


class RegistroTransporte(models.Model):
    """Registro operativo de transporte realizado."""

    documento_dat = models.ForeignKey(
        "gestion.DocumentoDAT",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="registros_operativos",
    )
    referencia = models.CharField(max_length=120, blank=True, db_index=True)
    dat_numero = models.CharField(max_length=150, blank=True, null=True, db_index=True)

    fecha_transporte = models.DateTimeField(db_index=True)
    tiempo_carga = models.DateTimeField(null=True, blank=True)
    tiempo_descarga = models.DateTimeField(null=True, blank=True)

    explotacion_origen = models.ForeignKey(
        "gestion.Explotacion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transportes_origen",
    )
    persona_origen = models.ForeignKey(
        "gestion.Persona",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transportes_origen_persona",
    )
    destinatario = models.ForeignKey(
        "gestion.Persona",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transportes_destino",
    )

    transportista = models.ForeignKey(
        "gestion.Transportista",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transportes",
    )
    vehiculo = models.ForeignKey(
        "gestion.Vehiculo",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="registros_transporte",
    )
    conductor = models.ForeignKey(
        "gestion.Persona",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transportes_conducidos",
    )

    cantidad = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
    )
    unidad = models.CharField(max_length=20, blank=True, null=True)

    peso_bruto = models.DecimalField(
        max_digits=14, decimal_places=3, null=True, blank=True
    )
    peso_neto = models.DecimalField(
        max_digits=14, decimal_places=3, null=True, blank=True
    )

    pallets = models.IntegerField(null=True, blank=True)
    bultos = models.IntegerField(null=True, blank=True)

    lotes = models.JSONField(null=True, blank=True)
    temperatura_controlada = models.BooleanField(default=False)
    temp_registrada = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )

    ruta = models.JSONField(null=True, blank=True)
    seguimiento_gps = models.JSONField(null=True, blank=True)
    permisos = models.JSONField(null=True, blank=True)

    documentos = models.ManyToManyField(
        "gestion.DocumentoDAT",
        blank=True,
        related_name="registros_transporte_relacionados",
    )
    receptor_firma = models.FileField(upload_to="firmas/", null=True, blank=True)

    estado = models.CharField(max_length=40, blank=True, default="pendiente")
    costo_transporte = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    observaciones = models.TextField(blank=True)
    datos_extra = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
