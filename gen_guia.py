"""
Genera la Guía Técnica y de Usuario del Dashboard Administración Digital España
en formato PDF, siguiendo el modelo del C.M.N.E.
Salida: guia_admindash.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable
from datetime import datetime
import os

# ── Paleta de colores ──────────────────────────────────────────
AZUL        = colors.HexColor("#0d47a1")
AZUL_CLARO  = colors.HexColor("#1565c0")
AZUL_BG     = colors.HexColor("#e3f2fd")
ROJO        = colors.HexColor("#b71c1c")
NARANJA     = colors.HexColor("#e65100")
VERDE       = colors.HexColor("#1b5e20")
GRIS_DARK   = colors.HexColor("#263238")
GRIS_MED    = colors.HexColor("#546e7a")
GRIS_LIGHT  = colors.HexColor("#eceff1")
AMARILLO    = colors.HexColor("#f9a825")
BLANCO      = colors.white

W, H = A4

# ── Estilos ────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()
    s = {}

    s["portada_titulo"] = ParagraphStyle("portada_titulo",
        fontName="Helvetica-Bold", fontSize=22, textColor=BLANCO,
        leading=28, alignment=TA_CENTER, spaceAfter=8)

    s["portada_sub"] = ParagraphStyle("portada_sub",
        fontName="Helvetica", fontSize=12, textColor=AZUL_BG,
        leading=16, alignment=TA_CENTER, spaceAfter=6)

    s["portada_meta"] = ParagraphStyle("portada_meta",
        fontName="Helvetica", fontSize=9, textColor=AZUL_BG,
        leading=13, alignment=TA_CENTER)

    s["h1"] = ParagraphStyle("h1",
        fontName="Helvetica-Bold", fontSize=14, textColor=AZUL,
        leading=18, spaceBefore=18, spaceAfter=6,
        borderPad=4, leftIndent=0)

    s["h2"] = ParagraphStyle("h2",
        fontName="Helvetica-Bold", fontSize=11, textColor=AZUL_CLARO,
        leading=15, spaceBefore=12, spaceAfter=4)

    s["h3"] = ParagraphStyle("h3",
        fontName="Helvetica-Bold", fontSize=10, textColor=GRIS_DARK,
        leading=13, spaceBefore=8, spaceAfter=3)

    s["body"] = ParagraphStyle("body",
        fontName="Helvetica", fontSize=9.5, textColor=GRIS_DARK,
        leading=14, alignment=TA_JUSTIFY, spaceAfter=4)

    s["body_en"] = ParagraphStyle("body_en",
        fontName="Helvetica-Oblique", fontSize=8.5, textColor=GRIS_MED,
        leading=13, alignment=TA_JUSTIFY, spaceAfter=6)

    s["bullet"] = ParagraphStyle("bullet",
        fontName="Helvetica", fontSize=9.5, textColor=GRIS_DARK,
        leading=14, leftIndent=14, spaceAfter=2,
        bulletIndent=4)

    s["code"] = ParagraphStyle("code",
        fontName="Courier", fontSize=8, textColor=GRIS_DARK,
        leading=12, leftIndent=10, spaceAfter=2,
        backColor=GRIS_LIGHT)

    s["note"] = ParagraphStyle("note",
        fontName="Helvetica-Oblique", fontSize=8.5, textColor=NARANJA,
        leading=12, leftIndent=8, spaceAfter=4)

    s["alert"] = ParagraphStyle("alert",
        fontName="Helvetica-Bold", fontSize=9, textColor=ROJO,
        leading=13, leftIndent=8, spaceAfter=4)

    s["footer"] = ParagraphStyle("footer",
        fontName="Helvetica", fontSize=7.5, textColor=GRIS_MED,
        alignment=TA_CENTER)

    s["toc_item"] = ParagraphStyle("toc_item",
        fontName="Helvetica", fontSize=9.5, textColor=GRIS_DARK,
        leading=16, leftIndent=10)

    s["toc_num"] = ParagraphStyle("toc_num",
        fontName="Helvetica-Bold", fontSize=9.5, textColor=AZUL,
        leading=16)

    return s

S = make_styles()

# ── Helpers ────────────────────────────────────────────────────
def hr(color=AZUL, thickness=0.8):
    return HRFlowable(width="100%", thickness=thickness,
                      color=color, spaceAfter=6, spaceBefore=2)

def sp(h=6):
    return Spacer(1, h)

def h1(txt):
    return [hr(AZUL, 1.5), Paragraph(txt, S["h1"]), sp(2)]

def h2(txt):
    return [Paragraph(txt, S["h2"]), sp(2)]

def body(txt):
    return Paragraph(txt, S["body"])

def body_en(txt):
    return Paragraph(f"<i>EN: {txt}</i>", S["body_en"])

def bullet(items):
    return [Paragraph(f"• {i}", S["bullet"]) for i in items]

def code(lines):
    elems = []
    for l in lines:
        elems.append(Paragraph(l.replace(" ", "&nbsp;"), S["code"]))
    return elems

def tabla(data, col_widths=None, header_color=AZUL):
    col_widths = col_widths or [W * 0.28, W * 0.38, W * 0.26]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  header_color),
        ("TEXTCOLOR",    (0,0), (-1,0),  BLANCO),
        ("FONTNAME",     (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,0),  8.5),
        ("ALIGN",        (0,0), (-1,0),  "CENTER"),
        ("FONTNAME",     (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",     (0,1), (-1,-1), 8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [BLANCO, GRIS_LIGHT]),
        ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#b0bec5")),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",   (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
    ])
    t.setStyle(style)
    return t

# ── Header / Footer de página ──────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    # Header band
    canvas.setFillColor(AZUL)
    canvas.rect(0, H - 1.1*cm, W, 1.1*cm, fill=1, stroke=0)
    canvas.setFillColor(BLANCO)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(1.5*cm, H - 0.72*cm,
                      "Dashboard Administración Digital España — Guía Técnica y de Usuario v1.0")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(W - 1.5*cm, H - 0.72*cm, "M. Castillo · mybloggingnotes@gmail.com")
    # Footer
    canvas.setFillColor(GRIS_MED)
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(W/2, 0.6*cm,
        f"© 2026 M. Castillo · mybloggingnotes@gmail.com  —  Página {doc.page}")
    canvas.restoreState()

def on_page_first(canvas, doc):
    """Sin header/footer en portada."""
    pass

# ── PORTADA ────────────────────────────────────────────────────
def portada():
    elems = []
    # Fondo azul simulado con tabla de una celda
    portada_data = [[
        Paragraph(
            "<b>Dashboard<br/>Administración Digital España</b>",
            ParagraphStyle("pt", fontName="Helvetica-Bold", fontSize=26,
                           textColor=BLANCO, leading=32, alignment=TA_CENTER)
        )
    ]]
    pt = Table(portada_data, colWidths=[W - 3*cm])
    pt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), AZUL),
        ("TOPPADDING",    (0,0), (-1,-1), 30),
        ("BOTTOMPADDING", (0,0), (-1,-1), 30),
        ("LEFTPADDING",   (0,0), (-1,-1), 20),
        ("RIGHTPADDING",  (0,0), (-1,-1), 20),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
    ]))
    elems += [sp(4*cm), pt, sp(0.6*cm)]

    for txt, sty in [
        ("Guía Técnica y de Usuario v1.0", S["portada_sub"]),
        ("Análisis OSINT · Cumplimiento eGov · Brecha Digital · Ciberseguridad", S["portada_sub"]),
        ("Marzo 2026", S["portada_meta"]),
        ("M. Castillo · mybloggingnotes@gmail.com", S["portada_meta"]),
    ]:
        elems.append(Paragraph(txt,
            ParagraphStyle("px", parent=sty,
                           textColor=AZUL if "sub" not in sty.name else AZUL)))
        elems.append(sp(4))

    # Caja de resumen
    elems.append(sp(1*cm))
    resumen_data = [[
        Paragraph(
            "Este documento describe la arquitectura, módulos, fuentes de datos, "
            "metodología y uso del Dashboard de Administración Digital España, "
            "una plataforma OSINT para el análisis del estado de la digitalización "
            "pública y la ciberseguridad en España en el contexto europeo.",
            ParagraphStyle("rb", fontName="Helvetica", fontSize=9.5,
                           textColor=GRIS_DARK, leading=14, alignment=TA_JUSTIFY)
        )
    ]]
    rt = Table(resumen_data, colWidths=[W - 3*cm])
    rt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), AZUL_BG),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LEFTPADDING",   (0,0), (-1,-1), 16),
        ("RIGHTPADDING",  (0,0), (-1,-1), 16),
        ("BOX",           (0,0), (-1,-1), 1, AZUL),
    ]))
    elems.append(rt)
    elems.append(PageBreak())
    return elems

# ── ÍNDICE ─────────────────────────────────────────────────────
def indice():
    elems = []
    elems += h1("Índice / Table of Contents")
    secciones = [
        ("1",  "Introducción / Introduction"),
        ("2",  "Arquitectura del sistema / System Architecture"),
        ("3",  "Dashboards disponibles / Available Dashboards"),
        ("4",  "Módulos del panel / Dashboard Modules"),
        ("5",  "Indicadores visuales / Visual Indicators"),
        ("6",  "Fuentes de datos / Data Sources"),
        ("7",  "Módulo OSINT — Scraper diario"),
        ("8",  "Módulo Ciberseguridad & ENS"),
        ("9",  "Metodología / Methodology"),
        ("10", "Uso de los datos / Data Usage"),
        ("11", "Comandos de operación / Operation Commands"),
        ("12", "Auditoría de fuentes / Source Auditing"),
        ("13", "Glosario / Glossary"),
        ("14", "Preguntas frecuentes / FAQ"),
        ("15", "Vigilancia de Normativa Nueva / Normativa Watch"),
    ]
    toc_data = [["#", "Sección / Section"]]
    for num, titulo in secciones:
        toc_data.append([num, titulo])
    elems.append(tabla(toc_data, col_widths=[1.2*cm, W - 4.2*cm], header_color=AZUL_CLARO))
    elems.append(PageBreak())
    return elems

# ── SECCIÓN 1: Introducción ─────────────────────────────────────
def seccion_intro():
    elems = []
    elems += h1("1. Introducción / Introduction")
    elems.append(body(
        "El <b>Dashboard de Administración Digital España</b> es una plataforma de análisis de "
        "inteligencia abierta (OSINT) que monitoriza el estado de la transformación digital "
        "de las administraciones públicas españolas, su posición relativa en el contexto europeo, "
        "el nivel de cumplimiento del Esquema Nacional de Seguridad (ENS), los incidentes de "
        "ciberseguridad y las tendencias normativas nacionales y de la Unión Europea."
    ))
    elems.append(body_en(
        "The Dashboard Administración Digital España is an open-source intelligence (OSINT) "
        "platform that monitors the digital transformation status of Spanish public administrations, "
        "their relative position in the European context, ENS compliance levels, cybersecurity "
        "incidents and regulatory trends."
    ))
    elems.append(sp(6))
    elems += h2("Objetivos principales")
    elems += bullet([
        "Análisis comparativo del índice DESI (Digital Economy and Society Index) España vs EU",
        "Grado de cumplimiento del ENS por tipo de entidad pública",
        "Monitorización de incidentes gestionados por CCN-CERT e INCIBE",
        "Detección de brechas digitales respecto a la referencia europea",
        "Seguimiento de normativa: BOE, EUR-Lex, NIS2, eIDAS 2.0, AI Act",
        "Ingesta diaria automática de fuentes OSINT estructuradas en CSV",
    ])
    return elems

# ── SECCIÓN 2: Arquitectura ─────────────────────────────────────
def seccion_arquitectura():
    elems = []
    elems += h1("2. Arquitectura del Sistema / System Architecture")
    elems.append(body(
        "El sistema opera en un servidor local ARM (Odroid-C2, Debian/DietPi) y "
        "está compuesto por tres capas funcionales:"
    ))
    elems.append(sp(4))
    arq_data = [
        ["Capa", "Componente", "Descripción"],
        ["Ingestión", "osint_scraper.py", "Scraper RSS + APIs. Genera CSVs diarios en data/"],
        ["Procesamiento", "Pandas / Python stdlib", "Deduplicación, clasificación, filtrado por relevancia"],
        ["Visualización", "Streamlit + Plotly", "Dashboard web interactivo en localhost:8501"],
    ]
    elems.append(tabla(arq_data,
        col_widths=[2.8*cm, 4.5*cm, W - 10.3*cm]))
    elems.append(sp(8))
    elems += h2("Estructura de directorios")
    elems += code([
        "admindash-osint/",
        "├── dashboard.py          ← Dashboard principal Streamlit (6 tabs)",
        "├── osint_scraper.py      ← Scraper OSINT diario",
        "├── setup_scraper.sh      ← Instalador + configuración cron",
        "├── data/",
        "│   ├── osint_YYYY-MM-DD.csv   ← CSVs diarios del scraper",
        "│   ├── .seen_hashes.json      ← Caché de deduplicación (30d)",
        "│   └── .audit_history.json    ← Historial de auditorías (90d)",
        "├── logs/",
        "│   ├── scraper_YYYY-MM-DD.log ← Log diario de ejecución",
        "│   └── audit_alert_*.txt      ← Alertas de umbral superado",
        "└── venv/                      ← Entorno virtual Python",
    ])
    elems.append(sp(6))
    elems += h2("Requisitos del sistema")
    req_data = [
        ["Componente", "Versión mínima", "Notas"],
        ["Python",     "3.10+",          "stdlib: urllib, xml, json, csv, hashlib"],
        ["Streamlit",  "1.28+",          "pip install streamlit"],
        ["Plotly",     "5.x",            "pip install plotly"],
        ["Pandas",     "2.x",            "pip install pandas"],
        ["ReportLab",  "4.x",            "pip install reportlab (generación de guía)"],
        ["Hardware",   "Odroid-C2 ARM",  "512 MB RAM mínimo, 2 GB recomendado"],
        ["SO",         "Debian/DietPi",  "Cualquier Linux con Python 3.10+"],
    ]
    elems.append(tabla(req_data,
        col_widths=[3.5*cm, 3.2*cm, W - 9.7*cm]))
    return elems

# ── SECCIÓN 3: Dashboards disponibles ──────────────────────────
def seccion_dashboards():
    elems = []
    elems += h1("3. Dashboards Disponibles / Available Dashboards")
    dash_data = [
        ["Dashboard", "Archivo", "Contenido"],
        ["Principal integrado", "dashboard.py",
         "6 tabs temáticos — análisis DESI, ciberseguridad, OSINT, cronología, referencias, metodología"],
    ]
    elems.append(tabla(dash_data, col_widths=[3.5*cm, 4*cm, W - 10.5*cm]))
    elems.append(sp(6))
    elems.append(body(
        "El dashboard se actualiza automáticamente al recibir nuevos CSVs en la carpeta "
        "<b>data/</b>. No requiere autenticación para su uso en red local. "
        "Accesible desde cualquier dispositivo en la misma red en <b>http://IP_ODROID:8501</b>."
    ))
    elems.append(body_en(
        "The dashboard auto-updates when new CSVs arrive in the data/ folder. "
        "No authentication required for local network use. "
        "Accessible from any device on the same network at http://ODROID_IP:8501."
    ))
    return elems

# ── SECCIÓN 4: Módulos del panel ────────────────────────────────
def seccion_modulos():
    elems = []
    elems += h1("4. Módulos del Panel / Dashboard Modules")
    elems.append(body(
        "El dashboard está organizado en <b>6 pestañas (tabs)</b> temáticas. "
        "Cada una carga sus propios datos y genera visualizaciones específicas."
    ))
    elems.append(sp(4))
    tabs_data = [
        ["Tab", "Contenido principal", "Fuente de datos"],
        ["📊 Análisis Principal",
         "KPIs DESI, ranking EU, radar dimensiones, evolución eGov, "
         "sectores críticos, brechas, servicios ciudadanos",
         "Datos estáticos (DESI 2023, SEDIA 2024, eGov Benchmark)"],
        ["🔐 Ciberseguridad & ENS",
         "KPIs CCN-CERT, incidentes por año/tipo, cumplimiento ENS, "
         "madurez por entidad, radar amenazas, comparativa EU NIS2, "
         "incidentes notables, retos 2025-2027",
         "CCN-CERT 2024, INCIBE, ENISA, NIS2 Country Assessment"],
        ["🛰 OSINT & Alertas",
         "Métricas de fuentes activas, evolución diaria de capturas, "
         "top fuentes, distribución por categoría, alertas críticas "
         "con enlace directo",
         "CSVs diarios: data/osint_YYYY-MM-DD.csv"],
        ["📅 Línea Cronológica",
         "15 hitos legislativos y estratégicos 1992-2025, "
         "filtro por categoría, gráfico de densidad histórica",
         "Datos curados: leyes, planes, eventos clave"],
        ["📚 Referencias Documentales",
         "15 referencias ordenadas cronológicamente con enlace "
         "a documento oficial o portal web, filtro por tipo ES/EU",
         "DESI, eGov Benchmark, ENS, eIDAS, AI Act, PRTR..."],
        ["⚙️ Metodología",
         "Objetivo, fuentes primarias, proceso de construcción "
         "(7 pasos), limitaciones, stack técnico",
         "Documentación interna"],
    ]
    elems.append(tabla(tabs_data,
        col_widths=[3.8*cm, 6.5*cm, W - 13.3*cm]))
    return elems

# ── SECCIÓN 5: Indicadores visuales ────────────────────────────
def seccion_indicadores():
    elems = []
    elems += h1("5. Indicadores Visuales / Visual Indicators")
    viz_data = [
        ["Tipo de gráfico", "Módulos que lo usan", "Detalle"],
        ["Barras horizontales", "Ranking DESI, sectores ENS, tipos de ataque",
         "Comparación de valores entre categorías ordenadas"],
        ["Barras apiladas", "Incidentes CCN-CERT por año y gravedad",
         "Desglose acumulado con línea total en eje secundario"],
        ["Barras agrupadas", "Brechas España vs EU por área",
         "Comparación directa de dos series por categoría"],
        ["Radar/Spider", "Dimensiones DESI, amenazas ciberseguridad",
         "Perfil multidimensional con hasta 3 series superpuestas"],
        ["Gauge (velocímetro)", "Cumplimiento global eGov, NIS2 Score, SOC",
         "KPI único con zonas de color y umbral marcado"],
        ["Línea temporal", "Evolución eGov 2018-2024, madurez ENS",
         "Series múltiples con marcadores por año"],
        ["Treemap", "Inversión vs cumplimiento por sector",
         "Jerarquía tamaño=inversión, color=cumplimiento"],
        ["Scatter (burbujas)", "Uso vs satisfacción servicios ciudadanos",
         "Tamaño proporcional a usuarios, color a satisfacción"],
        ["Donut (pie)", "Estado ENS global, distribución OSINT por fuente",
         "Distribución proporcional con etiqueta central"],
        ["Tabla interactiva", "OSINT & Alertas — artículos con enlace",
         "Vista filtrable con hipervínculo a artículo original"],
        ["Cronología HTML", "Línea Cronológica",
         "Timeline vertical con badges de categoría y filtro"],
    ]
    elems.append(tabla(viz_data,
        col_widths=[3.8*cm, 5.5*cm, W - 12.3*cm]))
    return elems

# ── SECCIÓN 6: Fuentes de datos ─────────────────────────────────
def seccion_fuentes():
    elems = []
    elems += h1("6. Fuentes de Datos / Data Sources")
    elems += h2("6.1 Datos estructurados estáticos")
    elems.append(body(
        "Los gráficos de los tabs Análisis Principal y Ciberseguridad usan "
        "DataFrames hardcodeados en dashboard.py, actualizados manualmente "
        "con cada publicación oficial de los informes anuales."
    ))
    est_data = [
        ["Fuente", "Tipo", "Periodicidad", "Datos extraídos"],
        ["DESI 2023 — Comisión Europea", "PDF/Web", "Anual",
         "Puntuación 0-100 por país y dimensión (5 dimensiones)"],
        ["eGovernment Benchmark 2023 — CE", "PDF", "Anual",
         "Índice eGov por país, servicios públicos digitales"],
        ["SEDIA / Informe AGE 2024", "PDF/Web", "Anual",
         "Cumplimiento ENS por entidad, inversión, madurez"],
        ["CCN-CERT Informe Ciberamenazas 2024","PDF", "Anual",
         "Incidentes por año, gravedad, tipo de ataque"],
        ["INCIBE Informe Anual 2024", "PDF", "Anual",
         "Avisos, vulnerabilidades, sectores afectados"],
        ["ENISA Threat Landscape 2024", "PDF", "Anual",
         "Amenazas EU, probabilidad, impacto por vector"],
        ["NIS2 Country Assessment EU", "Web", "Semestral",
         "NIS2 Readiness Score por país EU"],
        ["OBSAE — Estadísticas eGov", "Web/CSV", "Anual",
         "Usuarios por servicio, satisfacción ciudadana"],
    ]
    elems.append(tabla(est_data,
        col_widths=[4.2*cm, 1.8*cm, 2.2*cm, W - 11.2*cm]))
    elems.append(sp(8))
    elems += h2("6.2 Fuentes OSINT dinámicas (scraper diario)")
    elems.append(body(
        "El módulo OSINT consume <b>24 fuentes RSS y 2 APIs públicas</b> "
        "actualizadas diariamente. Ver Sección 7 para detalles del scraper."
    ))
    osint_data = [
        ["Fuente", "Categoría", "Estado"],
        ["CERT-EU Security Advisories", "Ciberseguridad", "✓ Activa"],
        ["CERT-EU Threat Intelligence", "Ciberseguridad", "✓ Activa"],
        ["INCIBE Avisos de Seguridad", "Ciberseguridad", "✓ Activa"],
        ["INCIBE-CERT Vulnerabilidades", "Ciberseguridad", "✓ Activa"],
        ["Administración Digital (administracion.gob.es)", "Admin. Digital", "✓ Activa"],
        ["PAe — Administración Electrónica", "Admin. Digital", "✓ Activa"],
        ["Observatorio OBSAE", "Estadísticas eGov", "✓ Activa"],
        ["datos.gob.es — Blog", "Datos Abiertos", "✓ Activa"],
        ["datos.gob.es — Noticias", "Datos Abiertos", "✓ Activa"],
        ["EC Digital Strategy News", "Política Digital EU", "✓ Activa"],
        ["La Moncloa — Noticias de Gobierno", "Admin. Digital", "✓ Activa"],
        ["BOE — Disposiciones Generales", "Normativa ES", "✓ Activa"],
        ["BOE — Últimas disposiciones (semana)", "Normativa ES", "✓ Activa"],
        ["Krebs on Security", "Ciber. Internacional", "✓ Activa"],
        ["The Hacker News", "Ciber. Internacional", "✓ Activa"],
        ["Bleeping Computer", "Ciber. Internacional", "✓ Activa"],
        ["Securelist (Kaspersky ICS/APT)", "Ciber. Internacional", "✓ Activa"],
        ["CISA Alerts (US-CERT)", "Ciber. Internacional", "✓ Activa"],
        ["CISA Known Exploited Vulnerabilities", "Ciber. Internacional", "✓ Activa"],
        ["Dark Reading", "Ciber. Internacional", "✓ Activa"],
        ["SANS Internet Stormcast", "Ciber. Internacional", "✓ Activa"],
        ["BOE API REST (sumario diario)", "Normativa ES", "✓ API"],
        ["datos.gob.es CKAN API", "Datos Abiertos", "✓ API"],
    ]
    elems.append(tabla(osint_data,
        col_widths=[6.5*cm, 3.8*cm, 2*cm]))
    return elems

# ── SECCIÓN 7: Scraper OSINT ────────────────────────────────────
def seccion_scraper():
    elems = []
    elems += h1("7. Módulo OSINT — Scraper Diario")
    elems.append(body(
        "El scraper <b>osint_scraper.py</b> se ejecuta diariamente a las 06:00h "
        "mediante cron y genera un CSV estructurado con los artículos captados "
        "en el periodo de 24 horas. Opera exclusivamente con la librería estándar "
        "de Python (sin dependencias externas críticas)."
    ))
    elems.append(sp(4))
    elems += h2("Flujo de procesamiento")
    elems += bullet([
        "Descarga RSS de las 24 fuentes configuradas (timeout 15s por fuente)",
        "Parsea RSS 2.0 y Atom — tolerante a fallos por fuente",
        "Clasifica severidad por palabras clave (Crítica / Alta / Media / Info)",
        "Filtra por relevancia: solo artículos relacionados con el ámbito del dashboard",
        "Deduplica usando hash MD5(título+URL) con caché de 30 días",
        "Consulta BOE API REST para el sumario del día",
        "Consulta datos.gob.es CKAN API para datasets recientes",
        "Genera data/osint_YYYY-MM-DD.csv con 7 columnas",
        "Ejecuta auditoría automática si el ratio de fuentes OK < 60%",
    ])
    elems.append(sp(4))
    elems += h2("Formato del CSV generado")
    csv_data = [
        ["Columna", "Tipo", "Descripción", "Ejemplo"],
        ["date",     "date",   "Fecha de publicación",    "2026-03-09"],
        ["title",    "str",    "Título (máx. 200 chars)", "CCN-CERT alerta sobre..."],
        ["source",   "str",    "Nombre de la fuente",     "INCIBE Avisos de Seguridad"],
        ["category", "str",    "Categoría temática",      "Ciberseguridad"],
        ["url",      "str",    "Enlace al artículo",      "https://incibe.es/..."],
        ["summary",  "str",    "Resumen (máx. 300 chars)","Se han detectado..."],
        ["severity", "str",    "Crítica/Alta/Media/Info", "Alta"],
    ]
    elems.append(tabla(csv_data,
        col_widths=[2.2*cm, 1.4*cm, 4.8*cm, W - 11.4*cm]))
    elems.append(sp(6))
    elems += h2("Palabras clave de clasificación de severidad")
    sev_data = [
        ["Severidad", "Palabras clave (muestra)"],
        ["Crítica", "ransomware, zero-day, APT, exfiltración masiva, paralización, cifrado sistemas"],
        ["Alta",    "alerta, vulnerabilidad, exploit, malware, phishing, brecha, intrusión, DDoS"],
        ["Media",   "riesgo, advertencia, parche, boletín, aviso, recomendación"],
        ["Info",    "(resto de artículos que superan el filtro de relevancia)"],
    ]
    elems.append(tabla(sev_data, col_widths=[2.2*cm, W - 5.2*cm]))
    return elems

# ── SECCIÓN 8: Ciberseguridad & ENS ────────────────────────────
def seccion_ciber():
    elems = []
    elems += h1("8. Módulo Ciberseguridad & ENS")
    elems.append(body(
        "El tab <b>🔐 Ciberseguridad & ENS</b> integra datos de las principales "
        "fuentes de inteligencia de ciberseguridad pública española y europea "
        "para ofrecer una visión 360° del estado de seguridad de las AA.PP."
    ))
    elems.append(sp(4))
    kpi_data = [
        ["KPI", "Valor 2024", "Fuente"],
        ["Incidentes gestionados CCN-CERT", "97.663", "CCN-CERT Informe 2024"],
        ["Incidentes críticos", "872", "CCN-CERT Informe 2024"],
        ["Entidades ENS certificadas (media)", "38%", "SEDIA / Informe ENS 2024"],
        ["Ayuntamientos < 20k con ENS adecuado", "9%", "SEDIA / Informe ENS 2024"],
        ["NIS2 Readiness Score España", "63 / 100", "NIS2 Country Assessment EU"],
        ["Puestos de ciberseguridad sin cubrir (púb.)", "24.000", "INCIBE / ENISA 2024"],
        ["Entidades con SOC activo", "31%", "CCN-CERT / OBSAE"],
        ["Ranking EU NIS2 España", "#6 / 11 analizados", "NIS2 Country Assessment EU"],
    ]
    elems.append(tabla(kpi_data, col_widths=[6*cm, 3*cm, W - 12*cm]))
    elems.append(sp(6))
    elems += h2("Sectores más afectados (incidentes graves 2024)")
    sec_data = [
        ["Sector", "Incidentes", "% Graves", "Tiempo resp."],
        ["Sanidad",              "1.842", "18%", "6h"],
        ["Administración Central","1.234","22%", "4h"],
        ["Educación",            "987",  "12%", "12h"],
        ["Transporte",           "743",  "15%", "8h"],
        ["Energía",              "621",  "21%", "3h"],
        ["Justicia",             "412",  "19%", "9h"],
        ["Telecomunicaciones",   "378",  "11%", "7h"],
        ["Agua / Saneamiento",   "201",  "24%", "14h"],
        ["Defensa",              "156",  "31%", "2h"],
    ]
    elems.append(tabla(sec_data,
        col_widths=[4.5*cm, 2.5*cm, 2.5*cm, W - 12.5*cm]))
    return elems

# ── SECCIÓN 9: Metodología ──────────────────────────────────────
def seccion_metodologia():
    elems = []
    elems += h1("9. Metodología / Methodology")
    elems.append(body(
        "El dashboard combina dos capas de datos: <b>datos estructurados estáticos</b> "
        "(extraídos manualmente de informes oficiales) y <b>datos dinámicos OSINT</b> "
        "(capturados automáticamente cada día por el scraper)."
    ))
    elems.append(sp(4))
    pasos = [
        ("1", "Recopilación OSINT",
         "Scraping RSS + APIs públicas. 24 fuentes, ciclo diario 06:00h. "
         "Almacenado en CSVs con formato: date, title, source, category, url, summary, severity."),
        ("2", "Extracción de métricas estáticas",
         "Lectura de informes PDF (DESI, eGov Benchmark, SEDIA, CCN-CERT) "
         "para extraer puntuaciones por dimensión, país y sector."),
        ("3", "Normalización",
         "Los índices heterogéneos (0-1, 0-100, porcentajes) se normalizan "
         "a escala 0-100 para comparabilidad. DataFrames Pandas."),
        ("4", "Cálculo de brechas",
         "Brecha = Referencia EU (P75) – España. Se usa el percentil 75 "
         "como referencia (no la media) para un nivel de exigencia mayor."),
        ("5", "Clasificación de severidad OSINT",
         "Cada artículo se clasifica automáticamente por palabras clave "
         "en título+resumen: Crítica / Alta / Media / Info."),
        ("6", "Deduplicación",
         "Hash MD5(título+URL) con caché JSON de 30 días. "
         "Evita artículos repetidos entre ejecuciones diarias."),
        ("7", "Visualización",
         "Plotly Express + Graph Objects con template plotly_dark. "
         "Barras, radar, gauge, treemap, scatter, donut, líneas temporales."),
    ]
    paso_data = [["#", "Paso", "Descripción"]]
    for num, titulo, desc in pasos:
        paso_data.append([num, titulo, desc])
    elems.append(tabla(paso_data, col_widths=[0.8*cm, 3.5*cm, W - 7.3*cm]))
    elems.append(sp(6))
    elems += h2("Limitaciones")
    elems += bullet([
        "Los datos DESI y eGov Benchmark son anuales — no reflejan cambios infra-anuales",
        "Los porcentajes de cumplimiento sectorial son estimaciones basadas en informes públicos, no auditorías independientes",
        "La brecha vs EU usa P75 como referencia ideal, lo que puede sobreestimar el retraso relativo",
        "El módulo OSINT depende de la calidad y estructura de los CSVs generados",
        "Los datos de satisfacción ciudadana proceden de encuestas OBSAE con limitaciones muestrales",
        "CCN-CERT bloquea el acceso automatizado a sus RSS — se usan fuentes alternativas equivalentes",
    ])
    return elems

# ── SECCIÓN 10: Uso de los datos ────────────────────────────────
def seccion_uso():
    elems = []
    elems += h1("10. Uso de los Datos / Data Usage")
    elems.append(body("Los datos del dashboard son adecuados para:"))
    elems += bullet([
        "Seguimiento del estado de la transformación digital de las AA.PP. españolas",
        "Análisis comparativo de posición España vs EU en digitalización y ciberseguridad",
        "Detección temprana de escaladas en incidentes de ciberseguridad por sector",
        "Monitorización de normativa: BOE, EUR-Lex, NIS2, eIDAS 2.0, AI Act",
        "Input para análisis de riesgo y comunicación estratégica en sector público",
        "Investigación académica — datos exportables en CSV",
    ])
    elems.append(sp(6))
    elems.append(Paragraph(
        "⚠ No recomendado para toma de decisiones operativas críticas sin verificación "
        "adicional de fuentes primarias, ni como única fuente de inteligencia en "
        "situaciones de alta consecuencia.",
        S["alert"]
    ))
    elems.append(sp(4))
    elems.append(body(
        "Se recomienda citar como: <b>Dashboard Administración Digital España · "
        "M. Castillo · mybloggingnotes@gmail.com · 2026</b>"
    ))
    return elems

# ── SECCIÓN 11: Comandos de operación ──────────────────────────
def seccion_comandos():
    elems = []
    elems += h1("11. Comandos de Operación / Operation Commands")
    elems += h2("Lanzar el dashboard")
    elems += code([
        "cd ~/admindash-osint",
        "source venv/bin/activate",
        "streamlit run dashboard.py",
        "# Acceso red local:",
        "streamlit run dashboard.py --server.address 0.0.0.0 --server.port 8501",
    ])
    elems.append(sp(6))
    elems += h2("Ejecutar el scraper OSINT")
    cmd_data = [
        ["Comando", "Acción"],
        ["python3 osint_scraper.py", "Ejecución normal — genera CSV del día"],
        ["python3 osint_scraper.py --test", "Modo test: verbose, sin guardar ni modificar caché"],
        ["python3 osint_scraper.py --all", "Guardar todos los artículos sin filtro de relevancia"],
        ["python3 osint_scraper.py --fuentes", "Listar las 24 fuentes configuradas"],
        ["python3 osint_scraper.py --audit", "Auditoría manual de todas las fuentes"],
        ["python3 osint_scraper.py --trend", "Tendencia histórica de auditorías (90 días)"],
        ["python3 osint_scraper.py --threshold 0.7", "Cambiar umbral de alerta al 70%"],
        ["python3 osint_scraper.py --purge 60", "Purgar CSVs con más de 60 días"],
    ]
    elems.append(tabla(cmd_data, col_widths=[6*cm, W - 9*cm]))
    elems.append(sp(6))
    elems += h2("Configuración cron (automático)")
    elems += code([
        "# Ver cron actual:",
        "crontab -l",
        "",
        "# Línea instalada por setup_scraper.sh:",
        "0 6 * * * cd ~/admindash-osint && venv/bin/python3 osint_scraper.py >> logs/scraper.log 2>&1",
        "",
        "# Ver logs en tiempo real:",
        "tail -f logs/scraper.log",
    ])
    return elems

# ── SECCIÓN 12: Auditoría ───────────────────────────────────────
def seccion_auditoria():
    elems = []
    elems += h1("12. Auditoría de Fuentes / Source Auditing")
    elems.append(body(
        "El sistema incluye un módulo de <b>autoauditoría automática</b> que verifica "
        "la disponibilidad de todas las fuentes RSS en cada ejecución. Si el ratio de "
        "fuentes OK cae por debajo del umbral configurado (60% por defecto), se "
        "dispara automáticamente una auditoría completa y se genera un fichero de alerta."
    ))
    elems.append(sp(4))
    aud_data = [
        ["Parámetro", "Valor por defecto", "Descripción"],
        ["SOURCES_OK_THRESHOLD", "0.60 (60%)",
         "Porcentaje mínimo de fuentes OK antes de disparar alerta"],
        ["AUDIT_TTL_DAYS", "90 días",
         "Días de retención del historial de auditorías"],
        ["HASH_TTL_DAYS", "30 días",
         "Días de retención del caché de deduplicación"],
        ["Archivo historial", "data/.audit_history.json",
         "Historial de ejecuciones con fecha, ratio OK y fuentes caídas"],
        ["Archivo alerta", "logs/audit_alert_YYYY-MM-DD.txt",
         "Generado cuando se supera el umbral — lista fuentes caídas"],
    ]
    elems.append(tabla(aud_data, col_widths=[4*cm, 3*cm, W - 10*cm]))
    elems.append(sp(6))
    elems += h2("Ejemplo de salida — tendencia histórica (--trend)")
    elems += code([
        "================================================================",
        "  HISTORIAL DE AUDITORÍAS (7 registros)",
        "================================================================",
        "  2026-03-03  [████████████░░░░░░░░]  12/24 (50%)  ⚠ ALERTA",
        "  2026-03-04  [████████████████░░░░]  16/24 (67%)       OK",
        "  2026-03-05  [██████████████████░░]  18/24 (75%)       OK",
        "  2026-03-06  [██████████████████░░]  18/24 (75%)       OK",
        "  2026-03-07  [████████████████████]  20/24 (83%)       OK",
        "  2026-03-08  [████████████████████]  20/24 (83%)       OK",
        "  2026-03-09  [████████████████████]  20/24 (83%)       OK",
        "  Media disponibilidad: 75.4%",
        "  Días con alerta:       1 / 7",
        "  Umbral configurado:   60%",
        "================================================================",
    ])
    return elems

# ── SECCIÓN 13: Glosario ────────────────────────────────────────
def seccion_glosario():
    elems = []
    elems += h1("13. Glosario / Glossary")
    glos_data = [
        ["Término / Term", "Definición ES", "EN"],
        ["OSINT", "Inteligencia de fuentes abiertas", "Open Source Intelligence"],
        ["DESI", "Índice de Economía y Sociedad Digital EU (0-100)", "Digital Economy and Society Index"],
        ["ENS", "Esquema Nacional de Seguridad — marco legal ciberseguridad AA.PP.", "National Security Framework (Spain)"],
        ["NIS2", "Directiva EU de seguridad de redes e información (2022)", "Network and Information Security Directive 2"],
        ["eIDAS 2.0", "Reglamento EU de identidad digital y servicios de confianza", "EU Digital Identity Regulation"],
        ["AI Act", "Reglamento EU de inteligencia artificial (2024/1689)", "EU Artificial Intelligence Act"],
        ["CCN-CERT", "Centro de respuesta a incidentes del Centro Criptológico Nacional", "National Cryptologic Centre CERT (Spain)"],
        ["INCIBE", "Instituto Nacional de Ciberseguridad de España", "National Cybersecurity Institute (Spain)"],
        ["ENISA", "Agencia de la UE para la Ciberseguridad", "EU Agency for Cybersecurity"],
        ["CISA", "Agencia de Ciberseguridad e Infraestructura EEUU", "US Cybersecurity and Infrastructure Security Agency"],
        ["SOC", "Centro de operaciones de seguridad", "Security Operations Center"],
        ["APT", "Amenaza persistente avanzada (ciberataque estatal)", "Advanced Persistent Threat"],
        ["RSS", "Protocolo de sindicación de contenido web", "Really Simple Syndication"],
        ["Brecha digital", "Diferencia en puntos porcentuales España vs referencia EU (P75)", "Digital gap vs EU P75 benchmark"],
        ["Severidad", "Clasificación de criticidad: Crítica/Alta/Media/Info", "Criticality classification"],
        ["Hash MD5", "Huella digital para deduplicación de artículos", "Deduplication fingerprint"],
        ["mtime", "Fecha de modificación del archivo (timestamp del sistema)", "File modification timestamp"],
    ]
    elems.append(tabla(glos_data, col_widths=[3.2*cm, 6*cm, W - 12.2*cm]))
    return elems

# ── SECCIÓN 14: FAQ ─────────────────────────────────────────────
def seccion_faq():
    elems = []
    elems += h1("14. Preguntas Frecuentes / FAQ")

    faqs = [
        ("¿Con qué frecuencia se actualizan los datos OSINT?",
         "El scraper se ejecuta diariamente a las 06:00h mediante cron. El dashboard "
         "refleja siempre el estado del último CSV generado. Los datos estáticos "
         "(DESI, ENS, CCN-CERT) se actualizan manualmente con cada informe anual."),
        ("¿Qué ocurre si el scraper no encuentra artículos relevantes?",
         "El módulo OSINT muestra un aviso informativo y el resto del dashboard sigue "
         "funcionando con normalidad. Los datos estáticos de los otros tabs no se ven "
         "afectados."),
        ("¿Por qué algunas fuentes RSS fallan?",
         "Los portales institucionales españoles (CCN-CERT, INCIBE, ENISA) cambian sus "
         "URLs RSS con frecuencia o bloquean scrapers con 403. El sistema dispara una "
         "auditoría automática cuando el ratio de fuentes OK baja del 60%. Revisa "
         "logs/audit_alert_*.txt para ver las URLs caídas."),
        ("¿Cómo añado una fuente RSS nueva?",
         "Edita el array RSS_SOURCES en osint_scraper.py añadiendo un diccionario con "
         "name, url, category y default_severity. En la siguiente ejecución diaria "
         "la fuente quedará activa automáticamente."),
        ("¿Un índice de cumplimiento ENS alto garantiza seguridad real?",
         "No. El índice refleja el porcentaje de entidades con certificación o "
         "adecuación formal al ENS. La seguridad operativa real depende de factores "
         "adicionales como la madurez del SOC, la formación del personal y la "
         "gestión de incidentes."),
        ("¿Se conservan los CSVs indefinidamente?",
         "Por defecto el scraper purga CSVs con más de 30 días. Puedes modificar "
         "este valor con el argumento --purge N al ejecutar el scraper."),
        ("¿Puedo usar los datos para investigación?",
         "Sí. Los datos en CSV son adecuados para análisis estadístico, series "
         "temporales y modelos predictivos. Se recomienda citar: "
         "Dashboard Administración Digital España · M. Castillo · "
         "mybloggingnotes@gmail.com · 2026"),
        ("¿Cómo accedo al dashboard desde otro dispositivo en la red local?",
         "Lanza el dashboard con: streamlit run dashboard.py --server.address 0.0.0.0 "
         "--server.port 8501. Accede desde cualquier dispositivo en la misma red "
         "en http://IP_ODROID:8501 (la IP del Odroid-C2)."),
    ]

    for pregunta, respuesta in faqs:
        elems.append(KeepTogether([
            Paragraph(f"<b>▸ {pregunta}</b>", S["h3"]),
            Paragraph(respuesta, S["body"]),
            sp(4),
        ]))

    return elems

# ── ÚLTIMA CAPTURA (inyectada dinámicamente) ────────────────────
def seccion_ultima_captura():
    elems = []
    elems += h1("Anexo: Estado de la Última Captura OSINT")

    # Detectar último CSV en data/
    data_dir = "data"
    ultima_fecha = "No disponible"
    ultimo_csv   = "No encontrado"
    n_articulos  = 0
    fuentes_csv  = []

    import glob, csv as csv_mod
    csvs = sorted(glob.glob(f"{data_dir}/osint_*.csv"))
    if csvs:
        ultimo_csv = os.path.basename(csvs[-1])
        ultima_fecha = ultimo_csv.replace("osint_","").replace(".csv","")
        try:
            with open(csvs[-1], newline="", encoding="utf-8") as f:
                reader = csv_mod.DictReader(f)
                rows = list(reader)
                n_articulos = len(rows)
                fuentes_csv = list({r.get("source","") for r in rows if r.get("source")})
        except Exception:
            pass
    else:
        # Fallback si no hay CSVs (entorno de generación)
        ultima_fecha = datetime.now().strftime("%Y-%m-%d")
        ultimo_csv   = f"osint_{ultima_fecha}.csv (pendiente de primera ejecución)"

    ts_gen = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cap_data = [
        ["Campo", "Valor"],
        ["Archivo CSV más reciente",       ultimo_csv],
        ["Fecha de última captura",        ultima_fecha],
        ["Artículos en último CSV",        str(n_articulos) if n_articulos else "—"],
        ["Fuentes con datos en último CSV",str(len(fuentes_csv)) if fuentes_csv else "—"],
        ["Fecha de generación de esta guía", ts_gen],
        ["Generado por",                   "M. Castillo · mybloggingnotes@gmail.com"],
        ["Versión del dashboard",          "v1.0 · Marzo 2026"],
    ]
    elems.append(tabla(cap_data, col_widths=[5.5*cm, W - 8.5*cm]))

    if fuentes_csv:
        elems.append(sp(6))
        elems += h2("Fuentes con datos en el último CSV")
        for f in sorted(fuentes_csv):
            elems.append(Paragraph(f"• {f}", S["bullet"]))

    return elems

# ── SECCIÓN 15: Vigilancia de Normativa Nueva ──────────────────
def seccion_normativa():
    elems = []
    elems += h1("15. Vigilancia de Normativa Nueva / Normativa Watch")
    elems.append(body(
        "El módulo <b>normativa_watch.py</b> es un componente independiente que "
        "analiza los CSVs generados por el scraper diario, detecta automáticamente "
        "documentos que parecen normativa relevante (disposiciones BOE, reglamentos "
        "EU, directivas, instrucciones técnicas) y los presenta en el dashboard "
        "como candidatos para incorporar a las Referencias Documentales. "
        "No modifica ningún archivo existente del proyecto."
    ))
    elems.append(sp(4))

    elems += h2("15.1 Arquitectura — módulo completamente independiente")
    elems += code([
        "admindash-osint/",
        "├── dashboard.py          ← NO se modifica (solo lee el CSV)",
        "├── osint_scraper.py      ← NO se modifica",
        "├── normativa_watch.py    ← NUEVO — detector de normativa",
        "├── normativa_alert.py    ← NUEVO — alertas por email",
        "├── setup_normativa.sh    ← NUEVO — instalador del cron",
        "└── data/",
        "    └── normativa_nuevas.csv  ← generado por normativa_watch",
    ])
    elems.append(sp(6))

    elems += h2("15.2 Flujo de trabajo")
    flujo_data = [
        ["Hora", "Proceso", "Resultado"],
        ["06:00h", "osint_scraper.py (cron)",
         "Genera data/osint_YYYY-MM-DD.csv con artículos del día"],
        ["08:06h", "normativa_watch.py (cron)",
         "Lee CSVs, filtra normativa, escribe data/normativa_nuevas.csv"],
        ["08:06h", "normativa_alert.py (si procede)",
         "Envía email si hay normativa de severidad Alta o Crítica"],
        ["Cualquier hora", "Dashboard tab Referencias",
         "Muestra panel con candidatas pendientes de revisión"],
        ["Manual", "Tú — revisión humana",
         "Editas normativa_nuevas.csv: revisado=SI/NO"],
    ]
    elems.append(tabla(flujo_data, col_widths=[2.5*cm, 4.5*cm, W - 10*cm]))
    elems.append(sp(6))

    elems += h2("15.3 Qué significa «Pendiente de revisión»")
    elems.append(body(
        "El sistema no añade normativa automáticamente a las Referencias Documentales "
        "porque eso requiere criterio editorial. «Pendiente de revisión» significa "
        "que el módulo detectó un documento que parece normativa relevante, pero "
        "<b>eres tú quien decide</b> si merece quedarse en el dashboard de forma permanente."
    ))
    elems.append(sp(4))
    decision_data = [
        ["Valor columna 'revisado'", "Significado", "Efecto en dashboard"],
        ['""  (vacío)',
         "Pendiente — no revisado todavía",
         "Aparece en el panel de candidatas"],
        ['"SI"',
         "Aprobado — lo añades a referencias[]",
         "Desaparece del panel (ya está en Referencias)"],
        ['"NO"',
         "Descartado — no es relevante",
         "Desaparece del panel sin añadir"],
    ]
    elems.append(tabla(decision_data,
        col_widths=[3.5*cm, 5*cm, W - 11.5*cm]))
    elems.append(sp(4))
    elems.append(body(
        "Para incorporar una candidata aprobada a las Referencias Documentales, "
        "edita el array <b>referencias[]</b> en dashboard.py añadiendo el bloque "
        "correspondiente (ver Sección 11 — Comandos de Operación)."
    ))
    elems.append(sp(6))

    elems += h2("15.4 Palabras clave de detección")
    elems.append(body(
        "normativa_watch.py usa tres criterios combinados para clasificar "
        "un artículo como normativa:"
    ))
    kw_data = [
        ["Criterio", "Ejemplos"],
        ["Tipo de disposición",
         "Real Decreto, Orden Ministerial, Reglamento (UE), Directiva (UE), "
         "Ley Orgánica, Resolución, Circular, Instrucción Técnica"],
        ["Ámbito de interés",
         "ENS, eIDAS, NIS2, DORA, AI Act, RGPD, administración electrónica, "
         "identidad digital, EUDIW, interoperabilidad, datos abiertos, PRTR"],
        ["Fuente conocida",
         "BOE, EUR-Lex, SEDIA, PAe, INCIBE, CCN, Comisión Europea, "
         "La Moncloa, Congreso, Senado"],
    ]
    elems.append(tabla(kw_data, col_widths=[4*cm, W - 7*cm]))
    elems.append(sp(6))

    elems += h2("15.5 Comandos del módulo")
    cmd_data = [
        ["Comando", "Acción"],
        ["python3 normativa_watch.py",
         "Ejecución normal — escanea últimos 2 días de CSVs"],
        ["python3 normativa_watch.py --test",
         "Modo test: muestra candidatas sin guardar ni enviar email"],
        ["python3 normativa_watch.py --dias 7",
         "Escanear últimos 7 días (útil tras un periodo sin ejecutar)"],
        ["python3 normativa_watch.py --reset",
         "Limpiar caché — fuerza redetección de todo"],
        ["python3 normativa_alert.py --test",
         "Test de conexión SMTP + envío de email de prueba"],
    ]
    elems.append(tabla(cmd_data, col_widths=[5.5*cm, W - 8.5*cm]))
    elems.append(sp(6))

    elems += h2("15.6 Configuración del email de alertas")
    elems.append(body(
        "Las alertas por email se envían cuando se detecta normativa de severidad "
        "<b>Alta</b> o <b>Crítica</b>. Usa exclusivamente <b>smtplib</b> "
        "(librería estándar Python — sin dependencias externas). "
        "Compatible con Gmail mediante App Password."
    ))
    elems.append(sp(4))
    elems.append(Paragraph(
        "⚠ Nunca guardes la contraseña directamente en el código. "
        "Usa siempre variables de entorno.",
        S["alert"]
    ))
    elems.append(sp(4))

    elems += h2("Paso 1 — Crear App Password en Gmail")
    elems += bullet([
        "Accede a: https://myaccount.google.com/apppasswords",
        "Requiere verificación en 2 pasos activada en la cuenta",
        "Nombre de la app: AdminDash (o cualquier nombre)",
        "Gmail genera una contraseña de 16 caracteres — cópiala",
    ])
    elems.append(sp(4))

    elems += h2("Paso 2 — Configurar variables de entorno en el Odroid")
    elems += code([
        "# Añadir a ~/.bashrc del usuario dietpi:",
        'echo \'export NORMATIVA_EMAIL_FROM="tucuenta@gmail.com"\' >> ~/.bashrc',
        'echo \'export NORMATIVA_EMAIL_PASS="abcd efgh ijkl mnop"\' >> ~/.bashrc',
        'echo \'export NORMATIVA_EMAIL_TO="mybloggingnotes@gmail.com"\' >> ~/.bashrc',
        "",
        "# Activar sin reiniciar:",
        "source ~/.bashrc",
    ])
    elems.append(sp(4))
    elems.append(Paragraph(
        "⚠ El cron no carga ~/.bashrc automáticamente. Para que las variables "
        "estén disponibles en el cron, añádelas también a ~/.profile o declara "
        "las variables directamente en la línea del crontab (ver paso 3).",
        S["note"]
    ))
    elems.append(sp(4))

    elems += h2("Paso 3 — Opción alternativa: variables en el crontab")
    elems += code([
        "# Editar crontab:",
        "crontab -e",
        "",
        "# Añadir las variables ANTES de la línea del cron:",
        'NORMATIVA_EMAIL_FROM="tucuenta@gmail.com"',
        'NORMATIVA_EMAIL_PASS="abcd efgh ijkl mnop"',
        'NORMATIVA_EMAIL_TO="mybloggingnotes@gmail.com"',
        "",
        "# Línea del cron (ya instalada por setup_normativa.sh):",
        "6 8 * * * cd ~/admindash-osint && venv/bin/python3 normativa_watch.py >> logs/normativa.log 2>&1",
    ])
    elems.append(sp(4))

    elems += h2("Paso 4 — Test de la conexión email")
    elems += code([
        "cd ~/admindash-osint && source venv/bin/activate",
        "python3 normativa_alert.py --test",
        "",
        "# Salida esperada:",
        "# INFO  Conectando a smtp.gmail.com:587...",
        "# INFO  Conexion SMTP correcta. Credenciales validas.",
        "# INFO  Email de prueba enviado a mybloggingnotes@gmail.com",
    ])
    elems.append(sp(6))

    elems += h2("15.7 Ficheros generados")
    files_data = [
        ["Fichero", "Contenido", "Retención"],
        ["data/normativa_nuevas.csv",
         "Candidatas detectadas con columnas: fecha_deteccion, "
         "fecha_publicacion, titulo, fuente, tipo_normativa, url, "
         "resumen, severidad, revisado",
         "Permanente (edición manual)"],
        ["data/.normativa_seen.json",
         "Caché de hashes para deduplicación entre ejecuciones",
         "90 días (TTL automático)"],
        ["data/.alert_tmp.json",
         "Fichero temporal de paso entre watch y alert. "
         "Se elimina automáticamente tras el envío",
         "Efímero"],
        ["logs/normativa_YYYY-MM-DD.log",
         "Log diario de ejecución del watch",
         "No se purga automáticamente"],
    ]
    elems.append(tabla(files_data,
        col_widths=[4.5*cm, 7*cm, W - 14.5*cm]))
    return elems

# ── CONSTRUCCIÓN DEL PDF ────────────────────────────────────────
def build_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=1.8*cm,
        bottomMargin=1.5*cm,
        title="Guía Técnica y de Usuario — Dashboard Administración Digital España",
        author="M. Castillo · mybloggingnotes@gmail.com",
        subject="Dashboard OSINT Administración Digital España v1.0",
    )

    story = []

    # Portada (sin header/footer)
    story += portada()

    # Resto de páginas con header/footer
    story += indice()
    story += seccion_intro()
    story += seccion_arquitectura()
    story += seccion_dashboards()
    story += seccion_modulos()
    story += seccion_indicadores()
    story += seccion_fuentes()
    story += seccion_scraper()
    story += seccion_ciber()
    story += seccion_metodologia()
    story += seccion_uso()
    story += seccion_comandos()
    story += seccion_auditoria()
    story += seccion_glosario()
    story += [PageBreak()]
    story += seccion_faq()
    story += [PageBreak()]
    story += seccion_normativa()
    story += [PageBreak()]
    story += seccion_ultima_captura()

    # Página final
    story.append(PageBreak())
    story.append(sp(6*cm))
    story.append(tabla([[
        Paragraph(
            "© 2026 M. Castillo · mybloggingnotes@gmail.com<br/>"
            "Dashboard Administración Digital España · Marzo 2026<br/>"
            "Todos los derechos reservados",
            ParagraphStyle("fin", fontName="Helvetica", fontSize=10,
                           textColor=BLANCO, alignment=TA_CENTER, leading=16)
        )
    ]], col_widths=[W - 3*cm]))

    def _first_page(canvas, doc):
        on_page_first(canvas, doc)

    def _later_pages(canvas, doc):
        on_page(canvas, doc)

    doc.build(story,
              onFirstPage=_first_page,
              onLaterPages=_later_pages)
    print(f"✅ PDF generado: {output_path}")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    build_pdf("data/guia_admindash.pdf")
