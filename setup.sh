#!/bin/bash
# =============================================================
# setup.sh — Instalación completa del proyecto AdminDash OSINT
# Dashboard Administración Digital España
# M. Castillo · mybloggingnotes@gmail.com
#
# Uso: bash setup.sh
# Incluye: venv, dependencias, cron, servicio systemd
# =============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
LOG_DIR="$SCRIPT_DIR/logs"
DATA_DIR="$SCRIPT_DIR/data"
SERVICE_NAME="admindash"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
USER_NAME="$(whoami)"

echo "=============================================="
echo "  Setup AdminDash OSINT — Admin Digital ES   "
echo "  Usuario: $USER_NAME · Dir: $SCRIPT_DIR      "
echo "=============================================="
echo ""

# ── 1. Directorios ────────────────────────────────────────────
echo "[1/6] Creando directorios..."
mkdir -p "$DATA_DIR" "$LOG_DIR"
echo "      OK: data/ logs/"

# ── 2. Entorno virtual ────────────────────────────────────────
echo "[2/6] Configurando entorno virtual Python..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "      Creado: $VENV_DIR"
else
    echo "      Ya existe: $VENV_DIR"
fi

# ── 3. Dependencias ───────────────────────────────────────────
echo "[3/6] Instalando dependencias..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"
echo "      Instaladas: streamlit, plotly, pandas, reportlab, feedparser..."

# Verificar versión de streamlit instalada
ST_VER=$("$VENV_DIR/bin/python3" -c "import streamlit; print(streamlit.__version__)" 2>/dev/null || echo "?")
echo "      Streamlit: $ST_VER"

# ── 4. Cron para scraper ──────────────────────────────────────
echo "[4/6] Configurando cron para scraper OSINT..."
CRON_CMD="0 6 * * * cd $SCRIPT_DIR && $VENV_DIR/bin/python3 osint_scraper.py >> $LOG_DIR/scraper.log 2>&1"
CRON_COMMENT="# OSINT Scraper — AdminDash (M. Castillo)"
CRON_TMP="$LOG_DIR/.crontab_backup_$(date +%Y%m%d_%H%M%S).txt"

# Volcar cron actual a fichero temporal (nunca se pierde nada)
crontab -l 2>/dev/null > "$CRON_TMP" || true
echo "      Backup del cron actual: $CRON_TMP"

if grep -qF "osint_scraper.py" "$CRON_TMP" 2>/dev/null; then
    echo "      Cron ya configurado. Sin cambios."
else
    # Añadir SOLO la línea nueva al final del fichero temporal
    echo "" >> "$CRON_TMP"
    echo "$CRON_COMMENT" >> "$CRON_TMP"
    echo "$CRON_CMD" >> "$CRON_TMP"

    # Instalar el crontab desde el fichero (no desde pipe)
    crontab "$CRON_TMP"

    # Verificar que se instaló correctamente
    if crontab -l 2>/dev/null | grep -qF "osint_scraper.py"; then
        echo "      Cron añadido: todos los días a las 06:00 AM"
        echo "      Backup guardado en: $CRON_TMP"
    else
        echo "      ⚠ ERROR: el cron no se instaló. Backup en: $CRON_TMP"
        echo "      Puedes restaurarlo manualmente con: crontab $CRON_TMP"
    fi
fi

# ── 5. Servicio systemd para dashboard ────────────────────────
echo "[5/6] Configurando servicio systemd para el dashboard..."

if [ "$EUID" -ne 0 ]; then
    echo "      ⚠ No es root — copiando service con sudo..."
    sudo bash -c "cat > $SERVICE_FILE" << SVCEOF
[Unit]
Description=Dashboard Administración Digital España (Streamlit)
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$SCRIPT_DIR
ExecStart=$VENV_DIR/bin/streamlit run dashboard.py \\
    --server.address 0.0.0.0 \\
    --server.port 8501 \\
    --server.headless true \\
    --server.runOnSave false \\
    --browser.gatherUsageStats false
Restart=on-failure
RestartSec=10
StandardOutput=append:$LOG_DIR/streamlit.log
StandardError=append:$LOG_DIR/streamlit.log

[Install]
WantedBy=multi-user.target
SVCEOF
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl restart "$SERVICE_NAME"
    echo "      Servicio habilitado y arrancado: $SERVICE_NAME"
else
    cat > "$SERVICE_FILE" << SVCEOF
[Unit]
Description=Dashboard Administración Digital España (Streamlit)
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$SCRIPT_DIR
ExecStart=$VENV_DIR/bin/streamlit run dashboard.py \\
    --server.address 0.0.0.0 \\
    --server.port 8501 \\
    --server.headless true \\
    --server.runOnSave false \\
    --browser.gatherUsageStats false
Restart=on-failure
RestartSec=10
StandardOutput=append:$LOG_DIR/streamlit.log
StandardError=append:$LOG_DIR/streamlit.log

[Install]
WantedBy=multi-user.target
SVCEOF
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    systemctl restart "$SERVICE_NAME"
    echo "      Servicio habilitado y arrancado: $SERVICE_NAME"
fi

# ── 6. Generar PDF de la guía ─────────────────────────────────
echo "[6/6] Generando guía PDF inicial..."
if [ -f "$SCRIPT_DIR/gen_guia.py" ]; then
    "$VENV_DIR/bin/python3" "$SCRIPT_DIR/gen_guia.py" 2>/dev/null && \
        echo "      Guía generada: data/guia_admindash.pdf" || \
        echo "      ⚠ No se pudo generar la guía (no crítico)"
else
    echo "      gen_guia.py no encontrado — se generará desde el dashboard"
fi

# ── Resumen ───────────────────────────────────────────────────
IP=$(hostname -I | awk '{print $1}')
echo ""
echo "=============================================="
echo "  Instalación completada"
echo "=============================================="
echo ""
echo "  Dashboard:    http://${IP}:8501"
echo "  Scraper cron: 06:00 AM diario"
echo ""
echo "  Comandos de gestión:"
echo "    Ver estado:      sudo systemctl status $SERVICE_NAME"
echo "    Parar:           sudo systemctl stop $SERVICE_NAME"
echo "    Reiniciar:       sudo systemctl restart $SERVICE_NAME"
echo "    Ver log dash:    tail -f $LOG_DIR/streamlit.log"
echo "    Ver log scraper: tail -f $LOG_DIR/scraper.log"
echo "    Ejecutar scraper ahora: venv/bin/python3 osint_scraper.py"
echo "    Auditar fuentes: venv/bin/python3 osint_scraper.py --audit"
echo ""
