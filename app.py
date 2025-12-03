import streamlit as st
import pandas as pd
from src.data_loader import DataLoader

st.set_page_config(page_title="BetSight MVP", layout="wide", page_icon="⚽")

st.title("⚽ BetSight Intelligence")
st.sidebar.header("Filtros")

with st.spinner("Carregando dados da Premier League..."):
    df = DataLoader.load_data()

if not df.empty:
    st.metric("Total de Jogos", len(df))
    st.subheader("📋 Base de Dados Recente")
    st.dataframe(df.head(20), use_container_width=True)
else:
    st.error("Erro ao carregar dados.")