import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURACIÓN DEL HANGAR ---
st.set_page_config(page_title="SUR DAO - Auditoría Sistémica", layout="wide", page_icon="🌑")

# Estética Dark Mode con acentos en Verde (Rescate) y Rojo (Alerta)
st.markdown("""
<style>
    .stApp {background-color: #0E1117;}
    .metric-card {background-color: #1c202a; padding: 20px; border-radius: 12px; border-top: 4px solid #4CAF50;}
    .shame-card {background-color: #1c202a; padding: 20px; border-radius: 12px; border-top: 4px solid #FF4B4B;}
    .big-number {font-size: 2.5em; font-weight: bold; color: #4CAF50;}
    .shame-number {font-size: 2.5em; font-weight: bold; color: #FF4B4B;}
</style>
""", unsafe_allow_html=True)

# --- 2. EL REACTOR DE DATOS (SABUESO FINAL) ---
def load_data():
    df_master = None
    
    # Rutas esperadas tras tu limpieza
    path_of = 'data/oferta.csv'
    path_ret = 'data/retencion.csv'
    path_dur = 'data/duracion.csv'
    
    if os.path.exists(path_of) and os.path.exists(path_ret):
        try:
            # Carga Oferta (Suelen ser ; en SIES)
            df_of = pd.read_csv(path_of, sep=';', encoding='latin1', on_bad_lines='skip')
            
            # Carga Retención
            df_ret = pd.read_csv(path_ret, encoding='latin1', on_bad_lines='skip')
            
            # Limpieza rápida de Arancel
            col_aran = [c for c in df_of.columns if 'Arancel' in c][0]
            df_of['Arancel_Num'] = pd.to_numeric(df_of[col_aran].astype(str).str.replace(r'[$.]', '', regex=True), errors='coerce').fillna(0)
            
            # Normalización para el Merge (IES a Mayúsculas)
            c_ies_of = [c for c in df_of.columns if 'Nombre IES' in c][0]
            df_of['JOIN_KEY'] = df_of[c_ies_of].str.upper().str.strip()
            
            c_ies_ret = [c for c in df_ret.columns if 'Nombre' in c and 'institu' in c.lower()][0]
            df_ret['JOIN_KEY'] = df_ret[c_ies_ret].str.upper().str.strip()
            
            # Merge
            df_master = pd.merge(df_of, df_ret, on='JOIN_KEY', how='left')
            
            # KPI de Deserción (Buscamos columna 2024)
            c_val = [c for c in df_ret.columns if '2024' in str(c)][0]
            df_master['Retencion'] = pd.to_numeric(df_master[c_val], errors='coerce').fillna(0.75)
            df_master['Desercion'] = 1 - df_master['Retencion']
            df_master['Capital_Riesgo'] = (df_master['Arancel_Num'] * df_master['Desercion']) / 1000000
            
            return df_master
        except Exception as e:
            st.error(f"Error procesando CSVs: {e}")
    return None

df = load_data()

# --- 3. INTERFAZ DE AUDITORÍA ---
st.title("🌑 SUR DAO: Auditoría de Capital Humano")
st.markdown("#### *Documentando la ineficiencia sistémica y el Muro Invisible*")

if df is not None:
    # Sidebar
    st.sidebar.header("⚙️ Configuración DAO")
    rescate_pct = st.sidebar.slider("% Validación de Trayectoria (Res. 1983)", 0, 100, 20)
    
    # KPIs Principales
    total_riesgo = df['Capital_Riesgo'].sum()
    total_rescate = total_riesgo * (rescate_pct / 100)
    
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"<div class='shame-card'><h4>💸 Sangría Sistémica</h4><p class='shame-number'>${total_riesgo:,.0f} MM</p><p>Capital en riesgo por deserción</p></div>", unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='metric-card'><h4>🛡️ Rescate SUR DAO</h4><p class='big-number'>${total_rescate:,.0f} MM</p><p>Potencial de validación ética</p></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='metric-card'><h4>⚖️ Base Legal</h4><p class='big-number'>Res. 8417</p><p>Formación Integral Activa</p></div>", unsafe_allow_html=True)

    st.divider()

    # Pestañas
    tab1, tab2, tab3 = st.tabs(["🚩 El Muro Invisible", "⏳ Deuda de Vida", "📊 Ranking de Fuga"])

    with tab1:
        st.subheader("Brecha de Retención por Origen Socioeconómico (2024)")
        # Gráfico basado en tu hallazgo: Columna 7 (Municipal) vs Columna 10 (Pagado)
        brecha_fig = pd.DataFrame({
            'Origen': ['Municipal (Col 7)', 'Subvencionado', 'Part. Pagado (Col 10)'],
            'Retención (%)': [71.0, 76.0, 81.0] # Datos promedio SIES que viste
        })
        fig = px.bar(brecha_fig, x='Origen', y='Retención (%)', color='Origen', 
                     color_discrete_map={'Municipal (Col 7)':'#FF4B4B', 'Part. Pagado (Col 10)':'#4CAF50'},
                     text='Retención (%)')
        st.plotly_chart(fig, use_container_width=True)
        st.info("💡 El 'Muro Invisible' es ese 10% de diferencia. SUR DAO custodia las trayectorias que el sistema descarta por origen.")

    with tab2:
        st.subheader("Sobreduración: El Secuestro del Tiempo")
        if os.path.exists('data/duracion.csv'):
            st.success("Datos de duración real cargados.")
            # Aquí se puede expandir el análisis de años extra
        else:
            st.warning("Sube 'duracion.csv' para calcular la deuda exacta de años de vida.")
        
        st.write("---")
        st.markdown("##### Simulación de Impacto Temporal")
        anos_extra = st.slider("Años de Sobreduración Promedio", 0.0, 5.0, 2.3)
        costo_oportunidad = anos_extra * 12 * 600000 # 12 meses * Sueldo Mínimo aprox
        st.metric("Costo de Oportunidad por Alumno", f"${costo_oportunidad:,.0f} CLP", f"+{anos_extra} años")

    with tab3:
        st.subheader("Fuga de Capital por Institución")
        top_fuga = df.groupby('JOIN_KEY')['Capital_Riesgo'].sum().reset_index().sort_values('Capital_Riesgo', ascending=False).head(15)
        fig_fuga = px.bar(top_fuga, x='JOIN_KEY', y='Capital_Riesgo', color='Capital_Riesgo', color_continuous_scale='Reds')
        st.plotly_chart(fig_fuga, use_container_width=True)

else:
    st.error("🚨 Hangar Vacío: No se detectan archivos en `data/`.")
    st.markdown("""
    ### Instrucciones de Despliegue:
    1. Asegúrate de que tus archivos se llamen exactamente: `oferta.csv` y `retencion.csv`.
    2. Deben estar dentro de la carpeta `data/`.
    3. Si el error persiste, revisa que el separador de `oferta.csv` sea punto y coma (`;`).
    """)
