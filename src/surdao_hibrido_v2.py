import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="SurDAO v8.1")

@st.cache_data
def load_data():
    # 1. Tabla Nacional (La que tiene el nombre largo con "Hoja1")
    # Nota: Agregamos headers manuales porque este CSV no los trae en la primera fila
    headers_to = ['Universidad', 'Acreditacion', 'Carrera', 'Desercion_1erAño', 
                  'Empleabilidad_1erAño', 'Duracion_Real', 'Filtro_Extra', 'Retencion_1erAño', 'Salario_Rango']
    df_to = pd.read_csv("data/Terapia_ocupacional.xlsx - Hoja1.csv", names=headers_to)
    
    # 2. Match Ejecutivo (USACH vs Central)
    df_story = pd.read_csv("data/TO_USACH_CENTRAL.xlsx - Hoja1.csv")
    
    # 3. Evolución SIES (El reporte oficial del Mineduc)
    df_evo = pd.read_csv("data/Informe_Titulacion_2024_SIES_.xlsx - Evolución Titulación Pregrado.csv", skiprows=4)
    
    return df_to, df_story, df_evo

# --- EJECUCIÓN DEL DASHBOARD ---
try:
    df_to, df_story, df_evo = load_data()

    st.title("👐 **SurDAO Terapia Ocupacional**")
    st.markdown("### *Criterio SIES 2024 - Nodo Santiago Tian77*")

    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Acreditación USACH", "7 Años", "Máximo Nivel")
    c2.metric("Deserción Nacional Promedio", f"{df_to['Desercion_1erAño'].mean():.1f}%")
    c3.metric("Empleabilidad 1er Año", "88.9%", "USACH")

    # Visualización de tu historia
    st.subheader("🎯 Comparativa Crítica: USACH vs Central")
    st.dataframe(df_story, use_container_width=True)

    # Gráfico de Evolución SIES
    st.subheader("📈 Evolución Histórica Titulados")
    # Extraemos los datos de la fila de TO del SIES
    row_to = df_evo[df_evo.iloc[:,0].str.contains("Terapia Ocupacional", na=False, case=False)]
    if not row_to.empty:
        anios = [str(i) for i in range(2007, 2025)]
        valores = row_to.iloc[0, 1:19].values
        fig = px.line(x=anios, y=valores, title="Crecimiento Nacional de la Carrera", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    st.success("🚀 **Hangar Operativo:** Datos cargados respetando archivos originales.")

except Exception as e:
    st.error(f"❌ Error de Carga: Verifica que los archivos estén en la carpeta 'data/'. Detalles: {e}")
