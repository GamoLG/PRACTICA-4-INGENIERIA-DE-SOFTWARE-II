# API Segura de Gestión de Tareas - ISW UNSAAC
## Guía 4: Ingeniería de Software Seguro — Ejercicio Propuesto 1.2
### Implementación de Autenticación Resistente a Ataques Comunes

---

## 1. Diagramas de Flujo de Autenticación y Seguridad

### A. Flujo de Autenticación con Bloqueo Progresivo y Regeneración de Sesión

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario / Atacante
    participant W as WAF / Rate Limiter
    participant API as FastAPI Backend
    participant DB as SQLite DB
    participant Log as audit.log

    U->>W: POST /auth/login {username, password}
    W->>W: Verificar bloqueo activo (IP y Usuario)
    alt Bloqueo temporal activo (3 fallos=30s, 5 fallos=180s)
        W-->>U: HTTP 429 Too Many Requests (Tiempo restante)
        W->>Log: Registro de intento en bloqueo
    else Sin bloqueo activo
        W->>API: Procesar credenciales
        API->>DB: Consultar usuario y password_hash (bcrypt)
        alt Credenciales inválidas o usuario no existe
            API->>W: Registrar intento fallido
            API->>Log: LOGIN FAIL {username, IP}
            API-->>U: HTTP 401 Unauthorized ("Credenciales incorrectas")
        else Credenciales válidas
            API->>W: Limpiar historial de fallos
            API->>API: Generar JWT con nuevo JTI (UUID) y token_version
            API->>Log: LOGIN OK {username, IP}
            API-->>U: HTTP 200 OK {access_token, role}
        end
    end
```

### B. Flujo de Restablecimiento de Contraseña y Revocación de Sesión

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario
    participant API as FastAPI Backend
    participant DB as SQLite DB
    participant Log as audit.log

    Note over U,API: 1. Solicitud de Restablecimiento
    U->>API: POST /auth/forgot-password {username}
    API->>DB: Invalidar tokens anteriores (used = 1)
    API->>API: Generar token seguro (secrets.token_urlsafe)
    API->>API: Calcular SHA-256(token)
    API->>DB: Guardar token_hash con expiración corta (15 min)
    API->>Log: PASSWORD_RESET_REQUEST {username, IP} (sin exponer token)
    API-->>U: HTTP 200 OK ("Si la cuenta existe...", reset_token)

    Note over U,API: 2. Cambio de Contraseña y Revocación
    U->>API: POST /auth/reset-password {token, new_password}
    API->>API: Validar complejidad de contraseña (regex)
    API->>DB: Buscar token_hash no usado (used = 0) y no expirado
    alt Token inválido o ya utilizado
        API-->>U: HTTP 400 Bad Request ("Token inválido o ya utilizado")
    else Token válido
        API->>API: Hashear nueva contraseña con bcrypt (12 rondas)
        API->>DB: UPDATE users SET password_hash, token_version = token_version + 1
        API->>DB: UPDATE password_reset_tokens SET used = 1
        API->>Log: PASSWORD_RESET_SUCCESS {user_id, IP} (Sesiones revocadas)
        API-->>U: HTTP 200 OK ("Contraseña restablecida. Sesiones revocadas.")
    end

    Note over U,API: 3. Intento de uso de token JWT anterior
    U->>API: GET /tasks con JWT emitido previo al cambio
    API->>DB: Verificar token_version del JWT vs BD
    API-->>U: HTTP 401 Unauthorized ("Sesión revocada debido a cambio de credenciales")
```

---

## 2. Controles de Seguridad Implementados (Guía 4 - Ejercicio 1.2)

1. **Hash Criptográfico Lento:** `bcrypt` con costo adaptativo de 12 rondas de salt para almacenamiento de contraseñas.
2. **Límite de Intentos y Bloqueo Temporal Progresivo:**
   - Seguimiento independiente por **dirección IP** y por **nombre de usuario**.
   - 3 a 4 intentos fallidos: **30 segundos** de bloqueo (`HTTP 429`).
   - 5 o más intentos fallidos: **180 segundos (3 minutos)** de bloqueo (`HTTP 429`).
3. **Mensajes Genéricos Anti-Enumeración:** Respuestas homogéneas (`401 Unauthorized: "Credenciales incorrectas"`) tanto para usuarios inexistentes como contraseñas erróneas.
4. **Regeneración de Sesión:** Cada login exitoso genera un identificador de sesión único criptográfico (`jti = UUIDv4`).
5. **Revocación de Sesión al Cambiar Contraseña:** Campo `token_version` por usuario. Al cambiar credenciales o hacer logout se incrementa el contador, invalidando de inmediato todos los JWT antiguos.
6. **Restablecimiento de Contraseña Resistente:**
   - Token aleatorio criptoseguro generado con `secrets.token_urlsafe(32)`.
   - Almacenamiento protegido: en la base de datos se guarda únicamente el hash `SHA-256` del token.
   - Expiración corta de 15 minutos.
   - Invalidación automática de tokens previos.
   - Token de un solo uso (`used = 1`).
   - Registro en `audit.log` sin exponer el contenido del token.
7. **Control de Acceso Basado en Roles (RBAC):**
   - **Estudiante:** Acceso exclusivo a sus tareas propias.
   - **Docente:** Auditoría y visualización de todas las tareas.
   - **Administrador:** Lectura, edición y eliminación de cualquier tarea.
8. **Protección Anti-IDOR y Anti-SQLi:**
   - Verificación de propiedad en servidor (`owner_id == session.user_id`).
   - Consultas con sentencias parametrizadas (*Prepared Statements* con marcadores `?`).
9. **Cabeceras HTTP de Seguridad:** Inyección de `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`.

---

## 3. Catálogo Completo de Endpoints

### Autenticación y Gestión de Sesión
| Método | Endpoint | Descripción | Control de Seguridad |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Registro de usuario | Hash bcrypt (12 rondas) + complejidad estricta |
| `POST` | `/auth/login` | Inicio de sesión (JWT) | Bloqueo progresivo por IP y cuenta + JTI único |
| `POST` | `/auth/logout` | Cierre de sesión seguro | Revocación en servidor (`token_version + 1`) |
| `POST` | `/auth/forgot-password` | Solicitud de restablecimiento | Token de un solo uso, expiración 15 min, anti-enumeración |
| `POST` | `/auth/reset-password` | Confirmar nueva contraseña | Invalida token, actualiza hash y revoca sesiones previas |

### Gestión de Tareas
| Método | Endpoint | Descripción | Acceso |
| :--- | :--- | :--- | :--- |
| `POST` | `/tasks` | Crear tarea | Requiere JWT |
| `GET` | `/tasks` | Listar tareas con filtros | RBAC (Estudiante: propias / Docente y Admin: todas) |
| `GET` | `/tasks/{id}` | Ver detalle de una tarea | Anti-IDOR (Dueño, Docente o Admin) |
| `GET` | `/tasks/search?q=` | Búsqueda por título | Prepared Statements contra SQLi |
| `PUT` | `/tasks/{id}` | Actualizar tarea | Anti-IDOR (Solo Dueño o Admin) |
| `DELETE` | `/tasks/{id}` | Eliminar tarea | Anti-IDOR (Solo Dueño o Admin) |
| `GET` | `/` | Servir frontend web SPA interactivo | Público |

---

## 4. Actividad 3 — App Vulnerable (SAST)

Archivo `app_vulnerable.py`: aplicación Flask con vulnerabilidades intencionales para análisis estático (Pylint / Bandit):

| Vulnerabilidad | CWE | Severidad | Descripción |
| :--- | :--- | :--- | :--- |
| SQL Injection | CWE-89 | Crítica | Concatenación directa de entrada del usuario en consulta SQL |
| IDOR | CWE-639 | Crítica | No se verifica que el usuario sea propietario del recurso |
| XSS Reflejado | CWE-79 | Alta | `render_template_string` sin sanitización permite ejecutar JavaScript |
| SQL Injection (LIKE) | CWE-89 | Crítica | Concatenación directa del parámetro de búsqueda |

---

## 5. Actividad 4 — App Segura (Refactorización)

Archivo `app_segura.py`: versión corregida con los siguientes controles:

- **SQL Injection →** Consultas parametrizadas con marcadores `?`
- **IDOR →** Validación de ownership en servidor, retorna HTTP 403 Forbidden
- **XSS →** `markupsafe.escape()` para codificación de salida
- **Contraseñas →** Hash con `bcrypt` (12 rondas) en lugar de texto plano
- **Validación →** Longitud, tipo y valores permitidos en todas las entradas

**Resultado Bandit:** 0 vulnerabilidades detectadas.

---

## 6. Suite de Pruebas de Seguridad Automatizadas

Suite de **19 pruebas automatizadas** desarrolladas con `pytest` y `TestClient`:

```bash
python -m pytest test_security.py -v
```

| Prueba | Objetivo Verificado |
| :--- | :--- |
| `test_01_registro_y_login_seguro` | Registro con hash bcrypt, login válido y mitigación de enumeración |
| `test_02_validacion_servidor_y_anti_mass_assignment` | Rechazo 422 ante campos no permitidos o estados inválidos |
| `test_03_control_acceso_anti_idor` | Rechazo 403 Forbidden al editar o eliminar tarea ajena |
| `test_04_prevencion_inyeccion_sql` | Neutralización de payloads SQLi en búsquedas |
| `test_05_rbac_docente_y_administrador` | Privilegios de auditoría (docente) y edición global (admin) |
| `test_06_ciclo_crud_completo_con_endpoint_id` | Ciclo completo crear, leer, editar, eliminar y 404 |
| `test_07_fuerza_bruta_bloqueo_progresivo` | Activación de bloqueo temporal HTTP 429 |
| `test_08_restablecimiento_contrasena_un_solo_uso` | Token de reset no puede reutilizarse (400) |
| `test_09_revocacion_sesion_al_cambiar_contrasena` | Tokens JWT previos revocados (401) tras cambio de clave |
| `test_10_sesion_expirada` | Rechazo 401 ante tokens JWT vencidos |
| `test_11_campo_vacio_titulo` | Título vacío retorna 422 |
| `test_12_campo_demasiado_largo` | Título > 120 caracteres retorna 422 |
| `test_13_estado_invalido` | Estado no permitido retorna 422 |
| `test_14_campo_extra_inyectado` | Campo extra (extra=forbid) retorna 422 |
| `test_15_caracteres_especiales_y_unicode` | Payloads XSS/SQLi aceptados como texto, emojis y ñ |
| `test_16_sin_token_autenticacion` | Sin token retorna 401/403 en todos los endpoints protegidos |
| `test_17_busqueda_sqli_parametrizada` | Payloads SQLi en búsqueda no alteran la consulta |
| `test_18_busqueda_cadena_larga` | Búsqueda > 50 caracteres retorna 422 |
| `test_19_valores_nulos_en_body` | Valores null en campos requeridos retorna 422 |

**Resultado:** 19 passed ✅

---

## 7. Instrucciones de Ejecución

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Iniciar servidor local
python -m uvicorn main:app --reload --port 8000

# 3. Correr las 19 pruebas automatizadas
python -m pytest test_security.py -v

# 4. Análisis SAST de la app vulnerable
pip install pylint bandit
pylint app_vulnerable.py
bandit app_vulnerable.py
bandit app_segura.py
```

* **Frontend Web:** `http://127.0.0.1:8000`
* **Swagger UI Docs:** `http://127.0.0.1:8000/docs`
* **Demo en Render:** `https://practica-4-ingenieria-de-software-ii.onrender.com`
