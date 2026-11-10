import os
import pytest
from fastapi.testclient import TestClient
from main import app, DB_FILE, init_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    init_db()  # <-- Crea las tablas users y tasks de inmediato
    yield
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
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