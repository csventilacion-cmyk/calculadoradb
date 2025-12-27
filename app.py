import streamlit as st
import numpy as np
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Calculadora dB - CS Sistemas de Aire",
    page_icon="🔊",
    layout="centered"
)

# --- GESTIÓN DE ESTADO (SESSION STATE) ---
# Inicializamos variables de sesión si no existen
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Definimos la contraseña de acceso (Cámbiala aquí)
PASSWORD_CORRECTA = "csaires2025" 

# --- FUNCIONES ---

def verificar_login():
    """Verifica la contraseña ingresada."""
    input_pass = st.session_state.input_password
    if input_pass == PASSWORD_CORRECTA:
        st.session_state.authenticated = True
        st.session_state.input_password = "" # Limpiar campo por seguridad
    else:
        st.error("❌ Contraseña incorrecta. Intente de nuevo.")

def cerrar_sesion():
    """Cierra la sesión actual."""
    st.session_state.authenticated = False
    st.rerun()

def calcular_suma_logaritmica(lista_db):
    """
    Realiza la suma energética de niveles sonoros.
    Fórmula: 10 * log10( sum( 10^(Li/10) ) )
    """
    if not lista_db:
        return 0.0
    
    # Convertimos a array de numpy para eficiencia
    valores = np.array(lista_db)
    
    # Evitamos errores con valores vacíos o nulos
    valores = valores[~np.isnan(valores)]
    
    if len(valores) == 0:
        return 0.0
        
    # Cálculo de la energía sumada
    suma_energia = np.sum(10 ** (valores / 10))
    
    # Reconversión a dB
    resultado_db = 10 * np.log10(suma_energia)
    
    return resultado_db

# --- INTERFAZ: LOGIN ---
if not st.session_state.authenticated:
    st.title("🔒 Acceso Restringido")
    st.write("Bienvenido al Portal de Ingeniería de **CS SISTEMAS DE AIRE**.")
    
    st.text_input(
        "Ingrese su contraseña:", 
        type="password", 
        key="input_password", 
        on_change=verificar_login
    )
    
    st.button("Ingresar", on_click=verificar_login)
    
    st.info("Nota: Esta herramienta es de uso interno para cálculo de ruido en sistemas de ventilación.")

# --- INTERFAZ: APLICACIÓN PRINCIPAL ---
else:
    # Barra lateral con botón de salir
    with st.sidebar:
        st.write(f"Logueado como: **Admin**")
        if st.button("Cerrar Sesión"):
            cerrar_sesion()

    # Encabezado
    st.title("🔊 Calculadora de Ruido Acumulado")
    st.markdown("""
    Esta herramienta realiza la **suma logarítmica** de múltiples fuentes de ruido. 
    Ideal para calcular el impacto total de varios extractores o inyectores funcionando simultáneamente.
    """)
    
    st.divider()

    # --- SECCIÓN DE ENTRADA DE DATOS ---
    st.subheader("1. Listado de Equipos")
    
    # Configuración inicial del DataFrame
    if 'df_ruido' not in st.session_state:
        # Datos por defecto para mostrar el ejemplo
        data_inicial = {
            "Nombre del Equipo": ["Extractor S&P 1", "Inyector Muro"],
            "Nivel Sonoro (dB)": [65.0, 62.0]
        }
        st.session_state.df_ruido = pd.DataFrame(data_inicial)

    # Editor de datos (Permite agregar/borrar filas dinámicamente)
    column_config = {
        "Nombre del Equipo": st.column_config.TextColumn(
            "Equipo / Fuente",
            help="Nombre descriptivo del ventilador o fuente",
            default="Nuevo Equipo",
            required=True
        ),
        "Nivel Sonoro (dB)": st.column_config.NumberColumn(
            "Presión Sonora (dB)",
            help="Valor en decibeles",
            min_value=0,
            max_value=200,
            step=0.1,
            format="%.1f dB",
            required=True
        )
    }

    # Renderizar la tabla editable
    df_editado = st.data_editor(
        st.session_state.df_ruido,
        column_config=column_config,
        num_rows="dynamic", # Permite añadir filas
        use_container_width=True,
        hide_index=True,
        key="editor_datos" 
    )

    # Botón de reinicio rápido
    if st.button("🗑️ Borrar todo y reiniciar"):
        st.session_state.df_ruido = pd.DataFrame(
            {"Nombre del Equipo": [], "Nivel Sonoro (dB)": []}
        )
        st.rerun()

    st.divider()

    # --- SECCIÓN DE RESULTADOS ---
    st.subheader("2. Análisis Resultante")

    # Extraer los valores numéricos válidos
    lista_decibeles = df_editado["Nivel Sonoro (dB)"].dropna().tolist()
    
    if len(lista_decibeles) > 0:
        # Realizar cálculo
        resultado_total = calcular_suma_logaritmica(lista_decibeles)
        
        # Columnas para mostrar resultado y detalles lado a lado
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### Nivel Total Acumulado")
            # Mostramos el resultado en grande
            st.metric(
                label="Suma Logarítmica", 
                value=f"{resultado_total:.2f} dB",
                delta=f"{len(lista_decibeles)} fuentes activas",
                delta_color="off"
            )
        
        with col2:
            st.info("💡 **Nota Técnica:**")
            st.markdown("""
            El sonido no se suma aritméticamente ($50+50 \\neq 100$).
            * **Regla Práctica:** Dos fuentes de igual intensidad suman **+3 dB** al total.
            * **Ejemplo:** $60 \\text{ dB} + 60 \\text{ dB} = 63 \\text{ dB}$.
            """)
            
        # Gráfico simple opcional para visualizar la contribución
        # (Descomentar si se desea ver barras de los equipos vs el total)
        # st.bar_chart(df_editado.set_index("Nombre del Equipo"))

    else:
        st.warning("⚠️ Por favor, ingrese al menos un equipo y su nivel de dB en la tabla de arriba.")

    # Pie de página profesional
    st.markdown("---")
    st.caption("© 2025 CS SISTEMAS DE AIRE | Herramienta de Cálculo Interna v1.0")
