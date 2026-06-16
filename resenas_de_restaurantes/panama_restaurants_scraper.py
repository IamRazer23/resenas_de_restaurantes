import requests
import pandas as pd
import json
import time
import os
import sys
from tqdm import tqdm
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")
if not API_KEY:
    sys.exit("ERROR: Variable de entorno GOOGLE_PLACES_API_KEY no configurada. "
             "Agrégala al archivo .env")
OUTPUT_CSV = "./Downloads/panama_restaurants.csv"
OUTPUT_JSON = "./Downloads/panama_restaurants_raw.json"

# Parámetros de búsqueda
SEARCH_RADIUS_METERS = 1500       # Radio por zona (en metros)
MAX_RESULTS_PER_ZONE = 20         # Máx. lugares por petición (límite API: 20)
MIN_REVIEWS = 5                   # Filtrar lugares con al menos N reseñas
MAX_REVIEWS_PER_PLACE = 5         # Máx. reseñas a extraer por restaurante
LANGUAGE = "es"                   # Idioma de los resultados
DELAY_BETWEEN_REQUESTS = 0.3      # Segundos entre llamadas (evita rate limiting)

# ─────────────────────────────────────────────
# ZONAS DE BÚSQUEDA — Centro de Ciudad de Panamá
# Solo distritos urbanos con alta densidad de restaurantes.
# Se excluyen: Panamá Norte, La Chorrera, Arraiján,
# San Miguelito, Tocumen y áreas periféricas.
# ─────────────────────────────────────────────
SEARCH_ZONES = [
    # Casco Antiguo / San Felipe
    {"name": "Casco Antiguo",          "lat": 8.9524,  "lng": -79.5354},
    # Bella Vista / Obarrio
    {"name": "Bella Vista",            "lat": 8.9935,  "lng": -79.5185},
    {"name": "Obarrio",                "lat": 8.9980,  "lng": -79.5143},
    # Marbella / El Cangrejo
    {"name": "Marbella",               "lat": 9.0036,  "lng": -79.5132},
    {"name": "El Cangrejo",            "lat": 9.0058,  "lng": -79.5268},
    # San Francisco
    {"name": "San Francisco",          "lat": 9.0098,  "lng": -79.4965},
    # Paitilla / Punta Pacífica
    {"name": "Paitilla",               "lat": 8.9898,  "lng": -79.5074},
    {"name": "Punta Pacífica",         "lat": 8.9847,  "lng": -79.5044},
    # Balboa / Ancón
    {"name": "Balboa",                 "lat": 8.9638,  "lng": -79.5564},
    # Costa del Este (sector comercial central)
    {"name": "Costa del Este Centro",  "lat": 9.0251,  "lng": -79.4710},
    # Multiplaza / Chanis
    {"name": "Multiplaza / Chanis",    "lat": 9.0177,  "lng": -79.4833},
    # Vía España
    {"name": "Vía España",             "lat": 9.0015,  "lng": -79.5228},
    # El Dorado (zona comercial)
    {"name": "El Dorado",              "lat": 9.0342,  "lng": -79.5232},
    # Albrook / Curundú (cerca del mall)
    {"name": "Albrook Mall area",      "lat": 8.9814,  "lng": -79.5555},
]

# ─────────────────────────────────────────────
# ENDPOINTS DE LA API
# ─────────────────────────────────────────────
NEARBY_SEARCH_URL = "https://places.googleapis.com/v1/places:searchNearby"
PLACE_DETAILS_URL = "https://places.googleapis.com/v1/places/{place_id}"


# ─────────────────────────────────────────────
# FUNCIONES DE EXTRACCIÓN
# ─────────────────────────────────────────────

def nearby_search(lat: float, lng: float, radius: int) -> list[dict]:
    """
    Realiza una búsqueda de restaurantes cercanos a un punto dado
    usando la Places API (New) — Nearby Search.
    """
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.rating,"
            "places.userRatingCount,"
            "places.formattedAddress,"
            "places.location,"
            "places.priceLevel,"
            "places.primaryType,"
            "places.types"
        ),
    }
    body = {
        "includedTypes": ["restaurant", "cafe", "bar", "bakery", "meal_takeaway", "meal_delivery"],
        "maxResultCount": MAX_RESULTS_PER_ZONE,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": float(radius),
            }
        },
        "languageCode": LANGUAGE,
    }

    response = requests.post(NEARBY_SEARCH_URL, headers=headers, json=body)
    if response.status_code != 200:
        print(f"  [ERROR nearby_search] {response.status_code}: {response.text[:200]}")
        return []

    data = response.json()
    return data.get("places", [])


def get_place_details(place_id: str) -> dict:
    headers = {
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": (
            "id,"
            "displayName,"
            "rating,"
            "userRatingCount,"
            "formattedAddress,"
            "location,"
            "priceLevel,"
            "primaryType,"
            "types,"
            "reviews,"
            "regularOpeningHours,"
            "nationalPhoneNumber,"
            "websiteUri,"
            "googleMapsUri,"
            "takeout,"
            "delivery,"
            "dineIn,"
            "servesBreakfast,"
            "servesLunch,"
            "servesDinner,"
            "servesVegetarianFood"
        ),
    }
    # La API (New) requiere el prefijo "places/" en el ID
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"  [ERROR place_details] {place_id} → {response.status_code}: {response.text[:100]}")
        return {}

    return response.json()


def parse_reviews(raw_reviews: list) -> list[dict]:
    """Extrae y normaliza hasta MAX_REVIEWS_PER_PLACE reseñas."""
    reviews = []
    for r in raw_reviews[:MAX_REVIEWS_PER_PLACE]:
        reviews.append({
            "author": r.get("authorAttribution", {}).get("displayName", ""),
            "rating": r.get("rating"),
            "text": r.get("text", {}).get("text", ""),
            "language": r.get("text", {}).get("languageCode", ""),
            "published_at": r.get("publishTime", ""),
            "relative_time": r.get("relativePublishTimeDescription", ""),
        })
    return reviews


def parse_opening_hours(hours_data: dict) -> dict:
    """Extrae el horario de apertura en formato legible."""
    if not hours_data:
        return {"open_now": None, "schedule": []}
    return {
        "open_now": hours_data.get("openNow"),
        "schedule": hours_data.get("weekdayDescriptions", []),
    }


def flatten_for_csv(place: dict, reviews: list, zone_name: str) -> dict:
    """
    Aplana el objeto de un lugar para almacenarlo en una fila de CSV.
    Las reseñas se serializan como JSON dentro de una celda.
    """
    loc = place.get("location", {})
    hours = parse_opening_hours(place.get("regularOpeningHours", {}))

    price_map = {
        "PRICE_LEVEL_FREE": "Gratis",
        "PRICE_LEVEL_INEXPENSIVE": "Económico ($)",
        "PRICE_LEVEL_MODERATE": "Moderado ($$)",
        "PRICE_LEVEL_EXPENSIVE": "Caro ($$$)",
        "PRICE_LEVEL_VERY_EXPENSIVE": "Muy caro ($$$$)",
    }

    return {
        "place_id": place.get("id", ""),
        "name": place.get("displayName", {}).get("text", ""),
        "zone": zone_name,
        "address": place.get("formattedAddress", ""),
        "latitude": loc.get("latitude"),
        "longitude": loc.get("longitude"),
        "rating": place.get("rating"),
        "total_reviews": place.get("userRatingCount"),
        "price_level": price_map.get(place.get("priceLevel", ""), "Desconocido"),
        "primary_type": place.get("primaryType", ""),
        "types": ", ".join(place.get("types", [])),
        "phone": place.get("nationalPhoneNumber", ""),
        "website": place.get("websiteUri", ""),
        "google_maps_url": place.get("googleMapsUri", ""),
        "editorial_summary": place.get("editorialSummary", {}).get("text", ""),
        "open_now": hours.get("open_now"),
        "schedule": " | ".join(hours.get("schedule", [])),
        "takeout": place.get("takeout"),
        "delivery": place.get("delivery"),
        "dine_in": place.get("dineIn"),
        "serves_breakfast": place.get("servesBreakfast"),
        "serves_lunch": place.get("servesLunch"),
        "serves_dinner": place.get("servesDinner"),
        "serves_beer": place.get("servesBeer"),
        "serves_wine": place.get("servesWine"),
        "serves_vegetarian": place.get("servesVegetarianFood"),
        "wheelchair_accessible": place.get("wheelchairAccessibleEntrance"),
        "reviews_json": json.dumps(reviews, ensure_ascii=False),
        "reviews_count_extracted": len(reviews),
    }


# ─────────────────────────────────────────────
# FLUJO PRINCIPAL
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Extractor de Restaurantes — Ciudad de Panamá")
    print("=" * 60)

    seen_place_ids: set[str] = set()
    all_places_raw: list[dict] = []
    rows_csv: list[dict] = []

    # ── FASE 1: Búsqueda por zonas ──────────────────────────────
    print(f"\n[1/2] Buscando restaurantes en {len(SEARCH_ZONES)} zonas...\n")

    for zone in tqdm(SEARCH_ZONES, desc="Zonas"):
        results = nearby_search(zone["lat"], zone["lng"], SEARCH_RADIUS_METERS)
        new_places = [p for p in results if p.get("id") not in seen_place_ids]

        for place in new_places:
            pid = place.get("id")
            if pid:
                seen_place_ids.add(pid)
                # Guardamos zona de origen para referencia
                place["_zone_name"] = zone["name"]
                all_places_raw.append(place)

        time.sleep(DELAY_BETWEEN_REQUESTS)

    print(f"\n  → {len(all_places_raw)} restaurantes únicos encontrados.\n")

    # ── FASE 2: Detalles + reseñas por lugar ────────────────────
    print("[2/2] Obteniendo detalles y reseñas...\n")

    for place_stub in tqdm(all_places_raw, desc="Restaurantes"):
        place_id = place_stub.get("id", "")
        zone_name = place_stub.get("_zone_name", "")

        # Filtro rápido: descartar lugares con muy pocas reseñas
        if place_stub.get("userRatingCount", 0) < MIN_REVIEWS:
            continue

        details = get_place_details(place_id)
        if not details:
            continue

        reviews = parse_reviews(details.get("reviews", []))
        row = flatten_for_csv(details, reviews, zone_name)
        rows_csv.append(row)

        time.sleep(DELAY_BETWEEN_REQUESTS)

    # ── GUARDAR RESULTADOS ───────────────────────────────────────
    print(f"\n  → {len(rows_csv)} restaurantes con detalles extraídos.")

    if rows_csv:
        df = pd.DataFrame(rows_csv)
        df.sort_values(["zone", "rating"], ascending=[True, False], inplace=True)

        # Crear directorio de salida si no existe
        os.makedirs(os.path.dirname(OUTPUT_CSV) or ".", exist_ok=True)

        df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
        print(f"  CSV guardado en: {OUTPUT_CSV}")

        # JSON con datos crudos (útil para el análisis de reseñas con LLM)
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(rows_csv, f, ensure_ascii=False, indent=2)
        print(f"  JSON guardado en: {OUTPUT_JSON}")
    else:
        print("  [AVISO] No se extrajeron datos. Verifica tu API Key y cuota.")

    print("\n¡Extracción completada!")
    print("=" * 60)


if __name__ == "__main__":
    main()