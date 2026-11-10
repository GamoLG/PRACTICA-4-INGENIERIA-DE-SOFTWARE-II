# API Segura de Gestión de Tareas - ISW UNSAAC

## 1. Descripción Técnica y Arquitectura
Implementación de una API RESTful desarrollada con **FastAPI** y **SQLite** bajo el enfoque **SSDLC** (Security Software Development Life Cycle), mitigando vulnerabilidades críticas del **OWASP Top 10** (A01: Broken Access Control, A03: Injection, A07: Identification and Authentication Failures) y los escenarios auditados en la práctica de laboratorio.

### Controles de Seguridad Implementados:
- **Autenticación:** Hash `bcrypt` con costo adaptativo (`salt rounds = 12`). Tokens JWT con expiración estricta y algoritmo HMAC-SHA256. Mensajes y tiempos de respuesta idénticos para mitigar enumeración de cuentas.
- **Prevención IDOR:** Verificación de propiedad del recurso en servidor antes de procesar lecturas/actualizaciones (`owner_id == session.user_id`), retornando `HTTP 403 Forbidden` ante accesos no autorizados.
- **Prevención SQLi:** *Prepared Statements* (consultas parametrizadas con placeholders `?` y tuplas de argumentos) en todas las operaciones, incluyendo el endpoint de búsqueda con comodines (`LIKE ?`).
- **Validación Estricta:** DTOs con Pydantic V2 enforcing `extra="forbid"` (mitigación de *Mass Assignment*) y listas blancas (*whitelists*) para estados permitidos (`pendiente`, `en_progreso`, `completada`).
- **Control de Acceso Basado en Roles (RBAC):** Jerarquía de privilegios entre `estudiante`, `docente` y `administrador`.

---

## 2. Paquetes y Dependencias a Instalar

Para ejecutar la API, correr las pruebas automatizadas y realizar el análisis SAST, se requieren las siguientes librerías de Python:

| Paquete | Versión Recomendada | Función en el Proyecto |
| :--- | :--- | :--- |
| **`fastapi`** | `>=0.110.0` | Framework web reactivo de alto rendimiento. |
| **`uvicorn[standard]`** | `>=0.28.0` | Servidor ASGI para desplegar FastAPI en local. |
| **`pydantic`** | `>=2.6.0` | Validación estricta de esquemas, tipos y payloads. |
| **`bcrypt`** | `>=4.1.2` | Hashing lento y seguro de contraseñas con salt. |
| **`pyjwt`** | `>=2.8.0` | Creación y decodificación criptográfica de tokens JWT. |
| **`pytest`** | `>=8.0.0` | Framework para pruebas automatizadas unitarias y de integración. |
| **`httpx`** | `>=0.27.0` | Cliente HTTP utilizado internamente por `TestClient` para simular peticiones. |
| **`pylint`** | `>=3.0.0` | Herramienta SAST para análisis estático de código fuente. |

### Comando de Instalación Rápida (Un solo paso):

```bash
pip install fastapi "uvicorn[standard]" pydantic bcrypt pyjwt pytest httpx pylint
```

O utilizando el archivo `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## 3. Matriz de Modelado STRIDE y Riesgos ($P \times I$)

Evaluación de los hallazgos según el caso de estudio base y mapeo a la taxonomía STRIDE con cálculo de nivel de riesgo ($R = P \times I$):

| Hallazgo Auditado | Categoría STRIDE | Actor de Amenaza | Probabilidad ($P$) | Impacto ($I$) | Nivel de Riesgo ($P \times I$) | Control Técnico / Mitigación Implementada |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Hallazgo A:** Alteración de ID (`/reservas?id=104` a `105`) expone datos ajenos. | **Elevation of Privilege** / **Information Disclosure** (IDOR) | Usuario autenticado estándar | 4 | 4 | **16 (Alto)** | Control de acceso a nivel de objeto en backend (`owner_id == session.user_id`). Ante accesos ajenos, el servidor responde estrictamente `HTTP 403 Forbidden`. |
| **Hallazgo B:** Parámetros de búsqueda concatenados directamente en consultas SQL. | **Tampering** / **Information Disclosure** (SQLi) | Atacante externo / usuario malicioso | 4 | 5 | **20 (Crítico)** | Consultas Parametrizadas (*Prepared Statements* con marcadores de posición `?` y tuplas de argumentos). |
| **Hallazgo C:** Renderización directa de cadenas sin escapar en salida web. | **Tampering** (XSS) | Usuario con permisos de creación de contenido | 3 | 3 | **9 (Medio)** | Tipado estricto mediante DTOs Pydantic, serialización JSON automática que neutraliza HTML y sanitización contextual de cadenas. |

---

## 4. Requisitos de Seguridad Verificables

1. **RS-01 [Almacenamiento de Credenciales]:** Contraseñas hasheadas exclusivamente con `bcrypt` (12 rondas de salt).
2. **RS-02 [Anti-Enumeración]:** Login responde `401 Unauthorized` con mensaje genérico `"Credenciales incorrectas"` tanto para usuario inexistente como clave inválida.
3. **RS-03 [Anti-IDOR]:** Un estudiante solo puede editar o eliminar sus propias tareas. Accesos no autorizados retornan `HTTP 403 Forbidden`.
4. **RS-04 [Anti-SQLi]:** Filtros de búsqueda utilizan `WHERE title LIKE ?` pasando `(f"%{q}%",)` como tupla binaria, neutralizando payloads como `' OR 1=1 --`.
5. **RS-05 [Anti-Mass Assignment]:** DTOs Pydantic con `model_config = ConfigDict(extra="forbid")`. La inyección de campos como `"role": "admin"` arroja `HTTP 422 Unprocessable Entity`.

---

## 5. Estructura del Repositorio

```text
gestion_tarea_api/
│── main.py              # API RESTful en FastAPI (Auth JWT, RBAC, CRUD, Búsqueda segura)
│── test_security.py     # Suite de pruebas automatizadas con pytest (4 casos de seguridad)
│── requirements.txt     # Lista de dependencias del proyecto
│── tasks.db             # Base de datos SQLite (generada dinámicamente)
└── README.md            # Memoria técnica y documentación de ejecución
```

---

## 6. Instrucciones de Ejecución

### Paso 1: Iniciar el Servidor de la API
```bash
python -m uvicorn main:app --reload --port 8000
```
- **Documentación Swagger UI:** `http://127.0.0.1:8000/docs`
- **Documentación Redoc:** `http://127.0.0.1:8000/redoc`

### Paso 2: Ejecutar las Pruebas Automatizadas de Seguridad
En una segunda terminal, corre:
```bash
python -m pytest test_security.py -v
```
**Resultado esperado (4 tests en verde):**
```text
test_security.py::test_01_registro_y_login_seguro PASSED                         [ 25%]
test_security.py::test_02_validacion_servidor_y_anti_mass_assignment PASSED     [ 50%]
test_security.py::test_03_control_acceso_anti_idor PASSED                       [ 75%]
test_security.py::test_04_prevencion_inyeccion_sql PASSED                        [100%]
================================== 4 passed in 3.20s ===================================
```

### Paso 3: Análisis Estático de Código (SAST)
```bash
python -m pylint main.py
```

---

## 7. Catálogo Completo de Endpoints

### Autenticación
| Método | Endpoint | Descripción | Acceso |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Registro de usuario con hash seguro (bcrypt) | Público |
| `POST` | `/auth/login` | Inicio de sesión, retorna JWT Bearer | Público |

### Gestión de Tareas
| Método | Endpoint | Descripción | Acceso |
| :--- | :--- | :--- | :--- |
| `POST` | `/tasks` | Crear nueva tarea vinculada al usuario activo | Requiere JWT |
| `GET` | `/tasks` | Listar tareas (Estudiante: solo suyas; Docente/Admin: todas) | Requiere JWT (RBAC) |
| `GET` | `/tasks/search?q={query}` | Búsqueda segura por título usando sentencias parametrizadas | Requiere JWT |
| `PUT` | `/tasks/{id}` | Actualizar tarea con validación de propiedad (Anti-IDOR) | Dueño o Admin |
| `DELETE` | `/tasks/{id}` | Eliminar tarea con validación de propiedad (Anti-IDOR) | Dueño o Admin |