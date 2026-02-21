import pandas as pd

print("🚀 Iniciando 'Trazador de Supervivencia' de SUR DAO...")
print("📡 Objetivo: Seguir al ser humano (MRUN) a través del laberinto institucional.")

try:
    # 1. Definir la Cohorte de Captura (Alumnos con plata fiscal en un año base, ej: 2018)
    # Ajusta el año si quieres ver una generación más antigua
    ANIO_BASE = 2018
    print(f"⏳ Identificando a los capturados en el año {ANIO_BASE}...")
    
    df_mat = pd.read_parquet("data/MATRICULA_GLOBAL.parquet", 
                             columns=['ANIO_DATA', 'NOMB_INST', 'NOMB_CARRERA', 'MRUN', 'VALOR_ARANCEL'])
    
    df_bec = pd.read_parquet("data/ASIGNACIONES_GLOBAL.parquet",
                             columns=['ANIO_DATA', 'MRUN', 'BENEFICIO_BECA_FSCU'])
    
    # Filtramos por el año base y que tengan beneficio
    cohorte = pd.merge(df_mat[df_mat['ANIO_DATA'] == ANIO_BASE], 
                       df_bec[df_bec['ANIO_DATA'] == ANIO_BASE], 
                       on='MRUN', how='inner')

    print(f"✅ Cohorte identificada: {len(cohorte['MRUN'].unique()):,.0f} seres humanos financiados.")

    # 2. Cargar TODA la base de Titulados (Histórica)
    print("⏳ Cargando la base de sobrevivientes (Titulados)...")
    df_tit = pd.read_parquet("data/TITULADOS_GLOBAL.parquet", columns=['MRUN'])
    
    # Convertimos los MRUN a un Set para una búsqueda ultra rápida (O(1))
    sobrevivientes_set = set(df_tit['MRUN'].unique())

    # 3. El Momento de la Verdad: ¿Quién salió del sistema?
    print("⚔️ Cruzando trayectorias... buscando el pulso de cada MRUN...")
    
    def verificar_supervivencia(mrun):
        return 1 if mrun in sobrevivientes_set else 0

    cohorte['SOBREVIVIENTE'] = cohorte['MRUN'].apply(verificar_supervivencia)

    # 4. Agrupar por Institución para ver el Desempeño Real
    print("📊 Calculando Tasa de Supervivencia Real por Institución...")
    informe_real = cohorte.groupby('NOMB_INST').agg(
        PERSONAS_FINANCIADAS=('MRUN', 'nunique'),
        DINERO_INVERTIDO=('VALOR_ARANCEL', 'sum'),
        TITULADOS_REALES=('SOBREVIVIENTE', 'sum')
    ).reset_index()

    informe_real['TASA_SUPERVIVENCIA'] = (informe_real['TITULADOS_REALES'] / informe_real['PERSONAS_FINANCIADAS']) * 100
    informe_real = informe_real.sort_values(by='DINERO_INVERTIDO', ascending=False)

    # 5. Reporte Final
    print("\n" + "="*80)
    print(f"🕵️ REPORTE DE SUPERVIVENCIA REAL (Cohorte {ANIO_BASE})")
    print("="*80)
    for index, row in informe_real.head(15).iterrows():
        print(f"🏛️ {row['NOMB_INST']}")
        print(f"   ➔ Inversión Estatal ese año: ${row['DINERO_INVERTIDO']/1e6:,.1f} Millones")
        print(f"   ➔ Personas Capturadas: {row['PERSONAS_FINANCIADAS']:,.0f}")
        print(f"   ➔ Sobrevivientes (se titularon de CUALQUIER COSA): {row['TITULADOS_REALES']:,.0f}")
        print(f"   ➔ Tasa de Éxito Humano: {row['TASA_SUPERVIVENCIA']:.1f}%")
        print("-" * 50)

except Exception as e:
    print(f"❌ Error en el trazado: {e}")