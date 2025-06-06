# Manual de Usuario – Sistema de Gestión de Personas

## Índice

- [Introducción](#introducción)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
  - [Instalación con Docker Desktop](#instalación-con-docker-desktop)
  - [Instalación sin Docker](#instalación-sin-docker)
  - [Solución de problemas comunes](#solución-de-problemas-comunes)
- [Configuración y variables de entorno](#configuración-y-variables-de-entorno)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Primer uso](#primer-uso)
- [Funcionalidades principales](#funcionalidades-principales)
- [Gestión de Personas](#gestión-de-personas)
- [Gestión de Usuarios](#gestión-de-usuarios)
- [Reportes](#reportes)
- [Preguntas frecuentes (FAQ)](#preguntas-frecuentes-faq)
- [Soporte y contacto](#soporte-y-contacto)

---

## Introducción

Este sistema permite la gestión de personas y usuarios, con registro de datos personales, fotografía, estado, municipio, colonia y más. Incluye control de acceso, roles y reportes.

## Requisitos

- Python 3.10+ (verifica con `python --version`)
- Docker Desktop (opcional, recomendado)
- Git (opcional, para clonar el repositorio)
- Acceso a internet para instalar dependencias
- Sistema operativo Windows, Linux o macOS

## Instalación

### Instalación con Docker Desktop

1. **Instala Docker Desktop** desde [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
2. Clona o descarga el proyecto en tu equipo.
3. Abre una terminal en la carpeta del proyecto y ejecuta:

   ```powershell
   docker-compose up --build
   ```

4. Accede a la app en [http://localhost:5000](http://localhost:5000)
5. El usuario inicial es `admin` y la contraseña es `admin`.

**Ventajas:**

- No necesitas instalar Python ni dependencias manualmente.
- El entorno es reproducible y aislado.

### Instalación sin Docker

1. Instala Python 3.10+ en tu sistema. Descárgalo de [python.org](https://www.python.org/downloads/).
2. (Opcional) Crea y activa un entorno virtual:

   ```powershell
   python -m venv venv
   .\venv\Scripts\activate    # Windows
   # source venv/bin/activate  # Linux/macOS
   ```

3. Instala las dependencias:

   ```powershell
   pip install -r requirements.txt
   ```

   Si tienes problemas con permisos, usa:
   ```powershell
   pip install --user -r requirements.txt
   ```

4. Ejecuta la app:

   ```powershell
   python app.py
   ```

   Si ves un error de puerto en uso, cambia el puerto en `app.py` o cierra la app que lo esté usando.

5. Accede a la app en [http://localhost:5000](http://localhost:5000)

### Solución de problemas comunes

- **Python no reconocido:** Asegúrate de agregar Python al PATH durante la instalación.
- **Error de permisos:** Ejecuta la terminal como administrador o usa `pip install --user ...`.
- **Docker no inicia:** Reinicia Docker Desktop o tu equipo.
- **Puerto 5000 ocupado:** Cambia el puerto en `app.py` (por ejemplo, a 5001) y accede a `http://localhost:5001`.
- **Problemas con dependencias:** Actualiza pip con `python -m pip install --upgrade pip`.
- **Error de SQLite:** Verifica que tienes permisos de escritura en la carpeta del proyecto.

## Configuración y variables de entorno

Puedes crear un archivo `.env` en la raíz del proyecto para personalizar variables como:

```
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta
UPLOAD_FOLDER=static/uploads
```

Si usas Docker, el archivo `.env` se carga automáticamente.

## Estructura del proyecto

- `app.py`: Archivo principal de la aplicación.
- `utils/dbmanager.py`: Lógica de acceso a base de datos.
- `templates/`: Archivos HTML de la interfaz.
- `static/uploads/`: Carpeta donde se guardan las fotos.
- `municipios_limpio.json`: Catálogo de estados y municipios.
- `database.db`: Base de datos SQLite.
- `requirements.txt`: Lista de dependencias Python.
- `docker-compose.yml` y `Dockerfile`: Archivos para despliegue con Docker.

## Primer uso

- Ingresa con usuario `admin` y contraseña `admin`.
- Cambia la contraseña del admin si lo deseas.
- Crea usuarios adicionales desde el menú "Usuarios" (solo admin).

## Funcionalidades principales

- **CRUD de personas:** Alta, edición, eliminación y consulta de personas con datos completos.
- **Gestión de usuarios:** Control de acceso, roles y permisos.
- **Selección dinámica de estado y municipio:** Los municipios se filtran automáticamente según el estado seleccionado.
- **Carga de fotografía:** Validación de tamaño mínimo (512x512 px).
- **Reportes:** Visualización e impresión de listados de personas.
- **Tema claro/oscuro:** Alternancia desde la barra superior.

## Gestión de Personas

- Accede al menú "Personas".
- Haz clic en "+ Nueva Persona" para registrar una nueva.
- Completa todos los campos obligatorios:
  - Nombres, apellidos, CURP, dirección, colonia, código postal, fecha de nacimiento, estado, municipio, clave de elector y fotografía.
- Para editar o eliminar, usa los botones correspondientes en la lista.

## Gestión de Usuarios

- Solo el usuario admin puede crear, editar o eliminar usuarios.
- Define permisos de lectura, creación, edición e impresión para cada usuario.

## Reportes

- Accede a la sección "Reportes" para ver e imprimir el listado general de personas.

## Preguntas frecuentes (FAQ)

**¿Cómo restauro la base de datos a estado inicial?**

- Borra el archivo `database.db` y reinicia la app. Se creará una base vacía (solo admin).

**¿Dónde se guardan las fotos?**

- En la carpeta `static/uploads/`.

**¿Puedo cambiar el puerto de la app?**

- Sí, edita la línea `app.run(port=5000)` en `app.py`.

**¿Cómo limpio imágenes o datos de prueba?**

- Borra manualmente los archivos en `static/uploads/` y/o la base de datos.

**¿Qué hago si olvido la contraseña del admin?**

- Borra `database.db` para restaurar el acceso con admin/admin (se perderán los datos).

## Soporte y contacto

Para soporte técnico, contacta al administrador del sistema o revisa la documentación incluida en el repositorio.

---

## Descripción

Sistema web para la gestión de personas y usuarios, desarrollado en Flask y SQLite, con soporte para Docker y despliegue rápido.

## Instalación rápida

- **Con Docker:**
  ```powershell
  docker-compose up --build
  ```
- **Sin Docker:**
  ```powershell
  pip install -r requirements.txt
  python app.py
  ```

## Acceso inicial

- Usuario: `admin`
- Contraseña: `admin`

## Licencia

Uso interno. Para más información, consulta al desarrollador.

## Ejemplos visuales y capturas de pantalla

A continuación se muestran ejemplos de cómo se ve el sistema en funcionamiento. Puedes agregar tus propias capturas de pantalla en la carpeta `static/` y enlazarlas aquí para personalizar el manual.

### Pantalla de inicio de sesión

![Pantalla de inicio de sesión](static/ejemplo_login.png)

### Menú principal (modo claro y oscuro)

![Menú principal claro](static/ejemplo_menu_claro.png)

![Menú principal oscuro](static/ejemplo_menu_oscuro.png)

### Formulario de alta de persona

![Formulario nueva persona](static/ejemplo_nueva_persona.png)

### Listado de personas

![Listado de personas](static/ejemplo_listado_personas.png)

## Ejemplos de personalización de reportes

Puedes personalizar el reporte de personas desde la opción "⚙️ Personalizar Plantilla" (solo administrador). Aquí tienes ejemplos visuales y de código para inspirarte:

### Ejemplo de encabezado simple

```html
<h1 style='color:navy'>Mi Reporte de Personas</h1>
```

### Ejemplo de encabezado con logo

```html
<div style='display:flex;align-items:center'>
  <img src='/static/logo.svg' height='40' style='margin-right:10px'>
  <span style='font-size:1.5em'>Reporte de Personas 2025</span>
</div>
```

### Ejemplo de pie de página con fecha y usuario

```html
<div style='font-size:12px;text-align:right'>Generado el {{ "now"|date("%d/%m/%Y") }} por {{ session['usuario'] }}</div>
```

### Ejemplo de pie con firma

```html
<div class='firma'>Firma del responsable</div>
```

### Ejemplo de estilos CSS para tabla zebra

```css
.table-striped tbody tr:nth-child(odd) { background: #f9f9f9; }
```

### Ejemplo para ocultar columnas en impresión (CURP)

```css
@media print { .table th:nth-child(2), .table td:nth-child(2) { display:none; } }
```

### Ejemplo de firma personalizada

```css
.firma { margin-top:40px; text-align:right; font-style:italic; }
```

### Vista previa visual

A continuación, algunos ejemplos de cómo se vería el reporte:

#### Encabezado con logo

![Ejemplo encabezado con logo](static/logo.svg)

#### Tabla con estilo zebra

![Ejemplo tabla zebra](static/ejemplo_tabla_zebra.png)

#### Pie de página con firma

![Ejemplo pie firma](static/ejemplo_firma.png)

> Puedes crear tus propias capturas de pantalla y guardarlas en la carpeta `static/` para personalizar aún más este manual.

---

## Aviso de licencia

Este proyecto está licenciado bajo los términos de la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles. Puedes usar, modificar y distribuir este software libremente, pero se proporciona "tal cual", sin garantías.

---
