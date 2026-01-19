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
            if 'Sexo' not in df.columns:
                df['Sexo'] = "No especificado"
            return df
        except:
            pass
    return pd.DataFrame(columns=[
        "Nombre", "Apellido", "Cedula", "Edad", "Sexo", "Grupo_Familiar", 
        "Calle", "Nro_Casa", "Patologia", "Medicamentos", "Fecha_Registro"
    ])

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

# --- APP ---
st.set_page_config(page_title="Médico Pro Cloud", page_icon="🩺", layout="wide")

if st.sidebar.button("Cerrar Sesión"):
    del st.session_state["autenticado"]
    st.rerun()

df = cargar_datos()
menu = ["Dashboard", "Nuevo Registro", "Editar Paciente", "Historial"]
choice = st.sidebar.selectbox("Menú Principal", menu)

if choice == "Dashboard":
    st.title("🩺 Panel de Indicadores Médicos")
    hace_3_meses = datetime.now() - timedelta(days=90)
    df_reciente = df[df['Fecha_Registro'] >= hace_3_meses]
    
    # Métricas superiores
    m1, m2, m3 = st.columns(3)
    m1.metric("Pacientes (90 días)", len(df_reciente))
    m2.metric("Total Histórico", len(df))
    m3.metric("Promedio de Edad", f"{round(df['Edad'].mean(), 1)} años" if not df.empty else "0")

    st.markdown("---")
    
    if not df.empty:
        col_izq, col_der = st.columns(2)
        
        with col_izq:
            st.subheader("📊 Distribución por Género")
            conteo_sexo = df['Sexo'].value_counts().reset_index()
            conteo_sexo.columns = ['Sexo', 'Cantidad']
            fig_pie = px.pie(conteo_sexo, values='Cantidad', names='Sexo', 
                             hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_der:
            st.subheader("🦠 Patologías más Comunes")
            # Limpiamos los textos de patología (quitar espacios y poner mayúscula inicial)
            df['Patologia_Clean'] = df['Patologia'].str.strip().str.capitalize()
            conteo_pat = df['Patologia_Clean'].value_counts().nlargest(10).reset_index()
            conteo_pat.columns = ['Enfermedad', 'Casos']
            
            fig_bar = px.bar(conteo_pat, x='Casos', y='Enfermedad', orientation='h',
                             color='Casos', color_continuous_scale='Reds')
            st.plotly_chart(fig_bar, use_container_width=True)
            
        st.markdown("---")
        st.write("### Últimos Pacientes Registrados")
        st.table(df[['Nombre', 'Apellido', 'Cedula', 'Patologia']].tail(5))
    else:
        st.info("No hay datos para generar estadísticas aún.")

# (El resto del código de Registro, Editar e Historial se mantiene igual que antes)
elif choice == "Nuevo Registro":
    st.subheader("📝 Nuevo Registro")
    with st.form("reg_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        n = c1.text_input("Nombre")
        a = c2.text_input("Apellido")
        ced = c1.text_input("Cédula")
        ed = c2.number_input("Edad", 0, 120, step=1)
        sx = st.selectbox("Sexo", OPCIONES_SEXO)
        pat = st.text_area("Patología")
        med = st.text_area("Medicamentos")
        if st.form_submit_button("Guardar"):
            if n and ced:
                nueva = pd.DataFrame([{"Nombre":n,"Apellido":a,"Cedula":ced,"Edad":ed,"Sexo":sx,"Patologia":pat,"Medicamentos":med,"Fecha_Registro":datetime.now()}])
                df = pd.concat([df, nueva], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("Guardado")
                st.rerun()

elif choice == "Editar Paciente":
    st.subheader("🔍 Editar")
    if not df.empty:
        sel = st.selectbox("Paciente", ["Seleccione..."] + df['Cedula'].astype(str).tolist())
        if sel != "Seleccione...":
            idx = df[df['Cedula'].astype(str) == sel].index[0]
            with st.form("ed"):
                en = st.text_input("Nombre", value=df.at[idx, 'Nombre'])
                ep = st.text_area("Patología", value=df.at[idx, 'Patologia'])
                if st.form_submit_button("Actualizar"):
                    df.at[idx, 'Nombre'] = en
                    df.at[idx, 'Patologia'] = ep
                    df.to_csv(DB_FILE, index=False)
                    st.success("Actualizado")
                    st.rerun()

elif choice == "Historial":
    st.subheader("📋 Datos")
    st.dataframe(df)
    st.download_button("Descargar CSV", df.to_csv(index=False), "datos.csv")
    
    
