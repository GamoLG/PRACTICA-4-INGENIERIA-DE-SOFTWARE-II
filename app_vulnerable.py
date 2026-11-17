"""
app_vulnerable.py — Versión INSEGURA (Actividad 3)
===================================================
Implementación defectuosa con vulnerabilidades intencionales:
  - VULNERABILIDAD 1: Inyección SQL por concatenación de cadenas
  - VULNERABILIDAD 2: IDOR — sin verificación de propiedad del recurso
  - VULNERABILIDAD 3: XSS — renderización directa sin escape de HTML

Este archivo existe SOLO para fines educativos y de auditoría SAST.
NO usar en producción.
"""

import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_FILE = "vulnerable.db"


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            descripcion TEXT,
            estado TEXT,
            owner_id INTEGER
        )
    """)
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════
# VULNERABILIDAD 1: INYECCIÓN SQL
# La búsqueda concatena directamente la entrada
# del usuario en la consulta SQL.
# ══════════════════════════════════════════════
@app.route("/api/reserva", methods=["GET"])
def obtener_reserva():
    id_reserva = request.args.get("id")
    user_id_session = request.args.get("user_id")  # Simulación de sesión

    conn = get_db_connection()
    cursor = conn.cursor()

    # ⚠️ INSEGURO: concatenación directa → permite SQL injection
    query = f"SELECT * FROM reservas WHERE id = {id_reserva}"
    reserva = cursor.execute(query).fetchone()

    conn.close()

    if reserva:
        # ⚠️ INSEGURO: no verifica que owner_id == user_id_session (IDOR)
        return jsonify(dict(reserva))
    return jsonify({"error": "No encontrada"}), 404


# ══════════════════════════════════════════════
# VULNERABILIDAD 2: IDOR
# Cualquier usuario puede ver/editar/eliminar
# reservas de otros sin verificación de propiedad.
# ══════════════════════════════════════════════
@app.route("/api/reserva/<int:reserva_id>", methods=["DELETE"])
def eliminar_reserva(reserva_id):
    user_id_session = request.args.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    # ⚠️ INSEGURO: elimina sin verificar que owner_id == user_id_session
    cursor.execute(f"DELETE FROM reservas WHERE id = {reserva_id}")
    conn.commit()
    conn.close()

    return jsonify({"message": "Eliminada"})


# ══════════════════════════════════════════════
# VULNERABILIDAD 1 (variante): Búsqueda por título
# con concatenación de cadenas.
# ══════════════════════════════════════════════
@app.route("/api/buscar", methods=["GET"])
def buscar_reservas():
    search = request.args.get("q", "")

    conn = get_db_connection()
    cursor = conn.cursor()

    # ⚠️ INSEGURO: concatenación directa del parámetro de búsqueda
    query = "SELECT * FROM reservas WHERE titulo LIKE '%" + search + "%'"
    resultados = cursor.execute(query).fetchall()

    conn.close()
    return jsonify([dict(r) for r in resultados])


# ══════════════════════════════════════════════
# VULNERABILIDAD 3: XSS (Cross-Site Scripting)
# Renderiza directamente el contenido del usuario
# sin escape, permitiendo inyección de scripts.
# ══════════════════════════════════════════════
@app.route("/api/comentario", methods=["POST"])
def agregar_comentario():
    data = request.get_json()
    nombre = data.get("nombre", "Anónimo")
    comentario = data.get("comentario", "")

    # ⚠️ INSEGURO: render_template_string sin escape → XSS
    html = render_template_string(
        f"<h3>Comentario de {nombre}</h3><p>{comentario}</p>"
    )
    return html


# ══════════════════════════════════════════════
# ENDPOINT DE REGISTRO SIN VALIDACIÓN
# Acepta cualquier dato sin restricciones.
# ══════════════════════════════════════════════
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")  # ⚠️ Se guarda en texto plano
    role = data.get("role", "estudiante")

    conn = get_db_connection()
    cursor = conn.cursor()

    # ⚠️ INSEGURO: contraseña en texto plano, sin validación de longitud ni complejidad
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Usuario ya existe"}), 400

    conn.close()
    return jsonify({"message": "Registrado"}), 201


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
