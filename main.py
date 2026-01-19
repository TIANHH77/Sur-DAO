import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SUR DAO Dashboard", layout="wide")
st.title("🌑 SUR DAO - Capa Sombra Dashboard")
st.markdown("**SIES 2025 + USACH | Retención + Empleabilidad**")

@st.cache_data
def load_data():
    df = pd.read_csv("data/surdao_real_matches_2025.csv")
    return df

df = load_data()
st.write("Columnas:", df.columns.tolist())  # Debug

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 KPIs", "📄 Tabla", "📊 Barras", "📈 Scatter", "🔵 Bubble"])

with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Carreras", len(df))
    col2.metric("Créditos", int(df["Creditos_Acum"].sum()))
    col3.metric("Capital $MM", round(df["Capital_Recuperable"].sum(), 2))

with tab2:
    st.dataframe(df, width="stretch")

with tab3:
    fig = px.bar(df.head(10), x="Carrera_SURDAO", y="Capital_Recuperable", 
                 color="Universidad", title="Capital por Carrera")
    st.plotly_chart(fig, width="stretch")

with tab4:
    fig = px.scatter(df.head(20), x="Desercion_SIES_pct", y="Capital_Recuperable",
                     size="Creditos_Acum", color="Universidad",
                     hover_name="Carrera_SURDAO", title="Deserción vs Capital")
    st.plotly_chart(fig, width="stretch")

with tab5:
    fig = px.scatter(df.head(20), x="Desercion_SIES_pct", y="Score",
                     size="Capital_Recuperable", color="Universidad",
                     title="Deserción vs Score (Empleabilidad proxy)")
    st.plotly_chart(fig, width="stretch")

st.markdown("[Repo](https://github.com/TIANHH77/-Earth-Commons-DAO)")


