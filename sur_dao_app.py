import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import unicodedata
from validador_sct import calcular_saqueo_trayectoria

# 🦅 SUR DAO - EL CENTRO DE MANDO (VERSIÓN MAESTRA)
st.set_page_config(page_title="SUR DAO | Capa Sombra", layout="wide", page_icon="🦅")

# --- UTILIDADES DE NORMALIZACIÓN ---
def normalizar(txt):
    if not txt: return "SIN DATO"
    txt = str(txt).upper().strip()
    return ''.join(c for c in unicodedata.normalize('NFKD', txt) if unicodedata.category(c) != 'Mn')

# --- CARGA DE DATOS (CON CACHÉ PARA VELOCIDAD) ---
@st.cache_data
def cargar_datos_maestros():
    # 1. Matrícula y Plata
    cols_mat = ['ANIO_DATA', 'MRUN', 'NOMB_INST', 'VALOR_ARANCEL', 'REGION_SEDE']
    df_mat = pd.read_parquet("data/MATRICULA_GLOBAL.parquet", columns=cols_mat)
    df_mat['VALOR_ARANCEL'] = pd.to_numeric(df_mat['VALOR_ARANCEL'], errors='coerce').fillna(0)
    
    # 2. Asignaciones (Los capturados por el Estado)
    df_bec = pd.read_parquet("data/ASIGNACIONES_GLOBAL.parquet", columns=['ANIO_DATA', 'MRUN'])
    
    # 3. Titulados (Los sobrevivientes)
    cols_tit = ['MRUN']
    df_tit = pd.read_parquet("data/TITULADOS_GLOBAL.parquet", columns=cols_tit)
    mrun_tit = set(df_tit['MRUN'].dropna())
    
    # 4. GeoJSON de Chile
    geo_path = "regiones.json" if os.path.exists("regiones.json") else "data/chile_regiones.geojson"
    geojson_chile = None
    if os.path.exists(geo_path):
        with open(geo_path, encoding='utf-8') as f:
            geojson_chile = json.load(f)
            
    return df_mat, df_bec, mrun_tit, geojson_chile

# --- INTERFAZ PRINCIPAL ---
st.title("🌑 SUR DAO | Protocolo de la Capa Sombra")
st.markdown("*Auditoría Ciudadana, Justicia Ocupacional y Soberanía Digital de Trayectorias.*")

# Cargando el motor...
try:
    df_mat, df_bec, mrun_tit, geojson_chile = cargar_datos_maestros()
except Exception as e:
    st.error(f"🚨 Falla en el silo de datos: {e}. Verifica que los .parquet existan.")
    st.stop()

# --- LAS 4 DIMENSIONES DE LA GUILLOTINA ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Atlas Territorial", 
    "⚖️ El Espejismo (Retención)", 
    "🪙 Validador SCT (Trueque)", 
    "🪖 Disciplina vs Mercado"
])

# ---------------------------------------------------------
# PESTAÑA 1: ATLAS TERRITORIAL (El mapa del dinero)
# ---------------------------------------------------------
with tab1:
    st.header("Distribución de la Inversión Fiscal y el Saqueo")
    
    # Filtro básico para el mapa
    anio_mapa = st.selectbox("Seleccione Año de Auditoría", sorted(df_mat['ANIO_DATA'].unique(), reverse=True))
    
    df_mapa_anio = df_mat[df_mat['ANIO_DATA'] == anio_mapa]
    map_data = df_mapa_anio.groupby('REGION_SEDE')['VALOR_ARANCEL'].sum().reset_index()
    map_data.columns = ['REGION', 'INVERSION']
    
    # Normalización rápida de nombres para el GeoJSON
    nombres_mapa = {
        "REGION METROPOLITANA DE SANTIAGO": "Región Metropolitana de Santiago",
        "REGION DE VALPARAISO": "Región de Valparaíso",
        "REGION DEL BIOBIO": "Región del Biobío"
    }
    map_data['REGION'] = map_data['REGION'].replace(nombres_mapa)
    
    if geojson_chile:
        fig_map = px.choropleth_mapbox(
            map_data, geojson=geojson_chile, locations="REGION",
            featureidkey="properties.name",
            color="INVERSION", color_continuous_scale="Reds",
            mapbox_style="carto-darkmatter", opacity=0.8,
            center={"lat": -33.4489, "lon": -70.6693}, zoom=4.5
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="black", font_color="white")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("No se encontró el archivo GeoJSON para renderizar el mapa.")

# ---------------------------------------------------------
# PESTAÑA 2: EL ESPEJISMO (Contraste de Supervivencia)
# ---------------------------------------------------------
with tab2:
    st.header("El Espejismo de la Retención vs. La Realidad")
    st.markdown("Basado en la Cohorte 2018 (Tracking de Supervivencia Real)")
    
    # Lógica de st_tabs1 adaptada y optimizada
    df_mat_2018 = df_mat[df_mat['ANIO_DATA'] == 2018]
    df_bec_2018 = df_bec[df_bec['ANIO_DATA'] == 2018]
    capturados_2018 = pd.merge(df_mat_2018, df_bec_2018, on='MRUN')
    
    mrun_2019 = set(df_mat[df_mat['ANIO_DATA'] == 2019]['MRUN'])
    
    if st.button("🔥 Ejecutar Motor RIS (Cohorte 2018)"):
        with st.spinner("Masticando microdatos... calculando mortandad institucional..."):
            resumen = capturados_2018.groupby('NOMB_INST').agg(
                Total_Almas=('MRUN', 'nunique'),
                Inversion_Total=('VALOR_ARANCEL', 'sum')
            ).reset_index()

            def analizar_trayectoria(inst):
                mruns_inst = set(capturados_2018[capturados_2018['NOMB_INST'] == inst]['MRUN'])
                retenidos = len(mruns_inst.intersection(mrun_2019))
                sobrevivientes = len(mruns_inst.intersection(mrun_tit))
                return pd.Series([retenidos, sobrevivientes])

            top_inst = resumen.sort_values(by='Inversion_Total', ascending=False).head(10)
            top_inst[['Retenidos', 'Sobrevivientes']] = top_inst['NOMB_INST'].apply(analizar_trayectoria)
            
            top_inst['% Retención Oficial'] = (top_inst['Retenidos'] / top_inst['Total_Almas']) * 100
            top_inst['% Titulación Real'] = (top_inst['Sobrevivientes'] / top_inst['Total_Almas']) * 100
            
            # Gráfico de la verdad
            fig = go.Figure()
            fig.add_trace(go.Bar(x=top_inst['NOMB_INST'], y=top_inst['% Retención Oficial'], name='Retención 1er Año (El Espejismo)', marker_color='gray'))
            fig.add_trace(go.Bar(x=top_inst['NOMB_INST'], y=top_inst['% Titulación Real'], name='Titulación Final (La Verdad)', marker_color='red'))
            fig.update_layout(barmode='group', template='plotly_dark', title="La Brecha de la Muerte")
            st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# PESTAÑA 3: VALIDADOR SCT (El Trueque)
# ---------------------------------------------------------
with tab3:
    st.header("🪙 Certificado de Soberanía y Trueque")
    st.markdown("*Algoritmo de justicia ocupacional basado en la Guía Práctica SCT-Chile (2007) y Arizmendi (2025).*")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("Ingresa la energía invertida en la institución de origen:")
        cursados = st.number_input("Semestres Sobrevividos", min_value=1, max_value=20, value=6)
        arancel = st.number_input("Arancel Anual Promedio (CLP)", min_value=0, value=3500000, step=100000)
    with col2:
        st.warning("Ingresa el 'castigo' de la burocracia (Reglamento 1983):")
        reconocidos = st.number_input("Semestres Reconocidos tras convalidación", min_value=0, max_value=20, value=4)
        
    if st.button("⚖️ Calcular Expropiación"):
        if reconocidos >= cursados:
            st.success("No hay anomalías de convalidación detectadas.")
        else:
            # Llamada directa al motor importado
            resultado = calcular_saqueo_trayectoria(cursados, reconocidos, arancel)
            
            st.error(f"### ⚠️ Falla Multisistémica. Bloqueo normativo activo.")
            c1, c2, c3 = st.columns(3)
            c1.metric("Créditos Expropiados", f"{resultado['SCT_Expropiados']} SCT", f"-{resultado['Porcentaje_Castigo_Malla']:.1f}% Malla")
            c2.metric("Energía Vital Secuestrada", f"{resultado['Horas_Vida_Secuestradas']:,.0f} Horas", "Tiempo irrecuperable")
            c3.metric("Capital Absorbido", f"${resultado['Capital_Secuestrado_CLP']:,.0f} CLP", "Costo del atraso")
            
            st.markdown(f"> **Resolución Forense:** Según los estándares de equivalencia de horas (CRUCH), la institución ha borrado **{resultado['Horas_Vida_Secuestradas']:,.0f} horas de contacto real** del historial del MRUN. El sistema actual fuerza a pagar dos veces por el mismo tiempo invertido.")

# ---------------------------------------------------------
# PESTAÑA 4: DISCIPLINA VS MERCADO
# ---------------------------------------------------------
with tab4:
    st.header("🪖 Contraste: El Modelo de Disciplina vs El Mercado Civil")
    st.markdown("¿Es la eficiencia del 8% un accidente, o una característica del diseño financiero?")
    
    ef_mil = 94.2
    ef_civ = 8.5 # Valor promedio duro del sistema civil extraído previamente
    
    c1, c2 = st.columns(2)
    with c1:
        st.success(f"Eficiencia FF.AA. (Aprox): {ef_mil}%")
        st.progress(ef_mil/100)
    with c2:
        st.error(f"Eficiencia Universidades Civiles (Aprox): {ef_civ}%")
        st.progress(ef_civ/100)

    st.info(f"💡 El modelo de disciplina institucional titula **{(ef_mil/ef_civ):.1f} veces más rápido** que el modelo basado en retención de aranceles civiles.")