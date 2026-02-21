import pandas as pd

print("🔍 Sabueso v5.1 (La Guillotina Ajustada): Calibrando el filo...")

try:
    # 1. Cargar Matrícula (Costo y Personas)
    print("⏳ Cruzando la matriz financiera (Aranceles vs MRUN)...")
    df_mat = pd.read_parquet("data/MATRICULA_GLOBAL.parquet", 
                             columns=['ANIO_DATA', 'NOMB_INST', 'NOMB_CARRERA', 'MRUN', 'VALOR_ARANCEL'])
    
    # 2. Cargar Asignaciones (El beneficio estatal)
    df_bec = pd.read_parquet("data/ASIGNACIONES_GLOBAL.parquet",
                             columns=['ANIO_DATA', 'MRUN', 'BENEFICIO_BECA_FSCU'])

    df_mat['VALOR_ARANCEL'] = pd.to_numeric(df_mat['VALOR_ARANCEL'], errors='coerce').fillna(0)
    
    # Estandarizamos texto para que no falle el cruce
    df_mat['NOMB_CARRERA'] = df_mat['NOMB_CARRERA'].astype(str).str.strip().str.upper()
    df_mat['NOMB_INST'] = df_mat['NOMB_INST'].astype(str).str.strip().str.upper()

    # El Cruce de Captura (Plata + Capturados)
    df_cruce = pd.merge(df_mat, df_bec, on=['MRUN', 'ANIO_DATA'], how='inner')
    vivos = df_cruce[df_cruce['ANIO_DATA'] >= 2023]['NOMB_INST'].unique()
    df_cruce = df_cruce[df_cruce['NOMB_INST'].isin(vivos)]

    print("💰 Consolidando el desfalco...")
    resumen = df_cruce.groupby(['NOMB_INST', 'NOMB_CARRERA']).agg(
        ALUMNOS_ESTATALES=('MRUN', 'nunique'),
        TOTAL_ARANCEL_COBRADO=('VALOR_ARANCEL', 'sum')
    ).reset_index()

    # 3. Cargar Titulados (La Realidad)
    print("⏳ Abriendo la bóveda de Titulados para buscar sobrevivientes...")
    df_tit = pd.read_parquet("data/TITULADOS_GLOBAL.parquet")
    df_tit.columns = [str(c).upper() for c in df_tit.columns]
    
    # Búsqueda a prueba de balas: obligamos a que busque el NOMBRE y no el CÓDIGO
    col_inst_tit = next(c for c in df_tit.columns if 'INST' in c and ('NOMB' in c or 'NOMBRE' in c))
    col_carr_tit = next(c for c in df_tit.columns if 'CARR' in c and ('NOMB' in c or 'NOMBRE' in c))
    
    # Convertimos a texto para igualar
    df_tit[col_inst_tit] = df_tit[col_inst_tit].astype(str).str.strip().str.upper()
    df_tit[col_carr_tit] = df_tit[col_carr_tit].astype(str).str.strip().str.upper()

    if 'MRUN' in df_tit.columns:
        resumen_tit = df_tit.groupby([col_inst_tit, col_carr_tit])['MRUN'].nunique().reset_index()
        resumen_tit.columns = ['NOMB_INST', 'NOMB_CARRERA', 'TOTAL_TITULADOS']
    else:
        col_total = next(c for c in df_tit.columns if 'TOTAL' in c or 'TITULADO' in c and c not in [col_inst_tit, col_carr_tit])
        df_tit[col_total] = pd.to_numeric(df_tit[col_total], errors='coerce').fillna(0)
        resumen_tit = df_tit.groupby([col_inst_tit, col_carr_tit])[col_total].sum().reset_index()
        resumen_tit.columns = ['NOMB_INST', 'NOMB_CARRERA', 'TOTAL_TITULADOS']

    # 4. EL CRUCE FATAL (Dinero vs Titulados)
    print("⚔️ Ejecutando el Cruce Final: Tasa de Mortandad Institucional...")
    informe_final = pd.merge(resumen, resumen_tit, on=['NOMB_INST', 'NOMB_CARRERA'], how='left')
    informe_final['TOTAL_TITULADOS'] = informe_final['TOTAL_TITULADOS'].fillna(0)

    # Separar Pregrado y Posgrado
    keywords = 'DIPLOMADO|MAGISTER|DOCTORADO|POSTITULO|POSTÍTULO|ESPECIALIDAD|MAGÍSTER'
    mask_pos = informe_final['NOMB_CARRERA'].str.contains(keywords, case=False, na=False)

    top_pre = informe_final[~mask_pos].sort_values(by='TOTAL_ARANCEL_COBRADO', ascending=False)

    # 5. Imprimir la Guillotina
    print("\n" + "="*80)
    print("💀 EL EMBUDO DE LA MUERTE (TOP 10 PREGRADO) 💀")
    print("="*80)
    for index, row in top_pre.head(10).iterrows():
        print(f"🏛️ {row['NOMB_INST']} | 📚 {row['NOMB_CARRERA']}")
        print(f"   ➔ Dinero Fiscal Capturado: ${row['TOTAL_ARANCEL_COBRADO']/1e6:,.1f} Millones")
        print(f"   ➔ Alumnos que entraron (Con Beca): {row['ALUMNOS_ESTATALES']:,.0f}")
        print(f"   ➔ Sobrevivientes (Titulados Históricos): {row['TOTAL_TITULADOS']:,.0f}")
        
        # Calcular el porcentaje de los que lograron salir vivos
        if row['ALUMNOS_ESTATALES'] > 0:
            tasa = (row['TOTAL_TITULADOS'] / row['ALUMNOS_ESTATALES']) * 100
            print(f"   ➔ Tasa de Titulación Histórica: {tasa:.1f}%")
        print("-" * 50)

except Exception as e:
    print(f"❌ Error crítico en el filo: {e}")
    print(f"🔍 Columnas en Titulados: {df_tit.columns.tolist()}")