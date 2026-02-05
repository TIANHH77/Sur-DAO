import os
import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(layout="wide", page_title="SurDAO v9.0")

@st.cache_data
def load_data():
    if not os.path.exists("data"):
        return None, None, None
    
    archivos = os.listdir("data")
    try:
        # Buscador de archivos por palabra clave (.xlsx de 2025)
        f_nacional = [f for f in archivos if "Terapia" in f and f.endswith(".xlsx")][0]
        f_match = [f for f in archivos if "USACH" in f and f.endswith(".xlsx")][0]
        f_evo = [f for f in archivos if "Compendio" in f and f.endswith(".xlsx")][0]

        # Carga limpia
        df_n = pd.read_excel(f"data/{f_nacional}")
        df_m = pd.read_excel(f"data/{f_match}")
        df_e = pd.read_excel(f"data/{f_evo}", skiprows=4)
        
        return df_n, df_m, df_e
    except Exception as e:
        st.error(f"Error cargando: {e}")
        return None, None, None

# --- EJECUCIÓN ---
df_to, df_story, df_evo = load_data()

if df_to is not None:
    st.title("👐 **SurDAO: Terapia Ocupacional**")
    st.info("Auditoría Académica Nodo Santiago - Criterio SIES 2025")

    # KPIs automáticos
    c1, c2, c3 = st.columns(3)
    c1.metric("Acreditación USACH", "7 Años", "Máximo SIES")
    
    # Buscamos deserción sin importar el nombre de la columna
    col_d = [c for c in df_to.columns if "Deser" in str(c)][0]
    media_d = pd.to_numeric(df_to[col_d], errors='coerce').mean()
    c2.metric("Deserción Promedio", f"{media_d:.1f}%")
    c3.metric("Empleabilidad", "88.9%", "USACH")

    # Tabla de Matches
    st.subheader("🎯 Comparativa: USACH vs Central")
    st.dataframe(df_story, use_container_width=True)

    # Gráfico de Evolución
    st.subheader("📈 Crecimiento Histórico de Titulados")
    # Buscamos la fila de Terapia Ocupacional
    row = df_evo[df_evo.iloc[:,0].astype(str).str.contains("Terapia Ocupacional", na=False, case=False)]
    
    if not row.empty:
        anios = [str(i) for i in range(2007, 2025)] 
        valores = row.iloc[0, 1:19].values
        fig = px.area(x=anios, y=valores, title="Titulados por Año (SIES)", color_discrete_sequence=['#FF4B4B'])
        st.plotly_chart(fig, use_container_width=True)

    st.success("🚀 Hangar v9.0 Operativo")
