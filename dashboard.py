import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import glob
import os
import sys
from datetime import datetime as _dt
from pathlib import Path as _Path

st.set_page_config(
    page_title="Dashboard - Administración Digital España",
    layout="wide",
    page_icon="🇪🇸"
)

# ============================================================
# === ESTILOS CSS ===
# ============================================================
st.markdown("""
<style>
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #4fc3f7;
        border-left: 4px solid #4fc3f7;
        padding-left: 0.8rem;
        margin: 1.5rem 0 1rem 0;
    }
    /* Referencias documentales */
    .ref-card {
        background: linear-gradient(135deg, #1a1f2e, #1e2535);
        border: 1px solid #2a3550;
        border-left: 4px solid #4fc3f7;
        border-radius: 8px;
        padding: 0.9rem 1.2rem;
        margin: 0.5rem 0;
    }
    .ref-year {
        display: inline-block;
        background: #0d47a1;
        color: #e3f2fd;
        border-radius: 4px;
        padding: 1px 8px;
        font-size: 0.78rem;
        font-weight: bold;
        margin-right: 8px;
    }
    .ref-tag {
        display: inline-block;
        background: #1b3a2d;
        color: #80cbc4;
        border-radius: 4px;
        padding: 1px 7px;
        font-size: 0.74rem;
        margin-right: 4px;
    }
    .ref-tag-eu {
        background: #2c1f4a;
        color: #ce93d8;
    }
    .ref-tag-es {
        background: #3b1f1f;
        color: #ef9a9a;
    }
    /* Timeline */
    .tl-container {
        position: relative;
        padding: 0 0 0 2.5rem;
        border-left: 3px solid #1e3a5f;
        margin-left: 1.5rem;
    }
    .tl-item {
        position: relative;
        margin-bottom: 1.4rem;
    }
    .tl-dot {
        position: absolute;
        left: -2.95rem;
        top: 0.2rem;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        border: 3px solid #0d47a1;
    }
    .tl-year {
        font-size: 0.78rem;
        font-weight: 800;
        color: #90caf9;
        letter-spacing: 1px;
        margin-bottom: 2px;
    }
    .tl-title {
        font-size: 0.97rem;
        font-weight: 700;
        color: #e3f2fd;
        margin-bottom: 3px;
    }
    .tl-desc {
        font-size: 0.84rem;
        color: #90a4ae;
        line-height: 1.5;
    }
    .tl-badge {
        display: inline-block;
        font-size: 0.72rem;
        padding: 1px 7px;
        border-radius: 10px;
        margin-right: 4px;
        font-weight: 600;
    }
    .badge-ley    { background:#0d3b6e; color:#90caf9; }
    .badge-plan   { background:#1b4332; color:#95d5b2; }
    .badge-eu     { background:#2c1f4a; color:#ce93d8; }
    .badge-hito   { background:#4a2800; color:#ffcc80; }
    .badge-crisis { background:#4a0000; color:#ef9a9a; }
    /* Metodología */
    .meto-box {
        background: #131822;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .meto-step {
        display: flex;
        gap: 1rem;
        margin: 0.7rem 0;
        align-items: flex-start;
    }
    .meto-num {
        background: #0d47a1;
        color: white;
        border-radius: 50%;
        width: 26px;
        height: 26px;
        min-width: 26px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: bold;
    }
    /* Ciberseguridad */
    .ciber-kpi {
        background: linear-gradient(135deg, #1a0a0a, #2a1010);
        border: 1px solid #5a1a1a;
        border-left: 4px solid #ef5350;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.4rem 0;
        text-align: center;
    }
    .ciber-kpi-val {
        font-size: 2rem;
        font-weight: 900;
        color: #ef5350;
        line-height: 1.1;
    }
    .ciber-kpi-label {
        font-size: 0.78rem;
        color: #90a4ae;
        margin-top: 3px;
    }
    .ciber-kpi-delta {
        font-size: 0.82rem;
        color: #ff8a65;
        font-weight: 600;
    }
    .threat-card {
        background: #12191f;
        border: 1px solid #1e3a5f;
        border-left: 4px solid;
        border-radius: 8px;
        padding: 0.8rem 1.1rem;
        margin: 0.4rem 0;
    }
    .ens-badge {
        display: inline-block;
        border-radius: 5px;
        padding: 2px 9px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-right: 6px;
    }
    .ens-alto    { background:#1a3a1a; color:#81c784; }
    .ens-medio   { background:#2a2a10; color:#fff176; }
    .ens-basico  { background:#1a1a3a; color:#90caf9; }
    .ens-nc      { background:#3a1a1a; color:#ef9a9a; }
    .incident-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0.8rem;
        border-bottom: 1px solid #1e2535;
        font-size: 0.88rem;
    }
    .incident-row:hover { background: #151c28; }
    .sev-critica  { color:#ef5350; font-weight:800; }
    .sev-alta     { color:#ff8a65; font-weight:700; }
    .sev-media    { color:#ffd54f; font-weight:600; }
    .sev-baja     { color:#81c784; font-weight:500; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# === DATOS ===
# ============================================================

desi_data = pd.DataFrame({
    "País": ["Dinamarca","Finlandia","Suecia","Países Bajos","Irlanda",
             "Estonia","Austria","Bélgica","Luxemburgo","España",
             "Portugal","Alemania","Francia","Italia","Grecia",
             "Polonia","Rumanía","Bulgaria"],
    "DESI_Score": [69.6,69.2,67.7,65.7,60.0,61.3,55.8,56.0,57.1,56.1,
                   52.6,50.9,51.2,43.9,39.9,44.7,38.1,36.0],
    "Grupo": ["Top","Top","Top","Top","Top","Alto","Medio-Alto","Medio-Alto",
              "Medio-Alto","Medio-Alto","Medio","Medio","Medio","Bajo","Bajo",
              "Bajo","Crítico","Crítico"]
})

dimensiones = pd.DataFrame({
    "Dimensión": ["Conectividad","Capital Humano","Integración Digital",
                  "Servicios Públicos Digitales","Investigación e Innovación"],
    "España":      [62.4, 55.1, 48.7, 71.2, 42.3],
    "Media_EU":    [57.3, 50.8, 52.1, 63.0, 58.9],
    "Objetivo_2030":[80.0, 80.0, 80.0,100.0, 70.0]
})

sectores = pd.DataFrame({
    "Sector": ["Sanidad digital (HCE)","Justicia electrónica","Educación digital",
               "Gestión tributaria (AEAT)","Seguridad Social","Ayuntamientos < 20k hab.",
               "Registro Civil electrónico","Contratación pública","Administración local",
               "Interoperabilidad entre AA.PP."],
    "Cumplimiento_%": [72,58,65,92,88,31,45,78,42,55],
    "Prioridad": ["Alta","Crítica","Alta","Baja","Baja","Crítica","Crítica","Media","Crítica","Alta"],
    "Inversión_M€": [1200,450,890,320,560,210,180,340,290,170]
})

evolucion = pd.DataFrame({
    "Año":      [2018,2019,2020,2021,2022,2023,2024],
    "España":   [44.0,47.2,51.8,55.3,58.1,61.4,64.2],
    "Media_EU": [50.1,52.0,54.3,56.8,58.9,61.0,63.5],
    "Dinamarca":[75.2,77.0,78.5,79.1,80.0,81.3,82.0],
    "Italia":   [30.1,32.5,35.0,37.2,39.8,42.1,44.5]
})

brechas = pd.DataFrame({
    "Área": ["Identidad digital (eIDAS 2.0)","Interoperabilidad transfronteriza",
             "Cloud gubernamental","Ciberseguridad AA.PP.","IA en Administración",
             "Accesibilidad web (WCAG 2.1)","Datos abiertos (Open Data)",
             "Firma electrónica avanzada","Notificaciones electrónicas","5G en zonas rurales"],
    "España_%":        [68,42,55,63,28,71,74,82,79,38],
    "EU_Referencia_%": [75,68,70,72,45,85,80,88,84,62],
    "Brecha_ptos":     [ 7,26,15, 9,17,14, 6, 6, 5,24]
})

servicios_uso = pd.DataFrame({
    "Servicio": ["Declaración Renta (AEAT)","Cl@ve PIN / permanente",
                 "Sede Electrónica SEPE","Notificaciones electrónicas",
                 "Sede SS","Padrón municipal online","Cita previa sanidad",
                 "Registro Civil online","Contratos públicos (PLACE)",
                 "Universidades (Secretaría virtual)"],
    "Usuarios_millones": [22.4,18.7,9.2,14.3,12.1,5.8,8.9,2.1,1.4,3.6],
    "Satisfacción_%":    [78,72,61,68,75,55,63,41,52,67]
})

alert_words = ['alerta','riesgo','crítico','brecha','fallo','vulnerabilidad']

# ============================================================
# === REFERENCIAS DOCUMENTALES ===
# ============================================================
referencias = [
    {
        "año": "2024",
        "tipo": "ES",
        "titulo": "Informe SEDIA 2024 — Secretaría de Estado de Digitalización e IA",
        "descripcion": "Informe anual de estado de la transformación digital de la Administración General del Estado.",
        "url": "https://www.digitales.gob.es/informe-sedia-2024",
        "descargable": True
    },
    {
        "año": "2023",
        "tipo": "EU",
        "titulo": "DESI 2023 — Digital Economy and Society Index",
        "descripcion": "Índice anual de la Comisión Europea que evalúa el desempeño digital de los 27 estados miembros.",
        "url": "https://digital-strategy.ec.europa.eu/en/policies/desi",
        "descargable": True
    },
    {
        "año": "2023",
        "tipo": "ES",
        "titulo": "España Digital 2026 — Plan de Digitalización de AA.PP.",
        "descripcion": "Plan estratégico del Gobierno de España para la digitalización de las administraciones públicas.",
        "url": "https://espanadigital.gob.es",
        "descargable": False
    },
    {
        "año": "2023",
        "tipo": "EU",
        "titulo": "eGovernment Benchmark 2023 — European Commission",
        "descripcion": "Referencia comparativa de servicios de administración electrónica en Europa. Evalúa 36 países.",
        "url": "https://digital-strategy.ec.europa.eu/en/library/egovernment-benchmark-2023",
        "descargable": True
    },
    {
        "año": "2022",
        "tipo": "EU",
        "titulo": "Reglamento eIDAS 2.0 — Identidad Digital Europea",
        "descripcion": "Marco legal europeo para la identidad digital y servicios de confianza. Revisión de eIDAS 2014.",
        "url": "https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:52021PC0281",
        "descargable": True
    },
    {
        "año": "2022",
        "tipo": "ES",
        "titulo": "Plan de Recuperación, Transformación y Resiliencia (PRTR) — Componente 11",
        "descripcion": "Componente de modernización de las AA.PP. del plan de recuperación post-COVID. Inversión: 4.320 M€.",
        "url": "https://planderecuperacion.gob.es/como-funciona/componente-11",
        "descargable": False
    },
    {
        "año": "2022",
        "tipo": "EU",
        "titulo": "Brújula Digital 2030 — Digital Decade Policy Programme",
        "descripcion": "Objetivos de la UE para la transformación digital al 2030: conectividad, competencias, servicios públicos.",
        "url": "https://digital-strategy.ec.europa.eu/en/policies/europes-digital-decade",
        "descargable": False
    },
    {
        "año": "2021",
        "tipo": "ES",
        "titulo": "Esquema Nacional de Seguridad (ENS) — Real Decreto 311/2022",
        "descripcion": "Marco regulatorio de ciberseguridad para sistemas de información de las AA.PP. españolas.",
        "url": "https://www.boe.es/eli/es/rd/2022/05/03/311",
        "descargable": True
    },
    {
        "año": "2021",
        "tipo": "ES",
        "titulo": "Esquema Nacional de Interoperabilidad (ENI) — Actualización 2021",
        "descripcion": "Normativa que regula los criterios de interoperabilidad entre sistemas de las AA.PP.",
        "url": "https://administracion.gob.es/pag_Home/eni.html",
        "descargable": False
    },
    {
        "año": "2020",
        "tipo": "EU",
        "titulo": "Estrategia Europea de Datos — COM(2020) 66",
        "descripcion": "Marco europeo para la gobernanza de datos, espacios de datos sectoriales y datos abiertos.",
        "url": "https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:52020DC0066",
        "descargable": True
    },
    {
        "año": "2020",
        "tipo": "ES",
        "titulo": "Agenda España Digital 2025",
        "descripcion": "Plan estratégico de digitalización del Gobierno con 10 ejes y 50 medidas concretas.",
        "url": "https://www.lamoncloa.gob.es/presidente/actividades/Paginas/2020/espanadigital2025.aspx",
        "descargable": False
    },
    {
        "año": "2019",
        "tipo": "ES",
        "titulo": "Informe COTEC 2019 — Innovación en España",
        "descripcion": "Análisis de capacidades de innovación y digitalización pública y privada en España.",
        "url": "https://cotec.es/publicacion/informe-cotec-2019",
        "descargable": True
    },
    {
        "año": "2016",
        "tipo": "ES",
        "titulo": "Ley 39/2015 — Procedimiento Administrativo Común",
        "descripcion": "Ley que establece la obligatoriedad de la tramitación electrónica para personas jurídicas.",
        "url": "https://www.boe.es/eli/es/l/2015/10/01/39/con",
        "descargable": True
    },
    {
        "año": "2016",
        "tipo": "ES",
        "titulo": "Ley 40/2015 — Régimen Jurídico del Sector Público",
        "descripcion": "Regula las relaciones entre las AA.PP. y el funcionamiento electrónico del sector público.",
        "url": "https://www.boe.es/eli/es/l/2015/10/01/40/con",
        "descargable": True
    },
    {
        "año": "2024",
        "tipo": "EU",
        "titulo": "AI Act — Reglamento de IA de la UE (2024/1689)",
        "descripcion": "Primera regulación mundial de inteligencia artificial con impacto directo en IA usada por AA.PP.",
        "url": "https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=OJ:L_202401689",
        "descargable": True
    },
]

# ============================================================
# === HITOS CRONOLÓGICOS ===
# ============================================================
hitos = [
    {
        "año": "1992",
        "color": "#546e7a",
        "badge_tipo": "badge-ley",
        "badge_txt": "LEY",
        "titulo": "Ley 30/1992 — Primera ventana hacia lo digital",
        "desc": "Introduce el concepto de tramitación electrónica en España por primera vez, aunque sin obligatoriedad ni infraestructura real. Marca el inicio conceptual de la e-administración."
    },
    {
        "año": "2007",
        "color": "#1565c0",
        "badge_tipo": "badge-ley",
        "badge_txt": "LEY",
        "titulo": "Ley 11/2007 — Acceso Electrónico de los Ciudadanos",
        "desc": "Hito fundamental: consagra el derecho de los ciudadanos a relacionarse electrónicamente con la Administración. Obliga a las AA.PP. a ofrecer servicios digitales. Base del modelo actual."
    },
    {
        "año": "2010",
        "color": "#0277bd",
        "badge_tipo": "badge-plan",
        "badge_txt": "PLAN",
        "titulo": "ENI y ENS — Esquemas Nacionales de Interoperabilidad y Seguridad",
        "desc": "Primeros marcos técnicos vinculantes para garantizar que los sistemas de las AA.PP. puedan comunicarse entre sí de forma segura y coherente. Fundamento técnico de la interoperabilidad pública."
    },
    {
        "año": "2015",
        "color": "#6a1b9a",
        "badge_tipo": "badge-eu",
        "badge_txt": "EU",
        "titulo": "eIDAS — Reglamento europeo de Identidad Digital",
        "desc": "La UE establece un marco común para la identificación electrónica y servicios de confianza (firmas, sellos, certificados). España adapta el DNI electrónico y el sistema Cl@ve."
    },
    {
        "año": "2015",
        "color": "#1565c0",
        "badge_tipo": "badge-ley",
        "badge_txt": "LEY",
        "titulo": "Leyes 39 y 40/2015 — Reforma del Procedimiento Administrativo",
        "desc": "Obligan a personas jurídicas y entidades a relacionarse solo electrónicamente con la Administración. Eliminan el papel como canal principal para empresas y autónomos. Gran salto estructural."
    },
    {
        "año": "2018",
        "color": "#558b2f",
        "badge_tipo": "badge-plan",
        "badge_txt": "PLAN",
        "titulo": "Plan de Transformación Digital de la AGE",
        "desc": "El Gobierno lanza el primer plan integral de digitalización de la Administración General del Estado con horizonte 2021. Contempla cloud, datos, ciberseguridad e interoperabilidad."
    },
    {
        "año": "2020",
        "color": "#b71c1c",
        "badge_tipo": "badge-crisis",
        "badge_txt": "CRISIS",
        "titulo": "COVID-19 — Acelerador forzado de la digitalización",
        "desc": "La pandemia colapsa las sedes electrónicas (SEPE, SS) y revela brechas críticas. A la vez actúa como catalizador: se acelera la adopción de cita previa, notificaciones y videconferencia en AA.PP."
    },
    {
        "año": "2020",
        "color": "#1b5e20",
        "badge_tipo": "badge-plan",
        "badge_txt": "PLAN",
        "titulo": "Agenda España Digital 2025",
        "desc": "10 ejes estratégicos, 50 medidas. Incluye digitalización de pymes, conectividad 5G, datos, IA y modernización del sector público. Primer plan integrado en la era post-COVID."
    },
    {
        "año": "2021",
        "color": "#e65100",
        "badge_tipo": "badge-hito",
        "badge_txt": "FONDOS",
        "titulo": "PRTR — 4.320 M€ para modernización de AA.PP. (Componente 11)",
        "desc": "Los fondos europeos Next Generation EU canalizan inversión histórica hacia digitalización pública, refuerzo del ENS, interoperabilidad y formación de empleados públicos."
    },
    {
        "año": "2022",
        "color": "#1565c0",
        "badge_tipo": "badge-plan",
        "badge_txt": "PLAN",
        "titulo": "España Digital 2026 — Plan de Digitalización de las AA.PP.",
        "desc": "Continuación y ampliación del plan anterior. Define indicadores concretos de cumplimiento, arquitectura de referencia de cloud público y hoja de ruta de identidad digital nacional."
    },
    {
        "año": "2022",
        "color": "#6a1b9a",
        "badge_tipo": "badge-eu",
        "badge_txt": "EU",
        "titulo": "Brújula Digital 2030 — Objetivos europeos",
        "desc": "La UE fija metas vinculantes: 100% de servicios públicos clave digitales, identidad digital para todos los ciudadanos, interoperabilidad transfronteriza total. España debe alcanzar estos objetivos."
    },
    {
        "año": "2023",
        "color": "#0277bd",
        "badge_tipo": "badge-hito",
        "badge_txt": "HITO",
        "titulo": "Cl@ve sube a 18,7 millones de usuarios activos",
        "desc": "El sistema de identificación digital unificado consolida su adopción masiva. Se integra en más de 2.000 procedimientos administrativos. Mayor servicio de identidad digital de Europa por usuarios."
    },
    {
        "año": "2024",
        "color": "#6a1b9a",
        "badge_tipo": "badge-eu",
        "badge_txt": "EU",
        "titulo": "eIDAS 2.0 y Cartera de Identidad Digital Europea (EUDIW)",
        "desc": "La UE lanza el marco para la billetera de identidad digital europea. España, junto a Alemania y Francia, forma parte del piloto de implementación POTENTIAL. Objetivo: operativa en 2026."
    },
    {
        "año": "2024",
        "color": "#b71c1c",
        "badge_tipo": "badge-eu",
        "badge_txt": "AI ACT",
        "titulo": "Reglamento de IA de la UE — Impacto en AA.PP.",
        "desc": "Primer marco regulatorio mundial de IA con vigencia directa. Los sistemas de IA usados por AA.PP. para toma de decisiones quedan clasificados como 'alto riesgo'. Implica auditoría y transparencia obligatorias."
    },
    {
        "año": "2025",
        "color": "#1b5e20",
        "badge_tipo": "badge-plan",
        "badge_txt": "OBJETIVO",
        "titulo": "Objetivo: 100% de procedimientos administrativos digitalizados (AGE)",
        "desc": "Meta fijada en España Digital 2026. A fecha de redacción, el porcentaje real se estima en torno al 78% para la AGE, con mayor brecha en administración local (especialmente municipios pequeños)."
    },
]

# ============================================================
# === DATOS CIBERSEGURIDAD ===
# ============================================================

# --- Incidentes gestionados por CCN-CERT (2018-2024) ---
incidentes_anuales = pd.DataFrame({
    "Año":        [2018, 2019, 2020, 2021, 2022, 2023, 2024],
    "Total":      [38192, 42997, 55356, 109452, 118820, 107777, 97663],
    "Críticos":   [  156,   189,   421,    963,   1129,    987,   872],
    "Altos":      [ 2340,  2891,  4812,   9823,  11042,  10234,  9341],
    "Medios":     [12300, 14200, 18900,  38000,  41000,  37800, 34200],
    "Bajos":      [23396, 25717, 31223,  60666,  65649,  58756, 53250],
})

# --- Distribución por tipo de ataque (2024, CCN-CERT) ---
tipos_ataque = pd.DataFrame({
    "Tipo": [
        "Phishing / Ingeniería social",
        "Ransomware",
        "Intrusión / Acceso no autorizado",
        "Malware diverso",
        "DoS / DDoS",
        "Exfiltración de datos",
        "Vulnerabilidades web",
        "Amenaza interna",
        "Supply chain attack",
        "APT (Amenaza Persistente Avanzada)"
    ],
    "Incidentes_2024": [28400, 8200, 12300, 15600, 9800, 4300, 7200, 2100, 1800, 960],
    "Variación_%":     [+12,   +34,   +8,    +5,   +21,   +41,   +3,  -4,   +67,  +28],
    "Impacto": ["Alto","Crítico","Alto","Medio","Medio","Crítico","Medio","Alto","Crítico","Crítico"]
})

# --- Cumplimiento ENS por tipo de entidad (2024) ---
ens_entidades = pd.DataFrame({
    "Entidad":        ["AGE","CCAA","Diputaciones","Ayunt. > 50k","Ayunt. 20-50k",
                       "Ayunt. < 20k","Universidades","Sanidad Pública","Justicia","Fuerzas y Cuerpos"],
    "Certificados_%": [72, 58, 61, 45, 28, 9,  42, 38, 65, 81],
    "Adecuados_%":    [18, 22, 19, 31, 38, 24, 33, 29, 21, 12],
    "No_conformes_%": [10, 20, 20, 24, 34, 67, 25, 33, 14,  7],
    "Categoría_ENS":  ["Alto","Medio","Medio","Medio","Básico","Básico",
                       "Medio","Alto","Alto","Alto"]
})

# --- Evolución madurez ENS (índice 0-100) ---
madurez_ens = pd.DataFrame({
    "Año":   [2019, 2020, 2021, 2022, 2023, 2024],
    "AGE":   [  48,   52,   59,   65,   70,   74],
    "CCAA":  [  35,   38,   43,   49,   55,   60],
    "Local": [  18,   21,   24,   28,   33,   38],
    "Objetivo_2026": [80, 80, 80, 80, 80, 80],
})

# --- Principales amenazas y retos (radar multidimensional) ---
amenazas_radar = pd.DataFrame({
    "Dimensión": [
        "Ransomware AA.PP.", "Phishing ciudadano", "Infraestructuras críticas",
        "Identidad y acceso", "Supply chain", "IA adversarial",
        "Desinformación", "Ciberespionaje"
    ],
    "Probabilidad":  [88, 92, 71, 79, 65, 48, 83, 60],
    "Impacto":       [91, 72, 95, 68, 88, 74, 61, 85],
    "Preparación_ES":[55, 61, 70, 58, 42, 31, 49, 64],
})

# --- Comparativa EU ciberseguridad pública (NIS2 readiness 2024) ---
ciber_eu = pd.DataFrame({
    "País":         ["Estonia","Países Bajos","Finlandia","Alemania","Francia",
                     "España","Portugal","Italia","Polonia","Grecia","Rumanía"],
    "NIS2_Score":   [87, 82, 85, 76, 74, 63, 58, 55, 51, 44, 38],
    "CSIRT_Madurez":[95, 88, 91, 82, 79, 70, 64, 61, 55, 48, 40],
    "Ejercicios_%": [92, 85, 88, 78, 72, 65, 58, 52, 49, 41, 35],
})

# --- Sectores críticos más afectados (incidentes graves 2024) ---
sectores_ciber = pd.DataFrame({
    "Sector":      ["Sanidad","Administración Central","Educación","Transporte",
                    "Energía","Finanzas públicas","Justicia","Telecomunicaciones",
                    "Agua / Saneamiento","Defensa"],
    "Incidentes":  [1842, 1234, 987, 743, 621, 588, 412, 378, 201, 156],
    "Graves_%":    [  18,   22,  12,  15,  21,  14,  19,  11,  24,  31],
    "Tiempo_resp_h":[  6,    4,  12,   8,   3,   5,   9,   7,  14,   2],
})

# --- Incidentes notables AA.PP. España (log de eventos) ---
incidentes_notables = [
    {"fecha":"Ene 2024","org":"Ministerio de Trabajo (SEPE)","tipo":"Ransomware","sev":"Crítica",
     "desc":"Cifrado de sistemas, paralización parcial de servicios durante 5 días. Ryuk/Revil."},
    {"fecha":"Mar 2024","org":"Ayuntamiento de Sevilla","tipo":"Ransomware","sev":"Crítica",
     "desc":"LockBit 3.0 cifra servidores municipales. 1,5 TB de datos exfiltrados. 1.5M€ rescate exigido."},
    {"fecha":"May 2024","org":"Hospital Clínic de Barcelona","tipo":"Ransomware","sev":"Crítica",
     "desc":"RansomHouse afecta sistemas del hospital. Pacientes derivados. Datos clínicos publicados."},
    {"fecha":"Jun 2024","org":"DGT (Dirección Gral. Tráfico)","tipo":"Exfiltración","sev":"Alta",
     "desc":"34M de registros de vehículos y conductores expuestos. Vendidos en foro darknet IntelBroker."},
    {"fecha":"Sep 2024","org":"Tribunal Constitucional","tipo":"DDoS","sev":"Alta",
     "desc":"Campaña DDoS sostenida durante 72h por grupo pro-ruso NoName057(16)."},
    {"fecha":"Oct 2024","org":"Correos","tipo":"Phishing masivo","sev":"Media",
     "desc":"Campaña de smishing suplantando a Correos afecta a +500k ciudadanos."},
    {"fecha":"Nov 2024","org":"AEAT (Agencia Tributaria)","tipo":"Extorsión / Datos","sev":"Alta",
     "desc":"Grupo Trinity reclama 38M€ tras supuesta exfiltración de 560 GB de datos fiscales."},
    {"fecha":"Dic 2024","org":"Red SARA / Interoperabilidad","tipo":"Intrusión","sev":"Alta",
     "desc":"Sondeo de vulnerabilidades detectado en red troncal de comunicaciones entre AA.PP."},
]

# --- Retos y desafíos ENS 2025-2027 ---
retos_ens = [
    {"icono":"🏛","titulo":"Adhesión de la Administración Local",
     "desc":"Más del 67% de ayuntamientos de menos de 20.000 habitantes no ha iniciado el proceso de adecuación al ENS. Brecha estructural entre AA.PP. grandes y pequeñas.",
     "urgencia":"Crítica"},
    {"icono":"🤖","titulo":"IA Adversarial y deepfakes institucionales",
     "desc":"Uso de IA generativa para suplantar identidades de funcionarios, generar documentos falsos y atacar sistemas de verificación. Regulación aún insuficiente.",
     "urgencia":"Emergente"},
    {"icono":"🔗","titulo":"Seguridad en la cadena de suministro (Supply Chain)",
     "desc":"El 67% de los incidentes críticos en 2024 tuvieron origen en un proveedor de software o servicio externo. NIS2 exige diligencia debida en toda la cadena.",
     "urgencia":"Crítica"},
    {"icono":"👁","titulo":"Visibilidad y monitorización continua",
     "desc":"Solo el 31% de las entidades públicas dispone de SOC propio o contratado. La detección tardía amplifica el impacto de los incidentes.",
     "urgencia":"Alta"},
    {"icono":"🎓","titulo":"Brecha de talento en ciberseguridad pública",
     "desc":"Se estiman 24.000 puestos sin cubrir en el sector público español. La retención frente al sector privado es el principal obstáculo.",
     "urgencia":"Alta"},
    {"icono":"🇪🇺","titulo":"Transposición completa de NIS2",
     "desc":"España debe transponer la Directiva NIS2 (plazo: oct 2024, ya superado). El reglamento amplía el ámbito a más de 4.000 entidades adicionales.",
     "urgencia":"Crítica"},
    {"icono":"☁","titulo":"Seguridad en cloud gubernamental",
     "desc":"La migración acelerada a cloud sin arquitecturas de seguridad maduras crea nuevas superficies de ataque. El CCN-CERT trabaja en el marco INES para cloud público.",
     "urgencia":"Alta"},
    {"icono":"🔐","titulo":"Gestión de identidades privilegiadas (PAM)",
     "desc":"El robo de credenciales privilegiadas está detrás del 78% de las intrusiones graves. La implantación de PAM en AA.PP. es inferior al 20%.",
     "urgencia":"Alta"},
]

# ============================================================
# === CABECERA ===
# ============================================================
st.markdown("# 🇪🇸 Dashboard — Administración Digital España")
st.markdown("**Análisis OSINT · Cumplimiento eGov · Brecha Digital · Sectores Críticos**")
st.markdown("---")

# ============================================================
# === TABS PRINCIPALES ===
# ============================================================
tab_main, tab_ciber, tab_osint, tab_crono, tab_refs, tab_meto = st.tabs([
    "📊 Análisis Principal",
    "🔐 Ciberseguridad & ENS",
    "🛰 OSINT & Alertas",
    "📅 Línea Cronológica",
    "📚 Referencias Documentales",
    "⚙️ Metodología"
])

# ============================================================
# ===  TAB 1: ANÁLISIS PRINCIPAL ===
# ============================================================
with tab_main:

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("DESI España 2023",          "56.1 / 100",  "+4.7 vs 2022")
    k2.metric("Ranking EU (27)",            "#10",         "↑2 posiciones")
    k3.metric("Servicios públicos digit.",  "71.2%",       "+8.2% vs EU media")
    k4.metric("Brecha media vs ref. EU",    "-12.3 ptos")
    k5.metric("Sectores críticos",          "5 / 10")

    st.markdown("---")

    # DESI + Radar
    col_a, col_b = st.columns([1.4, 1])
    with col_a:
        st.markdown('<div class="section-title">📊 Ranking DESI 2023 — Unión Europea</div>', unsafe_allow_html=True)
        color_map = {"Top":"#4fc3f7","Alto":"#66bb6a","Medio-Alto":"#aed581",
                     "Medio":"#ffa726","Bajo":"#ef9a9a","Crítico":"#ef5350"}
        fig_desi = px.bar(
            desi_data.sort_values("DESI_Score"),
            x="DESI_Score", y="País", orientation="h",
            color="Grupo", color_discrete_map=color_map,
            text="DESI_Score", template="plotly_dark",
            title="Puntuación DESI por país (0-100)"
        )
        fig_desi.update_traces(textposition="outside", texttemplate="%{text:.1f}")
        fig_desi.add_vline(x=56.1, line_dash="dot", line_color="#ffd54f",
                           annotation_text="🇪🇸 España", annotation_position="top right")
        fig_desi.update_layout(height=540, margin=dict(l=10, r=30, t=50, b=20))
        st.plotly_chart(fig_desi, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-title">🕸 Dimensiones DESI — España vs EU vs 2030</div>', unsafe_allow_html=True)
        cats = dimensiones["Dimensión"].tolist()
        fig_radar = go.Figure()
        for serie, color, fill, dash in [
            ("España",      "#4fc3f7", "rgba(79,195,247,0.2)",  "solid"),
            ("Media_EU",    "#ffa726", "rgba(255,167,38,0.15)", "solid"),
            ("Objetivo_2030","#66bb6a","rgba(102,187,106,0.05)","dot"),
        ]:
            vals = dimensiones[serie].tolist()
            fig_radar.add_trace(go.Scatterpolar(
                r=vals + [vals[0]], theta=cats + [cats[0]],
                fill="toself", name=serie,
                line=dict(color=color, dash=dash),
                fillcolor=fill
            ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            template="plotly_dark", height=460,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            margin=dict(l=20, r=20, t=50, b=60)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")

    # Evolución + Gauge
    col_c, col_d = st.columns([1.6, 1])
    with col_c:
        st.markdown('<div class="section-title">📈 Evolución eGov Index (2018–2024)</div>', unsafe_allow_html=True)
        fig_evol = go.Figure()
        for pais, color in [("España","#4fc3f7"),("Media_EU","#ffa726"),
                             ("Dinamarca","#66bb6a"),("Italia","#ef5350")]:
            fig_evol.add_trace(go.Scatter(
                x=evolucion["Año"], y=evolucion[pais], name=pais,
                mode="lines+markers",
                line=dict(color=color, width=2.5 if pais=="España" else 1.5),
                marker=dict(size=7 if pais=="España" else 5)
            ))
        fig_evol.update_layout(
            template="plotly_dark", height=380,
            yaxis=dict(range=[25,90], title="Puntuación"),
            xaxis=dict(title="Año"),
            legend=dict(orientation="h", y=1.12),
            margin=dict(l=10, r=10, t=60, b=30)
        )
        st.plotly_chart(fig_evol, use_container_width=True)

    with col_d:
        st.markdown('<div class="section-title">🎯 Cumplimiento Global España</div>', unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=64.2,
            delta={"reference":63.5, "valueformat":".1f", "suffix":" vs EU media"},
            title={"text":"España — eGov 2024 (%)", "font":{"size":15}},
            gauge={
                "axis": {"range":[0,100]},
                "bar":  {"color":"#4fc3f7"},
                "steps":[
                    {"range":[0,40],  "color":"#c62828"},
                    {"range":[40,60], "color":"#e65100"},
                    {"range":[60,80], "color":"#1565c0"},
                    {"range":[80,100],"color":"#1b5e20"},
                ],
                "threshold":{"line":{"color":"#ffd54f","width":4},"thickness":0.8,"value":80}
            }
        ))
        fig_gauge.update_layout(template="plotly_dark", height=340,
                                 margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")

    # Sectores críticos
    st.markdown('<div class="section-title">🚨 Sectores Críticos — Grado de Cumplimiento</div>', unsafe_allow_html=True)
    col_e, col_f = st.columns([1.5, 1])

    with col_e:
        color_prio = {"Crítica":"#ef5350","Alta":"#ffa726","Media":"#4fc3f7","Baja":"#66bb6a"}
        ss = sectores.sort_values("Cumplimiento_%")
        bars = [go.Bar(
            x=[r["Cumplimiento_%"]], y=[r["Sector"]], orientation="h",
            marker_color=color_prio.get(r["Prioridad"],"#90a4ae"),
            name=r["Prioridad"], showlegend=False,
            text=f"{r['Cumplimiento_%']}%", textposition="outside"
        ) for _, r in ss.iterrows()]
        for prio, col in color_prio.items():
            bars.append(go.Bar(x=[None], y=[None], orientation="h",
                               marker_color=col, name=prio))
        fig_sec = go.Figure(bars)
        fig_sec.add_vline(x=75, line_dash="dot", line_color="#ffd54f",
                          annotation_text="Umbral mínimo (75%)")
        fig_sec.update_layout(template="plotly_dark", height=430,
                               xaxis=dict(range=[0,110], title="Cumplimiento (%)"),
                               margin=dict(l=10, r=40, t=30, b=20))
        st.plotly_chart(fig_sec, use_container_width=True)

    with col_f:
        fig_inv = px.treemap(
            sectores, path=["Prioridad","Sector"], values="Inversión_M€",
            color="Cumplimiento_%",
            color_continuous_scale=["#c62828","#ffa726","#66bb6a"],
            range_color=[25,95], template="plotly_dark",
            title="Inversión estimada vs cumplimiento"
        )
        fig_inv.update_layout(height=420, margin=dict(l=5,r=5,t=40,b=5))
        st.plotly_chart(fig_inv, use_container_width=True)

    st.markdown("---")

    # Brechas
    st.markdown('<div class="section-title">🔍 Brechas Digitales — España vs Referencia EU</div>', unsafe_allow_html=True)
    col_g, col_h = st.columns(2)
    bs = brechas.sort_values("Brecha_ptos", ascending=False)

    with col_g:
        fig_br = go.Figure()
        fig_br.add_trace(go.Bar(name="España %",       x=bs["Área"], y=bs["España_%"],
                                marker_color="#4fc3f7", text=bs["España_%"], textposition="outside"))
        fig_br.add_trace(go.Bar(name="Referencia EU %",x=bs["Área"], y=bs["EU_Referencia_%"],
                                marker_color="#ffa726", text=bs["EU_Referencia_%"], textposition="outside"))
        fig_br.update_layout(barmode="group", template="plotly_dark", height=420,
                              xaxis=dict(tickangle=-30), yaxis=dict(range=[0,110]),
                              legend=dict(orientation="h", y=1.1),
                              margin=dict(l=10,r=10,t=60,b=120))
        st.plotly_chart(fig_br, use_container_width=True)

    with col_h:
        fig_ba = px.bar(bs, x="Área", y="Brecha_ptos",
                        color="Brecha_ptos",
                        color_continuous_scale=["#66bb6a","#ffa726","#ef5350"],
                        text="Brecha_ptos", title="Brecha absoluta (puntos)",
                        template="plotly_dark")
        fig_ba.update_traces(textposition="outside", texttemplate="-%{text} ptos")
        fig_ba.update_layout(height=420, xaxis=dict(tickangle=-30),
                              coloraxis_showscale=False,
                              margin=dict(l=10,r=10,t=60,b=120))
        st.plotly_chart(fig_ba, use_container_width=True)

    st.markdown("---")

    # Servicios ciudadanos
    st.markdown('<div class="section-title">👤 Servicios Digitales — Uso y Satisfacción</div>', unsafe_allow_html=True)
    col_i, col_j = st.columns([1.2, 1])

    with col_i:
        fig_uso = px.bar(
            servicios_uso.sort_values("Usuarios_millones", ascending=False),
            x="Servicio", y="Usuarios_millones",
            color="Satisfacción_%",
            color_continuous_scale=["#ef5350","#ffa726","#66bb6a"],
            range_color=[35,85], text="Usuarios_millones",
            title="Usuarios activos (millones)", template="plotly_dark"
        )
        fig_uso.update_traces(textposition="outside", texttemplate="%{text:.1f}M")
        fig_uso.update_layout(height=420, xaxis=dict(tickangle=-30),
                               margin=dict(l=10,r=20,t=60,b=120))
        st.plotly_chart(fig_uso, use_container_width=True)

    with col_j:
        fig_sc = px.scatter(
            servicios_uso, x="Usuarios_millones", y="Satisfacción_%",
            text="Servicio", size="Usuarios_millones",
            color="Satisfacción_%",
            color_continuous_scale=["#ef5350","#ffa726","#66bb6a"],
            range_color=[35,85], title="Uso vs Satisfacción", template="plotly_dark"
        )
        fig_sc.update_traces(textposition="top center", textfont_size=9)
        fig_sc.add_hline(y=70, line_dash="dot", line_color="#ffd54f",
                         annotation_text="Umbral satisfacción (70%)")
        fig_sc.update_layout(height=420, coloraxis_showscale=False,
                              margin=dict(l=10,r=10,t=60,b=30))
        st.plotly_chart(fig_sc, use_container_width=True)


# ============================================================
# === TAB 2: CIBERSEGURIDAD & ENS ===
# ============================================================
with tab_ciber:
    st.markdown("## 🔐 Ciberseguridad en la Administración Pública Española")
    st.markdown(
        "Estado del **Esquema Nacional de Seguridad (ENS)**, evolución de incidentes gestionados por "
        "**CCN-CERT**, brecha con Europa, sectores más afectados, amenazas emergentes y retos 2025-2027."
    )
    st.markdown("---")

    # --- KPIs Ciberseguridad ---
    st.markdown('<div class="section-title">🚨 KPIs de Ciberseguridad — AA.PP. España 2024</div>', unsafe_allow_html=True)
    kc1, kc2, kc3, kc4, kc5, kc6 = st.columns(6)
    kpis_ciber = [
        (kc1, "97.663",    "Incidentes gestionados (CCN-CERT)",   "-10k vs 2023 (post-pico)"),
        (kc2, "872",       "Incidentes críticos",                 "+347% vs 2019"),
        (kc3, "38%",       "Entidades ENS certificadas (media)",  "Objetivo: 80% en 2026"),
        (kc4, "9%",        "Ayunt. < 20k con ENS adecuado",       "⚠ Brecha estructural"),
        (kc5, "63 / 100",  "NIS2 Readiness Score",                "+8 vs 2023"),
        (kc6, "24.000",    "Puestos ciber sin cubrir (sector púb.)","Déficit de talento"),
    ]
    for col, val, label, delta in kpis_ciber:
        col.markdown(f"""
        <div class="ciber-kpi">
            <div class="ciber-kpi-val">{val}</div>
            <div class="ciber-kpi-label">{label}</div>
            <div class="ciber-kpi-delta">{delta}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Fila 1: Evolución incidentes + Tipos de ataque ---
    col_c1, col_c2 = st.columns([1.3, 1])

    with col_c1:
        st.markdown('<div class="section-title">📈 Evolución de Incidentes CCN-CERT (2018–2024)</div>', unsafe_allow_html=True)
        fig_inc = go.Figure()
        colores_inc = {"Bajos":"#546e7a","Medios":"#ffa726","Altos":"#ef8a00","Críticos":"#ef5350"}
        for nivel, color in colores_inc.items():
            fig_inc.add_trace(go.Bar(
                name=nivel, x=incidentes_anuales["Año"],
                y=incidentes_anuales[nivel],
                marker_color=color
            ))
        fig_inc.add_trace(go.Scatter(
            name="Total", x=incidentes_anuales["Año"],
            y=incidentes_anuales["Total"],
            mode="lines+markers+text",
            line=dict(color="#ffffff", width=2, dash="dot"),
            marker=dict(size=8),
            text=incidentes_anuales["Total"].apply(lambda x: f"{x//1000}k"),
            textposition="top center", textfont=dict(size=10),
            yaxis="y2"
        ))
        fig_inc.update_layout(
            barmode="stack", template="plotly_dark", height=400,
            yaxis=dict(title="Incidentes por gravedad"),
            yaxis2=dict(title="Total", overlaying="y", side="right",
                        showgrid=False, range=[0, 140000]),
            legend=dict(orientation="h", y=1.12),
            margin=dict(l=10, r=10, t=60, b=30)
        )
        st.plotly_chart(fig_inc, use_container_width=True)

    with col_c2:
        st.markdown('<div class="section-title">🦠 Tipos de Ataque — Top 10 (2024)</div>', unsafe_allow_html=True)
        color_impacto = {"Crítico":"#ef5350","Alto":"#ffa726","Medio":"#4fc3f7","Bajo":"#66bb6a"}
        ta_sorted = tipos_ataque.sort_values("Incidentes_2024", ascending=True)
        fig_ta = go.Figure()
        for _, row in ta_sorted.iterrows():
            fig_ta.add_trace(go.Bar(
                x=[row["Incidentes_2024"]], y=[row["Tipo"]],
                orientation="h",
                marker_color=color_impacto.get(row["Impacto"], "#90a4ae"),
                name=row["Impacto"], showlegend=False,
                text=f"{row['Incidentes_2024']:,}  ({'+' if row['Variación_%']>0 else ''}{row['Variación_%']}%)",
                textposition="outside"
            ))
        for imp, col in color_impacto.items():
            fig_ta.add_trace(go.Bar(x=[None], y=[None], orientation="h",
                                    marker_color=col, name=imp))
        fig_ta.update_layout(
            template="plotly_dark", height=400,
            xaxis=dict(title="Incidentes", range=[0, 38000]),
            margin=dict(l=10, r=60, t=30, b=20)
        )
        st.plotly_chart(fig_ta, use_container_width=True)

    st.markdown("---")

    # --- Fila 2: Cumplimiento ENS + Madurez temporal ---
    col_c3, col_c4 = st.columns(2)

    with col_c3:
        st.markdown('<div class="section-title">🏛 Cumplimiento ENS por Tipo de Entidad</div>', unsafe_allow_html=True)
        fig_ens = go.Figure()
        ens_cols = {
            "Certificados_%": ("#66bb6a","ENS Certificado"),
            "Adecuados_%":    ("#ffd54f","Adecuado (sin cert.)"),
            "No_conformes_%": ("#ef5350","No conforme"),
        }
        for col_key, (color, nombre) in ens_cols.items():
            fig_ens.add_trace(go.Bar(
                name=nombre,
                x=ens_entidades["Entidad"],
                y=ens_entidades[col_key],
                marker_color=color,
                text=ens_entidades[col_key].apply(lambda v: f"{v}%"),
                textposition="inside"
            ))
        fig_ens.add_hline(y=80, line_dash="dot", line_color="#4fc3f7",
                          annotation_text="Objetivo 2026 (80%)", annotation_position="top right")
        fig_ens.update_layout(
            barmode="stack", template="plotly_dark", height=400,
            xaxis=dict(tickangle=-25),
            yaxis=dict(title="%", range=[0, 115]),
            legend=dict(orientation="h", y=1.12),
            margin=dict(l=10, r=10, t=60, b=100)
        )
        st.plotly_chart(fig_ens, use_container_width=True)

    with col_c4:
        st.markdown('<div class="section-title">📊 Evolución Madurez ENS por Nivel (2019–2024)</div>', unsafe_allow_html=True)
        fig_mad = go.Figure()
        mad_series = [
            ("AGE",          "#4fc3f7", "solid"),
            ("CCAA",         "#ffa726", "solid"),
            ("Local",        "#ef5350", "solid"),
            ("Objetivo_2026","#66bb6a", "dot"),
        ]
        for nombre, color, dash in mad_series:
            fig_mad.add_trace(go.Scatter(
                x=madurez_ens["Año"], y=madurez_ens[nombre],
                name=nombre.replace("_"," "),
                mode="lines+markers",
                line=dict(color=color, width=2.5, dash=dash),
                marker=dict(size=7)
            ))
        fig_mad.update_layout(
            template="plotly_dark", height=400,
            yaxis=dict(range=[0, 95], title="Índice de madurez ENS (0-100)"),
            legend=dict(orientation="h", y=1.12),
            margin=dict(l=10, r=10, t=60, b=30)
        )
        st.plotly_chart(fig_mad, use_container_width=True)

    st.markdown("---")

    # --- Fila 3: Radar amenazas + Comparativa EU ---
    col_c5, col_c6 = st.columns([1, 1.2])

    with col_c5:
        st.markdown('<div class="section-title">🎯 Radar de Amenazas — Probabilidad vs Impacto vs Preparación</div>', unsafe_allow_html=True)
        dims = amenazas_radar["Dimensión"].tolist()
        fig_ar = go.Figure()
        for serie, color, fill in [
            ("Probabilidad",   "#ef5350", "rgba(239,83,80,0.15)"),
            ("Impacto",        "#ffa726", "rgba(255,167,38,0.15)"),
            ("Preparación_ES", "#4fc3f7", "rgba(79,195,247,0.2)"),
        ]:
            vals = amenazas_radar[serie].tolist()
            fig_ar.add_trace(go.Scatterpolar(
                r=vals + [vals[0]], theta=dims + [dims[0]],
                fill="toself", name=serie,
                line_color=color, fillcolor=fill
            ))
        fig_ar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            template="plotly_dark", height=430,
            legend=dict(orientation="h", y=-0.15),
            margin=dict(l=20, r=20, t=40, b=60)
        )
        st.plotly_chart(fig_ar, use_container_width=True)

    with col_c6:
        st.markdown('<div class="section-title">🇪🇺 Comparativa EU — NIS2 Readiness & Madurez CSIRT</div>', unsafe_allow_html=True)
        fig_eu_c = go.Figure()
        ciber_eu_s = ciber_eu.sort_values("NIS2_Score")
        fig_eu_c.add_trace(go.Bar(
            name="NIS2 Score", x=ciber_eu_s["NIS2_Score"], y=ciber_eu_s["País"],
            orientation="h", marker_color="#4fc3f7",
            text=ciber_eu_s["NIS2_Score"], textposition="outside"
        ))
        fig_eu_c.add_trace(go.Bar(
            name="Madurez CSIRT", x=ciber_eu_s["CSIRT_Madurez"], y=ciber_eu_s["País"],
            orientation="h", marker_color="#ffa726", opacity=0.7,
            text=ciber_eu_s["CSIRT_Madurez"], textposition="outside"
        ))
        fig_eu_c.add_vline(x=63, line_dash="dot", line_color="#4fc3f7",
                           annotation_text="🇪🇸 España NIS2", annotation_position="top")
        fig_eu_c.update_layout(
            barmode="overlay", template="plotly_dark", height=430,
            xaxis=dict(range=[0, 110], title="Puntuación"),
            legend=dict(orientation="h", y=1.1),
            margin=dict(l=10, r=40, t=60, b=20)
        )
        st.plotly_chart(fig_eu_c, use_container_width=True)

    st.markdown("---")

    # --- Fila 4: Sectores más afectados + Bubble chart ---
    col_c7, col_c8 = st.columns([1.2, 1])

    with col_c7:
        st.markdown('<div class="section-title">🏥 Sectores Más Afectados — Incidentes Graves 2024</div>', unsafe_allow_html=True)
        fig_sec_c = px.bar(
            sectores_ciber.sort_values("Incidentes", ascending=True),
            x="Incidentes", y="Sector", orientation="h",
            color="Graves_%",
            color_continuous_scale=["#1565c0", "#ffa726", "#ef5350"],
            range_color=[10, 35],
            text="Incidentes",
            title="Incidentes totales (color = % graves)",
            template="plotly_dark"
        )
        fig_sec_c.update_traces(textposition="outside")
        fig_sec_c.update_layout(height=420, margin=dict(l=10, r=40, t=50, b=20))
        st.plotly_chart(fig_sec_c, use_container_width=True)

    with col_c8:
        st.markdown('<div class="section-title">⏱ Tiempo de Respuesta vs % Graves por Sector</div>', unsafe_allow_html=True)
        fig_bub = px.scatter(
            sectores_ciber,
            x="Tiempo_resp_h", y="Graves_%",
            size="Incidentes", text="Sector",
            color="Incidentes",
            color_continuous_scale=["#1565c0","#ef5350"],
            title="Respuesta (h) vs Incidentes graves (%)",
            template="plotly_dark"
        )
        fig_bub.update_traces(textposition="top center", textfont_size=8)
        fig_bub.add_hline(y=20, line_dash="dot", line_color="#ffd54f",
                          annotation_text="Umbral gravedad 20%")
        fig_bub.add_vline(x=8, line_dash="dot", line_color="#80cbc4",
                          annotation_text="SLA respuesta (8h)")
        fig_bub.update_layout(height=420, coloraxis_showscale=False,
                               margin=dict(l=10, r=10, t=50, b=30))
        st.plotly_chart(fig_bub, use_container_width=True)

    st.markdown("---")

    # --- Incidentes Notables ---
    st.markdown('<div class="section-title">📋 Registro de Incidentes Notables — AA.PP. España 2024</div>', unsafe_allow_html=True)
    sev_cls = {"Crítica":"sev-critica","Alta":"sev-alta","Media":"sev-media","Baja":"sev-baja"}
    sev_icon = {"Crítica":"🔴","Alta":"🟠","Media":"🟡","Baja":"🟢"}
    border_col = {"Crítica":"#ef5350","Alta":"#ff8a65","Media":"#ffd54f","Baja":"#81c784"}

    for inc in incidentes_notables:
        bc = border_col.get(inc["sev"],"#4fc3f7")
        sc = sev_cls.get(inc["sev"],"")
        si = sev_icon.get(inc["sev"],"")
        st.markdown(f"""
        <div class="threat-card" style="border-left-color:{bc}">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                <span style="color:#90caf9;font-size:0.8rem;font-weight:600">{inc['fecha']}</span>
                <span class="ens-badge ens-{'nc' if inc['sev']=='Crítica' else 'medio' if inc['sev']=='Alta' else 'basico'}"
                      style="border-left-color:{bc}">
                    {si} {inc['sev']}
                </span>
            </div>
            <div style="font-weight:700;color:#e3f2fd;font-size:0.95rem">{inc['org']}</div>
            <div style="color:#ce93d8;font-size:0.8rem;margin:2px 0">Tipo: <strong>{inc['tipo']}</strong></div>
            <div style="color:#90a4ae;font-size:0.84rem">{inc['desc']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Retos y Desafíos ---
    st.markdown('<div class="section-title">🔭 Retos y Desafíos ENS 2025–2027</div>', unsafe_allow_html=True)
    urg_color = {"Crítica":"#ef5350","Emergente":"#ce93d8","Alta":"#ffa726"}

    col_r1, col_r2 = st.columns(2)
    for i, reto in enumerate(retos_ens):
        col = col_r1 if i % 2 == 0 else col_r2
        uc = urg_color.get(reto["urgencia"],"#90a4ae")
        with col:
            st.markdown(f"""
            <div class="threat-card" style="border-left-color:{uc}">
                <div style="font-size:1.3rem;margin-bottom:4px">{reto['icono']}
                    <span style="font-weight:700;color:#e3f2fd;font-size:0.95rem"> {reto['titulo']}</span>
                    <span class="ens-badge" style="background:transparent;border:1px solid {uc};color:{uc};float:right">
                        {reto['urgencia']}
                    </span>
                </div>
                <div style="color:#90a4ae;font-size:0.84rem">{reto['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Gauge NIS2 + donut ENS ---
    col_cg1, col_cg2, col_cg3 = st.columns(3)

    with col_cg1:
        fig_nis = go.Figure(go.Indicator(
            mode="gauge+number",
            value=63,
            title={"text":"NIS2 Readiness — España", "font":{"size":14}},
            gauge={
                "axis":{"range":[0,100]},
                "bar":{"color":"#4fc3f7"},
                "steps":[
                    {"range":[0,40],"color":"#b71c1c"},
                    {"range":[40,65],"color":"#e65100"},
                    {"range":[65,85],"color":"#1565c0"},
                    {"range":[85,100],"color":"#1b5e20"},
                ],
                "threshold":{"line":{"color":"#ffd54f","width":4},"thickness":0.8,"value":85}
            }
        ))
        fig_nis.update_layout(template="plotly_dark", height=280,
                               margin=dict(l=20,r=20,t=40,b=10))
        st.plotly_chart(fig_nis, use_container_width=True)

    with col_cg2:
        fig_ens_d = go.Figure(go.Pie(
            labels=["Certificados ENS","Adecuados","No conformes"],
            values=[38, 26, 36],
            hole=0.55,
            marker=dict(colors=["#66bb6a","#ffd54f","#ef5350"]),
            textinfo="label+percent"
        ))
        fig_ens_d.update_layout(
            title="Estado ENS — Media todas las AA.PP.",
            template="plotly_dark", height=280,
            showlegend=False,
            margin=dict(l=10,r=10,t=50,b=10),
            annotations=[dict(text="ENS<br>2024", x=0.5, y=0.5,
                               font_size=13, showarrow=False, font_color="#e3f2fd")]
        )
        st.plotly_chart(fig_ens_d, use_container_width=True)

    with col_cg3:
        fig_soc = go.Figure(go.Indicator(
            mode="gauge+number",
            value=31,
            title={"text":"Entidades con SOC activo (%)", "font":{"size":14}},
            gauge={
                "axis":{"range":[0,100]},
                "bar":{"color":"#ffa726"},
                "steps":[
                    {"range":[0,30],"color":"#b71c1c"},
                    {"range":[30,60],"color":"#e65100"},
                    {"range":[60,80],"color":"#1565c0"},
                    {"range":[80,100],"color":"#1b5e20"},
                ],
                "threshold":{"line":{"color":"#ffd54f","width":4},"thickness":0.8,"value":70}
            }
        ))
        fig_soc.update_layout(template="plotly_dark", height=280,
                               margin=dict(l=20,r=20,t=40,b=10))
        st.plotly_chart(fig_soc, use_container_width=True)

    st.markdown(
        "<small>📡 Fuentes: CCN-CERT Informe de Ciberamenazas 2024 · "
        "INCIBE Informe Anual 2024 · ENISA Threat Landscape 2024 · "
        "NIS2 Country Assessment EU · Informes SEDIA/ENS</small>",
        unsafe_allow_html=True
    )


# ============================================================
# === TAB 3: OSINT & ALERTAS ===
# ============================================================
with tab_osint:
    st.markdown('<div class="section-title">🛰 Módulo OSINT — Fuentes externas (CSVs)</div>', unsafe_allow_html=True)

    files = sorted(glob.glob("data/osint_*.csv"))

    if not files:
        st.info("📂 No se encontraron archivos CSV en `data/osint_*.csv`. "
                "Coloca los archivos exportados en la carpeta `data/` para activar este módulo.")
    else:
        dfs = []
        for f in files[-14:]:
            try:
                dfs.append(pd.read_csv(f))
            except Exception as e:
                st.warning(f"No se pudo leer {f}: {e}")

        if dfs:
            df = pd.concat(dfs, ignore_index=True)
            df['date'] = pd.to_datetime(df['date'], errors='coerce')

            o1, o2, o3, o4 = st.columns(4)
            o1.metric("Fuentes únicas", df['source'].nunique() if 'source' in df.columns else "N/A")
            o2.metric("Artículos totales", len(df))
            alert_count = int(df['title'].str.contains('|'.join(alert_words), case=False, na=False).sum()) \
                if 'title' in df.columns else 0
            o3.metric("Artículos con alertas", alert_count)
            last_date = df['date'].max()
            o4.metric("Última fecha", last_date.strftime("%Y-%m-%d") if pd.notna(last_date) else "N/A")

            col_p, col_q = st.columns(2)
            with col_p:
                if 'date' in df.columns:
                    dc = df.groupby(df['date'].dt.date).size().reset_index()
                    dc.columns = ['date', 'count']
                    fig_d = px.line(dc, x='date', y='count', markers=True,
                                    title="Evolución diaria de capturas", template="plotly_dark")
                    st.plotly_chart(fig_d, use_container_width=True)

            with col_q:
                if 'source' in df.columns:
                    ts = df['source'].value_counts().nlargest(10).reset_index()
                    ts.columns = ['source','count']
                    fig_ts = px.bar(ts, x='source', y='count', text='count', color='source',
                                    title="Top 10 fuentes", template="plotly_dark")
                    fig_ts.update_layout(showlegend=False)
                    st.plotly_chart(fig_ts, use_container_width=True)

            if 'source' in df.columns:
                fig_pie = px.pie(df, names='source', title="Distribución por fuente",
                                 template="plotly_dark")
                st.plotly_chart(fig_pie, use_container_width=True)

            # Referencias OSINT con enlaces si existe columna url/link
            st.markdown('<div class="section-title">🔗 Artículos con enlace</div>', unsafe_allow_html=True)
            url_col = next((c for c in ['url','link','href'] if c in df.columns), None)
            title_col = 'title' if 'title' in df.columns else None

            if url_col and title_col:
                df_links = df[[title_col, 'source', 'date', url_col]].dropna(subset=[url_col])
                df_links = df_links.sort_values('date', ascending=False).head(50)
                for _, row in df_links.iterrows():
                    fecha = row['date'].strftime("%Y-%m-%d") if pd.notna(row['date']) else "—"
                    st.markdown(
                        f'<div class="ref-card">'
                        f'<span class="ref-year">{fecha}</span>'
                        f'<span class="ref-tag">{row["source"]}</span>'
                        f'<strong>{row[title_col]}</strong><br>'
                        f'<a href="{row[url_col]}" target="_blank">🔗 Abrir artículo</a>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.info("Para mostrar enlaces, el CSV necesita una columna `url` o `link`.")

            # Alertas críticas
            if title_col:
                df_alerts = df[df[title_col].str.contains('|'.join(alert_words), case=False, na=False)]
                st.markdown('<div class="section-title">🚨 Alertas críticas detectadas</div>', unsafe_allow_html=True)
                if df_alerts.empty:
                    st.info("No hay artículos con alertas críticas en el periodo.")
                else:
                    cols_show = [c for c in [title_col, 'source', 'date', url_col] if c and c in df_alerts.columns]
                    st.dataframe(df_alerts[cols_show], use_container_width=True)

            if 'lat' in df.columns and 'lon' in df.columns:
                st.subheader("🗺 Mapa de actividad")
                fig_map = px.scatter_geo(df, lat='lat', lon='lon',
                                         hover_name='title', color='source',
                                         title="Distribución geográfica", template="plotly_dark")
                st.plotly_chart(fig_map, use_container_width=True)


# ============================================================
# === TAB 3: LÍNEA CRONOLÓGICA ===
# ============================================================
with tab_crono:
    st.markdown("## 📅 Línea Cronológica — Administración Digital en España")
    st.markdown(
        "Principales hitos legislativos, planes estratégicos, crisis y logros "
        "desde los años 90 hasta la actualidad. La digitalización de la Administración "
        "española es un proceso de más de tres décadas con aceleración notable desde 2020."
    )
    st.markdown("---")

    # Filtro por tipo
    tipos_disp = ["Todos", "LEY", "PLAN", "EU / Regulación", "HITO / FONDOS", "CRISIS / EVENTO"]
    filtro = st.selectbox("Filtrar por categoría", tipos_disp)

    badge_map = {
        "badge-ley":   ("LEY",            "LEY"),
        "badge-plan":  ("PLAN",           "PLAN"),
        "badge-eu":    ("EU / Regulación","EU / Regulación"),
        "badge-hito":  ("HITO / FONDOS",  "HITO / FONDOS"),
        "badge-crisis":("CRISIS / EVENTO","CRISIS / EVENTO"),
    }

    st.markdown('<div class="tl-container">', unsafe_allow_html=True)
    for h in hitos:
        cat_nombre = badge_map.get(h["badge_tipo"], ("", ""))[1]
        if filtro != "Todos" and filtro != cat_nombre:
            continue
        dot_color = h["color"]
        st.markdown(f"""
        <div class="tl-item">
            <div class="tl-dot" style="background:{dot_color};border-color:{dot_color};"></div>
            <div class="tl-year">{h['año']}</div>
            <div class="tl-title">
                <span class="tl-badge {h['badge_tipo']}">{h['badge_txt']}</span>
                {h['titulo']}
            </div>
            <div class="tl-desc">{h['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    # Gráfico de densidad de hitos por año
    st.markdown('<div class="section-title">📊 Intensidad legislativa y estratégica por período</div>', unsafe_allow_html=True)
    años_hitos = [int(h["año"]) for h in hitos]
    hitos_df = pd.DataFrame({"Año": años_hitos, "Tipo": [badge_map.get(h["badge_tipo"],("",""))[1] for h in hitos]})
    fig_h = px.histogram(hitos_df, x="Año", color="Tipo", nbins=15,
                          template="plotly_dark",
                          title="Distribución de hitos por año y categoría",
                          color_discrete_map={
                              "LEY":"#4fc3f7","PLAN":"#66bb6a","EU / Regulación":"#ce93d8",
                              "HITO / FONDOS":"#ffcc80","CRISIS / EVENTO":"#ef5350"
                          })
    fig_h.update_layout(height=300, bargap=0.1, margin=dict(l=10,r=10,t=50,b=30))
    st.plotly_chart(fig_h, use_container_width=True)


# ============================================================
# === TAB 4: REFERENCIAS DOCUMENTALES ===
# ============================================================
with tab_refs:
    st.markdown("## 📚 Referencias Documentales")
    st.markdown(
        "Corpus documental base del dashboard. Ordenado cronológicamente (más reciente primero). "
        "Los documentos marcados con 🔽 tienen enlace directo a descarga o consulta oficial."
    )
    st.markdown("---")

    # ── PANEL NORMATIVA NUEVA (normativa_watch.py) ──────────────
    _norm_csv = _Path("data/normativa_nuevas.csv")
    if _norm_csv.exists():
        try:
            import pandas as _pd_norm
            _df_norm = _pd_norm.read_csv(_norm_csv)
            _pendientes = _df_norm[_df_norm.get("revisado", _pd_norm.Series(dtype=str)).fillna("") == ""]
            if not _pendientes.empty:
                n_crit = int((_pendientes.get("severidad","") == "Crítica").sum())
                n_alta = int((_pendientes.get("severidad","") == "Alta").sum())
                _badge = f"🔴 {n_crit} crítica(s)" if n_crit else f"🟠 {n_alta} alta(s)" if n_alta else f"⚪ {len(_pendientes)}"
                with st.expander(f"🔔 Normativa nueva detectada automáticamente — {len(_pendientes)} pendiente(s) de revisión  {_badge}", expanded=n_crit > 0):
                    st.markdown(
                        "Candidatas detectadas por `normativa_watch.py`. "
                        "Revisa cada una y decide si incorporarla a las Referencias Documentales. "
                        "Para marcarla como revisada edita `data/normativa_nuevas.csv` → columna `revisado` → `SI` o `NO`."
                    )
                    for _, _nr in _pendientes.sort_values("fecha_deteccion", ascending=False).head(20).iterrows():
                        _sev = _nr.get("severidad", "Info")
                        _sev_color = {"Crítica": "#b71c1c", "Alta": "#e65100", "Media": "#f9a825"}.get(_sev, "#546e7a")
                        _sev_icon  = {"Crítica": "🔴", "Alta": "🟠", "Media": "🟡"}.get(_sev, "⚪")
                        _url_nr = _nr.get("url", "")
                        _enlace_nr = f'<a href="{_url_nr}" target="_blank">🔗 Ver documento</a>' if _url_nr else ""
                        st.markdown(f"""
                        <div style="background:#1a1f2e;border:1px solid #2a3550;border-left:4px solid {_sev_color};
                                    border-radius:6px;padding:10px 14px;margin:4px 0">
                            {_sev_icon} <span style="background:{_sev_color};color:#fff;padding:1px 7px;
                            border-radius:3px;font-size:11px">{_sev}</span>
                            <span style="color:#90a4ae;font-size:11px;margin-left:8px">{_nr.get("tipo_normativa","")}</span>
                            <span style="color:#90a4ae;font-size:11px;margin-left:8px">{_nr.get("fecha_publicacion","")}</span><br>
                            <strong style="color:#e3f2fd">{_nr.get("titulo","")[:100]}</strong><br>
                            <span style="color:#78909c;font-size:12px">{_nr.get("fuente","")}</span>
                            {"  ·  " + _enlace_nr if _enlace_nr else ""}
                        </div>
                        """, unsafe_allow_html=True)
        except Exception as _e_norm:
            pass  # Si hay cualquier error, no interrumpe el tab
    # ── FIN PANEL NORMATIVA NUEVA ────────────────────────────────

    # Filtros
    col_rf1, col_rf2 = st.columns([1, 2])
    filtro_tipo = col_rf1.selectbox("Tipo de fuente", ["Todas", "ES — España", "EU — Europa"])
    filtro_busca = col_rf2.text_input("Buscar en título o descripción", "")

    refs_ord = sorted(referencias, key=lambda x: x["año"], reverse=True)

    for r in refs_ord:
        # Filtros
        if filtro_tipo == "ES — España" and r["tipo"] != "ES":
            continue
        if filtro_tipo == "EU — Europa" and r["tipo"] != "EU":
            continue
        if filtro_busca and filtro_busca.lower() not in (r["titulo"]+r["descripcion"]).lower():
            continue

        tag_cls  = "ref-tag-es" if r["tipo"] == "ES" else "ref-tag-eu"
        tag_label= "🇪🇸 España"  if r["tipo"] == "ES" else "🇪🇺 UE / Europa"
        enlace = ""
        if r["descargable"]:
            enlace = f'<br><a href="{r["url"]}" target="_blank">🔽 Descargar / Consultar documento oficial</a>'
        else:
            enlace = f'<br><small>📍 Disponible en: <a href="{r["url"]}" target="_blank">{r["url"]}</a></small>'

        st.markdown(f"""
        <div class="ref-card">
            <span class="ref-year">{r['año']}</span>
            <span class="ref-tag {tag_cls}">{tag_label}</span>
            <strong>{r['titulo']}</strong><br>
            <span style="color:#90a4ae;font-size:0.87rem">{r['descripcion']}</span>
            {enlace}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        f"<small>Total referencias: **{len(referencias)}** · "
        f"Con descarga directa: **{sum(1 for r in referencias if r['descargable'])}** · "
        f"Solo consulta web: **{sum(1 for r in referencias if not r['descargable'])}**</small>",
        unsafe_allow_html=True
    )


# ============================================================
# === TAB 5: METODOLOGÍA ===
# ============================================================
with tab_meto:
    st.markdown("## ⚙️ Metodología, Fuentes de Datos y Decisiones de Diseño")
    st.markdown("---")

    # ── BLOQUE GUÍA PDF ─────────────────────────────────────────
    _PDF_PATH   = _Path("data/guia_admindash.pdf")
    _GEN_SCRIPT = _Path("gen_guia.py")

    def _ultima_captura():
        csvs = sorted(glob.glob("data/osint_*.csv"))
        if csvs:
            nombre = os.path.basename(csvs[-1])
            fecha  = nombre.replace("osint_","").replace(".csv","")
            mtime  = _dt.fromtimestamp(os.path.getmtime(csvs[-1]))
            return fecha, mtime.strftime("%Y-%m-%d %H:%M"), nombre
        return "—", "—", "—"

    _fecha_cap, _mtime_cap, _csv_nombre = _ultima_captura()

    # Caja de estado del sistema
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        st.metric("📅 Última captura OSINT", _fecha_cap)
    with col_g2:
        st.metric("🕐 Timestamp del CSV", _mtime_cap)
    with col_g3:
        _n_csvs = len(glob.glob("data/osint_*.csv"))
        st.metric("📁 CSVs en data/", f"{_n_csvs} archivos")

    st.markdown("---")

    # Botón descarga directa si ya existe el PDF
    col_d1, col_d2 = st.columns([3, 1])
    with col_d1:
        st.markdown(
            "📄 **Guía Técnica y de Usuario — Dashboard Administración Digital España v1.0**  \n"
            "Documento completo con arquitectura, módulos, fuentes, metodología, glosario, FAQ "
            "y estado de la última captura OSINT."
        )
    with col_d2:
        if _PDF_PATH.exists():
            with open(_PDF_PATH, "rb") as _pdf_f:
                st.download_button(
                    label="⬇️ Descargar guía PDF",
                    data=_pdf_f.read(),
                    file_name=f"guia_admindash_{_dt.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                )
        else:
            st.info("Genera el PDF primero con el botón de abajo.")

    # Botón regenerar guía al vuelo (si gen_guia.py está disponible)
    if _GEN_SCRIPT.exists():
        st.markdown("---")
        _col_r1, _col_r2 = st.columns([3, 1])
        with _col_r1:
            st.markdown(
                "🔄 **Regenerar guía actualizada** — recalcula la fecha de última captura "
                "e inyecta los datos del CSV más reciente en el PDF."
            )
        with _col_r2:
            if st.button("🔄 Regenerar PDF"):
                with st.spinner("Generando PDF..."):
                    try:
                        result = subprocess.run(
                            [sys.executable, str(_GEN_SCRIPT)],
                            capture_output=True, text=True, timeout=60
                        )
                        if result.returncode == 0:
                            st.success("✅ PDF regenerado. Recarga la página para ver el PDF actualizado.")
                        else:
                            st.error(f"Error al generar PDF:\n{result.stderr[:400]}")
                    except Exception as _e:
                        st.error(f"Error: {_e}")

    st.markdown("---")

    # Bloque 1: Objetivo
    st.markdown('<div class="section-title">🎯 Objetivo del Dashboard</div>', unsafe_allow_html=True)
    st.markdown("""
    Este dashboard nació como herramienta de **inteligencia abierta (OSINT)** para monitorizar
    el estado de la administración digital en España, comparar su posición respecto a Europa
    e identificar sectores y áreas con mayor brecha de cumplimiento.

    Combina dos capas de datos:
    - **Datos estructurados estáticos**: índices oficiales EU/ES, planes estratégicos, métricas de servicios.
    - **Datos dinámicos OSINT**: capturas periódicas de fuentes abiertas en CSVs, con detección de alertas.
    """)

    # Bloque 2: Fuentes
    st.markdown('<div class="section-title">📡 Fuentes de Datos Primarias</div>', unsafe_allow_html=True)

    fuentes_tabla = pd.DataFrame({
        "Fuente": [
            "DESI (Digital Economy & Society Index)",
            "eGovernment Benchmark — Comisión Europea",
            "SEDIA — Secretaría de Estado de Digitalización",
            "Agenda España Digital 2025/2026",
            "Plan de Recuperación (PRTR) — Componente 11",
            "ENS / ENI — BOE",
            "Cl@ve — Estadísticas de uso",
            "AEAT — Memoria de Actividades",
            "SEPE / SS — Memorias anuales",
            "Feeds OSINT propios (RSS, scraping)"
        ],
        "Tipo": ["EU","EU","ES","ES","ES","ES","ES","ES","ES","OSINT"],
        "Periodicidad": ["Anual","Anual","Anual","Permanente","Semestral",
                         "Actualización normativa","Mensual","Anual","Anual","Diaria"],
        "Formato": ["PDF/Web","PDF","PDF/Web","Web","Web","BOE/PDF",
                    "Web","PDF","PDF","CSV"]
    })
    st.dataframe(fuentes_tabla, use_container_width=True, hide_index=True)

    # Bloque 3: Proceso
    st.markdown('<div class="section-title">🔄 Proceso de Construcción</div>', unsafe_allow_html=True)
    pasos = [
        ("1", "Recopilación OSINT",
         "Scraping y agregación RSS de fuentes institucionales, medios especializados y portales de datos abiertos. Almacenado en CSVs diarios con formato: date, title, source, url."),
        ("2", "Extracción de métricas clave",
         "Lectura manual y automatizada de informes PDF (DESI, eGov Benchmark, SEDIA) para extraer puntuaciones por dimensión, país y sector."),
        ("3", "Normalización y estructuración",
         "Los datos se organizan en DataFrames pandas. Los índices heterogéneos (0-1, 0-100, porcentajes) se normalizan a escala 0-100 para comparabilidad."),
        ("4", "Cálculo de brechas",
         "Para cada área se calcula: Brecha = Referencia EU – España. Se usa el percentil 75 de la EU como referencia (no la media), lo que eleva el nivel de exigencia."),
        ("5", "Visualización con Plotly",
         "Todos los gráficos usan Plotly (template plotly_dark). Se priorizan: barras horizontales para rankings, radar para perfiles multidimensionales, gauge para KPIs, treemap para distribución."),
        ("6", "Detección de alertas OSINT",
         "Los artículos se filtran por palabras clave semánticas en título: alerta, riesgo, crítico, brecha, fallo, vulnerabilidad. Se cuenta y visualiza la densidad temporal."),
        ("7", "Actualización continua",
         "El módulo OSINT carga automáticamente los 14 CSVs más recientes de la carpeta data/. La recarga se hace en cada sesión Streamlit sin necesidad de reiniciar."),
    ]
    for num, titulo, desc in pasos:
        st.markdown(f"""
        <div class="meto-box">
            <div class="meto-step">
                <div class="meto-num">{num}</div>
                <div>
                    <strong style="color:#e3f2fd">{titulo}</strong><br>
                    <span style="color:#90a4ae;font-size:0.88rem">{desc}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Bloque 4: Limitaciones
    st.markdown('<div class="section-title">⚠️ Limitaciones y Consideraciones</div>', unsafe_allow_html=True)
    st.markdown("""
    - **Los datos DESI y eGov Benchmark son anuales**: no reflejan cambios infra-anuales.
    - **Los porcentajes de cumplimiento sectorial** son estimaciones basadas en memorias
      e informes públicos, no auditorías independientes. Deben tratarse como aproximaciones.
    - **La brecha respecto a Europa** usa el P75 EU como referencia ideal, lo que puede
      sobreestimar el retraso relativo de España frente a la media simple.
    - **El módulo OSINT** depende de la calidad y estructura de los CSVs generados.
      Si los feeds no están correctamente etiquetados, la detección de alertas puede ser
      incompleta o generar falsos positivos.
    - **Datos de satisfacción ciudadana**: proceden de encuestas del Observatorio de
      Administración Electrónica (OBSAE), con limitaciones de representatividad muestral.
    """)

    # Bloque 5: Stack técnico
    st.markdown('<div class="section-title">🛠 Stack Técnico</div>', unsafe_allow_html=True)
    stack = pd.DataFrame({
        "Componente": ["Frontend / App","Gráficos interactivos","Datos tabulares",
                       "Procesamiento","OSINT / Ingesta","Despliegue"],
        "Tecnología": ["Streamlit 1.x","Plotly Express + Graph Objects","Pandas",
                       "Python 3.10+","glob + pandas CSV reader","Local (Odroid-C2 / ARM)"],
        "Versión mín.": ["1.28","5.x","2.x","3.10","stdlib","—"]
    })
    st.dataframe(stack, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown(
        "<small>📡 Dashboard desarrollado como herramienta OSINT de análisis de política digital pública. "
        "Datos: DESI 2023 · eGovMonitor · SEDIA 2024 · Informes BOE · OBSAE · "
        "Actualizado: 2024</small>",
        unsafe_allow_html=True
    )


# ============================================================
# === FOOTER GLOBAL ===
# ============================================================
st.markdown("---")
st.markdown(
    "<small>🇪🇸 Dashboard Administración Digital España · "
    "Datos: DESI 2023 · eGov Benchmark · SEDIA 2024 · PRTR · BOE · OSINT propio</small>"
    "<br><small>© M. Castillo · "
    "<a href='mailto:mybloggingnotes@gmail.com'>mybloggingnotes@gmail.com</a> · "
    "Todos los derechos reservados</small>",
    unsafe_allow_html=True
)
