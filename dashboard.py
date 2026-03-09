import streamlit as st
import pandas as pd
import glob
import plotly.express as px

st.set_page_config(page_title="OSINT Administración Digital", layout="wide")
st.title("Dashboard OSINT - Administración Digital España")

files = glob.glob("data/osint_*.csv")
dfs = [pd.read_csv(f) for f in files[-7:]]  # Últimos 7 días
df = pd.concat(dfs, ignore_index=True)

st.metric("Fuentes capturadas", df['source'].nunique())
st.metric("Artículos recientes", len(df))

st.subheader("Últimas noticias / datos")
st.dataframe(df[['date','source','title','url']])

counts = df.groupby(['date','source']).size().reset_index(name='count')
fig = px.line(counts, x='date', y='count', color='source', markers=True, title="Evolución diaria de capturas")
st.plotly_chart(fig, use_container_width=True)
