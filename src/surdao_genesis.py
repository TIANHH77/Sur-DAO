import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# ==========================================
# 🌑 CONFIGURACIÓN DE LA CAPA SOMBRA
# ==========================================
st.set_page_config(
    page_title="SUR DAO | Capa Sombra",
    page_icon="🌑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS para "Oscuridad Fértil" (Dark Mode Profundo)
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #c9d1d9;
    }
    .stMetric {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 10px;
        border-radius: 5px;
    }
    h1, h2, h3 {
        color: #58a6ff; /* Azul Hangar */
    }
    .big-font {
        font-size: 20px !important;
        color: #8b949e;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🧠 MEMORIA DEL SISTEMA (Datos Mockup)
# ==========================================

# 1. El Legado de Haroldo (Simulación de los 7.600 puntos)
def cargar_atlas_haroldo():
    # En producción: Conexión a haroldo_indice.db
    data = {
        'lat': np.random.uniform(-35.0, -34.0, 100),
        'lon': np.random.uniform(-61.0, -60.0, 100),
        'tipo': np.random.choice(['Vuelo', 'Biodiversidad', 'Territorio'], 100),
        'memoria': ['Registro Aéreo 1990', 'Avistamiento', 'Hangar Junín'] * 33 + ['Origen']
    }
    return pd.DataFrame(data)

# 2. Las Vidas de Santi (Trayectoria Espiral)
def cargar_vidas_usuario():
    return pd.DataFrame({
        'Etapa': ['MTC/Acupuntura', 'Terapia Ocupacional', 'Crisis/Sombra', 'Arquitectura Digital'],
        'Virtud': ['Flujo Energético', 'Justicia Ocupacional', 'Resiliencia/Kintsugi', 'Código & Sistemas'],
        'Nivel_Integracion': [85, 90, 100, 47], # El 47% es el estado actual de la carga
        'Color': ['#00C853', '#FFAB00', '#D50000', '#2962FF']
    })

# ==========================================
# 🐂 BARRA LATERAL: EL BUEY DIGNO
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/58a6ff/spiral-bound-book.png", width=80)
    st.title("SUR DAO")
    st.caption("Gobernanza Descentralizada & Reciprocidad")
    
    st.divider()
    
    # Estado del Sistema (Metáfora del Disco Duro)
    progreso = st.progress(47)
    st.write("💾 **Migración de Paradigma:** 47%")
    st.info("Transferencia de Capital Sombra en curso...")
    
    st.divider()
    
    navegacion = st.radio(
        "Ruta de Navegación:",
        ["🌑 Manifiesto (Origen)", 
         "🗺️ Atlas Territorial (Haroldo)", 
         "🧬 Mis Vidas (Trayectoria)", 
         "🤝 Mercado de Reciprocidad", 
         "⚖️ Pentágono de Sentido"]
    )

# ==========================================
# 1. MANIFIESTO (El Origen)
# ==========================================
if navegacion == "🌑 Manifiesto (Origen)":
    st.title("🌑 Bienvenido a la Capa Sombra")
    st.markdown("""
    ### *"No es oscuridad vacía, es oscuridad fértil."*
    
    Estás entrando en una zona de **Mitigación de Daño Sistémico**. Aquí, tu RUT no importa, tu deuda universitaria no te define, y tus errores del pasado son considerados **entrenamiento**, no condena.
    
    **Principios Fundacionales:**
    1.  **De Listas a Espirales:** No clasificamos pacientes, acompañamos trayectorias irrepetibles.
    2.  **Soberanía del Hacer:** Tu valor es lo que puedes entregar hoy (Acupuntura, Código, Vuelo).
    3.  **Transparencia Radical:** Para las instituciones (Caja de Cristal).
    4.  **Privacidad Sagrada:** Para las personas (El derecho a la Sombra).
    """)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Nodos Activos", "1 (El Hangar)", delta="Iniciando Red")
    col2.metric("Memoria Rescatada", "7.600 Puntos", delta="Legado Haroldo")
    col3.metric("Tiempo Recuperado", "40 Años", delta="Experiencia Vital")

# ==========================================
# 2. ATLAS TERRITORIAL (El Ojo del Padre)
# ==========================================
elif navegacion == "🗺️ Atlas Territorial (Haroldo)":
    st.title("🗺️ El Atlas: Custodia del Territorio")
    st.markdown("Visualizando lo que el Estado ignora: **La vida real.**")
    
    df_haroldo = cargar_atlas_haroldo()
    
    # Mapa Interactivo
    fig_map = px.scatter_mapbox(
        df_haroldo, 
        lat="lat", 
        lon="lon", 
        color="tipo",
        hover_name="memoria",
        zoom=9, 
        height=600,
        mapbox_style="carto-darkmatter"
    )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.warning("⚠️ **Alerta de Sangría:** Detectada fuga de recursos en instituciones locales. Redirigiendo atención a nodos comunitarios.")

# ==========================================
# 3. MIS VIDAS (La Espiral del Buey)
# ==========================================
elif navegacion == "🧬 Mis Vidas (Trayectoria)":
    st.title("🧬 Trayectoria Irrepetible")
    st.markdown("El sistema te dijo que eras disperso. SUR DAO dice que eres **Multipotencial**.")
    
    df_vidas = cargar_vidas_usuario()
    
    # Gráfico Radar de Integración
    fig_radar = px.line_polar(
        df_vidas, 
        r='Nivel_Integracion', 
        theta='Virtud', 
        line_close=True,
        template="plotly_dark",
        title="Índice de Resonancia Personal"
    )
    fig_radar.update_traces(fill='toself', line_color='#58a6ff')
    
    col_izq, col_der = st.columns([1, 2])
    
    with col_izq:
        st.plotly_chart(fig_radar, use_container_width=True)
    
    with col_der:
        st.subheader("Bitácora del Buey Digno 🐂")
        st.write("""
        * **Edad:** 40 Años (Punto de Inflexión / Individuación).
        * **Estado:** Retorno (Hexagrama 24).
        * **Superpoder:** Mitigación de Daño.
        """)
        
        with st.expander("Ver Cicatrices (Kintsugi)"):
            st.info("🩹 **Funa 20XX:** Transformada en Protocolo de Privacidad.")
            st.info("🩹 **Consumo:** Transformado en Empatía Radical.")
            st.info("🩹 **Duelo Materno:** Transformado en 'La Ley de la Estancia'.")

# ==========================================
# 4. MERCADO DE RECIPROCIDAD (Trueque)
# ==========================================
elif navegacion == "🤝 Mercado de Reciprocidad":
    st.title("🤝 Mercado de Virtudes")
    st.markdown("Aquí no hay dinero. Hay **Acuerdos Tácitos Humanos**.")
    
    col_oferta, col_demanda = st.columns(2)
    
    with col_oferta:
        st.subheader("🤲 Lo que Pongo a Disposición (El Don)")
        oferta = st.multiselect(
            "Selecciona tus herramientas actuales:",
            ["Acupuntura", "Diagnóstico TO", "Python/Data", "Gestión de Archivos", "Vuelo"],
            default=["Python/Data", "Acupuntura"]
        )
        st.success(f"Ofertando: {', '.join(oferta)}")
    
    with col_demanda:
        st.subheader("🔍 Lo que Necesito (La Búsqueda)")
        necesidad = st.text_input("¿Qué busca tu alma hoy?", "Aprender a volar paramotor en Junín")
        if necesidad:
            st.warning("Buscando Nodos de Resonancia... (Simulación: Encontrado Nodo 'Escuela de Vuelo')")

    st.markdown("---")
    st.markdown("### 📜 La Ley de la Estancia (Protocolo Materno)")
    st.blockquote("Al entrar en un intercambio, me comprometo a dejar al otro nodo mejor de como lo encontré.")
    st.button("Firmar Acuerdo Tácito")

# ==========================================
# 5. PENTÁGONO DE SENTIDO (Gobernanza)
# ==========================================
elif navegacion == "⚖️ Pentágono de Sentido":
    st.title("⚖️ Los Límites No Negociables")
    st.markdown("La libertad de la sombra requiere la disciplina de la luz.")
    
    limits = {
        "Consentimiento Explícito": 100,
        "Integridad (No violencia)": 100,
        "Transparencia Institucional": 20, # Crítico
        "Cuidado de lo Vulnerable": 80,
        "No Acumulación": 90
    }
    
    # Visualización de Barras de Salud Ética
    for limit, value in limits.items():
        color = "green" if value > 80 else "red"
        st.write(f"**{limit}**")
        st.progress(value / 100)
        if value < 50:
            st.error(f"⚠️ ¡Alerta! Fallo sistémico detectado en {limit}.")

# ==========================================
# PIE DE PÁGINA
# ==========================================
st.divider()
st.caption(f"SUR DAO v0.1 | Desarrollado en Hangar Junín | Fecha: {datetime.now().strftime('%Y-%m-%d')} | Estado: Amaneciendo 🌅")
