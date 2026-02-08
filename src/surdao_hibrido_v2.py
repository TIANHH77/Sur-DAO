import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata
import json
import os

# --- 1. NORMALIZACIÓN GALÁCTICA ---
def normalize_columns(df):
    def clean(col):
        col = col.strip().lower()
        col = unicodedata.normalize('NFKD', col).encode('ascii', errors='ignore').decode('utf-8')
        return col
    df.columns = [clean(c) for c in df.columns]
    return df

# --- 2. CONFIGURACIÓN Y TÍTULOS ---
st.set_page_config(page_title="SUR DAO - Radar Comunitario", layout="wide", page_icon="🌑")
st.title("🌑 SUR DAO: Radar de Capital Humano y Comunitario")
st.markdown("### *Transformando la Deserción en Potencial Territorial*")

# --- 3. CARGA DE DATOS (Simulación Estratégica) ---
@st.cache_data
def load_and_prep():
    # Datos que hablan el idioma de la USACH: Territorio y Comunidad
    data = pd.DataFrame({
        "carrera": ["Terapia Ocupacional", "Ing. Civil Informática", "Psicología", "Trabajo Social", "Arquitectura"],
        "desercion_pct": [38.0, 40.5, 45.2, 32.1, 28.4],
        "impacto_mm": [1.8, 2.5, 2.3, 1.5, 2.0],
        "nodos_comunitarios": [12, 5, 18, 25, 8], # Estudiantes liderando iniciativas barriales
        "potencial_vinculacion": ["Alto", "Medio", "Muy Alto", "Crítico", "Medio"]
    })
    return data

df_master = load_and_prep()

# --- 4. DASHBOARD DE IMPACTO ---
# Métricas Clave (KPIs que duelen y KPIs que esperanza)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Deserción Promedio", "36.8%", "-2.1% vs año anterior")
col2.metric("Capital en Riesgo", "$10.1 MM", "Presupuesto perdido")
col3.metric("Nodos Comunitarios", "68 Activos", "Estudiantes en territorio")
col4.metric("Potencial Recuperación", "Alta", "Mediante Trueque de Saberes")

# --- 5. PESTAÑAS DE ANÁLISIS ---
tab1, tab2, tab3 = st.tabs(["📊 Alerta Académica", "🌱 Tejido Comunitario", "🌑 La Propuesta"])

with tab1:
    st.subheader("Mapa de Calor de Deserción")
    st.markdown("Identificación de carreras donde el sistema expulsa talento.")
    fig = px.bar(df_master, x="carrera", y="desercion_pct", color="impacto_mm",
                 title="Porcentaje de Deserción vs Impacto Económico",
                 color_continuous_scale="Reds")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("💎 El Valor Oculto: Liderazgo Territorial")
    st.markdown("""
    **La tesis:** El estudiante que abandona la academia a menudo es un líder en su comunidad. 
    Este gráfico muestra dónde está ese **Capital Comunitario** que la universidad está ignorando.
    """)
    fig2 = px.scatter(df_master, x="desercion_pct", y="nodos_comunitarios", 
                      size="impacto_mm", color="potencial_vinculacion",
                      hover_name="carrera", text="carrera",
                      title="Correlación: Deserción vs Actividad Comunitaria",
                      labels={"nodos_comunitarios": "Iniciativas Barriales Activas", "desercion_pct": "% Deserción"})
    st.plotly_chart(fig2, use_container_width=True)
    st.info("💡 **Insight:** Carreras como Terapia Ocupacional y Trabajo Social tienen alta deserción pero **altísimo impacto barrial**. Recuperarlos no es solo un tema económico, es un deber ético.")

with tab3:
    st.subheader("🔄 Modelo de Reciprocidad (La Solución)")
    st.markdown("""
    **Propuesta para la USACH:**
    1.  **Reconocer** los saberes territoriales como créditos académicos (validación de la Sombra).
    2.  **Implementar** el protocolo de Trueque Educativo: Condonación de deuda a cambio de servicio comunitario gestionado por SUR DAO.
    3.  **Habilitar** nodos de re-vinculación flexibles (sin la rigidez de la malla actual).
    """)
    st.success("✅ **Meta:** Que no se repita la historia de la exclusión por deuda. Transformar al 'deudor' en 'socio comunitario'.")

# Footer con Sello USACH (Estratégico)
st.markdown("---")
st.caption("Desarrollado por SUR DAO - Infraestructura de Resistencia Académica | Vinculado a Lab. de Innovación Social")
