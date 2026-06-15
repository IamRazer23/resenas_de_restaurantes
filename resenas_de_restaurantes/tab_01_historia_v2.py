import streamlit as st
from components_v2 import crear_metric_card, crear_insight_card, mostrar_seccion
from config_v2 import COLORS

def tab_historia_general(df_filtered, df, restaurantes_filtrados, total_restaurantes):
    mostrar_seccion("¿Qué panorama muestran los restaurantes filtrados?")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        crear_metric_card("Restaurantes", restaurantes_filtrados, f"de {total_restaurantes} total")
    
    with col2:
        rating = df_filtered['rating'].mean() if len(df_filtered) > 0 else 0
        crear_metric_card("Rating Promedio", f"{rating:.2f} ⭐", "evaluación general")
    
    with col3:
        reviews = df_filtered['total_reviews'].sum() if len(df_filtered) > 0 else 0
        crear_metric_card("Total de Reviews", f"{int(reviews):,}", "reseñas acumuladas")
    
    with col4:
        sentimiento = df_filtered['sentimiento'].mode()[0] if len(df_filtered) > 0 else "N/A"
        crear_metric_card("Sentimiento Dominante", sentimiento, "opinión general")
    
    st.markdown("---")
    
    st.markdown(f"<h3 style='color: {COLORS['pastel_cyan']};'>💡 Insights Clave</h3>", unsafe_allow_html=True)
    
    if len(df_filtered) > 0:
        zona_mejor = df_filtered.groupby('zona_cat')['rating'].mean().idxmax()
        rating_zona = df_filtered.groupby('zona_cat')['rating'].mean().max()
        crear_insight_card(
            "Zona con Mejor Rating",
            f"<b>{zona_mejor}</b> con promedio de <b>{rating_zona:.2f}⭐</b>",
            "📍"
        )
        
        tipo_mejor = df_filtered.groupby('tipo_comida')['rating'].mean().idxmax()
        rating_tipo = df_filtered.groupby('tipo_comida')['rating'].mean().max()
        crear_insight_card(
            "Tipo de Comida Mejor Evaluado",
            f"<b>{tipo_mejor}</b> con promedio de <b>{rating_tipo:.2f}⭐</b>",
            "🍽️"
        )
        
        favorito = df_filtered.loc[df_filtered['rating'].idxmax(), 'name']
        rating_favorito = df_filtered['rating'].max()
        crear_insight_card(
            "Favorito Confiable",
            f"<b>{favorito}</b> con rating de <b>{rating_favorito:.2f}⭐</b>",
            "⭐"
        )
