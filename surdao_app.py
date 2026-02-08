import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np

# --- 1. CONFIGURACIÓN DEL HANGAR (ESTÉTICA SUR DAO) ---
st.set_page_config(page_title="SUR DAO - Master v5.0", layout="wide", page_icon="🌑")

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
    p, li {color: #B0B0B0 !important;}
    .big-number {font-size: 2.2em; font-weight: bold; color: #4CAF50;}
    .shame-number {font-size: 2.2em; font-weight: bold; color: #FF4B4B;}
</style>
""", unsafe_allow_html=True)

# --- 2. EL REACTOR DE DATOS (SABUESO V6) ---
@st.cache_data
def load_data():
    data_dict = {}
    
    # Palabras clave para identificar archivos aunque cambien de nombre
    keywords = {
        "oferta": ["Oferta", "Academica", "2025"],
        "retencion": ["Retencion", "IES"],
        "movilidad": ["Movilidad", "Regional"],
        "duracion": ["Duracion", "Real", "Instituciones"]
    }

    def encontrar_archivo(palabras_clave):
        for directorio in ['data', '.']:
            if os.path.exists(directorio):
                for archivo in os.listdir(directorio):
                    if all(k.lower() in archivo.lower() for k in palabras_clave):
                        return os.path.join(directorio, archivo)
        return None

    # A) CARGA OFERTA
    path_of = encontrar_archivo(keywords["oferta"])
    if path_of:
        try:
            df = pd.read_csv(path_of, sep=';', encoding='latin1', on_bad_lines='skip', low_memory=False)
            if 'Arancel Anual' in df.columns:
                df['Arancel Anual'] = pd.to_numeric(df['Arancel Anual'].astype(str).str.replace(r'[$.]', '', regex=True), errors='coerce')
            data_dict["oferta"] = df
        except: pass

    # B) CARGA RETENCIÓN
    path_ret = encontrar_archivo(keywords["retencion"])
    if path_ret:
        try:
            df_raw = pd.read_csv(path_ret, sep=',', header=None, nrows=20)
            h_idx = df_raw[df_raw.apply(lambda x: x.astype(str).str.contains('Nombre de la institución', case=False).any(), axis=1)].index[0]
            df_ret = pd.read_csv(path_ret, sep=',', header=h_idx)
            col_ies = [c for c in df_ret.columns if 'Nombre' in c and 'institución' in c][0]
            col_val = [c for c in df_ret.columns if '2024' in str(c)][0]
            df_ret = df_ret[[col_ies, col_val]].copy()
            df_ret.columns = ['Institucion', 'Retencion']
            df_ret['Institucion'] = df_ret['Institucion'].astype(str).str.upper().str.strip()
            data_dict["retencion"] = df_ret
        except: pass

    # C) CARGA MOVILIDAD
    path_mov = encontrar_archivo(keywords["movilidad"])
    if path_mov:
        try:
            df_raw_m = pd.read_csv(path_mov, sep=',', header=None, nrows=20)
            h_idx_m = df_raw_m[df_raw_m.apply(lambda x: x.astype(str).str.contains('Región egreso EM', case=False).any(), axis=1)].index[0]
            df_mov = pd.read_csv(path_mov, sep=',', header=h_idx_m)
            df_mov.set_index(df_mov.columns[0], inplace=True)
            data_dict["movilidad"] = df_mov
        except: pass

    # D) FUSIÓN MAESTRA
    if "oferta" in data_dict and "retencion" in data_dict:
        df_of = data_dict["oferta"].copy()
        # Mapeo flexible
        cols = {
            'Institucion': [c for c in df_of.columns if 'Nombre IES' in c][0],
            'Carrera': [c for c in df_of.columns if 'Nombre Carrera' in c][0],
            'Generica': [c for c in df_of.columns if 'Carrera Genérica' in c][0],
            'Arancel': 'Arancel Anual',
            'Duracion': [c for c in df_of.columns if 'Duración Total' in c][0],
            'Region': [c for c in df_of.columns if 'Región Sede' in c][0]
        }
        df_core = df_of[list(cols.values())].copy()
        df_core.columns = list(cols.keys())
        df_core['Institucion'] = df_core['Institucion'].astype(str).str.upper().str.strip()
        
        df_master = pd.merge(df_core, data_dict["retencion"], on='Institucion', how='left')
        df_master['Retencion'] = pd.to_numeric(df_master['Retencion'], errors='coerce').fillna(df_master['Retencion'].mean())
        df_master['Desercion'] = 1 - df_master['Retencion']
        df_master['Capital_Riesgo'] = (df_master['Arancel'] * df_master['Desercion']) / 1000000
        
        data_dict["master"] = df_master

    return data_dict

db = load_data()

# --- 3. DASHBOARD ---
if "master" in db:
    df = db["master"]
    
    with st.sidebar:
        st.title("🎛️ SUR DAO Control")
        st.divider()
        meta = st.slider("Meta Recuperación (%)", 0, 100, 15)
        st.divider()
        regiones = ["Todas"] + sorted(df['Region'].unique().tolist())
        sel_reg = st.selectbox("Región", regiones)
        if sel_reg != "Todas":
            df = df[df['Region'] == sel_reg]

    # Cálculos dinámicos
    total_r = df['Capital_Riesgo'].sum()
    rescate = total_r * (meta/100)

    st.title("🌑 SUR DAO: Auditoría de Capital Humano")
    
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='metric-card'><h3>💸 Sangría Actual</h3><p class='shame-number'>${total_r:,.0f} MM</p></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='metric-card'><h3>🛡️ Rescate Simulado</h3><p class='big-number'>${rescate:,.0f} MM</p></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='metric-card'><h3>⚖️ Base Habilitante</h3><p class='big-number'>Res. 1983</p></div>", unsafe_allow_html=True)

    st.divider()

    t1, t2, t3 = st.tabs(["📊 Radar SIES", "⚖️ Hacking Legal", "🗺️ Movilidad"])

    with t1:
        # Gráfico Instituciones
        df_ies = df.groupby('Institucion')['Capital_Riesgo'].sum().reset_index().sort_values('Capital_Riesgo', ascending=False).head(15)
        fig_ies = px.bar(df_ies, x='Institucion', y='Capital_Riesgo', title="MM$ en Riesgo por Institución", color_discrete_sequence=['#FF4B4B'])
        st.plotly_chart(fig_ies, use_container_width=True)

    with t2:
        st.subheader("🛠️ Aplicación de Normativa USACH")
        c_l1, c_l2 = st.columns(2)
        with c_l1:
            st.markdown("""
            <div class='legal-card'>
                <h4>Res. 8417: Formación Integral</h4>
                <p>Define actividades formativas como bienestar y construcción de comunidad. SUR DAO las certifica.</p>
            </div>
            <div class='legal-card'>
                <h4>Res. 1983: Convalidación</h4>
                <p>Reconocimiento de aprendizajes independiente del origen. El trueque es convalidable.</p>
            </div>
            """, unsafe_allow_html=True)
        with c_l2:
            st.info("Simula la conversión de horas de comunidad a créditos académicos (SCT) usando la Res. 1983.")
            h = st.number_input("Horas de Proyecto Comunitario", 0, 500, 120)
            st.success(f"Equivalencia: {int(h/27)} SCT Recuperados")

    with t3:
        if "movilidad" in db:
            st.subheader("Matriz de Migración Territorial")
            fig_m = px.imshow(db["movilidad"].iloc[0:16, 0:16], color_continuous_scale='Viridis')
            st.plotly_chart(fig_m, use_container_width=True)
        else:
            st.warning("Archivo de Movilidad no detectado.")

else:
    st.error("🚨 Datos no encontrados. Sube los archivos reales a la carpeta /data")
