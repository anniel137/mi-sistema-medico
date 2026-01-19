import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
DB_FILE = "base_datos_medica_v2.csv"
USUARIO_ADMIN = "admin"
CLAVE_ADMIN = "12345"

# Opciones para el campo Sexo
OPCIONES_SEXO = ["Hombre", "Mujer", "Bisexual", "Prefiero no decirlo"]

def cargar_datos():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            # Verificar si la columna Sexo existe (para compatibilidad con datos viejos)
            if 'Sexo' not in df.columns:
                df['Sexo'] = "No especificado"
            return df
        except:
            pass
    return pd.DataFrame(columns=[
        "Nombre", "Apellido", "Cedula", "Edad", "Sexo", "Grupo_Familiar", 
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
    st.write("### Últimos ingresos")
    st.dataframe(df_reciente.tail(5))

# --- VISTA: NUEVO REGISTRO ---
elif choice == "Nuevo Registro":
    st.subheader("📝 Registro de Paciente")
    with st.form("reg_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        n = col_a.text_input("Nombre")
        a = col_b.text_input("Apellido")
        c = col_a.text_input("Cédula / ID")
        e = col_b.number_input("Edad", 0, 120, step=1)
        
        # Nuevo campo de Sexo
        sexo = st.selectbox("Sexo / Identidad", OPCIONES_SEXO)
        
        st.markdown("**🏠 Ubicación y Familia**")
        gf = st.text_input("Grupo Familiar")
        calle = st.text_input("Calle / Avenida")
        casa = st.text_input("Número de Casa")
        
        st.markdown("**🏥 Datos Médicos**")
        p = st.text_area("Patología")
        m = st.text_area("Medicamentos")
        
        if st.form_submit_button("Guardar Datos"):
            if n and c:
                nueva_fila = pd.DataFrame([{
                    "Nombre": n, "Apellido": a, "Cedula": c, "Edad": e, "Sexo": sexo,
                    "Grupo_Familiar": gf, "Calle": calle, "Nro_Casa": casa,
                    "Patologia": p, "Medicamentos": m, "Fecha_Registro": datetime.now()
                }])
                df = pd.concat([df, nueva_fila], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success(f"✅ {n} ha sido registrado correctamente")
            else:
                st.error("Nombre y Cédula son obligatorios")

# --- VISTA: EDITAR PACIENTE ---
elif choice == "Editar Paciente":
    st.subheader("🔍 Editar Registro Existente")
    
    if df.empty:
        st.warning("No hay datos para editar.")
    else:
        cedulas = df['Cedula'].astype(str).tolist()
        cedula_sel = st.selectbox("Seleccione la Cédula", ["Seleccione..."] + cedulas)
        
        if cedula_sel != "Seleccione...":
            idx = df[df['Cedula'].astype(str) == cedula_sel].index[0]
            p_data = df.iloc[idx]
            
            with st.form("edit_form"):
                st.info(f"Editando registro de: {p_data['Nombre']}")
                col1, col2 = st.columns(2)
                en = col1.text_input("Nombre", value=p_data['Nombre'])
                ea = col2.text_input("Apellido", value=p_data['Apellido'])
                ee = col2.number_input("Edad", 0, 120, value=int(p_data['Edad']))
                
                # Editar Sexo
                # Buscamos el índice del sexo actual para que aparezca seleccionado
                try:
                    index_sexo = OPCIONES_SEXO.index(p_data['Sexo'])
                except:
                    index_sexo = 0
                esexo = st.selectbox("Sexo / Identidad", OPCIONES_SEXO, index=index_sexo)
                
                egf = st.text_input("Grupo Familiar", value=p_data['Grupo_Familiar'])
                ecalle = st.text_input("Calle", value=p_data['Calle'])
                ecasa = st.text_input("Casa", value=p_data['Nro_Casa'])
                ep = st.text_area("Patología", value=p_data['Patologia'])
                em = st.text_area("Medicamentos", value=p_data['Medicamentos'])
                
                if st.form_submit_button("Actualizar"):
                    df.at[idx, 'Nombre'] = en
                    df.at[idx, 'Apellido'] = ea
                    df.at[idx, 'Edad'] = ee
                    df.at[idx, 'Sexo'] = esexo
                    df.at[idx, 'Grupo_Familiar'] = egf
                    df.at[idx, 'Calle'] = ecalle
                    df.at[idx, 'Nro_Casa'] = ecasa
                    df.at[idx, 'Patologia'] = ep
                    df.at[idx, 'Medicamentos'] = em
                    
                    df.to_csv(DB_FILE, index=False)
                    st.success("✅ Datos actualizados")
                    st.rerun()

# --- VISTA: HISTORIAL ---
elif choice == "Historial (3 Meses)":
    st.subheader("📋 Historial de Pacientes")
    hace_3_meses = datetime.now() - timedelta(days=90)
    df_reciente = df[df['Fecha_Registro'] >= hace_3_meses]
    st.dataframe(df_reciente)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Respaldo (CSV)", csv, "base_datos_medica.csv", "text/csv")
