#!/usr/bin/env python3
"""
normativa_watch.py
==================
Módulo independiente de vigilancia de normativa nueva para el
Dashboard de Administración Digital España.

Lee los CSVs generados por osint_scraper.py del día actual,
filtra artículos de normativa relevante (BOE, EUR-Lex, etc.)
y genera:
  - data/normativa_nuevas.csv   → candidatas para el tab Referencias
  - data/.normativa_seen.json   → caché de deduplicación (90 días)

Si detecta normativa nueva de categoría Alta/Crítica,
llama a normativa_alert.py para enviar email.

Uso:
    python3 normativa_watch.py              # ejecución normal
    python3 normativa_watch.py --test       # verbose sin guardar
    python3 normativa_watch.py --dias 7     # buscar en últimos 7 días de CSVs
    python3 normativa_watch.py --reset      # limpiar caché de vistos

Cron (08:06 — después del scraper de las 06:00):
    6 8 * * * cd ~/admindash-osint && venv/bin/python3 normativa_watch.py >> logs/normativa.log 2>&1

Autor: M. Castillo · mybloggingnotes@gmail.com
"""

import os
import csv
import json
import glob
import logging
import argparse
import hashlib
import subprocess
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

# ============================================================
# === CONFIGURACIÓN ===
# ============================================================

DATA_DIR         = Path("data")
LOGS_DIR         = Path("logs")
OUTPUT_CSV       = DATA_DIR / "normativa_nuevas.csv"
SEEN_FILE        = DATA_DIR / ".normativa_seen.json"
ALERT_SCRIPT     = Path("normativa_alert.py")

# Días de retención en caché de normativa vista
SEEN_TTL_DAYS    = 90

# Días hacia atrás de CSVs a escanear (normalmente 1, subir si se ejecuta tarde)
DEFAULT_DIAS_CSV = 2

# Columnas del CSV de salida
CSV_COLUMNS = [
    "fecha_deteccion",  # cuando lo detectó el watch
    "fecha_publicacion",# fecha del artículo original
    "titulo",
    "fuente",
    "categoria_osint",  # categoría del scraper original
    "tipo_normativa",   # BOE / EUR-Lex / INCIBE / etc. (inferido)
    "url",
    "resumen",
    "severidad",
    "revisado",         # "" = pendiente, "SI" = incorporado a referencias, "NO" = descartado
]

# ============================================================
# === LOGGING ===
# ============================================================

LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            LOGS_DIR / f"normativa_{date.today()}.log",
            encoding="utf-8"
        ),
    ]
)
log = logging.getLogger("normativa_watch")

# ============================================================
# === PALABRAS CLAVE DE NORMATIVA ===
# ============================================================

# Palabras que identifican normativa real (no noticias sobre normativa)
NORMATIVA_KEYWORDS = [
    # BOE — tipos de disposición
    "real decreto", "real decreto-ley", "orden ministerial", "resolución",
    "ley orgánica", "ley ", "instrucción técnica", "circular",
    "disposición adicional", "disposición transitoria",
    # EUR-Lex — tipos EU
    "reglamento (ue)", "reglamento ue", "directiva (ue)", "directiva ue",
    "decisión (ue)", "decisión ue", "recomendación", "comunicación",
    "doue", "diario oficial", "diario oficial de la unión",
    # Ámbitos específicos de interés
    "esquema nacional de seguridad", "ens ",
    "esquema nacional de interoperabilidad", "eni ",
    "administración electrónica", "sede electrónica",
    "identidad digital", "cartera digital europea", "eudiw",
    "eidas", "eidas 2", "firma electrónica", "certificado digital",
    "nis2", "nis 2", "dora ", "ai act", "reglamento ia",
    "datos abiertos", "open data", "interoperabilidad",
    "ciberseguridad", "protección de datos", "rgpd", "gdpr",
    "inteligencia artificial", "infraestructura crítica",
    "transformación digital", "agenda digital",
    "plan de recuperación", "prtr", "componente 11",
]

# Fuentes que típicamente publican normativa
NORMATIVA_SOURCES = [
    "boe", "eur-lex", "diario oficial", "doue",
    "sedia", "administración digital", "administracion.gob",
    "pae", "obsae", "datos.gob", "incibe", "ccn",
    "comisión europea", "commission", "parlamento europeo",
    "moncloa", "congreso", "senado",
]

# Categorías OSINT que contienen normativa
NORMATIVA_CATEGORIES = [
    "Normativa ES", "Normativa EU", "Política Digital EU",
    "Administración Digital", "Datos Abiertos",
]

# Severidades que activan email de alerta
ALERT_SEVERITIES = ["Crítica", "Alta"]

# ============================================================
# === CACHÉ DE VISTOS ===
# ============================================================

def load_seen() -> dict:
    if SEEN_FILE.exists():
        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            cutoff = (date.today() - timedelta(days=SEEN_TTL_DAYS)).isoformat()
            return {k: v for k, v in data.items() if v >= cutoff}
        except Exception:
            pass
    return {}


def save_seen(seen: dict):
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(seen, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.warning(f"No se pudo guardar caché: {e}")


def make_hash(titulo: str, url: str) -> str:
    return hashlib.md5(
        f"{titulo.strip().lower()}{url.strip()}".encode()
    ).hexdigest()

# ============================================================
# === DETECCIÓN DE NORMATIVA ===
# ============================================================

def es_normativa(row: dict) -> bool:
    """
    Devuelve True si el artículo parece normativa real.
    Criterio: categoría normativa O palabras clave en título/resumen.
    """
    categoria = row.get("category", "").strip()
    titulo    = row.get("title", "").lower()
    resumen   = row.get("summary", "").lower()
    fuente    = row.get("source", "").lower()
    texto     = f"{titulo} {resumen}"

    # Por categoría directa
    if any(c.lower() in categoria.lower() for c in NORMATIVA_CATEGORIES):
        if any(kw in texto for kw in NORMATIVA_KEYWORDS):
            return True

    # Por fuente conocida de normativa
    if any(s in fuente for s in NORMATIVA_SOURCES):
        if any(kw in texto for kw in NORMATIVA_KEYWORDS):
            return True

    # Por palabras clave fuertes en título (sin importar fuente)
    strong_kw = [
        "real decreto", "reglamento (ue)", "directiva (ue)",
        "ley orgánica", "orden ministerial", "resolución boe",
        "esquema nacional", "eidas", "nis2", "ai act", "dora "
    ]
    if any(kw in titulo for kw in strong_kw):
        return True

    return False


def inferir_tipo(row: dict) -> str:
    """Infiere el tipo de normativa a partir de la fuente y el título."""
    fuente = row.get("source", "").lower()
    titulo = row.get("title", "").lower()

    if "boe" in fuente or "real decreto" in titulo or "orden ministerial" in titulo:
        return "BOE — España"
    if "eur-lex" in fuente or "reglamento (ue)" in titulo or "directiva (ue)" in titulo:
        return "EUR-Lex — UE"
    if "incibe" in fuente or "ccn" in fuente:
        return "INCIBE / CCN-CERT"
    if "comisión europea" in fuente or "commission" in fuente:
        return "Comisión Europea"
    if "moncloa" in fuente or "congreso" in fuente or "senado" in fuente:
        return "Gobierno / Legislativo ES"
    if "datos.gob" in fuente:
        return "Datos Abiertos ES"
    return "Otras fuentes"

# ============================================================
# === LECTURA DE CSVs OSINT ===
# ============================================================

def leer_csvs_recientes(dias: int = DEFAULT_DIAS_CSV) -> list[dict]:
    """Lee los CSVs OSINT de los últimos N días."""
    cutoff = date.today() - timedelta(days=dias)
    rows   = []
    csvs   = sorted(glob.glob(str(DATA_DIR / "osint_*.csv")))

    for csv_path in csvs:
        nombre = Path(csv_path).stem  # osint_YYYY-MM-DD
        try:
            fecha_csv = date.fromisoformat(nombre.replace("osint_", ""))
        except ValueError:
            continue
        if fecha_csv < cutoff:
            continue
        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row["_csv_file"] = csv_path
                    rows.append(row)
        except Exception as e:
            log.warning(f"No se pudo leer {csv_path}: {e}")

    log.info(f"CSVs leídos ({dias}d): {len(rows)} artículos totales")
    return rows

# ============================================================
# === LECTURA / ESCRITURA CSV NORMATIVA ===
# ============================================================

def leer_normativa_existente() -> list[dict]:
    """Carga el CSV de normativa detectada (si existe)."""
    if not OUTPUT_CSV.exists():
        return []
    try:
        with open(OUTPUT_CSV, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def guardar_normativa(rows: list[dict]):
    """Escribe/actualiza el CSV de normativa candidata."""
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=CSV_COLUMNS, extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)
    log.info(f"CSV normativa actualizado: {OUTPUT_CSV} ({len(rows)} entradas)")

# ============================================================
# === MOTOR PRINCIPAL ===
# ============================================================

def run(test_mode: bool = False, dias: int = DEFAULT_DIAS_CSV) -> list[dict]:
    log.info(f"=== normativa_watch — {datetime.now().isoformat()} ===")

    seen          = load_seen()
    osint_rows    = leer_csvs_recientes(dias)
    existentes    = leer_normativa_existente()
    nuevas        = []
    stats         = {"escaneados": len(osint_rows), "nuevas": 0, "duplicadas": 0}

    for row in osint_rows:
        if not es_normativa(row):
            continue

        titulo = row.get("title", "").strip()
        url    = row.get("url", "").strip()
        if not titulo:
            continue

        h = make_hash(titulo, url)
        if h in seen:
            stats["duplicadas"] += 1
            continue

        nueva = {
            "fecha_deteccion":  date.today().isoformat(),
            "fecha_publicacion": row.get("date", ""),
            "titulo":           titulo,
            "fuente":           row.get("source", ""),
            "categoria_osint":  row.get("category", ""),
            "tipo_normativa":   inferir_tipo(row),
            "url":              url,
            "resumen":          row.get("summary", "")[:300],
            "severidad":        row.get("severity", "Info"),
            "revisado":         "",  # pendiente de revisión manual
        }
        nuevas.append(nueva)
        seen[h] = date.today().isoformat()
        stats["nuevas"] += 1

    # Combinar con existentes (que no hayan sido borradas) y guardar
    todas = existentes + nuevas

    if not test_mode and nuevas:
        guardar_normativa(todas)
        save_seen(seen)

    # Resumen
    log.info(
        f"Resumen: {stats['escaneados']} escaneados / "
        f"{stats['nuevas']} nuevas / "
        f"{stats['duplicadas']} duplicadas / "
        f"{len(todas)} total en CSV"
    )

    # Alertas email si hay normativa de severidad Alta/Crítica
    alertas = [n for n in nuevas if n["severidad"] in ALERT_SEVERITIES]
    if alertas and not test_mode:
        log.info(f"Normativa de alta prioridad: {len(alertas)} — lanzando alerta email...")
        _lanzar_alerta(alertas)
    elif alertas and test_mode:
        log.info(f"[TEST] Se enviaría alerta para {len(alertas)} normativa(s) de alta prioridad")

    # Imprimir resumen en modo test
    if test_mode or nuevas:
        _print_resumen(nuevas)

    return nuevas


def _lanzar_alerta(alertas: list[dict]):
    """Llama a normativa_alert.py pasando las alertas como JSON temporal."""
    if not ALERT_SCRIPT.exists():
        log.warning(f"{ALERT_SCRIPT} no encontrado — email no enviado")
        return
    tmp = DATA_DIR / ".alert_tmp.json"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(alertas, f, ensure_ascii=False)
        result = subprocess.run(
            [sys.executable, str(ALERT_SCRIPT), str(tmp)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            log.info("Email de alerta enviado correctamente")
        else:
            log.warning(f"Error al enviar email: {result.stderr[:200]}")
    except Exception as e:
        log.warning(f"No se pudo lanzar alerta: {e}")
    finally:
        tmp.unlink(missing_ok=True)


def _print_resumen(nuevas: list[dict]):
    print(f"\n{'='*62}")
    print(f"  NORMATIVA NUEVA DETECTADA — {date.today()}")
    print(f"{'='*62}")
    if not nuevas:
        print("  Sin normativa nueva en el periodo.")
    for n in nuevas:
        sev_icon = {"Crítica": "🔴", "Alta": "🟠", "Media": "🟡"}.get(n["severidad"], "⚪")
        print(f"\n  {sev_icon} [{n['severidad']:>7}] {n['titulo'][:70]}")
        print(f"     Fuente : {n['fuente']}")
        print(f"     Tipo   : {n['tipo_normativa']}")
        print(f"     Fecha  : {n['fecha_publicacion']}")
        print(f"     URL    : {n['url'][:70]}")
    print(f"\n  Total nuevas: {len(nuevas)}")
    print(f"{'='*62}\n")

# ============================================================
# === PUNTO DE ENTRADA ===
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Vigilancia de normativa nueva — AdminDash OSINT"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Modo test: verbose sin guardar CSV ni actualizar caché"
    )
    parser.add_argument(
        "--dias", type=int, default=DEFAULT_DIAS_CSV, metavar="N",
        help=f"Días de CSVs a escanear (default: {DEFAULT_DIAS_CSV})"
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="Limpiar caché de normativa vista (fuerza redetección)"
    )
    args = parser.parse_args()

    if args.reset:
        if SEEN_FILE.exists():
            SEEN_FILE.unlink()
            log.info("Caché de normativa vista eliminada.")
        return

    run(test_mode=args.test, dias=args.dias)


if __name__ == "__main__":
    main()
