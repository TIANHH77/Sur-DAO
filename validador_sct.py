import pandas as pd

def calcular_saqueo_trayectoria(semestres_cursados, semestres_reconocidos, valor_arancel_anual):
    """
    Motor Forense de SUR DAO.
    Calcula la Energía Humana secuestrada por topes de convalidación institucionales.
    
    Parámetros:
    - semestres_cursados: Tiempo real sobrevivido en la institución origen.
    - semestres_reconocidos: Tiempo que la nueva malla digna validar (el "castigo").
    - valor_arancel_anual: Costo financiero del año académico.
    """
    
    # 1. Constantes del Sistema (Basado en Guía Práctica SCT-Chile 2007)
    SCT_POR_SEMESTRE = 30
    HORAS_POR_SCT = 27.5
    
    # 2. El Cálculo del Secuestro (La diferencia entre lo vivido y lo validado)
    semestres_robados = semestres_cursados - semestres_reconocidos
    
    if semestres_robados <= 0:
        return {"estado": "Sin anomalías", "horas_robadas": 0, "dinero_robado": 0}

    # 3. Transformación a Energía y Capital
    sct_expropiados = semestres_robados * SCT_POR_SEMESTRE
    horas_vida_robadas = sct_expropiados * HORAS_POR_SCT
    
    anos_robados = semestres_robados / 2
    dinero_secuestrado = anos_robados * valor_arancel_anual
    
    # 4. Cálculo del Porcentaje de Castigo
    porcentaje_perdida = (semestres_robados / semestres_cursados) * 100

    return {
        "SCT_Generados_Total": semestres_cursados * SCT_POR_SEMESTRE,
        "SCT_Expropiados": sct_expropiados,
        "Porcentaje_Castigo_Malla": porcentaje_perdida,
        "Horas_Vida_Secuestradas": horas_vida_robadas,
        "Capital_Secuestrado_CLP": dinero_secuestrado
    }

# --- CASO CERO: LA PRUEBA DE LA GUILLOTINA ---
if __name__ == "__main__":
    # Ejecutamos el escenario real: 
    # Llegar a 3er año (6 semestres) y ser retrocedido a 2do año (4 semestres).
    # Supongamos un arancel de $3.500.000.
    
    print("🌑 EJECUTANDO AUDITORÍA DE CONVALIDACIÓN 🌑")
    print("-" * 50)
    
    auditoria = calcular_saqueo_trayectoria(
        semestres_cursados=6, 
        semestres_reconocidos=4, 
        valor_arancel_anual=3500000
    )
    
    print(f"Créditos SCT totales generados:     {auditoria['SCT_Generados_Total']} SCT")
    print(f"Créditos SCT borrados por la malla: {auditoria['SCT_Expropiados']} SCT")
    print(f"Porcentaje de vida invalidado:      {auditoria['Porcentaje_Castigo_Malla']:.1f}%")
    print(f"Energía vital expropiada:           {auditoria['Horas_Vida_Secuestradas']:,.0f} Horas")
    print(f"Costo del Saqueo Institucional:     ${auditoria['Capital_Secuestrado_CLP']:,.0f} CLP")
    print("-" * 50)
    print("Resolución: Falla multisistémica detectada. Bloqueo normativo activo.")