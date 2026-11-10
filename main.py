import sqlite3
import datetime
from contextlib import asynccontextmanager
from enum import Enum
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, ConfigDict
import bcrypt
import jwt

# ==========================================
# CONFIGURACIÓN Y CONSTANTES CRIPTOGRÁFICAS
# ==========================================
SECRET_KEY = "UNSAAC_ISW_SECURE_TOKEN_SECRET_KEY_CHANGE_IN_PROD"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
DB_FILE = "tasks.db"

# ==========================================
# GESTIÓN Y PERSISTENCIA DE BASE DE DATOS
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL,
        owner_id INTEGER NOT NULL,
        FOREIGN KEY (owner_id) REFERENCES users (id)
    )
    """)
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

# ==========================================
# INSTANCIA FASTAPI Y SEGURIDAD HTTP
# ==========================================
app = FastAPI(
    title="API Segura de Gestión de Tareas - ISW UNSAAC",
    version="1.0.0",
    description="Sistema de tareas con RBAC, mitigación IDOR, Prepared Statements y validación estricta",
    lifespan=lifespan
)
security = HTTPBearer()

# ==========================================
# ENUMS Y MODELOS PYDANTIC (VALIDACIÓN DE ENTRADA)
# ==========================================
class UserRole(str, Enum):
    ESTUDIANTE = "estudiante"
    DOCENTE = "docente"
    ADMINISTRADOR = "administrador"

class TaskStatus(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"

class UserRegisterSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.ESTUDIANTE

class UserLoginSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str
    password: str

class TaskCreateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(..., min_length=3, max_length=120)
    description: Optional[str] = Field(None, max_length=1000)
    status: TaskStatus = TaskStatus.PENDIENTE

class TaskUpdateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: Optional[str] = Field(None, min_length=3, max_length=120)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None

# ==========================================
# UTILIDADES CRIPTOGRÁFICAS Y SESIÓN JWT
# ==========================================
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: sqlite3.Connection = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no válido")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado o inválido")

    cursor = db.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inexistente")
    return dict(user)

# ==========================================
# ENDPOINT: SERVIR EL FRONTEND WEB
# ==========================================
@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse("index.html")

# ==========================================
# ENDPOINTS: AUTENTICACIÓN
# ==========================================
@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegisterSchema, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (user_data.username,))
    if cursor.fetchone():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de usuario ya está registrado")

    pw_hash = hash_password(user_data.password)
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (user_data.username, pw_hash, user_data.role.value)
    )
    db.commit()
    return {"message": "Usuario registrado exitosamente"}

@app.post("/auth/login")
def login(login_data: UserLoginSchema, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id, username, password_hash, role FROM users WHERE username = ?", (login_data.username,))
    user = cursor.fetchone()

    # Mitigación enumeración: mensaje y código de estado idénticos para fallos
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")

    token = create_access_token({"sub": user["username"], "role": user["role"], "id": user["id"]})
    return {"access_token": token, "token_type": "bearer", "role": user["role"]}

# ==========================================
# ENDPOINTS: GESTIÓN DE TAREAS (CRUD, RBAC, ANTI-IDOR)
# ==========================================
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreateSchema,
    current_user: dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, status, owner_id) VALUES (?, ?, ?, ?)",
        (task.title, task.description, task.status.value, current_user["id"])
    )
    db.commit()
    return {"message": "Tarea creada correctamente", "task_id": cursor.lastrowid}

@app.get("/tasks")
def list_tasks(
    current_user: dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    # RBAC: Administrador y Docente auditan todo; Estudiante solo sus registros
    if current_user["role"] in [UserRole.ADMINISTRADOR.value, UserRole.DOCENTE.value]:
        cursor.execute("SELECT id, title, description, status, owner_id FROM tasks")
    else:
        cursor.execute("SELECT id, title, description, status, owner_id FROM tasks WHERE owner_id = ?", (current_user["id"],))

    return [dict(row) for row in cursor.fetchall()]

@app.get("/tasks/search")
def search_tasks(
    q: str = Query(..., min_length=1, max_length=50),
    current_user: dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    search_param = f"%{q}%"

    # Consulta parametrizada segura contra SQLi
    if current_user["role"] in [UserRole.ADMINISTRADOR.value, UserRole.DOCENTE.value]:
        cursor.execute("SELECT id, title, description, status, owner_id FROM tasks WHERE title LIKE ?", (search_param,))
    else:
        cursor.execute(
            "SELECT id, title, description, status, owner_id FROM tasks WHERE title LIKE ? AND owner_id = ?",
            (search_param, current_user["id"])
        )
    return [dict(row) for row in cursor.fetchall()]

@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    task_data: TaskUpdateSchema,
    current_user: dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    cursor.execute("SELECT id, owner_id FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")

    # Anti-IDOR: Rechazo 403 si el recurso no pertenece al usuario autenticado
    if task["owner_id"] != current_user["id"] and current_user["role"] != UserRole.ADMINISTRADOR.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: No posee privilegios sobre este recurso")

    updates = []
    params = []
    if task_data.title is not None:
        updates.append("title = ?")
        params.append(task_data.title)
    if task_data.description is not None:
        updates.append("description = ?")
        params.append(task_data.description)
    if task_data.status is not None:
        updates.append("status = ?")
        params.append(task_data.status.value)

    if not updates:
        return {"message": "Sin cambios"}

    params.append(task_id)
    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, tuple(params))
    db.commit()
    return {"message": "Tarea actualizada correctamente"}

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    cursor.execute("SELECT id, owner_id FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")

    # Anti-IDOR: Validación de propiedad antes de eliminar
    if task["owner_id"] != current_user["id"] and current_user["role"] != UserRole.ADMINISTRADOR.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: No posee privilegios sobre este recurso")

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    return {"message": "Tarea eliminada exitosamente"}