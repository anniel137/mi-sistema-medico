import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px

# --- CONFIGURACIÓN ---
DB_FILE = "base_datos_medica_v2.csv"
USUARIO_ADMIN = "admin"
CLAVE_ADMIN = "12345"
OPCIONES_SEXO = ["Hombre", "Mujer", "Bisexual", "Prefiero no decirlo"]

def cargar_datos():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            # Asegurar que todas las columnas existan
            columnas_necesarias = ["Nombre", "Apellido", "Cedula", "Edad", "Sexo", "Grupo_Familiar", "Calle", "Nro_Casa", "Patologia", "Medicamentos", "Fecha_Registro"]
            for col in columnas_necesarias:
                if col not in df.columns:
                    df[col] = "No especificado"
            return df
        except:
            pass
    return pd.DataFrame(columns=["Nombre", "Apellido", "Cedula", "Edad", "Sexo", "Grupo_Familiar", "Calle", "Nro_Casa", "Patologia", "Medicamentos", "Fecha_Registro"])

# --- LOGIN ---
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

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Médico Pro Cloud", page_icon="🩺", layout="wide")

if st.sidebar.button("Cerrar Sesión"):
    del st.session_state["autenticado"]
    st.rerun()

df = cargar_datos()
menu = ["Dashboard", "Nuevo Registro", "Editar Paciente", "Historial Completo"]
choice = st.sidebar.selectbox("Menú Principal", menu)

# --- DASHBOARD CON HISTOGRAMA ---
if choice == "Dashboard":
    st.title("🩺 Dashboard e Indicadores")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Pacientes", len(df))
    m2.metric("Promedio Edad", f"{round(df['Edad'].mean(), 1)} años" if not df.empty else "0")
    m3.metric("Última actualización", datetime.now().strftime("%d/%m/%Y"))

    st.markdown("---")

    if not df.empty:
        col_izq, col_der = st.columns(2)
        
        with col_izq:
            st.subheader("📊 Distribución de Género")
            fig_pie = px.pie(df, names='Sexo', hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_der:
            st.subheader("📈 Histograma de Patologías")
            # Limpieza rápida para el histograma
            df['Patologia_F'] = df['Patologia'].str.strip().str.capitalize()
            fig_hist = px.histogram(df, x="Patologia_F", color="Patologia_F", 
                                   labels={'Patologia_F':'Patología', 'count':'Número de Pacientes'},
                                   template="plotly_white")
            fig_hist.update_layout(showlegend=False)
            st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No hay datos suficientes para mostrar gráficas.")

# --- NUEVO REGISTRO ---
elif choice == "Nuevo Registro":
    st.subheader("📝 Registro de Paciente")
    with st.form("reg_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        n = c1.text_input("Nombre")
        a = c2.text_input("Apellido")
        ced = c1.text_input("Cédula / ID")
        ed = c2.number_input("Edad", 0, 120, step=1)
        sx = st.selectbox("Sexo", OPCIONES_SEXO)
        
        st.markdown("**🏠 Ubicación**")
        gf = st.text_input("Grupo Familiar")
        calle = st.text_input("Calle/Av")
        casa = st.text_input("Nro Casa")
        
        st.markdown("**🏥 Médico**")
        pat = st.text_area("Patología")
        med = st.text_area("Medicamentos")
        
        if st.form_submit_button("Guardar Registro"):
            if n and ced:
                nueva = pd.DataFrame([{"Nombre":n, "Apellido":a, "Cedula":ced, "Edad":ed, "Sexo":sx, 
                                       "Grupo_Familiar":gf, "Calle":calle, "Nro_Casa":casa, 
                                       "Patologia":pat, "Medicamentos":med, "Fecha_Registro":datetime.now()}])
                df = pd.concat([df, nueva], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("✅ Paciente guardado")
                st.rerun()
            else:
                st.error("Nombre y Cédula son obligatorios")

# --- EDITAR PACIENTE (TODOS LOS CAMPOS) ---
elif choice == "Editar Paciente":
    st.subheader("🔍 Modificar Datos de Paciente")
    if not df.empty:
        # Buscador por cédula para seleccionar al paciente
        lista_pacientes = [f"{row['Cedula']} - {row['Nombre']} {row['Apellido']}" for index, row in df.iterrows()]
        seleccion = st.selectbox("Seleccione el paciente a editar", ["Seleccione..."] + lista_pacientes)
        
        if seleccion != "Seleccione...":
            cedula_actual = seleccion.split(" - ")[0]
            idx = df[df['Cedula'].astype(str) == cedula_actual].index[0]
            
            with st.form("form_edicion"):
                st.warning(f"Está editando los datos de: {df.at[idx, 'Nombre']}")
                
                col1, col2 = st.columns(2)
                # Ahora todos los campos son editables
                edit_n = col1.text_input("Nombre", value=df.at[idx, 'Nombre'])
                edit_a = col2.text_input("Apellido", value=df.at[idx, 'Apellido'])
                edit_ced = col1.text_input("Cédula / ID", value=str(df.at[idx, 'Cedula']))
                edit_ed = col2.number_input("Edad", 0, 120, value=int(df.at[idx, 'Edad']))
                
                current_sex = df.at[idx, 'Sexo']
                edit_sx = st.selectbox("Sexo", OPCIONES_SEXO, index=OPCIONES_SEXO.index(current_sex) if current_sex in OPCIONES_SEXO else 0)
                
                edit_gf = st.text_input("Grupo Familiar", value=df.at[idx, 'Grupo_Familiar'])
                edit_calle = st.text_input("Calle", value=df.at[idx, 'Calle'])
                edit_casa = st.text_input("Nro Casa", value=df.at[idx, 'Nro_Casa'])
                
                edit_pat = st.text_area("Patología", value=df.at[idx, 'Patologia'])
                edit_med = st.text_area("Medicamentos", value=df.at[idx, 'Medicamentos'])
                
                if st.form_submit_button("Guardar Cambios"):
                    df.at[idx, 'Nombre'] = edit_n
                    df.at[idx, 'Apellido'] = edit_a
                    df.at[idx, 'Cedula'] = edit_ced
                    df.at[idx, 'Edad'] = edit_ed
                    df.at[idx, 'Sexo'] = edit_sx
                    df.at[idx, 'Grupo_Familiar'] = edit_gf
                    df.at[idx, 'Calle'] = edit_calle
                    df.at[idx, 'Nro_Casa'] = edit_casa
                    df.at[idx, 'Patologia'] = edit_pat
                    df.at[idx, 'Medicamentos'] = edit_med
                    
                    df.to_csv(DB_FILE, index=False)
                    st.success("✨ ¡Datos actualizados correctamente!")
                    st.rerun()
    else:
        st.info("No hay pacientes registrados.")

# --- HISTORIAL ---
elif choice == "Historial Completo":
    st.subheader("📋 Base de Datos de Pacientes")
    # Buscador rápido
    busqueda = st.text_input("🔍 Buscar por Nombre o Cédula")
    if busqueda:
        df_mostrar = df[df['Nombre'].str.contains(busqueda, case=False) | df['Cedula'].astype(str).contains(busqueda)]
    else:
        df_mostrar = df
    
    st.dataframe(df_mostrar)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Excel (CSV)", csv, "base_datos_medica.csv", "text/csv")
