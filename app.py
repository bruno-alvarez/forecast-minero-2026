import streamlit as st
import pandas as pd
import numpy as np

# 1. Configuración de la página
st.set_page_config(page_title="App Minera Pro 2026", layout="wide", initial_sidebar_state="expanded")
st.title("🚀 Dashboard Avanzado: Forecast 5+7 (2026)")
st.markdown("### Modelo de Proyección No Lineal por Naturaleza de Gasto")

# 2. Carga de datos actualizados
@st.cache_data
def load_data():
    # Agregamos header=1 para que se salte la fila superior de títulos
    df = pd.read_excel('Datos Proyecto Mejora  2026.xlsx', sheet_name='Forecast 5+7', header=1)
    return df

try:
    df = load_data()
    
    # 3. Variables de tiempo (Año 2026)
    actual_cols = ['Jan-26', 'Feb-26', 'Mar-26', 'Apr-26', 'May-26']
    forecast_cols = ['Jun-26', 'Jul-26', 'Aug-26', 'Sep-26', 'Oct-26', 'Nov-26', 'Dec-26']
    
    # 4. BARRA LATERAL: Filtros Operacionales
    st.sidebar.header("🎯 Filtros de Operación")
    
    # Filtro VP
    lista_vp = df['VP'].dropna().unique().tolist()
    vp_seleccionado = st.sidebar.selectbox("1. Seleccione VP", lista_vp)
    
    # Filtro Gerencia
    gerencias_disp = df[df['VP'] == vp_seleccionado]['Gerencia'].dropna().unique().tolist()
    gerencia_seleccionada = st.sidebar.multiselect("2. Seleccione Gerencia(s)", gerencias_disp, default=gerencias_disp)
    
    # Filtro de Clasificación
    clases_disp = df[(df['VP'] == vp_seleccionado) & (df['Gerencia'].isin(gerencia_seleccionada))]['Classif'].dropna().unique().tolist()
    clase_seleccionada = st.sidebar.multiselect("3. Naturaleza del Gasto", clases_disp, default=clases_disp)

    # 5. BARRA LATERAL: Control No Lineal (Requisito de Rúbrica)
    st.sidebar.markdown("---")
    st.sidebar.header("📈 Ajuste No Lineal (Tasa Compuesta)")
    st.sidebar.caption("Ajusta la tasa de crecimiento mensual compuesto (interés compuesto) a partir del último mes real (May-26).")
    
    tasas_crecimiento = {}
    for clase in clase_seleccionada:
        # Permite ajustar el crecimiento/decrecimiento porcentual compuesto mes a mes
        tasas_crecimiento[clase] = st.sidebar.slider(
            f"Crecimiento Mensual - {clase} (%)", 
            min_value=-10.0, max_value=10.0, value=0.0, step=0.5
        )

    # 6. Procesamiento y Cálculo del Modelo No Lineal
    df_filtrado = df[(df['VP'] == vp_seleccionado) & 
                     (df['Gerencia'].isin(gerencia_seleccionada)) & 
                     (df['Classif'].isin(clase_seleccionada))].copy()

    if not df_filtrado.empty:
        # Sumar los 5 meses reales
        df_filtrado['Suma_Actuals_5M'] = df_filtrado[actual_cols].sum(axis=1)
        
        # Iterar sobre las clases seleccionadas para aplicar la curva no lineal
        for clase in clase_seleccionada:
            tasa = tasas_crecimiento[clase] / 100.0
            mask = df_filtrado['Classif'] == clase
            
            # Tomamos el gasto de Mayo 2026 como "Mes 0" para proyectar la curva
            base_gasto = df_filtrado.loc[mask, 'May-26']
            
            # Fórmula exponencial: Valor Futuro = Valor Base * (1 + tasa)^t
            for i, mes in enumerate(forecast_cols, start=1):
                df_filtrado.loc[mask, mes + '_Proyectado'] = base_gasto * ((1 + tasa) ** i)
                
        # Consolidar el nuevo Forecast No Lineal
        forecast_proyectados = [m + '_Proyectado' for m in forecast_cols]
        df_filtrado['Suma_Forecast_7M_NoLineal'] = df_filtrado[forecast_proyectados].sum(axis=1)
        
        # Calcular el Cierre de Año (Actuals + Nuevo Forecast)
        df_filtrado['Nuevo_Forecast_FY'] = df_filtrado['Suma_Actuals_5M'] + df_filtrado['Suma_Forecast_7M_NoLineal']
        
        # 7. INTERFAZ: KPIs
        total_budget = df_filtrado['Budget FY'].sum()
        total_nuevo_forecast = df_filtrado['Nuevo_Forecast_FY'].sum()
        variacion = total_budget - total_nuevo_forecast
        porcentaje_var = (variacion / total_budget) * 100 if total_budget > 0 else 0

        st.subheader("Indicadores de Gestión (Año 2026)")
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Presupuesto (Budget FY)", f"${total_budget:,.0f}")
        kpi2.metric("Proyección No Lineal (FY)", f"${total_nuevo_forecast:,.0f}")
        kpi3.metric("Varianza al Cierre", f"${variacion:,.0f}", f"{porcentaje_var:.1f}%", delta_color="normal")

        # 8. Gráfico de Curva Exponencial
        st.markdown("---")
        st.subheader("📈 Comportamiento del Gasto: Evolución Mensual")
        
        # Preparar la línea de tiempo fusionando meses reales y proyectados
        meses_totales = actual_cols + forecast_proyectados
        nombres_limpios = actual_cols + forecast_cols
        
        # Sumar el gasto por mes para el gráfico
        gasto_mensual = df_filtrado[meses_totales].sum().values
        df_grafico = pd.DataFrame({'Mes': nombres_limpios, 'Gasto USD': gasto_mensual})
        
        st.line_chart(df_grafico.set_index('Mes'))
        
        st.info("💡 **Análisis para Presentación Ejecutiva:** Esta curva representa una **proyección no lineal**. En lugar de asignar un gasto fijo mensual, el modelo toma el gasto consolidado de `May-26` y le aplica una tasa de escalamiento compuesto mensual simulando efectos macroeconómicos (ej. inflación, precio de la energía) o variaciones de invierno operacional.")

    else:
        st.warning("⚠️ No hay datos para los filtros seleccionados.")

except Exception as e:
    st.error(f"Error técnico: {e}. Revisa que el archivo se llame 'Datos Proyecto Mejora  2026.xlsx' y esté cerrado en tu computador.")