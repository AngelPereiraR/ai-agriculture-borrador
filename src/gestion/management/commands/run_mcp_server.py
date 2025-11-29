import logging

from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from fastmcp import FastMCP

# Importamos los modelos de Django
from gestion.models import Dummy

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-django")


class Command(BaseCommand):
    help = "Inicia el servidor FastMCP con contexto de Django"

    def handle(self, *args, **kwargs):
        # 1. Definimos el servidor MCP
        mcp = FastMCP(
            "Agente Agricola Django",
            instructions="Servidor MCP integrado con Django para gestión agrícola.",
        )

        # 2. Definimos la Tool (Herramienta)
        @mcp.tool()
        async def crear_registro_dummy(
            nombre: str, descripcion: str = "Sin descripción"
        ) -> str:
            """
            Crea un registro de prueba en la base de datos de Django.
            Útil para verificar la conexión y el funcionamiento del ORM.
            """
            try:
                nuevo_dummy = await sync_to_async(Dummy.objects.create)(
                    nombre=nombre, descripcion=descripcion
                )

                msg = f"Éxito: Dummy creado con ID {nuevo_dummy.id} - {nuevo_dummy.nombre}"
                logger.info(msg)
                return msg

            except Exception as e:
                error_msg = f"Error al crear dummy: {str(e)}"
                logger.error(error_msg)
                return error_msg

        @mcp.tool()
        async def listar_dummies() -> str:
            """Lista los últimos 5 dummies creados en la base de datos."""

            # Definimos la consulta (QuerySet)
            queryset = Dummy.objects.all().order_by("-creado_en")[:5]

            dummies = await sync_to_async(list)(queryset)

            if not dummies:
                return "No hay registros."

            reporte = "Últimos registros:\n"
            for d in dummies:
                reporte += f"- ID {d.id}: {d.nombre} ({d.creado_en})\n"
            return reporte

        # 3. Ejecutamos el servidor MCP
        self.stdout.write(
            self.style.SUCCESS("Iniciando servidor MCP en puerto 8001...")
        )

        # Usamos transporte HTTP
        mcp.run(transport="http", host="0.0.0.0", port=8001, path="/mcp")
