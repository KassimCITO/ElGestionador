import sqlite3
from config import Config

class DBManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE

    def get_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        with self.get_db() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT UNIQUE NOT NULL,
                    clave TEXT NOT NULL,
                    rol TEXT NOT NULL,
                    perm_lectura INTEGER DEFAULT 1,
                    perm_creacion INTEGER DEFAULT 1,
                    perm_edicion INTEGER DEFAULT 1,
                    perm_impresion INTEGER DEFAULT 1
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS personas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    apellido_paterno TEXT NOT NULL,
                    apellido_materno TEXT NOT NULL,
                    curp TEXT UNIQUE NOT NULL,
                    direccion TEXT NOT NULL,
                    colonia TEXT NOT NULL,
                    cp TEXT NOT NULL,
                    fecha_nac TEXT NOT NULL,
                    id_municipio INTEGER NOT NULL,
                    id_estado INTEGER NOT NULL,
                    clave_elector TEXT NOT NULL,
                    foto TEXT
                )
            """)
            admin = db.execute("SELECT * FROM usuarios WHERE usuario = 'admin'").fetchone()
            if not admin:
                db.execute("""
                    INSERT INTO usuarios (usuario, clave, rol, perm_lectura, perm_creacion, perm_edicion, perm_impresion)
                    VALUES ('admin', 'admin', 'admin', 1, 1, 1, 1)
                """)
                db.commit()

    def get_usuarios(self):
        with self.get_db() as db:
            return db.execute("SELECT * FROM usuarios").fetchall()

    def get_usuario(self, usuario_id):
        with self.get_db() as db:
            return db.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()

    def get_usuario_by_username(self, username, clave):
        with self.get_db() as db:
            return db.execute("SELECT * FROM usuarios WHERE usuario = ? AND clave = ?", (username, clave)).fetchone()

    def insert_usuario(self, nuevo):
        with self.get_db() as db:
            db.execute("""
                INSERT INTO usuarios (usuario, clave, rol, perm_lectura, perm_creacion, perm_edicion, perm_impresion)
                VALUES (:usuario, :clave, :rol, :perm_lectura, :perm_creacion, :perm_edicion, :perm_impresion)
            """, nuevo)
            db.commit()

    def update_usuario(self, usuario_id, clave, rol, perm_lectura, perm_creacion, perm_edicion, perm_impresion):
        with self.get_db() as db:
            db.execute("""
                UPDATE usuarios SET clave=?, rol=?, perm_lectura=?, perm_creacion=?, perm_edicion=?, perm_impresion=? WHERE id=?
            """, (clave, rol, perm_lectura, perm_creacion, perm_edicion, perm_impresion, usuario_id))
            db.commit()

    def update_usuario_no_clave(self, usuario_id, rol, perm_lectura, perm_creacion, perm_edicion, perm_impresion):
        with self.get_db() as db:
            db.execute("""
                UPDATE usuarios SET rol=?, perm_lectura=?, perm_creacion=?, perm_edicion=?, perm_impresion=? WHERE id=?
            """, (rol, perm_lectura, perm_creacion, perm_edicion, perm_impresion, usuario_id))
            db.commit()

    def delete_usuario(self, usuario_id):
        with self.get_db() as db:
            db.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
            db.commit()

    def get_personas(self):
        with self.get_db() as db:
            return db.execute("SELECT * FROM personas").fetchall()

    def get_persona(self, persona_id):
        with self.get_db() as db:
            return db.execute("SELECT * FROM personas WHERE id = ?", (persona_id,)).fetchone()

    def insert_persona(self, datos, nombre_archivo):
        with self.get_db() as db:
            db.execute("""
                INSERT INTO personas (nombre, apellido_paterno, apellido_materno, curp, direccion, colonia, cp, fecha_nac, id_estado, id_municipio, clave_elector, foto)
                VALUES (:nombre, :apellido_paterno, :apellido_materno, :curp, :direccion, :colonia, :cp, :fecha_nac, :id_estado, :id_municipio, :clave_elector, ?)
            """, (*[datos[k] for k in ["nombre","apellido_paterno","apellido_materno","curp","direccion","colonia","cp","fecha_nac","id_estado","id_municipio","clave_elector"]], nombre_archivo))
            db.commit()

    def update_persona(self, persona_id, datos):
        with self.get_db() as db:
            db.execute("""
                UPDATE personas
                SET nombre=:nombre, apellido_paterno=:apellido_paterno,
                    apellido_materno=:apellido_materno, curp=:curp,
                    direccion=:direccion, colonia=:colonia, cp=:cp, fecha_nac=:fecha_nac,
                    id_estado=:id_estado, id_municipio=:id_municipio, clave_elector=:clave_elector
                WHERE id = :id
            """, {**datos, "id": persona_id})
            db.commit()

    def update_persona_foto(self, persona_id, nombre_archivo):
        with self.get_db() as db:
            db.execute("UPDATE personas SET foto = ? WHERE id = ?", (nombre_archivo, persona_id))
            db.commit()
