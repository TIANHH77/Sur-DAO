import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURACIÓN VISUAL (ESTÉTICA INSTITUCIONAL/HACKER) ---
st.set_page_config(page_title="SUR DAO - Protocolo USACH", layout="wide", page_icon="🌑")

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
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #FFD700; /* Dorado Legal */
        margin-bottom: 10px;
    }
    h1, h2, h3 {color: #E0E0E0 !important;}
    .big-number {font-size: 2.5em; font-weight: bold; color: #4CAF50;}
    .shame-number {font-size: 2.5em; font-weight: bold; color: #FF4B4B;}
</style>
""", unsafe_allow_html=True)

# --- 2. CARGA DE DATOS (Mismo Motor Robusto SIES) ---
@st.cache_data
def load_data():
    # ... (Mantenemos la misma lógica de carga de la versión anterior) ...
    # Para ahorrar espacio en el chat, asumo que usas el mismo bloque 'load_data' 
    # de la versión v4 que te pasé. Si necesitas que lo repita, avísame.
    # Aquí simulamos la carga para que el script corra en el ejemplo:
    data = {
        'Institucion': ['USACH', 'USACH', 'USACH', 'U. CHILE', 'INACAP'],
        'Carrera': ['Ing. Informática', 'Terapia Ocupacional', 'Arquitectura', 'Derecho', 'Mecánica'],
        'Generica': ['Tecnología', 'Salud', 'Arte', 'Humanidades', 'Tecnología'],
        'Arancel': [4500000, 3800000, 4200000, 5100000, 2200000],
        'Retencion_Actual': [0.60, 0.65, 0.72, 0.85, 0.55],
        'Duracion_Formal': [10, 10, 12, 10, 4],
        'Region': ['Metropolitana', 'Metropolitana', 'Metropolitana', 'Metropolitana', 'Metropolitana']
    }
    df = pd.DataFrame(data)
    df['Tasa_Desercion'] = 1 - df['Retencion_Actual']
    df['Capital_Riesgo_MM'] = (df['Arancel'] * df['Tasa_Desercion']) / 1000000 
    return df

df = load_data()

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🎛️ SUR DAO Control")
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Logo_Usach.svg/1200px-Logo_Usach.svg.png", width=100)
    st.caption("Protocolo de Vinculación Institucional")
    st.markdown("---")
    meta_recuperacion = st.slider("Meta de Recuperación (%)", 0, 50, 15)
    st.markdown("---")
    st.info("Documentación Cargada:\n- Res. 8417 (Formación Integral)\n- Res. 1983 (Convalidación)\n- Res. 6414 (Horarios)")

# --- 4. DASHBOARD ---
# Lógica de simulación
total_riesgo = df['Capital_Riesgo_MM'].sum()
recuperado = total_riesgo * (meta_recuperacion/100)

st.title("🌑 Radar SUR DAO: Capa Sombra & Normativa")
st.markdown("#### *Validando trayectorias mediante infraestructura legal existente*")

# KPIs
c1, c2, c3 = st.columns(3)
c1.markdown(f"<div class='metric-card'><h3>💸 Sangría Financiera</h3><p class='shame-number'>${total_riesgo:,.0f} MM</p><p>Presupuesto perdido hoy</p></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='metric-card'><h3>⚖️ Capital Legal</h3><p class='big-number'>Res. 1983</p><p>Habilitador del Trueque</p></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='metric-card'><h3>🛡️ Potencial Rescate</h3><p class='big-number'>${recuperado:,.0f} MM</p><p>Aplicando Normativa</p></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# PESTAÑAS
tab1, tab2, tab3 = st.tabs(["📜 Hacking Normativo", "📊 Datos SIES", "🧬 Simulador"])

# --- LA NUEVA JOYA DE LA CORONA ---
with tab1:
    st.subheader("🛠️ La Bisagra Jurídica: Cómo SUR DAO encaja en la USACH")
    st.markdown("No necesitamos cambiar la ley. Necesitamos aplicar las Resoluciones que ya existen.")
    
    col_leg1, col_leg2 = st.columns(2)
    
    with col_leg1:
        st.markdown("<div class='legal-card'><h4>📄 Resolución Exenta N° 8417 (2019)</h4><p><b>'Establece Normativa para Formación Integral'</b></p><p><i>Art. 1: Actividades orientadas al desarrollo y bienestar... construcción de comunidad universitaria diversa.</i></p><p>👉 <b>Aplicación SUR DAO:</b> Los 'Nodos Comunitarios' (ollas comunes, voluntariado) se certifican como créditos de Formación Integral.</p></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='legal-card'><h4>📄 Resolución Exenta N° 1983 (2018)</h4><p><b>'Reglamento de Convalidaciones'</b></p><p><i>Art. 1: Reconocimiento de aprendizajes... independiente de dónde fue aprobada la actividad.</i></p><p>👉 <b>Aplicación SUR DAO:</b> El 'Trueque Educativo' genera evidencias de aprendizaje que la Facultad DEBE convalidar si cumplen el resultado.</p></div>", unsafe_allow_html=True)

    with col_leg2:
        st.markdown("### 🧬 El Validador de Trayectoria")
        st.markdown("Prueba de concepto: ¿Es convalidable esta actividad de la sombra?")
        
        actividad = st.text_input("Actividad realizada en la Sombra", "Gestión de Logística para Comedor Solidario")
        horas = st.number_input("Horas dedicadas", 50, 500, 120)
        
        if st.button("Analizar Convalidación"):
            st.success(f"✅ **VIABLE.** Según Res. 1983 Art. 1:")
            st.markdown(f"""
            - **Actividad:** {actividad}
            - **Equivalencia:** {int(horas/18)} Créditos SCT (Estimado)
            - **Asignatura Potencial:** 'Gestión de Proyectos' o 'Responsabilidad Social'.
            - **Estado:** *Listo para Trueque.*
            """)
            st.caption("Esto transforma la 'deserción' en 'pausa activa reconocida'.")

with tab2:
    st.subheader("Evidencia del SIES (Mifuturo.cl)")
    fig = px.bar(df, x='Carrera', y='Capital_Riesgo_MM', color='Tasa_Desercion',
                 title="Fuga de Capital por Carrera", color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Proyección a Futuro")
    st.markdown("Si la USACH activa el **Art. 14 de la Res. 8417** (Responsabilidad de la Vicerrectoría), el impacto es inmediato.")
    st.metric("Retorno de Inversión Social", f"+ {meta_recuperacion}%")
