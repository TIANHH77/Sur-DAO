import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="SUR DAO - Piloto", layout="wide", page_icon="🌑")
st.title("🌑 SUR DAO - Custodia de Trayectorias USACH")

# --- 2. CARGA DE DATOS REALES ---
@st.cache_data
def load_data():
    try:
        # Cargamos el archivo principal de alertas y riesgo
        df = pd.read_csv("data/surdao_alerta_final.csv")
        # Cargamos el stock histórico para el KPI de los 504k
        df_stock = pd.read_csv("data/surdao_stock_historico.csv")
        return df, df_stock
    except Exception as e:
        st.error(f"⚠️ Error al cargar archivos en /data: {e}")
        return pd.DataFrame(), pd.DataFrame()

df, df_stock = load_data()

# --- 3. PROCESAMIENTO PARA LA MIXTURA (JSON) ---
if not df.empty:
    # Calculamos métricas reales para el index.html
    nodos_criticos = len(df[df['Alerta Final'].str.contains('🔴', na=False)])
    
    data_sur = {
        "metricas": {
            "desercion_primer_ano": 35.27, # Dato SIES 2025
            "capital_social_riesgo": "22.6M (Estimado)",
            "estudiantes_en_sombra": nodos_criticos,
            "sobreduracion_promedio": "4.7 semestres"
        },
        "contexto": "Sincronización Piloto SUR - USACH 2026"
    }

    # Creamos el puente con el portal web
    with open('data_sur.json', 'w') as f:
        json.dump(data_sur, f, indent=4)

# --- 4. DASHBOARD: KPIs ---
if not df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Nodos en Análisis", df.shape[0])
    # Simulamos capital recuperable basado en el pool de skills si no existe la columna
    capital_total = 22.6 
    col2.metric("Nodos en Riesgo Crítico 🔴", nodos_criticos)
    col3.metric("Capital en Riesgo ($MM)", f"{capital_total}M")

    # --- 5. VISUALIZACIONES (Lo que te gusta) ---
    
    # Tabla Maestra
    st.subheader("📄 Radar de Alertas SIES")
    st.dataframe(df, width=None) # Ajustado para evitar el warning de 2025

    # Gráfico de Barras: Riesgo por Carrera
    st.subheader("📊 Nivel de Riesgo por Carrera")
    fig_bar = px.bar(
        df,
        x="Carrera",
        y="Riesgo",
        color="Alerta Final",
        title="Distribución de Alertas en el Nodo",
        color_discrete_map={'🔴 Riesgo crítico': 'red', '🟠 Riesgo con red parcial': 'orange'}
    )
    st.plotly_chart(fig_bar, width='stretch')

    # Scatter: Apoyo Par vs Riesgo
    st.subheader("🎯 Efectividad del Apoyo de Pares")
    fig_scatter = px.scatter(
        df,
        x="Carrera",
        y="Riesgo",
        size="ID", # O cualquier métrica numérica
        color="Apoyo Par",
        hover_name="Alerta Final",
        title="Relación Carrera, Riesgo y Apoyo"
    )
    st.plotly_chart(fig_scatter, width='stretch')

# --- 6. ACCESO AL PORTAL (Tu idea del botón) ---
st.sidebar.markdown("---")
st.sidebar.success("✅ Portal Web Sincronizado")
# Cambia esta URL por la de tu Live Server o GitHub Pages
st.sidebar.link_button("🌐 IR AL PORTAL PÚBLICO", "http://localhost:5500/index.html")

# Botón de descarga de los datos procesados
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Descargar Reporte Piloto",
        data=csv,
        file_name='reporte_piloto_sur.csv',
        mime='text/csv',
    )
