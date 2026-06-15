import csv
import json
import os
import re
import sys
import time

import pandas as pd
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ============================================================
# CONFIGURACIÓN
# ============================================================

API_KEY = os.environ.get("GROQ_API_KEY")
if not API_KEY:
    sys.exit("ERROR: Variable de entorno GROQ_API_KEY no configurada. "
             "Obtén tu key gratis en https://console.groq.com y agrégala al .env")
MODELO = "llama-3.1-8b-instant"  # free tier: 30 RPM, 14400 RPD
PAUSA = 4                          # segundos entre llamadas (~15 RPM, bajo el límite de TPM)

_DIR = os.path.dirname(os.path.abspath(__file__))
ENTRADA = os.path.join(_DIR, "Downloads", "panama_restaurants.csv")
SALIDA = os.path.join(_DIR, "panama_restaurants_sentiment.csv")
CACHE = os.path.join(_DIR, "cache_sentimiento.csv")

ASPECTOS = ["comida", "servicio", "precio", "ambiente"]
ETIQUETAS_VALIDAS = {"positivo", "negativo", "neutral", "no_mencionado"}

client = Groq(api_key=API_KEY)

SYSTEM_PROMPT = """Eres un analizador de sentimiento por aspecto para reseñas de \
restaurantes en Panamá. Analiza la reseña y determina el sentimiento para CADA \
uno de estos aspectos:

- comida: calidad, sabor, frescura, presentación de los platos
- servicio: atención, amabilidad, rapidez, trato del personal
- precio: relación calidad-precio, si es caro, barato o justo
- ambiente: lugar, decoración, limpieza, ruido, comodidad

Reglas:
- Para cada aspecto usa EXACTAMENTE una de estas etiquetas: "positivo", \
"negativo", "neutral", "no_mencionado".
- Usa "no_mencionado" si la reseña NO habla de ese aspecto. NO inventes.
- "general" es el sentimiento global: "positivo", "negativo" o "neutral".
- La reseña puede estar en inglés o español; analízala igual.
- Responde ÚNICAMENTE con un objeto JSON válido, sin texto adicional ni markdown.

Formato exacto:
{"comida": "...", "servicio": "...", "precio": "...", "ambiente": "...", "general": "..."}"""


# ============================================================
# LLAMADA AL LLM  (única parte a tocar si cambian de proveedor)
# ============================================================

def analizar_resena(texto, reintentos=3):
    """Devuelve dict con sentimiento por aspecto, o None si falla."""
    for intento in range(reintentos):
        try:
            resp = client.chat.completions.create(
                model=MODELO,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": texto},
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )
            raw = (resp.choices[0].message.content or "").strip()
            data = json.loads(raw)

            resultado = {}
            for aspecto in ASPECTOS + ["general"]:
                etq = str(data.get(aspecto, "no_mencionado")).lower().strip()
                if aspecto == "general" and etq not in {"positivo", "negativo", "neutral"}:
                    etq = "neutral"
                elif aspecto != "general" and etq not in ETIQUETAS_VALIDAS:
                    etq = "no_mencionado"
                resultado[aspecto] = etq
            return resultado
        except Exception as e:
            m = re.search(r"retry in (\d+(?:\.\d+)?)s", str(e))
            espera = int(float(m.group(1))) + 2 if m else 5 * (intento + 1)
            print(f"      reintento {intento + 1} (espero {espera}s): {e}")
            time.sleep(espera)
    return None


# ============================================================
# CACHÉ (para retomar)
# ============================================================

def cargar_cache():
    cache = {}
    if not os.path.exists(CACHE):
        return cache
    campos = ["review_key"] + ASPECTOS + ["general"]
    with open(CACHE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not all(c in (reader.fieldnames or []) for c in campos):
            print(f"  [AVISO] Cache corrupto o con formato incorrecto, se ignora.")
            return cache
        for row in reader:
            try:
                cache[row["review_key"]] = {a: row[a] for a in ASPECTOS + ["general"]}
            except KeyError:
                continue
    return cache


# ============================================================
# AGREGACIÓN POR RESTAURANTE
# ============================================================

def score_y_menciones(sent_list, aspecto):
    """score en [-1, 1] entre las reseñas que mencionan el aspecto, + nº de menciones."""
    pos = sum(1 for s in sent_list if s and s.get(aspecto) == "positivo")
    neg = sum(1 for s in sent_list if s and s.get(aspecto) == "negativo")
    neu = sum(1 for s in sent_list if s and s.get(aspecto) == "neutral")
    menciones = pos + neg + neu
    if menciones == 0:
        return "", 0
    return round((pos - neg) / menciones, 3), menciones


def general_mayoritario(sent_list):
    conteo = {"positivo": 0, "negativo": 0, "neutral": 0}
    for s in sent_list:
        if s and s.get("general") in conteo:
            conteo[s["general"]] += 1
    if sum(conteo.values()) == 0:
        return ""
    return max(conteo, key=conteo.get)


# ============================================================
# PROCESO PRINCIPAL
# ============================================================

def procesar():
    df = pd.read_csv(ENTRADA, encoding="utf-8-sig")
    print(f"Leídos {len(df)} restaurantes.")

    # 1) Aplanar todas las reseñas en (review_key, texto)
    todas = []  # (review_key, texto)
    for _, row in df.iterrows():
        rid = row["place_id"]
        try:
            revs = json.loads(row["reviews_json"]) if pd.notna(row["reviews_json"]) else []
        except (json.JSONDecodeError, TypeError):
            revs = []
        for j, rv in enumerate(revs):
            texto = (rv.get("text") or "").strip()
            if texto:
                todas.append((f"{rid}_{j}", texto))

    print(f"Total de reseñas con texto: {len(todas)}")

    # 2) Analizar las que falten (con resume vía caché)
    cache = cargar_cache()
    print(f"Ya en caché: {len(cache)}\n")

    nuevo = not os.path.exists(CACHE)
    with open(CACHE, "a", newline="", encoding="utf-8") as fcache:
        cw = csv.DictWriter(fcache, fieldnames=["review_key"] + ASPECTOS + ["general"])
        if nuevo:
            cw.writeheader()

        for i, (key, texto) in enumerate(todas, 1):
            if key in cache:
                continue
            sent = analizar_resena(texto)
            if sent is None:
                print(f"[{i}/{len(todas)}] {key} -> FALLÓ, se omite")
                continue
            fila = {"review_key": key}
            fila.update(sent)
            cw.writerow(fila)
            fcache.flush()
            cache[key] = sent
            print(f"[{i}/{len(todas)}] {key} -> {sent['general']}")
            time.sleep(PAUSA)

    # 3) Reconstruir el CSV final (formato de Luz + columnas de sentimiento)
    print("\nAgregando resultados por restaurante...")
    col_sentiment_json = []
    col_scores = {a: [] for a in ASPECTOS}
    col_menciones = {a: [] for a in ASPECTOS}
    col_general = []

    for _, row in df.iterrows():
        rid = row["place_id"]
        try:
            revs = json.loads(row["reviews_json"]) if pd.notna(row["reviews_json"]) else []
        except (json.JSONDecodeError, TypeError):
            revs = []

        sent_list = [cache.get(f"{rid}_{j}") for j in range(len(revs))]
        col_sentiment_json.append(json.dumps(sent_list, ensure_ascii=False))

        for a in ASPECTOS:
            sc, men = score_y_menciones(sent_list, a)
            col_scores[a].append(sc)
            col_menciones[a].append(men)
        col_general.append(general_mayoritario(sent_list))

    df["sentiment_json"] = col_sentiment_json
    for a in ASPECTOS:
        df[f"{a}_score"] = col_scores[a]
        df[f"{a}_menciones"] = col_menciones[a]
    df["sentimiento_general"] = col_general

    df.to_csv(SALIDA, index=False, encoding="utf-8-sig")
    print(f"\nGuardado: {SALIDA}  ({len(df)} restaurantes)")


if __name__ == "__main__":
    procesar()
