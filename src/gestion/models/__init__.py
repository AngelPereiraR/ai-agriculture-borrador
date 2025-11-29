from .analisis import AnalisisLaboratorio
from .contacto import Direccion, Persona
from .destinatario import Destinatario
from .diario import DiarioActividad, SemillaTratada
from .dummy import Dummy
from .explotacion import Explotacion, Parcela
from .movimientos import RegistroMovimientoProducto
from .operativa import Asesor, EquipoAplicacion
from .personal import Personal
from .titular import Titular
from .transporte import DocumentoDAT, RegistroTransporte, Transportista
from .vehiculo import Vehiculo

__all__ = [
    "Dummy",
    "Direccion",
    "Persona",
    "Explotacion",
    "Parcela",
    "Titular",
    "Vehiculo",
    "Destinatario",
    "Personal",
    "DiarioActividad",
    "SemillaTratada",
    "RegistroMovimientoProducto",
    "AnalisisLaboratorio",
    "Transportista",
    "DocumentoDAT",
    "RegistroTransporte",
    "Asesor",
    "EquipoAplicacion",
]
