import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuración inicial ---
st.set_page_config(page_title="SUR DAO Dashboard", layout="wide")
st.title("🌑 SUR DAO - Capa Sombra Dashboard")
st.markdown("**Datos reales SIES 2025 + USACH | Retención + Empleabilidad**")

# --- Cargar datos ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/surdao_real_matches_2025.csv")
    except:
        df = pd.read_csv("data/surdao_super_matches_2026.csv")
    # Añadir columna empleabilidad default si falta
    if "Empleabilidad_%" not in df.columns:
        df["Empleabilidad_%"] = 85.0
    return df

df = load_data()

# --- Definir pestañas ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 KPIs", "📄 Tabla", "📊 Barras", "📈 Scatter", "🔵 Bubble Chart"
])

# --- KPIs ---
with tab1:
    st.subheader("📊 Indicadores principales")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total carreras", df.shape[0])
    col2.metric("Créditos SCT", int(df.get("creditos_sct", df.get("Creditos_Acum", 0)).sum()))
    col3.metric("Capital $MM", round(df.get("impacto_mm", df.get("Capital_Recuperable", 0)).sum(), 2))

# --- Tabla ---
with tab2:
    st.subheader("📄 Matches SURDAO-SIES")
    st.dataframe(df, use_container_width=True)

# --- Barras ---
with tab3:
    st.subheader("📊 Impacto por Carrera")
    y_col = df.get("impacto_mm", df.get("Capital_Recuperable", "creditos_sct"))
    fig_bar = px.bar(df.head(10), x=df.columns[0], y=y_col, 
                     title="Capital humano por carrera (Top 10)")
    st.plotly_chart(fig_bar, use_container_width=True)

# --- Scatter ---
with tab4:
    st.subheader("📈 Deserción vs Capital")
    x_col = df.get("desercion_pct", df.get("Desercion_SIES_pct", 0))
    fig_scatter = px.scatter(df.head(20), x=x_col, y=y_col, 
                             size=df.get("creditos_sct", 10), 
                             title="Relación deserción-capital")
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- Bubble Chart ---
with tab5:
    st.subheader("🔵 Deserción vs Empleabilidad vs Capital")
    fig_bubble = px.scatter(df.head(20), 
                            x=df.get("desercion_pct", 30), 
                            y=df.get("Empleabilidad_%", 85), 
                            size=y_col,
                            title="Bubble: Deserción vs Empleabilidad")
    st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("---")
st.markdown("[Repo GitHub](https://github.com/TIANHH77/-Earth-Commons-DAO)")


