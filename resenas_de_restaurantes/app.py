# ============================================================================
# PANAMA RESTAURANTS ANALYTICS - VERSIÓN 2
# ============================================================================

import os

import streamlit as st

from config_v2 import CSS_CUSTOM, COLORS
from data_loader_v2 import (
    load_data,
    crear_columnas_calculadas,
    aplicar_filtros,
    obtener_opciones_filtros,
)
from tab_01_historia_v2 import tab_historia_general
from tab_02_calidad_v2 import tab_calidad_popularidad
from tab_03_zonas_v2 import tab_zonas_tipos
from tab_04_sentimiento_v2 import tab_sentimiento
from tab_05_clusters_v2 import tab_clusters
from tab_06_exploracion_v2 import tab_exploracion
from tab_07_recomendaciones_v2 import tab_recomendaciones

# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Panama Restaurants Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CSS_CUSTOM, unsafe_allow_html=True)

# ============================================================================
# CARGA Y PROCESAMIENTO DE DATOS
# ============================================================================

# load_data() lee los CSV de forma relativa al directorio de trabajo, por lo
# que este debe apuntar a la carpeta del script antes de cargar los datos.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

df = load_data()
df = crear_columnas_calculadas(df)
opciones_filtros = obtener_opciones_filtros(df)

# ============================================================================
# BARRA LATERAL - FILTROS GLOBALES
# ============================================================================

st.sidebar.markdown(f"<h2 style='color: {COLORS['pastel_cyan']};'>Filtros Globales</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

tipo_comida_seleccionado = st.sidebar.multiselect(
    "Tipo de Comida",
    options=["Todos"] + opciones_filtros['tipos_comida'],
    default="Todos",
    help="Selecciona uno o más tipos de comida",
)

rango_precio_seleccionado = st.sidebar.multiselect(
    "Rango de Precio",
    options=["Todos"] + opciones_filtros['rangos_precio'],
    default="Todos",
    help="Selecciona uno o más rangos de precio",
)

zona_seleccionada = st.sidebar.multiselect(
    "Zona",
    options=["Todas"] + opciones_filtros['zonas'],
    default="Todas",
    help="Selecciona una o más zonas",
)

calificacion_seleccionada = st.sidebar.multiselect(
    "Calificación",
    options=["Todas"] + opciones_filtros['calificaciones'],
    default="Todas",
    help="Selecciona una o más categorías de calificación",
)

sentimiento_seleccionado = st.sidebar.multiselect(
    "Sentimiento",
    options=["Todos"] + opciones_filtros['sentimientos'],
    default="Todos",
    help="Selecciona uno o más sentimientos",
)

st.sidebar.markdown("---")
total_restaurantes = len(df)
st.sidebar.metric("Total Restaurantes", total_restaurantes)

# ============================================================================
# APLICAR FILTROS
# ============================================================================

df_filtered = aplicar_filtros(
    df,
    zona_seleccionada if "Todas" not in zona_seleccionada else None,
    tipo_comida_seleccionado if "Todos" not in tipo_comida_seleccionado else None,
    rango_precio_seleccionado if "Todos" not in rango_precio_seleccionado else None,
    calificacion_seleccionada if "Todas" not in calificacion_seleccionada else None,
    sentimiento_seleccionado if "Todos" not in sentimiento_seleccionado else None,
)

restaurantes_filtrados = len(df_filtered)

# ============================================================================
# TÍTULO PRINCIPAL
# ============================================================================

st.markdown(f"""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: {COLORS['blanco']};">Panama Restaurants Analytics</h1>
        <p style="color: {COLORS['pastel_cyan']}; font-size: 16px;">
        Descubriendo patrones de calidad, experiencia y preferencias gastronómicas en Panamá
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# PESTAÑAS PRINCIPALES
# ============================================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Historia General",
    "Calidad vs Popularidad",
    "Zonas y Tipos de Comida",
    "Sentimiento y Experiencia",
    "Clusters",
    "Exploración Detallada",
    "Recomendaciones",
])

with tab1:
    tab_historia_general(df_filtered, df, restaurantes_filtrados, total_restaurantes)

with tab2:
    tab_calidad_popularidad(df_filtered)

with tab3:
    tab_zonas_tipos(df_filtered)

with tab4:
    tab_sentimiento(df_filtered)

with tab5:
    tab_clusters(df_filtered)

with tab6:
    tab_exploracion(df_filtered)

with tab7:
    tab_recomendaciones(df_filtered, df)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; color: {COLORS['pastel_cyan']}; font-size: 12px;">
    <p>Dashboard de Análisis de Restaurantes de Panamá |
    Datos actualizados |
    Filtros dinámicos habilitados</p>
    </div>
""", unsafe_allow_html=True)
