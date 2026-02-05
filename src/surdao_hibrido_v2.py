import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata
import json
import os

# --- 1. NORMALIZACIÓN GALÁCTICA ---
def normalize_columns(df):
    def clean(col):
        col = col.strip().lower()
        col = unicodedata.normalize('NFKD', col).encode('ascii', errors='ignore').decode('utf-8')
        return col
    df.columns = [clean(c) for c in df.columns]
    return df

# --- 2. CONFIGURACIÓN Y TÍTULOS ---
st.set_page_config(page_title="SUR DAO - Capa Sombra", layout="wide", page_icon="🌑")
st.title("🌑 SUR DAO - Capa Sombra Dashboard")
st.markdown("### *Develando el Capital Humano en la Zona Gris*")

# --- 3. CARGA DE DATOS CON RESILIENCIA ---
@st.cache_data
def load_and_prep():
    # Creamos carpeta data si no existe para evitar errores
    if not os.path.exists('data'): os.makedirs('data')
    
    # Carga de archivos con los fallbacks de tu modo cannabis
    real = pd.DataFrame({
        "carrera": ["Ing.Civil Informática", "Psicología", "Terapia Ocupacional"],
        "desercion_pct": [40.5, 45.2, 38.0],
        "impacto_mm": [2.5, 2.3, 1.8]
    })
    
    # Intentar cargar el Master Merge si existe, si no, usar demo
    try:
        df_m = pd.read_csv("data/surdao_master.csv")
    except:
        df_m = real # Fallback

    return normalize_columns(df_m)

df_master = load_and_prep()

# --- 4. GENERADOR DEL ADN (Para el Portal HTML) ---
# Esto alimenta el 'index.html' que encontraste
metricas_sombra = {
    "metricas": {
        "desercion_primer_ano": round(df_master['desercion_pct'].mean(), 1) if 'desercion_pct' in df_master.columns else 28.8,
        "capital_social_riesgo": f"${df_master['impacto_mm'].sum():.1f}MM" if 'impacto_mm' in df_master.columns else "$7.3MM",
        "estudiantes_en_sombra": len(df_master) * 1000 # Escala simbólica
    }
}
with open('data_sur.json', 'w') as f:
    json.dump(metricas_sombra, f)

# --- 5. INTERFAZ DE COMANDO (TABS) ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Auditoría SIES", "⚠️ Alerta de Sombra", "⚖️ Burocracia vs DAO", "🤝 Comunidad"])

with tab1:
    st.subheader("Cruce Maestro de Trayectorias")
    st.dataframe(df_master, use_container_width=True)
    
    if "impacto_mm" in df_master.columns:
        fig = px.bar(df_master, x="carrera", y="impacto_mm", color="desercion_pct",
                     title="Capital Humano Recuperable por Nodo",
                     color_continuous_scale="Viridis")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Zonas de Fricción Crítica")
    if "desercion_pct" in df_master.columns:
        riesgo = df_master[df_master["desercion_pct"] > 35]
        for _, row in riesgo.iterrows():
            st.warning(f"📍 **{row['carrera']}**: Trayectoria herida. Impacto: ${row['impacto_mm']}MM")

with tab3:
    st.subheader("Eficiencia de la Resonancia")
    st.markdown("""
    | Dimensión | Burocracia Institucional | SUR DAO (Capa Sombra) | Ganancia de Resonancia |
    | :--- | :--- | :--- | :--- |
    | **Visibilidad** | Registro de Defunción | Trayectoria Viva | +100% |
    | **Valor** | Deuda Bancaria | Capital Social | Incalculable |
    | **Acción** | Listas de Espera | Trueque Inmediato | 12x Velocidad |
    """)

with tab4:
    st.subheader("🤝 Formas de Contribuir")
    st.info("No importa si tu aporte es técnico, narrativo o comunitario: cada contribución fortalece el común.")
    st.markdown("- **Código:** Mejora el motor en `dashboard_real_sies.py`.")
    st.markdown("- **Datos:** Valida los datasets en `data/`.")
    st.markdown("- **Proyectos:** Conecta iniciativas territoriales.")

st.sidebar.markdown("---")
st.sidebar.write("🌑 **SUR DAO v10.0**")
st.sidebar.write("Modo: **Análisis de Resonancia**")
