from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from config import Config
from utils.permisos import verificar_permiso
from dotenv import load_dotenv
from PIL import Image
import json
from utils.dbmanager import DBManager

import os

REPORTE_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'reporte_config.json')

def cargar_config_reporte():
    if os.path.exists(REPORTE_CONFIG_PATH):
        with open(REPORTE_CONFIG_PATH, encoding='utf-8') as f:
            return json.load(f)
    # Configuración por defecto
    return {
        "encabezado": "<h2 class='mb-4 text-center'>Reporte General de Personas</h2>",
        "pie": "<div class='text-center mt-4'><small>Generado por ElGestionador</small></div>",
        "estilos": ""
    }

def guardar_config_reporte(config):
    with open(REPORTE_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

app = Flask(__name__)
app.config.from_object(Config)

# Cargar variables de entorno desde .env
load_dotenv()

# Crear carpeta de subidas si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Cargar municipios de México en memoria
with open(os.path.join(os.path.dirname(__file__), 'municipios_limpio.json'), encoding='utf-8') as f:
    MUNICIPIOS_MX = json.load(f)

# Cargar estados de México en memoria (IDs y nombres)
ESTADOS_MX = [
    {"id": int(eid), "nombre": MUNICIPIOS_MX[eid][0]["nombre_estado"] if "nombre_estado" in MUNICIPIOS_MX[eid][0] else None}
    if isinstance(MUNICIPIOS_MX[eid][0], dict) and "nombre_estado" in MUNICIPIOS_MX[eid][0]
    else {"id": int(eid), "nombre": None}
    for eid in MUNICIPIOS_MX.keys()
]
# Si no hay nombre_estado, usar un mapeo manual (por compatibilidad)
ESTADOS_NOMBRES = [
    "Aguascalientes", "Baja California", "Baja California Sur", "Campeche", "Coahuila", "Colima", "Chiapas", "Chihuahua", "Ciudad de México", "Durango", "Guanajuato", "Guerrero", "Hidalgo", "Jalisco", "México", "Michoacán", "Morelos", "Nayarit", "Nuevo León", "Oaxaca", "Puebla", "Querétaro", "Quintana Roo", "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco", "Tamaulipas", "Tlaxcala", "Veracruz", "Yucatán", "Zacatecas"
]
for i, estado in enumerate(ESTADOS_MX):
    if not estado["nombre"]:
        estado["nombre"] = ESTADOS_NOMBRES[i]

dbman = DBManager()
dbman.create_tables()
dbman.migrate_add_fields()

app.permanent_session_lifetime = timedelta(minutes=30)

@app.before_request
def proteger_rutas():
    rutas_libres = ["login", "static"]
    if request.endpoint not in rutas_libres and not session.get("usuario"):
        return redirect(url_for("login"))
    # Si ya está logueado y entra a /, redirigir a dashboard
    if request.endpoint == "login" and session.get("usuario"):
        return redirect(url_for("dashboard"))

    # Bloqueo por intentos fallidos
    if request.endpoint == "login":
        if session.get("bloqueado_hasta"):
            from datetime import datetime
            if datetime.now() < session["bloqueado_hasta"]:
                flash("Demasiados intentos fallidos. Intenta más tarde.", "danger")
                return render_template("login.html")
            else:
                session.pop("bloqueado_hasta")
                session.pop("intentos_fallidos", None)

# Autenticación
@app.route("/", methods=["GET", "POST"])
def login():
    from datetime import datetime, timedelta
    if request.method == "POST":
        usuario = request.form["usuario"].strip()
        clave = request.form["clave"]
        user = dbman.get_usuario_by_username(usuario, clave)
        if user:
            session["usuario"] = user["usuario"]
            session["rol"] = user["rol"]
            session["permisos"] = {
                "lectura": bool(user["perm_lectura"]),
                "creacion": bool(user["perm_creacion"]),
                "edicion": bool(user["perm_edicion"]),
                "impresion": bool(user["perm_impresion"])
            }
            session.pop("intentos_fallidos", None)
            session.pop("bloqueado_hasta", None)
            flash(f"Bienvenido, {usuario}", "success")
            return redirect(url_for("dashboard"))
        else:
            intentos = session.get("intentos_fallidos", 0) + 1
            session["intentos_fallidos"] = intentos
            if intentos >= 3:
                session["bloqueado_hasta"] = datetime.now() + timedelta(minutes=5)
                flash("Demasiados intentos fallidos. Intenta de nuevo en 5 minutos.", "danger")
            else:
                flash(f"Usuario o contraseña incorrectos. Intento {intentos}/3", "danger")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

# Listar personas
@app.route("/personas")
def personas():
    if not verificar_permiso("lectura"):
        return redirect(url_for("dashboard"))
    personas = dbman.get_personas()
    # Mapear IDs a nombres de estado y municipio
    estados_dict = {e["id"]: e["nombre"] for e in ESTADOS_MX}
    municipios_dict = {}
    for eid, municipios in MUNICIPIOS_MX.items():
        municipios_dict[int(eid)] = {m["id"]: m["nombre"] for m in municipios}
    personas_list = []
    for p in personas:
        estado_nombre = estados_dict.get(p["id_estado"], "-")
        municipio_nombre = municipios_dict.get(p["id_estado"], {}).get(p["id_municipio"], "-")
        persona_dict = dict(p)
        persona_dict["estado"] = estado_nombre
        persona_dict["municipio"] = municipio_nombre
        personas_list.append(persona_dict)
    return render_template("personas.html", personas=personas_list)

# Nueva persona
@app.route("/personas/nueva", methods=["GET", "POST"])
def nueva_persona():
    if not verificar_permiso("creacion"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        id_estado = request.form["id_estado"]
        id_municipio = request.form["id_municipio"]
        clave_elector = request.form["clave_elector"].strip().upper()
        datos = {
            "nombre": request.form["nombre"].strip().upper(),
            "apellido_paterno": request.form["apellido_paterno"].strip().upper(),
            "apellido_materno": request.form["apellido_materno"].strip().upper(),
            "curp": request.form["curp"].strip().upper(),
            "direccion": request.form["direccion"],
            "colonia": request.form["colonia"],
            "cp": request.form["cp"],
            "fecha_nac": request.form["fecha_nac"],
            "id_estado": id_estado,
            "id_municipio": id_municipio,
            "clave_elector": clave_elector
        }
        if not datos["nombre"] or not datos["apellido_paterno"] or not datos["apellido_materno"] or not datos["curp"]:
            flash("Nombre, apellidos y CURP no pueden quedar en blanco.", "warning")
            return render_template("nueva_persona.html", estados=ESTADOS_MX, municipios_json=json.dumps(MUNICIPIOS_MX, ensure_ascii=False))
        archivo = request.files["foto"]
        nombre_archivo = None
        if archivo:
            try:
                img = Image.open(archivo)
                if img.width < 512 or img.height < 512:
                    flash("La fotografía debe tener al menos 512 x 512 píxeles.", "warning")
                    return render_template("nueva_persona.html", estados=ESTADOS_MX, municipios_json=json.dumps(MUNICIPIOS_MX, ensure_ascii=False))
                archivo.seek(0)
                nombre_archivo = secure_filename(archivo.filename)
                archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre_archivo))
            except Exception:
                flash("Archivo de imagen no válido.", "warning")
                return render_template("nueva_persona.html", estados=ESTADOS_MX, municipios_json=json.dumps(MUNICIPIOS_MX, ensure_ascii=False))
        dbman.insert_persona(datos, nombre_archivo)
        return redirect(url_for("personas"))
    return render_template("nueva_persona.html", estados=ESTADOS_MX, municipios_json=json.dumps(MUNICIPIOS_MX, ensure_ascii=False))

# Editar persona
@app.route("/personas/editar/<int:id>", methods=["GET", "POST"])
def editar_persona(id):
    if not verificar_permiso("edicion"):
        return redirect(url_for("dashboard"))
    persona = dbman.get_persona(id)
    if request.method == "POST":
        datos = {
            "nombre": request.form["nombre"].strip().upper(),
            "apellido_paterno": request.form["apellido_paterno"].strip().upper(),
            "apellido_materno": request.form["apellido_materno"].strip().upper(),
            "curp": request.form["curp"].strip().upper(),
            "direccion": request.form["direccion"],
            "colonia": request.form["colonia"],
            "cp": request.form["cp"],
            "fecha_nac": request.form["fecha_nac"],
            "id_estado": request.form["id_estado"],
            "id_municipio": request.form["id_municipio"],
            "clave_elector": request.form["clave_elector"].strip().upper(),
            "notas": request.form.get("notas", ""),
            "modificado_por": session.get("usuario")
        }
        if not datos["nombre"] or not datos["apellido_paterno"] or not datos["apellido_materno"] or not datos["curp"]:
            flash("Nombre, apellidos y CURP no pueden quedar en blanco.", "warning")
            return render_template("editar_persona.html", persona=persona, estados=ESTADOS_MX, municipios_json=json.dumps(MUNICIPIOS_MX, ensure_ascii=False))
        archivo = request.files["foto"]
        if archivo:
            try:
                img = Image.open(archivo)
                if img.width < 512 or img.height < 512:
                    flash("La fotografía debe tener al menos 512 x 512 píxeles.", "warning")
                    return render_template("editar_persona.html", persona=persona, estados=ESTADOS_MX, municipios_json=json.dumps(MUNICIPIOS_MX, ensure_ascii=False))
                archivo.seek(0)
                nombre_archivo = secure_filename(archivo.filename)
                archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre_archivo))
                dbman.update_persona_foto(id, nombre_archivo)
            except Exception:
                flash("Archivo de imagen no válido.", "warning")
                return render_template("editar_persona.html", persona=persona, estados=ESTADOS_MX, municipios_json=json.dumps(MUNICIPIOS_MX, ensure_ascii=False))
        dbman.update_persona(id, datos)
        return redirect(url_for("personas"))
    return render_template("editar_persona.html", persona=persona, estados=ESTADOS_MX, municipios_json=json.dumps(MUNICIPIOS_MX, ensure_ascii=False))

# Usuarios
@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    if session.get("rol") != "admin":
        return redirect(url_for("dashboard"))
    mostrar_formulario = request.args.get("nuevo") == "1"
    if request.method == "POST":
        nuevo = {
            "usuario": request.form["usuario"],
            "clave": request.form["clave"],
            "rol": request.form.get("rol", "user"),
            "perm_lectura": int("perm_lectura" in request.form),
            "perm_creacion": int("perm_creacion" in request.form),
            "perm_edicion": int("perm_edicion" in request.form),
            "perm_impresion": int("perm_impresion" in request.form),
        }
        dbman.insert_usuario(nuevo)
        return redirect(url_for("usuarios"))
    usuarios = dbman.get_usuarios()
    return render_template("usuarios.html", usuarios=usuarios, mostrar_formulario=mostrar_formulario)

@app.route("/usuarios/eliminar/<int:usuario_id>", methods=["POST", "GET"])
def eliminar_usuario(usuario_id):
    if session.get("rol") != "admin":
        return redirect(url_for("dashboard"))
    usuario = dbman.get_usuario(usuario_id)
    if not usuario or usuario["usuario"] == "admin":
        flash("No se puede eliminar el usuario administrador.", "warning")
        return redirect(url_for("usuarios"))
    dbman.delete_usuario(usuario_id)
    flash("Usuario eliminado correctamente.", "success")
    return redirect(url_for("usuarios"))

# Editar usuario
@app.route("/usuarios/editar/<int:usuario_id>", methods=["GET", "POST"])
def editar_usuario(usuario_id):
    if session.get("rol") != "admin":
        return redirect(url_for("dashboard"))
    usuario = dbman.get_usuario(usuario_id)
    if not usuario:
        flash("Usuario no encontrado.", "warning")
        return redirect(url_for("usuarios"))
    if usuario["usuario"] == "admin" and session.get("usuario") != "admin":
        flash("Solo el administrador puede editar su propia cuenta.", "warning")
        return redirect(url_for("usuarios"))
    if request.method == "POST":
        clave = request.form["clave"]
        rol = request.form.get("rol", "user")
        perm_lectura = int("perm_lectura" in request.form)
        perm_creacion = int("perm_creacion" in request.form)
        perm_edicion = int("perm_edicion" in request.form)
        perm_impresion = int("perm_impresion" in request.form)
        if clave:
            dbman.update_usuario(usuario_id, clave, rol, perm_lectura, perm_creacion, perm_edicion, perm_impresion)
        else:
            dbman.update_usuario_no_clave(usuario_id, rol, perm_lectura, perm_creacion, perm_edicion, perm_impresion)
        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for("usuarios"))
    return render_template("editar_usuario.html", usuario=usuario)

# Cerrar sesión
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/configuracion_reporte", methods=["GET", "POST"])
def configuracion_reporte():
    if session.get("rol") != "admin":
        return redirect(url_for("dashboard"))
    config = cargar_config_reporte()
    if request.method == "POST":
        if "encabezado" in request.form and "pie" in request.form and "estilos" in request.form:
            config["encabezado"] = request.form["encabezado"]
            config["pie"] = request.form["pie"]
            config["estilos"] = request.form["estilos"]
            guardar_config_reporte(config)
            flash("Plantilla de reporte actualizada.", "success")
            return redirect(url_for("configuracion_reporte"))
        # Restaurar valores por defecto si se solicita
        if request.form.get("restaurar") == "1":
            config = {
                "encabezado": "<h2 class='mb-4 text-center'>Reporte General de Personas</h2>",
                "pie": "<div class='text-center mt-4'><small>Generado por ElGestionador</small></div>",
                "estilos": ""
            }
            guardar_config_reporte(config)
            flash("Valores por defecto restaurados.", "info")
            return redirect(url_for("configuracion_reporte"))
    return render_template("configuracion_reporte.html", config=config)

@app.route("/reportes")
def reportes():
    if not verificar_permiso("lectura"):
        return redirect(url_for("dashboard"))
    personas = dbman.get_personas()
    estados_dict = {e["id"]: e["nombre"] for e in ESTADOS_MX}
    municipios_dict = {}
    for eid, municipios in MUNICIPIOS_MX.items():
        municipios_dict[int(eid)] = {m["id"]: m["nombre"] for m in municipios}
    personas_list = []
    for p in personas:
        estado_nombre = estados_dict.get(p["id_estado"], "-")
        municipio_nombre = municipios_dict.get(p["id_estado"], {}).get(p["id_municipio"], "-")
        persona_dict = dict(p)
        persona_dict["estado"] = estado_nombre
        persona_dict["municipio"] = municipio_nombre
        personas_list.append(persona_dict)
    config = cargar_config_reporte()
    return render_template("reportes.html", personas=personas_list, config_reporte=config)

@app.route("/personas/eliminar/<int:id>", methods=["POST", "GET"])
def eliminar_persona(id):
    if not verificar_permiso("edicion"):
        return redirect(url_for("dashboard"))
    dbman.delete_persona(id)
    flash("Persona eliminada correctamente.", "success")
    return redirect(url_for("personas"))

@app.route("/personas/reporte/<int:id>")
def reporte_persona(id):
    if not verificar_permiso("lectura"):
        return redirect(url_for("dashboard"))
    persona = dbman.get_persona(id)
    if not persona:
        flash("Persona no encontrada.", "warning")
        return redirect(url_for("personas"))
    estados_dict = {e["id"]: e["nombre"] for e in ESTADOS_MX}
    municipios_dict = {}
    for eid, municipios in MUNICIPIOS_MX.items():
        municipios_dict[int(eid)] = {m["id"]: m["nombre"] for m in municipios}
    persona_dict = dict(persona)
    persona_dict["estado"] = estados_dict.get(persona["id_estado"], "-")
    persona_dict["municipio"] = municipios_dict.get(persona["id_estado"], {}).get(persona["id_municipio"], "-")
    config = cargar_config_reporte()
    return render_template("reporte_persona.html", persona=persona_dict, config_reporte=config)

if __name__ == "__main__":
    app.run(debug=True)
