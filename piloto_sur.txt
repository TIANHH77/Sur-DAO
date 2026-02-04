import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata

# -----------------------------
# Función para normalizar columnas
# -----------------------------
def normalize_columns(df):
    """
    Normaliza los nombres de columnas:
    - Elimina espacios al inicio y al final
    - Convierte todo a minúsculas
    - Reemplaza tildes y caracteres especiales por su forma básica
    """
    def clean(col):
        col = col.strip().lower()
        col = unicodedata.normalize('NFKD', col).encode('ascii', errors='ignore').decode('utf-8')
        return col
    df.columns = [clean(c) for c in df.columns]
    return df

# -----------------------------
# Configuración de la app
# -----------------------------
st.set_page_config(page_title="SUR DAO USACH", layout="wide", page_icon="🌑")
st.title("🌑 SUR DAO - Custodia de Trayectorias USACH")
st.markdown("**Datos reales SIES 2025 + USACH** | Infraestructura porosa para retención")

# -----------------------------
# Función para cargar CSV con fallback demo
# -----------------------------
@st.cache_data
def load_csv(path, demo_df=None, index_col=None):
    try:
        df = pd.read_csv(path)
        if index_col and index_col in df.columns:
            df.set_index(index_col, inplace=True)
        return df
    except FileNotFoundError:
        if demo_df is not None:
            st.warning(f"{path} no encontrado - usando demo")
            return demo_df
        else:
            st.warning(f"{path} no encontrado - vacío")
            return pd.DataFrame()

# -----------------------------
# Cargar datasets
# -----------------------------
real = load_csv("data/surdao_real_matches_2025.csv", demo_df=pd.DataFrame({
    "carrera": ["Ing.Civil Informática", "Psicología"],
    "desercion_pct": [40.5, 45.2],
    "creditos_sct": [208, 192],
    "impacto_mm": [2.5, 2.3]
}))

hibrido = load_csv("data/surdao_hibrido_v2.csv", demo_df=pd.DataFrame({
    "Carrera": ["Ing.Civil Informática", "Psicología"],
    "Años_Est": [7, 5],
    "Creditos": [280, 200],
    "Valor_Humano_MM": [3.36, 2.40],
    "Vacantes_Destino": [600, 150],
    "Match_Afin": ["Automatización 🟢", "🔴 Crítica Apoyo"]
}))

becas   = load_csv("data/becas.csv", index_col="ID")
junaeb  = load_csv("data/junaeb.csv", index_col="ID")
mineduc = load_csv("data/mineduc.csv", index_col="ID")
usach   = load_csv("data/usach.csv")
pares   = load_csv("data/pares.csv", index_col="ID")

# 🔮 Normalizar todos en bloque
datasets = [real, hibrido, becas, junaeb, mineduc, usach, pares]
datasets = [normalize_columns(df) for df in datasets]
real, hibrido, becas, junaeb, mineduc, usach, pares = datasets
# 👀 Depuración: mostrar columnas antes del merge
st.write("Columnas en REAL:", real.columns.tolist())
st.write("Columnas en HIBRIDO:", hibrido.columns.tolist())
st.write("Columnas en USACH:", usach.columns.tolist())
st.write("Columnas en BECAS:", becas.columns.tolist())
st.write("Columnas en JUNAEB:", junaeb.columns.tolist())
st.write("Columnas en MINEDUC:", mineduc.columns.tolist())
st.write("Columnas en PARES:", pares.columns.tolist())
# Normalización + renombrado seguro
datasets = [real, hibrido, becas, junaeb, mineduc, usach, pares]
datasets = [normalize_columns(df) for df in datasets]
real, hibrido, becas, junaeb, mineduc, usach, pares = datasets

# 🔧 Renombrar clave automáticamente
for df in [real, hibrido, usach]:
    if "Carrera" in df.columns:
        df.rename(columns={"Carrera": "carrera"}, inplace=True)
    if "programa" in df.columns:
        df.rename(columns={"programa": "carrera"}, inplace=True)




# -----------------------------
# Merge maestro
# -----------------------------
df_master = real.merge(hibrido, on="carrera", how="outer")
df_master = df_master.merge(usach, on="carrera", how="outer")
df_master = df_master.merge(becas, left_index=True, right_index=True, how="outer")
df_master = df_master.merge(junaeb, left_index=True, right_index=True, how="outer")
df_master = df_master.merge(mineduc, left_index=True, right_index=True, how="outer")
df_master = df_master.merge(pares, left_index=True, right_index=True, how="outer")

# 👀 Mostrar columnas resultantes para verificar
st.write("### Columnas en df_master:", df_master.columns.tolist())

# Exportar automáticamente a CSV maestro
df_master.to_csv("data/surdao_master.csv", index=False)

# -----------------------------
# KPIs
# -----------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Carreras Analizadas", len(df_master))
if "creditos" in df_master.columns:
    col2.metric("Créditos SCT Total", f"{df_master['creditos'].sum():.0f}")
if "valor_humano_mm" in df_master.columns:
    col3.metric("Impacto Humano", f"${df_master['valor_humano_mm'].sum():.1f}MM")

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3 = st.tabs(["📊 Datos Reales SIES", "⚠️ Riesgo Alto (>40%)", "⏱️ Burocracia vs DAO"])

with tab1:
    st.subheader("Cruces SIES 2025 + Deserción USACH")
    st.dataframe(df_master, use_container_width=True)

with tab2:
    st.subheader("Carreras Alto Riesgo (Deserción >40%)")
    if "desercion_pct" in df_master.columns:
        alto_riesgo = df_master[df_master["desercion_pct"] > 40]
        for _, row in alto_riesgo.iterrows():
            st.error(f"🚨 **{row['carrera']}** – {row['desercion_pct']:.1f}% – ${row['impacto_mm']:.1f}MM")

with tab3:
    st.subheader("Tiempos: Burocracia vs Custodia DAO")
    st.markdown("""
    | Fase | Burocracia | DAO Custodia | Diferencia |
    |------|------------|--------------|------------|
    | Detección | 6-12 meses | 1-2 semanas | 6x más rápido |
    | Respuesta | 3-6 meses | 1 semana | 12x más rápido |
    | Trazabilidad | Dispersa | Blockchain | 100% visible |
    """)

# -----------------------------
# Gráfico impacto
# -----------------------------
if "impacto_mm" in df_master.columns and "carrera" in df_master.columns:
    fig = px.bar(df_master.head(10), x="carrera", y="impacto_mm",
                 title="Impacto Humano por Carrera (Top 10)", color="desercion_pct")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("*SUR DAO Fase 1 - Datos SIES Mineduc 2025*")
st.markdown("[Repo](https://github.com/TIANHH77/-Earth-Commons-DAO)")
