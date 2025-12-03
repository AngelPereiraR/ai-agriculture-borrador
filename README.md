# **Proyecto-Agente-Futuro---Agricultura**

**Sistema de Gestión Agrícola Inteligente**

La misión principal de este proyecto es crear un **registro histórico de las actividades por campaña** agrícola. Esta base de datos centralizada permite:

1. **Automatizar la generación de documentos oficiales:** Rellenar automáticamente el **Cuaderno de Explotación** y el **Documento de Acompañamiento al Transporte (DAT)**, reduciendo la carga administrativa.
2. **Consultas a Largo Plazo:** Garantizar que la información siga siendo accesible y consultable años más adelante para análisis históricos y auditorías.

Este sistema utiliza una arquitectura basada en **Docker DevContainers** para asegurar un entorno de desarrollo robusto y replicable.

## **🏗️ Stack Tecnológico**

* **Backend:** Django 5+ (Python)
* **Base de Datos:** PostgreSQL 15
* **IA:** Ollama (LLM Local) \+ Open WebUI (Interfaz de Chat)
* **Infraestructura:** Docker Compose

## **🚀 Guía de Inicio Rápido**

Sigue estos pasos para levantar el proyecto desde cero en tu máquina local.

### **1\. Requisitos Previos**

Asegúrate de tener instalado:

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) o Docker Engine (Linux).
* [Visual Studio Code (VS Code)](https://code.visualstudio.com/).
* Extensión [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) para VS Code.

### **2\. Configuración de Variables de Entorno**

El proyecto necesita credenciales para funcionar.

1. Ubícate en la **raíz del proyecto** (al mismo nivel que .devcontainer y src).
2. Copia la plantilla de configuración:
   \# En terminal (Linux/Mac/Git Bash) desde la raíz
   cp .env.template .env

3. (Opcional) Edita el archivo .env si necesitas cambiar contraseñas. La configuración por defecto es segura para desarrollo local.

**⚠️ Importante:** El archivo .env contiene claves secretas y **nunca** debe subirse al repositorio (ya está bloqueado en .gitignore).

### **3\. Levantar el Entorno (DevContainer)**

1. Abre la carpeta del proyecto en **VS Code**.
2. Pulsa F1 (o Ctrl+Shift+P) y selecciona:**Dev Containers: Reopen in Container**
3. Espera a que Docker construya las imágenes (la primera vez puede tardar unos minutos).

### **4\. Configuración Automática (Post-Create)**

Al abrir el contenedor, se ejecutará automáticamente un script de configuración. **No necesitas escribir nada**.

El sistema realizará los siguientes pasos por sí solo:

1. **Instalación de dependencias:** (requirements.txt y pre-commit).
2. **Espera de Base de Datos:** Verifica que PostgreSQL esté listo.
3. **Migraciones:** Aplica los cambios en la base de datos.
4. **Creación de Superusuario:** Crea automáticamente un usuario administrador con las credenciales definidas en .env (o por defecto: admin / admin).

**Nota:** Verás el progreso de esta configuración en las terminales que se abren automáticamente.

### **5\. Ejecución de Servidores**

Gracias a las tareas de VS Code (tasks.json), los servidores se iniciarán automáticamente una vez termine la configuración.

Verás dos terminales dedicadas en VS Code:

1. **Run Django Server:** Ejecuta el backend en el puerto 8000\.
2. **Run MCP Server:** Ejecuta el servidor de herramientas IA en el puerto 8001\.

## **🌍 Acceso a los Servicios**

* **Web Django:** [http://localhost:8000](https://www.google.com/search?q=http://localhost:8000)
* **Panel de Admin:** [http://localhost:8000/admin](https://www.google.com/search?q=http://localhost:8000/admin)
  * *Usuario:* admin
  * *Contraseña:* admin (o la que definiste en .env)
* **Open WebUI (Chat IA):** [http://localhost:3100](https://www.google.com/search?q=http://localhost:3100)

## **📖 Guía de Uso**

Sigue estos pasos para configurar completamente Open WebUI y comenzar a usar el asistente agrícola inteligente.

### **Paso 1: Registro del Administrador**

La primera vez que accedas a Open WebUI ([http://localhost:3100](http://localhost:3100)), se te solicitará crear una cuenta de administrador:

1. Introduce un **nombre de usuario**.
2. Proporciona una **dirección de correo electrónico**.
3. Establece una **contraseña** segura.
4. Haz clic en **Sign Up** para crear la cuenta.

**Nota:** El primer usuario registrado automáticamente tendrá privilegios de administrador.

### **Paso 2: Configuración del MCP Server**

El servidor MCP se inicia automáticamente en el puerto **8001** junto con el proyecto. Para conectarlo con Open WebUI:

1. Accede al panel de administración: [http://localhost:3100/admin](http://localhost:3100/admin)
2. Ve a **Settings** → **External Tools**.
3. Haz clic en **Import**.
4. Selecciona el archivo `src/rag/custom-external-tools-to-import.json` del directorio del proyecto.
5. Las herramientas de agricultura se importarán automáticamente.

### **Paso 3: Configuración de Prompts**

Para importar los prompts personalizados del sistema:

1. Haz clic en **Workspace** (en el menú lateral).
2. Selecciona **Prompts**.
3. Haz clic en **Import**.
4. Selecciona el archivo `src/rag/custom-prompts-to-import.json`.
5. Los prompts personalizados estarán ahora disponibles.

### **Paso 4: Configuración del Modelo Personalizado**

Para configurar el asistente agrícola inteligente:

1. Ve a **Admin Panel** → **Settings** → **Models** → **Manage Models**.
2. En el campo **Pull a model from Ollama.com**, escribe `qwen3:latest`.
3. Haz clic en **Pull Model** y espera a que se descargue (puede tardar unos minutos).
4. Una vez descargado, ve a **Workspace** → **Models**.
5. Haz clic en **Import**.
6. Selecciona el archivo `src/rag/custom-models-to-import.json`.
7. Localiza el modelo **Asistente Agrícola Inteligente** y haz clic en los **tres puntos (...)** → **Edit**.
8. En **Base Model (From)**, selecciona `qwen3:latest`.
9. En la sección **Tools**, marca la casilla **Agriculture Tools**.
10. Haz clic en **Save & Update**.

**⚠️ Problema con la descarga del modelo:**

Si al hacer **Pull** del modelo se queda permanentemente en **100%** o **0%** desde el comienzo y no inicia la descarga, es probable que sea un problema temporal de los servidores de Ollama que están bloqueando las descargas en ese momento.

**Solución:** Espera hasta el día siguiente (preferiblemente entre las **09:00-14:00 CET/CEST**) para realizar la configuración cuando los servidores estén desbloqueados.

¡Ya está todo listo! Ahora puedes comenzar a usar el asistente agrícola inteligente para gestionar tus actividades agrícolas.

### **⚠️ Consideraciones de Rendimiento**

**Tiempo de respuesta inicial:**
Open WebUI puede tardar varios minutos en "despertar" los modelos antes de responder a la primera petición de un chat. Si el modelo tarda **más de 7-10 minutos** en pasar de la fase de buscando conocimiento, considera usar modelos más ligeros que requieren menos recursos:

- `qwen3:4b` (4 mil millones de parámetros)
- `qwen3:1.7b` (1.7 mil millones de parámetros)
- `qwen3:0.6b` (600 millones de parámetros)

**Requisitos de hardware:**

Para un rendimiento adecuado se **requiere una tarjeta gráfica NVIDIA**. Si solo dispones de CPU, debes realizar los siguientes ajustes antes de lanzar el proyecto:

1. Abre el archivo `.devcontainer/compose.yaml` (para desarrollo) o `build/compose.yaml` (para producción).
2. Localiza y **comenta** las siguientes líneas que configuran la GPU:
   ```yaml
   runtime: nvidia
   environment:
     - NVIDIA_VISIBLE_DEVICES=all
   ```
3. **Comenta estas líneas** añadiendo `#` al inicio de cada una.
4. En VS Code, pulsa **F1** (o **Ctrl+Shift+P**) y selecciona: **Dev Containers: Rebuild Container**.

**Nota:** El rendimiento en modo CPU será significativamente más lento que con GPU NVIDIA.

### **Uso del Chat**

Una vez completada la configuración, puedes comenzar a usar el asistente:

1. Haz clic en **New Chat** en la interfaz de Open WebUI.
2. Selecciona el modelo **Asistente Agrícola Inteligente** en el menú desplegable de modelos.
3. (Opcional) Haz clic en **Set as default** para usar este modelo por defecto en futuros chats.
4. En el campo de texto del chat, escribe `/` para ver todos los **comandos disponibles** (prompts personalizados).
5. Selecciona el comando deseado o escribe tu consulta directamente.

¡Ahora estás listo para interactuar con el asistente agrícola inteligente!

### **📋 Guía de Comandos Disponibles**

El sistema incluye los siguientes prompts personalizados que puedes invocar escribiendo `/` en el chat:

#### **Configuración Inicial**
- `/config_explotacion` - Configurar la explotación agrícola principal con todos sus datos oficiales (REGA, titular, dirección).
- `/nuevo_titular` - Registrar un titular administrativo con datos de contacto y documentación.

#### **Gestión de Recursos**
- `/nueva_parcela` - Dar de alta una parcela con identificación SIGPAC, cultivo, superficie y régimen hídrico.
- `/nuevo_personal` - Registrar un trabajador o aplicador con sus datos personales y habilitaciones.
- `/nueva_maquina` - Registrar maquinaria de aplicación (ROMA) con fechas de inspección.
- `/nuevo_vehiculo` - Dar de alta un vehículo para transporte (tractor, remolque, furgoneta, etc.).
- `/nuevo_cliente` - Registrar un destinatario/cliente con datos fiscales y dirección.
- `/nuevo_transportista` - Registrar una empresa de transportes para usar en los DAT.
- `/nuevo_asesor` - Dar de alta un asesor técnico (GIP) con número ROPO.

#### **Actividades de Campo**
- `/tratamiento` - Registrar una aplicación de fitosanitarios con producto, dosis, plaga y equipo utilizado.
- `/riego` - Registrar riego o fertilización con horarios y cantidades.
- `/siembra` - Registrar siembra con semilla tratada, indicando producto fitosanitario aplicado.
- `/analisis` - Registrar un análisis de laboratorio (suelo, foliar, agua, residuos).
- `/venta` - Registrar venta o salida de cosecha con datos del cliente y lote.

#### **Documentación Oficial**
- `/cuaderno` - Generar el Cuaderno de Explotación completo para un año específico (incluye todas las secciones oficiales).
- `/dat` - Generar un Documento de Acompañamiento al Transporte con datos del destinatario, productos, transporte y calidad.

#### **Consultas**
- `/consulta` - Realizar consultas avanzadas al histórico de datos con filtros opcionales (año, producto, actividad, parcela, plaga).

**Nota:** Al seleccionar un comando, el sistema te solicitará los parámetros necesarios mediante un formulario interactivo.

### **Paso 5 (Opcional): Administración de Usuarios y Grupos**

El administrador puede añadir usuarios adicionales y crear grupos con permisos personalizados.

**Añadir usuarios:**

1. Ve a **Admin Panel** → **Users** → **Overview**.
2. Haz clic en el botón **Add User** (icono **+**).
3. Completa el formulario:
   - **Rol:** Selecciona entre `Pending`, `User` o `Admin`.
   - **Nombre:** Introduce el nombre del usuario.
   - **Email:** Proporciona el correo electrónico.
   - **Contraseña:** Establece una contraseña.
4. Alternativamente, puedes **importar un archivo CSV** con múltiples usuarios.

**Crear grupos:**

1. Ve a **Admin Panel** → **Users** → **Groups**.
2. Haz clic en **Create Group**.
3. En la pestaña **General**, asigna un nombre al grupo.
4. En la pestaña **Permissions**, selecciona los permisos que tendrá el grupo y desmarca aquellos que estarán prohibidos.
5. En la pestaña **Users**, selecciona los usuarios que formarán parte de este grupo.
6. Guarda la configuración.

## **👩‍💻 Flujo de Trabajo (Desarrollo)**

### **Gestión de Base de Datos (Modelos)**

Si modificas o creas un archivo models.py:

1. **Crea la migración:**
   python src/manage.py makemigrations

2. **Aplica el cambio en tu BD local:**
   python src/manage.py migrate

3. **Guarda los cambios:** Debes hacer git commit tanto de tu código (models.py) como de los archivos generados en migrations/. **¡No los ignores\!** Son necesarios para que tus compañeros tengan la misma estructura de BD.

### **Preparación para Commit**

Antes de hacer un commit, se recomienda ejecutar:

pre-commit run \-a

Esto asegura que todos los hooks de calidad de código se ejecuten en todos los archivos.

## **🚀 Modo Producción**

1. **Configuración de Variables de Entorno:**
   Crea un archivo `.env.prod` en la raíz del proyecto (basado en `.env.template` o `.env`) con las credenciales de producción.

2. **Crear la imagen de producción:**
   ```bash
   docker build -t agro:0.1 -f build/Dockerfile .
   ```

3. **Crear y levantar el entorno Docker de producción:**
   ```bash
   docker compose -f build/compose.yaml up --build
   ```

4. **Configuración Manual Post-Lanzamiento:**
   Una vez levantado el entorno de producción, accede al contenedor (`docker exec -it <container_id> /bin/bash`) y ejecuta:

   *   **Migración de modelos:**
       ```bash
       python manage.py migrate
       ```
   *   **Levantamiento de los servicios:**
       ```bash
       python manage.py runserver 0.0.0.0:8000
       python manage.py run_mcp_server
       ```

## **🛠️ Solución de Problemas**

### Los servidores no arrancan automáticamente:
Si las terminales de tareas no aparecen:

1. Presiona F1 \> **Tasks: Run Task**.
2. Selecciona "1. Run Django Server" o "2. Run MCP Server".

### Error de conexión a Base de Datos:
Si Docker no reconoce las contraseñas o falla la conexión:

1. Verifica que el archivo .env existe en la raíz.
2. Reconstruye el contenedor: F1 \> **Dev Containers: Rebuild Container**.

### Nuevas librerías:
Si al ejecutar el código falta alguna librería:

1. Haz git pull para bajar los últimos cambios.
2. Ejecuta pip install \-r src/requirements.txt manualmente si el contenedor ya estaba abierto.

### Incompatibilidad con Open WebUI v0.6.40:
Si tienes instalada la versión **v0.6.40** de Open WebUI, FastMCP se rompe y no funciona correctamente. Para solucionarlo usando **Docker Desktop**:

**En desarrollo:**
1. Abre **Docker Desktop**.
2. Ve a la sección **Containers**.
3. Busca el stack `proyectoagentefuturoagricultura-borrador_devcontainer`.
4. Dentro del stack, localiza el contenedor `openwebui-1` y haz clic en el icono de la **papelera** para eliminarlo.
5. Ve a la sección **Volumes**.
6. Busca el volumen `proyectoagentefuturoagricultura-borrador_devcontainer_openwebui_data` y haz clic en el icono de la **papelera** para eliminarlo.
7. Vuelve a abrir el proyecto en el DevContainer desde VS Code para que se reinstale la versión v0.6.36.

**En producción:**
1. Abre **Docker Desktop**.
2. Ve a la sección **Containers**.
3. Busca el stack `proyectoagentefuturoagricultura-borrador_build`.
4. Dentro del stack, localiza el contenedor `openwebui-1` y haz clic en el icono de la **papelera** para eliminarlo.
5. Ve a la sección **Volumes**.
6. Busca el volumen `proyectoagentefuturoagricultura-borrador_build_openwebui_data` y haz clic en el icono de la **papelera** para eliminarlo.
7. Vuelve a levantar el entorno:
   ```bash
   docker compose -p proyectoagentefuturoagricultura-borrador_build -f build/compose.yaml up -d
   ```

**Nota:** La versión v0.6.36 de Open WebUI es la última versión estable compatible con FastMCP.
