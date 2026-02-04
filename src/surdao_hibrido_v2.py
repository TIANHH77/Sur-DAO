import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configuración de página épica
st.set_page_config(page_title="SurDAO Híbrido v2", layout="wide")

st.title("🏹 SurDAO: Motor de Inteligencia Académica")
st.markdown("---")

def cargar_y_procesar(años_min):
    # Cargar base con manejo de errores
    try:
        df = pd.read_csv("data/Oferta_Academica_2025_SIES.csv", encoding='latin1', errors='ignore')
    except:
        st.error("¡No encontré el CSV! Revisa la carpeta /data.")
        return None

    # Normalización inteligente de columnas
    col_map = {
        'Vacantes Semestre Uno': 'Vacantes_S1',
        'Vacantes S1': 'Vacantes_S1',
        'Semestres reconocidos': 'Sem_rec',
        'Sem_Rec_SCT': 'Sem_rec'
    }
    df = df.rename(columns=col_map)

    # Asegurar que existan o crear dummy si fallan
    if 'Vacantes_S1' not in df.columns: df['Vacantes_S1'] = 0
    if 'Sem_rec' not in df.columns: df['Sem_rec'] = 0

    df['Vacantes_S1'] = pd.to_numeric(df['Vacantes_S1'], errors='coerce').fillna(0)
    df['Sem_rec'] = pd.to_numeric(df['Sem_rec'], errors='coerce').fillna(0)

    # 1. Filtrar carreras viables (Lógica SurDAO)
    general = df[(df['Vacantes_S1'] > 50) & (df['Sem_rec'] >= 6)].copy()

    # 2. Cálculos de Valor
    general['Años_Est'] = np.clip(general['Sem_rec']/2, 3, 7)
    general['Creditos'] = general['Años_Est'] * 40
    general['Valor_Humano'] = general['Creditos'] * 12000

    # 3. Foco USACH
    usach_mask = general['Nombre IES'].str.contains('SANTIAGO|USACH', case=False, na=False)
    usach_prior = general[usach_mask & (general['Años_Est'] >= años_min)]

    return general, usach_prior

# Sidebar para controles
st.sidebar.header("Parámetros de Simulación")
años_input = st.sidebar.slider("Años mínimos de carrera", 3, 7, 3)

data_gen, data_usach = cargar_y_procesar(años_input)

if data_gen is not None:
    # Métricas clave arriba
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Carreras Viables", len(data_gen))
    with col2:
        st.metric("Prioridad USACH", len(data_usach))
    with col3:
        capital_mm = (data_usach['Valor_Humano'].sum() / 1e6)
        st.metric("Capital Recuperable", f"${capital_mm:,.1f} MM")

    # Gráfico de dispersión: Vacantes vs Valor Humano
    st.subheader("Visualización de Potencial Académico")
    fig = px.scatter(data_usach, 
                     x="Vacantes_S1", 
                     y="Valor_Humano", 
                     size="Años_Est", 
                     color="Nombre Carrera",
                     hover_name="Nombre Carrera",
                     title="Relación Vacantes vs Capital Humano")
    st.plotly_chart(fig, use_container_width=True)

    # Tabla interactiva
    st.subheader("Top 50 Nodos USACH")
    st.dataframe(data_usach.nlargest(50, 'Valor_Humano')[['Nombre Carrera', 'Años_Est', 'Valor_Humano']])

    # Exportar resultados
    st.download_button("Descargar Reporte CSV", 
                       data_usach.to_csv(index=False), 
                       "surdao_report.csv", "text/csv")

