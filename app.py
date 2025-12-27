import streamlit as st
import numpy as np
import pandas as pd
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Calculadora dB - CS Sistemas de Aire",
    page_icon="🔊",
    layout="centered"
)

# --- GESTIÓN DE ESTADO (SESSION STATE) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'login_failed' not in st.session_state:
    st.session_state.login_failed = False

# Definimos la contraseña de acceso
PASSWORD_CORRECTA = "CS2026" 

# --- FUNCIONES ---

def verificar_login():
    """Verifica la contraseña ingresada."""
    input_pass = st.session_state.input_password
    if input_pass == PASSWORD_CORRECTA:
        st.session_state.authenticated = True
        st.session_state.login_failed = False # Resetear error si entra bien
        st.session_state.input_password = "" # Limpiar campo
    else:
        st.session_state.login_failed = True # Activar mensaje de error

def cerrar_sesion():
    """Cierra la sesión actual."""
    st.session_state.authenticated = False
    st.session_state.login_failed = False
    st.rerun()

def calcular_suma_logaritmica(lista_db):
    """Realiza la suma energética de niveles sonoros."""
    if not lista_db:
        return 0.0
    valores = np.array(lista_db)
    valores = valores[~np.isnan(valores)]
    if len(valores) == 0:
        return 0.0
    suma_energia = np.sum(10 ** (valores / 10))
    resultado_db = 10 * np.log10(suma_energia)
    return resultado_db

# --- INTERFAZ: LOGIN ---
if not st.session_state.authenticated:
    
    # Intentar cargar el logo si existe, si no, poner texto
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    else:
        st.header("CS SISTEMAS DE AIRE")

    st.markdown("### 🔒 Acceso Restringido")
    
    st.text_input(
        "Ingrese su contraseña:", 
        type="password", 
        key="input_password", 
        on_change=verificar_login
    )
    
    st.button("Ingresar", on_click=verificar_login)
    
    # Mensaje de error controlado
    if st.session_state.login_failed:
        st.error("❌ Contraseña incorrecta. Intente de nuevo.")

# --- INTERFAZ: APLICACIÓN PRINCIPAL ---
else:
    # Barra lateral
    with st.sidebar:
        # Logo en la barra lateral también (opcional)
        if os.path.exists("logo.png"):
            st.image("logo.png", width=150)
        st.write("Usuario: **Admin**")
        if st.button("Cerrar Sesión"):
            cerrar_sesion()

    # Encabezado Principal
    st.title("🔊 Calculadora de Ruido Acumulado")
    
    # TEXTO ACTUALIZADO (Punto 3)
    st.info("""
    Esta herramienta realiza la **suma logarítmica** de múltiples fuentes de ruido. 
    Ideal para estimar el impacto total de varios extractores o inyectores funcionando simultáneamente, 
    recuerda que es un aproximado y existen muchas variantes adicionales a considerar por la estructura del recinto.
    """)
    
    st.divider()

    # --- SECCIÓN DE ENTRADA DE DATOS ---
    st.subheader("1. Listado de Equipos")
    
    if 'df_ruido' not in st.session_state:
        data_inicial = {
            "Nombre del Equipo": ["Extractor S&P 1", "Inyector Muro"],
            "Nivel Sonoro (dB)": [65.0, 62.0]
        }
        st.session_state.df_ruido = pd.DataFrame(data_inicial)

    column_config = {
        "Nombre del Equipo": st.column_config.TextColumn(
            "Equipo / Fuente",
            default="Nuevo Equipo",
            required=True
        ),
        "Nivel Sonoro (dB)": st.column_config.NumberColumn(
            "Presión Sonora (dB)",
            min_value=0,
            max_value=200,
            step=0.1,
            format="%.1f dB",
            required=True
        )
    }

    df_editado = st.data_editor(
        st.session_state.df_ruido,
        column_config=column_config,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="editor_datos" 
    )

    if st.button("🗑️ Borrar todo y reiniciar"):
        st.session_state.df_ruido = pd.DataFrame(
            {"Nombre del Equipo": [], "Nivel Sonoro (dB)": []}
        )
        st.rerun()

    st.divider()

    # --- SECCIÓN DE RESULTADOS ---
    st.subheader("2. Análisis Resultante")

    lista_decibeles = df_editado["Nivel Sonoro (dB)"].dropna().tolist()
    
    if len(lista_decibeles) > 0:
        resultado_total = calcular_suma_logaritmica(lista_decibeles)
        
        # MOSTRAR SOLO EL RESULTADO (Punto 4: Se quitó la nota técnica)
        st.markdown("#### Nivel Total Acumulado")
        st.metric(
            label="Suma Logarítmica", 
            value=f"{resultado_total:.2f} dB",
            delta=f"{len(lista_decibeles)} fuentes activas",
            delta_color="off"
        )

    else:
        st.warning("⚠️ Por favor, ingrese al menos un equipo y su nivel de dB en la tabla de arriba.")

    st.markdown("---")
    st.caption("© 2025 CS SISTEMAS DE AIRE | Herramienta de Cálculo Interna")
