# ============================================================================
# CONFIGURACIÓN DE COLORES Y TEMA - v2
# ============================================================================

COLORS = {
    "morado_oscuro": "#04001a",
    "morado_medio": "#2e2b56",
    "morado_claro": "#6357a0",
    "pastel_cyan": "#a689f7",
    "pastel_rosa": "#f7c3ff",
    "pastel_verde": "#a689f7",
    "pastel_amarillo": "#f7c3ff",
    "pastel_lila": "#a689f7",
    "pastel_naranja": "#a689f7",
    
    "blanco": "#ffffff",
    "gris_claro": "#e8e8e8",
    "gris_medio": "#b0b0b0",
    "gris_oscuro": "#333333",
    "negro": "#000000"
}

MORADO_OSCURO = COLORS["morado_oscuro"]
MORADO_MEDIO = COLORS["morado_medio"]
MORADO_CLARO = COLORS["morado_claro"]
BLANCO = COLORS["blanco"]
GRIS_CLARO = COLORS["gris_claro"]

CSS_CUSTOM = f"""
    <style>
    body, .main {{
        background-color: {MORADO_OSCURO} !important;
        color: {BLANCO} !important;
    }}
    
    .stApp {{
        background-color: {MORADO_OSCURO} !important;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        padding: 15px 25px;
        font-weight: bold;
        border-radius: 8px;
        background-color: {MORADO_MEDIO};
        color: {BLANCO} !important;
        border: 2px solid {MORADO_CLARO};
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {MORADO_CLARO} !important;
        color: {BLANCO} !important;
    }}
    
    .metric-card {{
        background: linear-gradient(135deg, {MORADO_MEDIO} 0%, {MORADO_CLARO} 100%);
        padding: 20px;
        border-radius: 12px;
        border: 2px solid {MORADO_CLARO};
        box-shadow: 0 4px 6px rgba(99, 87, 160, 0.3);
        margin-bottom: 15px;
    }}
    
    .metric-card h4 {{
        color: {COLORS['pastel_cyan']};
        margin: 0;
        font-size: 14px;
        font-weight: bold;
    }}
    
    .metric-card h2 {{
        color: {BLANCO};
        margin: 5px 0;
        font-size: 24px;
    }}
    
    .metric-card p {{
        color: {GRIS_CLARO};
        margin: 0;
        font-size: 12px;
    }}
    
    .insight-card {{
        background: linear-gradient(135deg, {MORADO_MEDIO} 0%, {MORADO_CLARO} 100%);
        padding: 20px;
        border-radius: 12px;
        border: 2px solid {MORADO_CLARO};
        box-shadow: 0 4px 6px rgba(99, 87, 160, 0.3);
        margin-bottom: 15px;
    }}
    
    .insight-card h4 {{
        color: {COLORS['pastel_cyan']};
        margin: 0 0 10px 0;
        font-size: 14px;
        font-weight: bold;
    }}
    
    .insight-card p {{
        color: {BLANCO};
        margin: 0;
        font-size: 13px;
        line-height: 1.5;
    }}
    
    .insight-card b {{
        color: {COLORS['pastel_rosa']};
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {MORADO_OSCURO};
        border-right: 2px solid {MORADO_CLARO};
    }}
    
    .stSelectbox label, .stMultiselect label, .stRadio label {{
        color: {COLORS['pastel_cyan']} !important;
        font-weight: bold;
    }}
    
    .stButton > button {{
        background-color: {MORADO_CLARO};
        color: {BLANCO};
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }}
    
    .stButton > button:hover {{
        background-color: {COLORS['pastel_cyan']};
        color: {MORADO_OSCURO};
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: {BLANCO} !important;
    }}
    
    p, div {{
        color: {BLANCO} !important;
    }}
    
    .dataframe {{
        background-color: {MORADO_MEDIO} !important;
    }}
    
    .dataframe th {{
        background-color: {MORADO_CLARO} !important;
        color: {BLANCO} !important;
        font-weight: bold;
    }}
    
    .dataframe td {{
        color: {GRIS_CLARO} !important;
        background-color: {MORADO_MEDIO} !important;
    }}
    
    hr {{
        border: 1px solid {MORADO_CLARO} !important;
    }}
    
    .stWarning {{
        background-color: {MORADO_MEDIO}99 !important;
        border-left: 5px solid {COLORS['pastel_rosa']} !important;
        color: {BLANCO} !important;
    }}
    
    .stInfo {{
        background-color: {MORADO_MEDIO}99 !important;
        border-left: 5px solid {COLORS['pastel_cyan']} !important;
        color: {BLANCO} !important;
    }}
    
    .stSlider label {{
        color: {COLORS['pastel_cyan']} !important;
        font-weight: bold;
    }}
    </style>
"""
