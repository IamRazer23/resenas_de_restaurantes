import streamlit as st
from components_v2 import mostrar_seccion
from config_v2 import COLORS

def tab_exploracion(df_filtered):
    mostrar_seccion("Exploración Detallada")
    
    if len(df_filtered) == 0:
        st.warning("No hay restaurantes que coincidan con los filtros seleccionados.")
        st.info("💡 Intenta ajustar los filtros para ver más resultados.")
        return
    
    # Seleccionar columnas relevantes
    cols_mostrar = ['name', 'rating', 'total_reviews', 'zona_cat', 'tipo_comida', 'rango_precio', 'sentimiento']
    cols_disponibles = [col for col in cols_mostrar if col in df_filtered.columns]
    
    st.markdown(f"<p style='color: {COLORS['pastel_cyan']};'>Total: {len(df_filtered)} restaurantes</p>", unsafe_allow_html=True)
    
    st.dataframe(
        df_filtered[cols_disponibles].sort_values('rating', ascending=False),
        use_container_width=True,
        height=600
    )
    
    # Descargar CSV
    csv = df_filtered[cols_disponibles].to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Descargar como CSV",
        data=csv,
        file_name="restaurantes_filtrados.csv",
        mime="text/csv"
    )
