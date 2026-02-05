import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# --- 1. CONFIGURACIÓN DEL HANGAR ---
st.set_page_config(page_title="SUR DAO - Piloto", layout="wide", page_icon="🌑")
st.title("🌑 SUR DAO - Custodia de Trayectorias USACH")

# --- 2. CARGA DE DATOS ---
@st.cache_data
def load_data():
    try:
        # Cargamos el radar de alertas
        df = pd.read_csv("data/surdao_alerta_final.csv")
        return df
    except Exception as e:
        st.error(f"⚠️ Error: No se encuentran los CSV en /data. {e}")
        return pd.DataFrame()

df = load_data()

# --- 3. PROCESAMIENTO Y MIXTURA (JSON) ---
if not df.empty:
    # Identificamos nodos críticos para el portal
    nodos_criticos = len(df[df['Alerta Final'].str.contains('🔴', na=False)])
    
    # Preparamos el ADN para el index.html
    data_sur = {
        "metricas": {
            "desercion_primer_ano": 35.27,
            "capital_social_riesgo": "22.6M (Estimado)",
            "estudiantes_en_sombra": nodos_criticos,
            "sobreduracion_promedio": "4.7 semestres"
        },
        "contexto": "Sincronización Piloto SUR - USACH 2026"
    }

    # Creamos el puente de datos
    with open('data_sur.json', 'w') as f:
        json.dump(data_sur, f, indent=4)

# --- 4. DASHBOARD: KPIs MAESTROS ---
if not df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Nodos en Análisis", df.shape[0])
    col2.metric("Alerta Crítica 🔴", nodos_criticos)
    col3.metric("Brecha Sombra", "4.7 Semestres")

    # --- 5. VISUALIZACIONES (El poder del dato) ---
    
    # Gráfico de Barras: Riesgo por Carrera
    st.subheader("📊 Distribución de Riesgo por Carrera")
    fig_bar = px.bar(
        df,
        x="Carrera",
        y="Riesgo",
        color="Alerta Final",
        title="Impacto del SIES por Unidad Académica",
        color_discrete_map={'🔴 Riesgo crítico': 'red', '🟠 Riesgo con red parcial': 'orange'},
        width=None # Nueva sintaxis para evitar warnings
    )
    st.plotly_chart(fig_bar, width='stretch')

    # Gráfico de la Brecha (El Abismo)
    st.subheader("⏳ El Abismo de la Sobreduración")
    df_dur = pd.DataFrame({
        'Estado': ['Promesa (Acreditación)', 'Realidad (Capa Sombra)'],
        'Semestres': [10, 14.7]
    })
    fig_dur = px.bar(
        df_dur, x='Estado', y='Semestres', color='Estado',
        text='Semestres', title="4.7 Semestres de Capital Humano No Reconocido",
        color_discrete_map={'Promesa (Acreditación)': '#4A90E2', 'Realidad (Capa Sombra)': '#E94E77'}
    )
    st.plotly_chart(fig_dur, width='stretch')

# --- 6. BARRA LATERAL Y BOTÓN DE SALIDA ---
st.sidebar.markdown("---")
st.sidebar.subheader("🚀 Salida al Exterior")
st.sidebar.success("✅ Portal Web Sincronizado")

# AQUÍ ESTÁ EL BOTÓN MAESTRO
st.sidebar.link_button(
    "🌐 IR AL PORTAL PÚBLICO", 
    "http://74.249.85.193:8502" # Tu IP actual
)

st.sidebar.info("""
    Este dashboard procesa la 'Capa Sombra' de la USACH. 
    Al presionar el botón, verás cómo estos datos se 
    convierten en valor real en tu index.html.
""")

# Descarga de seguridad
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 Bajar Reporte SIES", csv, "piloto_sur_report.csv", "text/csv")
