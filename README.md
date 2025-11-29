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

## **🔧 Configuración del MCP Server**

### **Estado del Servidor**

El servidor MCP se inicia automáticamente en el puerto **8001** junto con el proyecto. No necesitas lanzarlo manualmente.

### **Conexión con Open WebUI**

Para que la IA pueda usar las herramientas de Django, debes conectar Open WebUI con el servidor MCP (esto se hace una sola vez):

1. Accede al panel de administración de Open WebUI: [http://localhost:3100/admin](https://www.google.com/search?q=http://localhost:3100/admin)
2. Ve a **Settings** \> **External Tools**.
3. Busca la sección **MCP**.
4. Añade una nueva conexión con los siguientes datos:
   * **URL:** http://ai-agriculture:8001/mcp
   * *(Nota: Asegúrate de incluir /mcp al final).*
5. Guarda la configuración.

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
