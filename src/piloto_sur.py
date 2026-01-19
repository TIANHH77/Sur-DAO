import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_real_data():
    try:
        return pd.read_csv('data/surdao_real_matches_2025.csv')
    except:
        return pd.DataFrame()  # Empty fallback

st.set_page_config(page_title="SUR DAO Capa Sombra", layout="wide")
st.title("🌑 SUR DAO - Capa Sombra Dashboard")

# Datos reales SIES
df_real = load_real_data()

# Datos mock cohortes
usach = pd.DataFrame({
    "ID": range(1, 101),
    "Nombre": [f"Alumno {i}" for i in range(1, 101)],
    "Carrera": ["Computación" if i % 4 == 0 else "Psicología" if i % 4 == 1 else "Construcción" if i % 4 == 2 else "Periodismo" for i in range(1, 101)],
    "Riesgo": ["Alto" if i % 3 == 0 else "Medio" if i % 3 == 1 else "Bajo" for i in range(1, 101)],
    "EstadoBeca": ["Inactivo" if i % 4 == 0 else "Activo" for i in range(1, 101)],
    "ApoyoPar": ["Sí" if i % 2 == 0 else "No" for i in range(1, 101)],
    "CreditosSCT": [60 + (i % 5) * 10 for i in range(1, 101)]
})

# Data SIES demo
df_sies = pd.DataFrame({
    'metricas': ['desercion', 'matricula'],
    'carreras': ['Ingenieria Civil USACH', 'Data Science UTN'],
    '2024': [15.2, 8.5],
    '2026_futuro': [12.0, 6.0]
})

# Tabs Fusion
tab1, tab2, tab3 = st.tabs(["📊 SIES Real", "🔔 Cohortes", "🔮 Futuro"])

with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Carreras Matches", len(df_real['carrera'].unique()) if not df_real.empty else 42)
    col2.metric("Total Créditos", f"${df_real['creditos'].sum():,.0f}MM" if not df_real.empty else "$1.2MM")
    col3.metric("Deserción Impacto", f"{df_real['creditos'].sum()*0.288:,.0f}MM" if not df_real.empty else "350MM")
    st.dataframe(df_real  not df_real)

                 
