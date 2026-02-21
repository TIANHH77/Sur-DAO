import os
import pandas as pd

# --- RUTAS DE TUS CARPETAS ---
BASE = r"C:\PROYECTOS\SURDAO\data\FUENTES_CRUDAS"
SALIDA = r"C:\PROYECTOS\SURDAO\data"

config = {
    "MATRICULA": {
        "folder": "MATRICULA_ED_SUPERIOR",
        "prefix": "Matricula-Ed-Superior-",
        "years": range(2012, 2026),
        "file_name": "MATRICULA_GLOBAL.parquet"
    },
    "ASIGNACION": {
        "folder": "ASIGNACION_BECASYCREDITOS",
        "prefix": "Asignaciones-de-Becas-y-Creditos-",
        "years": range(2012, 2025),
        "file_name": "ASIGNACIONES_GLOBAL.parquet"
    },
    "POSTULACION": {
        "folder": "POSTULACION_BECASYCREDITOS_",
        "prefix": "Postulaciones-a-Becas-y-Creditos-",
        "years": range(2012, 2025),
        "file_name": "POSTULACIONES_GLOBAL.parquet"
    }
}

def procesar_silo(nombre, settings):
    print(f"\n🚀 Iniciando fase: {nombre}")
    dfs = []
    ruta_tipo = os.path.join(BASE, settings["folder"])
    
    for anio in settings["years"]:
        carpeta_anio = os.path.join(ruta_tipo, f"{settings['prefix']}{anio}")
        if os.path.exists(carpeta_anio):
            archivos = [f for f in os.listdir(carpeta_anio) if f.endswith(('.csv', '.xlsx', '.xls'))]
            for arc in archivos:
                ruta_arc = os.path.join(carpeta_anio, arc)
                try:
                    # Lectura Robusta
                    if arc.endswith('.csv'):
                        df = pd.read_csv(ruta_arc, sep=None, engine='python', encoding='latin-1', on_bad_lines='skip')
                    else:
                        df = pd.read_excel(ruta_arc)
                    
                    # Normalización Forense de Columnas
                    df.columns = [str(c).upper().strip().replace(" ", "_") for c in df.columns]
                    df['ANIO_DATA'] = anio
                    dfs.append(df)
                    print(f"   ✅ {anio}: {arc} inyectado.")
                except Exception as e:
                    print(f"   ❌ Error en {anio} ({arc}): {e}")

    if dfs:
        final_df = pd.concat(dfs, ignore_index=True)
        # Limpieza de tipos para Parquet
        for col in final_df.columns:
            if final_df[col].dtype == 'object':
                final_df[col] = final_df[col].astype(str).replace(['nan', 'None', 'NaN'], '')
        
        final_df.to_parquet(os.path.join(SALIDA, settings["file_name"]), index=False)
        print(f"🎯 SILO GENERADO: {settings['file_name']} ({len(final_df)} registros)")

# --- EJECUCIÓN MAESTRA ---
for tipo, settings in config.items():
    procesar_silo(tipo, settings)

print("\n🦅 SUR DAO: Todos los silos están en órbita. El Centinela tiene visión total.")