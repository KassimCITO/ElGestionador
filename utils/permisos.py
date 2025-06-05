from flask import session

def verificar_permiso(tipo):
    permisos = session.get("permisos", {})
    return permisos.get(tipo, False)
