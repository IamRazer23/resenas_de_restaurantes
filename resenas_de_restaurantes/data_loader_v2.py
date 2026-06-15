import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

@st.cache_data
def load_data():
    try:
        current_dir = Path.cwd()
        
        clustered_file = current_dir / "PANAMA_RESTAURANTS_CLUSTERED.csv"
        df_clustered = pd.read_csv(clustered_file, sep=';', encoding='iso-8859-1')
        
        sentiment_file = current_dir / "panama_restaurants_sentiment.csv"
        df_sentiment = pd.read_csv(sentiment_file, encoding='utf-8-sig')
        
        df = pd.merge(
            df_clustered,
            df_sentiment[['place_id', 'comida_score', 'servicio_score', 'precio_score', 'ambiente_score', 'sentimiento_general']],
            on='place_id',
            how='left'
        )
        
        return df
    
    except FileNotFoundError as e:
        st.error(f"❌ Error al cargar archivos CSV: {e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error procesando datos: {e}")
        st.stop()

def crear_columnas_calculadas(df):
    df = df.copy()
    
    df['score_confianza'] = df['rating'] * np.log1p(df['total_reviews'])
    
    sentimiento_map = {'Muy positivo': 4, 'Positivo': 3, 'Neutral': 2, 'Negativo': 1}
    df['sentimiento_score'] = df['sentimiento'].map(sentimiento_map).fillna(2)
    
    aspectos = ['comida_score', 'servicio_score', 'precio_score', 'ambiente_score']
    df['aspecto_promedio'] = df[aspectos].mean(axis=1)
    
    df['aspecto_fuerte'] = df[aspectos].idxmax(axis=1).str.replace('_score', '')
    df['aspecto_debil'] = df[aspectos].idxmin(axis=1).str.replace('_score', '')
    
    rating_promedio = df['rating'].median()
    reviews_promedio = df['total_reviews'].median()
    sentimiento_promedio = df['sentimiento_score'].median()
    
    def categorizar_popularidad(row):
        rating_alto = row['rating'] >= rating_promedio
        reviews_alto = row['total_reviews'] >= reviews_promedio
        sentimiento_positivo = row['sentimiento_score'] >= sentimiento_promedio
        
        if rating_alto and reviews_alto and sentimiento_positivo:
            return 'Favorito confiable'
        elif rating_alto and not reviews_alto and sentimiento_positivo:
            return 'Joya oculta'
        elif reviews_alto and not (rating_alto and sentimiento_positivo):
            return 'Popular con riesgo'
        else:
            return 'Bajo atractivo'
    
    df['categoria_popularidad_calidad'] = df.apply(categorizar_popularidad, axis=1)
    
    return df

def aplicar_filtros(df, zona, tipo_comida, rango_precio, calificacion, sentimiento):
    df_filtered = df.copy()
    
    if zona and "Todas" not in zona and zona:
        df_filtered = df_filtered[df_filtered['zona_cat'].isin(zona)]
    
    if tipo_comida and "Todos" not in tipo_comida and tipo_comida:
        df_filtered = df_filtered[df_filtered['tipo_comida'].isin(tipo_comida)]
    
    if rango_precio and "Todos" not in rango_precio and rango_precio:
        df_filtered = df_filtered[df_filtered['rango_precio'].isin(rango_precio)]
    
    if calificacion and "Todas" not in calificacion and calificacion:
        df_filtered = df_filtered[df_filtered['calificacion_cat'].isin(calificacion)]
    
    if sentimiento and "Todos" not in sentimiento and sentimiento:
        df_filtered = df_filtered[df_filtered['sentimiento'].isin(sentimiento)]
    
    return df_filtered

def obtener_opciones_filtros(df):
    return {
        'zonas': sorted([z for z in df['zona_cat'].unique() if pd.notna(z)]),
        'tipos_comida': sorted([t for t in df['tipo_comida'].unique() if pd.notna(t)]),
        'rangos_precio': sorted([p for p in df['rango_precio'].unique() if pd.notna(p)]),
        'calificaciones': ['Excelente (4.5-5.0)', 'Muy Bueno (4.0-4.4)', 'Bueno (3.5-3.9)', 'Regular (<3.5)'],
        'sentimientos': sorted([s for s in df['sentimiento'].unique() if pd.notna(s)])
    }
