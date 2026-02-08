import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SUR DAO - Radar SIES Real", layout="wide", page_icon="🌑")

# --- ESTILOS CSS PARA QUE SE VEA COMO HACKER DE LA USACH ---
st.markdown("""
<style>
    .metric-card {background-color: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 5px solid #FF4B4B;}
    .big-font {font-size:20px !important;}
</style>
""", unsafe_allow_html=True)

st.title("🌑 SUR DAO: Radar de Capital Humano (Data SIES 2025)")
st.markdown("### *Transformando la 'Deserción' en Capital Comunitario Latente*")

# --- MOTOR DE PROCESAMIENTO DE DATOS (EL REACTOR) ---
@st.cache_data
def load_sies_data():
    try:
        # 1. CARGAR OFERTA (La base madre)
        # Intentamos leer con diferentes encodings por si acaso
        try:
            df_oferta = pd.read_csv('Oferta_Academica_2025_SIES_02_06_2025_WEB_E.csv', sep=';', encoding='utf-8', on_bad_lines='skip')
        except:
            df_oferta = pd.read_csv('Oferta_Academica_2025_SIES_02_06_2025_WEB_E.csv', sep=';', encoding='latin1', on_bad_lines='skip')

        # Limpieza de Arancel (Sacar $ y puntos)
        if 'Arancel Anual' in df_oferta.columns:
            df_oferta['Arancel Anual'] = pd.to_numeric(df_oferta['Arancel Anual'].astype(str).str.replace(r'[$.]', '', regex=True), errors='coerce')
        
        # Selección de Columnas Clave (Buscamos nombres parecidos por si cambian)
        cols_map = {
            'Nombre IES': [c for c in df_oferta.columns if 'Nombre IES' in c][0],
            'Carrera': [c for c in df_oferta.columns if 'Nombre Carrera' in c][0],
            'Generica': [c for c in df_oferta.columns if 'Carrera Genérica' in c][0], # Área Carrera Genérica
            'Arancel': 'Arancel Anual',
            'Duracion_Formal': [c for c in df_oferta.columns if 'Duración Total' in c][0],
            'Region': [c for c in df_oferta.columns if 'Región Sede' in c][0]
        }
        df_core = df_oferta[list(cols_map.values())].copy()
        df_core.columns = ['Institucion', 'Carrera', 'Carrera_Generica', 'Arancel', 'Duracion_Formal', 'Region']
        
        # 2. CARGAR RETENCIÓN (Por Institución para tener dato general)
        # Buscamos la fila donde empieza el encabezado real
        df_ret = pd.read_csv('Informe_Retencion_SIES_2025.xlsx - Retención 1er año x IES.csv', sep=',', header=None)
        header_idx = df_ret[df_ret.apply(lambda x: x.astype(str).str.contains('Nombre de la institución').any(), axis=1)].index[0]
        df_ret = pd.read_csv('Informe_Retencion_SIES_2025.xlsx - Retención 1er año x IES.csv', sep=',', header=header_idx)
        
        # Renombramos y limpiamos
        col_ies_ret = [c for c in df_ret.columns if 'Nombre de la institución' in c][0]
        # Asumimos que la última columna con datos es 2024
        col_2024 = [c for c in df_ret.columns if '2024' in str(c)][0]
        
        df_ret = df_ret[[col_ies_ret, col_2024]].copy()
        df_ret.columns = ['Institucion', 'Retencion_2024']
        
        # Normalizar Nombres para el Cruce (Upper y Strip)
        df_core['Institucion'] = df_core['Institucion'].astype(str).str.upper().str.strip()
        df_ret['Institucion'] = df_ret['Institucion'].astype(str).str.upper().str.strip()
        
        # 3. MERGE (Fusión de Datos)
        df_final = pd.merge(df_core, df_ret, on='Institucion', how='left')
        
        # Llenar vacíos (Si no hay dato de retención, usamos el promedio del sistema para no romper el gráfico)
        avg_ret = df_final['Retencion_2024'].mean()
        df_final['Retencion_2024'] = df_final['Retencion_2024'].fillna(avg_ret)
        
        # 4. CÁLCULO DE KPIs SUR DAO
        df_final['Desercion_Rate'] = 1 - df_final['Retencion_2024']
        # Capital en Riesgo = Arancel * Duración Formal * Tasa de Deserción
        # (Es una estimación del dinero que "se va" con los alumnos que desertan en 1er año)
        df_final['Capital_Riesgo_MM'] = (df_final['Arancel'] * df_final['Desercion_Rate']) / 1000000 
        
        return df_final
        
    except Exception as e:
        st.error(f"Error en el Reactor SIES: {e}")
        return pd.DataFrame()

df_sies = load_sies_data()

# --- DASHBOARD VISUAL ---
if not df_sies.empty:
    
    # KPIs Globales
    total_capital = df_sies['Capital_Riesgo_MM'].sum()
    avg_desercion = df_sies['Desercion_Rate'].mean() * 100
    total_carreras = len(df_sies)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Capital Humano en Riesgo (Anual)", f"${total_capital:,.0f} MM", "Monto Latente")
    col2.metric("Tasa Deserción Sistema", f"{avg_desercion:.1f}%", "Promedio Nacional")
    col3.metric("Programas Monitoreados", f"{total_carreras}", "Oferta 2025")
    col4.metric("Nodos Potenciales", "35,000+", "Estimado SUR DAO")

    st.markdown("---")

    # FILTROS
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        region = st.selectbox("Filtrar por Región", ["Todas"] + sorted(df_sies['Region'].dropna().unique().tolist()))
    with col_f2:
        tipo_carrera = st.selectbox("Filtrar por Área Genérica", ["Todas"] + sorted(df_sies['Carrera_Generica'].dropna().unique().tolist()))

    # APLICAR FILTROS
    df_view = df_sies.copy()
    if region != "Todas":
        df_view = df_view[df_view['Region'] == region]
    if tipo_carrera != "Todas":
        df_view = df_view[df_view['Carrera_Generica'] == tipo_carrera]

    # GRÁFICOS
    tab1, tab2, tab3 = st.tabs(["📊 Mapa de Calor (Dinero)", "📉 Zonas de Fricción", "🌱 Propuesta SUR DAO"])

    with tab1:
        st.subheader(f"Distribución del Capital en Riesgo - {region}")
        # Agrupamos por Institución para ver quién pierde más capital humano/dinero
        df_chart = df_view.groupby('Institucion')[['Capital_Riesgo_MM', 'Desercion_Rate']].mean().reset_index()
        df_chart['Capital_Total'] = df_view.groupby('Institucion')['Capital_Riesgo_MM'].sum().values
        
        # Top 20 Instituciones con más riesgo
        df_chart = df_chart.sort_values('Capital_Total', ascending=False).head(20)
        
        fig = px.bar(df_chart, x='Institucion', y='Capital_Total', color='Desercion_Rate',
                     title="Instituciones con Mayor Capital Social en Riesgo (MM$)",
                     labels={'Capital_Total': 'Monto en Riesgo (MM$)', 'Desercion_Rate': 'Tasa Deserción'},
                     color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Carreras con Mayor Deserción Crítica")
        df_scatter = df_view[df_view['Arancel'] > 0].sample(min(1000, len(df_view))) # Sample para no saturar
        fig2 = px.scatter(df_scatter, x='Arancel', y='Desercion_Rate', color='Carrera_Generica',
                          size='Duracion_Formal', hover_data=['Institucion', 'Carrera'],
                          title="Relación Costo vs Deserción (Cada punto es un programa)",
                          labels={'Arancel': 'Arancel Anual ($)', 'Desercion_Rate': 'Tasa de Deserción'})
        st.plotly_chart(fig2, use_container_width=True)
        
    with tab3:
        st.subheader("🔄 La Solución: Protocolo de Retención Comunitaria")
        st.markdown(f"""
        En la región de **{region}**, detectamos **${df_view['Capital_Riesgo_MM'].sum():,.0f} MM** en riesgo.
        
        **Propuesta para la USACH:**
        1.  **Interceptar** la deserción en las carreras de área: *{tipo_carrera if tipo_carrera != "Todas" else "Críticas"}*.
        2.  **Validar** los saberes de esos estudiantes mediante el *Trueque Educativo*.
        3.  **Redirigir** ese capital humano hacia nodos de desarrollo local en lugar de perderlo.
        """)
        st.info("Este dashboard demuestra que la 'deserción' no es un vacío, es un mercado de talento no regulado.")

else:
    st.warning("⚠️ Esperando datos... Asegúrate de que los archivos CSV estén en la carpeta.")
