import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURACIÓN DEL HANGAR (VISUAL) ---
st.set_page_config(page_title="SUR DAO - Master", layout="wide", page_icon="🌑")

st.markdown("""
<style>
    .stApp {background-color: #0E1117;}
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00FF00;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .legal-card {
        background-color: #1c202a;
        padding: 15px; border-radius: 8px; border-left: 5px solid #FFD700; margin-bottom: 10px;
    }
    h1, h2, h3 {color: #E0E0E0 !important;}
    .big-number {font-size: 2.2em; font-weight: bold; color: #4CAF50;}
    .shame-number {font-size: 2.2em; font-weight: bold; color: #FF4B4B;}
    .info-text {color: #B0B0B0;}
</style>
""", unsafe_allow_html=True)

# --- 2. EL REACTOR DE DATOS (CARGA INTELIGENTE) ---
@st.cache_data
def load_data():
    data_dict = {}
    
    # RUTAS DE ARCHIVOS (Ajustadas a tu poda)
    files = {
        "oferta": "Oferta_Academica_2025_SIES_02_06_2025_WEB_E.csv",
        "retencion": "Informe_Retencion_SIES_2025.xlsx - Retención 1er año x IES.csv",
        "movilidad": "Movilidad-Regional-2025_Anexo-13112025.xlsx - Anexo Movilidad Regional.csv",
        "duracion": "Duracion_Real_y_en-Exceso_SIES_2025.xlsx - Sobreduración de las carreras.csv"
    }

    # A) CARGA OFERTA (CORE)
    try:
        path = os.path.join("data", files["oferta"])
        df = pd.read_csv(path, sep=';', encoding='latin1', on_bad_lines='skip')
        # Limpieza Arancel
        if 'Arancel Anual' in df.columns:
            df['Arancel Anual'] = pd.to_numeric(df['Arancel Anual'].astype(str).str.replace(r'[$.]', '', regex=True), errors='coerce')
        data_dict["oferta"] = df
    except: st.warning("⚠️ Falta archivo de Oferta Académica en /data")

    # B) CARGA RETENCIÓN
    try:
        path = os.path.join("data", files["retencion"])
        # Buscamos el header dinámicamente
        df_raw = pd.read_csv(path, sep=',', header=None)
        header_idx = df_raw[df_raw.apply(lambda x: x.astype(str).str.contains('Nombre de la institución').any(), axis=1)].index[0]
        df_ret = pd.read_csv(path, sep=',', header=header_idx)
        # Normalizar
        col_ies = [c for c in df_ret.columns if 'Nombre de la institución' in c][0]
        col_val = [c for c in df_ret.columns if '2024' in str(c)][0]
        df_ret = df_ret[[col_ies, col_val]].copy()
        df_ret.columns = ['Institucion', 'Retencion']
        df_ret['Institucion'] = df_ret['Institucion'].str.upper().str.strip()
        data_dict["retencion"] = df_ret
    except: pass

    # C) CARGA MOVILIDAD (LA JOYA)
    try:
        path = os.path.join("data", files["movilidad"])
        # Header suele estar abajo
        df_mov = pd.read_csv(path, sep=',', header=None)
        h_idx = df_mov[df_mov.apply(lambda x: x.astype(str).str.contains('Región egreso EM').any(), axis=1)].index[0]
        df_mov = pd.read_csv(path, sep=',', header=h_idx)
        data_dict["movilidad"] = df_mov
    except: pass

    # D) FUSIÓN MAESTRA (SIES CORE)
    if "oferta" in data_dict and "retencion" in data_dict:
        df_main = data_dict["oferta"].copy()
        # Normalizar para cruce
        col_ies_main = [c for c in df_main.columns if 'Nombre IES' in c][0]
        df_main[col_ies_main] = df_main[col_ies_main].str.upper().str.strip()
        
        df_final = pd.merge(df_main, data_dict["retencion"], left_on=col_ies_main, right_on='Institucion', how='left')
        
        # Cálculos SUR DAO
        df_final['Retencion'] = df_final['Retencion'].fillna(df_final['Retencion'].mean())
        df_final['Desercion'] = 1 - df_final['Retencion']
        if 'Arancel Anual' in df_final.columns:
            df_final['Capital_Riesgo'] = (df_final['Arancel Anual'] * df_final['Desercion']) / 1000000 # MM$
        
        data_dict["master"] = df_final

    return data_dict

db = load_data()

# --- 3. SIDEBAR DE CONTROL ---
with st.sidebar:
    st.title("🎛️ SUR DAO Control")
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Logo_Usach.svg/1200px-Logo_Usach.svg.png", width=80)
    
    st.markdown("### 🎯 Simulador de Impacto")
    meta = st.slider("Meta Recuperación (%)", 0, 50, 15)
    
    st.markdown("### 📂 Estado de Datos")
    if "master" in db: st.success("✅ SIES Core: Activo")
    if "movilidad" in db: st.success("✅ Movilidad: Activo")
    else: st.warning("⚠️ Movilidad: Off")
    
    st.divider()
    st.caption("v2026.02 | Junín Hangar")

# --- 4. DASHBOARD MULTI-DIMENSIONAL ---
if "master" in db:
    df = db["master"]
    
    # Encabezado
    total_millones = df['Capital_Riesgo'].sum()
    recuperado_sim = total_millones * (meta/100)
    
    st.title("🌑 Protocolo SUR DAO: Auditoría Sistémica")
    st.markdown("#### *Convirtiendo la falla del sistema en infraestructura común*")
    
    # Tarjetas KPI
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f"<div class='metric-card'><h3>💸 Sangría Anual</h3><p class='shame-number'>${total_millones:,.0f} MM</p><p>Dinero quemado en deserción</p></div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='metric-card'><h3>🛡️ Rescate SUR DAO</h3><p class='big-number'>${recuperado_sim:,.0f} MM</p><p>Con {meta}% de retención</p></div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='metric-card'><h3>⚖️ Base Legal</h3><p class='big-number'>Res. 8417</p><p>Formación Integral</p></div>", unsafe_allow_html=True)
    k4.markdown(f"<div class='metric-card'><h3>🗺️ Fuga Regional</h3><p class='shame-number'>Alta</p><p>Centralismo Académico</p></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # PESTAÑAS PODEROSAS
    tabs = st.tabs(["📊 Radar Financiero", "⚖️ Hacking Normativo", "🗺️ Sangría Territorial", "⏳ Deuda de Vida"])

    # 1. RADAR FINANCIERO (El dinero manda)
    with tabs[0]:
        st.subheader("Mapa de Calor: Dónde se pierde el capital")
        col_ies = [c for c in df.columns if 'Nombre IES' in c][0]
        
        df_chart = df.groupby(col_ies)[['Capital_Riesgo', 'Desercion']].mean().reset_index()
        df_chart['Total_Riesgo'] = df.groupby(col_ies)['Capital_Riesgo'].sum().values
        df_chart = df_chart.sort_values('Total_Riesgo', ascending=False).head(15)
        
        fig = px.bar(df_chart, x=col_ies, y='Total_Riesgo', color='Desercion',
                     title="Top 15 Instituciones con mayor pérdida de capital social (MM$)",
                     color_continuous_scale='Reds', height=500)
        st.plotly_chart(fig, use_container_width=True)

    # 2. HACKING NORMATIVO (Tu as bajo la manga)
    with tabs[1]:
        st.subheader("🛠️ Infraestructura Legal Habilitante")
        c_leg1, c_leg2 = st.columns([1, 1])
        with c_leg1:
            st.markdown("""
            <div class='legal-card'>
                <h4>📄 Resolución Exenta N° 8417 (2019)</h4>
                <p><b>'Normativa de Formación Integral'</b></p>
                <p>El Art. 1 define formación integral como actividades para el <i>bienestar y la comunidad</i>.</p>
                <p>👉 <b>Hack:</b> Las actividades de SUR DAO (Ollas comunes, Archivos) caen en esta definición.</p>
            </div>
            <div class='legal-card'>
                <h4>📄 Resolución Exenta N° 1983 (2018)</h4>
                <p><b>'Reglamento de Convalidaciones'</b></p>
                <p>Permite reconocer aprendizajes <i>independiente de dónde se obtuvieron</i>.</p>
                <p>👉 <b>Hack:</b> Permite convalidar la experiencia en la Sombra por créditos académicos.</p>
            </div>
            """, unsafe_allow_html=True)
        with c_leg2:
            st.markdown("### 🧬 Simulador de Convalidación")
