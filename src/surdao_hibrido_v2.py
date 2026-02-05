import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    if not os.path.exists("data"):
        st.error("🚨 Hangar vacío: La carpeta 'data' no existe.")
        return None, None, None
    
    archivos = os.listdir("data")
    try:
        # Búsqueda por palabras clave
        f_nacional = [f for f in archivos if "Terapia" in f and f.endswith(".csv")][0]
        f_match = [f for f in archivos if "USACH" in f and f.endswith(".csv")][0]
        f_evo = [f for f in archivos if "SIES" in f and f.endswith(".csv")][0]

        headers_nacional = ['u','a','c','d','e','dr','f','r','s']
        
        df_nacional = pd.read_csv(f"data/{f_nacional}", names=headers_nacional)
        df_match = pd.read_csv(f"data/{f_match}")
        df_evo = pd.read_csv(f"data/{f_evo}", skiprows=4)
        
        return df_nacional, df_match, df_evo
    except IndexError:
        st.error(f"❌ No encontré archivos. En /data veo: {archivos}")
        return None, None, None

# --- AQUÍ LLAMAMOS AL MOTOR ---
df_to, df_story, df_evo = load_data()

# --- SI TODO CARGÓ, DIBUJAMOS EL DASHBOARD ---
if df_to is not None:
    st.title("👐 **SurDAO Terapia Ocupacional**")
    st.markdown("### *Criterio SIES 2024 - Nodo Santiago Tian77*")

    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Acreditación USACH", "7 Años", "Máximo Nivel")
    
    # Usamos df_to porque así lo definimos arriba en el return
    desercion_media = pd.to_numeric(df_to['d'], errors='coerce').mean()
    c2.metric("Deserción Nacional Promedio", f"{desercion_media:.1f}%")
    c3.metric("Empleabilidad 1er Año", "88.9%", "USACH")

    # Comparativa
    st.subheader("🎯 Comparativa Crítica: USACH vs Central")
    st.dataframe(df_story, use_container_width=True)

    # Evolución SIES
    st.subheader("📈 Evolución Histórica Titulados")
    row_to = df_evo[df_evo.iloc[:,0].str.contains("Terapia Ocupacional", na=False, case=False)]
    
    if not row_to.empty:
        anios = [str(i) for i in range(2007, 2025)]
        valores = row_to.iloc[0, 1:19].values
        fig = px.line(x=anios, y=valores, title="Crecimiento Nacional de la Carrera", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    st.success("🚀 **Hangar Operativo:** Datos cargados con blindaje v8.5")
