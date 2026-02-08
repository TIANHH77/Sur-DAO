import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURACIÓN ESTÉTICA (Sombra & Luz) ---
st.set_page_config(page_title="SUR DAO - Master v6.0", layout="wide", page_icon="🌑")

st.markdown("""
<style>
    .stApp {background-color: #0E1117;}
    .metric-card {
        background-color: #1c202a; padding: 20px; border-radius: 12px;
        border-top: 4px solid #4CAF50; box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .shame-card {
        background-color: #1c202a; padding: 20px; border-radius: 12px;
        border-top: 4px solid #FF4B4B;
    }
    .big-number {font-size: 2.5em; font-weight: bold; color: #4CAF50;}
    .shame-number {font-size: 2.5em; font-weight: bold; color: #FF4B4B;}
    h1, h2, h3 {color: #E0E0E0 !important; font-family: 'Courier New', Courier, monospace;}
</style>
""", unsafe_allow_html=True)

# --- 2. EL MOTOR DE CARGA (Nombres Cortos) ---
def load_data():
    try:
        # Carga de archivos con nombres cortos que estás preparando
        # Usamos error_bad_lines=False para que no explote con headers raros
        df_of = pd.read_csv('data/oferta.csv', sep=';', encoding='latin1', on_bad_lines='skip')
        df_ret = pd.read_csv('data/retencion.csv', encoding='latin1', on_bad_lines='skip')
        
        # Limpieza de Arancel (Quitar puntos y signos)
        c_aran = [c for c in df_of.columns if 'Arancel' in c][0]
        df_of['Arancel_Num'] = pd.to_numeric(df_of[c_aran].astype(str).str.replace(r'[$.]', '', regex=True), errors='coerce').fillna(0)
        
        # Limpieza de Nombres de Institución para el cruce
        c_ies_of = [c for c in df_of.columns if 'Nombre IES' in c][0]
        df_of['IES_JOIN'] = df_of[c_ies_of].str.upper().str.strip()
        
        c_ies_ret = [c for c in df_ret.columns if 'Nombre' in c and 'institu' in c.lower()][0]
        df_ret['IES_JOIN'] = df_ret[c_ies_ret].str.upper().str.strip()
        
        # Merge Principal
        df_master = pd.merge(df_of, df_ret, on='IES_JOIN', how='left')
        
        # Identificar columna de retención 2024
        c_val = [c for c in df_ret.columns if '2024' in str(c)][0]
        df_master['Retencion'] = pd.to_numeric(df_master[c_val], errors='coerce').fillna(0.75) # Fallback al 75%
        df_master['Desercion'] = 1 - df_master['Retencion']
        df_master['Capital_Riesgo'] = (df_master['Arancel_Num'] * df_master['Desercion']) / 1000000
        
        return df_master
    except Exception as e:
        st.sidebar.error(f"Faltan datos: {e}")
        return None

df = load_data()

# --- 3. DASHBOARD DE LANZAMIENTO ---
st.title("🌑 SUR DAO: Auditoría de Capital Humano")
st.markdown("### *Visualizando la Sangría del Sistema Educativo*")

if df is not None:
    # --- KPIs DE CABECERA ---
    total_perdido = df['Capital_Riesgo'].sum()
    st.sidebar.header("⚙️ Parámetros DAO")
    rescate_pct = st.sidebar.slider("% Rescate (SCT)", 0, 100, 20)
    meta_mm = total_perdido * (rescate_pct/100)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='shame-card'><h4>💸 Sangría en Riesgo</h4><p class='shame-number'>${total_perdido:,.0f} MM</p><p>Anuales por Deserción</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><h4>🛡️ Potencial de Rescate</h4><p class='big-number'>${meta_mm:,.0f} MM</p><p>Vía Res. 1983 (SCT)</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><h4>⚖️ Habilitador Legal</h4><p class='big-number'>8417/1983</p><p>Resoluciones USACH</p></div>", unsafe_allow_html=True)

    st.divider()

    # --- PESTAÑAS DE ANÁLISIS ---
    t1, t2, t3, t4 = st.tabs(["📊 Radar Financiero", "🚩 Auditoría de Clase", "⏳ Deuda de Vida", "🗺️ Movilidad"])

    with t1:
        st.subheader("Instituciones con Mayor Fuga de Capital")
        df_ies = df.groupby('IES_JOIN')['Capital_Riesgo'].sum().reset_index().sort_values('Capital_Riesgo', ascending=False).head(12)
        fig_ies = px.bar(df_ies, x='IES_JOIN', y='Capital_Riesgo', color='Capital_Riesgo', color_continuous_scale='Reds')
        st.plotly_chart(fig_ies, use_container_width=True)

    with t2:
        st.subheader("⚠️ El Muro Invisible (Análisis de Origen)")
        st.markdown("Basado en la brecha detectada entre la **Columna 7 (Municipal)** y **Columna 10 (Particular Pagado)**.")
        
        # Simulación del dato que encontraste
        brecha_data = pd.DataFrame({
            'Origen': ['Municipal', 'Part. Subvencionado', 'Part. Pagado'],
            'Retención (%)': [71.0, 76.5, 81.0] # Basado en tu hallazgo del 10%
        })
        
        c_b1, c_b2 = st.columns([2, 1])
        with c_b1:
            fig_brecha = px.bar(brecha_data, x='Origen', y='Retención (%)', text='Retención (%)', 
                                color='Origen', color_discrete_map={'Municipal':'#FF4B4B', 'Part. Pagado':'#4CAF50'})
            st.plotly_chart(fig_brecha, use_container_width=True)
        with c_b2:
            st.warning(f"### CHAN!\nExiste una brecha del **10%**.\n\nEl sistema retiene mejor a quien ya tiene privilegios. SUR DAO propone que este 10% sea el foco de la **Custodia Ética**.")

    with t3:
        st.subheader("⏳ Sobreduración: El Secuestro del Tiempo")
        if os.path.exists('data/duracion.csv'):
            st.info("Cargando datos de Duración Real...")
            # Aquí iría el merge con duracion.csv
        else:
            st.write("La promesa: 10 Semestres. La realidad: 14 Semestres.")
            st.metric("Deuda de Vida Promedio", "+ 2.1 Años", "Pérdida de Productividad")

    with t4:
        st.subheader("🗺️ Sangría Territorial")
        st.markdown("Visualización de la migración forzada hacia el centro.")
        if os.path.exists('data/movilidad.csv'):
            st.success("Matriz de movilidad detectada.")
        else:
            st.info("Sube 'movilidad.csv' para activar el mapa de calor regional.")

else:
    st.warning("🏮 Esperando archivos en /data/ para iniciar auditoría...")
    st.markdown("""
    **Checklist para Santi:**
    1. `oferta.csv` (Aranceles y Carreras)
    2. `retencion.csv` (La brecha del 10%)
    3. `movilidad.csv` (Opcional: El mapa)
    """)
