import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuración inicial ---
st.set_page_config(page_title="SUR DAO Dashboard", layout="wide")
st.title("🌑 SUR DAO - Capa Sombra Dashboard")

# --- Cargar datos ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/surdao_real_matches_2025.csv")
    # Añadir columna de empleabilidad si falta
    if "Empleabilidad_%" not in df.columns:
        df["Empleabilidad_%"] = 85.0
    return df

df = load_data()

# --- Definir pestañas ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 KPIs", "📄 Tabla", "📊 Barras", "📈 Scatter", "🔵 Bubble Chart"]
)

# --- KPIs ---
with tab1:
    st.subheader("📊 Indicadores principales")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total carreras SURDAO", df.shape[0])
    col2.metric("Créditos acumulados", int(df["Creditos_Acum"].sum()))
    col3.metric("Capital recuperable ($MM)", round(df["Capital_Recuperable"].sum(), 2))

# --- Tabla ---
with tab2:
    st.subheader("📄 Tabla de Matches SURDAO-SIES")
    st.dataframe(df, use_container_width=True)

# --- Barras ---
with tab3:
    st.subheader("📊 Impacto Económico por Carrera")
    fig_bar = px.bar(
        df,
        x="Carrera_SURDAO",
        y="Capital_Recuperable",
        color="Universidad",
        text="Capital_Recuperable",
        labels={
            "Carrera_SURDAO": "Carrera",
            "Capital_Recuperable": "Capital Recuperable ($MM)"
        },
        title="Capital humano recuperable por carrera"
    )
    fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

# --- Scatter ---
with tab4:
    st.subheader("📈 Deserción vs Capital Recuperable")
    fig_scatter = px.scatter(
        df,
        x="Desercion_SIES_pct",
        y="Capital_Recuperable",
        color="Universidad",
        size="Creditos_Acum",
        hover_name="Carrera_SURDAO",
        labels={
            "Desercion_SIES_pct": "Tasa de Deserción (%)",
            "Capital_Recuperable": "Capital Recuperable ($MM)"
        },
        title="Relación entre deserción y capital recuperable"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- Bubble Chart ---
with tab5:
    st.subheader("🔵 Deserción vs Empleabilidad vs Capital Recuperable")
    fig_bubble = px.scatter(
        df,
        x="Desercion_SIES_pct",
        y="Empleabilidad_%",
        size="Capital_Recuperable",
        color="Universidad",
        hover_name="Carrera_SURDAO",
        labels={
            "Desercion_SIES_pct": "Tasa de Deserción (%)",
            "Empleabilidad_%": "Empleabilidad (%)",
            "Capital_Recuperable": "Capital Recuperable ($MM)"
        },
        title="Deserción vs Empleabilidad vs Capital Recuperable"
    )
    fig_bubble.update_traces(marker=dict(opacity=0.7, line=dict(width=1, color='DarkSlateGrey')))
    fig_bubble.update_layout(
        xaxis_title="Tasa de Deserción (%)",
        yaxis_title="Empleabilidad (%)",
        legend_title="Universidad"
    )
    st.plotly_chart(fig_bubble, use_container_width=True)


