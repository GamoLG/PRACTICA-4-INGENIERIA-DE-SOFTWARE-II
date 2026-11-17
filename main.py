import sqlite3
import datetime
import logging
import os
import re
import time
import secrets
import hashlib
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager
from enum import Enum
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, Request, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, ConfigDict, field_validator
import bcrypt
import jwt

# ==========================================
# CONFIGURACIÓN Y CONSTANTES CRIPTOGRÁFICAS
# ==========================================
SECRET_KEY = os.environ.get("SECRET_KEY", "UNSAAC_ISW_SECURE_TOKEN_SECRET_KEY_CHANGE_IN_PROD")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
RESET_TOKEN_EXPIRE_MINUTES = 15
DB_FILE = "tasks.db"

# ==========================================
# LOGGING DE AUDITORÍA
# ==========================================
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

_file_handler = logging.FileHandler("audit.log", encoding="utf-8")
_file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(logging.Formatter("%(asctime)s [AUDIT] %(levelname)s %(message)s"))

audit_logger.addHandler(_file_handler)
audit_logger.addHandler(_stream_handler)

# ==========================================
# CONTROL DE INTENTOS Y BLOQUEO PROGRESIVO
# (Por IP y por Cuenta de Usuario)
# ==========================================
# Estructuras para seguimiento en memoria:
_failed_attempts_ip: dict = defaultdict(list)
_failed_attempts_user: dict = defaultdict(list)
_lockouts: dict = {}  # { "ip:X" o "user:Y": unlock_timestamp }

# Compatibilidad con tests
_login_attempts: dict = _failed_attempts_ip

def reset_security_state():
    """Limpia bloqueos e historiales de intentos para suite de tests."""
    _failed_attempts_ip.clear()
    _failed_attempts_user.clear()
    _lockouts.clear()

def check_login_rate_and_lockout(ip: str, username: str):
    """
    Verifica si la IP o la cuenta están bajo bloqueo temporal progresivo.
    Regla progresiva:
      - 3 a 4 intentos fallidos: bloqueo de 30 segundos
      - 5 o más intentos fallidos: bloqueo de 180 segundos (3 minutos)
    """
    now = time.time()

    for key, name in [(f"ip:{ip}", f"IP {ip}"), (f"user:{username}", f"la cuenta {username}")]:
        if key in _lockouts:
            unlock_time = _lockouts[key]
            if now < unlock_time:
                remaining = int(unlock_time - now) + 1
                audit_logger.warning(f"BLOCKED_ATTEMPT on {name}. Remaining: {remaining}s")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Demasiados intentos fallidos sobre {name}. Bloqueo temporal por {remaining} segundos."
                )
            else:
                del _lockouts[key]

def register_failed_login(ip: str, username: str):
    """Registra intento fallido y activa bloqueo progresivo si corresponde."""
    now = time.time()
    window = 300  # 5 minutos

    _failed_attempts_ip[ip] = [t for t in _failed_attempts_ip[ip] if t > now - window]
    _failed_attempts_ip[ip].append(now)

    _failed_attempts_user[username] = [t for t in _failed_attempts_user[username] if t > now - window]
    _failed_attempts_user[username].append(now)

    # Bloqueo progresivo por IP
    ip_fails = len(_failed_attempts_ip[ip])
    if ip_fails >= 5:
        _lockouts[f"ip:{ip}"] = now + 180
        audit_logger.warning(f"LOCKOUT ACTIVATED - ip:{ip} duration:180s")
    elif ip_fails >= 3:
        _lockouts[f"ip:{ip}"] = now + 30
        audit_logger.warning(f"LOCKOUT ACTIVATED - ip:{ip} duration:30s")

    # Bloqueo progresivo por Usuario
    user_fails = len(_failed_attempts_user[username])
    if user_fails >= 5:
        _lockouts[f"user:{username}"] = now + 180
        audit_logger.warning(f"LOCKOUT ACTIVATED - user:{username} duration:180s")
    elif user_fails >= 3:
        _lockouts[f"user:{username}"] = now + 30
        audit_logger.warning(f"LOCKOUT ACTIVATED - user:{username} duration:30s")

def clear_failed_login(ip: str, username: str):
    """Limpia intentos fallidos ante autenticación exitosa."""
    _failed_attempts_ip.pop(ip, None)
    _failed_attempts_user.pop(username, None)
    _lockouts.pop(f"ip:{ip}", None)
    _lockouts.pop(f"user:{username}", None)

# ==========================================
# GESTIÓN Y PERSISTENCIA DE BASE DE DATOS
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("PRAGMA journal_mode=WAL")

    # Tabla de usuarios con control de versión de tokens para revocación
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        token_version INTEGER DEFAULT 1
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)")

    # Migración token_version
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN token_version INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass

    # Tabla de tareas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL,
        owner_id INTEGER NOT NULL,
        priority TEXT NOT NULL DEFAULT 'media',
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (owner_id) REFERENCES users (id)
    )
    """)
    for col_def in [
        ("priority",   "TEXT NOT NULL DEFAULT 'media'"),
        ("created_at", "TEXT DEFAULT (datetime('now'))"),
        ("updated_at", "TEXT DEFAULT (datetime('now'))"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col_def[0]} {col_def[1]}")
        except sqlite3.OperationalError:
            pass

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_owner_id ON tasks (owner_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status   ON tasks (status)")

    # Tabla para tokens de restablecimiento de contraseña
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS password_reset_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token_hash TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        used INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reset_token_hash ON password_reset_tokens (token_hash)")

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
    version="2.1.0",
    description="Sistema seguro con RBAC, Anti-IDOR, Prepared Statements, Bloqueo Progresivo y Recuperación Segura",
    lifespan=lifespan
)
security = HTTPBearer()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cabeceras de seguridad HTTP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response: StarletteResponse = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# ==========================================
# ENUMS Y MODELOS PYDANTIC (VALIDACIÓN ESTRICTA)
# ==========================================
class UserRole(str, Enum):
    ESTUDIANTE = "estudiante"
    DOCENTE = "docente"
    ADMINISTRADOR = "administrador"

class TaskStatus(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"

class TaskPriority(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"

def validate_password_strength(v: str) -> str:
    if not re.search(r"[A-Z]", v):
        raise ValueError("La contraseña debe contener al menos una letra mayúscula")
    if not re.search(r"\d", v):
        raise ValueError("La contraseña debe contener al menos un dígito")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-\+\=\[\]\\\/~`';]", v):
        raise ValueError("La contraseña debe contener al menos un carácter especial")
    return v

class UserRegisterSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.ESTUDIANTE

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        return validate_password_strength(v)

class UserLoginSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str
    password: str

class ForgotPasswordSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(..., min_length=3, max_length=50)

class ResetPasswordSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        return validate_password_strength(v)

class TaskCreateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(..., min_length=3, max_length=120)
    description: Optional[str] = Field(None, max_length=1000)
    status: TaskStatus = TaskStatus.PENDIENTE
    priority: Optional[TaskPriority] = TaskPriority.MEDIA

class TaskUpdateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: Optional[str] = Field(None, min_length=3, max_length=120)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None

# ==========================================
# UTILIDADES CRIPTOGRÁFICAS Y SESIÓN JWT
# ==========================================
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def hash_token(token: str) -> str:
    """Hash SHA-256 para almacenamiento seguro de tokens de reseteo."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4()),  # Regeneración criptográfica de sesión
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: sqlite3.Connection = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_version: int = payload.get("token_version")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no válido")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado o inválido")

    cursor = db.cursor()
    cursor.execute("SELECT id, username, role, token_version FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inexistente")

    # Revocación de sesión: verificar que la versión del token coincida con la de la BD
    if token_version is not None and token_version != user["token_version"]:
        audit_logger.warning(f"REVOKED_SESSION_ATTEMPT - username:{username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión revocada debido a cambio de credenciales. Inicie sesión nuevamente."
        )

    return dict(user)

# ==========================================
# ENDPOINT: SERVIR EL FRONTEND WEB
# ==========================================
@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse("index.html")

# ==========================================
# ENDPOINTS: AUTENTICACIÓN RESISTENTE A ATAQUES
# ==========================================
@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegisterSchema, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (user_data.username,))
    if cursor.fetchone():
        audit_logger.warning(f"REGISTER FAIL - username_taken: {user_data.username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de usuario ya está registrado")

    pw_hash = hash_password(user_data.password)
    cursor.execute(
        "INSERT INTO users (username, password_hash, role, token_version) VALUES (?, ?, ?, 1)",
        (user_data.username, pw_hash, user_data.role.value)
    )
    db.commit()
    audit_logger.info(f"REGISTER OK - username: {user_data.username} role: {user_data.role.value}")
    return {"message": "Usuario registrado exitosamente"}

@app.post("/auth/login")
def login(request: Request, login_data: UserLoginSchema, db: sqlite3.Connection = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"

    # Verificación de bloqueo progresivo previo
    check_login_rate_and_lockout(client_ip, login_data.username)

    cursor = db.cursor()
    cursor.execute(
        "SELECT id, username, password_hash, role, token_version FROM users WHERE username = ?",
        (login_data.username,)
    )
    user = cursor.fetchone()

    # Mitigación enumeración: mensaje y código de estado idénticos para fallos
    if not user or not verify_password(login_data.password, user["password_hash"]):
        register_failed_login(client_ip, login_data.username)
        audit_logger.warning(f"LOGIN FAIL - username: {login_data.username} ip: {client_ip}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")

    # Éxito: limpia intentos fallidos
    clear_failed_login(client_ip, login_data.username)

    # Regeneración de sesión con identificador jti único y control de versión
    token = create_access_token({
        "sub": user["username"],
        "role": user["role"],
        "id": user["id"],
        "token_version": user["token_version"]
    })
    audit_logger.info(f"LOGIN OK - username: {user['username']} ip: {client_ip}")
    return {"access_token": token, "token_type": "bearer", "role": user["role"]}

@app.post("/auth/logout")
def logout(current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    """Invalida inmediatamente el token activo en el servidor incrementando su token_version."""
    cursor = db.cursor()
    cursor.execute("UPDATE users SET token_version = token_version + 1 WHERE id = ?", (current_user["id"],))
    db.commit()
    audit_logger.info(f"LOGOUT - username: {current_user['username']} (sessions revoked)")
    return {"message": "Sesión cerrada y revocada exitosamente"}

# ==========================================
# ENDPOINTS: RESTABLECIMIENTO DE CONTRASEÑA SEGURO
# ==========================================
@app.post("/auth/forgot-password")
def forgot_password(
    request: Request,
    forgot_data: ForgotPasswordSchema,
    db: sqlite3.Connection = Depends(get_db)
):
    client_ip = request.client.host if request.client else "unknown"
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (forgot_data.username,))
    user = cursor.fetchone()

    # Registro de auditoría sin exponer el token
    audit_logger.info(f"PASSWORD_RESET_REQUEST - username: {forgot_data.username} ip: {client_ip}")

    # Si el usuario no existe, se retorna respuesta genérica para evitar enumeración
    if not user:
        return {"message": "Si la cuenta existe, se ha procesado la solicitud de restablecimiento."}

    user_id = user["id"]

    # Invalidación estricta de tokens anteriores
    cursor.execute("UPDATE password_reset_tokens SET used = 1 WHERE user_id = ? AND used = 0", (user_id,))

    # Token aleatorio criptoseguro de un solo uso
    raw_token = secrets.token_urlsafe(32)
    tok_hash = hash_token(raw_token)

    # Expiración corta (15 minutos)
    expires_at = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)).isoformat()

    cursor.execute(
        "INSERT INTO password_reset_tokens (user_id, token_hash, expires_at, used) VALUES (?, ?, ?, 0)",
        (user_id, tok_hash, expires_at)
    )
    db.commit()

    # Retorna mensaje genérico y entrega el token para fines de demostración académica / testing
    return {
        "message": "Si la cuenta existe, se ha procesado la solicitud de restablecimiento.",
        "reset_token": raw_token
    }

@app.post("/auth/reset-password")
def reset_password(
    request: Request,
    reset_data: ResetPasswordSchema,
    db: sqlite3.Connection = Depends(get_db)
):
    client_ip = request.client.host if request.client else "unknown"
    tok_hash = hash_token(reset_data.token)

    cursor = db.cursor()
    cursor.execute(
        "SELECT id, user_id, expires_at, used FROM password_reset_tokens WHERE token_hash = ?",
        (tok_hash,)
    )
    token_record = cursor.fetchone()

    if not token_record or token_record["used"] == 1:
        audit_logger.warning(f"PASSWORD_RESET_FAIL - token inválido o reusado ip: {client_ip}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido o ya utilizado")

    # Verificación de expiración
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    expires_at = datetime.datetime.fromisoformat(token_record["expires_at"])
    if now_utc > expires_at:
        audit_logger.warning(f"PASSWORD_RESET_FAIL - token expirado ip: {client_ip}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token de restablecimiento ha expirado")

    user_id = token_record["user_id"]
    new_pw_hash = hash_password(reset_data.new_password)

    # 1. Actualizar contraseña
    # 2. Incrementar token_version (Revocación inmediata de todas las sesiones previas)
    cursor.execute(
        "UPDATE users SET password_hash = ?, token_version = token_version + 1 WHERE id = ?",
        (new_pw_hash, user_id)
    )

    # 3. Marcar token como consumido (un solo uso)
    cursor.execute("UPDATE password_reset_tokens SET used = 1 WHERE id = ?", (token_record["id"],))
    db.commit()

    audit_logger.info(f"PASSWORD_RESET_SUCCESS - user_id: {user_id} ip: {client_ip} (sessions revoked)")
    return {"message": "Contraseña restablecida exitosamente. Todas las sesiones activas han sido revocadas."}

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
    priority_val = task.priority.value if task.priority else TaskPriority.MEDIA.value
    cursor.execute(
        "INSERT INTO tasks (title, description, status, owner_id, priority, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
        (task.title, task.description, task.status.value, current_user["id"], priority_val)
    )
    db.commit()
    task_id = cursor.lastrowid
    audit_logger.info(f"CREATE TASK id:{task_id} title:'{task.title}' owner:{current_user['username']}")
    return {"message": "Tarea creada correctamente", "task_id": task_id}

@app.get("/tasks")
def list_tasks(
    current_user: dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    if current_user["role"] in [UserRole.ADMINISTRADOR.value, UserRole.DOCENTE.value]:
        cursor.execute(
            "SELECT id, title, description, status, owner_id, priority, created_at, updated_at FROM tasks"
        )
    else:
        cursor.execute(
            "SELECT id, title, description, status, owner_id, priority, created_at, updated_at FROM tasks WHERE owner_id = ?",
            (current_user["id"],)
        )
    return [dict(row) for row in cursor.fetchall()]

@app.get("/tasks/search")
def search_tasks(
    q: str = Query(..., min_length=1, max_length=50),
    current_user: dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    search_param = f"%{q}%"

    if current_user["role"] in [UserRole.ADMINISTRADOR.value, UserRole.DOCENTE.value]:
        cursor.execute(
            "SELECT id, title, description, status, owner_id, priority, created_at, updated_at FROM tasks WHERE title LIKE ?",
            (search_param,)
        )
    else:
        cursor.execute(
            "SELECT id, title, description, status, owner_id, priority, created_at, updated_at FROM tasks WHERE title LIKE ? AND owner_id = ?",
            (search_param, current_user["id"])
        )
    return [dict(row) for row in cursor.fetchall()]

@app.get("/tasks/{task_id}")
def get_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, title, description, status, owner_id, priority, created_at, updated_at FROM tasks WHERE id = ?",
        (task_id,)
    )
    task = cursor.fetchone()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")

    if current_user["role"] not in [UserRole.ADMINISTRADOR.value, UserRole.DOCENTE.value]:
        if task["owner_id"] != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: No posee privilegios sobre este recurso")

    return dict(task)

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
    if task_data.priority is not None:
        updates.append("priority = ?")
        params.append(task_data.priority.value)

    if not updates:
        return {"message": "Sin cambios"}

    updates.append("updated_at = datetime('now')")
    params.append(task_id)
    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, tuple(params))
    db.commit()
    audit_logger.info(f"UPDATE TASK id:{task_id} by:{current_user['username']}")
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

    if task["owner_id"] != current_user["id"] and current_user["role"] != UserRole.ADMINISTRADOR.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: No posee privilegios sobre este recurso")

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    audit_logger.info(f"DELETE TASK id:{task_id} by:{current_user['username']}")
    return {"message": "Tarea eliminada exitosamente"}
