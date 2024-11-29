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
    
    st.subheader("DataFrame Movimientos Nómina")
    st.dataframe(df_e1_nomina)
    
    st.subheader("DataFrame Matricial Nómina")
    st.dataframe(df_e2_nomina)

    # Cruce de e1-nomina y e2-nomina
    st.subheader("Cruce de Movimientos Nómina y Matricial Nómina")
    df_e1_nomina_cruzado = df_e1_nomina.merge(
        df_e2_nomina[['Empleado', 'Codigo CCosto']],
        on='Empleado',
        how='left'
    )
    
    # Operación para agregar 'Salario'
    st.subheader("Creación de columna 'Salario'")
    if 'Nombre Concepto' in df_e1_nomina_cruzado.columns and 'Valor Total' in df_e1_nomina_cruzado.columns:
        df_e1_nomina_cruzado['Valor Total'] = pd.to_numeric(df_e1_nomina_cruzado['Valor Total'], errors='coerce').fillna(0)
        df_e1_nomina_cruzado['Nombre Concepto'] = df_e1_nomina_cruzado['Nombre Concepto'].astype(str).str.strip()
        df_e1_nomina_cruzado['Salario'] = df_e1_nomina_cruzado['Valor Total']
        df_e1_nomina_cruzado.loc[
            df_e1_nomina_cruzado['Nombre Concepto'].str.startswith('DED -'),
            'Salario'
        ] *= -1

        # Agrupación
        st.subheader("Agrupación por 'Empleado', 'Fecha', y 'Codigo CCosto'")
        if {'Empleado', 'Fecha', 'Nombre', 'Codigo CCosto'}.issubset(df_e1_nomina_cruzado.columns):
            df_agrupado = df_e1_nomina_cruzado.groupby(['Empleado', 'Fecha', 'Codigo CCosto'], as_index=False).agg({
                'Salario': 'sum',
                'Nombre': 'first'
            })

            st.write("DataFrame agrupado por 'Empleado', 'Fecha', 'Codigo CCosto', incluyendo 'Nombre':")
            st.dataframe(df_agrupado)

            # Lógica del cruce con contabilidad
            st.subheader("Cruce entre el acumulado y contabilidad")
            df_contabilidad['Nit'] = df_contabilidad['Nit'].astype(str)
            df_agrupado['Empleado'] = df_agrupado['Empleado'].astype(str).str.replace('.0', '', regex=False)
            df_contabilidad['Fecha'] = pd.to_datetime(df_contabilidad['Fecha'], errors='coerce')
            df_agrupado['Fecha'] = pd.to_datetime(df_agrupado['Fecha'], errors='coerce')

            # Priorizar el cruce por débito primero
            df_contabilidad['Usado'] = False
            cruces = []

            for _, row in df_agrupado.iterrows():
                empleado, fecha, salario = row['Empleado'], row['Fecha'], row['Salario']
                cond_debito = (df_contabilidad['Nit'] == empleado) & (df_contabilidad['Fecha'] == fecha) & \
                              (df_contabilidad['Valor Debito'] == salario) & (~df_contabilidad['Usado'])
                cond_credito = (df_contabilidad['Nit'] == empleado) & (df_contabilidad['Fecha'] == fecha) & \
                               (df_contabilidad['Valor Credito'] == salario) & (~df_contabilidad['Usado'])

                if cond_debito.any():
                    idx = df_contabilidad[cond_debito].index[0]
                    cruces.append({**row.to_dict(), 'Tipo': 'Debito', 'Valor': salario})
                    df_contabilidad.at[idx, 'Usado'] = True
                elif cond_credito.any():
                    idx = df_contabilidad[cond_credito].index[0]
                    cruces.append({**row.to_dict(), 'Tipo': 'Credito', 'Valor': salario})
                    df_contabilidad.at[idx, 'Usado'] = True

            # Convertir los cruces en DataFrame
            df_cruces = pd.DataFrame(cruces)

            # Identificar no cruzados
            df_no_cruzados = df_agrupado[~df_agrupado['Empleado'].isin(df_cruces['Empleado'])]

            # Mostrar resultados
            st.subheader("Registros que cruzaron correctamente")
            st.write(f"Total: {len(df_cruces)}")
            st.dataframe(df_cruces)

            st.subheader("Registros que no cruzaron")
            st.write(f"Total: {len(df_no_cruzados)}")
            st.dataframe(df_no_cruzados)

            st.subheader("Registros usados en contabilidad")
            df_contabilidad_usados = df_contabilidad[df_contabilidad['Usado']]
            st.write(f"Total: {len(df_contabilidad_usados)}")
            st.dataframe(df_contabilidad_usados)

            st.subheader("Registros no usados en contabilidad")
            df_contabilidad_no_usados = df_contabilidad[~df_contabilidad['Usado']]
            st.write(f"Total: {len(df_contabilidad_no_usados)}")
            st.dataframe(df_contabilidad_no_usados)
    
