import streamlit as st
import plotly.graph_objects as go
from components_v2 import mostrar_seccion
from config_v2 import COLORS

def tab_zonas_tipos(df_filtered):
    mostrar_seccion("Zonas y Tipos de Comida")
    
    if len(df_filtered) == 0:
        st.warning("No hay datos para mostrar")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"<h4 style='color: {COLORS['pastel_cyan']};'>Rating por Zona</h4>", unsafe_allow_html=True)
        zona_stats = df_filtered.groupby('zona_cat')['rating'].agg(['mean', 'count']).reset_index()
        zona_stats = zona_stats.sort_values('mean', ascending=True)
        
        fig_zona = go.Figure(go.Bar(
            x=zona_stats['mean'],
            y=zona_stats['zona_cat'],
            orientation='h',
            marker=dict(color=COLORS['morado_claro'])
        ))
        
        fig_zona.update_layout(
            template="plotly_dark",
            paper_bgcolor=COLORS['morado_oscuro'],
            plot_bgcolor=COLORS['morado_medio'],
            font=dict(color=COLORS['blanco']),
            height=400
        )
        
        st.plotly_chart(fig_zona, use_container_width=True)
    
    with col2:
        st.markdown(f"<h4 style='color: {COLORS['pastel_cyan']};'>Rating por Tipo de Comida</h4>", unsafe_allow_html=True)
        tipo_stats = df_filtered.groupby('tipo_comida')['rating'].agg(['mean', 'count']).reset_index()
        tipo_stats = tipo_stats.sort_values('mean', ascending=True)
        
        fig_tipo = go.Figure(go.Bar(
            x=tipo_stats['mean'],
            y=tipo_stats['tipo_comida'],
            orientation='h',
            marker=dict(color=COLORS['pastel_rosa'])
        ))
        
        fig_tipo.update_layout(
            template="plotly_dark",
            paper_bgcolor=COLORS['morado_oscuro'],
            plot_bgcolor=COLORS['morado_medio'],
            font=dict(color=COLORS['blanco']),
            height=400
        )
        
        st.plotly_chart(fig_tipo, use_container_width=True)
