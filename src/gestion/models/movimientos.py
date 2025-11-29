from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class RegistroMovimientoProducto(models.Model):
    """Movimientos de producto: ventas, albaranes, salidas."""

    explotacion = models.ForeignKey(
        "gestion.Explotacion",
        on_delete=models.CASCADE,
        related_name="movimientos_producto",
    )
    fecha = models.DateField(db_index=True)
    producto = models.CharField("producto", max_length=200)
    cantidad_kg = models.DecimalField(
        "cantidad (kg)",
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    numero_albaran = models.CharField(
        "nº albarán / factura", max_length=100, blank=True
    )
    numero_lote = models.CharField("nº de lote", max_length=100, blank=True)
    cliente_nombre = models.CharField("cliente", max_length=250, blank=True)
    cliente_nif = models.CharField("NIF cliente", max_length=30, blank=True)
    cliente_direccion = models.JSONField(null=True, blank=True)
    numero_rgseaa = models.CharField("nº RGSEAA", max_length=100, blank=True)
