import os
import pytest
from fastapi.testclient import TestClient
from main import app, DB_FILE, init_db, _login_attempts

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    init_db()  # <-- Crea las tablas users y tasks de inmediato
    yield
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Limpia el rate limiter entre tests para evitar bloqueos por IP de TestClient."""
    _login_attempts.clear()
    yield
    _login_attempts.clear()
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
    # Obtener token
    token = client.post("/auth/login", json={
        "username": "estudiante_a",
        "password": "Password123!"
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Intento de inyectar campo extra prohibido (Mass Assignment)
    r_extra = client.post("/tasks", json={
        "title": "Tarea 1",
        "status": "pendiente",
        "role": "administrador"  # Campo extra prohibido
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
    # No debe retornar registros si no coinciden literalmente con el string
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

    # Docente puede auditar y listar todas las tareas
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

    # Admin crea tarea y puede editarla
    r_task = client.post("/tasks", json={
        "title": "Tarea de Admin",
        "description": "Prueba admin",
        "status": "pendiente",
        "priority": "alta"
    }, headers=headers_admin)
    assert r_task.status_code == 201
    admin_task_id = r_task.json()["task_id"]

    # Admin puede editar cualquier tarea
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
    assert r_get.json()["priority"] == "alta"

    # Update (PUT /tasks/{id})
    r_put = client.put(f"/tasks/{task_id}", json={
        "title": "Laboratorio ISW Finalizado",
        "status": "completada"
    }, headers=headers)
    assert r_put.status_code == 200

    # Delete (DELETE /tasks/{id})
    r_del = client.delete(f"/tasks/{task_id}", headers=headers)
    assert r_del.status_code == 200

    # Read after delete should return 404
    r_not_found = client.get(f"/tasks/{task_id}", headers=headers)
    assert r_not_found.status_code == 404