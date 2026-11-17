import os
import datetime
import pytest
import jwt
from fastapi.testclient import TestClient
from main import app, DB_FILE, init_db, reset_security_state, SECRET_KEY, ALGORITHM

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    init_db()
    yield
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

@pytest.fixture(autouse=True)
def reset_security():
    """Limpia bloqueos e historiales entre cada test."""
    reset_security_state()
    yield
    reset_security_state()

def test_01_registro_y_login_seguro():
    # Registro usuario A (estudiante)
    r_reg = client.post("/auth/register", json={
        "username": "estudiante_a",
        "password": "Password123!",
        "role": "estudiante"
    })
    assert r_reg.status_code == 201

    # Login exitoso
    r_log = client.post("/auth/login", json={
        "username": "estudiante_a",
        "password": "Password123!"
    })
    assert r_log.status_code == 200
    assert "access_token" in r_log.json()

    # Mitigación enumeración de usuarios (credenciales incorrectas devuelven 401 sin revelar existencia)
    r_fail = client.post("/auth/login", json={
        "username": "usuario_fantasma",
        "password": "Password123!"
    })
    assert r_fail.status_code == 401

def test_02_validacion_servidor_y_anti_mass_assignment():
    token = client.post("/auth/login", json={
        "username": "estudiante_a",
        "password": "Password123!"
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Intento de inyectar campo extra prohibido (Mass Assignment)
    r_extra = client.post("/tasks", json={
        "title": "Tarea 1",
        "status": "pendiente",
        "role": "administrador"
    }, headers=headers)
    assert r_extra.status_code == 422

    # Estado no permitido
    r_status = client.post("/tasks", json={
        "title": "Tarea 1",
        "status": "hackeado"
    }, headers=headers)
    assert r_status.status_code == 422

def test_03_control_acceso_anti_idor():
    # Registrar estudiante B
    client.post("/auth/register", json={
        "username": "estudiante_b",
        "password": "Password456!",
        "role": "estudiante"
    })
    token_b = client.post("/auth/login", json={
        "username": "estudiante_b",
        "password": "Password456!"
    }).json()["access_token"]

    # Estudiante A crea una tarea
    token_a = client.post("/auth/login", json={
        "username": "estudiante_a",
        "password": "Password123!"
    }).json()["access_token"]
    r_task = client.post("/tasks", json={"title": "Examen Final", "status": "pendiente"}, headers={"Authorization": f"Bearer {token_a}"})
    task_id = r_task.json()["task_id"]

    # Estudiante B intenta modificar la tarea del Estudiante A (Simulación IDOR)
    r_idor_put = client.put(f"/tasks/{task_id}", json={"title": "Alterado por B"}, headers={"Authorization": f"Bearer {token_b}"})
    assert r_idor_put.status_code == 403

    # Estudiante B intenta eliminar la tarea del Estudiante A (Simulación IDOR)
    r_idor_del = client.delete(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert r_idor_del.status_code == 403

def test_04_prevencion_inyeccion_sql():
    token_a = client.post("/auth/login", json={
        "username": "estudiante_a",
        "password": "Password123!"
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token_a}"}

    # Inyección SQL clásica en el parámetro de búsqueda
    sqli_payload = "' OR 1=1 --"
    r_search = client.get(f"/tasks/search?q={sqli_payload}", headers=headers)
    assert r_search.status_code == 200
    assert len(r_search.json()) == 0

def test_05_rbac_docente_y_administrador():
    # 1. Docente
    client.post("/auth/register", json={
        "username": "docente_1",
        "password": "DocentePassword123!",
        "role": "docente"
    })
    token_docente = client.post("/auth/login", json={
        "username": "docente_1",
        "password": "DocentePassword123!"
    }).json()["access_token"]
    headers_docente = {"Authorization": f"Bearer {token_docente}"}

    r_list = client.get("/tasks", headers=headers_docente)
    assert r_list.status_code == 200
    assert len(r_list.json()) >= 1

    # 2. Administrador
    client.post("/auth/register", json={
        "username": "admin_1",
        "password": "AdminPassword123!",
        "role": "administrador"
    })
    token_admin = client.post("/auth/login", json={
        "username": "admin_1",
        "password": "AdminPassword123!"
    }).json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    r_task = client.post("/tasks", json={
        "title": "Tarea de Admin",
        "description": "Prueba admin",
        "status": "pendiente",
        "priority": "alta"
    }, headers=headers_admin)
    assert r_task.status_code == 201
    admin_task_id = r_task.json()["task_id"]

    r_edit = client.put(f"/tasks/{admin_task_id}", json={"status": "completada"}, headers=headers_admin)
    assert r_edit.status_code == 200

def test_06_ciclo_crud_completo_con_endpoint_id():
    token_a = client.post("/auth/login", json={
        "username": "estudiante_a",
        "password": "Password123!"
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token_a}"}

    # Create
    r_create = client.post("/tasks", json={
        "title": "Laboratorio ISW",
        "description": "Implementar SSDLC",
        "status": "en_progreso",
        "priority": "alta"
    }, headers=headers)
    assert r_create.status_code == 201
    task_id = r_create.json()["task_id"]

    # Read individual (GET /tasks/{id})
    r_get = client.get(f"/tasks/{task_id}", headers=headers)
    assert r_get.status_code == 200
    assert r_get.json()["title"] == "Laboratorio ISW"

    # Update (PUT /tasks/{id})
    r_put = client.put(f"/tasks/{task_id}", json={
        "title": "Laboratorio ISW Finalizado",
        "status": "completada"
    }, headers=headers)
    assert r_put.status_code == 200

    # Delete (DELETE /tasks/{id})
    r_del = client.delete(f"/tasks/{task_id}", headers=headers)
    assert r_del.status_code == 200

    r_not_found = client.get(f"/tasks/{task_id}", headers=headers)
    assert r_not_found.status_code == 404

# ========================================================
# PRUEBAS GUÍA 4 - EJERCICIO 1.2: AUTENTICACIÓN RESISTENTE
# ========================================================
def test_07_fuerza_bruta_bloqueo_progresivo():
    """Simula ataque de fuerza bruta; verifica bloqueo temporal 429."""
    username = "estudiante_a"

    # 3 intentos fallidos consecutivos activan bloqueo
    for _ in range(3):
        r = client.post("/auth/login", json={"username": username, "password": "WrongPassword999!"})
        assert r.status_code in [401, 429]

    # El siguiente intento (incluso con credenciales correctas) debe ser bloqueado con 429
    r_blocked = client.post("/auth/login", json={"username": username, "password": "Password123!"})
    assert r_blocked.status_code == 429
    assert "bloqueo" in r_blocked.json()["detail"].lower()

def test_08_restablecimiento_contrasena_un_solo_uso():
    """Solicita token, restablece contraseña y verifica que el token no se pueda reutilizar."""
    username = "estudiante_b"

    # 1. Solicitar restablecimiento
    r_forgot = client.post("/auth/forgot-password", json={"username": username})
    assert r_forgot.status_code == 200
    reset_token = r_forgot.json().get("reset_token")
    assert reset_token is not None

    # 2. Restablecer con nueva contraseña
    new_pass = "NewSecretPassword2026!"
    r_reset = client.post("/auth/reset-password", json={
        "token": reset_token,
        "new_password": new_pass
    })
    assert r_reset.status_code == 200

    # 3. Reutilización de token (debe fallar con 400 Bad Request)
    r_reused = client.post("/auth/reset-password", json={
        "token": reset_token,
        "new_password": "AnotherPassword2026!"
    })
    assert r_reused.status_code == 400
    assert "utilizado" in r_reused.json()["detail"].lower()

    # 4. Iniciar sesión con la nueva contraseña funciona
    r_login = client.post("/auth/login", json={"username": username, "password": new_pass})
    assert r_login.status_code == 200

def test_09_revocacion_sesion_al_cambiar_contrasena():
    """Un token JWT emitido antes de un cambio de contraseña queda revocado (401)."""
    username = "estudiante_b"
    current_pass = "NewSecretPassword2026!"

    # 1. Login y obtención de sesión activa
    token_old = client.post("/auth/login", json={"username": username, "password": current_pass}).json()["access_token"]
    headers_old = {"Authorization": f"Bearer {token_old}"}

    # Verifica que el token antiguo funciona antes del cambio
    r_check = client.get("/tasks", headers=headers_old)
    assert r_check.status_code == 200

    # 2. Se restablece/cambia la contraseña
    r_forgot = client.post("/auth/forgot-password", json={"username": username})
    reset_token = r_forgot.json()["reset_token"]

    r_reset = client.post("/auth/reset-password", json={
        "token": reset_token,
        "new_password": "BrandNewPassword999!"
    })
    assert r_reset.status_code == 200

    # 3. El token antiguo intenta acceder a un recurso protegido -> debe ser 401 (Sesión revocada)
    r_revoked = client.get("/tasks", headers=headers_old)
    assert r_revoked.status_code == 401
    assert "revocada" in r_revoked.json()["detail"].lower()

def test_10_sesion_expirada():
    """Un token JWT con fecha de expiración vencida retorna 401 Unauthorized."""
    # Generar token JWT con exp en el pasado (-10 segundos)
    expired_payload = {
        "sub": "estudiante_a",
        "role": "estudiante",
        "id": 1,
        "token_version": 1,
        "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=10)
    }
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)

    r_exp = client.get("/tasks", headers={"Authorization": f"Bearer {expired_token}"})
    assert r_exp.status_code == 401
    assert "expirado" in r_exp.json()["detail"].lower()
