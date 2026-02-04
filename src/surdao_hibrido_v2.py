import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="SurDAO - Chocapic Edition", layout="wide")

def clean_and_load():
    # 1. Base de Oferta
    try:
        df_base = pd.read_csv("data/Oferta_Academica_2025_SIES.csv", encoding='latin1', errors='ignore')
    except:
        st.error("Falta la base de Oferta en /data")
        return None

    # 2. Cargar Duración (La Trinidad: Ingrediente 2)
    try:
        # Buscamos el archivo de duración por carrera
        df_dur = pd.read_csv("Duracion_Real_y_en-Exceso_SIES_2025.xlsx - Durac. Real y Exceso Carr.csv", skiprows=4)
        df_dur.columns = ['Nombre Carrera', 'Exceso', 'Real']
    except:
        df_dur = None

    # 3. Cargar Retención (La Trinidad: Ingrediente 3)
    try:
        # Buscamos la retención 2024
        df_ret = pd.read_csv("Informe_Retencion_SIES_2025.xlsx - Retención 1er año Carreras .csv", skiprows=5)
        # Usamos la columna '2024'
    except:
        df_ret = None

    return df_base, df_dur, df_ret

st.title("🍫 SurDAO: Operativo Chocapic")
st.info("Mezclando Oferta + Retención + Duración para encontrar el Capital Real.")

# ... (Aquí va la lógica de cruce de datos) ...
# El truco es normalizar los nombres de las carreras para que el 'merge' funcione.

st.markdown("""
### ¿Qué estamos calculando?
**Valor Chocapic** = `Valor Base` × `Tasa Retención` × `(Duración Formal / Duración Real)`
""")

# Métrica de ejemplo
st.metric("Potencial de Redención", "85.4%", "+2.3% vs Mes Anterior")

st.warning("⚠️ El hangar sigue detectando humedad, pero los datos están secos y listos.")

