import pandas as pd
import numpy as np

def surdao_hibrido(csv_sies="data/Oferta_Academica_2025_SIES.csv", años_min=3):
    # 1. Cargar base nacional
    df = pd.read_csv(csv_sies, encoding='latin1', errors='ignore')
    
    # Normalizar columnas (según nombres reales del SIES)
    df['Vacantes_S1'] = pd.to_numeric(df.get('Vacantes Semestre Uno', df.get('Vacantes S1')), errors='coerce')
    df['Sem_rec'] = pd.to_numeric(df.get('Semestres reconocidos', df.get('Sem_Rec_SCT')), errors='coerce')

    # 2. Filtrar carreras viables
    general = df[(df['Vacantes_S1'] > 50) & (df['Sem_rec'] >= 6)]

    # 3. Calcular años, créditos y valor humano
    general['Años_Est'] = np.clip(general['Sem_rec']/2, 3, 7)
    general['Creditos'] = general['Años_Est'] * 40
    general['Valor_Humano'] = general['Creditos'] * 12000

    # 4. Foco USACH
    usach_mask = general['Nombre IES'].str.contains('SANTIAGO|USACH', case=False, na=False)
    usach_prior = general[usach_mask & (general['Años_Est'] >= años_min)]

    # 5. Export top 50
    top_hibrido = usach_prior.nlargest(50, 'Valor_Humano')
    top_hibrido.to_csv('data/surdao_hibrido_usach_v2.csv', index=False)

    return {
        'general_carreras': len(general),
        'usach_prior_3mas': len(usach_prior),
        'top_50': top_hibrido,
        'capital_recuperable_mm': top_hibrido['Valor_Humano'].sum() / 1e6
    }

