import base64
import math
import re
from datetime import datetime
from io import BytesIO

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BG = "#F6F6E9"
GREEN = "#5A9A3A"
DARK = "#4A6B2F"
LIGHT = "#E8F5D8"

# Original EcoAI green-leaf logo supplied for this project (embedded; no extra upload needed).
LOGO_BYTES = base64.b64decode("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")

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
        "official_notice": "Официальные измерения показываются только при наличии подтверждённого источника.", "risk_low": "Низкий модельный индикатор",
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
        "official_notice": "Ресми өлшемдер тек расталған дереккөз болғанда көрсетіледі.", "risk_low": "Модельдік көрсеткіш төмен",
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
        "official_notice": "Official measurements are shown only when a verified source is available.", "risk_low": "Low model indicator",
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

# Reuse connections and retry short-lived HTTP/service errors once.
API_SESSION = requests.Session()
RETRY_POLICY = Retry(
    total=1,
    connect=1,
    read=0,
    status=1,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset(("GET", "POST")),
)
API_ADAPTER = HTTPAdapter(max_retries=RETRY_POLICY)
API_SESSION.mount("https://", API_ADAPTER)
API_SESSION.mount("http://", API_ADAPTER)

CITY_FALLBACKS = {
    "тараз": ("Taraz", 42.9006, 71.3667, "Zhambyl Region"),
    "taraz": ("Taraz", 42.9006, 71.3667, "Zhambyl Region"),
    "темиртау": ("Temirtau", 50.0549, 72.9646, "Karaganda Region"),
    "temirtau": ("Temirtau", 50.0549, 72.9646, "Karaganda Region"),
    "астана": ("Astana", 51.1694, 71.4491, "Astana"),
    "astana": ("Astana", 51.1694, 71.4491, "Astana"),
    "нур-султан": ("Astana", 51.1694, 71.4491, "Astana"),
    "алматы": ("Almaty", 43.2389, 76.8897, "Almaty"),
    "almaty": ("Almaty", 43.2389, 76.8897, "Almaty"),
    "шымкент": ("Shymkent", 42.3417, 69.5901, "Shymkent"),
    "shymkent": ("Shymkent", 42.3417, 69.5901, "Shymkent"),
    "караганда": ("Karaganda", 49.8064, 73.0855, "Karaganda Region"),
    "karaganda": ("Karaganda", 49.8064, 73.0855, "Karaganda Region"),
    "актобе": ("Aktobe", 50.2839, 57.1670, "Aktobe Region"),
    "aktobe": ("Aktobe", 50.2839, 57.1670, "Aktobe Region"),
    "павлодар": ("Pavlodar", 52.2873, 76.9674, "Pavlodar Region"),
    "pavlodar": ("Pavlodar", 52.2873, 76.9674, "Pavlodar Region"),
    "атырау": ("Atyrau", 47.1164, 51.8833, "Atyrau Region"),
    "atyrau": ("Atyrau", 47.1164, 51.8833, "Atyrau Region"),
    "семей": ("Semey", 50.4111, 80.2275, "Abai Region"),
    "костанай": ("Kostanay", 53.2144, 63.6246, "Kostanay Region"),
    "кызылорда": ("Kyzylorda", 44.8488, 65.4823, "Kyzylorda Region"),
    "актау": ("Aktau", 43.6532, 51.1975, "Mangystau Region"),
    "кокшетау": ("Kokshetau", 53.2833, 69.3833, "Akmola Region"),
}

@st.cache_data(ttl=3600, show_spinner=False)
def geocode_city(city):
    city_key = city.strip().casefold()
    variants = [city.strip()]
    if city_key in CITY_FALLBACKS:
        fallback_name = CITY_FALLBACKS[city_key][0]
        if fallback_name not in variants:
            variants.insert(0, fallback_name)
    last_error = None
    for candidate in variants:
        try:
            response = API_SESSION.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": candidate, "count": 15, "language": "en", "format": "json", "countryCode": "KZ"},
                headers=HEADERS,
                timeout=(8, 22),
            )
            response.raise_for_status()
            results = response.json().get("results", [])
            for place in results:
                if place.get("country_code", "").upper() == "KZ":
                    return place
        except requests.RequestException as exc:
            last_error = exc
    # Known city-centre fallback allows the dashboard to load even if geocoding is temporarily unavailable.
    if city_key in CITY_FALLBACKS:
        name, lat, lon, region = CITY_FALLBACKS[city_key]
        return {"name": name, "latitude": lat, "longitude": lon,
                "country_code": "KZ", "admin1": region, "is_fallback": True}
    if last_error:
        raise last_error
    raise ValueError("City was not found in Kazakhstan. Check the spelling.")

@st.cache_data(ttl=900, show_spinner=False)
def get_air_quality(lat, lon):
    params = {
        "latitude": lat, "longitude": lon,
        "current": "european_aqi,us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone",
        "hourly": "pm10,pm2_5,nitrogen_dioxide,sulphur_dioxide,ozone",
        "forecast_days": 2, "timezone": "auto",
    }
    response = API_SESSION.get(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
        params=params, headers=HEADERS, timeout=(8, 35),
    )
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=900, show_spinner=False)
def get_weather(lat, lon):
    params = {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
        "hourly": "wind_speed_10m,wind_direction_10m",
        "forecast_days": 2, "timezone": "auto",
    }
    response = API_SESSION.get(
        "https://api.open-meteo.com/v1/forecast",
        params=params, headers=HEADERS, timeout=(8, 35),
    )
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=1800, show_spinner=False)
def get_osm_industrial_objects(lat, lon):
    # Community-mapped features only; this is not an official complete factory register.
    query = f"""
    [out:json][timeout:20];
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
    endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ]
    last_error = None
    for endpoint in endpoints:
        try:
            response = API_SESSION.post(endpoint, data=query, headers=HEADERS, timeout=(8, 28))
            response.raise_for_status()
            elements = response.json().get("elements", [])
            objects = []
            for item in elements:
                tags = item.get("tags", {})
                name = tags.get("name")
                if not name:
                    continue
                center = item.get("center", item)
                lat0, lon0 = center.get("lat"), center.get("lon")
                if lat0 is None or lon0 is None:
                    continue
                objects.append({
                    "name": name, "lat": float(lat0), "lon": float(lon0),
                    "type": tags.get("industrial") or tags.get("man_made") or tags.get("landuse") or "industrial",
                    "operator": tags.get("operator", "Not specified in OSM"),
                    "website": tags.get("website", ""),
                    "osm_type": item.get("type", ""), "osm_id": item.get("id", ""),
                })
            unique = {}
            for obj in objects:
                key = (obj["name"].casefold(), round(obj["lat"], 4), round(obj["lon"], 4))
                unique[key] = obj
            return list(unique.values())
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
    if last_error:
        raise last_error
    return []

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
    "osm_objects": [], "factory_query": "", "city_query": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Header: small brand identity on every non-intro screen.
def find_logo():
    """Return the original EcoAI leaf logo embedded in app.py."""
    return LOGO_BYTES

def brand_header():
    col1, col2 = st.columns([5, 1])
    with col1:
        logo_path = find_logo()
        if logo_path:
            st.image(logo_path, width=62)
        st.markdown('<div class="brand">ECO AI KAZAKHSTAN</div>', unsafe_allow_html=True)
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
            st.markdown(
                f"<div style='background:{BG};padding:70px 15px;text-align:center;border-radius:20px'>"
                f"<div style='font-size:80px;color:{GREEN}'>❧</div>"
                f"<div style='font-size:46px;font-weight:800;color:{DARK}'>ECO AI</div></div>",
                unsafe_allow_html=True,
            )
        st.markdown("<div style='text-align:center;color:#4A6B2F;font-weight:600'>KAZAKHSTAN</div>", unsafe_allow_html=True)
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
        warnings = []
        with st.spinner("Получаем данные из открытых источников. Если источник недоступен, остальные разделы продолжат работать..."):
            try:
                city_data = geocode_city(city_input.strip())
                lat, lon = float(city_data["latitude"]), float(city_data["longitude"])
                try:
                    air_data = get_air_quality(lat, lon)
                except requests.RequestException as exc:
                    air_data = None
                    warnings.append(f"Open-Meteo Air Quality: {type(exc).__name__}")
                try:
                    weather_data = get_weather(lat, lon)
                except requests.RequestException as exc:
                    weather_data = None
                    warnings.append(f"Open-Meteo Weather: {type(exc).__name__}")
                try:
                    osm_data = get_osm_industrial_objects(lat, lon)
                except requests.RequestException as exc:
                    osm_data = []
                    warnings.append(f"OpenStreetMap Overpass: {type(exc).__name__}")
                st.session_state.city_query = city_input.strip()
                st.session_state.factory_query = factory_input.strip()
                st.session_state.city_result = city_data
                st.session_state.air = air_data or {}
                st.session_state.weather = weather_data or {}
                st.session_state.osm_objects = osm_data or []
                st.session_state.api_warnings = warnings
                st.success(f"{city_data['name']}, {city_data.get('admin1', 'Kazakhstan')} — {lat:.4f}, {lon:.4f}")
            except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
                st.error(f"{t('search_error')} {exc}")

city_data = st.session_state.city_result
air_data = st.session_state.air or {}
weather_data = st.session_state.weather or {}
osm_data = st.session_state.osm_objects or []
factory_query = st.session_state.factory_query.strip()

if not city_data:
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
for warning in st.session_state.get("api_warnings", []):
    st.warning(f"Источник временно недоступен: {warning}. Соответствующие значения будут показаны как недоступные, без выдуманных данных.")
if not air_data:
    st.info("Данные качества воздуха временно недоступны. Карта, ветер и поиск объектов могут работать отдельно.")
if not weather_data:
    st.info("Погодные данные временно недоступны. Остальные разделы остаются доступны.")

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
        q = factory_query.casefold()
        factory_matches = [o for o in osm_data if q in o["name"].casefold()]
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
        ("CO", "carbon_monoxide", "µg/m³"),
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
