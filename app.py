import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(page_title="Sistema Médico Cloud", page_icon="??", layout="centered")

# Nombre del archivo donde se guardan los datos en la nube
DB_FILE = "datos_medicos.csv"

# Función para cargar la base de datos
def cargar_datos():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
        return df
    return pd.DataFrame(columns=["Nombre", "Apellido", "Cedula", "Edad", "Patologia", "Medicamentos", "Fecha_Registro"])

# --- INTERFAZ PRINCIPAL ---
st.title("?? Gestión Médica Multiplataforma")
st.sidebar.header("Menú de Navegación")
opcion = st.sidebar.selectbox("Seleccione una opción", ["Dashboard", "Registrar Paciente", "Consultar Historial"])

df = cargar_datos()

# Lógica de tiempo: Calculamos la fecha de hace 3 meses
hace_3_meses = datetime.now() - timedelta(days=90)
# Filtramos los datos para mostrar solo lo reciente por defecto
df_reciente = df[df['Fecha_Registro'] >= hace_3_meses]

if opcion == "Dashboard":
    st.subheader("Resumen de Actividad")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Pacientes (Últimos 3 meses)", len(df_reciente))
    with col2:
        st.metric("Total Histórico", len(df))
    
    st.write("### Calendario de Referencia")
    st.date_input("Hoy es:", datetime.now())

elif opcion == "Registrar Paciente":
    st.subheader("Nuevo Registro")
    with st.form("form_registro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre")
        apellido = c2.text_input("Apellido")
        cedula = c1.text_input("Cédula / ID")
        edad = c2.number_input("Edad", 0, 120, step=1)
        
        patologia = st.text_area("Patología / Diagnóstico")
        medicamentos = st.text_area("Tratamiento / Medicamentos")
        
        enviar = st.form_submit_button("Guardar en la Nube")
        
        if enviar:
            if nombre and cedula:
                nuevo = pd.DataFrame([{
                    "Nombre": nombre, "Apellido": apellido, "Cedula": cedula,
                    "Edad": edad, "Patologia": patologia, "Medicamentos": medicamentos,
                    "Fecha_Registro": datetime.now()
                }])
                df = pd.concat([df, nuevo], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success(f"? Paciente {nombre} guardado exitosamente.")
                st.balloons()
            else:
                st.error("Error: El nombre y la cédula son obligatorios.")

elif opcion == "Consultar Historial":
    st.subheader("Registros Médicos (Últimos 3 Meses)")
    
    if df_reciente.empty:
        st.warning("No hay registros en los últimos 90 días.")
    else:
        # Mostrar tabla sin la columna de fecha interna para limpieza visual
        st.dataframe(df_reciente.drop(columns=["Fecha_Registro"]))
        
        # Botón para descargar el Excel (CSV)
        csv = df_reciente.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="?? Descargar Reporte en Excel (CSV)",
            data=csv,
            file_name=f"reporte_medico_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )