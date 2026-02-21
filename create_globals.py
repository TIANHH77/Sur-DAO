import pandas as pd
import os
import re

base = r"C:\PROYECTOS\SURDAO\data"
print("🔄 Iniciando Unificación SUR DAO v5.0 [MODO ATLAS]...")

def normalizar_region(reg):
    reg = str(reg).upper()
    if 'METROPOLITANA' in reg: return 'Metropolitana'
    if 'ARICA' in reg: return 'Arica y Parinacota'
    if 'TARAPACA' in reg: return 'Tarapacá'
    if 'ANTOFAGASTA' in reg: return 'Antofagasta'
    if 'ATACAMA' in reg: return 'Atacama'
    if 'COQUIMBO' in reg: return 'Coquimbo'
    if 'VALPARAISO' in reg: return 'Valparaíso'
    if 'O\'HIGGINS' in reg or 'OHIGGINS' in reg: return 'Libertador General Bernardo O\'Higgins'
    if 'MAULE' in reg: return 'Maule'
    if 'NUBLE' in reg: return 'Ñuble'
    if 'BIOBIO' in reg or 'BIO BIO' in reg: return 'Biobío'
    if 'ARAUCANIA' in reg: return 'Araucanía'
    if 'RIOS' in reg: return 'Los Ríos'
    if 'LAGOS' in reg: return 'Los Lagos'
    if 'AYSEN' in reg: return 'Aysén del General Carlos Ibáñez del Campo'
    if 'MAGALLANES' in reg: return 'Magallanes y de la Antártica Chilena'
    return reg

def limpiar_datos(df, filename):
    # 1. Limpieza de AÑO (Recupera 'OFE_2025' y similares)
    col_anio = 'AÑO' if 'OFERTA' in filename else 'ANIO_ING_CARR_ORI'
    if col_anio in df.columns:
        df[col_anio] = pd.to_numeric(df[col_anio].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce')
        # Filtro Nuclear 2012
        df = df[df[col_anio] >= 2012].copy()
        df[col_anio] = df[col_anio].fillna(0).astype(int)
    
    # 2. Normalización Regional
    col_reg = 'REGION SEDE' if 'REGION SEDE' in df.columns else ('REGION_SEDE' if 'REGION_SEDE' in df.columns else None)
    if col_reg:
        df['REGION_SEDE'] = df[col_reg].apply(normalizar_region)
    
    # 3. Blindaje PyArrow (Tipos de datos mixtos)
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).replace(['nan', 'None', 'NaN'], '')
            
    return df

# --- PROCESO OFERTA ---
ofertas = []
for f in ["UES_OFERTA.parquet", "FFAA_OFERTA.parquet", "IP_CFT_OFERTA.parquet"]:
    p = os.path.join(base, f)
    if os.path.exists(p):
        df = pd.read_parquet(p)
        df = limpiar_datos(df, f)
        
        # Clasificador TIPO_SISTEMA
        if 'TIPO_SISTEMA' not in df.columns:
            if 'FFAA' in f: df['TIPO_SISTEMA'] = 'FF.AA.'
            elif 'IP_CFT' in f: df['TIPO_SISTEMA'] = 'IP/CFT'
            else: df['TIPO_SISTEMA'] = 'UNIVERSIDADES'
        
        # Clasificador de NIVEL
        col_carrera = 'NOMBRE CARRERA' if 'NOMBRE CARRERA' in df.columns else 'NOMB_CARRERA'
        if col_carrera in df.columns:
            carr_up = df[col_carrera].str.upper()
            df['NIVEL'] = 'PREGRADO' # Default
            df.loc[carr_up.str.contains('DIPLOMADO'), 'NIVEL'] = 'DIPLOMADO'
            df.loc[carr_up.str.contains('MAGISTER|MAGÍSTER|DOCTORADO|POSTGRADO'), 'NIVEL'] = 'POSTGRADO'
        
        ofertas.append(df)
        print(f"   ✅ {f}: {len(df)} filas GEO")

if ofertas:
    pd.concat(ofertas, ignore_index=True).to_parquet(os.path.join(base, "OFERTA_GLOBAL.parquet"), index=False)
    print("🚀 OFERTA_GLOBAL v5 GEO Generada")

# --- PROCESO TITULADOS ---
titulados = []
for f in ["UES_TITULADOS.parquet", "FFAA_TITULADOS.parquet", "IP_CFT_TITULADOS.parquet"]:
    p = os.path.join(base, f)
    if os.path.exists(p):
        df = pd.read_parquet(p)
        df = limpiar_datos(df, f)
        
        # Clasificador de NIVEL para Titulados (Sincronización)
        col_carrera = 'NOMB_CARRERA' if 'NOMB_CARRERA' in df.columns else 'NOMBRE CARRERA'
        if col_carrera in df.columns:
            carr_up = df[col_carrera].str.upper()
            df['NIVEL'] = 'PREGRADO'
            df.loc[carr_up.str.contains('DIPLOMADO'), 'NIVEL'] = 'DIPLOMADO'
            df.loc[carr_up.str.contains('MAGISTER|MAGÍSTER|DOCTORADO|POSTGRADO'), 'NIVEL'] = 'POSTGRADO'
            
        titulados.append(df)
        print(f"   🎓 {f}: {len(df)} filas GEO")

if titulados:
    pd.concat(titulados, ignore_index=True).to_parquet(os.path.join(base, "TITULADOS_GLOBAL.parquet"), index=False)
    print("🚀 TITULADOS_GLOBAL v5 GEO Generada")

print("🎯 SUR DAO v5.0 LISTO PARA DESPEGUE.")
