from django.db import models


class AnalisisLaboratorio(models.Model):
    """Registro de análisis de laboratorio."""

    explotacion = models.ForeignKey(
        "gestion.Explotacion", on_delete=models.CASCADE, related_name="analisis"
    )
    fecha = models.DateField(db_index=True)
    material_analizado = models.CharField(
        "material analizado", max_length=200, blank=True
    )
    cultivo = models.CharField("cultivo / cosecha", max_length=200, blank=True)
    numero_boletin = models.CharField(
        "nº boletín de análisis", max_length=100, blank=True
    )
    laboratorio = models.CharField("laboratorio", max_length=250, blank=True)
    sustancias_activas_detectadas = models.TextField(blank=True)
