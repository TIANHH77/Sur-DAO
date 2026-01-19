import streamlit as st
import pandas as pd

st.title("SUR DAO - Capa Sombra Dashboard")

# Cargar datasets
usach = pd.read_csv("data/usach.csv")
mineduc = pd.read_csv("data/mineduc.csv")
junaeb = pd.read_csv("data/junaeb.csv")
becas = pd.read_csv("data/becas.csv")
pares = pd.read_csv("data/pares.csv")

# Merge datasets
df_full = usach.merge(mineduc, on="ID", how="left") \
               .merge(junaeb, on="ID", how="left") \
               .merge(becas, on="ID", how="left") \
               .merge(pares, on="ID", how="left")

st.subheader("🧑‍🎓 Cohorte completa")
st.dataframe(df_full)

