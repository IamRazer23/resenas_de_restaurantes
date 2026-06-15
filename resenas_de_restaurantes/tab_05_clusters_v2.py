import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from components_v2 import mostrar_seccion, crear_insight_card
from config_v2 import COLORS

def tab_clusters(df_filtered):
    mostrar_seccion("Análisis de Clusters K-Means")
    
    if len(df_filtered) == 0:
        st.warning("No hay datos para mostrar")
        return
    
    if 'cluster' not in df_filtered.columns:
        st.info("ℹ️ La columna 'cluster' no está disponible en los datos")
        return
    
    # ============================================================
    # VISTA GENERAL DE CLUSTERS
    # ============================================================
    
    st.markdown(f"<h4 style='color: {COLORS['pastel_cyan']};'>📊 Distribución y Características de Clusters</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    cluster_stats = df_filtered.groupby('cluster').agg({
        'rating': ['mean', 'std'],
        'total_reviews': ['mean', 'sum'],
        'name': 'count'
    }).round(2)
    
    cluster_stats.columns = ['Rating Promedio', 'Desv. Rating', 'Reviews Promedio', 'Total Reviews', 'Cantidad Restaurantes']
    cluster_stats = cluster_stats.reset_index()
    
    with col1:
        num_clusters = len(cluster_stats)
        st.metric("Número de Clusters", num_clusters)
    
    with col2:
        cluster_grande = cluster_stats.loc[cluster_stats['Cantidad Restaurantes'].idxmax()]
        st.metric("Cluster más Grande", f"Cluster {int(cluster_grande['cluster'])} ({int(cluster_grande['Cantidad Restaurantes'])} rest.)")
    
    with col3:
        cluster_mejor = cluster_stats.loc[cluster_stats['Rating Promedio'].idxmax()]
        st.metric("Cluster con mejor Rating", f"{cluster_mejor['Rating Promedio']:.2f}⭐")
    
    # ============================================================
    # GRÁFICO 1: RATING POR CLUSTER
    # ============================================================
    
    st.markdown("---")
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown(f"<h4 style='color: {COLORS['pastel_cyan']};'>Rating Promedio por Cluster</h4>", unsafe_allow_html=True)
        
        fig_rating = go.Figure(go.Bar(
            x=cluster_stats['cluster'].astype(str),
            y=cluster_stats['Rating Promedio'],
            marker=dict(
                color=cluster_stats['Rating Promedio'],
                colorscale=[[0, '#2e2b56'], [0.5, '#6357a0'], [1, '#a689f7']],
                line=dict(color=COLORS['pastel_cyan'], width=2)
            ),
            text=cluster_stats['Rating Promedio'].round(2),
            textposition='outside',
            hovertemplate='<b>Cluster %{x}</b><br>Rating: %{y:.2f}<extra></extra>'
        ))
        
        fig_rating.update_layout(
            template="plotly_dark",
            paper_bgcolor=COLORS['morado_oscuro'],
            plot_bgcolor=COLORS['morado_medio'],
            font=dict(color=COLORS['blanco']),
            height=400,
            xaxis_title="Cluster",
            yaxis_title="Rating Promedio",
            showlegend=False
        )
        
        st.plotly_chart(fig_rating, use_container_width=True)
    
    with col_right:
        st.markdown(f"<h4 style='color: {COLORS['pastel_cyan']};'>Cantidad de Restaurantes por Cluster</h4>", unsafe_allow_html=True)
        
        fig_count = go.Figure(go.Bar(
            x=cluster_stats['cluster'].astype(str),
            y=cluster_stats['Cantidad Restaurantes'],
            marker=dict(
                color=COLORS['pastel_rosa'],
                line=dict(color=COLORS['pastel_cyan'], width=2)
            ),
            text=cluster_stats['Cantidad Restaurantes'].astype(int),
            textposition='outside',
            hovertemplate='<b>Cluster %{x}</b><br>Restaurantes: %{y}<extra></extra>'
        ))
        
        fig_count.update_layout(
            template="plotly_dark",
            paper_bgcolor=COLORS['morado_oscuro'],
            plot_bgcolor=COLORS['morado_medio'],
            font=dict(color=COLORS['blanco']),
            height=400,
            xaxis_title="Cluster",
            yaxis_title="Cantidad",
            showlegend=False
        )
        
        st.plotly_chart(fig_count, use_container_width=True)
    
    # ============================================================
    # TABLA DETALLADA
    # ============================================================
    
    st.markdown("---")
    st.markdown(f"<h4 style='color: {COLORS['pastel_cyan']};'>📋 Detalles de Clusters</h4>", unsafe_allow_html=True)
    
    tabla_clusters = cluster_stats.copy()
    tabla_clusters['cluster'] = 'Cluster ' + tabla_clusters['cluster'].astype(str)
    tabla_clusters = tabla_clusters.rename(columns={
        'cluster': 'Grupo',
        'Rating Promedio': 'Rating Prom.',
        'Desv. Rating': 'Desv. Est.',
        'Reviews Promedio': 'Reviews Prom.',
        'Total Reviews': 'Total Rev.',
        'Cantidad Restaurantes': 'Cantidad'
    })
    
    st.dataframe(tabla_clusters, use_container_width=True, hide_index=True)
    
    # ============================================================
    # INSIGHTS POR CLUSTER
    # ============================================================
    
    st.markdown("---")
    st.markdown(f"<h4 style='color: {COLORS['pastel_cyan']};'>💡 Características de Cada Cluster</h4>", unsafe_allow_html=True)
    
    for idx, row in cluster_stats.iterrows():
        cluster_id = int(row['cluster'])
        cluster_data = df_filtered[df_filtered['cluster'] == cluster_id]
        
        tipo_comida_top = cluster_data['tipo_comida'].mode()[0] if len(cluster_data) > 0 else "N/A"
        zona_top = cluster_data['zona_cat'].mode()[0] if len(cluster_data) > 0 else "N/A"
        rango_precio_top = cluster_data['rango_precio'].mode()[0] if len(cluster_data) > 0 else "N/A"
        sentimiento_top = cluster_data['sentimiento'].mode()[0] if len(cluster_data) > 0 else "N/A"
        
        mensaje = f"""
        <b>Cluster {cluster_id}:</b> {int(row['Cantidad Restaurantes'])} restaurantes<br>
        • Rating: {row['Rating Promedio']:.2f}⭐ (σ={row['Desv. Rating']:.2f})<br>
        • Reviews: {int(row['Total Reviews'])} en total<br>
        • Tipo comida: <b>{tipo_comida_top}</b><br>
        • Zona: <b>{zona_top}</b><br>
        • Rango precio: <b>{rango_precio_top}</b><br>
        • Sentimiento: <b>{sentimiento_top}</b>
        """
        
        crear_insight_card(f"Cluster {cluster_id}", mensaje, "🎯")