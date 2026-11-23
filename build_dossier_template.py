import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Paleta de colores oficial de la plantilla
    C_NAVY_TITLE = RGBColor(15, 43, 72)     # #0f2b48 azul marino oscuro encabezados
    C_NAVY_CARD  = RGBColor(15, 35, 60)     # #0f233c fondo tarjetas requisitos
    C_BLUE_HDR   = RGBColor(14, 56, 96)     # #0e3860 azul marino SSDLC
    C_RED_ALERT  = RGBColor(220, 38, 38)    # #dc2626 rojo antes/crítico
    C_GREEN_OK   = RGBColor(22, 163, 74)    # #16a34a verde después
    C_ORANGE_WRN = RGBColor(234, 88, 12)    # #ea580c naranja
    C_YELLOW_WRN = RGBColor(234, 179, 8)    # #eab308 amarillo
    C_DARK_BOX   = RGBColor(20, 35, 55)     # #142337 cajas inferiores pruebas negativas
    C_WHITE      = RGBColor(255, 255, 255)
    C_GRAY_LIGHT = RGBColor(241, 245, 249)  # #f1f5f9
    C_TEXT_DARK  = RGBColor(30, 41, 59)     # #1e293b
    C_TEXT_MUTED = RGBColor(100, 116, 139)  # #64748b

    img_dir = "CAPTURAS DE PANTALLA DEL SOFTWARE"

    # =========================================================================
    # SLIDE 1: PORTADA OFICIAL (Igual a Imagen 1 e Imagen 3 de la plantilla)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    
    # 1. Franja guinda del escudo UNSAAC a la izquierda
    if os.path.exists("logo_0.png"):
        s1.shapes.add_picture("logo_0.png", 0, 0, Inches(3.96), Inches(7.50))
    else:
        bg_left = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(3.96), Inches(7.50))
        bg_left.fill.solid()
        bg_left.fill.fore_color.rgb = RGBColor(104, 19, 38)
        bg_left.line.fill.background()

    # 2. Logo redondo de Ingeniería Informática y de Sistemas arriba a la derecha
    if os.path.exists("logo_3.png"):
        s1.shapes.add_picture("logo_3.png", Inches(11.8), Inches(0.2), Inches(1.3), Inches(1.3))

    # 3. Textos institucionales
    t1 = s1.shapes.add_textbox(Inches(4.4), Inches(0.4), Inches(7.2), Inches(0.5))
    p = t1.text_frame.paragraphs[0]
    p.text = "FACULTAD DE INGENIERIA INFORMÁTICA"
    p.font.name = "Arial"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE

    t2 = s1.shapes.add_textbox(Inches(4.4), Inches(0.95), Inches(8.2), Inches(0.4))
    p = t2.text_frame.paragraphs[0]
    p.text = "ESCUELA PROFESIONAL DE INGENIERIA INFORMÁTICA Y DE SISTEMAS"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_TEXT_MUTED

    t3 = s1.shapes.add_textbox(Inches(4.4), Inches(1.45), Inches(8.2), Inches(0.5))
    p = t3.text_frame.paragraphs[0]
    p.text = "INGENIERIA DE SOFTWARE II"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE

    # Línea decorativa
    line = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.4), Inches(2.2), Inches(7.5), Inches(0.04))
    line.fill.solid()
    line.fill.fore_color.rgb = C_RED_ALERT
    line.line.fill.background()

    # Título del Proyecto
    t_title = s1.shapes.add_textbox(Inches(4.4), Inches(2.4), Inches(8.5), Inches(0.8))
    p = t_title.text_frame.paragraphs[0]
    p.text = "Titulo: Gestión de Tareas API (Software Seguro)"
    p.font.name = "Arial"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE

    # Equipo
    t_eq = s1.shapes.add_textbox(Inches(4.4), Inches(3.3), Inches(5.0), Inches(0.5))
    p = t_eq.text_frame.paragraphs[0]
    p.text = "EQUIPO: EQUIPO 02"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE

    # Integrantes
    t_int = s1.shapes.add_textbox(Inches(4.4), Inches(3.9), Inches(8.5), Inches(1.8))
    tf_int = t_int.text_frame
    tf_int.word_wrap = True
    p = tf_int.paragraphs[0]
    p.text = "INTEGRANTES:"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE
    
    p2 = tf_int.add_paragraph()
    p2.text = "• Estudiantes del Equipo 02 — Escuela Profesional de Ingeniería Informática y de Sistemas"
    p2.font.name = "Arial"
    p2.font.size = Pt(12)
    p2.font.color.rgb = C_TEXT_DARK

    p3 = tf_int.add_paragraph()
    p3.text = "• Docente: Ing. Alex Fernando Huillca Huaman"
    p3.font.name = "Arial"
    p3.font.size = Pt(12)
    p3.font.bold = True
    p3.font.color.rgb = C_TEXT_DARK

    p4 = tf_int.add_paragraph()
    p4.text = "• Repositorio: https://github.com/GamoLG/PRACTICA-4-INGENIERIA-DE-SOFTWARE-II"
    p4.font.name = "Arial"
    p4.font.size = Pt(10.5)
    p4.font.color.rgb = RGBColor(37, 99, 235)

    p5 = tf_int.add_paragraph()
    p5.text = "• Producción: https://practica-4-ingenieria-de-software-ii.onrender.com"
    p5.font.name = "Arial"
    p5.font.size = Pt(10.5)
    p5.font.color.rgb = RGBColor(16, 185, 129)

    # =========================================================================
    # SLIDE 2: ÍNDICE OFICIAL (Igual a Imagen 3 de la plantilla)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)

    # Lado izquierdo: ÍNDICE
    t_idx = s2.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(4.0), Inches(3.0))
    p = t_idx.text_frame.paragraphs[0]
    p.text = "ÍNDICE"
    p.font.name = "Arial Black"
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE

    # Línea vertical separadora
    sep = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.8), Inches(1.2), Inches(0.04), Inches(5.2))
    sep.fill.solid()
    sep.fill.fore_color.rgb = C_RED_ALERT
    sep.line.fill.background()

    # Lado derecho: Contenido
    t_cnt = s2.shapes.add_textbox(Inches(5.3), Inches(1.1), Inches(7.5), Inches(5.4))
    tf_c = t_cnt.text_frame
    tf_c.word_wrap = True

    p = tf_c.paragraphs[0]
    p.text = "Contenido"
    p.font.name = "Arial"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE
    p.space_after = Pt(20)

    indice_items = [
        "1.- Mapa SSDLC",
        "2.- Requisitos de seguridad",
        "3.- Matriz de riesgos",
        "4.- Propuesta de código seguro",
        "5.- Conclusiones y evidencias"
    ]
    for item in indice_items:
        p = tf_c.add_paragraph()
        p.text = item
        p.font.name = "Arial"
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(14)

    # =========================================================================
    # SLIDE 3: 1.- MAPA SSDLC (Estilo Imagen 4 de la plantilla)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)

    # Header banner azul petróleo
    hdr3 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(0.2), Inches(10.9), Inches(0.75))
    hdr3.fill.solid()
    hdr3.fill.fore_color.rgb = C_BLUE_HDR
    hdr3.line.fill.background()
    p = hdr3.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "MAPA SSDLC: GESTIÓN DE TAREAS API"
    p.font.name = "Arial"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    # 6 Etapas con diseño serpenteante
    ssdlc_steps = [
        ("1. Requisitos:", "DTOs Pydantic extra='forbid' y Especificación Formal", "Definición estricta de campos, roles y políticas de seguridad desde el día 0."),
        ("2. Diseño:", "Modelado STRIDE y Lógica de Permisos RBAC", "Definición de Trust Boundaries, JWT con identificador único jti y matriz RBAC."),
        ("3. Desarrollo:", "Consultas Parametrizadas y Análisis SAST", "Prepared Statements con '?' y verificación continua con Bandit (0 alertas)."),
        ("4. Pruebas:", "Control Anti-IDOR y Pruebas Automatizadas", "Validación owner_id a nivel de fila y 19 pruebas de penetración en pytest."),
        ("5. Despliegue:", "Hardening, TLS/HTTPS forzado y Security Headers", "Infraestructura segura en Render, HSTS, CSP, X-Frame-Options y CORS regex."),
        ("6. Mantenimiento:", "Monitoreo con audit.log y Revocación token_version", "Bitácora de auditoría sin credenciales y revocación inmediata de sesiones.")
    ]

    for i, (fase, title, desc) in enumerate(ssdlc_steps):
        col = i % 2
        row = i // 2
        left_p = Inches(1.2 + col * 5.6)
        top_p = Inches(1.2 + row * 1.95)

        box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_p, top_p, Inches(5.3), Inches(1.75))
        box.fill.solid()
        box.fill.fore_color.rgb = C_WHITE
        box.line.color.rgb = C_BLUE_HDR
        box.line.width = Pt(2)

        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = f"{fase} {title}"
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_BLUE_HDR
        p.space_after = Pt(4)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = "Arial"
        p2.font.size = Pt(10)
        p2.font.color.rgb = C_TEXT_DARK

    # =========================================================================
    # SLIDE 4: 2.- REQUISITOS DE SEGURIDAD (Estilo Imagen 5 de la plantilla)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)

    # Título en texto grande
    t_req = s4.shapes.add_textbox(Inches(1.5), Inches(0.3), Inches(10.3), Inches(1.0))
    p = t_req.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "REQUISITOS DE SEGURIDAD\nVERIFICABLES"
    p.font.name = "Arial Black"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE

    # Línea decorativa roja y naranja
    l_red = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.4), Inches(11.733), Inches(0.06))
    l_red.fill.solid()
    l_red.fill.fore_color.rgb = C_RED_ALERT
    l_red.line.fill.background()

    # 5 Tarjetas horizontales tipo píldora (Exacto al diseño de Imagen 5)
    reqs_pills = [
        ("REQ-SEC-01: Control de acceso anti-IDOR en tareas - Crítica", "Validación obligatoria owner_id == user_id. Rechazo con HTTP 403 Forbidden. (Test: test_03_idor)"),
        ("REQ-SEC-02: Prevención de Inyección SQL con Prepared Statements - Crítica", "Consultas parametrizadas con '?'. Búsqueda con ' OR 1=1 -- retorna lista vacía []. (Test: test_17_sqli)"),
        ("REQ-SEC-03: Almacenamiento seguro con hash bcrypt (costo 12) - Crítica", "Contraseñas protegidas mediante bcrypt con salt aleatorio (prefijo $2b$12$). (Test: test_01_register)"),
        ("REQ-SEC-04: Rate Limiting progresivo anti-fuerza bruta - Alta", "Bloqueo progresivo (30s / 180s) tras 3 fallos. El 4.º intento retorna HTTP 429. (Test: test_06_brute)"),
        ("REQ-SEC-05: Revocación global de sesiones por token_version - Alta", "Invalidación inmediata de JWT antiguos tras cambiar la contraseña (HTTP 401). (Test: test_09_revoke)")
    ]

    for idx, (req_title, req_sub) in enumerate(reqs_pills):
        top_pos = Inches(1.7 + idx * 1.05)
        
        # Tarjeta contenedor azul oscuro
        pill = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), top_pos, Inches(9.7), Inches(0.9))
        pill.fill.solid()
        pill.fill.fore_color.rgb = C_NAVY_CARD
        pill.line.fill.background()

        # Escudo / Badge a la izquierda
        shield = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.0), top_pos + Inches(0.12), Inches(0.65), Inches(0.65))
        shield.fill.solid()
        shield.fill.fore_color.rgb = C_RED_ALERT if idx < 3 else (C_ORANGE_WRN if idx == 3 else RGBColor(234, 88, 12))
        shield.line.fill.background()
        sp = shield.text_frame.paragraphs[0]
        sp.alignment = PP_ALIGN.CENTER
        sp.text = "🛡️"
        sp.font.size = Pt(16)

        # Texto del requisito
        tx = s4.shapes.add_textbox(Inches(2.8), top_pos + Inches(0.05), Inches(8.5), Inches(0.8))
        tf = tx.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = req_title
        p1.font.name = "Arial"
        p1.font.size = Pt(12.5)
        p1.font.bold = True
        p1.font.color.rgb = C_WHITE

        p2 = tf.add_paragraph()
        p2.text = req_sub
        p2.font.name = "Arial"
        p2.font.size = Pt(10)
        p2.font.color.rgb = RGBColor(203, 213, 225)

    # =========================================================================
    # SLIDE 5: 3.- MATRIZ DE RIESGOS (Estilo Imagen 6 de la plantilla)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)

    # Título
    t_mat = s5.shapes.add_textbox(Inches(1.5), Inches(0.2), Inches(10.3), Inches(0.8))
    p = t_mat.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "MATRIZ DE RIESGOS:\nGESTIÓN DE TAREAS API"
    p.font.name = "Arial Black"
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE

    # Línea decorativa
    l_m = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.3), Inches(11.733), Inches(0.05))
    l_m.fill.solid()
    l_m.fill.fore_color.rgb = C_RED_ALERT
    l_m.line.fill.background()

    # 5 Filas de riesgo estilo infografía (Idéntico a Imagen 6)
    risks = [
        ("R-01", C_RED_ALERT, "Inyección SQL en búsqueda:", "Riesgo Extremo / Crítico (Score: 20) — Mitigar con Prepared Statements (?)", [C_ORANGE_WRN, C_ORANGE_WRN, C_RED_ALERT, C_RED_ALERT]),
        ("R-02", C_ORANGE_WRN, "Acceso a tareas ajenas (IDOR):", "Riesgo Crítico (Score: 16) — Validar sesión activa y owner_id == user_id", [C_YELLOW_WRN, C_ORANGE_WRN, C_ORANGE_WRN, C_RED_ALERT]),
        ("R-03", C_ORANGE_WRN, "Fuerza bruta en Login:", "Riesgo Crítico (Score: 16) — Rate Limiting progresivo (IP y cuenta, 30s/180s)", [C_YELLOW_WRN, C_ORANGE_WRN, C_ORANGE_WRN, C_RED_ALERT]),
        ("R-04", C_ORANGE_WRN, "Reutilización token de reseteo:", "Riesgo Alto (Score: 15) — Token criptográfico SHA-256 de un solo uso (1h)", [C_YELLOW_WRN, C_YELLOW_WRN, C_ORANGE_WRN, C_ORANGE_WRN]),
        ("R-05", C_YELLOW_WRN, "Inyección XSS en comentarios:", "Riesgo Medio (Score: 9) — Sanitización de salidas con markupsafe.escape()", [RGBColor(34, 197, 94), C_YELLOW_WRN, C_YELLOW_WRN, C_YELLOW_WRN])
    ]

    for idx, (r_id, r_col, r_tit, r_desc, grid_colors) in enumerate(risks):
        top_pos = Inches(1.5 + idx * 1.1)

        # 1. Badge ID a la izquierda (R-01, R-02, etc.)
        b_id = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), top_pos, Inches(1.2), Inches(0.95))
        b_id.fill.solid()
        b_id.fill.fore_color.rgb = r_col
        b_id.line.fill.background()
        bp = b_id.text_frame.paragraphs[0]
        bp.alignment = PP_ALIGN.CENTER
        bp.text = r_id
        bp.font.name = "Arial Black"
        bp.font.size = Pt(20)
        bp.font.bold = True
        bp.font.color.rgb = C_WHITE

        # 2. Bloque central azul marino oscuro
        b_cnt = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(2.75), top_pos, Inches(5.8), Inches(0.95))
        b_cnt.fill.solid()
        b_cnt.fill.fore_color.rgb = C_NAVY_CARD
        b_cnt.line.fill.background()

        tf = b_cnt.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = r_tit
        p1.font.name = "Arial"
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = C_WHITE

        p2 = tf.add_paragraph()
        p2.text = r_desc
        p2.font.name = "Arial"
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = RGBColor(226, 232, 240)

        # 3. Cuadrícula de mapa de calor a la derecha (4 bloques de severidad)
        for g_i, g_col in enumerate(grid_colors):
            g_left = Inches(8.6 + g_i * 0.78)
            g_box = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, g_left, top_pos, Inches(0.74), Inches(0.95))
            g_box.fill.solid()
            g_box.fill.fore_color.rgb = g_col
            g_box.line.color.rgb = C_WHITE
            g_box.line.width = Pt(1)

    # =========================================================================
    # SLIDE 6: 4.- PROPUESTA DE CÓDIGO SEGURO (Estilo Imagen 7 de la plantilla)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)

    # Título
    t_cod = s6.shapes.add_textbox(Inches(1.5), Inches(0.3), Inches(10.3), Inches(0.8))
    p = t_cod.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "PROPUESTA DE\nCÓDIGO SEGURO"
    p.font.name = "Arial Black"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE

    # Línea decorativa
    l_c = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.3), Inches(11.733), Inches(0.05))
    l_c.fill.solid()
    l_c.fill.fore_color.rgb = C_RED_ALERT
    l_c.line.fill.background()

    # Cuadro Rojo Izquierdo: ANTES - CÓDIGO VULNERABLE
    box_bad = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(1.6), Inches(4.6), Inches(3.6))
    box_bad.fill.solid()
    box_bad.fill.fore_color.rgb = C_RED_ALERT
    box_bad.line.fill.background()

    # Ícono de advertencia ⚠️ arriba
    icon_w = s6.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(3.7), Inches(1.8), Inches(0.8), Inches(0.7))
    icon_w.fill.solid()
    icon_w.fill.fore_color.rgb = C_WHITE
    icon_w.line.fill.background()

    tf_b = box_bad.text_frame
    tf_b.word_wrap = True
    p = tf_b.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "\n\n\nANTES - CÓDIGO VULNERABLE:"
    p.font.name = "Arial Black"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_after = Pt(10)

    p2 = tf_b.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.text = "Concatenación SQL directa e IDOR sin validar usuario\n(Bandit B608 CWE-89, Pylint W0612 CWE-284)"
    p2.font.name = "Arial"
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_WHITE

    # Cuadro Verde Derecho: DESPUÉS - CÓDIGO SEGURO
    box_good = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.6), Inches(4.6), Inches(3.6))
    box_good.fill.solid()
    box_good.fill.fore_color.rgb = C_GREEN_OK
    box_good.line.fill.background()

    # Ícono escudo 🛡️ arriba
    icon_g = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), Inches(1.8), Inches(0.8), Inches(0.7))
    icon_g.fill.solid()
    icon_g.fill.fore_color.rgb = C_WHITE
    icon_g.line.fill.background()
    gp = icon_g.text_frame.paragraphs[0]
    gp.alignment = PP_ALIGN.CENTER
    gp.text = "🛡️"
    gp.font.size = Pt(18)

    tf_g = box_good.text_frame
    tf_g.word_wrap = True
    p = tf_g.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "\n\n\nDESPUÉS - CÓDIGO SEGURO:"
    p.font.name = "Arial Black"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_after = Pt(10)

    p2 = tf_g.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.text = "Validación Regex, consulta parametrizada con '?', filtro obligatorio owner_id == user_id (HTTP 403) y escape()"
    p2.font.name = "Arial"
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_WHITE

    # Cuadros inferiores oscuros: PRUEBAS NEGATIVAS (Idéntico a Imagen 7)
    b_neg1 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(5.4), Inches(4.6), Inches(1.4))
    b_neg1.fill.solid()
    b_neg1.fill.fore_color.rgb = C_DARK_BOX
    b_neg1.line.fill.background()
    tf_n1 = b_neg1.text_frame
    tf_n1.word_wrap = True

    p = tf_n1.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "PRUEBA NEGATIVA 1:"
    p.font.name = "Arial Black"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p2 = tf_n1.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.text = "Intento SQLi bloqueado (' OR 1=1 --)\nretorna lista vacía [] con HTTP 200"
    p2.font.name = "Arial"
    p2.font.size = Pt(11)
    p2.font.color.rgb = RGBColor(203, 213, 225)

    b_neg2 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(5.4), Inches(4.6), Inches(1.4))
    b_neg2.fill.solid()
    b_neg2.fill.fore_color.rgb = C_DARK_BOX
    b_neg2.line.fill.background()
    tf_n2 = b_neg2.text_frame
    tf_n2.word_wrap = True

    p = tf_n2.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "PRUEBA NEGATIVA 2:"
    p.font.name = "Arial Black"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p2 = tf_n2.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.text = "Intento IDOR bloqueado (DELETE recurso ajeno)\ncon código estricto HTTP 403 Forbidden"
    p2.font.name = "Arial"
    p2.font.size = Pt(11)
    p2.font.color.rgb = RGBColor(203, 213, 225)

    # =========================================================================
    # SLIDE 7: 5.- EVIDENCIAS (PARTE 1: LOGIN Y CONTROL DE ACCESO)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)

    # Título EVIDENCIAS
    t_ev = s7.shapes.add_textbox(Inches(2.5), Inches(0.2), Inches(8.3), Inches(0.6))
    p = t_ev.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "EVIDENCIAS"
    p.font.name = "Arial Black"
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE

    # Subtítulo LOGIN a la izquierda
    t_sub1 = s7.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(5.6), Inches(0.5))
    p = t_sub1.text_frame.paragraphs[0]
    p.text = "LOGIN Y SEGURIDAD DE ACCESO"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE

    # Subtítulo CRUD TAREAS a la derecha
    t_sub2 = s7.shapes.add_textbox(Inches(6.9), Inches(0.8), Inches(5.6), Inches(0.5))
    p = t_sub2.text_frame.paragraphs[0]
    p.text = "CRUD DE TAREAS Y VALIDACIÓN"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE

    # Línea decorativa
    l_ev = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.04))
    l_ev.fill.solid()
    l_ev.fill.fore_color.rgb = C_RED_ALERT
    l_ev.line.fill.background()

    # Imágenes lado izquierdo (Login)
    img_login = os.path.join(img_dir, "LOGIN.png")
    if os.path.exists(img_login):
        s7.shapes.add_picture(img_login, Inches(0.8), Inches(1.5), Inches(5.6), Inches(2.6))

    img_sec_log = os.path.join(img_dir, "seguridad en el inicio de sesion.png")
    if os.path.exists(img_sec_log):
        s7.shapes.add_picture(img_sec_log, Inches(0.8), Inches(4.3), Inches(5.6), Inches(2.7))

    # Imágenes lado derecho (CRUD Tareas)
    img_crud1 = os.path.join(img_dir, "creacion de tarea.png")
    if os.path.exists(img_crud1):
        s7.shapes.add_picture(img_crud1, Inches(6.9), Inches(1.5), Inches(5.6), Inches(2.6))

    img_crud2 = os.path.join(img_dir, "lista de tareas.png")
    if os.path.exists(img_crud2):
        s7.shapes.add_picture(img_crud2, Inches(6.9), Inches(4.3), Inches(5.6), Inches(2.7))

    # =========================================================================
    # SLIDE 8: 5.- EVIDENCIAS (PARTE 2: ANTI-IDOR, BÚSQUEDA Y ROLES)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)

    # Título EVIDENCIAS
    t_ev2 = s8.shapes.add_textbox(Inches(2.5), Inches(0.2), Inches(8.3), Inches(0.6))
    p = t_ev2.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "EVIDENCIAS"
    p.font.name = "Arial Black"
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE

    # Subtítulo Izquierdo: ANTI-IDOR & BÚSQUEDA
    t_sub3 = s8.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(5.6), Inches(0.5))
    p = t_sub3.text_frame.paragraphs[0]
    p.text = "PROTECCIÓN ANTI-IDOR & BÚSQUEDA"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE

    # Subtítulo Derecho: ROLES RBAC & SWAGGER
    t_sub4 = s8.shapes.add_textbox(Inches(6.9), Inches(0.8), Inches(5.6), Inches(0.5))
    p = t_sub4.text_frame.paragraphs[0]
    p.text = "ROLES RBAC & DOCUMENTACIÓN API"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE

    # Línea decorativa
    l_ev2 = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.04))
    l_ev2.fill.solid()
    l_ev2.fill.fore_color.rgb = C_RED_ALERT
    l_ev2.line.fill.background()

    # Imágenes lado izquierdo
    img_idor = os.path.join(img_dir, "eliminar una tarea.png")
    if os.path.exists(img_idor):
        s8.shapes.add_picture(img_idor, Inches(0.8), Inches(1.5), Inches(5.6), Inches(2.6))

    img_search = os.path.join(img_dir, "buscar tareas.png")
    if os.path.exists(img_search):
        s8.shapes.add_picture(img_search, Inches(0.8), Inches(4.3), Inches(5.6), Inches(2.7))

    # Imágenes lado derecho
    img_admin = os.path.join(img_dir, "perfil del admin.png")
    if os.path.exists(img_admin):
        s8.shapes.add_picture(img_admin, Inches(6.9), Inches(1.5), Inches(5.6), Inches(2.6))

    img_api = os.path.join(img_dir, "APIs del software 1.png")
    if os.path.exists(img_api):
        s8.shapes.add_picture(img_api, Inches(6.9), Inches(4.3), Inches(5.6), Inches(2.7))

    # =========================================================================
    # SLIDE 9: CONCLUSIONES (Estilo Imagen 8 de la plantilla)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)

    # Título CONCLUSIONES
    t_con = s9.shapes.add_textbox(Inches(2.5), Inches(0.3), Inches(8.3), Inches(0.6))
    p = t_con.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "CONCLUSIONES"
    p.font.name = "Arial Black"
    p.font.size = Pt(30)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_TITLE

    # Línea decorativa
    l_con = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(11.733), Inches(0.05))
    l_con.fill.solid()
    l_con.fill.fore_color.rgb = C_RED_ALERT
    l_con.line.fill.background()

    # 4 Bloques ejecutivos de conclusiones
    conclusions_data = [
        ("1. SEGURIDAD DESDE EL DISEÑO (SHIFT-LEFT):", "La aplicación formal del modelado de amenazas STRIDE y la definición de DTOs en Pydantic con extra='forbid' permitieron anticipar y erradicar vulnerabilidades críticas como SQLi e IDOR antes de escribir código, reduciendo drásticamente los costos de remediación."),
        ("2. EFECTIVIDAD DEL ANÁLISIS ESTÁTICO (SAST):", "El uso temprano de Bandit y Pylint aportó objetividad técnica al detectar la variable user_id_session no utilizada (W0612) en app_vulnerable.py, transformando un fallo de Broken Access Control en un control estricto a nivel de fila verificado con 0 alertas en app_segura.py."),
        ("3. TESTING NEGATIVO COMO SALVAGUARDA TÉCNICA:", "Evaluar únicamente el 'happy path' es insuficiente en software seguro. La batería de 19 pruebas de penetración automatizadas (pytest) inyectando payloads maliciosos reales garantiza que la lógica de negocio resista ataques sin degradar su integridad."),
        ("4. HARDENING Y OBSERVABILIDAD EN PRODUCCIÓN:", "La combinación de HTTPS forzado en Render, middleware de cabeceras de seguridad (HSTS, CSP, X-Frame-Options), CORS restrictivo y bitácora estructurada en audit.log consolida una arquitectura defendible y trazable que cumple con el OWASP Top 10.")
    ]

    for i, (tit, txt) in enumerate(conclusions_data):
        top_p = Inches(1.5 + i * 1.35)
        c_box = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), top_p, Inches(11.333), Inches(1.2))
        c_box.fill.solid()
        c_box.fill.fore_color.rgb = C_WHITE
        c_box.line.color.rgb = C_NAVY_TITLE
        c_box.line.width = Pt(1.5)

        tf = c_box.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = tit
        p1.font.name = "Arial"
        p1.font.size = Pt(12.5)
        p1.font.bold = True
        p1.font.color.rgb = C_NAVY_TITLE
        p1.space_after = Pt(2)

        p2 = tf.add_paragraph()
        p2.text = txt
        p2.font.name = "Arial"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = C_TEXT_DARK

    # Guardar la presentación
    output_pptx = "MINI_DOSSIER_PLANTILLA_OFICIAL.pptx"
    prs.save(output_pptx)
    print(f"Presentación oficial creada en: {output_pptx}")

if __name__ == "__main__":
    build_presentation()
