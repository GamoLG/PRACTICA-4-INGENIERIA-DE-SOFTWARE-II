# API Segura de Gestión de Tareas - ISW UNSAAC

## 1. Descripción Técnica y Arquitectura
Implementación de una API RESTful desarrollada con **FastAPI** y **SQLite** bajo el enfoque **SSDLC** (Security Software Development Life Cycle), mitigando vulnerabilidades críticas del **OWASP Top 10** (A01: Broken Access Control, A03: Injection, A04: Insecure Design, A05: Security Misconfiguration, A07: Identification and Authentication Failures, A09: Security Logging and Monitoring Failures) y los escenarios auditados en la práctica de laboratorio.

### Controles de Seguridad Implementados:
- **Autenticación Robusta:** Hash `bcrypt` con costo adaptativo (`salt rounds = 12`). Tokens JWT con expiración estricta y algoritmo HMAC-SHA256. Validación de complejidad de contraseñas (mínimo 8 caracteres, mayúscula, dígito y símbolo especial).
- **Rate Limiting:** Límite de 5 intentos por minuto por dirección IP en `/auth/login` (mitigación de ataques de fuerza bruta, retorna `HTTP 429 Too Many Requests`).
- **Prevención IDOR:** Verificación estricta de propiedad del recurso en servidor en operaciones de lectura individual, edición y eliminación (`owner_id == session.user_id`), respondiendo `HTTP 403 Forbidden` ante accesos no autorizados.
- **Prevención SQLi:** *Prepared Statements* (consultas parametrizadas con placeholders `?` y tuplas de argumentos) en todas las operaciones, incluyendo el endpoint de búsqueda con comodines (`LIKE ?`).
- **Validación Estricta:** DTOs con Pydantic V2 enforcing `extra="forbid"` (mitigación de *Mass Assignment*) y listas blancas (*whitelists*) para estados (`pendiente`, `en_progreso`, `completada`) y prioridades (`baja`, `media`, `alta`).
- **Control de Acceso Basado en Roles (RBAC):**
  - **Estudiante:** Acceso exclusivo a sus propias tareas (crear, listar, leer, editar, eliminar).
  - **Docente:** Auditoría global (puede listar y buscar tareas de todos los estudiantes, pero solo editar las suyas).
  - **Administrador:** Privilegios globales de lectura, edición y eliminación sobre cualquier tarea.
- **Cabeceras de Seguridad HTTP (Middleware):** Inyección automática de `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block` y `Referrer-Policy: strict-origin-when-cross-origin`.
- **Registro y Auditoría:** Logging persistente en `audit.log` y consola para eventos de autenticación (éxitos/fallos con IP) y modificaciones de tareas (creación, edición, eliminación).
- **Protección XSS en Frontend:** Función contextual `escapeHTML()` en JavaScript, diálogos nativos y manejo seguro de errores con desempaquetado de detalles Pydantic.

---

## 2. Paquetes y Dependencias

| Paquete | Versión Recomendada | Función en el Proyecto |
| :--- | :--- | :--- |
| **`fastapi`** | `>=0.110.0` | Framework web reactivo de alto rendimiento. |
| **`uvicorn[standard]`** | `>=0.28.0` | Servidor ASGI para desplegar FastAPI en local. |
| **`pydantic`** | `>=2.6.0` | Validación estricta de esquemas, tipos y payloads. |
| **`bcrypt`** | `>=4.1.2` | Hashing lento y seguro de contraseñas con salt. |
| **`pyjwt`** | `>=2.8.0` | Creación y decodificación criptográfica de tokens JWT. |
| **`pytest`** | `>=8.0.0` | Framework para pruebas automatizadas unitarias y de integración. |
| **`httpx`** | `>=0.27.0` | Cliente HTTP utilizado internamente por `TestClient` para simular peticiones. |

### Instalación:
```bash
pip install -r requirements.txt
```

---

## 3. Matriz de Modelado STRIDE y Riesgos ($P \times I$)

| Hallazgo Auditado | Categoría STRIDE | Actor de Amenaza | Probabilidad ($P$) | Impacto ($I$) | Nivel de Riesgo ($P \times I$) | Control Técnico / Mitigación Implementada |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Hallazgo A:** Alteración de ID (`/tasks/104` a `105`) expone/modifica datos ajenos. | **Elevation of Privilege** / **Information Disclosure** (IDOR) | Usuario autenticado estándar | 4 | 4 | **16 (Alto)** | Control de acceso a nivel de objeto en backend (`owner_id == session.user_id`). Responde estrictamente `HTTP 403 Forbidden`. |
| **Hallazgo B:** Parámetros de búsqueda concatenados directamente en consultas SQL. | **Tampering** / **Information Disclosure** (SQLi) | Atacante externo / usuario malicioso | 4 | 5 | **20 (Crítico)** | Consultas Parametrizadas (*Prepared Statements* con marcadores de posición `?` y tuplas de argumentos). |
| **Hallazgo C:** Renderización directa de cadenas sin escapar en salida web. | **Tampering** (XSS) | Usuario con permisos de creación de contenido | 3 | 3 | **9 (Medio)** | Tipado estricto mediante DTOs Pydantic, serialización JSON automática y sanitización `escapeHTML()` en frontend. |
| **Fuerza Bruta:** Intentos repetidos de autenticación sobre `/auth/login`. | **Denial of Service** / **Elevation of Privilege** | Atacante con diccionario de credenciales | 4 | 4 | **16 (Alto)** | Rate Limiter en memoria (máximo 5 intentos por minuto por IP -> `HTTP 429 Too Many Requests`). |

---

## 4. Requisitos de Seguridad Verificables

1. **RS-01 [Almacenamiento de Credenciales]:** Contraseñas hasheadas exclusivamente con `bcrypt` (12 rondas de salt) y política de complejidad exigida en DTO.
2. **RS-02 [Anti-Enumeración & Rate Limiting]:** Login responde `401 Unauthorized` genérico ante credenciales incorrectas y `429 Too Many Requests` ante exceso de intentos.
3. **RS-03 [Anti-IDOR]:** Un estudiante solo puede ver, editar o eliminar sus propias tareas. Accesos a tareas ajenas retornan `HTTP 403 Forbidden`.
4. **RS-04 [Anti-SQLi]:** Filtros de búsqueda utilizan `WHERE title LIKE ?` pasando `(f"%{q}%",)` como tupla binaria, neutralizando payloads como `' OR 1=1 --`.
5. **RS-05 [Anti-Mass Assignment]:** DTOs Pydantic con `model_config = ConfigDict(extra="forbid")`. La inyección de campos extras arroja `HTTP 422 Unprocessable Entity`.
6. **RS-06 [Auditoría]:** Cada acción crítica genera trazas fechadas en `audit.log`.

---

## 5. Estructura del Repositorio

```text
gestion_tarea_api/
├── .gitignore           # Exclusión de base de datos, logs, caché y entornos
├── main.py              # API RESTful en FastAPI (Auth, RBAC, CRUD, Búsqueda, Middleware)
├── index.html           # SPA moderna interactiva (Tailwind CSS, Modal, Cards, Toasts)
├── test_security.py     # Suite de 6 pruebas automatizadas con pytest
├── requirements.txt     # Dependencias del proyecto
├── tasks.db             # Base de datos SQLite (generada dinámicamente con índices y WAL)
├── audit.log            # Registro de auditoría de seguridad
└── README.md            # Memoria técnica completa
```

---

## 6. Instrucciones de Ejecución

### Paso 1: Iniciar el Servidor de la API
```bash
python -m uvicorn main:app --reload --port 8000
```
- **Aplicación Web:** `http://127.0.0.1:8000/`
- **Documentación Swagger UI:** `http://127.0.0.1:8000/docs`
- **Documentación Redoc:** `http://127.0.0.1:8000/redoc`

### Paso 2: Ejecutar las Pruebas Automatizadas
En una terminal:
```bash
python -m pytest test_security.py -v
```
**Resultado esperado (6 tests en verde):**
```text
test_security.py::test_01_registro_y_login_seguro PASSED                         [ 16%]
test_security.py::test_02_validacion_servidor_y_anti_mass_assignment PASSED     [ 33%]
test_security.py::test_03_control_acceso_anti_idor PASSED                       [ 50%]
test_security.py::test_04_prevencion_inyeccion_sql PASSED                        [ 66%]
test_security.py::test_05_rbac_docente_y_administrador PASSED                    [ 83%]
test_security.py::test_06_ciclo_crud_completo_con_endpoint_id PASSED             [100%]
================================== 6 passed in 3.29s ===================================
```

---

## 7. Catálogo Completo de Endpoints

### Autenticación
| Método | Endpoint | Descripción | Acceso |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Registro de usuario (bcrypt + validación de complejidad) | Público |
| `POST` | `/auth/login` | Inicio de sesión, retorna JWT Bearer (con Rate Limiting) | Público |

### Gestión de Tareas
| Método | Endpoint | Descripción | Acceso |
| :--- | :--- | :--- | :--- |
| `POST` | `/tasks` | Crear nueva tarea vinculada al usuario activo | Requiere JWT |
| `GET` | `/tasks` | Listar tareas (Estudiante: solo suyas; Docente/Admin: todas) | Requiere JWT (RBAC) |
| `GET` | `/tasks/{id}` | Obtener detalle de una tarea por su ID con Anti-IDOR | Dueño, Docente o Admin |
| `GET` | `/tasks/search?q={query}` | Búsqueda segura por título usando sentencias parametrizadas | Requiere JWT |
| `PUT` | `/tasks/{id}` | Actualizar título, descripción, estado o prioridad | Dueño o Admin |
| `DELETE` | `/tasks/{id}` | Eliminar tarea con validación de propiedad (Anti-IDOR) | Dueño o Admin |
| `GET` | `/` | Servir frontend web SPA interactivo | Público |
