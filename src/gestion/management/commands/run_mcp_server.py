import logging
from datetime import date, datetime

from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from django.db.models import Q
from fastmcp import FastMCP

# Importación de TODOS los modelos necesarios del sistema
from gestion.models import (
    AnalisisLaboratorio,
    Asesor,
    Destinatario,
    DiarioActividad,
    Direccion,
    DocumentoDAT,
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

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-django")


class Command(BaseCommand):
    help = "Inicia el servidor FastMCP con contexto de Django para Agricultura"

    def handle(self, *args, **kwargs):
        mcp = FastMCP(
            "Agente Agricola Django",
            instructions="Servidor MCP para gestión integral de datos agrícolas (Maestros, Cuaderno y DAT).",
        )

        # ==============================================================================
        # 1. HERRAMIENTAS DE CONFIGURACIÓN Y MAESTROS (Configuración Inicial)
        # ==============================================================================

        @mcp.tool()
        async def crear_titular(
            nombre: str,
            nif: str,
            registro_explotacion: str,
            apellidos: str = "",
            tipo_documento: str = "DNI",
            cif_explotacion: str = "",
            # Campos de Dirección y Contacto
            direccion_via: str = "",
            direccion_numero: str = "",
            municipio: str = "",
            provincia: str = "",
            codigo_postal: str = "",
            telefono: str = "",
            movil: str = "",
            email: str = "",
        ) -> str:
            """
            Crea un registro en el modelo Titular y su Dirección asociada.
            Comando asociado: /nuevo_titular
            """
            try:
                # 1. Verificar existencia
                if await sync_to_async(Titular.objects.filter(documento=nif).exists)():
                    return f"Error: Ya existe un titular con el documento {nif}."

                # 2. Crear Dirección (si se proporcionan datos básicos)
                direccion_obj = None
                if direccion_via or municipio or provincia:
                    direccion_obj = await sync_to_async(Direccion.objects.create)(
                        nombre_via=direccion_via,
                        numero=direccion_numero,
                        localidad=municipio,
                        provincia=provincia,
                        codigo_postal=codigo_postal,
                        telefono=telefono,
                        movil=movil,
                        email=email,
                    )

                # 3. Crear Titular
                obj = await sync_to_async(Titular.objects.create)(
                    nombre=nombre,
                    apellidos=apellidos,
                    documento=nif,
                    tipo_documento=tipo_documento.upper(),
                    registro_explotacion=registro_explotacion,
                    cif_explotacion=cif_explotacion if cif_explotacion else None,
                    direccion=direccion_obj,
                )

                info_dir = (
                    f" con dirección en {municipio}"
                    if direccion_obj
                    else " sin dirección"
                )
                return f"Titular creado: {obj.nombre} {obj.apellidos or ''} (REGA: {obj.registro_explotacion}){info_dir}."

            except Exception as e:
                return f"Error creando titular: {str(e)}"

        @mcp.tool()
        async def configurar_explotacion_principal(
            nombre_comercial: str,
            nif_titular: str,
            registro_nacional: str,
            registro_autonomico: str = "",
            nombre_titular: str = "",
            apellidos_titular: str = "",
            cif_explotacion: str = "",
            # Campos de Dirección
            direccion_via: str = "",
            direccion_numero: str = "",
            municipio: str = "",
            provincia: str = "",
            codigo_postal: str = "",
        ) -> str:
            """
            Configura la Explotación Agrícola principal, su titular y dirección.
            Comando asociado: /config_explotacion
            """
            try:
                # 1. Crear Dirección de la Explotación (si hay datos)
                direccion_obj = None
                if direccion_via or municipio or provincia:
                    direccion_obj = await sync_to_async(Direccion.objects.create)(
                        nombre_via=direccion_via,
                        numero=direccion_numero,
                        localidad=municipio,
                        provincia=provincia,
                        codigo_postal=codigo_postal,
                    )

                # 2. Crear o recuperar el Titular
                nombre_t = (
                    nombre_titular if nombre_titular else f"Titular {nif_titular}"
                )

                titular, created = await sync_to_async(Titular.objects.get_or_create)(
                    documento=nif_titular,
                    defaults={
                        "nombre": nombre_t,
                        "apellidos": apellidos_titular,
                        "tipo_documento": "DNI",
                        "registro_explotacion": registro_nacional,
                        "cif_explotacion": cif_explotacion,
                    },
                )

                # Actualización de titular si ya existía
                if not created:
                    update_t = False
                    if nombre_titular and titular.nombre != nombre_titular:
                        titular.nombre = nombre_titular
                        update_t = True
                    if apellidos_titular and titular.apellidos != apellidos_titular:
                        titular.apellidos = apellidos_titular
                        update_t = True
                    if update_t:
                        await sync_to_async(titular.save)()

                # 3. Crear o actualizar la Explotación
                explotacion, created_exp = await sync_to_async(
                    Explotacion.objects.update_or_create
                )(
                    nif=nif_titular,
                    defaults={
                        "nombre": nombre_comercial,
                        "numero_registro_nacional": registro_nacional,
                        "numero_registro_autonomico": registro_autonomico,
                        "titular": titular,
                        "direccion": direccion_obj,  # Vinculamos la dirección creada
                        "tipo_representacion": "PROPIETARIO",
                    },
                )

                info_dir = f" en {municipio}" if direccion_obj else ""
                return f"Explotación '{nombre_comercial}' configurada{info_dir}. Titular: {titular.nombre}."
            except Exception as e:
                return f"Error en configuración inicial: {str(e)}"

        @mcp.tool()
        async def crear_parcela(
            nombre_comun: str,
            referencia_sigpac: str,
            cultivo: str,
            superficie_ha: float,
            poligono: str = "",
            parcela: str = "",
            recinto: str = "",
            uso_sigpac: str = "",
            variedad: str = "",
            secano_regadio: str = "",
            aire_protegido: str = "",
        ) -> str:
            """
            Da de alta una nueva parcela.
            Comando asociado: /nueva_parcela
            """
            try:
                explotacion = await sync_to_async(Explotacion.objects.first)()
                if not explotacion:
                    return "Error: No hay una explotación configurada. Usa /config_explotacion primero."

                await sync_to_async(Parcela.objects.create)(
                    explotacion=explotacion,
                    referencia_sigpac=referencia_sigpac,
                    poligono=poligono,
                    parcela=parcela,
                    recinto=recinto,
                    uso_sigpac=uso_sigpac,
                    especie=cultivo,
                    variedad=variedad,
                    secano_regadio=secano_regadio,
                    aire_protegido=aire_protegido,
                    superficie_cultivada=superficie_ha,
                    superficie_sigpac=superficie_ha,
                )
                return f"Parcela creada: {cultivo} {variedad} en {referencia_sigpac} ({superficie_ha} ha) - Alias: {nombre_comun}"
            except Exception as e:
                return f"Error creando parcela: {str(e)}"

        @mcp.tool()
        async def crear_cliente_destinatario(
            nombre_fiscal: str,
            nif: str,
            matricula_vehiculo_preferido: str = None,
            # Campos de Dirección opcionales
            direccion_via: str = "",
            direccion_numero: str = "",
            municipio: str = "",
            provincia: str = "",
            codigo_postal: str = "",
        ) -> str:
            """
            Crea un cliente/destinatario y le asigna un vehículo preferido para automatizar DATs.
            Comando asociado: /nuevo_cliente
            """
            try:
                # 1. Gestionar Vehículo
                vehiculo = None
                if matricula_vehiculo_preferido:
                    vehiculo = await sync_to_async(
                        Vehiculo.objects.filter(
                            matricula=matricula_vehiculo_preferido
                        ).first
                    )()
                    if not vehiculo:
                        return f"Error: El vehículo {matricula_vehiculo_preferido} no existe. Regístralo con /nuevo_vehiculo."

                # 2. Crear Dirección (si aplica)
                direccion_obj = None
                if direccion_via or municipio or provincia:
                    direccion_obj = await sync_to_async(Direccion.objects.create)(
                        nombre_via=direccion_via,
                        numero=direccion_numero,
                        localidad=municipio,
                        provincia=provincia,
                        codigo_postal=codigo_postal,
                    )

                # 3. Crear Destinatario (Modelo específico)
                destinatario, created = await sync_to_async(
                    Destinatario.objects.get_or_create
                )(
                    documento=nif,
                    defaults={
                        "nombre": nombre_fiscal,
                        "tipo_documento": "DNI",  # Valor por defecto
                        "transporte_asignado": vehiculo,
                        "direccion": direccion_obj,
                    },
                )

                # Actualización si ya existía
                update_needed = False
                if not created:
                    if vehiculo and destinatario.transporte_asignado != vehiculo:
                        destinatario.transporte_asignado = vehiculo
                        update_needed = True
                    if direccion_obj and destinatario.direccion != direccion_obj:
                        destinatario.direccion = direccion_obj
                        update_needed = True
                    if update_needed:
                        await sync_to_async(destinatario.save)()

                # 4. Sincronizar con Persona (para que RegistroTransporte funcione con FK a Persona)
                await sync_to_async(Persona.objects.get_or_create)(
                    nif=nif,
                    defaults={"nombre": nombre_fiscal, "direccion": direccion_obj},
                )

                info_vehiculo = (
                    f"Vehículo asignado: {vehiculo.matricula}"
                    if vehiculo
                    else "Sin vehículo asignado"
                )
                return f"Cliente '{nombre_fiscal}' configurado. {info_vehiculo}"
            except Exception as e:
                return f"Error creando cliente: {str(e)}"

        @mcp.tool()
        async def crear_vehiculo(
            matricula: str, tipo: str, marca: str = "", modelo: str = ""
        ) -> str:
            """
            Registra un vehículo.
            Comando asociado: /nuevo_vehiculo
            """
            try:
                obj = await sync_to_async(Vehiculo.objects.create)(
                    matricula=matricula,
                    tipo=tipo.upper(),  # TRACTOR, COCHE, REMOLQUE, FURGONETA
                    marca=marca,
                    modelo=modelo,
                )
                return f"Vehículo registrado: {obj.tipo} - {obj.matricula} ({obj.marca} {obj.modelo})"
            except Exception as e:
                return f"Error creando vehículo: {str(e)}"

        @mcp.tool()
        async def crear_maquina_roma(
            descripcion: str,
            numero_inscripcion_roma: str,
            fecha_adquisicion: str = None,
            fecha_ultima_inspeccion: str = None,
        ) -> str:
            """
            Registra maquinaria de aplicación (ROMA) con sus fechas.
            Comando asociado: /nueva_maquina
            """
            try:
                explotacion = await sync_to_async(Explotacion.objects.first)()
                if not explotacion:
                    return "Error: No hay una explotación configurada."

                obj = await sync_to_async(EquipoAplicacion.objects.create)(
                    descripcion=descripcion,
                    numero_inscripcion_roma=numero_inscripcion_roma,
                    fecha_adquisicion=fecha_adquisicion,
                    fecha_ultima_inspeccion=fecha_ultima_inspeccion,
                    explotacion=explotacion,
                )
                return f"Máquina registrada: {obj.descripcion} (ROMA: {obj.numero_inscripcion_roma})"
            except Exception as e:
                return f"Error registrando máquina: {str(e)}"

        @mcp.tool()
        async def crear_personal_aplicador(
            nombre: str,
            documento: str,
            apellidos: str = "",
            sexo: str = "O",
            tipo_documento: str = "DNI",
            cargo: str = "",
            habilitado_fitosanitarios: bool = False,
            telefono: str = "",
            email: str = "",
        ) -> str:
            """
            Registra personal/aplicador con todos sus detalles.
            Comando asociado: /nuevo_personal
            """
            try:
                # 1. Crear Persona (Base para FKs en DiarioActividad)
                # Usamos 'nif' en Persona para mapear con 'documento' de Personal
                persona, _ = await sync_to_async(Persona.objects.get_or_create)(
                    nif=documento,
                    defaults={
                        "nombre": f"{nombre} {apellidos}".strip(),
                        "telefono": telefono,
                        "email": email,
                        "sexo": sexo,
                    },
                )

                # 2. Crear Personal (Datos específicos de RRHH/Cualificación)
                # Si no se especifica cargo pero se marca habilitado, inferir Aplicador
                cargo_final = (
                    cargo
                    if cargo
                    else ("Aplicador" if habilitado_fitosanitarios else "Trabajador")
                )

                await sync_to_async(Personal.objects.create)(
                    nombre=nombre,
                    apellidos=apellidos,
                    documento=documento,
                    tipo_documento=tipo_documento.upper(),
                    sexo=sexo.upper(),
                    cargo=cargo_final,
                    habilitado_fitosanitarios=habilitado_fitosanitarios,
                    telefono=telefono,
                    email=email,
                )

                return f"Personal registrado: {nombre} {apellidos} (Doc: {documento}). Cargo: {cargo_final}"
            except Exception as e:
                return f"Error registrando personal: {str(e)}"

        @mcp.tool()
        async def crear_asesor_tecnico(
            nombre: str, nif: str, codigo_ropo: str, tipo_asesoramiento: str = ""
        ) -> str:
            """
            Registra un Asesor Técnico (GIP).
            Comando asociado: /nuevo_asesor
            """
            try:
                persona, _ = await sync_to_async(Persona.objects.get_or_create)(
                    nif=nif, defaults={"nombre": nombre}
                )

                await sync_to_async(Asesor.objects.create)(
                    persona=persona,
                    numero_inscripcion_ropo=codigo_ropo,
                    tipo_carnet=tipo_asesoramiento,
                )
                return f"Asesor registrado: {nombre} (ROPO: {codigo_ropo})"
            except Exception as e:
                return f"Error creando asesor: {str(e)}"

        @mcp.tool()
        async def crear_transportista_externo(
            nombre: str, nif: str, telefono: str = "", email: str = ""
        ) -> str:
            """
            Registra un transportista externo con sus datos de contacto.
            Comando asociado: /nuevo_transportista
            """
            try:
                await sync_to_async(Transportista.objects.create)(
                    nombre=nombre, nif=nif, telefono=telefono, email=email
                )
                return f"Transportista registrado: {nombre} (Tel: {telefono})"
            except Exception as e:
                return f"Error creando transportista: {str(e)}"

        # ==============================================================================
        # 2. HERRAMIENTAS OPERATIVAS (Día a día en el campo)
        # ==============================================================================

        @mcp.tool()
        async def registrar_tratamiento(
            fecha: str,
            referencia_sigpac: str,
            producto: str,
            dosis: float,
            plaga: str,
            dosis_text: str = "",
            eficacia: str = "",
            nombre_equipo: str = "",
            observaciones: str = "",
        ) -> str:
            """
            Registra una aplicación de fitosanitarios buscando correctamente el aplicador.
            Comando asociado: /tratamiento
            """

            def _operacion_db():
                # 1. Buscar Parcela
                parcela = (
                    Parcela.objects.filter(
                        Q(referencia_sigpac__icontains=referencia_sigpac)
                        | Q(especie__icontains=referencia_sigpac)
                    )
                    .select_related("explotacion")
                    .first()
                )

                if not parcela:
                    return f"Error: Parcela '{referencia_sigpac}' no encontrada."

                # 2. Buscar Aplicador (Lógica corregida: Personal -> Persona)
                # Buscamos primero en Personal a alguien con carné
                aplicador_persona = Personal.objects.filter(
                    habilitado_fitosanitarios=True
                ).first()

                if not aplicador_persona:
                    return "Error: No hay personas registradas para asignar como aplicador."

                # 3. Buscar Equipo (Opcional)
                equipo = None
                if nombre_equipo:
                    equipo = EquipoAplicacion.objects.filter(
                        descripcion__icontains=nombre_equipo
                    ).first()

                # 4. Crear Registro
                actividad = DiarioActividad.objects.create(
                    explotacion=parcela.explotacion,
                    fecha=fecha,
                    tipo="TRATAMIENTO",
                    parcela=parcela,
                    superficie_tratada_ha=parcela.superficie_cultivada,
                    producto_nombre=producto,
                    dosis=dosis,
                    dosis_text=dosis_text,
                    problema_fitosanitario=plaga,
                    eficacia=eficacia,
                    equipo=equipo,
                    observaciones=observaciones,
                    aplicador=aplicador_persona,
                )
                return f"Tratamiento registrado ID: {actividad.id}. {producto} contra {plaga} en {parcela.referencia_sigpac}."

            try:
                resultado = await sync_to_async(_operacion_db)()
                return resultado
            except Exception as e:
                return f"Error al registrar tratamiento: {str(e)}"

        @mcp.tool()
        async def registrar_riego(
            fecha: str,
            referencia_sigpac: str,
            tipo_actividad: str,  # "Riego" o "Abonado"
            abono: str = "",
            cantidad: float = 0.0,
            unidad_cantidad: str = "",
            hora_inicio: str = None,
            hora_fin: str = None,
            observaciones: str = "",
        ) -> str:
            """
            Registra riego o fertilización con detalles de tiempo y dosis.
            Comando asociado: /riego
            """

            def _operacion_db():
                # 1. Buscar Parcela
                parcela = (
                    Parcela.objects.filter(
                        Q(referencia_sigpac__icontains=referencia_sigpac)
                        | Q(especie__icontains=referencia_sigpac)
                    )
                    .select_related("explotacion")
                    .first()
                )

                if not parcela:
                    return f"Error: Parcela '{referencia_sigpac}' no encontrada."

                tipo_db = (
                    "ABONADO" if "abono" in tipo_actividad.lower() or abono else "RIEGO"
                )

                # 2. Crear Registro
                actividad = DiarioActividad.objects.create(
                    explotacion=parcela.explotacion,
                    fecha=fecha,
                    tipo=tipo_db,
                    parcela=parcela,
                    superficie_tratada_ha=parcela.superficie_cultivada,
                    producto_nombre=abono,  # Si es solo agua, esto estará vacío o indicará "Agua"
                    dosis=cantidad,
                    dosis_text=unidad_cantidad,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    observaciones=f"Registro de {tipo_actividad}. {observaciones}",
                )
                return f"Actividad de {tipo_db} registrada ID: {actividad.id}."

            try:
                resultado = await sync_to_async(_operacion_db)()
                return resultado
            except Exception as e:
                return f"Error al registrar riego: {str(e)}"

        @mcp.tool()
        async def registrar_siembra(
            fecha: str,
            referencia_sigpac: str,
            cultivo: str,
            kilos_semilla: float,
            producto_semilla: str = "",
            registro_producto: str = "",
            observaciones: str = "",
        ) -> str:
            """
            Registra siembra con semilla tratada.
            Comando asociado: /siembra
            """
            try:
                # Buscar parcela por referencia o cultivo (nombre común a veces coincide)
                parcela = await sync_to_async(
                    Parcela.objects.filter(
                        Q(referencia_sigpac__icontains=referencia_sigpac)
                        | Q(especie__icontains=referencia_sigpac)
                    )
                    .select_related("explotacion")
                    .first
                )()

                if not parcela:
                    return f"Error: Parcela '{referencia_sigpac}' no encontrada."

                await sync_to_async(SemillaTratada.objects.create)(
                    explotacion=parcela.explotacion,
                    fecha_siembra=fecha,
                    parcela=parcela,
                    cultivo=cultivo,
                    superficie_sembrada_ha=parcela.superficie_cultivada,
                    cantidad_semilla_kg=kilos_semilla,
                    producto_fitosanitario=producto_semilla,
                    numero_registro=registro_producto,
                    observaciones=observaciones,
                )
                return f"Siembra registrada: {cultivo} en {parcela.referencia_sigpac}. Tratamiento semilla: {producto_semilla}"
            except Exception as e:
                return f"Error al registrar siembra: {str(e)}"

        @mcp.tool()
        async def registrar_analisis(
            fecha: str,
            material: str,
            cultivo: str,
            numero_boletin: str,
            laboratorio: str,
            resultado: str,
        ) -> str:
            """
            Registra análisis de laboratorio completo.
            Comando asociado: /analisis
            """
            try:
                explotacion = await sync_to_async(Explotacion.objects.first)()
                if not explotacion:
                    return "Error: No hay explotación configurada."

                obj = await sync_to_async(AnalisisLaboratorio.objects.create)(
                    explotacion=explotacion,
                    fecha=fecha,
                    material_analizado=material,
                    cultivo=cultivo,
                    numero_boletin=numero_boletin,
                    laboratorio=laboratorio,
                    sustancias_activas_detectadas=resultado,
                )
                return f"Análisis registrado ID: {obj.id} (Bol: {numero_boletin})."
            except Exception as e:
                return f"Error al registrar análisis: {str(e)}"

        # ==============================================================================
        # 3. HERRAMIENTAS DE GESTIÓN DOCUMENTAL (DAT y Ventas)
        # ==============================================================================

        @mcp.tool()
        async def generar_dat(
            nombre_destinatario: str,
            productos: list[str],
            cantidades: list[float],
            unidades: list[str],
            variedades: list[str] = [],
            matricula_remolque: str = "",
            nif_transportista: str = "",
            nombre_transportista: str = "",
            telefono_transportista: str = "",
            email_transportista: str = "",
            fecha_entrega_estimada: str = "",
            nombre_autorizado: str = "",
            nif_autorizado: str = "",
            es_ecologico: bool = False,
            es_integrada: bool = False,
            denominacion_origen: str = "",
            indicacion_geografica: str = "",
            especialidad_tradicional: str = "",
            categoria: str = "",
            naturaleza: str = "",
            finalidad: str = "",
            instrucciones_uso: str = "",
            condiciones_transporte: str = "",
        ) -> str:
            """
            Genera los datos completos para el Documento de Acompañamiento al Transporte (DAT).
            Busca datos en los modelos (Transportista, Persona) si se proporcionan NIFs.
            """
            try:
                # 0. Validaciones básicas
                if not (len(productos) == len(cantidades) == len(unidades)):
                    return "Error: Las listas de productos, cantidades y unidades deben tener la misma longitud."

                variedades_safe = variedades + [""] * (len(productos) - len(variedades))

                # 1. Recuperar Destinatario y Explotación (Base)
                destinatario = await sync_to_async(
                    Destinatario.objects.filter(nombre__icontains=nombre_destinatario)
                    .select_related("transporte_asignado", "direccion")
                    .first
                )()

                if not destinatario:
                    return f"Error: Destinatario '{nombre_destinatario}' no encontrado. Créalo con /nuevo_cliente."

                explotacion = await sync_to_async(
                    Explotacion.objects.select_related("titular", "direccion").first
                )()
                if not explotacion:
                    return "Error: No hay Explotación configurada como origen."

                # 2. LÓGICA INTELIGENTE: TRANSPORTISTA
                t_nombre = nombre_transportista or "(Rellenar)"
                t_nif = nif_transportista or "VACÍO"
                t_tel = telefono_transportista or "VACÍO"
                t_email = email_transportista or "VACÍO"

                if nif_transportista:
                    transp_db = await sync_to_async(
                        Transportista.objects.filter(nif=nif_transportista).first
                    )()
                    if transp_db:
                        t_nombre = transp_db.nombre
                        t_tel = transp_db.telefono or t_tel
                        t_email = transp_db.email or t_email
                    else:
                        persona_transp = await sync_to_async(
                            Persona.objects.filter(nif=nif_transportista).first
                        )()
                        if persona_transp:
                            t_nombre = persona_transp.nombre
                            t_tel = (
                                persona_transp.telefono or persona_transp.movil or t_tel
                            )
                            t_email = persona_transp.email or t_email

                # 3. LÓGICA INTELIGENTE: AUTORIZADO
                auth_nom = nombre_autorizado or "VACÍO"
                auth_nif = nif_autorizado or "VACÍO"

                if nif_autorizado:
                    persona_auth = await sync_to_async(
                        Persona.objects.filter(nif=nif_autorizado).first
                    )()
                    if persona_auth:
                        auth_nom = persona_auth.nombre

                titular = explotacion.titular
                if (
                    auth_nom == "VACÍO"
                    and explotacion.tipo_representacion == "REPRESENTANTE"
                    and titular
                ):
                    auth_nom = titular.nombre
                    auth_nif = titular.documento

                # 4. Buscar Parcela de Origen
                parcela_origen = await sync_to_async(
                    Parcela.objects.filter(
                        explotacion=explotacion, especie__icontains=productos[0]
                    ).first
                )()

                # 5. Generar Registros en BD
                vehiculo = destinatario.transporte_asignado
                numero_dat = f"DAT-{datetime.now().strftime('%Y%m%d-%H%M')}"
                obs = f"Destino: {destinatario.nombre}. Eco: {es_ecologico}. Total líneas: {len(productos)}"

                nuevo_dat = await sync_to_async(DocumentoDAT.objects.create)(
                    numero=numero_dat,
                    fecha_emision=date.today(),
                    explotacion=explotacion,
                    producto=productos[0],
                    cantidad=cantidades[0],
                    unidad=unidades[0],
                    observaciones=obs,
                )

                await sync_to_async(RegistroTransporte.objects.create)(
                    documento_dat=nuevo_dat,
                    fecha_transporte=datetime.now(),
                    destinatario=destinatario,
                    vehiculo=vehiculo,
                    cantidad=cantidades[0],
                    unidad=unidades[0],
                    estado="emitido",
                )

                # 6. Reporte Final
                def fmt_parts(d):
                    if not d:
                        return {
                            "via": "",
                            "nombre": "",
                            "num": "",
                            "cp": "",
                            "loc": "",
                            "prov": "",
                            "entidad": "",
                            "pais": "",
                        }
                    return {
                        "via": d.tipo_via or "",
                        "nombre": d.nombre_via or "",
                        "num": d.numero or "",
                        "cp": d.codigo_postal or "",
                        "loc": d.localidad or "",
                        "prov": d.provincia or "",
                        "entidad": d.entidad_poblacion or d.localidad or "",
                        "pais": d.pais or "España",
                    }

                org = fmt_parts(explotacion.direccion)
                dst = fmt_parts(destinatario.direccion)

                # Datos Titular
                t_nombre = titular.nombre if titular else explotacion.nombre
                t_nif = titular.documento if titular else explotacion.nif

                t_tel = "VACÍO"
                t_movil = ""
                t_email = "VACÍO"
                check_sexo_h = "[ ]"
                check_sexo_m = "[ ]"

                if t_nif:
                    persona_titular = await sync_to_async(
                        Persona.objects.filter(nif=t_nif).first
                    )()
                    if persona_titular:
                        t_tel = persona_titular.telefono or "VACÍO"
                        t_movil = persona_titular.movil or ""
                        t_email = persona_titular.email or "VACÍO"
                        if persona_titular.sexo == "H":
                            check_sexo_h = "[X]"
                        if persona_titular.sexo == "M":
                            check_sexo_m = "[X]"

                # Datos Destinatario (Extra)
                persona_dest = await sync_to_async(
                    Persona.objects.filter(nif=destinatario.documento).first
                )()
                dest_tel = persona_dest.telefono if persona_dest else ""
                dest_movil = persona_dest.movil if persona_dest else ""
                dest_email = persona_dest.email if persona_dest else ""

                # Sigpac
                sigpac_data = {"prov": "", "mun": "", "pol": "", "par": "", "rec": ""}
                if parcela_origen:
                    sigpac_data = {
                        "prov": (
                            explotacion.direccion.provincia
                            if explotacion.direccion
                            else ""
                        ),
                        "mun": (
                            explotacion.direccion.localidad
                            if explotacion.direccion
                            else ""
                        ),
                        "pol": parcela_origen.poligono or "",
                        "par": parcela_origen.parcela or "",
                        "rec": parcela_origen.recinto or "",
                    }

                # Transporte
                v_mat = vehiculo.matricula if vehiculo else "PENDIENTE DE ASIGNAR"
                fecha_salida = datetime.now().strftime("%d/%m/%Y")
                hora_salida = datetime.now().strftime("%H:%M")

                check_dop = (
                    f"[X] {denominacion_origen}"
                    if denominacion_origen
                    else "[ ] Denominación de Origen Protegida"
                )
                check_igp = (
                    f"[X] {indicacion_geografica}"
                    if indicacion_geografica
                    else "[ ] Indicación Geográfica Protegida"
                )
                check_etg = (
                    f"[X] {especialidad_tradicional}"
                    if especialidad_tradicional
                    else "[ ] Especialidad Tradicional Garantizada"
                )
                check_eco = (
                    "[X] Producción ecológica"
                    if es_ecologico
                    else "[ ] Producción ecológica"
                )
                check_int = (
                    "[X] Producción integrada de Andalucía"
                    if es_integrada
                    else "[ ] Producción integrada de Andalucía"
                )
                es_calidad_dif = (
                    "SÍ"
                    if (
                        denominacion_origen
                        or indicacion_geografica
                        or especialidad_tradicional
                    )
                    else "NO"
                )

                lineas_carga = ""
                for i, (prod, cant, unid, var) in enumerate(
                    zip(productos, cantidades, unidades, variedades_safe), 1
                ):
                    lineas_carga += f"\n* LÍNEA {i}:\n - Denominación: {prod}\n - Variedad: {var or 'VACÍO'}\n - Unidad: {unid}\n - Cantidad: {cant}"

                reporte = f"""DAT GENERADO: {numero_dat}
--------------------------------------------------------------------------------
1. ORIGEN DEL PORTE
1.1 TITULAR:
- Nombre/Razón Social: {t_nombre}
- DNI/NIE/NIF: {t_nif} | Sexo: {check_sexo_h}H {check_sexo_m}M
- Domicilio: {org['via']} {org['nombre']} Nº {org['num']}
- Entidad Población: {org['entidad']} | Municipio: {org['loc']}
- Provincia: {org['prov']} | CP: {org['cp']} | País: {org['pais']}
- Teléfono: {t_tel} | Móvil: {t_movil} | Email: {t_email}
- Autorizado: {auth_nom} | DNI Autorizado: {auth_nif}

1.2 UNIDAD DE PRODUCCIÓN (SIGPAC):
- Nombre Explotación: {explotacion.nombre}
- Provincia: {sigpac_data['prov']} | Municipio: {sigpac_data['mun']}
- Polígono: {sigpac_data['pol']} | Parcela: {sigpac_data['par']} | Recinto: {sigpac_data['rec']}

--------------------------------------------------------------------------------
2. DESTINATARIO
- Nombre/Razón Social: {destinatario.nombre}
- DNI/NIE/NIF: {destinatario.documento}
- Domicilio: {dst['via']} {dst['nombre']} Nº {dst['num']}
- Entidad Población: {dst['entidad']} | Municipio: {dst['loc']}
- Provincia: {dst['prov']} | CP: {dst['cp']} | País: {dst['pais']}
- Teléfono: {dest_tel} | Móvil: {dest_movil} | Email: {dest_email}

--------------------------------------------------------------------------------
3. TRANSPORTISTA / REBUSCADOR
- NIF: {t_nif}
- Nombre: {t_nombre}
- Matrícula Vehículo: {v_mat}
- Matrícula Remolque: {matricula_remolque}
- Teléfono: {t_tel} | Email: {t_email}

--------------------------------------------------------------------------------
4. DATOS DEL PORTE
- Fecha Salida: {fecha_salida} | Hora: {hora_salida}
- Fecha Entrega Estimada: {fecha_entrega_estimada}
{lineas_carga}

--------------------------------------------------------------------------------
5. CALIDAD COMERCIAL
- ¿Calidad Diferenciada? {es_calidad_dif}
- {check_dop}
- {check_igp}
- {check_etg}
- {check_eco}
- {check_int}
- Naturaleza/Composición: {naturaleza}
- Utilización/Finalidad: {finalidad}
- Categoría: {categoria}
- Instrucciones de uso: {instrucciones_uso}
- Condiciones producción/distribución: {condiciones_transporte}

--------------------------------------------------------------------------------
6 y 7. FIRMAS
- Lugar: {org['loc']} | Fecha: {fecha_salida}
- Firma Titular: (Pendiente)
- Firma Transportista: (Pendiente)
"""
                return reporte

            except Exception as e:
                return f"Error generando DAT: {str(e)}"

        @mcp.tool()
        async def registrar_venta(
            fecha: str,
            producto: str,
            cantidad: float,
            cliente: str,
            albaran: str,
            numero_lote: str = "",
            cliente_nif: str = "",
            numero_rgseaa: str = "",
        ) -> str:
            """
            Registra una venta o salida de cosecha completa.
            Comando asociado: /venta
            """
            try:
                explotacion = await sync_to_async(Explotacion.objects.first)()
                await sync_to_async(RegistroMovimientoProducto.objects.create)(
                    explotacion=explotacion,
                    fecha=fecha,
                    producto=producto,
                    cantidad_kg=cantidad,
                    cliente_nombre=cliente,
                    numero_albaran=albaran,
                    numero_lote=numero_lote,
                    cliente_nif=cliente_nif,
                    numero_rgseaa=numero_rgseaa,
                )
                return f"Venta registrada: {cantidad}kg de {producto} a {cliente} (Alb: {albaran})."
            except Exception as e:
                return f"Error registrando venta: {str(e)}"

        # ==============================================================================
        # 4. HERRAMIENTAS DE REPORTING (Consultas)
        # ==============================================================================

        @mcp.tool()
        async def generar_cuaderno(anio: int) -> str:
            """
            Genera los datos COMPLETOS para el Cuaderno de Explotación (Todas las secciones).
            Extrae toda la información disponible en la base de datos para el año solicitado.
            Comando asociado: /cuaderno
            """
            try:
                start_date = date(anio, 1, 1)
                end_date = date(anio, 12, 31)

                # 1. Recuperar Explotación y datos maestros
                explotacion = await sync_to_async(
                    Explotacion.objects.select_related("titular", "direccion").first
                )()
                if not explotacion:
                    return "Error: No hay explotación configurada en el sistema."

                titular = explotacion.titular
                dir_exp = explotacion.direccion

                # Helper para formatear direcciones
                def fmt_dir(d):
                    if not d:
                        return "VACÍO"
                    return f"{d.tipo_via or ''} {d.nombre_via or ''} Nº{d.numero or ''}, {d.codigo_postal or ''} {d.localidad or ''} ({d.provincia or ''})"

                # --- SECCIÓN 1: INFORMACIÓN GENERAL ---

                # 1.1 Datos Generales
                t_nombre = (
                    f"{titular.nombre} {titular.apellidos or ''}"
                    if titular
                    else explotacion.nombre
                )
                t_nif = titular.documento or "VACÍO"
                t_rega = explotacion.numero_registro_nacional or "VACÍO"
                t_rea = explotacion.numero_registro_autonomico or "VACÍO"
                t_dir = fmt_dir(dir_exp)
                t_tel = "VACÍO"
                t_movil = "VACÍO"
                t_email = "VACÍO"

                if titular.documento:
                    persona_transp = await sync_to_async(
                        Persona.objects.filter(nif=titular.documento).first
                    )()
                    if persona_transp:
                        t_nombre = persona_transp.nombre
                        t_tel = persona_transp.telefono or t_tel
                        t_movil = persona_transp.movil or t_movil
                        t_email = persona_transp.email or t_email

                # Representante (Lógica: Si el tipo es REPRESENTANTE, asumimos que los datos del titular vinculado son del rep.)
                rep_nombre = "VACÍO"
                rep_nif = "VACÍO"
                rep_tipo = "VACÍO"
                if explotacion.tipo_representacion == "REPRESENTANTE":
                    rep_nombre = t_nombre
                    rep_nif = t_nif
                    rep_tipo = "Representante Legal"

                r = f"""DATOS PARA CUADERNO DE EXPLOTACIÓN (CAMPAÑA {anio})
================================================================================
1. INFORMACIÓN GENERAL
--------------------------------------------------------------------------------
1.1 DATOS DE LA EXPLOTACIÓN
- Titular (Nombre/Razón Social): {t_nombre}
- NIF: {t_nif}
- Nº Registro Nacional (REGA): {t_rega}
- Nº Registro Autonómico (REA): {t_rea}
- Dirección Completa: {t_dir}
- Teléfono Fijo: {t_tel} | Móvil: {t_movil}
- Email: {t_email}

REPRESENTANTE (Si procede):
- Nombre y Apellidos: {rep_nombre}
- NIF: {rep_nif}
- Tipo de Representación: {rep_tipo}
- Firma y Fecha: (Pendiente manuscrita)
"""

                # 1.2 Personas/Empresas (Aplicadores)
                # Filtramos personal habilitado
                aplicadores = await sync_to_async(list)(
                    Personal.objects.filter(habilitado_fitosanitarios=True)
                )
                r += "\n1.2 PERSONAS O EMPRESAS QUE INTERVIENEN (APLICADORES)\n"
                if not aplicadores:
                    r += "* (VACÍO - Registrar aplicadores en 'Personal' con /nuevo_personal)\n"
                else:
                    for i, p in enumerate(aplicadores, 1):
                        # Inferir checkboxes del carné desde el cargo
                        carnet = (p.cargo or "").upper()
                        check_basico = "[X]" if "BASICO" in carnet else "[ ]"
                        check_cualif = "[X]" if "CUALIFICADO" in carnet else "[ ]"
                        check_fumig = "[X]" if "FUMIGADOR" in carnet else "[ ]"
                        check_piloto = "[X]" if "PILOTO" in carnet else "[ ]"

                        r += f"  FILA {i}:\n"
                        r += f"  - Nombre/Empresa: {p.nombre} {p.apellidos}\n"
                        r += f"  - NIF: {p.documento}\n"
                        r += f"  - Nº Inscripción ROPO: {p.documento}\n"
                        r += f"  - Carné: {check_basico}Básico {check_cualif}Cualif. {check_fumig}Fumigador {check_piloto}Piloto\n"
                        r += "  - ¿Es Asesor?: [ ] (Marcar si procede)\n"

                # 1.3 Equipos (Maquinaria)
                equipos = await sync_to_async(list)(
                    EquipoAplicacion.objects.filter(explotacion=explotacion)
                )
                r += "\n1.3 EQUIPOS DE APLICACIÓN (MAQUINARIA)\n"
                if not equipos:
                    r += "* (VACÍO - Registrar en 'EquipoAplicacion' con /nueva_maquina)\n"
                else:
                    for i, eq in enumerate(equipos, 1):
                        r += f"  FILA {i}:\n"
                        r += f"  - Descripción: {eq.descripcion}\n"
                        r += f"  - Nº Inscripción ROMA: {eq.numero_inscripcion_roma}\n"
                        r += f"  - Fecha Adquisición: {eq.fecha_adquisicion or 'VACÍO'}\n"
                        r += f"  - Fecha Última Inspección (ITEAF): {eq.fecha_ultima_inspeccion or 'VACÍO'}\n"

                # 1.4 Asesoramiento
                asesores = await sync_to_async(list)(
                    Asesor.objects.select_related("persona").all()
                )
                r += "\n1.4 ASESORAMIENTO (GIP)\n"
                if not asesores:
                    r += "* (VACÍO - Registrar en 'Asesor' con /nuevo_asesor)\n"
                else:
                    for i, a in enumerate(asesores, 1):
                        r += f"  FILA {i}:\n"
                        r += f"  - Nombre/Entidad: {a.persona.nombre}\n"
                        r += f"  - NIF: {a.persona.nif}\n"
                        r += (
                            f"  - Nº Identificación/ROPO: {a.numero_inscripcion_ropo}\n"
                        )
                        r += f"  - Tipo Explotación GIP: {a.tipo_carnet or 'VACÍO'} (Ej: AE, PI, Atrias)\n"

                # ==============================================================================
                # SECCIÓN 2: IDENTIFICACIÓN DE PARCELAS
                # ==============================================================================
                parcelas = await sync_to_async(list)(
                    Parcela.objects.filter(explotacion=explotacion)
                )
                r += "\n--------------------------------------------------------------------------------\n"
                r += "2. IDENTIFICACIÓN DE PARCELAS\n"
                r += "--------------------------------------------------------------------------------\n"

                # 2.1 Datos Identificativos y Agronómicos
                r += "2.1 DATOS IDENTIFICATIVOS Y AGRONÓMICOS\n"
                if not parcelas:
                    r += "* (VACÍO - Registrar en 'Parcela' con /nueva_parcela)\n"
                else:
                    for i, p in enumerate(parcelas, 1):
                        r += f"  FILA {i} (Nº Orden: {i}):\n"
                        r += f"  - Provincia/Municipio/Agregado/Zona: (Ver Ref SIGPAC: {p.referencia_sigpac})\n"
                        r += f"  - Polígono: {p.poligono or ''} | Parcela: {p.parcela or ''} | Recinto: {p.recinto or ''}\n"
                        r += f"  - Uso SIGPAC: {p.uso_sigpac or 'VACÍO'}\n"
                        r += f"  - Superficie SIGPAC: {p.superficie_sigpac or 0} ha\n"
                        r += f"  - Superficie Cultivada: {p.superficie_cultivada or 0} ha\n"
                        r += f"  - Especie: {p.especie or 'VACÍO'}\n"
                        r += f"  - Variedad: {p.variedad or 'VACÍO'}\n"
                        r += f"  - Secano/Regadío: {p.secano_regadio or 'VACÍO'}\n"
                        r += (
                            f"  - Aire Libre/Protegido: {p.aire_protegido or 'VACÍO'}\n"
                        )
                        r += "  - Sistema Asesoramiento GIP: (Rellenar manual: AE, PI, etc.)\n"

                # 2.2 Datos Medioambientales (Placeholder, modelo actual no tiene estos campos específicos)
                r += "\n2.2 DATOS MEDIOAMBIENTALES\n"
                if not parcelas:
                    r += "* (VACÍO)\n"
                else:
                    for i, p in enumerate(parcelas, 1):
                        r += f"  FILA {i} (Parcela Orden {i}):\n"
                        r += "  - ¿Puntos de agua en parcela?: [ ]SI [ ]NO\n"
                        r += "  - Distancia a agua (m): \n"
                        r += "  - Zonas Específicas (Protegidas): [ ]Totalmente [ ]Parcialmente [ ]NO\n"

                # ==============================================================================
                # SECCIÓN 3: TRATAMIENTOS FITOSANITARIOS
                # ==============================================================================
                r += "\n--------------------------------------------------------------------------------\n"
                r += "3. TRATAMIENTOS FITOSANITARIOS\n"
                r += "--------------------------------------------------------------------------------\n"

                # 3.1 Registro de Actuaciones
                tratamientos = await sync_to_async(list)(
                    DiarioActividad.objects.filter(
                        explotacion=explotacion,
                        fecha__range=(start_date, end_date),
                        tipo="TRATAMIENTO",
                    ).select_related("parcela", "aplicador", "equipo")
                )

                r += "3.1 REGISTRO DE ACTUACIONES FITOSANITARIAS\n"
                if not tratamientos:
                    r += "* (VACÍO - Sin tratamientos registrados en este periodo)\n"
                else:
                    for i, t in enumerate(tratamientos, 1):
                        parc_ref = t.parcela.referencia_sigpac if t.parcela else "TODAS"
                        cultivo_txt = (
                            f"{t.parcela.especie} {t.parcela.variedad}"
                            if t.parcela
                            else "Varios"
                        )
                        aplicador_txt = (
                            f"{t.aplicador.nombre} (NIF: {t.aplicador.documento})"
                            if t.aplicador
                            else "VACÍO"
                        )
                        equipo_txt = (
                            t.equipo.descripcion if t.equipo else "Manual/Sin equipo"
                        )

                        r += f"  FILA {i}:\n"
                        r += f"  - Id. Parcelas: {parc_ref}\n"
                        r += f"  - Cultivo/Especie/Variedad: {cultivo_txt}\n"
                        r += f"  - Fechas: {t.fecha}\n"
                        r += f"  - Sup. Tratada: {t.superficie_tratada_ha} ha\n"
                        r += f"  - Problema Fitosanitario: {t.problema_fitosanitario}\n"
                        r += f"  - Aplicador: {aplicador_txt}\n"
                        r += f"  - Equipo: {equipo_txt}\n"
                        r += f"  - Producto (Nombre): {t.producto_nombre}\n"
                        r += f"  - Producto (Nº Registro): {t.producto_numero_registro or 'VACÍO'}\n"
                        r += f"  - Dosis: {t.dosis} {t.dosis_text or ''}\n"
                        r += f"  - Eficacia: {t.eficacia or 'Buena'}\n"
                        r += f"  - Observaciones: {t.observaciones}\n"

                # 3.2 Semilla Tratada
                siembras = await sync_to_async(list)(
                    SemillaTratada.objects.filter(
                        explotacion=explotacion,
                        fecha_siembra__range=(start_date, end_date),
                    ).select_related("parcela")
                )

                r += "\n3.2 USO DE SEMILLA TRATADA\n"
                r += f"  ¿Aplica Tratamiento? [{'X' if siembras else ' '}] SI  [{' ' if siembras else 'X'}] NO\n"
                if siembras:
                    for i, s in enumerate(siembras, 1):
                        parc_ref = s.parcela.referencia_sigpac if s.parcela else "N/A"
                        r += f"  FILA {i}:\n"
                        r += f"  - Fecha Siembra: {s.fecha_siembra}\n"
                        r += f"  - Id. Parcela: {parc_ref}\n"
                        r += f"  - Cultivo/Variedad: {s.cultivo}\n"
                        r += f"  - Sup. Sembrada: {s.superficie_sembrada_ha} ha\n"
                        r += f"  - Cantidad Semilla: {s.cantidad_semilla_kg} kg\n"
                        r += f"  - Producto (Nombre): {s.producto_fitosanitario}\n"
                        r += f"  - Producto (Nº Registro): {s.numero_registro}\n"

                # 3.3, 3.4, 3.5 (Postcosecha, Locales, Transporte) - Modelos no específicos
                r += "\n3.3 TRATAMIENTOS POSTCOSECHA\n"
                r += "  ¿Aplica Tratamiento? [ ] SI  [X] NO (Consultar registros manuales si existen)\n"
                r += "\n3.4 TRATAMIENTOS LOCALES ALMACENAMIENTO\n"
                r += "  ¿Aplica Tratamiento? [ ] SI  [X] NO\n"
                r += "\n3.5 TRATAMIENTOS MEDIOS DE TRANSPORTE\n"
                r += "  ¿Aplica Tratamiento? [ ] SI  [X] NO\n"

                # ==============================================================================
                # SECCIÓN 4: ANÁLISIS
                # ==============================================================================
                r += "\n--------------------------------------------------------------------------------\n"
                r += "4. REGISTRO DE ANÁLISIS (RESIDUOS)\n"
                r += "--------------------------------------------------------------------------------\n"
                analisis = await sync_to_async(list)(
                    AnalisisLaboratorio.objects.filter(
                        explotacion=explotacion, fecha__range=(start_date, end_date)
                    )
                )
                if not analisis:
                    r += "* (VACÍO - Registrar con /analisis)\n"
                else:
                    for i, an in enumerate(analisis, 1):
                        r += f"  FILA {i}:\n"
                        r += f"  - Fecha: {an.fecha}\n"
                        r += f"  - Material Analizado: {an.material_analizado} (Veg/Tierra/Agua)\n"
                        r += f"  - Cultivo/Cosecha Muestreado: {an.cultivo}\n"
                        r += f"  - Nº Boletín Análisis: {an.numero_boletin}\n"
                        r += f"  - Laboratorio: {an.laboratorio}\n"
                        r += f"  - Sustancias Detectadas: {an.sustancias_activas_detectadas}\n"

                # ==============================================================================
                # SECCIÓN 5: COSECHA COMERCIALIZADA
                # ==============================================================================
                r += "\n--------------------------------------------------------------------------------\n"
                r += "5. REGISTRO DE COSECHA COMERCIALIZADA\n"
                r += "--------------------------------------------------------------------------------\n"
                ventas = await sync_to_async(list)(
                    RegistroMovimientoProducto.objects.filter(
                        explotacion=explotacion, fecha__range=(start_date, end_date)
                    )
                )
                if not ventas:
                    r += "* (VACÍO - Registrar con /venta)\n"
                else:
                    for i, v in enumerate(ventas, 1):
                        r += f"  FILA {i}:\n"
                        r += f"  - Fecha: {v.fecha}\n"
                        r += f"  - Producto: {v.producto}\n"
                        r += f"  - Cantidad: {v.cantidad_kg} kg\n"
                        r += "  - Parcela Origen: (Indicar Nº Orden de Parcela)\n"
                        r += f"  - Nº Albarán/Factura: {v.numero_albaran}\n"
                        r += f"  - Nº Lote: {v.numero_lote or 'VACÍO'}\n"
                        r += f"  - Cliente (Nombre): {v.cliente_nombre}\n"
                        r += f"  - Cliente (NIF): {v.cliente_nif}\n"
                        r += f"  - Cliente (RGSEAA): {v.numero_rgseaa or 'VACÍO'}\n"

                # ==============================================================================
                # SECCIÓN 6: FERTILIZACIÓN
                # ==============================================================================
                r += "\n--------------------------------------------------------------------------------\n"
                r += "6. REGISTRO DE FERTILIZACIÓN\n"
                r += "--------------------------------------------------------------------------------\n"
                abonados = await sync_to_async(list)(
                    DiarioActividad.objects.filter(
                        explotacion=explotacion,
                        fecha__range=(start_date, end_date),
                        tipo__in=["ABONADO", "RIEGO"],
                    ).select_related("parcela")
                )

                if not abonados:
                    r += "* (VACÍO - Registrar con /riego)\n"
                else:
                    for i, ab in enumerate(abonados, 1):
                        parc_ref = (
                            ab.parcela.referencia_sigpac if ab.parcela else "TODAS"
                        )
                        cultivo = ab.parcela.especie if ab.parcela else ""
                        prod_abono = (
                            ab.producto_nombre if ab.producto_nombre else "Agua/Riego"
                        )

                        r += f"  FILA {i}:\n"
                        r += f"  - Intervalo Fechas: {ab.fecha}\n"
                        r += f"  - Nº Orden Parcela: {parc_ref}\n"
                        r += f"  - Cultivo/Variedad: {cultivo}\n"
                        r += f"  - Tipo Abono/Producto: {prod_abono}\n"
                        r += "  - Nº Albarán: (Ver Observaciones)\n"
                        r += "  - Riqueza NPK: (Ver Observaciones)\n"
                        r += f"  - Dosis: {ab.dosis}\n"
                        r += f"  - Tipo Fertilización: {ab.tipo} (F/AF/AC)\n"
                        r += f"  - Observaciones: {ab.observaciones}\n"

                return r

            except Exception as e:
                return f"Error generando cuaderno completo: {str(e)}"

        @mcp.tool()
        async def consultar_historico(
            consulta: str,
            anio: int = None,
            producto: str = None,
            tipo_actividad: str = None,
            parcela_ref: str = None,
            plaga: str = None,
        ) -> str:
            """
            Consulta datos históricos con filtros avanzados.
            Comando asociado: /consulta
            """
            try:
                qs = DiarioActividad.objects.all()
                filters_desc = []

                if anio:
                    qs = qs.filter(fecha__year=anio)
                    filters_desc.append(f"Año {anio}")
                if producto:
                    qs = qs.filter(producto_nombre__icontains=producto)
                    filters_desc.append(f"Producto '{producto}'")
                if tipo_actividad:
                    qs = qs.filter(tipo__icontains=tipo_actividad)
                    filters_desc.append(f"Tipo '{tipo_actividad}'")
                if parcela_ref:
                    qs = qs.filter(
                        Q(parcela__referencia_sigpac__icontains=parcela_ref)
                        | Q(parcela__especie__icontains=parcela_ref)
                    )
                    filters_desc.append(f"Parcela '{parcela_ref}'")
                if plaga:
                    qs = qs.filter(problema_fitosanitario__icontains=plaga)
                    filters_desc.append(f"Plaga '{plaga}'")

                count = await sync_to_async(qs.count)()

                resumen = f"Se encontraron {count} registros. Filtros: {', '.join(filters_desc) or 'Ninguno'}.\n"

                if count > 0:
                    results = await sync_to_async(list)(
                        qs.select_related("parcela").order_by("-fecha")[:5]
                    )
                    resumen += "Últimos 5 registros:\n"
                    for r in results:
                        parc = r.parcela.referencia_sigpac if r.parcela else "N/A"
                        prod = r.producto_nombre or "Sin producto"
                        resumen += f"- {r.fecha} | {r.tipo} | {prod} ({r.dosis}) | Parcela: {parc}\n"

                return resumen
            except Exception as e:
                return f"Error en consulta: {str(e)}"

        self.stdout.write(
            self.style.SUCCESS("Iniciando servidor MCP Agrícola en puerto 8001...")
        )
        mcp.run(transport="http", host="0.0.0.0", port=8001, path="/mcp")
