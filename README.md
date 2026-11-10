
# Sistema Seguro de Gestión de Tareas (KawsayTasks)
**Guía de Práctica 04: Ingeniería de Software Seguro**  
**Curso:** Ingeniería de Software II  
**Institución:** Universidad Nacional de San Antonio Abad del Cusco (UNSAAC)  
**Escuela Profesional:** Ingeniería Informática y de Sistemas  
**Autor:** Jhoel Alex Luicho Quispe (Código: 224871)  
**Usuario GitHub:** GamoLG  
**Repositorio:** [PRACTICA-4-INGENIERIA-DE-SOFTWARE-II](https://github.com/GamoLG/PRACTICA-4-INGENIERIA-DE-SOFTWARE-II)

---

## 1. Descripción Técnica y Arquitectura del Sistema
El proyecto consiste en una aplicación web completa desarrollada bajo los lineamientos del ciclo de vida de desarrollo de software seguro (**SSDLC**), mitigando de forma proactiva vulnerabilidades críticas tipificadas en el **OWASP Top 10** (específicamente *A01: Broken Access Control*, *A03: Injection* y *A07: Identification and Authentication Failures*).

La solución desacopla la capa de presentación de la capa lógica y de persistencia:
* **Backend:** API RESTful de alto rendimiento construida con **FastAPI** en Python 3.11, implementando el ciclo de vida asíncrono `lifespan` y base de datos relacional integrada con **SQLite3**.
* **Frontend:** Interfaz SPA (*Single Page Application*) servida dinámicamente desde el backend (`index.html`), estructurada con HTML5 semántico, Tailwind CSS y JavaScript Vanilla interactivo con sanitización DOM nativa y control de visibilidad de contraseñas (`togglePassword`).
* **Seguridad Defensiva:** Validación estricta de esquemas, consultas preparadas obligatorias, hashing criptográfico adaptativo y control de acceso a nivel de objeto (Anti-IDOR) y roles (RBAC).


```text
┌────────────────────────────────────────────────────────────────────────┐
│                        CAPA DE PRESENTACIÓN                            │ │  • SPA HTML5 + Tailwind CSS (index.html)                               │ │  • Consola Interactiva OpenAPI / Swagger UI (/docs)                    │ └───────────────────────────────────┬────────────────────────────────────┘ │ HTTP / JSON (Bearer JWT) ┌───────────────────────────────────▼────────────────────────────────────┐ │                       BACKEND SEGURO (FastAPI)                         │ │  • Autenticación: bcrypt (salt=12) + PyJWT (HS256, exp=60m)            │ │  • RBAC & Objeto: estudiante, docente, administrador (Anti-IDOR)       │ │  • Validación: DTOs Pydantic V2 (extra="forbid")                       │ │  • Anti-SQLi: Prepared Statements en SQLite3                           │ └───────────────────────────────────┬────────────────────────────────────┘ │ SQL Parametrizado (?) ┌───────────────────────────────────▼────────────────────────────────────┐ │                      PERSISTENCIA (SQLite3)                            │ │  • Tablas: users (password_hash) | tasks (owner_id FK)                 │ └────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Controles de Seguridad Implementados (OWASP / SSDLC)

### A. Autenticación Robusta y Gestión de Credenciales (Ejercicio 1.2)
* **Algoritmo de Hash Lento:** Almacenamiento exclusivo de contraseñas procesadas mediante **bcrypt** con un factor de trabajo adaptativo de 12 rondas (`salt rounds = 12`). Nunca se persiste texto plano ni algoritmos vulnerables o rápidos (MD5, SHA-1, SHA-256 plano).
* **Tokens de Sesión Efímeros:** Generación y validación de tokens de acceso Bearer **JWT** firmados criptográficamente mediante HMAC-SHA256 (`HS256`) con ventana de expiración obligatoria (`exp` a 60 minutos).
* **Mitigación de Enumeración de Cuentas:** Mensajes de error unificados (`"Credenciales incorrectas"`) y código de estado idéntico (`HTTP 401 Unauthorized`) tanto ante nombres de usuario inexistentes como ante contraseñas inválidas.
* **Control de Interfaz:** Ocultamiento predeterminado de credenciales con opción de inspección temporal controlada por el usuario (`type="password"` $\leftrightarrow$ `type="text"`).

### B. Control de Acceso a Nivel de Objeto y Roles (Anti-IDOR & RBAC)
* **Control RBAC:** Tres roles jerárquicos: `estudiante`, `docente` y `administrador`.
* **Guarda de Propiedad en Servidor (Anti-IDOR):** En las operaciones de actualización (`PUT /tasks/{id}`) y eliminación (`DELETE /tasks/{id}`), el backend comprueba en el contexto de base de datos que `task.owner_id == current_user.id`. Si un usuario autenticado intenta manipular el identificador de un recurso ajeno, la solicitud es rechazada de inmediato con **`HTTP 403 Forbidden`**.
* **Auditoría Superior:** Los roles `docente` y `administrador` poseen permisos de visualización global, mientras que el `administrador` tiene facultades de saneamiento sobre cualquier tarea.

### C. Prevención de Inyección SQL (Anti-SQLi)
* **Consultas Parametrizadas (Prepared Statements):** Ningún parámetro suministrado por el cliente se concatena en cadenas SQL. Todas las transacciones utilizan placeholders de enlace posicional (`?`) enviando los datos en tuplas inmutables (`(param,)`).
* **Búsqueda Segura:** El endpoint `GET /tasks/search?q=` interpola comodines (`f"%{q}%"`) pasados como dato literal al driver SQLite, neutralizando payloads clásicos como `' OR 1=1 --`.

### D. Validación Estricta de Entradas (Anti-Mass Assignment)
* **Validación por Lista Blanca:** Modelos Pydantic V2 con restricción explícita `model_config = ConfigDict(extra="forbid")`. El envío de campos no autorizados (ej. inyección de `"role": "administrador"` en la creación de tareas) provoca el rechazo automático con **`HTTP 422 Unprocessable Entity`**.
* **Límites de Carga:** Longitudes acotadas para títulos (3 a 120 caracteres), descripciones (máximo 1 000 caracteres) y estados tipificados estrictos (`pendiente`, `en_progreso`, `completada`).

---

## 3. Catálogo de Endpoints de la API

| Método | Ruta | Acceso / Rol | Código Éxito | Códigos de Error | Descripción Técnica |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `GET` | `/` | Público | `200 OK` | `404` | Sirve la interfaz web SPA (`index.html`). |
| `GET` | `/docs` | Público | `200 OK` | - | Interfaz Swagger UI / OpenAPI interactiva. |
| `POST` | `/auth/register` | Público | `201 Created` | `400, 422` | Registra usuario con rol y genera hash bcrypt. |
| `POST` | `/auth/login` | Público | `200 OK` | `401, 422` | Emite el token JWT Bearer de sesión. |
| `POST` | `/tasks` | Autenticado | `201 Created` | `401, 422` | Crea una nueva tarea asociada al usuario en sesión. |
| `GET` | `/tasks` | Autenticado | `200 OK` | `401` | Lista tareas (propias para estudiante; todas para docente/admin). |
| `GET` | `/tasks/search` | Autenticado | `200 OK` | `401, 422` | Búsqueda por título parametrizada contra SQLi. |
| `PUT` | `/tasks/{id}` | Propietario / Admin | `200 OK` | `401, 403, 404, 422` | Actualiza tarea; valida pertenencia anti-IDOR. |
| `DELETE` | `/tasks/{id}` | Propietario / Admin | `200 OK` | `401, 403, 404` | Elimina tarea; valida pertenencia anti-IDOR. |

---

## 4. Requisitos de Instalación del Entorno

### Dependencias del Sistema
* Python 3.10 o superior (verificado en Python 3.11.4 de 64 bits).
* Git instalado y configurado.

### Instalación de Paquetes
Clona el repositorio y ubícate en la raíz del proyecto:
```bash
git clone https://github.com/GamoLG/PRACTICA-4-INGENIERIA-DE-SOFTWARE-II.git
cd PRACTICA-4-INGENIERIA-DE-SOFTWARE-II

````

Instala todas las dependencias requeridas mediante `pip`:

```bash
pip install -r requirements.txt

```

*(O de forma directa: `pip install fastapi uvicorn pydantic bcrypt pyjwt pytest httpx pylint`)*.

## 5. Guía de Ejecución y Pruebas

### 5.1. Levantar el Servidor de Aplicación

Ejecuta el servidor ASGI Uvicorn mediante el módulo de Python:

```bash
python -m uvicorn main:app --reload --port 8000

```

Acceso en navegadores:

- **Frontend Web (KawsayTasks):** `http://127.0.0.1:8000/`
- **Swagger UI / Documentación OpenAPI:** `http://127.0.0.1:8000/docs`

### 5.2. Ejecución de la Suite de Pruebas Automatizadas (Pytest)

En una segunda terminal, corre las aserciones de seguridad:

```bash
python -m pytest test_security.py -v

```

**Resultado validado (4/4 tests en verde):**

- `test_01_registro_y_login_seguro PASSED`: Verifica hash de contraseñas, login con JWT y rechazo de usuarios inexistentes (mitigación de enumeración).
- `test_02_validacion_servidor_y_anti_mass_assignment PASSED`: Verifica el rechazo con código 422 ante la inyección de parámetros prohibidos o estados corruptos.
- `test_03_control_acceso_anti_idor PASSED`: Verifica que el estudiante B recibe `403 Forbidden` al intentar editar o borrar un registro creado por el estudiante A.
- `test_04_prevencion_inyeccion_sql PASSED`: Verifica que payloads de inyección SQL no desbordan datos no autorizados.

### 5.3. Análisis Estático de Código Fuente (SAST)

Ejecuta el linter de seguridad y calidad:

```bash
python -m pylint main.py

```

## 6. Estructura del Repositorio

```text
PRACTICA-4-INGENIERIA-DE-SOFTWARE-II/
│── .gitignore           # Exclusión de base de datos local (*.db), cachés y entornos
│── README.md            # Memoria técnica completa y manual de procedimientos
│── requirements.txt     # Manifiesto de dependencias con versiones
│── main.py              # Backend FastAPI, autenticación JWT, RBAC, CRUD y Anti-IDOR
│── index.html           # Frontend SPA responsivo con Tailwind CSS y control de claves
└── test_security.py     # Suite de pruebas automatizadas con Pytest y TestClient

```

````

---

### ¿Qué se hizo y qué se debe hacer ahora?

####  Lo que ya está hecho y comprobado:
1. Implementación completa de la API en FastAPI con autenticación `bcrypt`, sesiones `JWT`, control `RBAC` (estudiante, docente, admin), mitigación de `IDOR` y prevención de `SQLi`[cite: 2, 5, 6, 7, 10, 11].
2. Frontend interactivo SPA (`index.html`) con TailwindCSS, conectado al backend, con botones para mostrar/ocultar contraseña y tablas dinámicas[cite: 14].
3. Suite de pruebas automatizadas en `test_security.py` verificada con **`4 passed`**[cite: 12].
4. Repositorio en GitHub configurado y vinculado bajo tu usuario `GamoLG`.

#### 📋 Lo que debes hacer ahora para entregar:
1. **Actualizar el README en tu proyecto:**
   * Abre `README.md` en tu editor, pega este contenido completo y guárdalo.
2. **Subir los últimos cambios a GitHub:**
   ```bash
   git add README.md index.html main.py
   git commit -m "docs: actualizar memoria tecnica y controles ssdlc en readme"
   git push origin main
