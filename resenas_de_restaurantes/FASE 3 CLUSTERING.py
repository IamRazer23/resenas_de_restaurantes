# -*- coding: utf-8 -*-
"""
Fase 3 - Clustering de Restaurantes (K-Means)
Proyecto: Plataforma de Análisis de Reseñas de Restaurantes en Panamá
Encoding: UTF-8 con BOM (utf-8-sig) para compatibilidad con tildes y caracteres especiales
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# 1. CARGA DE DATOS  (csv corregido con tildes)
# ─────────────────────────────────────────────
df = pd.read_csv('panama_restaurants_fixed.csv', encoding='utf-8-sig')
print(f"✅ Dataset cargado: {df.shape[0]} restaurantes, {df.shape[1]} columnas")

# ─────────────────────────────────────────────
# 2. MAPEO DE CATEGORÍAS  (Fase 3)
# ─────────────────────────────────────────────

# ── 2a. TIPO DE COMIDA ──────────────────────────────────────────────
tipo_comida_map = {
    # Panameña
    'panamanian_restaurant':    'Panameña',
    # Italiana
    'italian_restaurant':       'Italiana',
    'pizza_restaurant':         'Italiana',
    # Japonesa
    'japanese_restaurant':      'Japonesa',
    'sushi_restaurant':         'Japonesa',
    # China
    'chinese_restaurant':       'China',
    'hot_pot_restaurant':       'China',
    # Mexicana
    'mexican_restaurant':       'Mexicana',
    # Colombiana
    'colombian_restaurant':     'Colombiana',
    # Alemana
    'german_restaurant':        'Alemana',
    # Americana / BBQ / Grill
    'american_restaurant':      'Americana',
    'barbecue_restaurant':      'Americana',
    'bar_and_grill':            'Americana',
    'chicken_restaurant':       'Americana',
    # Mariscos
    'seafood_restaurant':       'Mariscos',
    # Brasileña (fusión latinoamericana)
    'brazilian_restaurant':     'Fusión',
    # Fusión
    'asian_fusion_restaurant':  'Fusión',
    'asian_restaurant':         'Fusión',
    'french_restaurant':        'Fusión',
    'restaurant':               'Fusión',
    # Cafetería / Panadería
    'cafe':                     'Cafetería',
    'coffee_shop':              'Cafetería',
    'bakery':                   'Cafetería',
    'cake_shop':                'Cafetería',
    'pastry_shop':              'Cafetería',
    # Fast Food
    'fast_food_restaurant':     'Fast Food',
    'meal_takeaway':            'Fast Food',
    'meal_delivery':            'Fast Food',
    # Cervecería
    'brewpub':                  'Americana',
    'cocktail_bar':             'Fusión',
    'bar':                      'Fusión',
}

df['tipo_comida'] = df['primary_type'].map(tipo_comida_map).fillna('Fusión')

# ── 2b. RANGO DE PRECIO ─────────────────────────────────────────────
precio_map = {
    'Económico ($)':  'Económico ($)',
    'Moderado ($$)':  'Medio ($$)',
    'Caro ($$$)':     'Alto ($$$)',
    'Desconocido':    'Medio ($$)',
}
df['rango_precio'] = df['price_level'].map(precio_map).fillna('Medio ($$)')

# ── 2c. ZONA ────────────────────────────────────────────────────────
zona_map = {
    'Costa del Este Centro': 'Costa del Este',
    'Casco Antiguo':         'Casco Viejo',
    'Albrook Mall area':     'Albrook',
    'Vía España':            'Vía Argentina',
    'Multiplaza / Chanis':   'Marbella',
    'Punta Pacífica':        'San Francisco',
    'Paitilla':              'San Francisco',
    'Balboa':                'Albrook',
    'El Dorado':             'Albrook',
    'Marbella':              'Marbella',
    'El Cangrejo':           'El Cangrejo',
    'Obarrio':               'Obarrio',
    'Bella Vista':           'Bella Vista',
    'San Francisco':         'San Francisco',
}
df['zona_cat'] = df['zone'].map(zona_map).fillna(df['zone'])

# ── 2d. CALIFICACIÓN ────────────────────────────────────────────────
def categorizar_rating(r):
    if r >= 4.5:   return 'Excelente (4.5-5.0)'
    elif r >= 4.0: return 'Muy bueno (4.0-4.4)'
    elif r >= 3.5: return 'Bueno (3.5-3.9)'
    else:          return 'Regular (<3.5)'

df['calificacion_cat'] = df['rating'].apply(categorizar_rating)

# ── 2e. SENTIMIENTO (proxy por rating hasta tener Fase 2) ──────────
def sentimiento_desde_rating(r):
    if r >= 4.5:   return 'Muy positivo'
    elif r >= 4.0: return 'Positivo'
    elif r >= 3.5: return 'Neutral'
    else:          return 'Negativo'

df['sentimiento'] = df['rating'].apply(sentimiento_desde_rating)

print("\n📊 Distribución de categorías:")
print("  Tipos de comida:\n  ", df['tipo_comida'].value_counts().to_dict())
print("  Rangos de precio:\n  ", df['rango_precio'].value_counts().to_dict())
print("  Zonas:\n  ", df['zona_cat'].value_counts().to_dict())
print("  Calificaciones:\n  ", df['calificacion_cat'].value_counts().to_dict())
print("  Sentimientos:\n  ", df['sentimiento'].value_counts().to_dict())

# ─────────────────────────────────────────────
# 3. ENCODING Y FEATURES PARA K-MEANS
# ─────────────────────────────────────────────
le = LabelEncoder()
features = pd.DataFrame()

features['tipo_comida_enc']   = le.fit_transform(df['tipo_comida'])
features['rango_precio_enc']  = le.fit_transform(df['rango_precio'])
features['zona_enc']          = le.fit_transform(df['zona_cat'])
features['calificacion_enc']  = le.fit_transform(df['calificacion_cat'])
features['sentimiento_enc']   = le.fit_transform(df['sentimiento'])
features['rating']            = df['rating']
features['total_reviews_log'] = np.log1p(df['total_reviews'])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)

# ─────────────────────────────────────────────
# 4. MÉTODO DEL CODO
# ─────────────────────────────────────────────
inertias = []
K_range = range(2, 12)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)

# ─────────────────────────────────────────────
# 5. K-MEANS FINAL (K=5)
# ─────────────────────────────────────────────
K_OPTIMO = 5
kmeans = KMeans(n_clusters=K_OPTIMO, random_state=42, n_init=10)
df['cluster'] = kmeans.fit_predict(X_scaled)

print(f"\n✅ K-Means ejecutado con K={K_OPTIMO}")
print(f"   Distribución: {df['cluster'].value_counts().sort_index().to_dict()}")

cluster_labels = {}
for c in range(K_OPTIMO):
    sub = df[df['cluster'] == c]
    tipo_dom   = sub['tipo_comida'].mode()[0]
    precio_dom = sub['rango_precio'].mode()[0]
    zona_dom   = sub['zona_cat'].mode()[0]
    rating_avg = sub['rating'].mean()
    cluster_labels[c] = f"C{c}: {tipo_dom} | {precio_dom} | {zona_dom} | ★{rating_avg:.1f}"

df['cluster_label'] = df['cluster'].map(cluster_labels)

print("\n📌 Perfil de cada cluster:")
for c, label in cluster_labels.items():
    print(f"   {label}  (n={len(df[df['cluster']==c])})")

# ─────────────────────────────────────────────
# 6. VISUALIZACIONES
# ─────────────────────────────────────────────
COLORS = ['#E63946', '#457B9D', '#2A9D8F', '#F4A261', '#6A0572']

fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle('Fase 3 – Clustering de Restaurantes en Panamá (K-Means)',
             fontsize=15, fontweight='bold', y=0.98)

# Plot 1: Elbow
ax = axes[0, 0]
ax.plot(list(K_range), inertias, 'o-', color='#457B9D', linewidth=2, markersize=7)
ax.axvline(x=K_OPTIMO, color='#E63946', linestyle='--', label=f'K = {K_OPTIMO}')
ax.set_xlabel('Número de clusters (K)')
ax.set_ylabel('Inercia')
ax.set_title('Método del Codo')
ax.legend(); ax.grid(alpha=0.3)

# Plot 2: PCA 2D
ax = axes[0, 1]
pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_scaled)
for c in range(K_OPTIMO):
    mask = df['cluster'] == c
    ax.scatter(X_pca[mask, 0], X_pca[mask, 1],
               c=COLORS[c], label=f'Cluster {c}',
               alpha=0.75, s=60, edgecolors='white', linewidths=0.4)
ax.set_title(f'Clusters en PCA 2D\n(varianza: {sum(pca.explained_variance_ratio_)*100:.1f}%)')
ax.set_xlabel('PC1'); ax.set_ylabel('PC2')
ax.legend(fontsize=8); ax.grid(alpha=0.2)

# Plot 3: Tamaño de clusters
ax = axes[0, 2]
counts = df['cluster'].value_counts().sort_index()
bars = ax.bar([f'C{c}' for c in counts.index], counts.values, color=COLORS, edgecolor='white')
ax.bar_label(bars, fmt='%d', padding=3, fontsize=10)
ax.set_title('Tamaño de cada Cluster')
ax.set_xlabel('Cluster'); ax.set_ylabel('Restaurantes')
ax.grid(axis='y', alpha=0.3)

# Plot 4: Tipo de comida por cluster
ax = axes[1, 0]
ct = pd.crosstab(df['cluster'], df['tipo_comida'])
ct.plot(kind='bar', ax=ax, colormap='Set2', edgecolor='white')
ax.set_title('Tipo de Comida por Cluster')
ax.set_xlabel('Cluster'); ax.set_ylabel('Cantidad')
ax.legend(fontsize=7, bbox_to_anchor=(1.01, 1))
ax.tick_params(axis='x', rotation=0); ax.grid(axis='y', alpha=0.3)

# Plot 5: Rating promedio por cluster
ax = axes[1, 1]
rating_means = df.groupby('cluster')['rating'].mean()
bars2 = ax.bar([f'C{c}' for c in rating_means.index], rating_means.values,
               color=COLORS, edgecolor='white')
ax.bar_label(bars2, fmt='%.2f', padding=3, fontsize=10)
ax.set_ylim(3.0, 5.2)
ax.set_title('Rating Promedio por Cluster')
ax.set_xlabel('Cluster'); ax.set_ylabel('Rating promedio')
global_avg = df['rating'].mean()
ax.axhline(y=global_avg, color='gray', linestyle='--', alpha=0.7,
           label=f'Media global ({global_avg:.2f})')
ax.legend(fontsize=9); ax.grid(axis='y', alpha=0.3)

# Plot 6: Heatmap zona × cluster
ax = axes[1, 2]
ct_zona = pd.crosstab(df['cluster'], df['zona_cat'])
sns.heatmap(ct_zona, ax=ax, cmap='YlOrRd', annot=True, fmt='d',
            linewidths=0.5, cbar_kws={'label': 'Restaurantes'})
ax.set_title('Distribución de Zonas por Cluster')
ax.set_xlabel('Zona'); ax.set_ylabel('Cluster')
ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('fase3_clustering_resultados.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n📊 Gráficas guardadas: fase3_clustering_resultados.png")

# ─────────────────────────────────────────────
# 7. EXPORTAR CSV FINAL  (utf-8-sig = tildes OK)
# ─────────────────────────────────────────────
output_cols = [
    'place_id', 'name', 'zone', 'zona_cat', 'rating', 'total_reviews',
    'price_level', 'rango_precio', 'primary_type', 'tipo_comida',
    'calificacion_cat', 'sentimiento', 'cluster', 'cluster_label'
]
df[output_cols].to_csv('panama_restaurants_clustered.csv',
                       index=False, encoding='utf-8-sig')
print("💾 CSV exportado: panama_restaurants_clustered.csv  (encoding: utf-8-sig)")

# ─────────────────────────────────────────────
# 8. RESUMEN FINAL
# ─────────────────────────────────────────────
print("\n" + "="*70)
print("RESUMEN FINAL DE CLUSTERS")
print("="*70)
for c in range(K_OPTIMO):
    sub = df[df['cluster'] == c]
    print(f"\n🔵 CLUSTER {c}  ({len(sub)} restaurantes)")
    print(f"   Rating promedio : {sub['rating'].mean():.2f}")
    print(f"   Tipo comida top : {sub['tipo_comida'].value_counts().head(3).to_dict()}")
    print(f"   Precio top      : {sub['rango_precio'].value_counts().head(2).to_dict()}")
    print(f"   Zona top        : {sub['zona_cat'].value_counts().head(3).to_dict()}")
    print(f"   Sentimiento     : {sub['sentimiento'].value_counts().head(2).to_dict()}")
    print(f"   Ejemplos        : {sub['name'].head(3).tolist()}")
