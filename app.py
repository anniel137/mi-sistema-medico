import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(page_title="Sistema Médico Cloud", page_icon="🩺", layout="centered")

# Nombre del archivo de datos
DB_FILE = "datos_medicos.csv"

# Función para cargar datos con manejo de errores de codificación
def cargar_datos():
    if os.path.exists(DB_FILE):
        try:
            # Intentamos cargar con UTF-8, si falla probamos con latin-1
            df = pd.read_csv(DB_FILE, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(DB_FILE, encoding='latin-1')
        
        df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
        return df
    return pd.DataFrame(columns=["Nombre", "Apellido", "Cedula", "Edad", "Patologia", "Medicamentos", "Fecha_Registro"])

# --- INTERFAZ ---
st.title("🩺 Gestión Médica Multiplataforma")
st.sidebar.header("Menú")
opcion = st.sidebar.selectbox("Seleccione", ["Dashboard", "Registrar Paciente", "Historial"])

df = cargar_datos()
hace_3_meses = datetime.now() - timedelta(days=90)
df_reciente = df[df['Fecha_Registro'] >= hace_3_meses]

if opcion == "Dashboard":
    st.subheader("Resumen")
    c1, c2 = st.columns(2)
    c1.metric("Pacientes (90 días)", len(df_reciente))
    c2.metric("Total Histórico", len(df))
    st.date_input("Fecha actual", datetime.now())

elif opcion == "Registrar Paciente":
    st.subheader("Nuevo Registro")
    with st.form("form_reg", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre")
        apellido = col2.text_input("Apellido")
        cedula = col1.text_input("Cédula / ID")
        edad = col2.number_input("Edad", 0, 120, step=1)
        patologia = st.text_area("Patología")
        medicamentos = st.text_area("Medicamentos")
        
        if st.form_submit_button("Guardar Datos"):
            if nombre and cedula:
                nuevo = pd.DataFrame([{
                    "Nombre": nombre, "Apellido": apellido, "Cedula": cedula,
                    "Edad": edad, "Patologia": patologia, "Medicamentos": medicamentos,
                    "Fecha_Registro": datetime.now()
                }])
                df = pd.concat([df, nuevo], ignore_index=True)
                # Guardamos forzando UTF-8 para evitar futuros errores
                df.to_csv(DB_FILE, index=False, encoding='utf-8')
                st.success("✅ Guardado con éxito")
                st.balloons()
            else:
                st.error("Nombre y Cédula son obligatorios")

elif opcion == "Historial":
    st.subheader("Registros (Últimos 3 Meses)")
    if df_reciente.empty:
        st.info("No hay registros recientes.")
    else:
        st.dataframe(df_reciente.drop(columns=["Fecha_Registro"]))
        csv = df_reciente.to_csv(index=False, encoding='utf-8').encode('utf-8')
        st.download_button("📥 Descargar CSV", csv, "reporte.csv", "text/csv")
