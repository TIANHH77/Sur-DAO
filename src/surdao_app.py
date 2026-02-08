import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURACIÓN VISUAL (ESTÉTICA SUR DAO) ---
st.set_page_config(page_title="SUR DAO - Radar SIES", layout="wide", page_icon="🌑")

# CSS Hacker/Institucional
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
    h1, h2, h3 {color: #E0E0E0 !important;}
    .big-number {font-size: 2.5em; font-weight: bold; color: #4CAF50;}
    .shame-number {font-size: 2.5em; font-weight: bold; color: #FF4B4B;}
    .css-1aumxhk {background-color: #262730;} 
</style>
""", unsafe_allow_html=True)

# --- 2. EL REACTOR DE DATOS (CARGA ROBUSTA) ---
@st.cache_data
def load_data():
    # Rutas relativas a la carpeta 'data/'
    path_oferta = os.path.join("data", "Oferta_Academica_2025_SIES_02_06_2025_WEB_E.csv")
    path_retencion = os.path.join("data", "Informe_Retencion_SIES_2025.xlsx - Retención 1er año x IES.csv")
    
    # Verificación de emergencia por si los archivos están en la raíz
    if not os.path.exists(path_oferta): path_oferta = "Oferta_Academica_2025_SIES_02_06_2025_WEB_E.csv"
    if not os.path.exists(path_retencion): path_retencion = "Informe_Retencion_SIES_2025.xlsx - Retención 1er año x IES.csv"

    try:
        # A) CARGAR OFERTA ACADÉMICA (Encoding latin1 y separador ;)
        try:
            df_oferta = pd.read_csv(path_oferta, sep=';', encoding='utf-8', on_bad_lines='skip')
        except:
            df_oferta = pd.read_csv(path_oferta, sep=';', encoding='latin1', on_bad_lines='skip')

        # Limpieza de Arancel (Quitar $ y puntos)
        if 'Arancel Anual' in df_oferta.columns:
            df_oferta['Arancel Anual'] = pd.to_numeric(df_oferta['Arancel Anual'].astype(str).str.replace(r'[$.]', '', regex=True), errors='coerce')
        
        # Mapeo de Columnas Clave
        # Buscamos las columnas aunque cambien ligeramente de nombre
        cols_map = {
            'Institucion': [c for c in df_oferta.columns if 'Nombre IES' in c][0],
            'Carrera': [c for c in df_oferta.columns if 'Nombre Carrera' in c][0],
            'Generica': [c for c in df_oferta.columns if 'Carrera Genérica' in c][0],
            'Arancel': 'Arancel Anual',
            'Duracion_Formal': [c for c in df_oferta.columns if 'Duración Total' in c][0],
            'Region': [c for c in df_oferta.columns if 'Región Sede' in c][0]
        }
        
        df_core = df_oferta[list(cols_map.values())].copy()
        df_core.columns = cols_map.keys() # Renombrar a nombres estándar
        
        # B) CARGAR RETENCIÓN (Buscando el encabezado correcto)
        df_ret_raw = pd.read_csv(path_retencion, sep=',', header=None)
        # Encontrar la fila que dice "Nombre de la institución"
        header_row = df_ret_raw[df_ret_raw.apply(lambda x: x.astype(str).str.contains('Nombre de la institución').any(), axis=1)].index[0]
        df_ret = pd.read_csv(path_retencion, sep=',', header=header_row)
        
        # Seleccionar Institución y último año disponible (2024 o 2023)
        col_ies = [c for c in df_ret.columns if 'Nombre de la institución' in c][0]
        col_dato = [c for c in df_ret.columns if '2024' in str(c)]
        if not col_dato: col_dato = [c for c in df_ret.columns if '2023' in str(c)]
        
        df_ret = df_ret[[col_ies, col_dato[0]]].copy()
        df_ret.columns = ['Institucion', 'Retencion_Actual']
        
        # C) FUSIÓN DE DATOS (MERGE)
        # Normalizar nombres para que crucen bien (Mayúsculas y sin espacios extra)
        df_core['Institucion'] = df_core['Institucion'].astype(str).str.upper().str.strip()
        df_ret['Institucion'] = df_ret['Institucion'].astype(str).str.upper().str.strip()
        
        df_final = pd.merge(df_core, df_ret, on='Institucion', how='left')
        
        # Imputación Inteligente: Si no hay dato de retención, usar promedio nacional para no romper la gráfica
        avg_ret = df_final['Retencion_Actual'].mean()
        df_final['Retencion_Actual'] = df_final['Retencion_Actual'].fillna(avg_ret)
        
        # D) CÁLCULOS KPI SUR DAO
        df_final['Tasa_Desercion'] = 1 - df_final['Retencion_Actual']
        # Capital en Riesgo = Arancel * Deserción (Dinero que se va con los alumnos)
        df_final['Capital_Riesgo_MM'] = (df_final['Arancel'] * df_final['Tasa_Desercion']) / 1000000 
        
        return df_final

    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

df = load_data()

# --- 3. BARRA LATERAL (PANEL DE CONTROL) ---
with st.sidebar:
    st.title("🎛️ SUR DAO Control")
    st.markdown("---")
    
    st.markdown("### 🔮 Simulador de Futuro")
    meta_recuperacion = st.slider("Meta de Recuperación (%)", 0, 50, 10, 
                                  help="Si aplicamos acompañamiento, ¿qué % de la deserción evitamos?")
    
    st.markdown("---")
    st.markdown("### 📍 Filtros Territoriales")
    
    if not df.empty:
        lista_regiones = ["Todas"] + sorted(df['Region'].dropna().unique().tolist())
        filtro_region = st.selectbox("Región", lista_regiones)
        
        lista_areas = ["Todas"] + sorted(df['Generica'].dropna().unique().tolist())
        filtro_area = st.selectbox("Área de Conocimiento", lista_areas)
    
    st.markdown("---")
    st.link_button("🏛️ Conectar con USACH", "https://www.usach.cl")
    st.caption("Protocolo v2026.1 - Capa Sombra")

# --- 4. DASHBOARD INTERACTIVO ---
if not df.empty:
    # Aplicar Filtros
    df_view = df.copy()
    if filtro_region != "Todas":
        df_view = df_view[df_view['Region'] == filtro_region]
    if filtro_area != "Todas":
        df_view = df_view[df_view['Generica'] == filtro_area]

    # Lógica del Simulador
    df_view['Capital_Recuperado'] = df_view['Capital_Riesgo_MM'] * (meta_recuperacion / 100)
    
    # Totales para las Tarjetas
    total_riesgo = df_view['Capital_Riesgo_MM'].sum()
    total_recuperado = df_view['Capital_Recuperado'].sum()
    total_programas = len(df_view)

    # Título Dinámico
    st.title(f"🌑 Radar de Capital Humano: {filtro_region}")
    st.markdown(f"#### Analizando **{total_programas}** programas académicos activos")

    # Tarjetas de KPI
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='metric-card'><h3>💸 Sangría del Sistema</h3><p class='shame-number'>${total_riesgo:,.0f} MM</p><p>Perdidos anualmente por deserción</p></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='metric-card'><h3>🛡️ Capital Recuperable</h3><p class='big-number'>${total_recuperado:,.0f} MM</p><p>Si aplicamos el Modelo SUR DAO</p></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='metric-card'><h3>🌱 Índice de Impacto</h3><p class='big-number'>Alto</p><p>Oportunidad de intervención</p></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Pestañas de Análisis
    tab1, tab2, tab3 = st.tabs(["📊 Mapa de Calor", "🧬 Simulador de Rescate", "📜 Manifiesto"])

    with tab1:
        st.subheader("Instituciones con Mayor Riesgo Financiero/Social")
        # Agrupar por Institución
        df_chart = df_view.groupby('Institucion')[['Capital_Riesgo_MM', 'Tasa_Desercion']].mean().reset_index()
        df_chart['Total_Riesgo'] = df_view.groupby('Institucion')['Capital_Riesgo_MM'].sum().values
        # Top 15
        df_chart = df_chart.sort_values('Total_Riesgo', ascending=False).head(15)
        
        fig = px.bar(df_chart, x='Institucion', y='Total_Riesgo', color='Tasa_Desercion',
                     title="Dinero en Riesgo por Institución (Color = Tasa Deserción)",
                     labels={'Total_Riesgo': 'Millones de Pesos (MM$)', 'Tasa_Desercion': 'Deserción'},
                     color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader(f"Proyección: Recuperando el {meta_recuperacion}% de trayectorias")
        
        col_sim1, col_sim2 = st.columns([2, 1])
        with col_sim1:
            # Scatter Plot: Costo vs Deserción
            fig2 = px.scatter(df_view.sample(min(500, len(df_view))), 
                              x="Arancel", y="Tasa_Desercion", 
                              size="Duracion_Formal", color="Generica",
                              hover_name="Carrera",
                              title="Mapa de Fricción: Costo vs Abandono (Muestra representativa)")
            st.plotly_chart(fig2, use_container_width=True)
        
        with col_sim2:
            st.info("""
            **¿Qué estamos viendo?**
            Cada punto es una carrera. Los puntos altos son alta deserción.
            
            **La Propuesta SUR DAO:**
            No se trata de bajar la exigencia, sino de **acompañar la trayectoria**.
            Al aplicar el protocolo de 'Trueque Educativo' y 'Nodos Comunitarios',
            convertimos esa deserción en capital social activo.
            """)
            st.success(f"💰 Ahorro Proyectado: **${total_recuperado:,.0f} MM**")

    with tab3:
        st.markdown("""
        ### 🌑 Protocolo de la Capa Sombra
        
        **1. El Diagnóstico:** El sistema actual considera la deserción como un "fracaso". Nosotros la vemos como una **fuga de capital**.
        
        **2. La Solución:**
        Utilizar la infraestructura de la USACH como "Bisagra" para validar saberes informales.
        
        **3. El Futuro:**
        Tokenizar la actividad comunitaria para que nadie caiga al vacío.
        
        > *"La sombra no se vende. La custodia no se compra. Lo humano decide."*
        """)

else:
    st.warning("⚠️ Esperando datos... Por favor asegúrate de tener la carpeta 'data/' con los archivos CSV del SIES.")
    st.info("Estructura requerida: /data/Oferta_Academica...csv y /data/Informe_Retencion...csv")
