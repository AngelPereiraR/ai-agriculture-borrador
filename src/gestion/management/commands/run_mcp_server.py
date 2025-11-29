import logging
from datetime import date, datetime
from django.db.models import Q
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from fastmcp import FastMCP

# Importación de TODOS los modelos necesarios del sistema
from gestion.models import (
    Explotacion,
    Parcela,
    Persona,
    DiarioActividad,
    DocumentoDAT,
    RegistroTransporte,
    Destinatario,
    Vehiculo,
    Transportista,
    EquipoAplicacion,
    SemillaTratada,
    RegistroMovimientoProducto,
    AnalisisLaboratorio,
    Asesor,
    Personal
)

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-django")

class Command(BaseCommand):
    help = "Inicia el servidor FastMCP con contexto de Django para Agricultura"

    def handle(self, *args, **kwargs):
        mcp = FastMCP(
            "Agente Agricola Django",
            instructions="Servidor MCP para gestión integral de datos agrícolas (Maestros, Cuaderno y DAT)."
        )

        # ==============================================================================
        # 1. HERRAMIENTAS DE CONFIGURACIÓN Y MAESTROS (Configuración Inicial)
        # ==============================================================================

        @mcp.tool()
        async def configurar_explotacion_principal(
            nombre_comercial: str,
            nif_titular: str,
            registro_nacional: str
        ) -> str:
            """
            Configura la Explotación Agrícola principal y su titular.
            Comando asociado: /config_inicial
            """
            try:
                titular, created = await sync_to_async(Persona.objects.get_or_create)(
                    nif=nif_titular,
                    defaults={'nombre': f"Titular {nif_titular}"}
                )
                
                explotacion, created_exp = await sync_to_async(Explotacion.objects.update_or_create)(
                    nif=nif_titular,
                    defaults={
                        'nombre': nombre_comercial,
                        'numero_registro_nacional': registro_nacional,
                        'titular': titular,
                        'tipo_representacion': 'PROPIETARIO'
                    }
                )
                return f"Explotación '{nombre_comercial}' configurada correctamente (ID: {explotacion.id})."
            except Exception as e:
                return f"Error en configuración inicial: {str(e)}"

        @mcp.tool()
        async def crear_parcela(
            nombre_comun: str,
            referencia_sigpac: str,
            cultivo: str,
            superficie_ha: float
        ) -> str:
            """
            Da de alta una nueva parcela.
            Comando asociado: /nueva_parcela
            """
            try:
                explotacion = await sync_to_async(Explotacion.objects.first)()
                if not explotacion:
                    return "Error: No hay una explotación configurada. Usa /config_inicial primero."

                obj = await sync_to_async(Parcela.objects.create)(
                    explotacion=explotacion,
                    referencia_sigpac=referencia_sigpac,
                    especie=cultivo,
                    superficie_cultivada=superficie_ha,
                    superficie_sigpac=superficie_ha
                )
                return f"Parcela creada: {cultivo} en {referencia_sigpac} ({superficie_ha} ha) - Alias: {nombre_comun}"
            except Exception as e:
                return f"Error creando parcela: {str(e)}"

        @mcp.tool()
        async def crear_cliente_destinatario(
            nombre_fiscal: str,
            nif: str,
            matricula_vehiculo_preferido: str = None
        ) -> str:
            """
            Crea un cliente/destinatario y le asigna un vehículo preferido para automatizar DATs.
            Comando asociado: /nuevo_cliente
            """
            try:
                vehiculo = None
                if matricula_vehiculo_preferido:
                    vehiculo = await sync_to_async(Vehiculo.objects.filter(matricula=matricula_vehiculo_preferido).first)()
                    if not vehiculo:
                        return f"Error: El vehículo {matricula_vehiculo_preferido} no existe. Regístralo con /nuevo_vehiculo."

                persona, _ = await sync_to_async(Persona.objects.get_or_create)(
                    nif=nif,
                    defaults={'nombre': nombre_fiscal}
                )

                destinatario, created = await sync_to_async(Destinatario.objects.get_or_create)(
                    documento=nif,
                    defaults={
                        'nombre': nombre_fiscal,
                        'transporte_asignado': vehiculo
                    }
                )
                
                if not created and vehiculo:
                    destinatario.transporte_asignado = vehiculo
                    await sync_to_async(destinatario.save)()
                
                info_vehiculo = f"Vehículo asignado: {vehiculo.matricula}" if vehiculo else "Sin vehículo asignado"
                return f"Cliente '{nombre_fiscal}' configurado. {info_vehiculo}"
            except Exception as e:
                return f"Error creando cliente: {str(e)}"

        @mcp.tool()
        async def crear_vehiculo(
            matricula: str,
            tipo: str,
            marca_modelo: str = ""
        ) -> str:
            """
            Registra un vehículo.
            Comando asociado: /nuevo_vehiculo
            """
            try:
                obj = await sync_to_async(Vehiculo.objects.create)(
                    matricula=matricula,
                    tipo=tipo.upper(),
                    marca=marca_modelo
                )
                return f"Vehículo registrado: {obj.tipo} - {obj.matricula}"
            except Exception as e:
                return f"Error creando vehículo: {str(e)}"

        @mcp.tool()
        async def crear_maquina_roma(
            descripcion: str,
            numero_roma: str,
            nombre_explotacion: str = ""
        ) -> str:
            """
            Registra maquinaria de aplicación (ROMA).
            Comando asociado: /nueva_maquina
            """
            try:
                explotacion = await sync_to_async(Explotacion.objects.first)()
                obj = await sync_to_async(EquipoAplicacion.objects.create)(
                    descripcion=descripcion,
                    numero_inscripcion_roma=numero_roma,
                    explotacion=explotacion
                )
                return f"Máquina registrada: {obj.descripcion} (ROMA: {obj.numero_inscripcion_roma})"
            except Exception as e:
                return f"Error registrando máquina: {str(e)}"

        @mcp.tool()
        async def crear_personal_aplicador(
            nombre: str,
            dni: str,
            telefono: str = "",
            email: str = "",
            nivel_carne: str = ""
        ) -> str:
            """
            Registra personal/aplicador con su nivel de carné.
            Comando asociado: /nuevo_personal
            """
            try:
                persona, _ = await sync_to_async(Persona.objects.get_or_create)(
                    nif=dni,
                    defaults={'nombre': nombre, 'telefono': telefono, 'email': email}
                )
                
                habilitado = True if nivel_carne and nivel_carne.lower() != "ninguno" else False
                
                await sync_to_async(Personal.objects.create)(
                    nombre=nombre,
                    apellidos="(Apellidos)", 
                    documento=dni,
                    tipo_documento="DNI",
                    sexo="O",
                    cargo=f"Aplicador - Nivel: {nivel_carne}",
                    habilitado_fitosanitarios=habilitado
                )
                
                return f"Personal registrado: {nombre} (DNI: {dni}). Nivel: {nivel_carne}"
            except Exception as e:
                return f"Error registrando personal: {str(e)}"

        @mcp.tool()
        async def crear_asesor_tecnico(
            nombre: str,
            nif: str,
            codigo_ropo: str,
            tipo_asesoramiento: str = ""
        ) -> str:
            """
            Registra un Asesor Técnico (GIP).
            Comando asociado: /nuevo_asesor
            """
            try:
                persona, _ = await sync_to_async(Persona.objects.get_or_create)(
                    nif=nif,
                    defaults={'nombre': nombre}
                )
                
                asesor = await sync_to_async(Asesor.objects.create)(
                    persona=persona,
                    numero_inscripcion_ropo=codigo_ropo,
                    tipo_carnet=tipo_asesoramiento 
                )
                return f"Asesor registrado: {nombre} (ROPO: {codigo_ropo})"
            except Exception as e:
                return f"Error creando asesor: {str(e)}"

        @mcp.tool()
        async def crear_transportista_externo(
            nombre: str,
            nif: str,
            email: str = ""
        ) -> str:
            """
            Registra un transportista externo.
            Comando asociado: /nuevo_transportista
            """
            try:
                obj = await sync_to_async(Transportista.objects.create)(
                    nombre=nombre,
                    nif=nif,
                    email=email
                )
                return f"Transportista registrado: {nombre}"
            except Exception as e:
                return f"Error creando transportista: {str(e)}"

        # ==============================================================================
        # 2. HERRAMIENTAS OPERATIVAS (Día a día en el campo)
        # ==============================================================================

        @mcp.tool()
        async def registrar_tratamiento(
            fecha: str,
            nombre_parcela: str,
            producto: str,
            dosis: float,
            plaga: str,
            observaciones: str = ""
        ) -> str:
            """
            Registra una aplicación de fitosanitarios.
            Comando asociado: /tratamiento
            """
            try:
                parcela = await sync_to_async(Parcela.objects.filter(
                    Q(referencia_sigpac__icontains=nombre_parcela) | Q(especie__icontains=nombre_parcela)
                ).first)()
                
                if not parcela:
                    return f"Error: Parcela '{nombre_parcela}' no encontrada."

                aplicador = await sync_to_async(Persona.objects.first)() 

                actividad = await sync_to_async(DiarioActividad.objects.create)(
                    explotacion=parcela.explotacion,
                    fecha=fecha,
                    tipo="TRATAMIENTO",
                    parcela=parcela,
                    superficie_tratada_ha=parcela.superficie_cultivada,
                    producto_nombre=producto,
                    dosis=dosis,
                    problema_fitosanitario=plaga,
                    observaciones=observaciones,
                    aplicador=aplicador
                )
                return f"Tratamiento registrado ID: {actividad.id}. {producto} contra {plaga} en {parcela.referencia_sigpac}."
            except Exception as e:
                return f"Error al registrar tratamiento: {str(e)}"

        @mcp.tool()
        async def registrar_riego(
            fecha: str,
            nombre_parcela: str,
            tipo_actividad: str, # "Riego" o "Abonado"
            abono: str = "",
            cantidad: float = 0.0
        ) -> str:
            """
            Registra riego o fertilización.
            Comando asociado: /riego
            """
            try:
                parcela = await sync_to_async(Parcela.objects.filter(
                    Q(referencia_sigpac__icontains=nombre_parcela) | Q(especie__icontains=nombre_parcela)
                ).first)()
                
                if not parcela:
                    return f"Error: Parcela '{nombre_parcela}' no encontrada."

                tipo_db = "ABONADO" if "abono" in tipo_actividad.lower() or abono else "RIEGO"
                
                actividad = await sync_to_async(DiarioActividad.objects.create)(
                    explotacion=parcela.explotacion,
                    fecha=fecha,
                    tipo=tipo_db,
                    parcela=parcela,
                    superficie_tratada_ha=parcela.superficie_cultivada,
                    producto_nombre=abono,
                    dosis=cantidad,
                    observaciones=f"Registro de {tipo_actividad}"
                )
                return f"Actividad de {tipo_db} registrada ID: {actividad.id}."
            except Exception as e:
                return f"Error al registrar riego: {str(e)}"

        @mcp.tool()
        async def registrar_siembra(
            fecha: str,
            nombre_parcela: str,
            cultivo: str,
            kilos_semilla: float,
            producto_semilla: str = "",
            registro_producto: str = ""
        ) -> str:
            """
            Registra siembra con semilla tratada.
            Comando asociado: /siembra
            """
            try:
                parcela = await sync_to_async(Parcela.objects.filter(
                    Q(referencia_sigpac__icontains=nombre_parcela)
                ).first)()
                
                if not parcela:
                    return f"Error: Parcela '{nombre_parcela}' no encontrada."

                obj = await sync_to_async(SemillaTratada.objects.create)(
                    explotacion=parcela.explotacion,
                    fecha_siembra=fecha,
                    parcela=parcela,
                    cultivo=cultivo,
                    superficie_sembrada_ha=parcela.superficie_cultivada,
                    cantidad_semilla_kg=kilos_semilla,
                    producto_fitosanitario=producto_semilla,
                    numero_registro=registro_producto
                )
                return f"Siembra registrada: {cultivo} en {parcela.referencia_sigpac}. Tratamiento semilla: {producto_semilla}"
            except Exception as e:
                return f"Error al registrar siembra: {str(e)}"

        @mcp.tool()
        async def registrar_analisis(
            fecha: str,
            material: str,
            laboratorio: str,
            resultado: str
        ) -> str:
            """
            Registra análisis de laboratorio.
            Comando asociado: /analisis
            """
            try:
                explotacion = await sync_to_async(Explotacion.objects.first)()
                obj = await sync_to_async(AnalisisLaboratorio.objects.create)(
                    explotacion=explotacion,
                    fecha=fecha,
                    material_analizado=material,
                    laboratorio=laboratorio,
                    sustancias_activas_detectadas=resultado
                )
                return f"Análisis registrado ID: {obj.id} ({material})."
            except Exception as e:
                return f"Error al registrar análisis: {str(e)}"

        # ==============================================================================
        # 3. HERRAMIENTAS DE GESTIÓN DOCUMENTAL (DAT y Ventas)
        # ==============================================================================

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
            condiciones_transporte: str = ""
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
                destinatario = await sync_to_async(Destinatario.objects.filter(
                    nombre__icontains=nombre_destinatario
                ).select_related('transporte_asignado', 'direccion').first)()

                if not destinatario:
                    return f"Error: Destinatario '{nombre_destinatario}' no encontrado. Créalo con /nuevo_cliente."

                explotacion = await sync_to_async(Explotacion.objects.select_related('titular', 'direccion').first)()
                if not explotacion:
                    return "Error: No hay Explotación configurada como origen."

                # 2. LÓGICA INTELIGENTE: TRANSPORTISTA
                # Prioridad: 1. Búsqueda en DB por NIF -> 2. Argumentos manuales
                t_nombre = nombre_transportista or "(Rellenar)"
                t_nif = nif_transportista or "VACÍO"
                t_tel = telefono_transportista or "VACÍO"
                t_email = email_transportista or "VACÍO"

                if nif_transportista:
                    # A. Buscar en modelo Transportista
                    transp_db = await sync_to_async(Transportista.objects.filter(nif=nif_transportista).first)()
                    if transp_db:
                        t_nombre = transp_db.nombre
                        t_tel = transp_db.telefono or t_tel
                        t_email = transp_db.email or t_email
                    else:
                        # B. Buscar en modelo Persona (para conductores propios/autónomos)
                        persona_transp = await sync_to_async(Persona.objects.filter(nif=nif_transportista).first)()
                        if persona_transp:
                            t_nombre = persona_transp.nombre
                            t_tel = persona_transp.telefono or persona_transp.movil or t_tel
                            t_email = persona_transp.email or t_email

                # 3. LÓGICA INTELIGENTE: AUTORIZADO
                auth_nom = nombre_autorizado or "VACÍO"
                auth_nif = nif_autorizado or "VACÍO"

                if nif_autorizado:
                    # Buscar persona por NIF si se proporciona
                    persona_auth = await sync_to_async(Persona.objects.filter(nif=nif_autorizado).first)()
                    if persona_auth:
                        auth_nom = persona_auth.nombre
                
                # Si sigue vacío, intentar inferir del titular/representante
                titular = explotacion.titular
                if auth_nom == "VACÍO" and explotacion.tipo_representacion == 'REPRESENTANTE' and titular:
                    auth_nom = titular.nombre
                    auth_nif = titular.nif

                # 4. Buscar Parcela de Origen (Referencia SIGPAC)
                parcela_origen = await sync_to_async(Parcela.objects.filter(
                    explotacion=explotacion,
                    especie__icontains=productos[0]
                ).first)()

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
                    observaciones=obs
                )

                persona_dest = await sync_to_async(Persona.objects.filter(nif=destinatario.documento).first)()
                
                await sync_to_async(RegistroTransporte.objects.create)(
                    documento_dat=nuevo_dat,
                    fecha_transporte=datetime.now(),
                    destinatario=persona_dest, 
                    vehiculo=vehiculo,
                    cantidad=cantidades[0],
                    unidad=unidades[0],
                    estado="emitido"
                )

                # 6. Construir Reporte Detallado
                def fmt_parts(d):
                    if not d: return {"via": "", "nombre": "", "num": "", "cp": "", "loc": "", "prov": "", "entidad": "", "pais": ""}
                    return {
                        "via": d.tipo_via or "", "nombre": d.nombre_via or "", "num": d.numero or "", 
                        "cp": d.codigo_postal or "", "loc": d.localidad or "", "prov": d.provincia or "",
                        "entidad": d.entidad_poblacion or d.localidad or "",
                        "pais": d.pais or "España"
                    }

                org = fmt_parts(explotacion.direccion)
                dst = fmt_parts(destinatario.direccion)
                
                # Datos Titular
                t_nombre = titular.nombre if titular else explotacion.nombre
                t_nif = explotacion.nif
                t_tel = titular.telefono if titular else "VACÍO"
                t_email = titular.email if titular else "VACÍO"
                
                # Sexo y Móvil Titular
                t_movil = titular.movil if titular else ""
                check_sexo_h = "[ ]"
                check_sexo_m = "[ ]"
                if titular and titular.sexo:
                    if titular.sexo == 'H': check_sexo_h = "[X]"
                    if titular.sexo == 'M': check_sexo_m = "[X]"

                # Datos Destinatario (Extra)
                dest_tel = persona_dest.telefono if persona_dest else ""
                dest_movil = persona_dest.movil if persona_dest else ""
                dest_email = persona_dest.email if persona_dest else ""

                # Sigpac
                sigpac_data = {"prov": "", "mun": "", "pol": "", "par": "", "rec": ""}
                if parcela_origen:
                    sigpac_data = {
                        "prov": explotacion.direccion.provincia if explotacion.direccion else "",
                        "mun": explotacion.direccion.localidad if explotacion.direccion else "",
                        "pol": parcela_origen.poligono or "",
                        "par": parcela_origen.parcela or "",
                        "rec": parcela_origen.recinto or ""
                    }

                # Transporte
                v_mat = vehiculo.matricula if vehiculo else "PENDIENTE DE ASIGNAR"
                
                # Fechas
                fecha_salida = datetime.now().strftime("%d/%m/%Y")
                hora_salida = datetime.now().strftime("%H:%M")
                
                # Calidad visual
                check_dop = f"[X] {denominacion_origen}" if denominacion_origen else "[ ] Denominación de Origen Protegida"
                check_igp = f"[X] {indicacion_geografica}" if indicacion_geografica else "[ ] Indicación Geográfica Protegida"
                check_etg = f"[X] {especialidad_tradicional}" if especialidad_tradicional else "[ ] Especialidad Tradicional Garantizada"
                check_eco = "[X] Producción ecológica" if es_ecologico else "[ ] Producción ecológica"
                check_int = "[X] Producción integrada de Andalucía" if es_integrada else "[ ] Producción integrada de Andalucía"
                
                es_calidad_diferenciada = "SÍ" if (denominacion_origen or indicacion_geografica or especialidad_tradicional) else "NO"

                # Tabla de productos
                lineas_carga = ""
                for i, (prod, cant, unid, var) in enumerate(zip(productos, cantidades, unidades, variedades_safe), 1):
                    var_str = var if var else ""
                    lineas_carga += f"""
* LÍNEA {i}:
- Denominación: {prod}
- Variedad/Tipo: {var_str}
- Unidad: {unid}
- Cantidad: {cant}"""

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
- ¿Calidad Diferenciada? {es_calidad_diferenciada}
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
            albaran: str
        ) -> str:
            """
            Registra una venta o salida de cosecha.
            Comando asociado: /venta
            """
            try:
                explotacion = await sync_to_async(Explotacion.objects.first)()
                obj = await sync_to_async(RegistroMovimientoProducto.objects.create)(
                    explotacion=explotacion,
                    fecha=fecha,
                    producto=producto,
                    cantidad_kg=cantidad,
                    cliente_nombre=cliente,
                    numero_albaran=albaran
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
            Comando asociado: /cuaderno
            """
            try:
                start_date = date(anio, 1, 1)
                end_date = date(anio, 12, 31)
                
                # Fetch Explotacion with related fields
                explotacion = await sync_to_async(Explotacion.objects.select_related('titular', 'direccion').first)()
                if not explotacion:
                    return "Error: No hay explotación configurada."
                
                # Helper for address
                def fmt_dir(d):
                    if not d: return "VACÍO"
                    return f"{d.tipo_via} {d.nombre_via} {d.numero}, {d.codigo_postal} {d.localidad} ({d.provincia})"

                # --- SECCIÓN 1: INFORMACIÓN GENERAL ---
                titular = explotacion.titular
                t_dir = explotacion.direccion
                
                # Titular info
                t_nombre = f"{titular.nombre} {titular.apellidos or ''}" if titular else explotacion.nombre
                t_nif = explotacion.nif
                t_reg_nac = explotacion.numero_registro_nacional
                t_reg_aut = explotacion.numero_registro_autonomico
                t_tel = titular.telefono if titular else ""
                t_movil = titular.movil if titular else ""
                t_email = titular.email if titular else ""
                
                # Representante info
                rep_nombre = t_nombre if explotacion.tipo_representacion == 'REPRESENTANTE' else "VACÍO"
                rep_nif = t_nif if explotacion.tipo_representacion == 'REPRESENTANTE' else "VACÍO"
                rep_tipo = explotacion.tipo_representacion

                info_general = f"""**SECCIÓN 1: INFORMACIÓN GENERAL**
                1.1 DATOS DE LA EXPLOTACIÓN
                - Titular Nombre/Razón Social: {t_nombre}
                - NIF: {t_nif}
                - Nº Reg. Nacional: {t_reg_nac}
                - Nº Reg. Autonómico: {t_reg_aut}
                - Dirección: {t_dir.nombre_via if t_dir else ''}, {t_dir.numero if t_dir else ''}
                - Localidad: {t_dir.localidad if t_dir else ''}
                - C. Postal: {t_dir.codigo_postal if t_dir else ''}
                - Provincia: {t_dir.provincia if t_dir else ''}
                - Teléfono Fijo: {t_tel}
                - Móvil: {t_movil}
                - Email: {t_email}

                REPRESENTANTE (Si aplica):
                - Nombre: {rep_nombre}
                - NIF: {rep_nif}
                - Tipo Representación: {rep_tipo}
                """

                # 1.2 APLICADORES
                personal_qs = Personal.objects.filter(habilitado_fitosanitarios=True)
                aplicadores = await sync_to_async(list)(personal_qs)
                
                info_general += "\n**SECCIÓN 1.2: PERSONAS O EMPRESAS (APLICADORES)**\n"
                if not aplicadores:
                    info_general += "VACÍO (Sin aplicadores registrados)\n"
                else:
                    for i, p in enumerate(aplicadores, 1):
                        info_general += f"FILA {i}:\n"
                        info_general += f"  - Nombre: {p.nombre} {p.apellidos}\n"
                        info_general += f"  - NIF: {p.documento}\n"
                        info_general += f"  - Nº ROPO: (Consultar Carné)\n" 
                        info_general += f"  - Tipo Carné (Cargo): {p.cargo}\n"

                # 1.3 MAQUINARIA
                equipos = await sync_to_async(list)(EquipoAplicacion.objects.filter(explotacion=explotacion))
                
                info_general += "\n**SECCIÓN 1.3: EQUIPOS DE APLICACIÓN**\n"
                if not equipos:
                    info_general += "VACÍO (Sin maquinaria)\n"
                else:
                    for i, eq in enumerate(equipos, 1):
                        info_general += f"FILA {i}:\n"
                        info_general += f"  - Descripción: {eq.descripcion}\n"
                        info_general += f"  - Nº ROMA: {eq.numero_inscripcion_roma}\n"
                        info_general += f"  - Fecha Adquisición: {eq.fecha_adquisicion}\n"
                        info_general += f"  - Última Inspección: {eq.fecha_ultima_inspeccion}\n"

                # 1.4 ASESORAMIENTO
                asesores = await sync_to_async(list)(Asesor.objects.select_related('persona').all())
                
                info_general += "\n**SECCIÓN 1.4: ASESORAMIENTO (GIP)**\n"
                if not asesores:
                    info_general += "VACÍO (Sin asesores)\n"
                else:
                    for i, a in enumerate(asesores, 1):
                        info_general += f"FILA {i}:\n"
                        info_general += f"  - Nombre/Entidad: {a.persona.nombre}\n"
                        info_general += f"  - NIF: {a.persona.nif}\n"
                        info_general += f"  - Nº ROPO/Identificación: {a.numero_inscripcion_ropo}\n"
                        info_general += f"  - Tipo Explotación GIP: {a.tipo_carnet}\n"

                # --- SECCIÓN 2: PARCELAS ---
                parcelas = await sync_to_async(list)(Parcela.objects.filter(explotacion=explotacion))
                
                info_parcelas = "\n**SECCIÓN 2: IDENTIFICACIÓN DE PARCELAS**\n"
                if not parcelas:
                    info_parcelas += "VACÍO (Sin parcelas)\n"
                else:
                    for i, p in enumerate(parcelas, 1):
                        info_parcelas += f"FILA {i}:\n"
                        info_parcelas += f"  - Nº Orden: {i}\n"
                        info_parcelas += f"  - Ref SIGPAC: {p.referencia_sigpac}\n"
                        info_parcelas += f"  - Polígono: {p.poligono} | Parcela: {p.parcela} | Recinto: {p.recinto}\n"
                        info_parcelas += f"  - Uso SIGPAC: {p.uso_sigpac}\n"
                        info_parcelas += f"  - Sup. SIGPAC: {p.superficie_sigpac}\n"
                        info_parcelas += f"  - Sup. Cultivada: {p.superficie_cultivada}\n"
                        info_parcelas += f"  - Especie: {p.especie}\n"
                        info_parcelas += f"  - Variedad: {p.variedad}\n"
                        info_parcelas += f"  - Regadío/Secano: {p.secano_regadio}\n"
                        info_parcelas += f"  - Aire Libre/Protegido: {p.aire_protegido}\n"

                # --- SECCIÓN 3: TRATAMIENTOS ---
                tratamientos = await sync_to_async(list)(DiarioActividad.objects.filter(
                    explotacion=explotacion,
                    fecha__range=(start_date, end_date),
                    tipo="TRATAMIENTO"
                ).select_related('parcela', 'aplicador', 'equipo'))
                
                info_tratamientos = "\n**SECCIÓN 3.1: REGISTRO DE ACTUACIONES FITOSANITARIAS**\n"
                if not tratamientos:
                    info_tratamientos += "VACÍO (Sin tratamientos)\n"
                else:
                    for i, t in enumerate(tratamientos, 1):
                        parc_ref = t.parcela.referencia_sigpac if t.parcela else "TODAS"
                        cultivo = f"{t.parcela.especie} {t.parcela.variedad}" if t.parcela else "Varios"
                        aplicador_nom = f"{t.aplicador.nombre} (NIF: {t.aplicador.nif})" if t.aplicador else "VACÍO"
                        equipo_nom = t.equipo.descripcion if t.equipo else "Manual/Sin equipo"
                        
                        info_tratamientos += f"FILA {i}:\n"
                        info_tratamientos += f"  - Fecha: {t.fecha}\n"
                        info_tratamientos += f"  - Parcela ID: {parc_ref}\n"
                        info_tratamientos += f"  - Cultivo: {cultivo}\n"
                        info_tratamientos += f"  - Superficie Tratada: {t.superficie_tratada_ha}\n"
                        info_tratamientos += f"  - Problema Fitosanitario: {t.problema_fitosanitario}\n"
                        info_tratamientos += f"  - Aplicador: {aplicador_nom}\n"
                        info_tratamientos += f"  - Equipo: {equipo_nom}\n"
                        info_tratamientos += f"  - Producto: {t.producto_nombre}\n"
                        info_tratamientos += f"  - Nº Registro: {t.producto_numero_registro}\n"
                        info_tratamientos += f"  - Dosis: {t.dosis} {t.dosis_text or ''}\n"
                        info_tratamientos += f"  - Eficacia: {t.eficacia}\n"
                        info_tratamientos += f"  - Observaciones: {t.observaciones}\n"

                # 3.2 SEMILLA TRATADA
                siembras = await sync_to_async(list)(SemillaTratada.objects.filter(
                    explotacion=explotacion,
                    fecha_siembra__range=(start_date, end_date)
                ).select_related('parcela'))
                
                info_semillas = "\n**SECCIÓN 3.2: SEMILLA TRATADA**\n"
                if not siembras:
                    info_semillas += "VACÍO (Sin siembra de semilla tratada)\n"
                else:
                    for i, s in enumerate(siembras, 1):
                        parc_ref = s.parcela.referencia_sigpac if s.parcela else "N/A"
                        info_semillas += f"FILA {i}:\n"
                        info_semillas += f"  - Fecha Siembra: {s.fecha_siembra}\n"
                        info_semillas += f"  - Parcela: {parc_ref}\n"
                        info_semillas += f"  - Cultivo/Variedad: {s.cultivo}\n"
                        info_semillas += f"  - Sup. Sembrada: {s.superficie_sembrada_ha}\n"
                        info_semillas += f"  - Cantidad Semilla: {s.cantidad_semilla_kg} kg\n"
                        info_semillas += f"  - Producto: {s.producto_fitosanitario}\n"
                        info_semillas += f"  - Nº Registro: {s.numero_registro}\n"

                # --- SECCIÓN 4: ANÁLISIS ---
                analisis = await sync_to_async(list)(AnalisisLaboratorio.objects.filter(
                    explotacion=explotacion,
                    fecha__range=(start_date, end_date)
                ))
                
                info_analisis = "\n**SECCIÓN 4: ANÁLISIS**\n"
                if not analisis:
                    info_analisis += "VACÍO (Sin análisis)\n"
                else:
                    for i, an in enumerate(analisis, 1):
                        info_analisis += f"FILA {i}:\n"
                        info_analisis += f"  - Fecha: {an.fecha}\n"
                        info_analisis += f"  - Material Analizado: {an.material_analizado}\n"
                        info_analisis += f"  - Cultivo/Cosecha: {an.cultivo}\n"
                        info_analisis += f"  - Nº Boletín: {an.numero_boletin}\n"
                        info_analisis += f"  - Laboratorio: {an.laboratorio}\n"
                        info_analisis += f"  - Resultados: {an.sustancias_activas_detectadas}\n"

                # --- SECCIÓN 5: COSECHA ---
                ventas = await sync_to_async(list)(RegistroMovimientoProducto.objects.filter(
                    explotacion=explotacion,
                    fecha__range=(start_date, end_date)
                ))
                
                info_ventas = "\n**SECCIÓN 5: COSECHA COMERCIALIZADA**\n"
                if not ventas:
                    info_ventas += "VACÍO (Sin ventas)\n"
                else:
                    for i, v in enumerate(ventas, 1):
                        info_ventas += f"FILA {i}:\n"
                        info_ventas += f"  - Fecha: {v.fecha}\n"
                        info_ventas += f"  - Producto: {v.producto}\n"
                        info_ventas += f"  - Cantidad: {v.cantidad_kg} kg\n"
                        info_ventas += f"  - Parcela Origen: (Rellenar manual o inferir)\n"
                        info_ventas += f"  - Nº Albarán/Factura: {v.numero_albaran}\n"
                        info_ventas += f"  - Lote: {v.numero_lote}\n"
                        info_ventas += f"  - Cliente: {v.cliente_nombre}\n"
                        info_ventas += f"  - NIF Cliente: {v.cliente_nif}\n"
                        info_ventas += f"  - RGSEAA: {v.numero_rgseaa}\n"

                # --- SECCIÓN 6: FERTILIZACIÓN ---
                abonados = await sync_to_async(list)(DiarioActividad.objects.filter(
                    explotacion=explotacion,
                    fecha__range=(start_date, end_date),
                    tipo__in=["ABONADO", "RIEGO"]
                ).select_related('parcela'))
                
                info_fertilizacion = "\n**SECCIÓN 6: REGISTRO DE FERTILIZACIÓN**\n"
                if not abonados:
                    info_fertilizacion += "VACÍO (Sin fertilización)\n"
                else:
                    count_fert = 0
                    for ab in abonados:
                        count_fert += 1
                        parc_ref = ab.parcela.referencia_sigpac if ab.parcela else "TODAS"
                        cultivo = ab.parcela.especie if ab.parcela else ""
                        prod = ab.producto_nombre if ab.producto_nombre else "Riego"
                        
                        info_fertilizacion += f"FILA {count_fert}:\n"
                        info_fertilizacion += f"  - Fecha: {ab.fecha}\n"
                        info_fertilizacion += f"  - Parcela: {parc_ref}\n"
                        info_fertilizacion += f"  - Cultivo: {cultivo}\n"
                        info_fertilizacion += f"  - Tipo Abono/Producto: {prod}\n"
                        info_fertilizacion += f"  - Nº Albarán: (Ver Observaciones)\n"
                        info_fertilizacion += f"  - Riqueza NPK: (Ver Observaciones)\n"
                        info_fertilizacion += f"  - Dosis: {ab.dosis}\n"
                        info_fertilizacion += f"  - Tipo Fertilizacion: {ab.tipo}\n"
                        info_fertilizacion += f"  - Observaciones: {ab.observaciones}\n"

                return info_general + info_parcelas + info_tratamientos + info_semillas + info_analisis + info_ventas + info_fertilizacion

            except Exception as e:
                return f"Error generando cuaderno completo: {str(e)}"

        @mcp.tool()
        async def consultar_historico(
            consulta: str,
            anio: int = None,
            producto: str = None
        ) -> str:
            """
            Consulta datos históricos.
            Comando asociado: /consulta
            """
            try:
                qs = DiarioActividad.objects.all()
                filters = []
                if anio:
                    qs = qs.filter(fecha__year=anio)
                    filters.append(f"Año {anio}")
                if producto:
                    qs = qs.filter(producto_nombre__icontains=producto)
                    filters.append(f"Producto '{producto}'")

                count = await sync_to_async(qs.count)()
                
                resumen = f"Se encontraron {count} registros que coinciden con: {', '.join(filters)}.\n"
                if count > 0:
                    first = await sync_to_async(qs.first)()
                    resumen += f"Ejemplo: {first.fecha} - {first.tipo} - {first.producto_nombre}"
                
                return resumen
            except Exception as e:
                return f"Error en consulta: {str(e)}"

        self.stdout.write(self.style.SUCCESS("Iniciando servidor MCP Agrícola en puerto 8001..."))
        mcp.run(transport="http", host="0.0.0.0", port=8001, path="/mcp")