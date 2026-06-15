import streamlit as st
import plotly.graph_objects as go
from components_v2 import mostrar_seccion
from config_v2 import COLORS

def tab_calidad_popularidad(df_filtered):
    mostrar_seccion("Rating vs Total de Reviews")
    
    if len(df_filtered) == 0:
        st.warning("No hay datos para mostrar")
        return
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_filtered['total_reviews'],
        y=df_filtered['rating'],
        mode='markers',
        marker=dict(
            size=8,
            color=df_filtered['rating'],
            colorscale=[[0, COLORS['morado_oscuro']], [1, COLORS['pastel_rosa']]],
            showscale=True,
            colorbar=dict(title="Rating")
        ),
        text=df_filtered['name'],
        hovertemplate='<b>%{text}</b><br>Reviews: %{x}<br>Rating: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Calidad vs Popularidad",
        xaxis_title="Total de Reviews",
        yaxis_title="Rating",
        template="plotly_dark",
        paper_bgcolor=COLORS['morado_oscuro'],
        plot_bgcolor=COLORS['morado_medio'],
        font=dict(color=COLORS['blanco']),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
