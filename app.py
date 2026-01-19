import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
DB_FILE = "base_datos_medica_v2.csv"
USUARIO_ADMIN = "admin"
CLAVE_ADMIN = "12345"

def cargar_datos():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
        return df
    return pd.DataFrame(columns=[
        "Nombre", "Apellido", "Cedula", "Edad", "Grupo_Familiar", 
        "Calle", "Nro_Casa", "Patologia", "Medicamentos", "Fecha_Registro"
    ])

# --- LÓGICA DE LOGIN ---
if "autenticado" not in st.session_state:
    st.title("🔐 Acceso al Sistema Médico")
    with st.form("login_form"):
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            if user == USUARIO_ADMIN and password == CLAVE_ADMIN:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
    st.stop()

# --- INTERFAZ PRINCIPAL ---
st.set_page_config(page_title="Sistema Médico Pro", page_icon="🩺")

if st.sidebar.button("Cerrar Sesión"):
    del st.session_state["autenticado"]
    st.rerun()

df = cargar_datos()
menu = ["Dashboard", "Nuevo Registro", "Editar Paciente", "Historial (3 Meses)"]
choice = st.sidebar.selectbox("Menú Principal", menu)

# --- VISTA: DASHBOARD ---
if choice == "Dashboard":
    st.title("🩺 Panel de Control")
    hace_3_meses = datetime.now() - timedelta(days=90)
    df_reciente = df[df['Fecha_Registro'] >= hace_3_meses]
    
    col1, col2 = st.columns(2)
    col1.metric("Pacientes Recientes", len(df_reciente))
    col2.metric("Total en Base de Datos", len(df))
    st.dataframe(df_reciente.tail(5)) # Muestra los últimos 5 agregados

# --- VISTA: NUEVO REGISTRO ---
elif choice == "Nuevo Registro":
    st.subheader("📝 Registro de Paciente")
    with st.form("reg_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        n = col_a.text_input("Nombre")
        a = col_b.text_input("Apellido")
        c = col_a.text_input("Cédula / ID")
        e = col_b.number_input("Edad", 0, 120)
        gf = st.text_input("Grupo Familiar")
        calle = st.text_input("Calle / Avenida")
        casa = st.text_input("Número de Casa")
        p = st.text_area("Patología")
        m = st.text_area("Medicamentos")
        
        if st.form_submit_button("Guardar Datos"):
            if n and c:
                nueva_fila = pd.DataFrame([{
                    "Nombre": n, "Apellido": a, "Cedula": c, "Edad": e,
                    "Grupo_Familiar": gf, "Calle": calle, "Nro_Casa": casa,
                    "Patologia": p, "Medicamentos": m, "Fecha_Registro": datetime.now()
                }])
                df = pd.concat([df, nueva_fila], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("✅ Paciente registrado con éxito")
            else:
                st.error("Nombre y Cédula son obligatorios")

# --- VISTA: EDITAR PACIENTE ---
elif choice == "Editar Paciente":
    st.subheader("🔍 Buscar y Editar Registro")
    
    if df.empty:
        st.warning("No hay pacientes registrados para editar.")
    else:
        # Buscador por Cédula
        cedulas = df['Cedula'].astype(str).tolist()
        cedula_sel = st.selectbox("Seleccione la Cédula del paciente a editar", ["Seleccione..."] + cedulas)
        
        if cedula_sel != "Seleccione...":
            # Obtener datos actuales del paciente
            paciente_idx = df[df['Cedula'].astype(str) == cedula_sel].index[0]
            p_data = df.iloc[paciente_idx]
            
            with st.form("edit_form"):
                st.info(f"Editando a: {p_data['Nombre']} {p_data['Apellido']}")
                col_a, col_b = st.columns(2)
                nuevo_n = col_a.text_input("Nombre", value=p_data['Nombre'])
                nuevo_a = col_b.text_input("Apellido", value=p_data['Apellido'])
                nuevo_e = col_b.number_input("Edad", 0, 120, value=int(p_data['Edad']))
                
                nuevo_gf = st.text_input("Grupo Familiar", value=p_data['Grupo_Familiar'])
                nuevo_calle = st.text_input("Calle", value=p_data['Calle'])
                nuevo_casa = st.text_input("Número de Casa", value=p_data['Nro_Casa'])
                
                nuevo_p = st.text_area("Patología", value=p_data['Patologia'])
                nuevo_m = st.text_area("Medicamentos", value=p_data['Medicamentos'])
                
                if st.form_submit_button("Actualizar Cambios"):
                    # Actualizar el DataFrame
                    df.at[paciente_idx, 'Nombre'] = nuevo_n
                    df.at[paciente_idx, 'Apellido'] = nuevo_a
                    df.at[paciente_idx, 'Edad'] = nuevo_e
                    df.at[paciente_idx, 'Grupo_Familiar'] = nuevo_gf
                    df.at[paciente_idx, 'Calle'] = nuevo_calle
                    df.at[paciente_idx, 'Nro_Casa'] = nuevo_casa
                    df.at[paciente_idx, 'Patologia'] = nuevo_p
                    df.at[paciente_idx, 'Medicamentos'] = nuevo_m
                    
                    df.to_csv(DB_FILE, index=False)
                    st.success("✨ ¡Datos actualizados correctamente!")
                    st.rerun()

# --- VISTA: HISTORIAL ---
elif choice == "Historial (3 Meses)":
    st.subheader("📋 Base de Datos Completa")
    hace_3_meses = datetime.now() - timedelta(days=90)
    df_reciente = df[df['Fecha_Registro'] >= hace_3_meses]
    st.dataframe(df_reciente)
    
    # Botón de Descarga
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Base de Datos para Respaldo", csv, "respaldo_medico.csv", "text/csv")
