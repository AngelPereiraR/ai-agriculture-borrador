from django.db import models


class Asesor(models.Model):
    """Entidades o personas asesoras."""

    persona = models.OneToOneField(
        "gestion.Persona",
        on_delete=models.CASCADE,
        related_name="asesor_profile",
        help_text="Persona física o jurídica asociada al asesor",
    )
    numero_inscripcion_ropo = models.CharField(
        "nº inscripción ROPO",
        max_length=50,
        blank=True,
        db_index=True,
        help_text="Número de inscripción en el ROPO (si aplica)",
    )
    tipo_carnet = models.CharField(
        "tipo de carné",
        max_length=50,
        blank=True,
        help_text="Tipo de carné (básico, cualificado, fumigador, piloto, ...)",
    )


class EquipoAplicacion(models.Model):
    """Equipos de aplicación."""

    descripcion = models.CharField("descripción", max_length=250)
    numero_inscripcion_roma = models.CharField(
        "nº inscripción ROMA",
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Número de inscripción ROMA del equipo (si aplica)",
    )
    fecha_adquisicion = models.DateField("fecha adquisición", null=True, blank=True)
    fecha_ultima_inspeccion = models.DateField(
        "fecha última inspección", null=True, blank=True
    )
    explotacion = models.ForeignKey(
        "gestion.Explotacion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="equipos",
        help_text="Explotación propietaria o usuaria del equipo",
    )
