# ============================================================================
# PANAMA RESTAURANTS ANALYTICS - VERSIÓN 2
# ============================================================================

import streamlit as st
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from config_v2 import CSS_CUSTOM, COLORS
from data_loader_v2 import load_data, crear_columnas_calculadas, aplicar_filtros, obtener_opciones_filtros
from tab_01_historia_v2 import tab_historia_general
from tab_02_calidad_v2 import tab_calidad_popularidad
from tab_03_zonas_v2 import tab_zonas_tipos
from tab_04_sentimiento_v2 import tab_sentimiento
from tab_05_clusters_v2 import tab_clusters
from tab_06_exploracion_v2 import tab_exploracion
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================

st.set_page_config(
    page_title="🍽️ Panama Restaurants Analytics",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CSS_CUSTOM, unsafe_allow_html=True)

# ============================================================================
# CARGAR Y PROCESAR DATOS
# ============================================================================

df = load_data()
df = crear_columnas_calculadas(df)
opciones_filtros = obtener_opciones_filtros(df)

# ============================================================================
# BARRA LATERAL - FILTROS GLOBALES
# ============================================================================

st.sidebar.markdown(f"<h2 style='color: {COLORS['pastel_cyan']};'>🔍 Filtros Globales</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

tipo_comida_seleccionado = st.sidebar.multiselect(
    "🍴 Tipo de Comida",
    options=["Todos"] + opciones_filtros['tipos_comida'],
    default="Todos",
    help="Selecciona uno o más tipos de comida"
)

rango_precio_seleccionado = st.sidebar.multiselect(
    "💰 Rango de Precio",
    options=["Todos"] + opciones_filtros['rangos_precio'],
    default="Todos",
    help="Selecciona uno o más rangos de precio"
)

zona_seleccionada = st.sidebar.multiselect(
    "📍 Zona",
    options=["Todas"] + opciones_filtros['zonas'],
    default="Todas",
    help="Selecciona una o más zonas"
)

calificacion_seleccionada = st.sidebar.multiselect(
    "⭐ Calificación",
    options=["Todas"] + opciones_filtros['calificaciones'],
    default="Todas",
    help="Selecciona una o más categorías de calificación"
)

sentimiento_seleccionado = st.sidebar.multiselect(
    "💭 Sentimiento",
    options=["Todos"] + opciones_filtros['sentimientos'],
    default="Todos",
    help="Selecciona uno o más sentimientos"
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
    sentimiento_seleccionado if "Todos" not in sentimiento_seleccionado else None
)

restaurantes_filtrados = len(df_filtered)

# ============================================================================
# TÍTULO PRINCIPAL
# ============================================================================

st.markdown(f"""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: {COLORS['blanco']};">🍽️ Panama Restaurants Analytics</h1>
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
    "📌 Historia General",
    "📊 Calidad vs Popularidad",
    "📍 Zonas y Tipos de Comida",
    "💭 Sentimiento y Experiencia",
    "🎯 Clusters",
    "🔎 Exploración Detallada",
    "🎯 Recomendaciones"
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
    st.markdown(f"<h2 style='color:{COLORS['pastel_cyan']};'>🎯 Sistema de Recomendación</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{COLORS['gris_claro']}; margin-top:-10px;'>Dinos qué buscas y encontraremos los restaurantes que mejor se adaptan a ti.</p>", unsafe_allow_html=True)

    if len(df) > 0:
        st.markdown("---")
        st.markdown(f"<h4 style='color:{COLORS['pastel_cyan']};'>⚙️ Tus Preferencias</h4>", unsafe_allow_html=True)

        col_pref1, col_pref2, col_pref3 = st.columns(3)
        tipos_disp   = sorted([t for t in df['tipo_comida'].dropna().unique()])
        zonas_disp   = sorted([z for z in df['zona_cat'].dropna().unique()])
        precios_disp = sorted([p for p in df['rango_precio'].dropna().unique()])

        with col_pref1:
            tipo_pref = st.selectbox("🍴 Tipo de comida", ["Sin preferencia"] + tipos_disp)
        with col_pref2:
            zona_pref = st.selectbox("📍 Zona", ["Sin preferencia"] + zonas_disp)
        with col_pref3:
            precio_pref = st.selectbox("💰 Rango de precio", ["Sin preferencia"] + precios_disp)

        col_n, _ = st.columns([1, 3])
        with col_n:
            top_n = st.selectbox("🔢 Número de recomendaciones", [5, 10, 15, 20], index=0)

        pesos = {'comida': 0.40, 'servicio': 0.25, 'precio': 0.20, 'ambiente': 0.15}

        st.markdown("---")

        if True:

            # ----------------------------------------------------------------
            # Aplicar preferencias como filtros duros sobre df_filtered
            # ----------------------------------------------------------------
            base = df_filtered if len(df_filtered) >= 3 else df
            rec  = base.copy()
            filtros_aplicados = []

            if tipo_pref != "Sin preferencia":
                rec = rec[rec['tipo_comida'] == tipo_pref]
                filtros_aplicados.append(f"Tipo: {tipo_pref}")
            if zona_pref != "Sin preferencia":
                rec = rec[rec['zona_cat'] == zona_pref]
                filtros_aplicados.append(f"Zona: {zona_pref}")
            if precio_pref != "Sin preferencia":
                rec = rec[rec['rango_precio'] == precio_pref]
                filtros_aplicados.append(f"Precio: {precio_pref}")

            # Sin resultados: relajar filtros uno a uno, manteniendo el más importante (tipo)
            if len(rec) == 0 and len(filtros_aplicados) > 1:
                rec = base.copy()
                filtros_aplicados = []
                if tipo_pref != "Sin preferencia":
                    tmp = rec[rec['tipo_comida'] == tipo_pref]
                    if len(tmp) > 0:
                        rec = tmp
                        filtros_aplicados.append(f"Tipo: {tipo_pref}")
                if zona_pref != "Sin preferencia" and len(filtros_aplicados) > 0:
                    tmp = rec[rec['zona_cat'] == zona_pref]
                    if len(tmp) > 0:
                        rec = tmp
                        filtros_aplicados.append(f"Zona: {zona_pref}")
                if precio_pref != "Sin preferencia" and len(filtros_aplicados) > 0:
                    tmp = rec[rec['rango_precio'] == precio_pref]
                    if len(tmp) > 0:
                        rec = tmp
                        filtros_aplicados.append(f"Precio: {precio_pref}")
                if len(filtros_aplicados) > 0:
                    st.info(f"ℹ️ No hay resultados con todos los filtros. Mostrando con: {' · '.join(filtros_aplicados)}")

            if len(rec) == 0:
                st.warning("No hay restaurantes que coincidan con tus preferencias.")
            else:
                if filtros_aplicados:
                    st.success(f"✅ Filtrando por: {' · '.join(filtros_aplicados)} → **{len(rec)} restaurantes**")

                rec = rec.copy()

                def _norm(s):
                    rng = s.max() - s.min()
                    return (s - s.min()) / rng if rng > 0 else s * 0 + 0.5

                rec['_r']  = _norm(rec['rating'])
                rec['_rv'] = _norm(np.log1p(rec['total_reviews']))
                _sent_map  = {'Muy positivo': 1.0, 'Positivo': 0.75, 'Neutral': 0.5, 'Negativo': 0.25}
                rec['_s']  = rec['sentimiento'].map(_sent_map).fillna(0.5)

                for asp in ['comida_score', 'servicio_score', 'precio_score', 'ambiente_score']:
                    if asp in rec.columns:
                        med = rec[asp].median()
                        med = 0 if pd.isna(med) else med
                        rec[f'_n_{asp}'] = _norm(rec[asp].fillna(med))
                    else:
                        rec[f'_n_{asp}'] = 0.5

                rec['_asp'] = (
                    pesos['comida']   * rec['_n_comida_score'] +
                    pesos['servicio'] * rec['_n_servicio_score'] +
                    pesos['precio']   * rec['_n_precio_score'] +
                    pesos['ambiente'] * rec['_n_ambiente_score']
                )
                rec['score'] = (
                    0.35 * rec['_r'] +
                    0.30 * rec['_asp'] +
                    0.20 * rec['_s'] +
                    0.15 * rec['_rv']
                ).fillna(rec['rating'] / 5.0).clip(0, 1)

                top_df = rec.nlargest(top_n, 'score').reset_index(drop=True)

                st.markdown(f"<h4 style='color:{COLORS['pastel_cyan']};'>🏆 Top {top_n} Restaurantes Recomendados</h4>", unsafe_allow_html=True)

                col_lista, col_radar = st.columns([3, 2])
                colores_rank = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32"}
                sent_colors  = {
                    'Muy positivo': '#22c55e',
                    'Positivo':     '#86efac',
                    'Neutral':      '#facc15',
                    'Negativo':     '#f87171',
                }

                def badge(txt, bg):
                    return (
                        f"<span style='background:{bg};color:#fff;padding:3px 10px;"
                        f"border-radius:12px;font-size:12px;font-weight:bold;"
                        f"margin-right:4px;'>{txt}</span>"
                    )

                with col_lista:
                    for i, (_, row) in enumerate(top_df.iterrows(), start=1):
                        c_rank  = colores_rank.get(i, COLORS['pastel_cyan'])
                        s_col   = sent_colors.get(row.get('sentimiento', ''), COLORS['morado_claro'])
                        aspecto = row.get('aspecto_fuerte', 'N/A')
                        aspecto = aspecto.capitalize() if pd.notna(aspecto) else 'N/A'
                        score_val = row['score'] if pd.notna(row['score']) else 0.0
                        barra   = int(score_val * 100)
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
                                    ⭐ {row['rating']:.1f}
                                    <span style="font-size:12px;color:{COLORS['gris_claro']};">
                                        ({int(row['total_reviews']) if pd.notna(row['total_reviews']) else 0:,} reseñas)
                                    </span>
                                </span>
                            </div>
                            <div style="margin-bottom:8px;">
                                {badge(row.get('tipo_comida','N/A'), COLORS['morado_claro'])}
                                {badge(row.get('zona_cat','N/A'), '#3b3769')}
                                {badge(row.get('rango_precio','N/A'), '#4a3f8c')}
                                {badge(row.get('sentimiento','N/A'), s_col)}
                                {badge('✨ ' + aspecto, '#2e2b56')}
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

                with col_radar:
                    st.markdown(f"<h4 style='color:{COLORS['pastel_cyan']};'>📡 Perfil del Top 5</h4>", unsafe_allow_html=True)
                    top5     = top_df.head(5)
                    cats     = ['Comida', 'Servicio', 'Precio', 'Ambiente', 'Rating']
                    col_map  = {
                        'Comida':   'comida_score',
                        'Servicio': 'servicio_score',
                        'Precio':   'precio_score',
                        'Ambiente': 'ambiente_score',
                        'Rating':   'rating',
                    }
                    fig_r    = go.Figure()
                    paleta_r = ['#a689f7', '#f7c3ff', '#6357a0', '#c4b5fd', '#ddd6fe']

                    for idx, (_, rest) in enumerate(top5.iterrows()):
                        vals = []
                        for cat, col_r in col_map.items():
                            v = rest.get(col_r, 0) if pd.notna(rest.get(col_r, 0)) else 0
                            vals.append(round((v / 5.0) * 10 if cat == 'Rating' else v, 2))
                        fig_r.add_trace(go.Scatterpolar(
                            r=vals + [vals[0]],
                            theta=cats + [cats[0]],
                            fill='toself',
                            name=rest['name'][:22] + ('…' if len(rest['name']) > 22 else ''),
                            line=dict(color=paleta_r[idx % 5], width=2),
                            fillcolor=paleta_r[idx % 5],
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

                    st.markdown(f"<h4 style='color:{COLORS['pastel_cyan']}; margin-top:10px;'>📊 Scores detallados</h4>", unsafe_allow_html=True)
                    cols_asp = [c for c in ['comida_score', 'servicio_score', 'precio_score', 'ambiente_score'] if c in top5.columns]
                    tabla = top5[['name', 'rating', 'score'] + cols_asp].copy()
                    tabla['score'] = (tabla['score'] * 100).round(1)
                    tabla = tabla.rename(columns={
                        'name':          'Restaurante',
                        'rating':        '⭐ Rating',
                        'score':         '🎯 Match %',
                        'comida_score':  '🍽️ Comida',
                        'servicio_score':'🤝 Servicio',
                        'precio_score':  '💵 Precio',
                        'ambiente_score':'🌆 Ambiente',
                    })
                    st.dataframe(tabla, use_container_width=True, hide_index=True)

                # Insights
                st.markdown("---")
                st.markdown(f"<h4 style='color:{COLORS['pastel_cyan']};'>💡 Insights de tu Selección</h4>", unsafe_allow_html=True)
                mejor = top_df.iloc[0]
                col_i1, col_i2, col_i3 = st.columns(3)
                with col_i1:
                    st.markdown(f"""
                    <div style="background:{COLORS['morado_medio']};border:1px solid {COLORS['morado_claro']};
                                border-radius:10px;padding:15px;text-align:center;">
                        <div style="font-size:28px;">🥇</div>
                        <div style="color:{COLORS['pastel_cyan']};font-weight:bold;font-size:13px;">Mejor Match</div>
                        <div style="color:{COLORS['blanco']};font-size:15px;margin-top:4px;">{mejor['name']}</div>
                        <div style="color:{COLORS['gris_claro']};font-size:12px;">{int(mejor['score']*100) if pd.notna(mejor['score']) else 0}% compatibilidad</div>
                    </div>""", unsafe_allow_html=True)
                with col_i2:
                    avg_r = top_df['rating'].mean()
                    st.markdown(f"""
                    <div style="background:{COLORS['morado_medio']};border:1px solid {COLORS['morado_claro']};
                                border-radius:10px;padding:15px;text-align:center;">
                        <div style="font-size:28px;">⭐</div>
                        <div style="color:{COLORS['pastel_cyan']};font-weight:bold;font-size:13px;">Rating Promedio Top</div>
                        <div style="color:{COLORS['blanco']};font-size:22px;margin-top:4px;">{avg_r:.2f}</div>
                        <div style="color:{COLORS['gris_claro']};font-size:12px;">de los {top_n} recomendados</div>
                    </div>""", unsafe_allow_html=True)
                with col_i3:
                    pct_pos = (top_df['sentimiento'].isin(['Muy positivo', 'Positivo'])).mean() * 100
                    st.markdown(f"""
                    <div style="background:{COLORS['morado_medio']};border:1px solid {COLORS['morado_claro']};
                                border-radius:10px;padding:15px;text-align:center;">
                        <div style="font-size:28px;">😊</div>
                        <div style="color:{COLORS['pastel_cyan']};font-weight:bold;font-size:13px;">Sentimiento Positivo</div>
                        <div style="color:{COLORS['blanco']};font-size:22px;margin-top:4px;">{pct_pos:.0f}%</div>
                        <div style="color:{COLORS['gris_claro']};font-size:12px;">de los recomendados</div>
                    </div>""", unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; color: {COLORS['pastel_cyan']}; font-size: 12px;">
    <p>🍽️ Dashboard de Análisis de Restaurantes de Panamá |
    Datos actualizados |
    Filtros dinámicos habilitados</p>
    </div>
""", unsafe_allow_html=True)
