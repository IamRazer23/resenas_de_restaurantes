import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import numpy as np

# ── Paleta ────────────────────────────────────────────────────────────────────
P_MAIN    = "#7C3AED"
P_MED     = "#A78BFA"
P_LIGHT   = "#C4B5FD"
P_PALE    = "#EDE9FE"
PINK_M    = "#EC4899"
PINK_L    = "#F9A8D4"
PINK_PALE = "#FCE7F3"
ROSE      = "#FDA4AF"
LAVENDER  = "#DDD6FE"
BG        = "#F5F3FF"

st.set_page_config(
    page_title="Restaurantes · Panamá",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background: {BG}; }}

[data-testid="stSidebar"] {{
  background: linear-gradient(175deg, #3B0764 0%, #6D28D9 55%, #A855F7 100%);
}}
[data-testid="stSidebar"] * {{ color: #EDE9FE !important; }}
[data-testid="stSidebar"] label {{ color: #C4B5FD !important; font-size:13px; font-weight:500; }}
[data-testid="stSidebar"] hr {{ border-color: rgba(196,181,253,0.3) !important; }}

.header-block {{
  background: linear-gradient(130deg, {P_MAIN} 0%, {PINK_M} 100%);
  border-radius: 20px; padding: 28px 32px; margin-bottom: 22px; color: white;
}}
.header-block h1 {{ font-size:24px; font-weight:700; margin:0 0 5px; }}
.header-block p  {{ font-size:13px; opacity:.85; margin:0; }}

.kpi {{
  background: white; border-radius: 16px;
  padding: 18px 20px; border-top: 4px solid {P_MAIN};
  box-shadow: 0 2px 10px rgba(124,58,237,.08);
}}
.kpi.k2 {{ border-top-color:{PINK_M}; }}
.kpi.k3 {{ border-top-color:{P_MED}; }}
.kpi.k4 {{ border-top-color:{ROSE}; }}
.kpi-lbl {{ font-size:11px; color:#9CA3AF; font-weight:600;
            text-transform:uppercase; letter-spacing:.06em; margin-bottom:4px; }}
.kpi-val {{ font-size:26px; font-weight:700; color:#1F1135; line-height:1.1; }}
.kpi-sub {{ font-size:11px; color:#C4B5FD; margin-top:3px; }}

.sec {{ font-size:13px; font-weight:600; color:{P_MAIN};
        border-bottom:2px solid {P_PALE}; padding-bottom:5px; margin-bottom:14px; }}

.missing {{
  background: linear-gradient(135deg, {PINK_PALE}, {P_PALE});
  border: 1.5px dashed {P_LIGHT}; border-radius:14px; padding:18px 22px;
}}
.missing b {{ color:{P_MAIN}; }}
.missing p {{ font-size:13px; color:#5B21B6; margin:6px 0 0; line-height:1.6; }}

.rev-card {{
  background:{P_PALE}; border-left:3px solid {P_MED};
  border-radius:10px; padding:10px 14px; margin:6px 0; font-size:13px;
}}
.rev-author {{ font-weight:600; color:{P_MAIN}; }}
.rev-stars  {{ color:{PINK_M}; }}
.rev-time   {{ font-size:11px; color:#9CA3AF; }}

div[data-testid="stMetric"] {{ display:none; }}
</style>
""", unsafe_allow_html=True)


# ── Datos ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    df = pd.read_csv("resenas_de_restaurantes/data/restaurantes_panama.csv")
    df["name_clean"] = df["name"].str.replace(r"\s*\|.*$", "", regex=True).str.strip()
    for c in ["comida_score","servicio_score","precio_score","ambiente_score"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # score 0-100 para mostrar
    for c, nc in [("comida_score","comida_pct"),("servicio_score","servicio_pct"),
                  ("precio_score","precio_pct"),("ambiente_score","ambiente_pct")]:
        df[nc] = ((df[c].fillna(0) + 1) / 2 * 100).round(1)
    return df

df = load()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🍽️ Restaurantes · Panamá")
    st.markdown("---")

    zonas = ["Todas"] + sorted(df["zone"].unique())
    zona_sel = st.selectbox("📍 Zona", zonas)

    tipos = ["Todos"] + sorted(df["primary_type"].dropna().unique())
    tipo_sel = st.selectbox("🍴 Tipo de local", tipos)

    precios = ["Todos"] + [x for x in ["Económico ($)","Moderado ($$)","Caro ($$$)","Desconocido"] if x in df["price_level"].values]
    precio_sel = st.selectbox("💰 Nivel de precio", precios)

    rating_min = st.slider("⭐ Rating mínimo", 3.0, 5.0, 3.5, 0.1)

    sent_opts = ["Todos","positivo","neutral","negativo"]
    sent_sel = st.selectbox("💬 Sentimiento general", sent_opts)

    st.markdown("---")
    st.markdown("**Estado del proyecto**")
    st.markdown("✅ Dataset recolectado")
    st.markdown("✅ Análisis de sentimiento")
    st.markdown("⏳ Clustering (pendiente)")
    st.markdown("⏳ Recomendador con LLM")


# ── Filtro ────────────────────────────────────────────────────────────────────
filt = df.copy()
if zona_sel   != "Todas":    filt = filt[filt["zone"]             == zona_sel]
if tipo_sel   != "Todos":    filt = filt[filt["primary_type"]     == tipo_sel]
if precio_sel != "Todos":    filt = filt[filt["price_level"]      == precio_sel]
if sent_sel   != "Todos":    filt = filt[filt["sentimiento_general"] == sent_sel]
filt = filt[filt["rating"] >= rating_min]


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-block">
  <h1>🍽️ Plataforma de Análisis de Restaurantes · Panamá</h1>
  <p>Sentimiento por aspecto · {len(filt)} locales en vista · {int(filt['total_reviews'].sum()):,} reseñas analizadas</p>
</div>""", unsafe_allow_html=True)


# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
pos_pct = (filt["sentimiento_general"]=="positivo").mean()*100
avg_food = filt["comida_pct"].mean()
avg_serv = filt["servicio_pct"].mean()

with k1:
    st.markdown(f"""<div class="kpi">
      <div class="kpi-lbl">Locales analizados</div>
      <div class="kpi-val">{len(filt)}</div>
      <div class="kpi-sub">de 187 en dataset</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi k2">
      <div class="kpi-lbl">Rating promedio</div>
      <div class="kpi-val">{filt['rating'].mean():.2f} ★</div>
      <div class="kpi-sub">escala Google 1–5</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi k3">
      <div class="kpi-lbl">Sentimiento positivo</div>
      <div class="kpi-val">{pos_pct:.0f}%</div>
      <div class="kpi-sub">de reseñas</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi k4">
      <div class="kpi-lbl">Total reseñas</div>
      <div class="kpi-val">{int(filt['total_reviews'].sum()):,}</div>
      <div class="kpi-sub">en selección</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── Fila A: Radar sentimiento + Distribución sentimiento ──────────────────────
cA1, cA2 = st.columns([1, 1])

with cA1:
    st.markdown('<div class="sec">📡 Sentimiento promedio por aspecto</div>', unsafe_allow_html=True)
    cats  = ["Comida","Servicio","Precio","Ambiente"]
    pcols = ["comida_pct","servicio_pct","precio_pct","ambiente_pct"]
    mcols = ["comida_menciones","servicio_menciones","precio_menciones","ambiente_menciones"]
    vals  = [filt[c].mean() for c in pcols]
    mvals = [filt[c].mean() for c in mcols]

    fig_r = go.Figure()
    fig_r.add_trace(go.Scatterpolar(
        r=vals+[vals[0]], theta=cats+[cats[0]],
        fill="toself", fillcolor="rgba(167,139,250,.22)",
        line=dict(color=P_MAIN, width=2.5),
        marker=dict(size=8, color=P_MAIN),
        hovertemplate="%{theta}: %{r:.1f}%<extra></extra>",
    ))
    fig_r.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,100],
                            tickfont=dict(size=10), gridcolor=LAVENDER),
            angularaxis=dict(tickfont=dict(size=13, color="#374151")),
            bgcolor="white",
        ),
        showlegend=False, height=290,
        margin=dict(l=30,r=30,t=10,b=10),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_r, use_container_width=True)

    # Menciones promedio por aspecto
    fig_men = go.Figure(go.Bar(
        x=cats, y=[round(v,1) for v in mvals],
        marker_color=[P_MAIN, PINK_M, P_MED, ROSE],
        text=[f"{v:.1f}" for v in mvals], textposition="outside",
        hovertemplate="%{x}: %{y:.1f} menciones prom.<extra></extra>",
    ))
    fig_men.update_layout(
        title=dict(text="Menciones promedio por aspecto", font=dict(size=12,color=P_MAIN), x=0),
        yaxis=dict(visible=False), xaxis=dict(tickfont=dict(size=12)),
        margin=dict(l=0,r=0,t=30,b=0), height=160,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_men, use_container_width=True)

with cA2:
    st.markdown('<div class="sec">💬 Distribución de sentimiento general</div>', unsafe_allow_html=True)
    sent_counts = filt["sentimiento_general"].value_counts().reset_index()
    sent_counts.columns = ["sentimiento","n"]
    color_sent = {"positivo": P_MAIN, "neutral": P_MED, "negativo": PINK_M}

    fig_sent = go.Figure(go.Pie(
        labels=sent_counts["sentimiento"],
        values=sent_counts["n"],
        hole=0.58,
        marker=dict(colors=[color_sent.get(s, LAVENDER) for s in sent_counts["sentimiento"]]),
        textinfo="label+percent",
        textfont=dict(size=13),
        hovertemplate="%{label}: %{value} locales (%{percent})<extra></extra>",
    ))
    fig_sent.add_annotation(
        text=f"<b>{len(filt)}</b><br><span style='font-size:10px'>locales</span>",
        x=0.5, y=0.5, showarrow=False, font=dict(size=14, color=P_MAIN),
    )
    fig_sent.update_layout(
        showlegend=True,
        legend=dict(orientation="h", y=-0.05, font=dict(size=12)),
        margin=dict(l=10,r=10,t=10,b=30), height=260,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_sent, use_container_width=True)

    st.markdown('<div class="sec" style="margin-top:10px">💰 Distribución por precio</div>', unsafe_allow_html=True)
    precio_counts = filt["price_level"].value_counts().reset_index()
    precio_counts.columns = ["nivel","n"]
    orden = ["Económico ($)","Moderado ($$)","Caro ($$$)","Desconocido"]
    precio_counts["orden"] = precio_counts["nivel"].map({v:i for i,v in enumerate(orden)})
    precio_counts = precio_counts.sort_values("orden")

    fig_precio = go.Figure(go.Bar(
        x=precio_counts["nivel"], y=precio_counts["n"],
        marker_color=[P_MAIN, P_MED, PINK_M, LAVENDER],
        text=precio_counts["n"], textposition="outside",
        hovertemplate="%{x}: %{y} locales<extra></extra>",
    ))
    fig_precio.update_layout(
        yaxis=dict(visible=False), xaxis=dict(tickfont=dict(size=11)),
        margin=dict(l=0,r=0,t=10,b=0), height=170,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_precio, use_container_width=True)


# ── Fila B: Rating por zona + Mapa ────────────────────────────────────────────
st.markdown('<div class="sec">📊 Rating y sentimiento por zona</div>', unsafe_allow_html=True)
cB1, cB2 = st.columns([1.1, 1])

with cB1:
    zona_stats = (filt.groupby("zone")
        .agg(
            rating=("rating","mean"),
            n=("name","count"),
            pos=("sentimiento_general", lambda x: (x=="positivo").mean()*100),
            comida=("comida_pct","mean"),
        ).reset_index().sort_values("rating", ascending=True))

    fig_zona = go.Figure()
    fig_zona.add_trace(go.Bar(
        name="Rating (×20)", y=zona_stats["zone"],
        x=(zona_stats["rating"]*20).round(1),
        orientation="h",
        marker_color=P_MAIN, opacity=0.85,
        hovertemplate="<b>%{y}</b><br>Rating: %{customdata:.2f}<extra></extra>",
        customdata=zona_stats["rating"],
    ))
    fig_zona.add_trace(go.Bar(
        name="% Positivo", y=zona_stats["zone"],
        x=zona_stats["pos"].round(1),
        orientation="h",
        marker_color=PINK_M, opacity=0.75,
        hovertemplate="<b>%{y}</b><br>Positivo: %{x:.0f}%<extra></extra>",
    ))
    fig_zona.update_layout(
        barmode="group",
        xaxis=dict(range=[0,110], tickfont=dict(size=10), gridcolor=P_PALE),
        yaxis=dict(tickfont=dict(size=11)),
        legend=dict(orientation="h", y=1.05, font=dict(size=11)),
        margin=dict(l=10,r=10,t=30,b=10), height=380,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_zona, use_container_width=True)

with cB2:
    st.markdown('<div class="sec">🗺️ Mapa de restaurantes</div>', unsafe_allow_html=True)
    mapa_df = filt.dropna(subset=["latitude","longitude"]).copy()
    color_sent_map = {"positivo": P_MAIN, "neutral": "#F59E0B", "negativo": PINK_M}
    mapa_df["color_sent"] = mapa_df["sentimiento_general"].map(color_sent_map)

    fig_map = px.scatter_mapbox(
        mapa_df, lat="latitude", lon="longitude",
        color="sentimiento_general",
        color_discrete_map=color_sent_map,
        hover_name="name_clean",
        hover_data={"rating":True,"zone":True,"price_level":True,
                    "latitude":False,"longitude":False},
        size_max=12, zoom=11,
        height=380,
    )
    fig_map.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat":8.994,"lon":-79.519},
        legend=dict(title="Sentimiento", font=dict(size=11), y=0.98),
        margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_map, use_container_width=True)


# ── Fila C: Scatter rating vs comida + tipos ─────────────────────────────────
cC1, cC2 = st.columns([1.3, 1])

with cC1:
    st.markdown('<div class="sec">📈 Rating vs. scores de sentimiento</div>', unsafe_allow_html=True)
    scatter_df = filt.dropna(subset=["comida_pct","servicio_pct"]).copy()
    fig_sc = px.scatter(
        scatter_df, x="comida_pct", y="servicio_pct",
        color="sentimiento_general",
        color_discrete_map={"positivo":P_MAIN,"neutral":"#F59E0B","negativo":PINK_M},
        size="rating", size_max=18,
        hover_name="name_clean",
        hover_data={"rating":True,"zone":True,"comida_pct":":.0f","servicio_pct":":.0f"},
        labels={"comida_pct":"Sentimiento Comida (%)","servicio_pct":"Sentimiento Servicio (%)"},
        height=310,
    )
    fig_sc.update_layout(
        legend=dict(title="Sentimiento", font=dict(size=11)),
        xaxis=dict(gridcolor=P_PALE, range=[0,110]),
        yaxis=dict(gridcolor=P_PALE, range=[0,110]),
        margin=dict(l=10,r=10,t=10,b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_sc, use_container_width=True)

with cC2:
    st.markdown('<div class="sec">🍴 Tipos de local</div>', unsafe_allow_html=True)
    tipo_counts = filt["primary_type"].value_counts().head(10).reset_index()
    tipo_counts.columns = ["tipo","n"]
    tipo_counts["tipo_fmt"] = tipo_counts["tipo"].str.replace("_"," ").str.title()

    fig_tipo = go.Figure(go.Bar(
        x=tipo_counts["n"], y=tipo_counts["tipo_fmt"],
        orientation="h",
        marker=dict(
            color=tipo_counts["n"],
            colorscale=[[0,LAVENDER],[0.5,P_MED],[1,P_MAIN]],
            showscale=False,
        ),
        text=tipo_counts["n"], textposition="outside",
        hovertemplate="%{y}: %{x} locales<extra></extra>",
    ))
    fig_tipo.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(tickfont=dict(size=11)),
        margin=dict(l=10,r=30,t=10,b=10), height=310,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_tipo, use_container_width=True)


# ── Banner clustering pendiente ───────────────────────────────────────────────
st.markdown(f"""
<div class="missing">
  <b>⏳ Módulo pendiente: Clustering de restaurantes</b>
  <p>En cuanto recibas el CSV de clustering, este espacio mostrará la distribución por grupos,
  el scatter PCA y la comparación de perfiles entre clusters.
  Las columnas esperadas son: <code>place_id</code> · <code>cluster_id</code> · <code>cluster_label</code></p>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── Ranking ───────────────────────────────────────────────────────────────────
st.markdown('<div class="sec">🏆 Ranking de restaurantes</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["⭐ Por Rating", "🍽️ Por Sentimiento Comida", "🤝 Por Sentimiento Servicio"])

def tabla_ranking(df_rank, sort_col, label):
    top = df_rank.sort_values(sort_col, ascending=False).head(15).reset_index(drop=True)
    rows = ""
    badge_map = {
        "positivo": f'<span style="background:#EDE9FE;color:{P_MAIN};padding:2px 9px;border-radius:20px;font-size:11px;font-weight:600">positivo</span>',
        "neutral":  '<span style="background:#FEF3C7;color:#92400E;padding:2px 9px;border-radius:20px;font-size:11px;font-weight:600">neutral</span>',
        "negativo": f'<span style="background:#FCE7F3;color:{PINK_M};padding:2px 9px;border-radius:20px;font-size:11px;font-weight:600">negativo</span>',
    }
    for i, r in top.iterrows():
        def bar(v, color=P_MAIN):
            return f'<div style="background:#F3F0FF;border-radius:4px;height:7px;width:70px;display:inline-block"><div style="background:{color};width:{int(v)}%;height:7px;border-radius:4px"></div></div>'
        rows += f"""<tr style="border-bottom:1px solid #F3F0FF">
          <td style="padding:8px 10px;font-weight:700;color:{P_MAIN}">{i+1}</td>
          <td style="padding:8px 10px"><b style="color:#1F1135">{r['name_clean']}</b></td>
          <td style="padding:8px 10px;color:#6B7280;font-size:12px">{r['zone']}</td>
          <td style="padding:8px 10px"><b style="color:{P_MAIN}">{r['rating']}</b></td>
          <td style="padding:8px 10px;font-size:12px">{r['price_level']}</td>
          <td style="padding:8px 10px">{bar(r['comida_pct'])} <span style="font-size:11px;color:#6B7280">{r['comida_pct']:.0f}%</span></td>
          <td style="padding:8px 10px">{bar(r['servicio_pct'], PINK_M)} <span style="font-size:11px;color:#6B7280">{r['servicio_pct']:.0f}%</span></td>
          <td style="padding:8px 10px">{badge_map.get(r['sentimiento_general'],'')}</td>
          <td style="padding:8px 10px;color:#9CA3AF;font-size:12px">{int(r['total_reviews']):,}</td>
        </tr>"""
    html = f"""<table style="width:100%;border-collapse:collapse;font-size:13px">
      <tr style="background:{P_PALE}">
        <th style="padding:8px 10px;color:{P_MAIN};text-align:left">#</th>
        <th style="padding:8px 10px;color:{P_MAIN};text-align:left">Nombre</th>
        <th style="padding:8px 10px;color:{P_MAIN};text-align:left">Zona</th>
        <th style="padding:8px 10px;color:{P_MAIN};text-align:left">Rating</th>
        <th style="padding:8px 10px;color:{P_MAIN};text-align:left">Precio</th>
        <th style="padding:8px 10px;color:{P_MAIN};text-align:left">Comida</th>
        <th style="padding:8px 10px;color:{P_MAIN};text-align:left">Servicio</th>
        <th style="padding:8px 10px;color:{P_MAIN};text-align:left">Sentimiento</th>
        <th style="padding:8px 10px;color:{P_MAIN};text-align:left">Reseñas</th>
      </tr>{rows}</table>"""
    st.markdown(html, unsafe_allow_html=True)

with tab1: tabla_ranking(filt, "rating", "Rating")
with tab2: tabla_ranking(filt, "comida_pct", "Comida")
with tab3: tabla_ranking(filt, "servicio_pct", "Servicio")

st.markdown("<br>", unsafe_allow_html=True)


# ── Detalle individual ────────────────────────────────────────────────────────
st.markdown('<div class="sec">🔍 Detalle de restaurante</div>', unsafe_allow_html=True)

nombres = sorted(filt["name_clean"].unique())
sel = st.selectbox("Selecciona un restaurante", nombres, key="detalle_sel")

if sel:
    row = filt[filt["name_clean"] == sel].iloc[0]

    d1, d2, d3, d4 = st.columns(4)
    for col, lbl, val, sub, cls in [
        (d1, "Rating Google",      f"{row['rating']} ★",        f"{int(row['total_reviews']):,} reseñas", ""),
        (d2, "Tipo de local",      row['primary_type'].replace("_"," ").title(), row['price_level'], " k2"),
        (d3, "Zona",               row['zone'],                  "", " k3"),
        (d4, "Sentimiento",        row['sentimiento_general'].capitalize(), "", " k4"),
    ]:
        col.markdown(f"""<div class="kpi{cls}">
          <div class="kpi-lbl">{lbl}</div>
          <div class="kpi-val" style="font-size:18px">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    r1, r2 = st.columns([1, 1.6])

    with r1:
        a_cats = ["Comida","Servicio","Precio","Ambiente"]
        a_vals = [row["comida_pct"], row["servicio_pct"], row["precio_pct"], row["ambiente_pct"]]
        a_menc = [row["comida_menciones"], row["servicio_menciones"],
                  row["precio_menciones"], row["ambiente_menciones"]]
        fig_ind = go.Figure(go.Scatterpolar(
            r=a_vals+[a_vals[0]], theta=a_cats+[a_cats[0]],
            fill="toself", fillcolor="rgba(236,72,153,.18)",
            line=dict(color=PINK_M, width=2.5),
            marker=dict(size=8, color=PINK_M),
            hovertemplate="%{theta}: %{r:.0f}%<extra></extra>",
        ))
        fig_ind.update_layout(
            polar=dict(
                radialaxis=dict(range=[0,100], tickfont=dict(size=9), gridcolor=PINK_PALE),
                angularaxis=dict(tickfont=dict(size=12)),
                bgcolor="white",
            ),
            showlegend=False, height=250,
            margin=dict(l=25,r=25,t=10,b=10),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_ind, use_container_width=True)

        # Menciones individuales
        st.markdown(f"""
        <div style="display:flex;gap:8px;flex-wrap:wrap;font-size:12px">
          {"".join(f'<span style="background:{P_PALE};color:{P_MAIN};padding:3px 10px;border-radius:20px">{c}: <b>{int(m)}</b> menc.</span>' for c, m in zip(a_cats, a_menc))}
        </div>""", unsafe_allow_html=True)

    with r2:
        if row.get("address") and str(row["address"]) != "nan":
            st.markdown(f"📍 `{row['address']}`")
        if row.get("google_maps_url") and str(row["google_maps_url"]) != "nan":
            st.markdown(f"[🗺️ Ver en Google Maps]({row['google_maps_url']})")

        if row.get("schedule") and str(row["schedule"]) != "nan":
            with st.expander("🕐 Ver horario"):
                for line in str(row["schedule"]).split(" | "):
                    st.markdown(f"• {line}")

        try:
            revs = json.loads(row["reviews_json"])
            st.markdown(f"**💬 Reseñas ({len(revs)} disponibles)**")
            for rev in revs[:3]:
                stars = "★" * int(rev.get("rating",0)) + "☆" * (5 - int(rev.get("rating",0)))
                st.markdown(f"""
                <div class="rev-card">
                  <span class="rev-author">{rev.get('author','')}</span> &nbsp;
                  <span class="rev-stars">{stars}</span> &nbsp;
                  <span class="rev-time">{rev.get('relative_time','')}</span><br>
                  <span style="color:#374151">{rev.get('text','')[:220]}{'…' if len(rev.get('text',''))>220 else ''}</span>
                </div>""", unsafe_allow_html=True)
        except Exception:
            pass