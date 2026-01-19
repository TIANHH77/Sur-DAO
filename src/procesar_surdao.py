import pandas as pd

# Base SURDAO
sies = pd.read_csv("data/surdao_real_matches_2025.csv")

# Diccionario de empleabilidad (ejemplo simplificado)
empleabilidad_dict = {
    "Ingeniería Civil en Electricidad": {"Empleabilidad_%": 96.3, "Ingreso": "2.5M-3M"},
    "Ingeniería Civil en Minas": {"Empleabilidad_%": 91.9, "Ingreso": ">3.5M"},
    "Ingeniería de Ejecución en Metalurgia": {"Empleabilidad_%": 72.2, "Ingreso": "1.8M-1.9M"},
    "Pedagogía en Química y Biología, y en Física y Matemáticas": {"Empleabilidad_%": 95.8, "Ingreso": "1.2M-1.3M"},
    "Pedagogía en Matemática y Computación": {"Empleabilidad_%": 94.9, "Ingreso": "1.3M-1.4M"},
    "Derecho": {"Empleabilidad_%": 80.2, "Ingreso": "2.1M-2.2M"},
    "Ingeniería de Ejecución Industrial": {"Empleabilidad_%": 89.4, "Ingreso": None},
    "Ingeniería Comercial": {"Empleabilidad_%": 89.7, "Ingreso": None},
    "Trabajo Social": {"Empleabilidad_%": 83.1, "Ingreso": None},
}

# Mapear empleabilidad e ingreso
sies["Empleabilidad_%"] = sies["Match_SIES"].map(lambda x: empleabilidad_dict.get(x, {}).get("Empleabilidad_%"))
sies["Ingreso_1er_año"] = sies["Match_SIES"].map(lambda x: empleabilidad_dict.get(x, {}).get("Ingreso"))

# Guardar SUPER CSV
sies.to_csv("data/surdao_super_matches_2026.csv", index=False)


