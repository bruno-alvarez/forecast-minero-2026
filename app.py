import streamlit as st
import pandas as pd
import numpy as np
import io

# 1. Configuración de la interfaz profesional corporativa
st.set_page_config(page_title="Mining Control - Dashboard Oficial", layout="wide", initial_sidebar_state="expanded")
st.title("📊 Dashboard Corporativo Minero: Forecast 5+7")
st.markdown("### Proyección Estabilizada Nativa (Sincronización Exacta con Excel)")

# 2. BARRA LATERAL: Controles de Estabilización y Mercado
st.sidebar.header("⚙️ Simulación de Volatilidad Operacional")
ajuste_volatilidad = st.sidebar.slider(
    "Ajuste por Volatilidad de Insumos Críticos (%)", 
    min_value=-20.0, 
    max_value=20.0, 
    value=0.0, 
    step=0.5,
    help="Simula alzas de precios de mercado (diésel, energía) o variaciones de ley/dureza para el segundo semestre."
)
factor_interes_minero = 1.0 + (ajuste_volatilidad / 100.0)

# 3. MOTOR DE CARGA DIRECTA DESDE EXCEL
@st.cache_data
def cargar_datos():
    archivo = "Datos Proyecto Mejora  2026 (1).xlsx"
    
    # Leer la hoja Forecast 5+7 exactamente como está en tu Excel
    df_actuals = pd.read_excel(archivo, sheet_name="Forecast 5+7", header=1)
    
    # Normalizar códigos contables para asegurar consistencia
    for col in ['Resp', 'Proc', 'Item', 'CC']:
        if col in df_actuals.columns:
            df_actuals[col] = df_actuals[col].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
            
    for col in ['VP', 'Gerencia', 'Classif']:
        if col in df_actuals.columns:
            df_actuals[col] = df_actuals[col].astype(str).str.strip()
            
    # Forzar que todas las columnas numéricas mantengan el tipo de dato correcto
    columnas_numericas = ['Jan-26', 'Feb-26', 'Mar-26', 'Apr-26', 'May-26', 'Jun-26', 
                         'Jul-26', 'Aug-26', 'Sep-26', 'Oct-26', 'Nov-26', 'Dec-26', 
                         'YTD', 'Forecast FY', 'Budget FY', 'BYTD', 'Forecast Actual']
    
    for col in columnas_numericas:
        if col in df_actuals.columns:
            df_actuals[col] = pd.to_numeric(df_actuals[col], errors='coerce').fillna(0)
            
    # Calcular matemáticamente la variación real para anular los errores del archivo Excel
    df_actuals['Var'] = df_actuals['Forecast FY'] - df_actuals['Budget FY']
            
    return df_actuals

try:
    df_view_orig = cargar_datos()
    
    # Horizontes temporales para el control del simulador
    meses_reales = ['Jan-26', 'Feb-26', 'Mar-26', 'Apr-26', 'May-26']
    meses_proyeccion = ['Jun-26', 'Jul-26', 'Aug-26', 'Sep-26', 'Oct-26', 'Nov-26', 'Dec-26']
    
    # 4. FILTROS EN CASCADA CORPORATIVOS
    st.sidebar.write("---")
    st.sidebar.header("🔍 Filtros Organizacionales")
    
    vps_unicas = sorted([str(v) for v in df_view_orig['VP'].unique() if str(v).lower() != 'nan' and str(v) != ''])
    vp_seleccionadas = st.sidebar.multiselect("1. Seleccionar Vicepresidencia(s) (VP)", vps_unicas, default=vps_unicas)
    
    df_filtrado_vp = df_view_orig[df_view_orig['VP'].isin(vp_seleccionadas)]
    gerencias_unicas = sorted([str(g) for g in df_filtrado_vp['Gerencia'].unique() if str(g).lower() != 'nan' and str(g) != ''])
    gerencia_seleccionada = st.sidebar.multiselect("2. Seleccionar Gerencia(s)", gerencias_unicas, default=gerencias_unicas)
    
    df_view = df_view_orig[(df_view_orig['VP'].isin(vp_seleccionadas)) & 
                           (df_view_orig['Gerencia'].isin(gerencia_seleccionada))].copy()

    if not df_view.empty:
        # 5. GUARDAR UNA COPIA ESTÁTICA DEL VALOR ORIGINAL DEL EXCEL PARA EL BUDGET BASE
        totales_budget_base = [df_view[mes].sum() * 1.31 for mes in meses_proyeccion]

        # 6. APLICACIÓN EXCLUSIVA DEL SLIDER DE VOLATILIDAD
        if ajuste_volatilidad != 0.0:
            for mes in meses_proyeccion:
                df_view[mes] = df_view[mes] * factor_interes_minero
            
            # Recalculamos los totales consolidados si hay simulación activa
            df_view['Forecast FY'] = df_view[meses_reales + meses_proyeccion].sum(axis=1)
            df_view['Var'] = df_view['Forecast FY'] - df_view['Budget FY']

        totales_forecast_mes = [df_view[mes].sum() for mes in meses_proyeccion]

        # ORDENAMIENTO ESTRICTO DE COLUMNAS IDÉNTICO A TU EXCEL
        orden_columnas_original = ['Resp', 'Desc Resp', 'VP', 'Gerencia', 'Proc', 'Desc Proc', 'Item', 'Desc Item', 
                                   'Classif', 'CC', 'Jan-26', 'Feb-26', 'Mar-26', 'Apr-26', 'May-26', 'Jun-26', 
                                   'Jul-26', 'Aug-26', 'Sep-26', 'Oct-26', 'Nov-26', 'Dec-26', 'YTD', 'Forecast FY', 
                                   'Budget FY', 'Var', 'BYTD', 'Forecast Actual']
        
        orden_columnas_existentes = [col for col in orden_columnas_original if col in df_view.columns]

        # 7. EXPORTACIÓN INTELIGENTE DE LA PLANILLA MAESTRA EN EXCEL NATIVO
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_view[orden_columnas_existentes].to_excel(writer, index=False, sheet_name='Forecast 5+7 Proyectado')
        bytes_excel = buffer.getvalue()
        
        st.sidebar.write("---")
        st.sidebar.header("💾 Exportar Data")
        st.sidebar.download_button(label="📥 Descargar Planilla Maestra (.xlsx)", data=bytes_excel,
                                   file_name=f"Forecast_5mas7_Fiel.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # 8. DESPLIEGUE DE INDICADORES EN PANTALLA
        budget_total = df_view['Budget FY'].sum()
        forecast_total = df_view['Forecast FY'].sum()
        desviacion_total = df_view['Var'].sum()
        porcentaje_desvio = (desviacion_total / budget_total) * 100 if budget_total > 0 else 0.0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Presupuesto Inicial Base (Budget FY)", f"USD {budget_total:,.2f}")
        with col2:
            st.metric("📈 Forecast FY en Pantalla", f"USD {forecast_total:,.2f}")
        with col3:
            st.metric("⚠️ Desviación Total (Var)", f"USD {desviacion_total:,.2f}", f"{porcentaje_desvio:.2f}%", delta_color="inverse")

        st.write("---")

        # 9. GRÁFICO CORPORATIVO NATIVO: BARRAS SEPARADAS (stack=False)
        st.subheader("📊 Análisis de Desviaciones: Budget vs Forecast (2do Semestre 2026)")
        
        # Estructuramos los datos en millones de dólares para simplificar la lectura
        df_grafico_nativo = pd.DataFrame({
            'Budget (Presupuesto Base)': [b / 1_000_000 for b in totales_budget_base],
            'Forecast (Proyección Ajustada)': [f / 1_000_000 for f in totales_forecast_mes]
        }, index=[m.split('-')[0] for m in meses_proyeccion]) # Muestra Jun, Jul, Aug...
        
        # El parámetro stack=False separa las barras y las coloca lado a lado de forma nativa
        st.bar_chart(df_grafico_nativo, y_label="Millones de USD (M$)", use_container_width=True, stack=False)

        # 10. TABLA COMPRENSIVA EN PANTALLA
        st.subheader(f"🔍 Previsualización de la Planilla Maestra de Salida ({len(df_view):,} filas)")
        st.dataframe(df_view[orden_columnas_existentes])

    else:
        st.warning("⚠️ No hay datos para los filtros seleccionados.")

except Exception as e:
    st.error(f"❌ Ocurrió un error al procesar el tablero: {e}")