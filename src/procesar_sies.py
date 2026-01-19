import pandas as pd
from difflib import get_close_matches

print("🌍 Earth Commons DAO - SURDAO Matches 2025")

# 1. Cargar SIES 2025
sies = pd.read_csv('Oferta_Academica_2025_SIES.csv', sep=';', low_memory=False)
print(f"✅ SIES: {len(sies)} carreras 2025")

# 2. Normalizar nombres de carrera
sies['Nombre_Carrera'] = sies['Nombre Carrera'].str.strip().str.title()

# 3. Datos SURDAO reales
surdao_data = [
    {'Carrera': 'Ing. Civil Informática', 'Desercion_pct': 40.5, 'Creditos': 208, 'Valor_MM': 2.5, 'Afin': 'Automatización Industrial', 'SCT_pct': 75},
    {'Carrera': 'Psicología', 'Desercion_pct': 45.2, 'Creditos': 192, 'Valor_MM': 2.3, 'Afin': 'Apoyo crítico', 'SCT_pct': 0},
    {'Carrera': 'Ciencias Exactas', 'Desercion_pct': 59.5, 'Creditos': 232, 'Valor_MM': 2.8, 'Afin': 'Ing. Civil + Pedagogía', 'SCT_pct': 60}
]
matches_df = pd.DataFrame(surdao_data)

# 4. Fuzzy match con SIES
for idx, row in matches_df.iterrows():
    query = row['Carrera'].title()
    candidates = get_close_matches(query, sies['Nombre_Carrera'].tolist(), n=1, cutoff=0.85)
    
    if candidates:
        match_carrera = candidates[0]
        sies_row = sies[sies['Nombre_Carrera'] == match_carrera].iloc[0]
        
        matches_df.at[idx, 'SIES_Match'] = match_carrera
        matches_df.at[idx, 'Universidad'] = sies_row.get('Nombre IES', 'N/A')
        matches_df.at[idx, 'Region'] = sies_row.get('Región Sede', 'N/A')
        matches_df.at[idx, 'Codigo_Carrera'] = sies_row.get('Código Carrera', 'N/A')
    else:
        matches_df.at[idx, 'SIES_Match'] = 'NO_ENCONTRADO'
        matches_df.at[idx, 'Universidad'] = 'N/A'
        matches_df.at[idx, 'Region'] = 'N/A'
        matches_df.at[idx, 'Codigo_Carrera'] = 'N/A'

# 5. Exportar CSV final
matches_df.to_csv('data/surdao_real_matches_2025.csv', index=False)
print("💾 CSV generado: surdao_real_matches_2025.csv ✅")
print(matches_df.head())

