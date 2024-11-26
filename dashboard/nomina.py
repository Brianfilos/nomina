import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Gestión de Nómina y Contabilidad")

# Subtítulo
st.subheader("Carga de Archivos y Cruce de Datos")

# Cargar los archivos
uploaded_e_contabilidad = st.file_uploader("Sube el archivo Movimientos Contables.xlsx", type=["xlsx"])
uploaded_e1_nomina = st.file_uploader("Sube el archivo Movimientos Nomina.xlsx", type=["xlsx"])
uploaded_e2_nomina = st.file_uploader("Sube el archivo Matricial Nomina.xlsx", type=["xlsx"])

if uploaded_e_contabilidad and uploaded_e1_nomina and uploaded_e2_nomina:
    # Leer los archivos
    df_contabilidad = pd.read_excel(uploaded_e_contabilidad)
    df_e1_nomina = pd.read_excel(uploaded_e1_nomina)
    df_e2_nomina = pd.read_excel(uploaded_e2_nomina)
    
    # Limpiar los nombres de las columnas eliminando espacios
    df_contabilidad.columns = df_contabilidad.columns.str.strip()
    df_e1_nomina.columns = df_e1_nomina.columns.str.strip()
    df_e2_nomina.columns = df_e2_nomina.columns.str.strip()
    
    # Mostrar los DataFrames
    st.subheader("DataFrame Movimientos Contables")
    st.dataframe(df_contabilidad)
    
    st.subheader("DataFrame Movimientos Nomina")
    st.dataframe(df_e1_nomina)
    
    st.subheader("DataFrame Matricial Nomina")
    st.dataframe(df_e2_nomina)

    # Cruce de e1-nomina y e2-nomina
    st.subheader("Cruce de Movimientos Nomina y Matricial Nomina")
    # Agregar la columna 'Codigo CCosto' de e2-nomina a e1-nomina usando la columna 'Empleado'
    df_e1_nomina_cruzado = df_e1_nomina.merge(
        df_e2_nomina[['Empleado', 'Codigo CCosto']],
        on='Empleado',
        how='left'
    )
    
    # Operación para agregar 'Salario'
    st.subheader("Creación de columna 'Salario'")
    if 'Nombre Concepto' in df_e1_nomina_cruzado.columns and 'Valor Total' in df_e1_nomina_cruzado.columns:
        # Convertir 'Valor Total' a numérico
        df_e1_nomina_cruzado['Valor Total'] = pd.to_numeric(df_e1_nomina_cruzado['Valor Total'], errors='coerce').fillna(0)

        # Limpiar espacios adicionales en la columna 'Nombre Concepto'
        df_e1_nomina_cruzado['Nombre Concepto'] = df_e1_nomina_cruzado['Nombre Concepto'].astype(str).str.strip()

        # Crear una nueva columna con el signo ajustado según el prefijo
        df_e1_nomina_cruzado['Salario'] = df_e1_nomina_cruzado['Valor Total']
        df_e1_nomina_cruzado.loc[
            df_e1_nomina_cruzado['Nombre Concepto'].str.startswith('DED -'),
            'Salario'
        ] *= -1

        # Agrupar por 'Empleado', 'Fecha', y 'Codigo CCosto', sumando los valores y tomando el primer 'Nombre'
        st.subheader("Agrupación por 'Empleado', 'Fecha', y 'Codigo CCosto'")
        if {'Empleado', 'Fecha', 'Nombre', 'Codigo CCosto'}.issubset(df_e1_nomina_cruzado.columns):
            df_agrupado = df_e1_nomina_cruzado.groupby(['Empleado', 'Fecha', 'Codigo CCosto'], as_index=False).agg({
                'Salario': 'sum',
                'Nombre': 'first'  # Toma el primer valor de 'Nombre' en cada grupo
            })

            st.write("DataFrame agrupado por 'Empleado', 'Fecha', 'Codigo CCosto', incluyendo 'Nombre':")
            st.dataframe(df_agrupado)

