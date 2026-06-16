"""Pestaña de recomendaciones.

Filtra los restaurantes según las preferencias del usuario (tipo de comida,
zona y rango de precio) y los ordena con un score ponderado de compatibilidad.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from config_v2 import COLORS

# Peso de cada componente en el score global de compatibilidad (suman 1.0).
PESOS_SCORE = {'rating': 0.35, 'aspectos': 0.30, 'sentimiento': 0.20, 'reviews': 0.15}

# Peso relativo de cada aspecto dentro del componente de aspectos del score.
PESOS_ASPECTOS = {'comida': 0.40, 'servicio': 0.25, 'precio': 0.20, 'ambiente': 0.15}

# Valor normalizado [0, 1] asignado a cada etiqueta de sentimiento.
SENTIMIENTO_VALOR = {'Muy positivo': 1.0, 'Positivo': 0.75, 'Neutral': 0.5, 'Negativo': 0.25}

ASPECTOS = ['comida_score', 'servicio_score', 'precio_score', 'ambiente_score']

# Colores de medalla para los tres primeros puestos del ranking.
COLORES_RANK = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32"}

SENT_COLORS = {
    'Muy positivo': '#22c55e',
    'Positivo':     '#86efac',
    'Neutral':      '#facc15',
    'Negativo':     '#f87171',
}

PALETA_RADAR = ['#a689f7', '#f7c3ff', '#6357a0', '#c4b5fd', '#ddd6fe']


def _normalizar(serie):
    """Escala una serie al rango [0, 1].

    Si el rango es cero (todos los valores iguales) devuelve 0.5 para no
    introducir sesgo en el score.
    """
    rango = serie.max() - serie.min()
    if rango > 0:
        return (serie - serie.min()) / rango
    return serie * 0 + 0.5


def _calcular_scores(rec):
    """Añade la columna 'score' (compatibilidad 0-1) al DataFrame.

    score = 0.35*rating + 0.30*aspectos + 0.20*sentimiento + 0.15*log(reseñas)

    El componente de aspectos pondera comida/servicio/precio/ambiente según
    PESOS_ASPECTOS. Los NaN del score final se rellenan con rating/5.
    """
    rec['_r'] = _normalizar(rec['rating'])
    rec['_rv'] = _normalizar(np.log1p(rec['total_reviews']))
    rec['_s'] = rec['sentimiento'].map(SENTIMIENTO_VALOR).fillna(0.5)

    for asp in ASPECTOS:
        if asp in rec.columns:
            mediana = rec[asp].median()
            mediana = 0 if pd.isna(mediana) else mediana
            rec[f'_n_{asp}'] = _normalizar(rec[asp].fillna(mediana))
        else:
            rec[f'_n_{asp}'] = 0.5

    rec['_asp'] = (
        PESOS_ASPECTOS['comida']   * rec['_n_comida_score'] +
        PESOS_ASPECTOS['servicio'] * rec['_n_servicio_score'] +
        PESOS_ASPECTOS['precio']   * rec['_n_precio_score'] +
        PESOS_ASPECTOS['ambiente'] * rec['_n_ambiente_score']
    )
    rec['score'] = (
        PESOS_SCORE['rating']      * rec['_r'] +
        PESOS_SCORE['aspectos']    * rec['_asp'] +
        PESOS_SCORE['sentimiento'] * rec['_s'] +
        PESOS_SCORE['reviews']     * rec['_rv']
    ).fillna(rec['rating'] / 5.0).clip(0, 1)
    return rec


def _badge(texto, fondo):
    """Devuelve el HTML de una etiqueta coloreada."""
    return (
        f"<span style='background:{fondo};color:#fff;padding:3px 10px;"
        f"border-radius:12px;font-size:12px;font-weight:bold;"
        f"margin-right:4px;'>{texto}</span>"
    )


def _aplicar_preferencias(base, tipo_pref, zona_pref, precio_pref):
    """Aplica las preferencias como filtros duros sobre 'base'.

    Si la combinación no deja resultados, relaja los filtros uno a uno
    manteniendo el más importante (tipo de comida). Devuelve
    (DataFrame filtrado, lista de filtros aplicados, se_relajo).
    """
    # (valor, columna, etiqueta) en orden de importancia: tipo > zona > precio.
    prefs = [
        (tipo_pref, 'tipo_comida', 'Tipo'),
        (zona_pref, 'zona_cat', 'Zona'),
        (precio_pref, 'rango_precio', 'Precio'),
    ]

    # 1) Filtros duros: aplicar todas las preferencias seleccionadas.
    rec = base.copy()
    filtros = []
    for valor, columna, etiqueta in prefs:
        if valor != "Sin preferencia":
            rec = rec[rec[columna] == valor]
            filtros.append(f"{etiqueta}: {valor}")

    if len(rec) > 0 or len(filtros) <= 1:
        return rec, filtros, False

    # 2) Sin resultados: relajar uno a uno. Cada preferencia se añade solo si
    #    conserva resultados, y las secundarias (zona, precio) solo si ya hay
    #    un filtro ancla aplicado (el tipo, la primera de la lista).
    rec = base.copy()
    filtros = []
    for i, (valor, columna, etiqueta) in enumerate(prefs):
        if valor == "Sin preferencia":
            continue
        if i > 0 and len(filtros) == 0:
            continue
        tmp = rec[rec[columna] == valor]
        if len(tmp) > 0:
            rec = tmp
            filtros.append(f"{etiqueta}: {valor}")

    return rec, filtros, True


def _render_lista(top_df):
    """Renderiza la lista de tarjetas de restaurantes recomendados."""
    for i, (_, row) in enumerate(top_df.iterrows(), start=1):
        c_rank = COLORES_RANK.get(i, COLORS['pastel_cyan'])
        s_col = SENT_COLORS.get(row.get('sentimiento', ''), COLORS['morado_claro'])
        aspecto = row.get('aspecto_fuerte', 'N/A')
        aspecto = aspecto.capitalize() if pd.notna(aspecto) else 'N/A'
        score_val = row['score'] if pd.notna(row['score']) else 0.0
        barra = int(score_val * 100)
        reviews = int(row['total_reviews']) if pd.notna(row['total_reviews']) else 0
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{COLORS['morado_medio']} 0%,#1a1740 100%);
                    border:2px solid {c_rank};border-radius:14px;
                    padding:18px 22px;margin-bottom:14px;">
            <div style="display:flex;justify-content:space-between;
                        align-items:center;margin-bottom:8px;">
                <span style="font-size:22px;font-weight:bold;color:{c_rank};">#{i}</span>
                <span style="font-size:18px;font-weight:bold;
                             color:{COLORS['blanco']};">{row['name']}</span>
                <span style="font-size:16px;color:{COLORS['pastel_cyan']};font-weight:bold;">
                    {row['rating']:.1f}
                    <span style="font-size:12px;color:{COLORS['gris_claro']};">
                        ({reviews:,} reseñas)
                    </span>
                </span>
            </div>
            <div style="margin-bottom:8px;">
                {_badge(row.get('tipo_comida', 'N/A'), COLORS['morado_claro'])}
                {_badge(row.get('zona_cat', 'N/A'), '#3b3769')}
                {_badge(row.get('rango_precio', 'N/A'), '#4a3f8c')}
                {_badge(row.get('sentimiento', 'N/A'), s_col)}
                {_badge(aspecto, '#2e2b56')}
            </div>
            <div style="margin-top:8px;">
                <span style="color:{COLORS['gris_claro']};font-size:12px;">
                    Match score: {barra}%
                </span>
                <div style="background:{COLORS['morado_oscuro']};
                            border-radius:6px;height:8px;margin-top:4px;">
                    <div style="background:{COLORS['pastel_cyan']};
                                width:{barra}%;height:8px;border-radius:6px;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_radar(top_df):
    """Renderiza el radar del top 5 y la tabla de scores detallados."""
    st.markdown(f"<h4 style='color:{COLORS['pastel_cyan']};'>Perfil del Top 5</h4>", unsafe_allow_html=True)
    top5 = top_df.head(5)
    cats = ['Comida', 'Servicio', 'Precio', 'Ambiente', 'Rating']
    col_map = {
        'Comida':   'comida_score',
        'Servicio': 'servicio_score',
        'Precio':   'precio_score',
        'Ambiente': 'ambiente_score',
        'Rating':   'rating',
    }
    fig_r = go.Figure()

    for idx, (_, rest) in enumerate(top5.iterrows()):
        vals = []
        for cat, col_r in col_map.items():
            v = rest.get(col_r, 0) if pd.notna(rest.get(col_r, 0)) else 0
            vals.append(round((v / 5.0) * 10 if cat == 'Rating' else v, 2))
        fig_r.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=cats + [cats[0]],
            fill='toself',
            name=rest['name'][:22] + ('...' if len(rest['name']) > 22 else ''),
            line=dict(color=PALETA_RADAR[idx % 5], width=2),
            fillcolor=PALETA_RADAR[idx % 5],
            opacity=0.25,
        ))

    fig_r.update_layout(
        polar=dict(
            bgcolor=COLORS['morado_medio'],
            radialaxis=dict(
                visible=True, range=[0, 10],
                color=COLORS['gris_claro'],
                gridcolor=COLORS['morado_claro']
            ),
            angularaxis=dict(color=COLORS['blanco'])
        ),
        paper_bgcolor=COLORS['morado_oscuro'],
        font=dict(color=COLORS['blanco']),
        legend=dict(
            font=dict(size=11, color=COLORS['blanco']),
            bgcolor=COLORS['morado_medio'],
            bordercolor=COLORS['morado_claro']
        ),
        height=420,
        margin=dict(l=40, r=40, t=40, b=40),
    )
    st.plotly_chart(fig_r, use_container_width=True)

    st.markdown(f"<h4 style='color:{COLORS['pastel_cyan']}; margin-top:10px;'>Scores detallados</h4>", unsafe_allow_html=True)
    cols_asp = [c for c in ASPECTOS if c in top5.columns]
    tabla = top5[['name', 'rating', 'score'] + cols_asp].copy()
    tabla['score'] = (tabla['score'] * 100).round(1)
    tabla = tabla.rename(columns={
        'name':           'Restaurante',
        'rating':         'Rating',
        'score':          'Match %',
        'comida_score':   'Comida',
        'servicio_score': 'Servicio',
        'precio_score':   'Precio',
        'ambiente_score': 'Ambiente',
    })
    st.dataframe(tabla, use_container_width=True, hide_index=True)


def _render_insights(top_df, top_n):
    """Renderiza las tarjetas de insights de la selección."""
    st.markdown("---")
    st.markdown(f"<h4 style='color:{COLORS['pastel_cyan']};'>Insights de tu Selección</h4>", unsafe_allow_html=True)
    mejor = top_df.iloc[0]
    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        compat = int(mejor['score'] * 100) if pd.notna(mejor['score']) else 0
        st.markdown(f"""
        <div style="background:{COLORS['morado_medio']};border:1px solid {COLORS['morado_claro']};
                    border-radius:10px;padding:15px;text-align:center;">
            <div style="color:{COLORS['pastel_cyan']};font-weight:bold;font-size:13px;">Mejor Match</div>
            <div style="color:{COLORS['blanco']};font-size:15px;margin-top:4px;">{mejor['name']}</div>
            <div style="color:{COLORS['gris_claro']};font-size:12px;">{compat}% compatibilidad</div>
        </div>""", unsafe_allow_html=True)
    with col_i2:
        avg_r = top_df['rating'].mean()
        st.markdown(f"""
        <div style="background:{COLORS['morado_medio']};border:1px solid {COLORS['morado_claro']};
                    border-radius:10px;padding:15px;text-align:center;">
            <div style="color:{COLORS['pastel_cyan']};font-weight:bold;font-size:13px;">Rating Promedio Top</div>
            <div style="color:{COLORS['blanco']};font-size:22px;margin-top:4px;">{avg_r:.2f}</div>
            <div style="color:{COLORS['gris_claro']};font-size:12px;">de los {top_n} recomendados</div>
        </div>""", unsafe_allow_html=True)
    with col_i3:
        pct_pos = (top_df['sentimiento'].isin(['Muy positivo', 'Positivo'])).mean() * 100
        st.markdown(f"""
        <div style="background:{COLORS['morado_medio']};border:1px solid {COLORS['morado_claro']};
                    border-radius:10px;padding:15px;text-align:center;">
            <div style="color:{COLORS['pastel_cyan']};font-weight:bold;font-size:13px;">Sentimiento Positivo</div>
            <div style="color:{COLORS['blanco']};font-size:22px;margin-top:4px;">{pct_pos:.0f}%</div>
            <div style="color:{COLORS['gris_claro']};font-size:12px;">de los recomendados</div>
        </div>""", unsafe_allow_html=True)


def tab_recomendaciones(df_filtered, df):
    """Renderiza la pestaña de recomendaciones personalizadas."""
    st.markdown(f"<h2 style='color:{COLORS['pastel_cyan']};'>Sistema de Recomendación</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{COLORS['gris_claro']}; margin-top:-10px;'>Dinos qué buscas y encontraremos los restaurantes que mejor se adaptan a ti.</p>", unsafe_allow_html=True)

    if len(df) == 0:
        return

    st.markdown("---")
    st.markdown(f"<h4 style='color:{COLORS['pastel_cyan']};'>Tus Preferencias</h4>", unsafe_allow_html=True)

    col_pref1, col_pref2, col_pref3 = st.columns(3)
    tipos_disp = sorted([t for t in df['tipo_comida'].dropna().unique()])
    zonas_disp = sorted([z for z in df['zona_cat'].dropna().unique()])
    precios_disp = sorted([p for p in df['rango_precio'].dropna().unique()])

    with col_pref1:
        tipo_pref = st.selectbox("Tipo de comida", ["Sin preferencia"] + tipos_disp)
    with col_pref2:
        zona_pref = st.selectbox("Zona", ["Sin preferencia"] + zonas_disp)
    with col_pref3:
        precio_pref = st.selectbox("Rango de precio", ["Sin preferencia"] + precios_disp)

    col_n, _ = st.columns([1, 3])
    with col_n:
        top_n = st.selectbox("Número de recomendaciones", [5, 10, 15, 20], index=0)

    st.markdown("---")

    # Aplicar preferencias como filtros duros sobre el conjunto filtrado.
    base = df_filtered if len(df_filtered) >= 3 else df
    rec, filtros_aplicados, se_relajo = _aplicar_preferencias(base, tipo_pref, zona_pref, precio_pref)

    if se_relajo and filtros_aplicados:
        st.info(f"No hay resultados con todos los filtros. Mostrando con: {' · '.join(filtros_aplicados)}")

    if len(rec) == 0:
        st.warning("No hay restaurantes que coincidan con tus preferencias.")
        return

    if filtros_aplicados:
        st.success(f"Filtrando por: {' · '.join(filtros_aplicados)} → **{len(rec)} restaurantes**")

    rec = _calcular_scores(rec.copy())
    top_df = rec.nlargest(top_n, 'score').reset_index(drop=True)

    st.markdown(f"<h4 style='color:{COLORS['pastel_cyan']};'>Top {top_n} Restaurantes Recomendados</h4>", unsafe_allow_html=True)

    col_lista, col_radar = st.columns([3, 2])
    with col_lista:
        _render_lista(top_df)
    with col_radar:
        _render_radar(top_df)

    _render_insights(top_df, top_n)
