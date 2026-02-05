import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata
import json
import os

# --- 1. FUNCIÓN DE NORMALIZACIÓN (El corazón del laboratorio) ---
def normalize_columns(df):
    def clean(col):
        col = col.strip().lower()
        col = unicodedata.normalize('NFKD', col).encode('ascii', errors='ignore').decode('utf-8')
        return col
    df.columns = [clean(c) for c in df.columns]
    return df

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SUR DAO - Capa Sombra", layout="wide", page_icon="🌑")
st.title("🌑 SUR DAO: Laboratorio de la Capa Sombra")

# --- 3. CARGA DE DATOS (Desde la raíz hacia /data) ---
@st.cache_data
def load_sur_data():
    try:
        # Rutas relativas desde la raíz
        df_pool = pd.read_csv("data/surdao_pool_skills.csv")
        df_alerta = pd.read_csv("data/surdao_alerta_final.csv")
        df_stock = pd.read_csv("data/surdao_stock_historico.csv")
        
        # Normalizamos para que el merge no falle
        df_pool = normalize_columns(df_pool)
        df_alerta = normalize_columns(df_alerta)
        
        return df_pool, df_alerta, df_stock
    except Exception as e:
        st.error(f"⚠️ Error de hangar: Verifica que los CSV estén en /data. {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_pool, df_alerta, df_stock = load_sur_data()

# --- 4. PROCESAMIENTO Y MIXTURA ---
if not df_alerta.empty:
    # Identificamos los nodos en riesgo real (los 🔴)
    nodos_criticos = len(df_alerta[df_alerta['alerta final'].str.contains('🔴', na=False)])
    
    # --- 🔄 SINCRONIZACIÓN CON EL PORTAL WEB ---
    data_sur = {
        "metricas": {
            "desercion_primer_ano": 35.27,  # Dato del SIES procesado
            "capital_social_riesgo": "22.6M (Estimado)",
            "estudiantes_en_sombra": nodos_criticos,
            "sobreduracion_promedio": "4.7 semestres"
        },
        "contexto": "Datos sincronizados - Laboratorio Sur DAO 2026"
    }

    with open('data_sur.json', 'w') as f:
        json.dump(data_sur, f, indent=4)
    st.sidebar.success("✅ Portal Web Sincronizado")

# --- 5. INTERFAZ STREAMLIT ---
tab1, tab2, tab3 = st.tabs(["📊 Análisis SIES", "🌑 Valor Sombra", "📜 Normativa"])

with tab1:
    st.subheader("Radar de Riesgo Académico")
    st.dataframe(df_alerta, use_container_width=True)
    if 'riesgo' in df_alerta.columns:
        fig = px.bar(df_alerta, x='carrera', y='riesgo', color='riesgo', title="Distribución de Riesgo por Nodo")
        st.plotly_chart(fig)

with tab2:
    st.subheader("Pool de Capital Humano")
    st.table(df_pool)
    st.write("Stock acumulado en 7 años:", df_stock.iloc[-1, -1] if not df_stock.empty else "504k")

with tab3:
    st.subheader("Respaldo Institucional")
    st.info("Utilizando Resolución Exenta 008417 (Formación Integral) como base de gobernanza.")
