from django.contrib import admin

from .models import (
    AnalisisLaboratorio,
    Asesor,
    Destinatario,
    DiarioActividad,
    Direccion,
    DocumentoDAT,
    Dummy,
    EquipoAplicacion,
    Explotacion,
    Parcela,
    Persona,
    Personal,
    RegistroMovimientoProducto,
    RegistroTransporte,
    SemillaTratada,
    Titular,
    Transportista,
    Vehiculo,
)


@admin.register(Dummy)
class DummyAdmin(admin.ModelAdmin):
    list_display = (
        "id","nombre", "creado_en")  # Columnas visibles en la lista
    search_fields = ("nombre",)  # Barra de búsqueda


@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tipo_via",
        "nombre_via",
        "numero",
        "localidad",
        "provincia",
        "pais",
        "codigo_postal",
    )
    search_fields = ("nombre_via", "localidad", "provincia", "codigo_postal")
    list_filter = ("provincia", "pais")


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = (
        "id","nombre", "nif", "sexo", "telefono", "email")
    search_fields = ("nombre", "nif", "email")
    list_filter = ("sexo",)


@admin.register(Explotacion)
class ExplotacionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "nif",
        "numero_registro_nacional",
        "numero_registro_autonomico",
        "titular",
    )
    search_fields = (
        "nombre",
        "nif",
        "numero_registro_nacional",
        "numero_registro_autonomico",
    )
    list_filter = ("tipo_representacion",)


@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "explotacion",
        "referencia_sigpac",
        "poligono",
        "parcela",
        "recinto",
        "especie",
        "superficie_cultivada",
    )
    search_fields = (
        "referencia_sigpac",
        "poligono",
        "parcela",
        "recinto",
        "especie",
        "explotacion__nombre",
    )
    list_filter = ("explotacion", "secano_regadio", "aire_protegido", "especie")


@admin.register(Titular)
class TitularAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "apellidos",
        "tipo_documento",
        "documento",
        "registro_explotacion",
    )
    search_fields = ("nombre", "apellidos", "documento", "registro_explotacion")
    list_filter = ("tipo_documento",)


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = (
        "id","tipo", "matricula", "marca", "modelo")
    search_fields = ("matricula", "marca", "modelo")
    list_filter = ("tipo",)


@admin.register(Destinatario)
class DestinatarioAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "tipo_documento",
        "documento",
        "direccion",
        "transporte_asignado",
    )
    search_fields = ("nombre", "documento")
    list_filter = ("tipo_documento",)


@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "apellidos",
        "sexo",
        "cargo",
        "tipo_documento",
        "documento",
        "habilitado_fitosanitarios",
    )
    search_fields = ("nombre", "apellidos", "documento", "cargo")
    list_filter = ("sexo", "habilitado_fitosanitarios", "tipo_documento")


@admin.register(DiarioActividad)
class DiarioActividadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fecha",
        "tipo",
        "explotacion",
        "parcela",
        "problema_fitosanitario",
        "estado_validacion",
    )
    search_fields = (
        "problema_fitosanitario",
        "producto_nombre",
        "observaciones",
        "explotacion__nombre",
    )
    list_filter = ("fecha", "tipo", "estado_validacion", "explotacion")
    date_hierarchy = "fecha"


@admin.register(SemillaTratada)
class SemillaTratadaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fecha_siembra",
        "cultivo",
        "explotacion",
        "parcela",
        "producto_fitosanitario",
        "cantidad_semilla_kg",
    )
    search_fields = (
        "cultivo",
        "producto_fitosanitario",
        "numero_registro",
        "explotacion__nombre",
    )
    list_filter = ("fecha_siembra", "cultivo", "explotacion")
    date_hierarchy = "fecha_siembra"


@admin.register(RegistroMovimientoProducto)
class RegistroMovimientoProductoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fecha",
        "explotacion",
        "producto",
        "cantidad_kg",
        "numero_albaran",
        "cliente_nombre",
    )
    search_fields = (
        "producto",
        "numero_albaran",
        "numero_lote",
        "cliente_nombre",
        "cliente_nif",
        "explotacion__nombre",
    )
    list_filter = ("fecha", "explotacion")
    date_hierarchy = "fecha"


@admin.register(AnalisisLaboratorio)
class AnalisisLaboratorioAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fecha",
        "explotacion",
        "material_analizado",
        "cultivo",
        "laboratorio",
        "numero_boletin",
    )
    search_fields = (
        "material_analizado",
        "cultivo",
        "laboratorio",
        "numero_boletin",
        "explotacion__nombre",
    )
    list_filter = ("fecha", "explotacion")
    date_hierarchy = "fecha"


@admin.register(Transportista)
class TransportistaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nif", "telefono", "email", "direccion")
    search_fields = ("nombre", "nif", "telefono", "email")


@admin.register(DocumentoDAT)
class DocumentoDATAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "numero",
        "fecha_emision",
        "explotacion",
        "producto",
        "cantidad",
        "unidad",
    )
    search_fields = ("numero", "producto", "explotacion__nombre")
    list_filter = ("fecha_emision", "explotacion")
    date_hierarchy = "fecha_emision"


@admin.register(RegistroTransporte)
class RegistroTransporteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "referencia",
        "fecha_transporte",
        "explotacion_origen",
        "destinatario",
        "vehiculo",
        "estado",
        "cantidad",
    )
    search_fields = (
        "referencia",
        "dat_numero",
        "vehiculo__matricula",
        "transportista__nombre",
    )
    list_filter = (
        "fecha_transporte",
        "estado",
        "temperatura_controlada",
        "transportista",
    )
    date_hierarchy = "fecha_transporte"


@admin.register(Asesor)
class AsesorAdmin(admin.ModelAdmin):
    list_display = (
        "id","persona", "numero_inscripcion_ropo", "tipo_carnet")
    search_fields = ("persona__nombre", "numero_inscripcion_ropo", "tipo_carnet")
    list_filter = ("tipo_carnet",)


@admin.register(EquipoAplicacion)
class EquipoAplicacionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "descripcion",
        "numero_inscripcion_roma",
        "fecha_adquisicion",
        "fecha_ultima_inspeccion",
        "explotacion",
    )
    search_fields = ("descripcion", "numero_inscripcion_roma", "explotacion__nombre")
    list_filter = ("explotacion", "fecha_ultima_inspeccion")
    date_hierarchy = "fecha_ultima_inspeccion"
