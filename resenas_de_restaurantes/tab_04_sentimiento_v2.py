import streamlit as st
import plotly.graph_objects as go
from components_v2 import mostrar_seccion
from config_v2 import COLORS

def tab_sentimiento(df_filtered):
    mostrar_seccion("Sentimiento y Experiencia")
    
    if len(df_filtered) == 0:
        st.warning("No hay datos para mostrar")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"<h4 style='color: {COLORS['pastel_cyan']};'>Distribución de Sentimientos</h4>", unsafe_allow_html=True)
        sentimiento_counts = df_filtered['sentimiento'].value_counts()
        
        # Colores vibrantes y distintos
        colores_pie = [
            '#f7c3ff',  # Rosa pastel - Color 5
            '#a689f7',  # Morado claro - Color 4
            '#6357a0',  # Morado medio - Color 3
            '#2e2b56',  # Morado oscuro - Color 2
            '#04001a'   # Negro oscuro - Color 1
        ]
        
        fig_sentimiento = go.Figure(data=[go.Pie(
            labels=sentimiento_counts.index,
            values=sentimiento_counts.values,
            hole=0,  # Sin agujero en el centro (pie chart completo)
            marker=dict(
                colors=colores_pie[:len(sentimiento_counts)],
                line=dict(color=COLORS['blanco'], width=3)  # Borde blanco entre secciones
            ),
            textposition='auto',
            textinfo='label+percent+value',
            textfont=dict(size=13, color=COLORS['blanco'], family="Arial Black"),
            hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>'
        )])
        
        fig_sentimiento.update_layout(
            template="plotly_dark",
            paper_bgcolor=COLORS['morado_oscuro'],
            font=dict(color=COLORS['blanco'], size=12),
            height=600,
            width=600,
            margin=dict(l=50, r=50, t=50, b=50),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.95,
                xanchor="right",
                x=0.95,
                bgcolor='rgba(46, 43, 86, 0.8)',
                bordercolor=COLORS['pastel_cyan'],
                borderwidth=2,
                font=dict(size=11)
            )
        )
        
        st.plotly_chart(fig_sentimiento, use_container_width=False, config={'responsive': True})
    
    with col2:
        st.markdown(f"<h4 style='color: {COLORS['pastel_cyan']};'>Sentimiento por Zona</h4>", unsafe_allow_html=True)
        sentimiento_zona = df_filtered.groupby('zona_cat')['sentimiento_score'].mean().reset_index().sort_values('sentimiento_score', ascending=False)
        
        fig_zona_sent = go.Figure(go.Bar(
            x=sentimiento_zona['zona_cat'],
            y=sentimiento_zona['sentimiento_score'],
            marker=dict(
                color=sentimiento_zona['sentimiento_score'],
                colorscale=[[0, '#2e2b56'], [0.5, '#6357a0'], [1, '#a689f7']],
                line=dict(color=COLORS['pastel_cyan'], width=2),
                colorbar=dict(title="Score")
            ),
            text=sentimiento_zona['sentimiento_score'].round(2),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Score: %{y:.2f}<extra></extra>'
        ))
        
        fig_zona_sent.update_layout(
            template="plotly_dark",
            paper_bgcolor=COLORS['morado_oscuro'],
            plot_bgcolor=COLORS['morado_medio'],
            font=dict(color=COLORS['blanco'], size=12),
            height=600,
            xaxis_title="Zona",
            yaxis_title="Score Sentimiento",
            showlegend=False
        )
        
        st.plotly_chart(fig_zona_sent, use_container_width=True)