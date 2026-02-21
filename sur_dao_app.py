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
# --- PESTAÑA 1: NORMALIZACIÓN Y RENDERIZADO DEL MAPA ---
with tab1:
    st.header("Distribución de la Inversión Fiscal y el Saqueo")
    
    anio_mapa = st.selectbox("Seleccione Año de Auditoría", sorted(df_mat['ANIO_DATA'].unique(), reverse=True))
    
    df_mapa_anio = df_mat[df_mat['ANIO_DATA'] == anio_mapa]
    map_data = df_mapa_anio.groupby('REGION_SEDE')['VALOR_ARANCEL'].sum().reset_index()
    map_data.columns = ['REGION', 'INVERSION']
    
    # Mapeo universal para que el GeoJSON (properties.name) y SIES (REGION_SEDE) se fusionen
    mapeo_regiones = {
        "REGION DE ARICA Y PARINACOTA": "Región de Arica y Parinacota",
        "REGION DE TARAPACA": "Región de Tarapacá",
        "REGION DE ANTOFAGASTA": "Región de Antofagasta",
        "REGION DE ATACAMA": "Región de Atacama",
        "REGION DE COQUIMBO": "Región de Coquimbo",
        "REGION DE VALPARAISO": "Región de Valparaíso",
        "REGION METROPOLITANA DE SANTIAGO": "Región Metropolitana de Santiago",
        "REGION DEL LIBERTADOR GENERAL BERNARDO O'HIGGINS": "Región del Libertador General Bernardo O'Higgins",
        "REGION DEL MAULE": "Región del Maule",
        "REGION DE NUBLE": "Región de Ñuble",
        "REGION DEL BIOBIO": "Región del Biobío",
        "REGION DE LA ARAUCANIA": "Región de la Araucanía",
        "REGION DE LOS RIOS": "Región de los Ríos",
        "REGION DE LOS LAGOS": "Región de los Lagos",
        "REGION AISEN DEL GENERAL CARLOS IBANEZ DEL CAMPO": "Región de Aysén del General Carlos Ibáñez del Campo",
        "REGION DE MAGALLANES Y DE LA ANTARTICA CHILENA": "Región de Magallanes y de la Antártica Chilena"
    }
    
    map_data['REGION'] = map_data['REGION'].map(mapeo_regiones).fillna(map_data['REGION'])
    
    if geojson_chile:
        fig_map = px.choropleth_mapbox(
            map_data, geojson=geojson_chile, locations="REGION",
            featureidkey="properties.name",
            color="INVERSION", color_continuous_scale="Reds",
            mapbox_style="carto-darkmatter", opacity=0.8,
            center={"lat": -33.4489, "lon": -70.6693}, zoom=4
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="black", font_color="white")
        st.plotly_chart(fig_map, use_container_width=True)
# ---------------------------------------------------------
# PESTAÑA 2: EL ESPEJISMO (Contraste de Supervivencia)
# ---------------------------------------------------------
# PESTAÑA 2: EL ESPEJISMO DE LA RETENCIÓN (MOTOR RIS V2)
# ---------------------------------------------------------
with tab2:
    st.header("El Espejismo de la Retención vs. La Realidad")
    st.markdown("Auditoría de cohortes históricas: ¿Cuántos entran capturados por el financiamiento y cuántos logran la titulación real?")

    # 1. Selector de Cohorte Dinámico (Habilita auditoría desde 2012)
    anios_disponibles = sorted(df_mat['ANIO_DATA'].unique())
    cohorte_seleccionada = st.selectbox(
        "Seleccione Cohorte para Tracking de Supervivencia Real", 
        anios_disponibles, 
        index=anios_disponibles.index(2018) if 2018 in anios_disponibles else 0
    )

    # 2. Filtrado dinámico de la cohorte seleccionada
    df_mat_cohorte = df_mat[df_mat['ANIO_DATA'] == cohorte_seleccionada]
    df_bec_cohorte = df_bec[df_bec['ANIO_DATA'] == cohorte_seleccionada]
    
    # Estudiantes con Matrícula y Beneficio en el mismo año (Los capturados financieramente)
    capturados = df_mat_cohorte[df_mat_cohorte['MRUN'].isin(df_bec_cohorte['MRUN'])]
    
    # Identificar la cohorte de retención (Seguimiento al año siguiente)
    mrun_siguiente_anio = set(df_mat[df_mat['ANIO_DATA'] == cohorte_seleccionada + 1]['MRUN'])

    # 3. Ejecución del Motor RIS
    if st.button(f"🔥 Ejecutar Motor RIS (Cohorte {cohorte_seleccionada})"):
        with st.spinner(f"Calculando mortandad institucional de la cohorte {cohorte_seleccionada}..."):
            
            # Agregación por Institución (Top 10 por inversión de aranceles secuestrados)
            resumen = capturados.groupby('NOMB_INST').agg(
                Total_Almas=('MRUN', 'nunique'),
                Inversion_Total=('VALOR_ARANCEL', 'sum')
            ).reset_index()

            def analizar_trayectoria(inst):
                mruns_inst = set(capturados[capturados['NOMB_INST'] == inst]['MRUN'])
                # Retenidos: ¿Siguen en el sistema al año siguiente?
                retenidos = len(mruns_inst.intersection(mrun_siguiente_anio))
                # Sobrevivientes: ¿Aparecen en la base global de titulados (sin importar el año)?
                sobrevivientes = len(mruns_inst.intersection(mrun_tit))
                return pd.Series([retenidos, sobrevivientes])

            top_inst = resumen.sort_values(by='Inversion_Total', ascending=False).head(10)
            top_inst[['Retenidos', 'Sobrevivientes']] = top_inst['NOMB_INST'].apply(analizar_trayectoria)
            
            top_inst['% Retención Oficial'] = (top_inst['Retenidos'] / top_inst['Total_Almas']) * 100
            top_inst['% Titulación Real'] = (top_inst['Sobrevivientes'] / top_inst['Total_Almas']) * 100
            
            # Visualización: La Brecha de la Muerte
            fig_brecha = go.Figure()
            fig_brecha.add_trace(go.Bar(
                x=top_inst['NOMB_INST'], 
                y=top_inst['% Retención Oficial'], 
                name='Retención (Flujo de Caja)', 
                marker_color='gray'
            ))
            fig_brecha.add_trace(go.Bar(
                x=top_inst['NOMB_INST'], 
                y=top_inst['% Titulación Real'], 
                name='Titulación Final (Sobrevivencia)', 
                marker_color='red'
            ))
            
            fig_brecha.update_layout(
                title=f"Contraste Forense: Retención vs Titulación (Cohorte {cohorte_seleccionada})",
                barmode='group', template='plotly_dark', xaxis_tickangle=-45
            )
            st.plotly_chart(fig_brecha, use_container_width=True)

            st.subheader("Hallazgos por Institución")
            st.dataframe(top_inst.style.format({
                'Inversion_Total': '${:,.0f}',
                '% Retención Oficial': '{:.1f}%',
                '% Titulación Real': '{:.1f}%'
            }))
# ---------------------------------------------------------
# PESTAÑA 2: EL ESPEJISMO DE LA RETENCIÓN
# ---------------------------------------------------------
with tab2:
    st.header("El Espejismo de la Retención vs. La Realidad")
    st.markdown("Auditoría de cohortes históricas: ¿Cuántos entran capturados por el financiamiento y cuántos logran la titulación real?")

    # 1. Selector de Cohorte Dinámico
    anios_disponibles = sorted(df_mat['ANIO_DATA'].unique())
    # Por defecto 2018, pero permite auditar desde 2012
    cohorte_seleccionada = st.selectbox(
        "Seleccione Cohorte para Tracking de Supervivencia", 
        anios_disponibles, 
        index=anios_disponibles.index(2018) if 2018 in anios_disponibles else 0
    )

    # 2. Filtrado dinámico de la cohorte seleccionada
    df_mat_cohorte = df_mat[df_mat['ANIO_DATA'] == cohorte_seleccionada]
    df_bec_cohorte = df_bec[df_bec['ANIO_DATA'] == cohorte_seleccionada]
    
    # Definir los "Capturados" (Estudiantes con Matrícula y Beneficio/Crédito en el mismo año)
    capturados = df_mat_cohorte[df_mat_cohorte['MRUN'].isin(df_bec_cohorte['MRUN'])]
    
    # Identificar la cohorte de retención (Año siguiente)
    mrun_siguiente_anio = set(df_mat[df_mat['ANIO_DATA'] == cohorte_seleccionada + 1]['MRUN'])

    # 3. Ejecución del Motor RIS
    if st.button(f"🔥 Ejecutar Motor RIS (Cohorte {cohorte_seleccionada})"):
        with st.spinner(f"Masticando microdatos de la cohorte {cohorte_seleccionada}..."):
            
            # Agregación por Institución (Top 10 por inversión de aranceles)
            resumen = capturados.groupby('NOMB_INST').agg(
                Total_Almas=('MRUN', 'nunique'),
                Inversion_Total=('VALOR_ARANCEL', 'sum')
            ).reset_index()

            # Función de rastreo de trayectoria real
            def analizar_trayectoria(inst):
                mruns_inst = set(capturados[capturados['NOMB_INST'] == inst]['MRUN'])
                # Retenidos: Siguen matriculados al año siguiente
                retenidos = len(mruns_inst.intersection(mrun_siguiente_anio))
                # Sobrevivientes: Aparecen en la base histórica de titulados
                sobrevivientes = len(mruns_inst.intersection(mrun_tit))
                return pd.Series([retenidos, sobrevivientes])

            # Análisis de las 10 instituciones con mayor flujo de capital
            top_inst = resumen.sort_values(by='Inversion_Total', ascending=False).head(10)
            top_inst[['Retenidos', 'Sobrevivientes']] = top_inst['NOMB_INST'].apply(analizar_trayectoria)
            
            # Cálculo de Brechas Forenses
            top_inst['% Retención Oficial'] = (top_inst['Retenidos'] / top_inst['Total_Almas']) * 100
            top_inst['% Titulación Real'] = (top_inst['Sobrevivientes'] / top_inst['Total_Almas']) * 100
            
            # Visualización: La Brecha de la Muerte
            fig_brecha = go.Figure()
            fig_brecha.add_trace(go.Bar(
                x=top_inst['NOMB_INST'], 
                y=top_inst['% Retención Oficial'], 
                name='% Retención (Flujo de Caja)', 
                marker_color='gray'
            ))
            fig_brecha.add_trace(go.Bar(
                x=top_inst['NOMB_INST'], 
                y=top_inst['% Titulación Real'], 
                name='% Titulación Real (Logro)', 
                marker_color='red'
            ))
            
            fig_brecha.update_layout(
                title=f"Contraste Forense: Retención vs Titulación (Cohorte {cohorte_seleccionada})",
                barmode='group',
                xaxis_tickangle=-45,
                height=500
            )
            
            st.plotly_chart(fig_brecha, use_container_width=True)
            
            # Tabla de Hallazgos
            st.subheader("Hallazgos por Institución")
            st.dataframe(top_inst.style.format({
                'Inversion_Total': '${:,.0f}',
                '% Retención Oficial': '{:.1f}%',
                '% Titulación Real': '{:.1f}%'
            }))
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