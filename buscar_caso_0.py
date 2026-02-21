import pandas as pd

print("🔍 Despertando al Sabueso v3.0: Adaptándose a la Matriz de Microdatos...")

try:
    # --- 1. MATRÍCULA (Contando a la gente) ---
    print("⏳ Extrayendo registros individuales (MRUN)...")
    # Usamos los nombres exactos que nos chivó el error
    df_mat = pd.read_parquet("data/MATRICULA_GLOBAL.parquet", 
                             columns=['ANIO_DATA', 'NOMB_INST', 'NOMB_CARRERA', 'MRUN'])

    # Renombramos para estandarizar
    df_mat.columns = ['ANIO', 'INSTITUCION', 'CARRERA', 'MRUN']

    print("🧮 Filtrando fantasmas y sumando alumnos reales...")
    # Filtro de instituciones vivas (2023 en adelante)
    vivos = df_mat[df_mat['ANIO'] >= 2023]['INSTITUCION'].unique()
    df_mat = df_mat[df_mat['INSTITUCION'].isin(vivos)]

    # Magia Negra: Contamos cuántas personas únicas entraron a cada carrera
    resumen_mat = df_mat.groupby(['INSTITUCION', 'CARRERA'])['MRUN'].count().reset_index()
    resumen_mat.rename(columns={'MRUN': 'MATRICULADOS_TOTAL'}, inplace=True)

    # --- 2. ASIGNACIONES (Contando la plata) ---
    print("⏳ Rastreado los fondos del Estado...")
    try:
        # Cargamos la bóveda de dinero
        df_bec = pd.read_parquet("data/ASIGNACIONES_GLOBAL.parquet")
        
        # Llevamos todo a mayúsculas para que no se escape nada
        df_bec.columns = [str(c).upper() for c in df_bec.columns]

        # Buscamos heurísticamente las columnas (porque siempre le cambian el nombre)
        col_anio = next(c for c in df_bec.columns if 'ANIO' in c or 'AÑO' in c)
        col_inst = next(c for c in df_bec.columns if 'INST' in c)
        col_carr = next(c for c in df_bec.columns if 'CARR' in c)
        col_monto = next(c for c in df_bec.columns if 'MONTO' in c or 'BENEFICIO' in c or 'PAGO' in c)

        df_bec = df_bec[[col_anio, col_inst, col_carr, col_monto]]
        df_bec.columns = ['ANIO', 'INSTITUCION', 'CARRERA', 'MONTO_BENEFICIO']

        print("💰 Sumando los cheques fiscales...")
        df_bec['MONTO_BENEFICIO'] = pd.to_numeric(df_bec['MONTO_BENEFICIO'], errors='coerce').fillna(0)
        resumen_bec = df_bec.groupby(['INSTITUCION', 'CARRERA'])['MONTO_BENEFICIO'].sum().reset_index()

        # --- 3. EL CRUCE FATAL ---
        print("⚔️ Ejecutando el Cruce Forense (Matrícula vs Dinero)...")
        cruce = pd.merge(resumen_mat, resumen_bec, on=['INSTITUCION', 'CARRERA'], how='inner')

        # Filtro de Actos (Pregrado vs Posgrado)
        keywords = 'DIPLOMADO|MAGISTER|DOCTORADO|POSTITULO|POSTÍTULO|ESPECIALIDAD|MAGÍSTER'
        mask_pos = cruce['CARRERA'].str.contains(keywords, case=False, na=False)

        top_pre = cruce[~mask_pos].sort_values(by='MONTO_BENEFICIO', ascending=False)
        top_pos = cruce[mask_pos].sort_values(by='MONTO_BENEFICIO', ascending=False)

        # --- 4. IMPRESIÓN DEL REPORTE ---
        print("\n" + "="*80)
        print("🚨 ACTO 1: EL SAQUEO PÚBLICO (TOP 10 PREGRADO) 🚨")
        print("="*80)
        for index, row in top_pre.head(10).iterrows():
            print(f"🏛️ {row['INSTITUCION']} | 📚 {row['CARRERA']}")
            print(f"   ➔ Matrícula Histórica: {row['MATRICULADOS_TOTAL']:,.0f} alumnos capturados")
            print(f"   ➔ Plata del Estado: ${row['MONTO_BENEFICIO']/1e6:,.1f} Millones")
            print("-" * 50)

        print("\n" + "="*80)
        print("🚨 ACTO 2: LA CAJA CHICA (TOP 10 POSTGRADOS/DIPLOMADOS) 🚨")
        print("="*80)
        for index, row in top_pos.head(10).iterrows():
            print(f"🏛️ {row['INSTITUCION']} | 📚 {row['CARRERA']}")
            print(f"   ➔ Matrícula Histórica: {row['MATRICULADOS_TOTAL']:,.0f} alumnos capturados")
            print(f"   ➔ Plata del Estado: ${row['MONTO_BENEFICIO']/1e6:,.1f} Millones")
            print("-" * 50)

    except StopIteration:
        # Si fallan los nombres en las Asignaciones, las imprimimos para hackearlas
        print(f"\n❌ El sistema de Becas usa nombres ocultos.")
        df_test = pd.read_parquet("data/ASIGNACIONES_GLOBAL.parquet")
        print("\n🔍 Nombres de columnas en la bóveda de dinero:\n", df_test.columns.tolist())

except Exception as e:
    print(f"❌ Error crítico en el motor: {e}")