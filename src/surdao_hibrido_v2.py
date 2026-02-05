import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="SurDAO v8.7")

@st.cache_data
def load_data():
    if not os.path.exists("data"):
        st.error("🚨 Hangar vacío: La carpeta 'data' no existe.")
        return None, None, None
    
    archivos = os.listdir("data")
    try:
        # 1. Buscamos por palabras clave y extensión .xlsx
        f_nacional = [f for f in archivos if "Terapia" in f and f.endswith(".xlsx")][0]
        f_match = [f for f in archivos if "USACH" in f and f.endswith(".xlsx")][0]
        f_evo = [f for f in archivos if "Compendio" in f and f.endswith(".xlsx")][0]

        # 2. Carga de Excels (Requiere openpyxl en requirements.txt)
        df_nacional = pd.read_excel(f"data/{f_nacional}")
        df_match = pd.read_excel(f"data/{f_match}")
        df_evo = pd.read_excel(f"data/{f_evo}", skiprows=4)
        
        return df_nacional, df_match, df_evo
    except Exception as e:
        st.error(f"❌ Error en el radar de archivos: {e}")
        st.write("Archivos detectados:", archivos)
        return None, None, None

# --- MOTOR ---
df_to, df_story, df_evo = load_data()

# --- DASHBOARD ---
if df_to is not None:
    st.title("👐 **SurDAO Terapia Ocupacional**")
    st.markdown("### *Auditoría SIES 2025 - Nodo Santiago Tian77*")

    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Acreditación USACH", "7 Años", "Máximo Nivel")
    
    # Buscador inteligente de columna de deserción
    try:
        col_desercion = [c for c in df_to.columns if "Deser" in str(c)][0]
        media_d = pd.to_numeric(df_to[col_desercion], errors='coerce').mean()
        c2.metric("Deserción Nacional Promedio", f"{media_d:.1f}%")
    except:
        c2.metric("Deserción Nacional", "Ver tabla", "Ref: SIES 2025")

    c3.metric("Empleabilidad 1er Año", "88.9%", "USACH")

    # Comparativa
    st.subheader("🎯 Comparativa Crítica: USACH vs Central")
    st.dataframe(df_story, use_container_width=True)

    # Evolución Histórica
    st.subheader("📈 Evolución Histórica Titulados")
    # Buscamos la fila de Terapia Ocupacional en el Compendio
    row_to = df_evo[df_evo.iloc[:,0].astype(str).str.contains("Terapia Ocupacional", na=False, case=False)]
    
    if not row_to.empty:
        # SIES Compendio suele tener años en las columnas 1 a 18 (aprox)
        anios = [str(i) for i in range(2007, 2025)] 
        valores = row_to.iloc[0, 1:19].values
        fig = px.line(x=anios, y=valores, title="Crecimiento de Titulados (Fuente: SIES)", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    st.success("🚀 **Hangar Operativo:** Datos 2025 cargados con éxito.")
