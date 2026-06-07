import streamlit as st
import pandas as pd
import numpy as np

# 1. Configuración de la página
st.set_page_config(page_title="App Minera Pro 2026", layout="wide", initial_sidebar_state="expanded")
st.title("🚀 Dashboard Avanzado: Forecast 5+7 (2026)")

# 2. Carga de datos
@st.cache_data
def load_data():
    return pd.read_excel('Datos Proyecto Mejora  2026.xlsx', sheet_name='Forecast 5+7', header=1)

try:
    df = load_data()
    
    # 3. Variables de tiempo
    actual_cols = ['Jan-26', 'Feb-26', 'Mar-26', 'Apr-26', 'May-26']
    forecast_cols = ['Jun-26', 'Jul-26', 'Aug-26', 'Sep-26', 'Oct-26', 'Nov-26', 'Dec-26']
    
    # 4. BARRA LATERAL: Filtros (MODIFICADO PARA SELECCIÓN MÚLTIPLE)
    st.sidebar.header("🎯 Filtros de Operación")
    
    # Filtro VP (Ahora es multiselect)
    todas_vp = df['VP'].dropna().unique().tolist()
    vp_seleccionadas = st.sidebar.multiselect("1. Seleccione VP(s)", todas_vp, default=todas_vp)
    
    # Filtro Gerencia (Se filtra basándose en las VPs seleccionadas)
    gerencias_disp = df[df['VP'].isin(vp_seleccionadas)]['Gerencia'].dropna().unique().tolist()
    gerencia_seleccionada = st.sidebar.multiselect("2. Seleccione Gerencia(s)", gerencias_disp, default=gerencias_disp)
    
    # Filtro de Clasificación
    clases_disp = df[(df['VP'].isin(vp_seleccionadas)) & (df['Gerencia'].isin(gerencia_seleccionada))]['Classif'].dropna().unique().tolist()
    clase_seleccionada = st.sidebar.multiselect("3. Naturaleza del Gasto", clases_disp, default=clases_disp)

    # 5. Ajuste No Lineal
    st.sidebar.markdown("---")
    tasas_crecimiento = {clase: st.sidebar.slider(f"Crecimiento - {clase} (%)", -10.0, 10.0, 0.0, 0.5) for clase in clase_seleccionada}

    # 6. Procesamiento
    df_filtrado = df[(df['VP'].isin(vp_seleccionadas)) & 
                     (df['Gerencia'].isin(gerencia_seleccionada)) & 
                     (df['Classif'].isin(clase_seleccionada))].copy()

    if not df_filtrado.empty:
        # Lógica de cálculo (idéntica a la tuya)
        df_filtrado['Suma_Actuals_5M'] = df_filtrado[actual_cols].sum(axis=1)
        for clase in clase_seleccionada:
            tasa = tasas_crecimiento[clase] / 100.0
            mask = df_filtrado['Classif'] == clase
            base_gasto = df_filtrado.loc[mask, 'May-26']
            for i, mes in enumerate(forecast_cols, start=1):
                df_filtrado.loc[mask, mes + '_Proyectado'] = base_gasto * ((1 + tasa) ** i)
        
        forecast_proyectados = [m + '_Proyectado' for m in forecast_cols]
        df_filtrado['Nuevo_Forecast_FY'] = df_filtrado['Suma_Actuals_5M'] + df_filtrado[forecast_proyectados].sum(axis=1)
        
        # 7. KPIs
        total_budget = df_filtrado['Budget FY'].sum()
        total_proyectado = df_filtrado['Nuevo_Forecast_FY'].sum()
        
        st.subheader("Indicadores de Gestión")
        col1, col2, col3 = st.columns(3)
        col1.metric("Presupuesto (FY)", f"${total_budget:,.0f}")
        col2.metric("Proyección (FY)", f"${total_proyectado:,.0f}")
        col3.metric("Varianza", f"${total_budget - total_proyectado:,.0f}")

        # Gráfico Consolidado Final
        st.markdown("---")
        st.header("📊 Proyección Total de Gastos")
        df_resumen = df_filtrado.groupby('Classif')[['Nuevo_Forecast_FY']].sum().reset_index()
        st.bar_chart(df_resumen.set_index('Classif')[['Nuevo_Forecast_FY']])

    else:
        st.warning("⚠️ No hay datos para los filtros seleccionados.")

except Exception as e:
    st.error(f"Error técnico: {e}")