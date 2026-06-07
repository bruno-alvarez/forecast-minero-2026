import streamlit as st
import pandas as pd
import numpy as np

# 1. Configuración de la página
st.set_page_config(page_title="App Minera Pro 2026", layout="wide", initial_sidebar_state="expanded")
st.title("🚀 Dashboard Avanzado: Forecast 5+7 (2026)")
st.markdown("### Modelo de Proyección No Lineal por Naturaleza de Gasto")

# 2. Carga de datos
@st.cache_data
def load_data():
    return pd.read_excel('Datos Proyecto Mejora  2026.xlsx', sheet_name='Forecast 5+7', header=1)

try:
    df = load_data()
    
    # 3. Variables de tiempo
    actual_cols = ['Jan-26', 'Feb-26', 'Mar-26', 'Apr-26', 'May-26']
    forecast_cols = ['Jun-26', 'Jul-26', 'Aug-26', 'Sep-26', 'Oct-26', 'Nov-26', 'Dec-26']
    
    # 4. BARRA LATERAL: Filtros
    st.sidebar.header("🎯 Filtros de Operación")
    todas_vp = df['VP'].dropna().unique().tolist()
    vp_seleccionadas = st.sidebar.multiselect("1. Seleccione VP(s)", todas_vp, default=todas_vp)
    
    gerencias_disp = df[df['VP'].isin(vp_seleccionadas)]['Gerencia'].dropna().unique().tolist()
    gerencia_seleccionada = st.sidebar.multiselect("2. Seleccione Gerencia(s)", gerencias_disp, default=gerencias_disp)
    
    clases_disp = df[(df['VP'].isin(vp_seleccionadas)) & (df['Gerencia'].isin(gerencia_seleccionada))]['Classif'].dropna().unique().tolist()
    clase_seleccionada = st.sidebar.multiselect("3. Naturaleza del Gasto", clases_disp, default=clases_disp)

    # 5. Ajuste No Lineal
    st.sidebar.markdown("---")
    st.sidebar.header("📈 Ajuste No Lineal")
    tasas_crecimiento = {clase: st.sidebar.slider(f"Crecimiento - {clase} (%)", -10.0, 10.0, 0.0, 0.5) for clase in clase_seleccionada}

    # 6. Cálculo del Modelo
    df_filtrado = df[(df['VP'].isin(vp_seleccionadas)) & 
                     (df['Gerencia'].isin(gerencia_seleccionada)) & 
                     (df['Classif'].isin(clase_seleccionada))].copy()

    if not df_filtrado.empty:
        # Lógica de proyección
        df_filtrado['Suma_Actuals_5M'] = df_filtrado[actual_cols].sum(axis=1)
        for clase in clase_seleccionada:
            tasa = tasas_crecimiento[clase] / 100.0
            mask = df_filtrado['Classif'] == clase
            base_gasto = df_filtrado.loc[mask, 'May-26']
            for i, mes in enumerate(forecast_cols, start=1):
                df_filtrado.loc[mask, mes + '_Proyectado'] = base_gasto * ((1 + tasa) ** i)
        
        forecast_proyectados = [m + '_Proyectado' for m in forecast_cols]
        df_filtrado['Nuevo_Forecast_FY'] = df_filtrado['Suma_Actuals_5M'] + df_filtrado[forecast_proyectados].sum(axis=1)
        
        # 7. INTERFAZ: KPIs
        col1, col2, col3 = st.columns(3)
        col1.metric("Presupuesto (FY)", f"${df_filtrado['Budget FY'].sum():,.0f}")
        col2.metric("Proyección (FY)", f"${df_filtrado['Nuevo_Forecast_FY'].sum():,.0f}")
        col3.metric("Varianza", f"${df_filtrado['Budget FY'].sum() - df_filtrado['Nuevo_Forecast_FY'].sum():,.0f}")

        # 8. GRÁFICO 1: Evolución Mensual
        st.subheader("📈 Evolución Mensual del Gasto")
        gasto_mensual = df_filtrado[actual_cols + forecast_proyectados].sum().values
        df_grafico = pd.DataFrame({'Mes': actual_cols + forecast_cols, 'Gasto USD': gasto_mensual})
        st.line_chart(df_grafico.set_index('Mes'))

        # 9. GRÁFICO 2: Consolidado por Naturaleza
        st.markdown("---")
        st.subheader("📊 Proyección Consolidada por Clasificación")
        df_resumen = df_filtrado.groupby('Classif')[['Nuevo_Forecast_FY']].sum().reset_index()
        st.bar_chart(df_resumen.set_index('Classif')[['Nuevo_Forecast_FY']])
        
        st.info("Este modelo calcula el cierre de año aplicando una curva exponencial de crecimiento según tus ajustes.")

    else:
        st.warning("⚠️ No hay datos para los filtros seleccionados.")

except Exception as e:
    st.error(f"Error técnico: {e}")