import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np

# --- 1. CONFIGURACIÓN DEL HANGAR (VISUAL) ---
st.set_page_config(page_title="SUR DAO - Master", layout="wide", page_icon="🌑")

# CSS: Estética Hacker / Institucional Dark
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
    .css-1aumxhk {background-color: #262730;} 
</style>
""", unsafe_allow_html=True)

# --- 2. EL REACTOR DE DATOS (CARGA INTELIGENTE) ---
@st.cache_data
def load_data():
    data_dict = {}
    
    # NOMBRES DE ARCHIVOS (Tal cual los tienes en /data)
    files = {
        "oferta": "Oferta_Academica_2025_SIES_02_06_2025_WEB_E.csv",
        "retencion": "Informe_Retencion_SIES_2025.xlsx - Retención 1er año x IES.csv",
        "movilidad": "Movilidad-Regional-2025_Anexo-13112025.xlsx - Anexo Movilidad Regional.csv",
        "duracion": "Duracion_Real_y_en-Exceso_SIES_2025.xlsx - Durac. Real y Exceso Carr.csv" 
        # Nota: Si no tienes el específico de Carreras, usa el de Sobreduración, el código intentará adaptarse.
    }

    # Helper para rutas
    def get_path(fname):
        if os.path.exists(os.path.join("data", fname)): return os.path.join("data", fname)
        if os.path.exists(fname): return fname
        return None

    # A) CARGA OFERTA (CORE)
    path = get_path(files["oferta"])
    if path:
        try:
            # Intentar leer con ; y encoding variable
            df = pd.read_csv(path, sep=';', encoding='latin1', on_bad_lines='skip', low_memory=False)
            # Limpieza Arancel
            if 'Arancel Anual' in df.columns:
                df['Arancel Anual'] = pd.to_numeric(df['Arancel Anual'].astype(str).str.replace(r'[$.]', '', regex=True), errors='coerce')
            data_dict["oferta"] = df
        except Exception as e: st.error(f"Error cargando Oferta: {e}")

    # B) CARGA RETENCIÓN (Buscador de Header)
    path = get_path(files["retencion"])
    if path:
        try:
            # Leemos las primeras 20 filas para encontrar dónde empieza la tabla
            df_raw = pd.read_csv(path, sep=',', header=None, nrows=20)
            # Buscamos la fila que contiene "Nombre de la institución"
            header_row = df_raw[df_raw.apply(lambda x: x.astype(str).str.contains('Nombre de la institución', case=False).any(), axis=1)].index[0]
            
            df_ret = pd.read_csv(path, sep=',', header=header_row)
            
            # Normalizar columnas
            col_ies = [c for c in df_ret.columns if 'Nombre de la institución' in c or 'Nombre IES' in c][0]
            # Buscamos la columna más reciente (2024, 2023...)
            cols_years = [c for c in df_ret.columns if '2024' in str(c)]
            if not cols_years: cols_years = [c for c in df_ret.columns if '2023' in str(c)]
            
            if cols_years:
                df_ret = df_ret[[col_ies, cols_years[0]]].copy()
                df_ret.columns = ['Institucion', 'Retencion']
                df_ret['Institucion'] = df_ret['Institucion'].astype(str).str.upper().str.strip()
                data_dict["retencion"] = df_ret
        except: pass

    # C) CARGA MOVILIDAD (LA JOYA)
    path = get_path(files["movilidad"])
    if path:
        try:
            df_raw = pd.read_csv(path, sep=',', header=None, nrows=20)
            # El header suele ser "Región egreso EM" vs Regiones
            h_idx = df_raw[df_raw.apply(lambda x: x.astype(str).str.contains('Región egreso EM', case=False).any(), axis=1)].index[0]
            df_mov = pd.read_csv(path, sep=',', header=h_idx)
            # Limpieza básica: Primera columna como índice
            df_mov.set_index(df_mov.columns[0], inplace=True)
            # Quedarnos solo con las columnas de regiones (limpiar totales si existen)
            data_dict["movilidad"] = df_mov
        except: pass

    # D) CARGA DURACIÓN (Opcional)
    path = get_path(files["duracion"])
    if path:
        try:
            df_raw = pd.read_csv(path, sep=',', header=None, nrows=20)
            h_idx = df_raw[df_raw.apply(lambda x: x.astype(str).str.contains('Carrera Genérica', case=False).any(), axis=1)].index[0]
            df_dur = pd.read_csv(path, sep=',', header=h_idx)
            
            col_nom = [c for c in df_dur.columns if 'Carrera Genérica' in c][0]
            col_real = [c for c in df_dur.columns if 'Duración Real 2024' in c]
            if not col_real: col_real = [c for c in df_dur.columns if 'Duración Real' in c]
            
            if col_real:
                df_dur = df_dur[[col_nom, col_real[0]]].copy()
                df_dur.columns = ['Generica', 'Duracion_Real']
                df_dur['Generica'] = df_dur['Generica'].astype(str).str.upper().str.strip()
                data_dict["duracion"] = df_dur
        except: pass

    # E) FUSIÓN MAESTRA (SIES CORE)
    if "oferta" in data_dict and "retencion" in data_dict:
        df_main = data_dict["oferta"].copy()
        
        # Mapeo de columnas Oferta
        cols_map = {}
        for c in df_main.columns:
            if 'Nombre IES' in c: cols_map['Institucion'] = c
            elif 'Nombre Carrera' in c: cols_map['Carrera'] = c
            elif 'Carrera Genérica' in c: cols_map['Generica'] = c
            elif 'Arancel Anual' in c: cols_map['Arancel'] = c
            elif 'Duración Total' in c: cols_map['Duracion_Formal'] = c
            elif 'Región Sede' in c: cols_map['Region'] = c
        
        # Filtrar solo columnas útiles y renombrar
        df_core = df_main[list(cols_map.values())].copy()
        df_core.columns = list(cols_map.keys())
        
        # Normalizar para cruce
        df_core['Institucion'] = df_core['Institucion'].astype(str).str.upper().str.strip()
        df_core['Generica'] = df_core['Generica'].astype(str).str.upper().str.strip()

        # MERGE 1: Retención (Por Institución)
        df_final = pd.merge(df_core, data_dict["retencion"], on='Institucion', how='left')
        
        # MERGE 2: Duración Real (Por Carrera Genérica) - Si existe
        if "duracion" in data_dict:
            df_final = pd.merge(df_final, data_dict["duracion"], on='Generica', how='left')
        else:
            df_final['Duracion_Real'] = df_final['Duracion_Formal'] # Fallback

        # Imputaciones y Cálculos Finales
        avg_ret = df_final['Retencion'].mean()
        df_final['Retencion'] = df_final['Retencion'].fillna(avg_ret)
        df_final['Desercion'] = 1 - df_final['Retencion']
        
        # CAPITAL EN RIESGO = Arancel * Deserción
        df_final['Capital_Riesgo'] = (df_final['Arancel'] * df_final['Desercion']) / 1000000 # MM$
        
        # TIEMPO ROB
