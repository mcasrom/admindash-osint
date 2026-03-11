#!/usr/bin/env python3
"""
normativa_alert.py
==================
Envía email de alerta cuando normativa_watch.py detecta
normativa nueva de severidad Alta o Crítica.

Usa exclusivamente smtplib (stdlib) — sin dependencias externas.

Configuración: edita la sección CONFIGURACIÓN DE EMAIL más abajo,
o usa variables de entorno para no guardar credenciales en disco:

    export NORMATIVA_EMAIL_FROM="tucuenta@gmail.com"
    export NORMATIVA_EMAIL_PASS="tu_app_password"
    export NORMATIVA_EMAIL_TO="destino@ejemplo.com"

Para Gmail necesitas una "App Password" (contraseña de aplicación),
no tu contraseña normal. Créala en:
    https://myaccount.google.com/apppasswords

Uso:
    python3 normativa_alert.py data/.alert_tmp.json   # llamado por normativa_watch.py
    python3 normativa_alert.py --test                  # test de conexión SMTP

Autor: M. Castillo · mybloggingnotes@gmail.com
"""

import os
import sys
import json
import smtplib
import logging
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date, datetime
from pathlib import Path

# ============================================================
# === CONFIGURACIÓN DE EMAIL ===
# Edita estos valores O usa variables de entorno (recomendado)
# ============================================================

EMAIL_FROM  = os.environ.get("NORMATIVA_EMAIL_FROM", "tucuenta@gmail.com")
EMAIL_PASS  = os.environ.get("NORMATIVA_EMAIL_PASS", "")          # App Password Gmail
EMAIL_TO    = os.environ.get("NORMATIVA_EMAIL_TO",   "mybloggingnotes@gmail.com")
SMTP_HOST   = os.environ.get("NORMATIVA_SMTP_HOST",  "smtp.gmail.com")
SMTP_PORT   = int(os.environ.get("NORMATIVA_SMTP_PORT", "587"))

# ============================================================
# === LOGGING ===
# ============================================================

Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("normativa_alert")

# ============================================================
# === CONSTRUCCIÓN DEL EMAIL ===
# ============================================================

def build_email(alertas: list[dict]) -> MIMEMultipart:
    """Construye el email con resumen de normativa nueva."""
    n_critica = sum(1 for a in alertas if a.get("severidad") == "Crítica")
    n_alta    = sum(1 for a in alertas if a.get("severidad") == "Alta")

    asunto = (
        f"[AdminDash] 🔔 {len(alertas)} normativa(s) nueva(s) — "
        f"{date.today().isoformat()}"
    )
    if n_critica:
        asunto = f"[AdminDash] 🔴 {n_critica} CRÍTICA(S) + {n_alta} alta(s) — {date.today().isoformat()}"

    # ── HTML ──────────────────────────────────────────────────
    filas_html = ""
    for a in alertas:
        sev   = a.get("severidad", "Info")
        color = {"Crítica": "#b71c1c", "Alta": "#e65100",
                 "Media": "#f9a825"}.get(sev, "#546e7a")
        badge = f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:12px">{sev}</span>'
        url   = a.get("url", "")
        enlace = f'<a href="{url}" style="color:#1565c0">Ver documento</a>' if url else "—"
        filas_html += f"""
        <tr style="border-bottom:1px solid #eceff1">
          <td style="padding:8px 6px">{badge}</td>
          <td style="padding:8px 6px;font-weight:600">{a.get('titulo','')[:90]}</td>
          <td style="padding:8px 6px;color:#546e7a;font-size:13px">{a.get('fuente','')}</td>
          <td style="padding:8px 6px;color:#546e7a;font-size:13px">{a.get('tipo_normativa','')}</td>
          <td style="padding:8px 6px;color:#546e7a;font-size:13px">{a.get('fecha_publicacion','')}</td>
          <td style="padding:8px 6px;font-size:13px">{enlace}</td>
        </tr>"""

    html = f"""
    <html><body style="font-family:Arial,sans-serif;color:#263238;max-width:900px;margin:auto">
      <div style="background:#0d47a1;padding:20px 24px;border-radius:8px 8px 0 0">
        <h2 style="color:#fff;margin:0">🇪🇸 Dashboard Administración Digital España</h2>
        <p style="color:#e3f2fd;margin:4px 0 0">Alerta de Normativa Nueva · {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
      </div>
      <div style="background:#e3f2fd;padding:12px 24px;border-left:4px solid #0d47a1">
        <strong>{len(alertas)} normativa(s) nueva(s)</strong> detectadas con severidad Alta o Crítica.
        Revisa el dashboard o el archivo <code>data/normativa_nuevas.csv</code>
        para marcarlas como revisadas.
      </div>
      <div style="padding:16px 0">
        <table style="width:100%;border-collapse:collapse;font-size:14px">
          <thead>
            <tr style="background:#f5f5f5;text-align:left">
              <th style="padding:8px 6px">Severidad</th>
              <th style="padding:8px 6px">Título</th>
              <th style="padding:8px 6px">Fuente</th>
              <th style="padding:8px 6px">Tipo</th>
              <th style="padding:8px 6px">Fecha</th>
              <th style="padding:8px 6px">Enlace</th>
            </tr>
          </thead>
          <tbody>{filas_html}</tbody>
        </table>
      </div>
      <div style="background:#fafafa;border-top:1px solid #eceff1;padding:12px 24px;font-size:12px;color:#78909c">
        <strong>Acción recomendada:</strong> revisa cada documento y, si procede,
        añádelo manualmente a la sección <em>Referencias Documentales</em> del dashboard.<br><br>
        Generado por <strong>normativa_watch.py</strong> ·
        M. Castillo · mybloggingnotes@gmail.com ·
        © 2026
      </div>
    </body></html>
    """

    # ── Texto plano (fallback) ────────────────────────────────
    texto_plano = f"ALERTA NORMATIVA NUEVA — {date.today()}\n{'='*60}\n\n"
    for a in alertas:
        texto_plano += (
            f"[{a.get('severidad','?'):>7}] {a.get('titulo','')}\n"
            f"  Fuente : {a.get('fuente','')}\n"
            f"  Tipo   : {a.get('tipo_normativa','')}\n"
            f"  Fecha  : {a.get('fecha_publicacion','')}\n"
            f"  URL    : {a.get('url','')}\n\n"
        )
    texto_plano += "\nRevisa data/normativa_nuevas.csv para marcarlas como revisadas.\n"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"]    = EMAIL_FROM
    msg["To"]      = EMAIL_TO
    msg.attach(MIMEText(texto_plano, "plain", "utf-8"))
    msg.attach(MIMEText(html,        "html",  "utf-8"))

    return msg

# ============================================================
# === ENVÍO ===
# ============================================================

def send_email(alertas: list[dict]) -> bool:
    """Envía el email. Devuelve True si se envió correctamente."""
    if not EMAIL_PASS:
        log.error(
            "EMAIL_PASS no configurado. Exporta la variable de entorno:\n"
            "  export NORMATIVA_EMAIL_PASS='tu_app_password_gmail'\n"
            "O edita EMAIL_PASS en normativa_alert.py"
        )
        return False

    msg = build_email(alertas)
    try:
        log.info(f"Conectando a {SMTP_HOST}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_FROM, EMAIL_PASS)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        log.info(f"Email enviado a {EMAIL_TO} — {len(alertas)} normativa(s)")
        return True
    except smtplib.SMTPAuthenticationError:
        log.error(
            "Error de autenticación SMTP. Verifica:\n"
            "  1. EMAIL_FROM y EMAIL_PASS correctos\n"
            "  2. Usas App Password de Gmail (no la contraseña normal)\n"
            "  3. Verificación en 2 pasos activada en la cuenta Gmail"
        )
    except smtplib.SMTPException as e:
        log.error(f"Error SMTP: {e}")
    except Exception as e:
        log.error(f"Error inesperado al enviar email: {e}")
    return False


def test_conexion():
    """Prueba la conexión SMTP sin enviar email real."""
    if not EMAIL_PASS:
        log.error("EMAIL_PASS no configurado.")
        return False
    try:
        log.info(f"Test conexión SMTP — {SMTP_HOST}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_FROM, EMAIL_PASS)
        log.info("✅ Conexión SMTP correcta. Credenciales válidas.")

        # Enviar email de prueba real
        alertas_test = [{
            "titulo":           "TEST — Normativa de prueba",
            "fuente":           "normativa_alert.py --test",
            "tipo_normativa":   "Test de conexión",
            "fecha_publicacion": date.today().isoformat(),
            "url":              "https://admindash-osint.streamlit.app",
            "resumen":          "Este es un email de prueba del sistema de alertas.",
            "severidad":        "Alta",
        }]
        msg = build_email(alertas_test)
        msg["Subject"] = f"[AdminDash TEST] Verificación de alertas — {date.today()}"
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASS)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        log.info(f"✅ Email de prueba enviado a {EMAIL_TO}")
        return True
    except Exception as e:
        log.error(f"❌ Error: {e}")
        return False

# ============================================================
# === PUNTO DE ENTRADA ===
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Alertas email de normativa nueva — AdminDash OSINT"
    )
    parser.add_argument(
        "json_file", nargs="?",
        help="Fichero JSON con lista de alertas (generado por normativa_watch.py)"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Test de conexión SMTP + envío de email de prueba"
    )
    args = parser.parse_args()

    if args.test:
        test_conexion()
        return

    if not args.json_file:
        parser.print_help()
        sys.exit(1)

    json_path = Path(args.json_file)
    if not json_path.exists():
        log.error(f"Fichero no encontrado: {json_path}")
        sys.exit(1)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            alertas = json.load(f)
    except Exception as e:
        log.error(f"No se pudo leer {json_path}: {e}")
        sys.exit(1)

    if not alertas:
        log.info("Sin alertas que enviar.")
        return

    ok = send_email(alertas)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
