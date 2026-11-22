# INFORME TÉCNICO: ACTIVIDADES 3 Y 4 — GUÍA DE PRÁCTICA 04
## Escuela Profesional de Ingeniería Informática y de Sistemas — UNSAAC
### Asignatura: Ingeniería de Software II (Laboratorio)
### Tema: Ingeniería de Software Seguro (SSDLC, SAST, Refactorización y Hardening)

---

## 1. ACTIVIDAD 3: Despliegue y Diagnóstico del Código Vulnerable (SAST)

### 1.1 Código Fuente Base (`app_vulnerable.py`)
Se implementó el script base provisto en la guía para auditar el sistema de reservas deportivas:

```python
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('reservas.db')
    conn.row_factory = sqlite3.Row
    return conn

# VULNERABILIDAD 1: Inyección SQL + IDOR
@app.route('/api/reserva', methods=['GET'])
def obtener_reserva():
    id_reserva = request.args.get('id')
    user_id_session = request.args.get('user_id')  # Simulación de usuario

    conn = get_db_connection()
    cursor = conn.cursor()
    # Inseguro: Concatenación directa de entradas en la consulta SQL (Línea 49)
    query = f"SELECT * FROM reservas WHERE id = {id_reserva}"
    reserva = cursor.execute(query).fetchone()
    conn.close()

    # VULNERABILIDAD 2: IDOR (Líneas 53-56)
    if reserva is None:
        return jsonify({'error': 'Reserva no encontrada'}), 404

    return jsonify(dict(reserva))

# VULNERABILIDAD 3: XSS Reflejado (Línea 62)
@app.route('/comentario', methods=['GET'])
def ver_comentario():
    comentario = request.args.get('texto', '')
    template = f"<h1>Comentario recibido:</h1><p>{comentario}</p>"
    return render_template_string(template)
```

---

### 1.2 Ejecución y Evidencias del Análisis SAST

#### A. Diagnóstico con Pylint
```bash
python -m pylint app_vulnerable.py
```
**Salida de advertencias reportadas:**
```text
************* Module app_vulnerable
app_vulnerable.py:44:4: W0612: Unused variable 'user_id_session' (unused-variable)
-----------------------------------
Your code has been rated at 7.88/10
```
> **Interpretación SAST:**  
> Pylint detecta la variable sin usar `user_id_session` en la línea 44. Esto constituye la evidencia estática directa del fallo **IDOR**: la aplicación extrae la identidad del usuario de la sesión, pero **nunca la utiliza** para restringir el acceso a los datos de la reserva consultada.

#### B. Diagnóstico con Bandit (Herramienta SAST de Seguridad Python)
```bash
python -m bandit -r app_vulnerable.py
```
**Salida de vulnerabilidades detectadas:**
```text
>> Issue: [B608:hardcoded_sql_expressions] Possible SQL injection vector through string-based query construction.
   Severity: Medium   Confidence: Low
   CWE: CWE-89 (https://cwe.mitre.org/data/definitions/89.html)
   Location: .\app_vulnerable.py:49:12
49    query = f"SELECT * FROM reservas WHERE id = {id_reserva}"
50    reserva = cursor.execute(query).fetchone()

>> Issue: [B201:flask_debug_true] A Flask app appears to be run with debug=True
   Severity: High   Confidence: Medium
   CWE: CWE-94
   Location: .\app_vulnerable.py:72:4
```

---

### 1.3 Matriz de Identificación de Brechas (Líneas Afectadas)

| Vulnerabilidad | Archivo y Línea | Categoría CWE / OWASP | Causa Raíz Técnica |
| :--- | :---: | :---: | :--- |
| **Inyección SQL (SQLi)** | `app_vulnerable.py:49` | **CWE-89** / OWASP A03 | Interpolación de strings (`f"SELECT ... WHERE id = {id_reserva}"`) sin prepared statements. |
| **Falla de Control de Acceso (IDOR)** | `app_vulnerable.py:44-55` | **CWE-639** / OWASP A01 | Ausencia de verificación de autorización en servidor (`user_id_session == reserva['user_id']`). |
| **Cross-Site Scripting (XSS)** | `app_vulnerable.py:62` | **CWE-79** / OWASP A03 | Renderizado directo de strings en `render_template_string` sin sanitización contextual. |

---

## 2. EJERCICIO PROPUESTO 3.1: Validación Servidor y Prevención de Inyección en Logs

### 2.1 Reglas de Validación Implementadas en FastAPI (`main.py`)
En el endpoint `POST /tasks`, se implementó validación estricta utilizando esquemas de Pydantic V2:

```python
class TaskCreateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")  # Mitigación Mass Assignment
    title: str = Field(..., min_length=3, max_length=120)
    description: Optional[str] = Field(None, max_length=1000)
    status: TaskStatus = TaskStatus.PENDIENTE  # Whitelist: pendiente, en_progreso, completada
    priority: Optional[TaskPriority] = TaskPriority.MEDIA
```

### 2.2 Protección contra Inyección en Logs (OWASP Log Injection)
Siguiendo las recomendaciones de OWASP, cuando una solicitud es rechazada por validación, el servidor **nunca registra el payload malicioso sin filtrar** para evitar que atacantes inyecten saltos de línea (`\r\n`) o comandos que falseen las bitácoras:
```python
# Registro seguro de reglas vulneradas sin exponer cargas maliciosas
audit_logger.warning("VALIDATION_ERROR - category: INVALID_INPUT parameter: title rule: LENGTH_OR_FORMAT")
```

### 2.3 Evidencia de Pruebas Automatizadas de Validación (Test 11)
* **Campo vacío (`title=""`):** Rechazado con `HTTP 422 Unprocessable Entity`.
* **Campo demasiado largo (`title > 120` caracteres):** Rechazado con `HTTP 422`.
* **Descripción excesiva (`description > 1000` caracteres):** Rechazado con `HTTP 422`.
* **Estado inválido (`status="borrada"`):** Rechazado con `HTTP 422`.
* **Inyección de campos extra (`role="admin"`):** Rechazado con `HTTP 422`.
* **Caracteres Unicode y tildes:** Aceptado exitosamente con `HTTP 201 Created`.
* **Sin token de autorización:** Rechazado con `HTTP 401 Unauthorized`.

---

## 3. ACTIVIDAD 4: Refactorización y Hardening de Código Seguro (`app_segura.py`)

### 3.1 Código Fuente Refactorizado
Se aplicaron defensas en profundidad en el nuevo archivo `app_segura.py`:

```python
import sqlite3
from flask import Flask, request, jsonify, abort
from markupsafe import escape

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('reservas.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/reserva', methods=['GET'])
def obtener_reserva():
    id_reserva = request.args.get('id')
    user_id_session = request.args.get('user_id')

    # DEFENSA 1: Validación estricta de formato numérico en servidor
    if not id_reserva or not id_reserva.isdigit() or not user_id_session:
        return jsonify({'error': 'Parámetros inválidos o sesión no provista'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # DEFENSA 2: Prepared Statement con marcador ? y tupla (Mitigación SQLi)
    query = "SELECT * FROM reservas WHERE id = ?"
    reserva = cursor.execute(query, (int(id_reserva),)).fetchone()
    conn.close()

    if reserva is None:
        return jsonify({'error': 'Reserva no encontrada'}), 404

    # DEFENSA 3: Autorización en servidor / Anti-IDOR (Mitigación IDOR)
    if str(reserva['user_id']) != str(user_id_session):
        # Aborta estrictamente con HTTP 403 sin revelar datos privados
        abort(403, description="Acceso denegado: No posee privilegios sobre este recurso")

    return jsonify(dict(reserva))

# DEFENSA 4: Sanitización contextual de salida HTML (Mitigación XSS)
@app.route('/comentario', methods=['GET'])
def ver_comentario():
    comentario = request.args.get('texto', '')
    comentario_sanitizado = escape(comentario)
    return f"<h1>Comentario recibido:</h1><p>{comentario_sanitizado}</p>"
```

### 3.2 Verificación SAST Post-Hardening con Bandit
```bash
python -m bandit -r app_segura.py
```
**Resultado del análisis:**
```text
Code scanned:
	Total lines of code: 56
Run metrics:
	Total issues (by severity):
		Undefined: 0
		Low: 0
		Medium: 0
		High: 0
Test results:
	No issues identified.
```
> **Resultado:** Cero vulnerabilidades detectadas (0 issues). Código blindado contra SQLi, IDOR y XSS.

---

## 4. EJERCICIO PROPUESTO 4.1: Tabla Comparativa "Antes vs. Después" de SQLi

### 4.1 Comparativa de Código

| Componente | Antes (Inseguro - Concatenación) | Después (Seguro - Prepared Statements) |
| :--- | :--- | :--- |
| **Sentencia SQL** | `query = f"SELECT * FROM tasks WHERE title LIKE '%" + search + "%'"` | `query = "SELECT * FROM tasks WHERE title LIKE ?"` |
| **Ejecución** | `cursor.execute(query)` | `cursor.execute(query, (f"%{q}%",))` |
| **Validación previa**| Ninguna (permite cadenas arbitrarias) | `q: str = Query(..., min_length=1, max_length=50)` |
| **Comportamiento ante `' OR 1=1 --`** | Modifica la lógica del compilador SQL retornando registros ajenos | Es tratado literalmente como texto plano; no altera la sintaxis SQL |

### 4.2 Justificación de Riesgo
> **¿Por qué la concatenación es crítica?**  
> Porque el motor de base de datos no puede distinguir entre los comandos SQL del programador y los datos suministrados por el usuario. Al usar sentencias parametrizadas (*Prepared Statements*), la base de datos precompila la estructura sintáctica de la consulta y trata cualquier entrada del usuario estrictamente como valor de datos, neutralizando cualquier intento de inyección.

---

## 5. Resultados de la Suite Automatizada de Pruebas (13 Tests en Verde)

Se ejecutó la suite completa de pruebas de seguridad:
```bash
python -m pytest test_security.py -v
```

```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.2.0
rootdir: c:\Users\ASUS\Desktop\9no semestre\ING DE SOFTWARE II-LABO\gestion_tarea_api
collected 13 items

test_security.py::test_01_registro_y_login_seguro PASSED                 [  7%]
test_security.py::test_02_validacion_servidor_y_anti_mass_assignment PASSED [ 15%]
test_security.py::test_03_control_acceso_anti_idor PASSED                [ 23%]
test_security.py::test_04_prevencion_inyeccion_sql PASSED                [ 30%]
test_security.py::test_05_rbac_docente_y_administrador PASSED            [ 38%]
test_security.py::test_06_ciclo_crud_completo_con_endpoint_id PASSED     [ 46%]
test_security.py::test_07_fuerza_bruta_bloqueo_progresivo PASSED         [ 53%]
test_security.py::test_08_restablecimiento_contrasena_un_solo_uso PASSED [ 61%]
test_security.py::test_09_revocacion_sesion_al_cambiar_contrasena PASSED [ 69%]
test_security.py::test_10_sesion_expirada PASSED                         [ 76%]
test_security.py::test_11_propuesto_3_1_validaciones_de_entrada_y_bordes PASSED [ 84%]
test_security.py::test_12_propuesto_4_1_busqueda_segura_casos_borde_sqli PASSED [ 92%]
test_security.py::test_13_actividad_3_y_4_app_vulnerable_vs_app_segura PASSED [100%]

======================== 13 passed in 6.49s ========================
```
