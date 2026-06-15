import streamlit as st
from config_v2 import COLORS

def crear_metric_card(title, value, subtitle=""):
    st.markdown(f"""
        <div class="metric-card">
            <h4>{title}</h4>
            <h2>{value}</h2>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
    """, unsafe_allow_html=True)

def crear_insight_card(titulo, contenido, icon="💡"):
    st.markdown(f"""
        <div class="insight-card">
            <h4>{icon} {titulo}</h4>
            <p>{contenido}</p>
        </div>
    """, unsafe_allow_html=True)

def mostrar_titulo_pagina(titulo, subtitulo=""):
    color_cyan = COLORS['pastel_cyan']
    color_blanco = COLORS['blanco']
    
    if subtitulo:
        subtitulo_html = f'<p style="color: {color_cyan}; font-size: 16px;">{subtitulo}</p>'
    else:
        subtitulo_html = ''
    
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: {color_blanco}; margin-bottom: 5px;">{titulo}</h1>
            {subtitulo_html}
        </div>
    """, unsafe_allow_html=True)

def mostrar_seccion(titulo):
    color_cyan = COLORS['pastel_cyan']
    st.markdown(f"<h2 style='color: {color_cyan};'>{titulo}</h2>", unsafe_allow_html=True)

def mostrar_mensaje_vacio():
    st.warning("⚠️ No hay restaurantes que coincidan con los filtros seleccionados.")
    st.info("💡 Intenta ajustar los filtros para ver más resultados.")

def crear_paleta_colores_por_categoria(categorias, tipo='pastel'):
    colores_pastel = [
        COLORS['pastel_rosa'],
        COLORS['pastel_cyan'],
        COLORS['pastel_verde'],
        COLORS['pastel_lila'],
        COLORS['pastel_amarillo'],
        COLORS['pastel_naranja'],
    ]
    
    colores_morados = [
        COLORS['morado_oscuro'],
        COLORS['morado_medio'],
        COLORS['morado_claro'],
    ]
    
    paleta = colores_pastel if tipo == 'pastel' else colores_morados
    
    colores_asignados = []
    for i, _ in enumerate(categorias):
        colores_asignados.append(paleta[i % len(paleta)])
    
    return colores_asignados
