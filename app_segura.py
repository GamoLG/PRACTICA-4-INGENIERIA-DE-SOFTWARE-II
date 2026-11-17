"""
app_segura.py — Versión CORREGIDA (Actividad 4)
================================================
Refactorización de app_vulnerable.py aplicando defensas en profundidad:
  - CORRECCIÓN 1: Consultas parametrizadas (Prepared Statements) contra SQLi
  - CORRECCIÓN 2: Validación de propiedad del recurso contra IDOR (HTTP 403)
  - CORRECCIÓN 3: Escape de salida HTML con markupsafe contra XSS
  - CORRECCIÓN 4: Hash de contraseñas con bcrypt (12 rondas)
  - CORRECCIÓN 5: Validación de entrada (longitud, tipo, caracteres)
"""

import sqlite3
from flask import Flask, request, jsonify, abort
from markupsafe import escape

app = Flask(__name__)
DB_FILE = "segura.db"


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL CHECK(length(username) BETWEEN 3 AND 50),
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('estudiante','docente','administrador'))
                DEFAULT 'estudiante'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL CHECK(length(trim(titulo)) >= 1),
            descripcion TEXT,
            estado TEXT NOT NULL CHECK(estado IN ('pendiente','en_progreso','completada')),
            owner_id INTEGER NOT NULL,
            FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════
# CORRECCIÓN 1: Consulta parametrizada
# Se usa marcador ? en lugar de concatenación.
# ══════════════════════════════════════════════
@app.route("/api/reserva", methods=["GET"])
def obtener_reserva():
    id_reserva = request.args.get("id")
    user_id_session = request.args.get("user_id")

    # CORRECCIÓN 5: Validación de entrada
    if not id_reserva or not id_reserva.isdigit():
        return jsonify({"error": "Parámetros inválidos o sesión no provista"}), 400

    if not user_id_session or not user_id_session.isdigit():
        return jsonify({"error": "Sesión no provista"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ SEGURO: consulta parametrizada con marcador ?
    query = "SELECT * FROM reservas WHERE id = ?"
    reserva = cursor.execute(query, (id_reserva,)).fetchone()

    conn.close()

    if not reserva:
        return jsonify({"error": "No encontrada"}), 404

    # ══════════════════════════════════════════
    # CORRECCIÓN 2: Validación de propiedad (Anti-IDOR)
    # Solo el dueño puede ver su propia reserva.
    # ══════════════════════════════════════════
    if str(reserva["owner_id"]) != str(user_id_session):
        # HTTP 403 Forbidden: el usuario no es el propietario
        return jsonify({"error": "Acceso denegado: no posee privilegios sobre este recurso"}), 403

    return jsonify(dict(reserva))


# ══════════════════════════════════════════════
# CORRECCIÓN 2: Anti-IDOR en eliminación
# Verifica propiedad antes de eliminar.
# ══════════════════════════════════════════════
@app.route("/api/reserva/<int:reserva_id>", methods=["DELETE"])
def eliminar_reserva(reserva_id):
    user_id_session = request.args.get("user_id")

    if not user_id_session or not user_id_session.isdigit():
        return jsonify({"error": "Sesión no provista"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Primero verificar que la reserva exista y sea del usuario
    reserva = cursor.execute(
        "SELECT * FROM reservas WHERE id = ?", (reserva_id,)
    ).fetchone()

    if not reserva:
        conn.close()
        return jsonify({"error": "No encontrada"}), 404

    # ✅ Verificación de propiedad
    if str(reserva["owner_id"]) != str(user_id_session):
        conn.close()
        return jsonify({"error": "Acceso denegado: no posee privilegios sobre este recurso"}), 403

    # ✅ SEGURO: consulta parametrizada
    cursor.execute("DELETE FROM reservas WHERE id = ?", (reserva_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Eliminada"})


# ══════════════════════════════════════════════
# CORRECCIÓN 1 (variante): Búsqueda parametrizada
# Reemplaza la concatenación por marcador ?.
# ══════════════════════════════════════════════
@app.route("/api/buscar", methods=["GET"])
def buscar_reservas():
    search = request.args.get("q", "")

    # CORRECCIÓN 5: Validación de longitud del parámetro
    if len(search) > 50:
        return jsonify({"error": "Búsqueda demasiado larga (máx. 50 caracteres)"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ SEGURO: consulta parametrizada con LIKE
    query = "SELECT * FROM reservas WHERE titulo LIKE ?"
    resultados = cursor.execute(query, (f"%{search}%",)).fetchall()

    conn.close()
    return jsonify([dict(r) for r in resultados])


# ══════════════════════════════════════════════
# CORRECCIÓN 3: Escape XSS con markupsafe
# Toda salida HTML pasa por escape().
# ══════════════════════════════════════════════
@app.route("/api/comentario", methods=["POST"])
def agregar_comentario():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos requeridos"}), 400

    nombre = data.get("nombre", "Anónimo")
    comentario = data.get("comentario", "")

    # ✅ SEGURO: escape de HTML para evitar XSS
    html = f"<h3>Comentario de {escape(nombre)}</h3><p>{escape(comentario)}</p>"
    return html


# ══════════════════════════════════════════════
# CORRECCIÓN 4: Registro con hash bcrypt
# y validación de entrada.
# ══════════════════════════════════════════════
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos requeridos"}), 400

    username = data.get("username", "")
    password = data.get("password", "")
    role = data.get("role", "estudiante")

    # Validación de entrada
    if len(username) < 3 or len(username) > 50:
        return jsonify({"error": "Username debe tener entre 3 y 50 caracteres"}), 400

    if len(password) < 8:
        return jsonify({"error": "Contraseña debe tener al menos 8 caracteres"}), 400

    if role not in ("estudiante", "docente", "administrador"):
        return jsonify({"error": "Rol inválido"}), 400

    import bcrypt
    # ✅ SEGURO: hash con bcrypt, 12 rondas de salt
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Usuario ya existe"}), 400

    conn.close()
    return jsonify({"message": "Registrado"}), 201


if __name__ == "__main__":
    init_db()
    app.run(debug=False, port=5001)
