import streamlit as st
import pandas as pd
import glob
import plotly.express as px
from datetime import datetime

# -----------------------------
# Configuración de página
# -----------------------------
st.set_page_config(
    page_title="OSINT Admin Digital",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo oscuro
st.markdown(
    """
    <style>
    body {background-color: #1e1e1e; color: #ffffff;}
    .stDataFrame div{color: #ffffff;}
    .main {background-color: #1e1e1e;}
    h2, h3, h4 {color: #ffffff;}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Cargar datos CSV
# -----------------------------
files = sorted(glob.glob("data/osint_*.csv"))
if not files:
    st.warning("No hay datos OSINT. Ejecuta el scraper primero.")
    st.stop()

dfs = [pd.read_csv(f) for f in files[-14:]]  # últimos 14 días
df = pd.concat(dfs, ignore_index=True)
df['date'] = pd.to_datetime(df['date'])

# -----------------------------
# Sidebar: filtros interactivos
# -----------------------------
st.sidebar.header("Filtros")
source_filter = st.sidebar.multiselect(
    "Selecciona fuente",
    options=df['source'].dropna().unique(),
    default=df['source'].dropna().unique()
)

date_min = df['date'].min()
date_max = df['date'].max()
date_filter = st.sidebar.date_input(
    "Rango de fechas",
    [date_min, date_max],
    min_value=date_min,
    max_value=date_max
)

keywords = st.sidebar.text_input("Filtrar por palabras clave (coma separadas)")
keywords_list = [k.strip().lower() for k in keywords.split(",") if k.strip()]

# Filtrado inicial
df_filtered = df[
    (df['source'].isin(source_filter)) &
    (df['date'] >= pd.to_datetime(date_filter[0])) &
    (df['date'] <= pd.to_datetime(date_filter[1]))
]

# Filtrado por palabras clave
if keywords_list:
    mask = df_filtered['title'].fillna("").str.lower().apply(lambda x: any(k in x for k in keywords_list))
    df_filtered = df_filtered[mask]

# -----------------------------
# Panel de métricas
# -----------------------------
st.title("Dashboard OSINT - Administración Digital España")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Fuentes únicas", df_filtered['source'].nunique())
col2.metric("Artículos filtrados", len(df_filtered))
col3.metric("Última fecha", df_filtered['date'].max().strftime("%Y-%m-%d"))
alert_words = ['fraude','incidencia','crisis']
col4.metric(
    "Artículos con alertas",
    df_filtered['title'].fillna("").str.lower().str.contains('|'.join(alert_words)).sum()
)

# -----------------------------
# Tabla de artículos filtrados
# -----------------------------
st.subheader("Artículos filtrados")
st.dataframe(df_filtered[['date','source','title','url']], height=300)

# -----------------------------
# Evolución diaria de capturas por fuente
# -----------------------------
st.subheader("Evolución diaria de capturas por fuente")
counts = df_filtered.groupby(['date','source']).size().reset_index(name='count')
if not counts.empty:
    fig_line = px.line(
        counts, x='date', y='count', color='source', markers=True,
        title="Artículos OSINT por día y fuente"
    )
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("No hay datos suficientes para gráfico de evolución.")

# -----------------------------
# Top 10 fuentes
# -----------------------------
st.subheader("Top 10 fuentes por número de artículos")
top_sources = df_filtered['source'].value_counts().nlargest(10).reset_index()
top_sources.columns = ['source','count']
if not top_sources.empty:
    fig_bar = px.bar(
        top_sources, x='source', y='count', color='source',
        title="Top 10 fuentes"
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No hay datos suficientes para gráfico de top fuentes.")

# -----------------------------
# Treemap jerárquico seguro
# -----------------------------
st.subheader("Distribución de artículos por fuente")
df_tree = df_filtered[df_filtered['title'].fillna("") != ""]
if not df_tree.empty:
    fig_tree = px.treemap(
        df_tree,
        path=['source','title'],
        values=[1]*len(df_tree),
        title="Treemap de artículos por fuente"
    )
    st.plotly_chart(fig_tree, use_container_width=True)
else:
    st.info("No hay datos válidos para treemap.")

# -----------------------------
# Panel de alertas
# -----------------------------
st.subheader("Artículos con alertas críticas")
df_alerts = df_filtered[df_filtered['title'].fillna("").str.lower().str.contains('|'.join(alert_words))]
if not df_alerts.empty:
    st.dataframe(df_alerts[['date','source','title','url']], height=200)
else:
    st.info("No hay artículos con alertas críticas en el periodo filtrado.")

# -----------------------------
# Indicador de zonas más activas (fuentes con más actividad)
# -----------------------------
st.subheader("Zonas / fuentes más activas")
activity = df_filtered.groupby('source').size().reset_index(name='count').sort_values('count', ascending=False)
if not activity.empty:
    fig_activity = px.bar(activity.head(10), x='source', y='count', color='source', title="Fuentes más activas")
    st.plotly_chart(fig_activity, use_container_width=True)
else:
    st.info("No hay datos para zonas activas.")

# -----------------------------
# Botón para refrescar CSV
# -----------------------------
if st.button("Refrescar datos"):
    st.experimental_rerun()
