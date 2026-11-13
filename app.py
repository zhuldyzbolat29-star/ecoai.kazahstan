import os
import math
import re
from datetime import datetime

import folium
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from folium.plugins import Fullscreen
from streamlit_folium import st_folium

# ============================================================
# ECO AI KAZAKHSTAN — educational environmental information app
# ============================================================

st.set_page_config(
    page_title="ECO AI Kazakhstan",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BG = "#F6F6E9"
GREEN = "#5A9A3A"
DARK = "#4A6B2F"
LIGHT = "#E8F5D8"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] {{
        font-family: 'Roboto', 'Arial', sans-serif;
    }}
    .stApp {{ background: {BG}; }}
    [data-testid="stHeader"] {{ background: rgba(246,246,233,0.96); }}
    h1, h2, h3 {{ color: {DARK}; font-weight: 700; }}
    p, label, span {{ color: #34402C; }}
    div.stButton > button, div.stFormSubmitButton > button {{
        background: {GREEN}; color: white; border: 0; border-radius: 12px;
        min-height: 44px; font-weight: 600;
    }}
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {{
        background: {DARK}; color: white; border: 0;
    }}
    div[data-testid="stTextInput"] input {{
        background: #fffef8; border: 1px solid #d4dfc8; border-radius: 10px;
    }}
    .eco-card {{
        background: #fffef8; border: 1px solid #e0e7d7; border-radius: 16px;
        padding: 18px; margin: 8px 0;
    }}
    .eco-muted {{ color: #66735e; font-size: 0.88rem; }}
    .eco-pill {{
        display:inline-block; background:{LIGHT}; color:{DARK}; padding:5px 10px;
        border-radius:20px; font-size:0.82rem; font-weight:600;
    }}
    .brand {{ color:{DARK}; font-size:1.7rem; font-weight:800; letter-spacing:.04em; }}
    .brand-mark {{ color:{GREEN}; font-size:1.8rem; }}
    footer {{visibility:hidden;}}
    </style>
    """,
    unsafe_allow_html=True,
)

LANGS = {
    "Русский": "ru",
    "Қазақша": "kk",
    "English": "en",
}
TEXT = {
    "ru": {
        "language": "Язык", "login_title": "Добро пожаловать в ECO AI",
        "login_sub": "Экологическая информационная платформа Казахстана",
        "login": "Логин (демо)", "password": "Пароль (демо)",
        "continue": "Продолжить", "city": "Город Казахстана",
        "factory": "Название предприятия / завода",
        "search": "Найти предприятие", "map": "Интерактивная карта",
        "air": "Загрязнение воздуха", "wind": "Ветер",
        "company": "Карточка предприятия", "risk": "Экологические риски",
        "analysis": "Анализ данных",
        "no_search": "Введите город и нажмите кнопку поиска.",
        "not_found": "Точное совпадение предприятия в открытых картографических данных не найдено.",
        "data_missing": "Данные недоступны для этой точки. Мы не подставляем вымышленные значения.",
        "model_notice": "Модельные данные Open-Meteo/CAMS, не прямое измерение у завода.",
        "official_notice": "Официальные измерения показываются только при наличии подтверждённого источника.",
        "source": "Источники данных", "risk_low": "Низкий модельный индикатор",
        "risk_mid": "Умеренный модельный индикатор", "risk_high": "Повышенный модельный индикатор",
        "risk_unknown": "Недостаточно данных для оценки",
        "no_factory": "Предприятие не найдено среди объектов OpenStreetMap в выбранной окрестности.",
        "osm_found": "Объекты промышленности из OpenStreetMap в окрестности города",
        "map_regions": "Региональные центры и подписи на карте. Это не административные границы.",
        "disclaimer": "ECO AI — информационный и учебный проект. Модельные данные не доказывают, что конкретный завод является источником загрязнения.",
        "temperature": "Температура", "humidity": "Влажность", "wind_speed": "Скорость ветра",
        "wind_dir": "Направление ветра", "aqi": "Индекс качества воздуха",
        "pollutant": "Загрязнитель", "value": "Значение", "unit": "Единица",
        "time": "Время", "no_chart": "Нет достаточного набора часовых данных для графика.",
        "factory_type": "Тип объекта", "coordinates": "Координаты",
        "open_map": "Открыть объект на карте", "search_error": "Не удалось получить данные:",
    },
    "kk": {
        "language": "Тіл", "login_title": "ECO AI платформасына қош келдіңіз",
        "login_sub": "Қазақстанның экологиялық ақпараттық платформасы",
        "login": "Логин (демо)", "password": "Құпиясөз (демо)",
        "continue": "Жалғастыру", "city": "Қазақстан қаласы",
        "factory": "Кәсіпорын / зауыт атауы", "search": "Кәсіпорынды іздеу",
        "map": "Интерактивті карта", "air": "Ауа ластануы", "wind": "Жел",
        "company": "Кәсіпорын картасы", "risk": "Экологиялық тәуекелдер",
        "analysis": "Деректерді талдау",
        "no_search": "Қаланы енгізіп, іздеу түймесін басыңыз.",
        "not_found": "Ашық карта деректерінен кәсіпорынның дәл сәйкестігі табылмады.",
        "data_missing": "Бұл нүкте үшін деректер қолжетімсіз. Жалған мәндер қолданылмайды.",
        "model_notice": "Open-Meteo/CAMS модельдік деректері, зауыт жанындағы тікелей өлшем емес.",
        "official_notice": "Ресми өлшемдер тек расталған дереккөз болғанда көрсетіледі.",
        "source": "Дереккөздер", "risk_low": "Модельдік көрсеткіш төмен",
        "risk_mid": "Модельдік көрсеткіш орташа", "risk_high": "Модельдік көрсеткіш жоғары",
        "risk_unknown": "Бағалау үшін дерек жеткіліксіз",
        "no_factory": "Таңдалған аумақта OpenStreetMap деректерінен кәсіпорын табылмады.",
        "osm_found": "Қала маңындағы OpenStreetMap өнеркәсіп нысандары",
        "map_regions": "Картадағы өңірлік орталықтар мен атаулар. Бұл әкімшілік шекаралар емес.",
        "disclaimer": "ECO AI — ақпараттық және оқу жобасы. Модельдік деректер нақты зауыттың ластау көзі екенін дәлелдемейді.",
        "temperature": "Температура", "humidity": "Ылғалдылық", "wind_speed": "Жел жылдамдығы",
        "wind_dir": "Жел бағыты", "aqi": "Ауа сапасының индексі",
        "pollutant": "Ластаушы зат", "value": "Мәні", "unit": "Өлшем бірлігі",
        "time": "Уақыт", "no_chart": "Графикке жеткілікті сағаттық дерек жоқ.",
        "factory_type": "Нысан түрі", "coordinates": "Координаттар",
        "open_map": "Нысанды картадан ашу", "search_error": "Деректерді алу мүмкін болмады:",
    },
    "en": {
        "language": "Language", "login_title": "Welcome to ECO AI",
        "login_sub": "Environmental information platform for Kazakhstan",
        "login": "Login (demo)", "password": "Password (demo)",
        "continue": "Continue", "city": "Kazakhstan city", "factory": "Enterprise / factory name",
        "search": "Find enterprise", "map": "Interactive map", "air": "Air pollution",
        "wind": "Wind", "company": "Enterprise profile", "risk": "Environmental risks",
        "analysis": "Data analysis", "no_search": "Enter a city and press Search.",
        "not_found": "No exact enterprise match was found in open map data.",
        "data_missing": "Data are unavailable for this point. No invented values are displayed.",
        "model_notice": "Open-Meteo/CAMS model data, not a direct measurement at the factory.",
        "official_notice": "Official measurements are shown only when a verified source is available.",
        "source": "Data sources", "risk_low": "Low model indicator",
        "risk_mid": "Moderate model indicator", "risk_high": "Elevated model indicator",
        "risk_unknown": "Not enough data to assess", "no_factory": "No enterprise was found in OpenStreetMap within the selected area.",
        "osm_found": "OpenStreetMap industrial objects near the city",
        "map_regions": "Regional centres and labels on the map. These are not administrative boundaries.",
        "disclaimer": "ECO AI is an informational and educational project. Model data do not prove that a specific factory is a pollution source.",
        "temperature": "Temperature", "humidity": "Humidity", "wind_speed": "Wind speed",
        "wind_dir": "Wind direction", "aqi": "Air quality index", "pollutant": "Pollutant",
        "value": "Value", "unit": "Unit", "time": "Time", "no_chart": "Not enough hourly data for a chart.",
        "factory_type": "Object type", "coordinates": "Coordinates", "open_map": "Open object on map",
        "search_error": "Could not retrieve data:",
    },
}

# Approximate regional-centre coordinates for map orientation only.
# Markers label centres; no administrative border polygons are claimed.
REGIONS = [
    ("Abai Region — Семей", 50.411, 80.227),
    ("Akmola Region — Кокшетау", 53.283, 69.383),
    ("Aktobe Region — Актобе", 50.283, 57.167),
    ("Almaty Region — Қонаев", 43.883, 77.067),
    ("Atyrau Region — Атырау", 47.117, 51.883),
    ("East Kazakhstan — Өскемен", 49.948, 82.628),
    ("Zhambyl Region — Тараз", 42.900, 71.367),
    ("Jetisu Region — Талдықорған", 45.017, 78.367),
    ("West Kazakhstan — Орал", 51.233, 51.367),
    ("Karaganda Region — Қарағанды", 49.800, 73.100),
    ("Kostanay Region — Қостанай", 53.217, 63.633),
    ("Kyzylorda Region — Қызылорда", 44.850, 65.483),
    ("Mangystau Region — Ақтау", 43.650, 51.167),
    ("Pavlodar Region — Павлодар", 52.300, 76.950),
    ("North Kazakhstan — Петропавл", 54.867, 69.150),
    ("Turkistan Region — Түркістан", 43.300, 68.250),
    ("Ulytau Region — Жезқазған", 47.783, 67.717),
    ("Almaty city", 43.238, 76.945),
    ("Astana city", 51.169, 71.449),
    ("Shymkent city", 42.341, 69.590),
]

HEADERS = {"User-Agent": "EcoAI-Kazakhstan-StudentProject/1.0 (educational demo)"}

def t(key):
    return TEXT[st.session_state.get("lang", "ru")].get(key, key)

@st.cache_data(ttl=3600, show_spinner=False)
def geocode_city(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 10, "language": "en", "format": "json", "countryCode": "KZ"}
    response = requests.get(url, params=params, headers=HEADERS, timeout=20)
    response.raise_for_status()
    results = response.json().get("results", [])
    results = [r for r in results if r.get("country_code", "").lower() == "kz" or
               r.get("country", "").lower() == "kazakhstan"]
    if not results:
        # Fallback to Nominatim when Open-Meteo geocoding has no Kazakhstan match.
        fallback = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": f"{city}, Kazakhstan", "format": "jsonv2", "limit": 5, "countrycodes": "kz"},
            headers=HEADERS, timeout=20,
        )
        fallback.raise_for_status()
        places = fallback.json()
        if not places:
            raise ValueError("Город не найден в Казахстане. Проверьте написание.")
        place = places[0]
        return {
            "name": place.get("name") or city,
            "admin1": place.get("display_name", "Kazakhstan").split(",")[-2].strip(),
            "country": "Kazakhstan", "country_code": "KZ",
            "latitude": float(place["lat"]), "longitude": float(place["lon"]),
        }
    # Prefer a result whose name exactly matches the requested city.
    return next((r for r in results if r.get("name", "").casefold() == city.casefold()), results[0])

@st.cache_data(ttl=1800, show_spinner=False)
def search_factory_nominatim(factory, city):
    if not factory.strip():
        return []
    response = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={
            "q": f"{factory}, {city}, Kazakhstan",
            "format": "jsonv2", "addressdetails": 1, "limit": 10,
            "countrycodes": "kz", "accept-language": "ru,en",
        },
        headers=HEADERS, timeout=25,
    )
    response.raise_for_status()
    results = []
    for item in response.json():
        address = item.get("address", {})
        if address.get("country_code", "kz").lower() != "kz":
            continue
        results.append({
            "name": item.get("name") or item.get("display_name", factory),
            "lat": float(item["lat"]), "lon": float(item["lon"]),
            "type": f"{item.get('category', 'place')} / {item.get('type', 'unknown')}",
            "operator": address.get("city") or address.get("town") or address.get("state") or "Not specified",
            "website": "", "osm_type": item.get("osm_type", ""),
            "osm_id": item.get("osm_id", ""),
            "display_name": item.get("display_name", ""),
        })
    return results

@st.cache_data(ttl=1800, show_spinner=False)
def get_air_quality(lat, lon):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat, "longitude": lon,
        "current": "european_aqi,us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone",
        "hourly": "pm10,pm2_5,nitrogen_dioxide,sulphur_dioxide,ozone",
        "forecast_days": 2, "timezone": "auto",
    }
    response = requests.get(url, params=params, headers=HEADERS, timeout=25)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=1800, show_spinner=False)
def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
        "hourly": "wind_speed_10m,wind_direction_10m",
        "forecast_days": 2, "timezone": "auto",
    }
    response = requests.get(url, params=params, headers=HEADERS, timeout=25)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=3600, show_spinner=False)
def get_osm_industrial_objects(lat, lon):
    # User-triggered, city-centred query. OSM results are community-mapped,
    # not a complete official register of Kazakhstan factories.
    query = f"""
    [out:json][timeout:25];
    (
      node(around:25000,{lat},{lon})["name"]["industrial"];
      way(around:25000,{lat},{lon})["name"]["industrial"];
      relation(around:25000,{lat},{lon})["name"]["industrial"];
      node(around:25000,{lat},{lon})["name"]["man_made"="works"];
      way(around:25000,{lat},{lon})["name"]["man_made"="works"];
      relation(around:25000,{lat},{lon})["name"]["man_made"="works"];
      node(around:25000,{lat},{lon})["name"]["landuse"="industrial"];
      way(around:25000,{lat},{lon})["name"]["landuse"="industrial"];
      relation(around:25000,{lat},{lon})["name"]["landuse"="industrial"];
    );
    out center tags;
    """
    response = requests.post(
        "https://overpass-api.de/api/interpreter",
        data=query,
        headers=HEADERS,
        timeout=40,
    )
    response.raise_for_status()
    elements = response.json().get("elements", [])
    objects = []
    for item in elements:
        tags = item.get("tags", {})
        name = tags.get("name")
        if not name:
            continue
        lat0 = item.get("lat", item.get("center", {}).get("lat"))
        lon0 = item.get("lon", item.get("center", {}).get("lon"))
        if lat0 is None or lon0 is None:
            continue
        objects.append({
            "name": name,
            "lat": float(lat0),
            "lon": float(lon0),
            "type": tags.get("industrial") or tags.get("man_made") or tags.get("landuse") or "industrial",
            "operator": tags.get("operator", "Not specified in OSM"),
            "website": tags.get("website", ""),
            "osm_type": item.get("type", ""),
            "osm_id": item.get("id", ""),
        })
    # Remove duplicates by name and rounded coordinates.
    unique = {}
    for obj in objects:
        unique[(obj["name"].lower(), round(obj["lat"], 4), round(obj["lon"], 4))] = obj
    return list(unique.values())

def wind_compass(degrees):
    if degrees is None:
        return "—"
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return directions[int((float(degrees) + 22.5) // 45) % 8]

def numeric(value):
    try:
        if value is None:
            return None
        v = float(value)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None

def risk_label(air):
    current = air.get("current", {})
    us_aqi = numeric(current.get("us_aqi"))
    eu_aqi = numeric(current.get("european_aqi"))
    if us_aqi is not None:
        if us_aqi <= 50:
            return t("risk_low"), "green", "US AQI"
        if us_aqi <= 100:
            return t("risk_mid"), "orange", "US AQI"
        return t("risk_high"), "red", "US AQI"
    if eu_aqi is not None:
        if eu_aqi <= 20:
            return t("risk_low"), "green", "European AQI"
        if eu_aqi <= 40:
            return t("risk_mid"), "orange", "European AQI"
        return t("risk_high"), "red", "European AQI"
    return t("risk_unknown"), "gray", "—"

# Session state
for key, default in {
    "stage": "intro", "lang": "ru",
    "city_result": None, "air": None, "weather": None,
    "osm_objects": [], "factory_query": "", "city_query": "", "osm_error": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Header: small brand identity on every non-intro screen.
def find_logo():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    for filename in ("eco_logo.png", "eco_logo.jpg", "eco_logo.jpeg"):
        candidate = os.path.join(project_dir, filename)
        if os.path.isfile(candidate):
            return candidate
    return None

def brand_header():
    col1, col2 = st.columns([5, 1])
    with col1:
        logo_path = find_logo()
        if logo_path:
            st.image(logo_path, width=112)
        else:
            st.error("Файл eco_logo.png не найден рядом с app.py.")
    with col2:
        if st.button("← " + ("Главная" if st.session_state.lang == "ru" else "Home"), use_container_width=True):
            st.session_state.stage = "login"
            st.rerun()
    st.divider()

if st.session_state.stage == "intro":
    st.markdown("<div style='height:5vh'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        logo_path = find_logo()
        if logo_path:
            st.image(logo_path, use_container_width=True)
        else:
            st.error("Не найден файл eco_logo.png. Добавьте его в корневую папку проекта рядом с app.py.")
        
        if st.button("Продолжить / Continue / Жалғастыру", use_container_width=True):
            st.session_state.stage = "login"
            st.rerun()
    st.stop()

if st.session_state.stage == "login":
    brand_header()
    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c2:
        st.markdown(f"<h2 style='text-align:center'>{t('login_title')}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center'>{t('login_sub')}</p>", unsafe_allow_html=True)
        language_label = st.selectbox(t("language"), list(LANGS.keys()), index=list(LANGS.values()).index(st.session_state.lang))
        st.session_state.lang = LANGS[language_label]
        # These fields are intentionally demo-only; credentials are not saved or authenticated.
        st.text_input(t("login"), key="demo_login")
        st.text_input(t("password"), type="password", key="demo_password")
        if st.button(t("continue"), use_container_width=True):
            st.session_state.stage = "app"
            st.rerun()
        st.caption("Демо-вход: логин и пароль не проверяются и не сохраняются. / Demo-only: credentials are not authenticated or stored.")
    st.stop()

# Main app
brand_header()
with st.sidebar:
    st.markdown("### ECO AI")
    language_label = st.selectbox(t("language"), list(LANGS.keys()), index=list(LANGS.values()).index(st.session_state.lang))
    st.session_state.lang = LANGS[language_label]
    st.markdown("---")
    st.caption("Open-Meteo · CAMS · OpenStreetMap")

st.markdown(f"## {t('search')}")
with st.form("enterprise_search"):
    col1, col2 = st.columns(2)
    with col1:
        city_input = st.text_input(t("city"), value=st.session_state.city_query, placeholder="Например: Тараз")
    with col2:
        factory_input = st.text_input(t("factory"), value=st.session_state.factory_query, placeholder="Например: Казфосфат")
    submitted = st.form_submit_button(t("search"), use_container_width=True)

if submitted:
    if not city_input.strip():
        st.error(t("no_search"))
    else:
        try:
            with st.spinner("Получаем географические и экологические данные..."):
                city_data = geocode_city(city_input.strip())
                lat, lon = float(city_data["latitude"]), float(city_data["longitude"])
                air_data = get_air_quality(lat, lon)
                weather_data = get_weather(lat, lon)
                osm_error = None
                try:
                    osm_data = get_osm_industrial_objects(lat, lon)
                except Exception as map_exc:
                    osm_data = []
                    osm_error = str(map_exc)
                named_results = []
                if factory_input.strip():
                    try:
                        named_results = search_factory_nominatim(factory_input.strip(), city_input.strip())
                    except Exception as search_exc:
                        osm_error = (osm_error + " | " if osm_error else "") + str(search_exc)
                # Put direct enterprise matches first and remove duplicate map records.
                combined = named_results + osm_data
                seen = set()
                osm_data = []
                for obj in combined:
                    key = (obj["name"].casefold(), round(obj["lat"], 4), round(obj["lon"], 4))
                    if key not in seen:
                        seen.add(key)
                        osm_data.append(obj)
            st.session_state.city_query = city_input.strip()
            st.session_state.factory_query = factory_input.strip()
            st.session_state.city_result = city_data
            st.session_state.air = air_data
            st.session_state.weather = weather_data
            st.session_state.osm_objects = osm_data
            st.session_state.osm_error = osm_error
            st.success(f"{city_data['name']}, {city_data.get('admin1', 'Kazakhstan')} — {lat:.4f}, {lon:.4f}")
        except Exception as exc:
            st.error(f"{t('search_error')} {exc}")

city_data = st.session_state.city_result
air_data = st.session_state.air
weather_data = st.session_state.weather
osm_data = st.session_state.osm_objects
factory_query = st.session_state.factory_query.strip()

if not city_data or not air_data or not weather_data:
    st.info(t("no_search"))
    st.markdown(f"<div class='eco-card'>{t('disclaimer')}</div>", unsafe_allow_html=True)
    st.stop()

lat, lon = float(city_data["latitude"]), float(city_data["longitude"])
city_name = city_data["name"]
current_air = air_data.get("current", {})
current_weather = weather_data.get("current", {})
risk_text, risk_color, risk_source = risk_label(air_data)

st.markdown(f"### {city_name} — {city_data.get('admin1', 'Kazakhstan')}")
st.markdown(f"<span class='eco-pill'>{t('model_notice')}</span>", unsafe_allow_html=True)
st.caption(t("official_notice"))

tabs = st.tabs([t("map"), t("air"), t("wind"), t("company"), t("risk"), t("analysis")])

# 1. Kazakhstan map and industrial OSM features
with tabs[0]:
    st.subheader(t("map"))
    st.caption(t("map_regions"))
    fmap = folium.Map(location=[48.0, 67.0], zoom_start=5, tiles="OpenStreetMap", control_scale=True)
    Fullscreen(position="topright").add_to(fmap)
    region_group = folium.FeatureGroup(name="Kazakhstan regional centres", show=True)
    for region_name, rlat, rlon in REGIONS:
        folium.CircleMarker(
            location=[rlat, rlon], radius=5, color=DARK, fill=True,
            fill_color=GREEN, fill_opacity=0.9,
            tooltip=region_name,
        ).add_to(region_group)
        folium.Marker(
            [rlat, rlon],
            icon=folium.DivIcon(html=f'<div style="font-size:10px;color:#34402c;font-weight:600;white-space:nowrap">{region_name.split(" — ")[0]}</div>'),
        ).add_to(region_group)
    region_group.add_to(fmap)
    folium.Marker(
        [lat, lon], tooltip=f"{city_name} — selected city",
        popup=f"{city_name}<br>Open-Meteo model grid point",
        icon=folium.Icon(color="green", icon="leaf", prefix="fa"),
    ).add_to(fmap)
    factory_matches = []
    if factory_query:
        q = re.sub(r"[^a-zа-яәіңғүұқөһ0-9]", "", factory_query.casefold())
        factory_matches = [
            o for o in osm_data
            if q and q in re.sub(r"[^a-zа-яәіңғүұқөһ0-9]", "", o["name"].casefold())
        ]
    visible_objects = factory_matches if factory_matches else osm_data[:80]
    factory_group = folium.FeatureGroup(name="OSM industrial objects", show=True)
    for obj in visible_objects:
        folium.Marker(
            [obj["lat"], obj["lon"]],
            tooltip=obj["name"],
            popup=f"<b>{obj['name']}</b><br>Type: {obj['type']}<br>Source: OpenStreetMap",
            icon=folium.Icon(color="darkgreen", icon="industry", prefix="fa"),
        ).add_to(factory_group)
    factory_group.add_to(fmap)
    folium.LayerControl(collapsed=False).add_to(fmap)
    st_folium(fmap, use_container_width=True, height=560, returned_objects=[])
    st.caption("Карта: ©️ OpenStreetMap contributors. " + t("map_regions"))
    if factory_query and not factory_matches:
        st.warning(t("not_found"))
        st.caption("Поиск проверяет OpenStreetMap/Nominatim. Это открытая карта, а не полный официальный реестр предприятий Казахстана.")
    if st.session_state.get("osm_error"):
        st.caption("Часть результатов карты временно недоступна: " + st.session_state.osm_error[:300])
    st.write(f"**{t('osm_found')}:** {len(osm_data)}")
    if visible_objects:
        st.dataframe(pd.DataFrame([
            {"Предприятие / объект": o["name"], "Тип": o["type"], "Широта": o["lat"], "Долгота": o["lon"]}
            for o in visible_objects
        ]), use_container_width=True, hide_index=True)
    else:
        st.info(t("no_factory"))

# 2. Air quality
with tabs[1]:
    st.subheader(t("air"))
    st.info(t("model_notice"))
    pollutants = [
        ("PM2.5", "pm2_5", "µg/m³"),
        ("PM10", "pm10", "µg/m³"),
        ("CO (угарный газ)", "carbon_monoxide", "µg/m³"),
        ("NO₂", "nitrogen_dioxide", "µg/m³"),
        ("SO₂", "sulphur_dioxide", "µg/m³"),
        ("O₃", "ozone", "µg/m³"),
    ]
    cols = st.columns(3)
    for i, (label, key, unit) in enumerate(pollutants):
        value = numeric(current_air.get(key))
        with cols[i % 3]:
            st.metric(label, f"{value:.2f} {unit}" if value is not None else "—")
    aqi_value = numeric(current_air.get("us_aqi"))
    if aqi_value is None:
        aqi_value = numeric(current_air.get("european_aqi"))
    st.metric(t("aqi"), f"{aqi_value:.0f}" if aqi_value is not None else "—")
    hourly = air_data.get("hourly", {})
    times = hourly.get("time", [])
    if times:
        chart_df = pd.DataFrame({"time": times})
        for label, key, unit in pollutants:
            vals = hourly.get(key, [])
            if vals and len(vals) == len(times):
                chart_df[label] = vals
        chart_df = chart_df.head(24)
        value_cols = [c for c in chart_df.columns if c != "time"]
        if value_cols:
            chosen = st.multiselect("Показатели для графика / Chart indicators", value_cols, default=value_cols[:2])
            if chosen:
                melted = chart_df.melt(id_vars="time", value_vars=chosen, var_name="Pollutant", value_name="µg/m³")
                fig = px.line(melted, x="time", y="µg/m³", color="Pollutant", markers=True,
                              title="Почасовые модельные данные / Hourly model data")
                fig.update_layout(paper_bgcolor=BG, plot_bgcolor="#fffef8")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(t("no_chart"))
    st.caption("Source: Open-Meteo Air Quality API / CAMS. " + t("model_notice"))
    st.markdown(f"[Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api)")
    st.caption("CO — это угарный газ (carbon monoxide), не CO₂. В этом API показатель CO₂ не подменяется показателем CO.")

# 3. Wind
with tabs[2]:
    st.subheader(t("wind"))
    wind_speed = numeric(current_weather.get("wind_speed_10m"))
    wind_dir = numeric(current_weather.get("wind_direction_10m"))
    temp = numeric(current_weather.get("temperature_2m"))
    humidity = numeric(current_weather.get("relative_humidity_2m"))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("wind_speed"), f"{wind_speed:.1f} km/h" if wind_speed is not None else "—")
    c2.metric(t("wind_dir"), f"{wind_dir:.0f}° {wind_compass(wind_dir)}" if wind_dir is not None else "—")
    c3.metric(t("temperature"), f"{temp:.1f} °C" if temp is not None else "—")
    c4.metric(t("humidity"), f"{humidity:.0f}%" if humidity is not None else "—")
    if wind_dir is not None:
        st.markdown(
            f"<div class='eco-card' style='text-align:center'>"
            f"<div style='font-size:14px;color:{DARK}'>Wind direction</div>"
            f"<div style='font-size:64px;color:{GREEN};transform:rotate({wind_dir}deg)'>↑</div>"
            f"<b>{wind_compass(wind_dir)} · {wind_dir:.0f}°</b></div>",
            unsafe_allow_html=True,
        )
    st.caption("Wind data are weather-model output, not proof of pollutant transport from a particular factory.")
    st.markdown("[Open-Meteo Weather API](https://open-meteo.com/en/docs)")

# 4. Enterprise profile
with tabs[3]:
    st.subheader(t("company"))
    if factory_matches:
        selected = factory_matches[0]
        st.markdown(f"### {selected['name']}")
        st.write(f"**{t('factory_type')}:** {selected['type']}")
        st.write(f"**{t('coordinates')}:** {selected['lat']:.5f}, {selected['lon']:.5f}")
        st.write(f"**Operator:** {selected['operator']}")
        if selected["website"]:
            st.write(f"**Website:** {selected['website']}")
        st.caption("Source: OpenStreetMap community-contributed map data. This is not an official industrial register.")
        st.markdown(f"https://www.openstreetmap.org/{selected['osm_type']}/{selected['osm_id']}")
    else:
        st.warning(t("not_found"))
        st.write("Предприятие может отсутствовать в OpenStreetMap или быть записано под другим названием.")
        st.write("The requested enterprise may be missing from OpenStreetMap or listed under another name.")
    st.markdown("#### Environmental measurements")
    st.info(t("official_notice"))
    st.write(t("data_missing"))
    st.markdown("[Казгидромет — официальный сайт](https://www.kazhydromet.kz/)")

# 5. Environmental risk screening
with tabs[4]:
    st.subheader(t("risk"))
    st.info("Предварительный индикатор основан только на модельном индексе воздуха в координатах города. Это не официальная оценка риска и не оценка конкретного предприятия.")
    st.markdown(f"### {risk_text}")
    st.write(f"Index source: {risk_source}")
    if risk_color == "green":
        st.success("Model index falls in the lower band.")
    elif risk_color == "orange":
        st.warning("Model index falls in a moderate band.")
    elif risk_color == "red":
        st.error("Model index is in an elevated band.")
    else:
        st.info(t("risk_unknown"))
    st.write("Для полноценной оценки нужны подтверждённые измерения, нормативы, временной период, метеоданные и проверенная методика.")
    st.write("A wind direction or a nearby factory alone cannot establish the source of pollution.")

# 6. Analysis
with tabs[5]:
    st.subheader(t("analysis"))
    st.write("Доступны почасовые модельные данные прогноза; исторический тренд не строится, если API не предоставляет соответствующий период.")
    st.write("Hourly model forecast is available; no historical trend is invented.")
    st.json({
        "city": city_name,
        "coordinates": {"latitude": lat, "longitude": lon},
        "air_quality_model": air_data.get("current", {}),
        "weather_model": weather_data.get("current", {}),
        "retrieved_at_local": datetime.now().astimezone().isoformat(timespec="minutes"),
    })

st.markdown("---")
st.markdown(f"<div class='eco-card'>{t('disclaimer')}</div>", unsafe_allow_html=True)
st.markdown(
    "**Data attribution:** Open-Meteo / Copernicus Atmosphere Monitoring Service (CAMS); "
    "OpenStreetMap contributors. "
    "[Open-Meteo Air Quality](https://open-meteo.com/en/docs/air-quality-api) · "
    "[Open-Meteo Weather](https://open-meteo.com/en/docs) · "
    "[OpenStreetMap](https://www.openstreetmap.org/copyright) · "
    "[Kazhydromet](https://www.kazhydromet.kz/)"
)
