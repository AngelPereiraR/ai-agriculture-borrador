# Diccionario Maestro de Entidades y Sinónimos (NLP/RAG)

Este documento relaciona los términos coloquiales del usuario con las entidades oficiales extraídas de los documentos (Cuaderno/DAT) y los modelos de datos.

## 1. Actores y Personas
Roles implicados en la gestión, aplicación y transporte.

| Entidad Oficial / Campo | Sinónimos y Variaciones (User Intent) | Contexto y Campos Relacionados |
| :--- | :--- | :--- |
| **Titular de la Explotación** | El dueño, el jefe, el agricultor, yo (si es el usuario), el propietario, "a mi nombre". | *Cuaderno 1.1, DAT 1.1.* Responsable legal. Campos: NIF, Nombre, Dirección. |
| **Representante / Autorizado** | El gestor, quien me firma, persona autorizada, apoderado, encargado. | *Cuaderno 1.1, DAT 1.1/6.* Firma por el titular. Campos: DNI, Nombre. |
| **Aplicador** | El que sulfata, tractorista, fumigador, la empresa de servicios, operario. | *Cuaderno 1.2, 3.1.* Quien echa el producto. Campos: ROPO, NIF, Carné (Básico/Cualificado). |
| **Asesor (GIP)** | El técnico, el ingeniero, el perito, quien valida, ATRIAS. | *Cuaderno 1.4, 3.1bis.* Técnico que justifica tratamientos. Campos: Nº ROPO, Firma. |
| **Destinatario / Cliente** | Comprador, la cooperativa, almazara, el almacén, a quién se lo vendo, receptor. | *DAT 2, Cuaderno 5.* Quien recibe la carga. Campos: RGSEAA, NIF, Domicilio. |
| **Transportista** | El camionero, el chófer, el del porte, conductor. | *DAT 3, 7.* Quien mueve la carga. Campos: NIF, Firma. |
| **Rebuscador** | El que rebusca, recolector residual. | *DAT 3.* Figura específica para recogida de remanentes. |

## 2. Lugares y Ubicaciones
Identificación geográfica y logística de las tierras e instalaciones.

| Entidad Oficial / Campo | Sinónimos y Variaciones (User Intent) | Contexto y Campos Relacionados |
| :--- | :--- | :--- |
| **Explotación** | La finca, el campo, la empresa agrícola, unidad de producción. | *General.* Entidad abstracta que agrupa parcelas. Campos: REGA, Nombre Comercial. |
| **Parcela / Recinto** | El trozo, la tierra, el olivar, la viña, la suerte, bancal, "la de abajo". | *Cuaderno 2.1, DAT 1.2.* Unidad física de cultivo. Campos: Polígono, Parcela, Recinto, SIGPAC/Catastro. |
| **Referencia SIGPAC** | Los números de la parcela, la referencia, las coordenadas, el mapa. | Identificador único. Campos: Provincia, Municipio, Agregado, Zona. |
| **Local de Almacenamiento** | La nave, la cochera, el cuarto de aperos, el almacén de los venenos, depósito. | *Cuaderno 3.4.* Donde se guardan los fitosanitarios. |
| **Punto de Captación de Agua** | El pozo, la balsa, la toma de agua, el río, canal. | *Cuaderno 2.2.* Puntos a proteger de contaminación. Coordenadas UTM. |
| **Zona Específica / Protegida** | Zona vulnerable, parque natural, zona de protección, red natura. | *Cuaderno 2.2.* Restricciones medioambientales (Hábitats, Agua potable). |
| **Domicilio / Dirección** | Donde vivo, dirección fiscal, calle, domicilio social. | *DAT 1.1, 2.* Dirección legal (no necesariamente la finca). Campos: Vía, CP, Municipio. |

## 3. Acciones y Eventos (Actividades)
Tareas que se registran en el diario o generan documentos.

| Entidad Oficial / Campo | Sinónimos y Variaciones (User Intent) | Contexto y Campos Relacionados |
| :--- | :--- | :--- |
| **Tratamiento Fitosanitario** | Sulfatar, curar, echar veneno, fumigar, tratar, aplicación, rociar. | *Cuaderno 3.1.* Actividad química principal. Campos: Dosis, Producto, Plaga, Eficacia. |
| **Fertilización / Abonado** | Echar abono, nitrato, estiércol, dar de comer, fertirrigación, abonar. | *Cuaderno 6.* Nutrición vegetal. Campos: Riqueza NPK, Tipo abono. |
| **Siembra** | Sembrar, plantar, poner la cosecha. | *Cuaderno 3.2.* Inicio de cultivo. Clave para semilla tratada. |
| **Cosecha / Recolección** | Coger (aceituna/mango), la campaña, recoger, vendimia, tala (si es madera). | *Cuaderno 5, DAT 4.* Origen del producto. |
| **Comercialización** | Vender, entregar, llevar al almacén, salida de producto. | *Cuaderno 5.* Venta legal. Campos: Albarán, Lote. |
| **Porte / Transporte** | El viaje, llevar la carga, el porte, transporte. | *DAT 4.* Movimiento físico. Campos: Fecha salida, Entrega estimada. |
| **Limpieza / Desinfección** | Lavar el camión, limpiar el almacén, desinfectar la cuba. | *Cuaderno 3.4, 3.5.* Tratamientos en instalaciones/vehículos. |
| **Análisis (Laboratorio)** | Analítica, muestra de residuos, ver si tiene bicho, análisis de tierra/foliar. | *Cuaderno 4.* Control de calidad/residuos. |
| **Inspección (ITEAF)** | Pasar la revisión de la máquina, la itv del tractor, inspección. | *Cuaderno 1.3.* Mantenimiento maquinaria. |

## 4. Objetos y Recursos
Insumos, maquinaria y productos físicos.

| Entidad Oficial / Campo | Sinónimos y Variaciones (User Intent) | Contexto y Campos Relacionados |
| :--- | :--- | :--- |
| **Producto Fitosanitario** | El veneno, el líquido, la cura, el bote, pesticida, herbicida, fungicida. | *Cuaderno 3.1.* Insumo químico. Campos: Nombre Comercial, Nº Registro (MAPA), Materia activa. |
| **Abono / Fertilizante** | Estiércol, basura, nitrato, urea, compost, la mierda (coloquial para orgánico). | *Cuaderno 6.* Insumo nutricional. Campos: Orgánico/Mineral, Riqueza. |
| **Cultivo / Especie** | Lo que tengo sembrado, el árbol, la planta (Ej: Mango, Olivo, Tomate). | *General.* Objeto de la producción. |
| **Variedad** | Tipo de planta (Ej: Osteen, Hojiblanca, Picual, Hass). | *General.* Especificación del cultivo. |
| **Semilla Tratada** | Simiente curada, grano certificado. | *Cuaderno 3.2.* Semilla con químico previo. |
| **Equipo de Aplicación** | La máquina, la cuba, el atomizador, la mochila, sulfatadora. | *Cuaderno 1.3.* Maquinaria para aplicar. Campos: Nº ROMA, Capacidad. |
| **Vehículo** | El camión, el tractor, la furgoneta, el coche. | *DAT 3.* Medio de transporte. Campos: Matrícula. |
| **Remolque** | El carro, la batea, el remolque. | *DAT 3.* Parte de carga del vehículo. |
| **Unidad de Carga** | Cajas, palots, sacos, a granel, big bag. | *DAT 4.* Formato de transporte. |
| **Plaga / Enfermedad** | El bicho, el gusano, la mosca, el repilo, la ceniza, el hongo, hierba. | *Cuaderno 3.1.* Motivo del tratamiento (Problema fitosanitario). |

## 5. Documentos y Datos Administrativos
Códigos, registros y papeles oficiales.

| Entidad Oficial / Campo | Sinónimos y Variaciones (User Intent) | Contexto y Campos Relacionados |
| :--- | :--- | :--- |
| **Cuaderno de Explotación** | El libro de campo, los papeles de la finca, el cuaderno digital, CUE. | Documento principal de registro (MAGRAMA). |
| **DAT (Doc. Acompañamiento)** | La guía, el conduce, el papel del transporte, albarán de transporte, guía de aceituna. | *Anexo VI.* Documento de trazabilidad (Junta de Andalucía). |
| **Nº Registro (Producto)** | El número del bote, registro MAPA, código del veneno. | Identificador único del fitosanitario. |
| **Nº ROMA** | Número de la máquina, inscripción de la cuba, cartilla agrícola. | Registro Oficial de Maquinaria Agrícola. |
| **Nº ROPO** | Carnet de aplicador, número de asesor, carnet cualificado. | Registro Oficial de Productores y Operadores. |
| **Nº REGA / REA** | Código de la explotación, número de ganadero/agricultor. | Registro de Explotaciones (Nacional/Autonómico). |
| **Nº RGSEAA** | Registro sanitario, número del almacén/cliente. | Registro General Sanitario de Empresas Alimentarias. |
| **Calidad Diferenciada** | Denominación de origen, ecológico, etiqueta de calidad, DO, IGP. | *DAT 5.* Certificaciones (DOP, IGP, ETG, Eco, Integrada). |
| **Lote** | Número de partida, lote de trazabilidad. | Identificador de un conjunto de producto. |
| **Albarán / Factura** | El papel de la compra, el ticket, justificante de venta. | Documento comercial. |