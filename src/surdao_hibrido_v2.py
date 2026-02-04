import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración Galáctica
st.set_page_config(layout="wide", page_title="SurDAO: Piloto Híbrido v400", page_icon="🦎")

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    # 1. El "Gran Hangar" (Todas las Ues)
    headers_nacional = ['Universidad', 'Acreditacion', 'Carrera', 'Desercion_1erAño', 
                       'Empleabilidad_1erAño', 'Duracion_Real', 'Filtro_Extra', 'Retencion_1erAño', 'Salario_Rango']
    df_nacional = pd.read_csv("Terapia_ocupacional.xlsx - Hoja1.csv", names=headers_nacional)
    
    # 2. El "Match Ejecutivo" (USACH vs Central)
    df_match = pd.read_csv("TO_USACH_CENTRAL.xlsx - Hoja1.csv")
    
    # 3. Evolución SIES (Nacional)
    df_evo = pd.read_csv("Informe_Titulacion_2024_SIES_.xlsx - Evolución Titulación Pregrado.csv", skiprows=4)
    
    return df_nacional, df_match, df_evo

df_nacional, df_match, df_evo = load_data()

# --- HEADER NARRATIVO ---
st.title("👐 **SurDAO: Nodo Terapia Ocupacional**")
st.markdown("## *“De literal 0 al Despliegue Híbrido: USACH vs El Mercado”*")
st.markdown("---")

# --- SECCIÓN 1: EL MATCH DEFINITIVO ---
st.subheader("🎯 La Trayectoria Haroldo: Análisis Ejecutivo")
col_match, col_text = st.columns([2, 1])

with col_match:
    # Mostramos la tabla de comparación directa que preparaste
    st.table(df_match)

with col_text:
    st.info("""
    **Análisis de la Custodia:**
    - **Eficiencia:** La USACH reduce la duración real en **0.8 semestres** frente a la Central.
    - **Blindaje:** El **80% de retención** de la USACH es el motor de este proyecto.
    - **El Valor del 1%:** Este dashboard es el insumo para validar el retorno de la inversión académica.
    """)

# --- SECCIÓN 2: KPIs NACIONALES (El Poder del Gran Hangar) ---
st.subheader("📊 El Contexto Nacional (Data SIES 2024)")

# Buscamos los datos específicos de la USACH en el archivo grande
usach_data = df_nacional[df_nacional['Universidad'].str.contains("SANTIAGO", na=False)].iloc[0]
promedio_desercion = df_nacional['Desercion_1erAño'].mean()

c1, c2, c3 = st.columns(3)
c1.metric("Deserción USACH", f"{usach_data['Desercion_1erAño']*100}%", f"vs {promedio_desercion*100:.1f}% Promedio Nacional", delta_color="inverse")
c2.metric("Acreditación USACH", "7 Años", "Excelencia Máxima")
c3.metric("Empleabilidad USACH", f"{usach_data['Empleabilidad_1erAño']*100}%", "Estabilidad de Nodo")

# --- SECCIÓN 3: EVOLUCIÓN HISTÓRICA ---
st.subheader("📈 Crecimiento de la Ocupación Humana (2007-2024)")
row_to = df_evo[df_evo.iloc[:,0].str.contains("Terapia Ocupacional", na=False, case=False)]

if not row_to.empty:
    anios = [str(i) for i in range(2007, 2025)]
    valores = row_to.iloc[0, 1:19].values
    fig = px.area(x=anios, y=valores, 
                  labels={'x':'Año', 'y':'Titulados'},
                  title="Titulados de Terapia Ocupacional en Chile")
    fig.update_traces(line_color='#00CC96')
    st.plotly_chart(fig, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("🚀 **Haroldohorta GitHub** | Rescate de Patrimonio Nikon (39.000 archivos) | Backup Maestro 28TB Operativo")
st.success("✅ **Modo Despliegue Completado.** Insumo listo para presentación institucional.")
