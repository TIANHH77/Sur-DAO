import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata
import json
import os

# --- 1. NORMALIZACIÓN ---
def normalize_columns(df):
    def clean(col):
        col = col.strip().lower()
        col = unicodedata.normalize('NFKD', col).encode('ascii', errors='ignore').decode('utf-8')
        return col
    df.columns = [clean(c) for c in df.columns]
    return df

# --- 2. CONFIGURACIÓN ---
st.set_page_config(page_title="SUR DAO - Capa Sombra", layout="wide", page_icon="🌑")
st.title("🌑 SUR DAO - Capa Sombra")

# --- 3. CARGA Y MERGE DE LOS 3 ARCHIVOS ---
@st.cache_data
def load_sur_data():
    try:
        # 1. El Pool de Skills y Valor Sombra
        df_pool = pd.read_csv("data/surdao_pool_skills.csv")
        # 2. El Radar de Alerta (Riesgo y Becas)
        df_alerta = pd.read_csv("data/surdao_alerta_final.csv")
        # 3. El Stock Histórico (Los 500k)
        df_stock = pd.read_csv("data/surdao_stock_historico.csv")
        
        # Limpiamos nombres para el merge
        df_pool = normalize_columns(df_pool)
        df_alerta = normalize_columns(df_alerta)
        
        return df_pool, df_alerta, df_stock
    except Exception as e:
        st.error(f"Faltan archivos en /data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_pool, df_alerta, df_stock = load_sur_data()

# --- 4. SINCRONIZACIÓN CON EL PORTAL (JSON) ---
if not df_alerta.empty:
    # Calculamos métricas para el index.html
    alertas_rojas = len(df_alerta[df_alerta['alerta final'].str.contains('🔴', na=False)])
    becas_inactivas = len(df_alerta[df_alerta['beca'] == 'Inactivo'])
    
    data_sur = {
        "metricas": {
            "estudiantes_riesgo_alto": alertas_rojas,
            "becas_inactivas": becas_inactivas,
            "stock_sombra": "504,000"
        }
    }
    with open('data_sur.json', 'w') as f:
        json.dump(data_sur, f, indent=4)
    st.sidebar.success("✅ Portal index.html Sincronizado")

# --- 5. VISUALIZACIÓN ---
tab1, tab2, tab3 = st.tabs(["📊 Radar de Riesgo", "🌑 Capa de Sombra", "📜 Normativa"])

with tab1:
    st.subheader("Estado de Trayectorias (USACH)")
    st.dataframe(df_alerta, use_container_width=True)
    
    if 'riesgo' in df_alerta.columns:
        fig = px.pie(df_alerta, names='riesgo', title="Distribución de Riesgo en el Nodo")
        st.plotly_chart(fig)

with tab2:
    st.subheader("Pool de Valor y Skills Perdidos")
    st.table(df_pool)
    st.info("Este capital circula en la sombra mientras el sistema oficial lo ignora.")

with tab3:
    st.subheader("Respaldo Legal")
    st.markdown("""
    **Resolución Exenta 008417 (USACH)**
    - *Art. 1:* La formación integral busca el bienestar del estudiante.
    - *Art. 6:* Reconocimiento de competencias transversales mediante créditos SCT.
    - *Situación:* El SUR DAO opera donde la institución deja de acompañar.
    """)

# Botón de "Ancla" sugerido para no perderse
st.sidebar.markdown("---")
if st.sidebar.button("↓ Ir al Final (Nuevos Datos)"):
    st.markdown('<div id="final"></div>', unsafe_allow_html=True)
