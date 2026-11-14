import os
import math
import re
from datetime import datetime

import folium
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import streamlit.components.v1 as components
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
        "analysis": "Анализ данных", "team": "О команде", "pollution_map": "Карта загрязнения Казахстана",
        "no_search": "Введите город и нажмите кнопку поиска.",
        "not_found": "Точное совпадение предприятия в открытых картографических данных не найдено.",
        "data_missing": "Данные недоступны для этой точки. Мы не подставляем вымышленные значения.",
        "model_notice": "Модельные данные Open-Meteo/CAMS, не прямое измерение у завода.",
        "official_notice": "Официальные измерения показываются только при наличии подтверждённого источника.",
        "source": "Источники данных", "risk_low": "Низкий модельный индикатор",
        "risk_mid": "Умеренный модельный индикатор", "risk_high": "Повышенный модельный индикатор",
        "risk_unknown": "Недостаточно данных для оценки",
        "risk_sensitive": "Повышенный риск для чувствительных групп",
        "risk_high": "Высокий уровень загрязнения воздуха",
        "risk_very_high": "Очень высокий уровень загрязнения воздуха",
        "risk_hazardous": "Опасный уровень загрязнения воздуха",
        "risk_fair": "Хорошее / приемлемое качество воздуха",
        "risk_poor": "Плохое качество воздуха",
        "risk_extreme": "Чрезвычайно плохое качество воздуха",
        "risk_site": "Точка оценки",
        "risk_city_point": "Модельная точка в центре города",
        "risk_factory_point": "Модельная точка рядом с найденным предприятием",
        "risk_detail_note": "Это предварительный скрининг качества воздуха по модели, а не официальная санитарная или экологическая экспертиза предприятия.",
        "risk_pollutants_title": "Текущие модельные концентрации загрязнителей",
        "risk_aqi_legend": "Категории US AQI: 0–50 — хорошее; 51–100 — умеренное; 101–150 — вредно для чувствительных групп; 151–200 — вредно; 201–300 — очень вредно; 301+ — опасное.",
        "risk_missing_notice": "Индекс качества воздуха недоступен. Уровень риска не присваивается.",
        "wind_map_caption": "Анимированная карта ветра Windy: потоки и прогнозная шкала обновляются на карте. Это модель прогноза, а не измерения датчика.",
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
        "analysis": "Деректерді талдау", "team": "Команда туралы", "pollution_map": "Қазақстанның ластану картасы",
        "no_search": "Қаланы енгізіп, іздеу түймесін басыңыз.",
        "not_found": "Ашық карта деректерінен кәсіпорынның дәл сәйкестігі табылмады.",
        "data_missing": "Бұл нүкте үшін деректер қолжетімсіз. Жалған мәндер қолданылмайды.",
        "model_notice": "Open-Meteo/CAMS модельдік деректері, зауыт жанындағы тікелей өлшем емес.",
        "official_notice": "Ресми өлшемдер тек расталған дереккөз болғанда көрсетіледі.",
        "source": "Дереккөздер", "risk_low": "Модельдік көрсеткіш төмен",
        "risk_mid": "Модельдік көрсеткіш орташа", "risk_high": "Модельдік көрсеткіш жоғары",
        "risk_unknown": "Бағалау үшін дерек жеткіліксіз",
        "risk_sensitive": "Сезімтал топтар үшін жоғары қауіп",
        "risk_high": "Ауа ластануының жоғары деңгейі",
        "risk_very_high": "Ауа ластануының өте жоғары деңгейі",
        "risk_hazardous": "Ауа ластануының қауіпті деңгейі",
        "risk_fair": "Ауа сапасы жақсы / қанағаттанарлық",
        "risk_poor": "Ауа сапасы нашар",
        "risk_extreme": "Ауа сапасы өте нашар",
        "risk_site": "Бағалау нүктесі",
        "risk_city_point": "Қала орталығындағы модельдік нүкте",
        "risk_factory_point": "Табылған кәсіпорын маңындағы модельдік нүкте",
        "risk_detail_note": "Бұл модель бойынша ауа сапасын алдын ала бағалау. Бұл кәсіпорынның ресми санитариялық немесе экологиялық сараптамасы емес.",
        "risk_pollutants_title": "Ластаушы заттардың ағымдағы модельдік концентрациялары",
        "risk_aqi_legend": "US AQI санаттары: 0–50 — жақсы; 51–100 — орташа; 101–150 — сезімтал топтарға зиянды; 151–200 — зиянды; 201–300 — өте зиянды; 301+ — қауіпті.",
        "risk_missing_notice": "Ауа сапасының индексі қолжетімсіз. Қауіп деңгейі берілмейді.",
        "wind_map_caption": "Windy желінің анимациялық картасы: жел ағындары мен болжам шкаласы картада көрсетіледі. Бұл датчик өлшемі емес, модель болжамы.",
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
        "analysis": "Data analysis", "team": "About the team", "pollution_map": "Kazakhstan pollution map", "no_search": "Enter a city and press Search.",
        "not_found": "No exact enterprise match was found in open map data.",
        "data_missing": "Data are unavailable for this point. No invented values are displayed.",
        "model_notice": "Open-Meteo/CAMS model data, not a direct measurement at the factory.",
        "official_notice": "Official measurements are shown only when a verified source is available.",
        "source": "Data sources", "risk_low": "Low model indicator",
        "risk_mid": "Moderate model indicator", "risk_high": "Elevated model indicator",
        "risk_unknown": "Not enough data to assess",
        "risk_sensitive": "Unhealthy for sensitive groups",
        "risk_high": "Unhealthy air quality",
        "risk_very_high": "Very unhealthy air quality",
        "risk_hazardous": "Hazardous air quality",
        "risk_fair": "Good / fair air quality",
        "risk_poor": "Poor air quality",
        "risk_extreme": "Extremely poor air quality",
        "risk_site": "Assessment point",
        "risk_city_point": "Model grid point in the city centre",
        "risk_factory_point": "Model grid point near the found enterprise",
        "risk_detail_note": "This is a preliminary model-based air-quality screening, not an official sanitary or environmental assessment of the enterprise.",
        "risk_pollutants_title": "Current modelled pollutant concentrations",
        "risk_aqi_legend": "US AQI categories: 0–50 good; 51–100 moderate; 101–150 unhealthy for sensitive groups; 151–200 unhealthy; 201–300 very unhealthy; 301+ hazardous.",
        "risk_missing_notice": "Air quality index is unavailable. No risk category is assigned.",
        "wind_map_caption": "Animated Windy wind map: animated flow and forecast timeline are shown on the map. This is model output, not a sensor measurement.", "no_factory": "No enterprise was found in OpenStreetMap within the selected area.",
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

# Representative city-centre points used for a countrywide model overview.
# These are sampling points for the atmospheric model, not monitoring stations.
NATIONAL_CITIES = [
    ("Астана", 51.1694, 71.4491),
    ("Алматы", 43.2383, 76.9450),
    ("Шымкент", 42.3417, 69.5901),
    ("Караганда", 49.8060, 73.0850),
    ("Темиртау", 50.0540, 72.9640),
    ("Тараз", 42.9000, 71.3670),
    ("Актобе", 50.2839, 57.1670),
    ("Атырау", 47.1170, 51.8830),
    ("Павлодар", 52.3000, 76.9500),
    ("Усть-Каменогорск", 49.9480, 82.6280),
    ("Семей", 50.4110, 80.2270),
    ("Костанай", 53.2170, 63.6330),
    ("Петропавловск", 54.8670, 69.1500),
    ("Кокшетау", 53.2830, 69.3830),
    ("Уральск", 51.2330, 51.3670),
    ("Кызылорда", 44.8500, 65.4830),
    ("Актау", 43.6500, 51.1670),
    ("Талдыкорган", 45.0170, 78.3670),
    ("Туркестан", 43.3000, 68.2500),
    ("Жезказган", 47.7830, 67.7170),
    ("Балхаш", 46.8480, 74.9950),
    ("Риддер", 50.3440, 83.5120),
    ("Рудный", 52.9720, 63.1160),
    ("Экибастуз", 51.7230, 75.3220),
    ("Кульсары", 46.9570, 54.0190),
    ("Хромтау", 50.2510, 58.4420),
]

# Kazhydromet publications identify these settlements as part of the air-monitoring
# network. When an exact station registry cannot be reached, markers are deliberately
# placed at settlement centres and labelled approximate (not as exact station sites).
MONITORING_SETTLEMENT_FALLBACK = [
    ("Астана", 51.1694, 71.4491), ("Алматы", 43.2383, 76.9450),
    ("Шымкент", 42.3417, 69.5901), ("Тараз", 42.9000, 71.3670),
    ("Караганда", 49.8060, 73.0850), ("Темиртау", 50.0540, 72.9640),
    ("Актобе", 50.2839, 57.1670), ("Атырау", 47.1170, 51.8830),
    ("Актау", 43.6500, 51.1670), ("Павлодар", 52.3000, 76.9500),
    ("Усть-Каменогорск", 49.9480, 82.6280), ("Семей", 50.4110, 80.2270),
    ("Костанай", 53.2170, 63.6330), ("Петропавловск", 54.8670, 69.1500),
    ("Кокшетау", 53.2830, 69.3830), ("Уральск", 51.2330, 51.3670),
    ("Кызылорда", 44.8500, 65.4830), ("Талдыкорган", 45.0170, 78.3670),
    ("Туркестан", 43.3000, 68.2500), ("Жезказган", 47.7830, 67.7170),
    ("Балхаш", 46.8480, 74.9950), ("Риддер", 50.3440, 83.5120),
    ("Рудный", 52.9720, 63.1160), ("Экибастуз", 51.7230, 75.3220),
    ("Кульсары", 46.9570, 54.0190), ("Хромтау", 50.2510, 58.4420),
]

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
            "direct_search_result": True,
        })
    return results

@st.cache_data(ttl=1800, show_spinner=False)
def get_air_quality(lat, lon):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat, "longitude": lon,
        "current": "european_aqi,us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone",
        "hourly": "pm10,pm2_5,carbon_dioxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi,european_aqi",
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

@st.cache_data(ttl=1800, show_spinner=False)
def get_national_air_overview():
    """One batched Open-Meteo Air Quality request for representative Kazakhstan cities."""
    latitudes = ",".join(f"{point[1]:.5f}" for point in NATIONAL_CITIES)
    longitudes = ",".join(f"{point[2]:.5f}" for point in NATIONAL_CITIES)
    response = requests.get(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
        params={
            "latitude": latitudes,
            "longitude": longitudes,
            "current": "us_aqi,pm2_5,pm10",
            "timezone": "auto",
        },
        headers=HEADERS,
        timeout=35,
    )
    response.raise_for_status()
    payload = response.json()
    records = payload if isinstance(payload, list) else [payload]
    result = []
    for idx, city in enumerate(NATIONAL_CITIES):
        if idx >= len(records):
            break
        current = records[idx].get("current", {}) if isinstance(records[idx], dict) else {}
        result.append({
            "name": city[0], "lat": city[1], "lon": city[2],
            "aqi": current.get("us_aqi"),
            "pm25": current.get("pm2_5"),
            "pm10": current.get("pm10"),
            "time": current.get("time", ""),
        })
    return result


@st.cache_data(ttl=86400, show_spinner=False)
def get_monitoring_station_registry():
    """Load georeferenced monitoring posts; fall back to labelled locality centres."""
    candidate_urls = [
        "https://raw.githubusercontent.com/qazybekb/AirDatakz-OpenData/main/stations.geojson",
        "https://raw.githubusercontent.com/qazybekb/AirDatakz-OpenData/main/csv/stations.geojson",
    ]
    for url in candidate_urls:
        try:
            response = requests.get(url, headers=HEADERS, timeout=(5, 12))
            response.raise_for_status()
            geo = response.json()
            features = geo.get("features", []) if isinstance(geo, dict) else []
            stations = []
            for feature in features:
                geometry = feature.get("geometry") or {}
                props = feature.get("properties") or {}
                coords = geometry.get("coordinates") or []
                if len(coords) < 2:
                    continue
                lon0, lat0 = float(coords[0]), float(coords[1])
                if not (40.0 <= lat0 <= 56.5 and 45.0 <= lon0 <= 88.5):
                    continue
                source = str(props.get("source") or props.get("operator") or props.get("network") or "").strip()
                # Include only stations explicitly identified as part of the government network.
                if not source or not any(token in source.casefold() for token in ("kgmt", "kazhydromet", "kaz гидромет")):
                    continue
                stations.append({
                    "name": str(props.get("name") or props.get("station_name") or props.get("id") or "Пост мониторинга"),
                    "city": str(props.get("city") or "Казахстан"),
                    "lat": lat0, "lon": lon0,
                    "source": source or "Источник не указан в реестре",
                    "station_id": str(props.get("id") or props.get("station_id") or ""),
                    "exact": True,
                })
            if stations:
                # De-duplicate by station identity and coordinates.
                unique = {}
                for station in stations:
                    key = (station["name"].casefold(), round(station["lat"], 5), round(station["lon"], 5))
                    unique[key] = station
                return {"stations": list(unique.values()), "exact": True,
                        "source": "AirData.kz station registry (Kazhydromet network)"}
        except Exception:
            continue

    fallback = [{
        "name": f"Посты наблюдения · {name}", "city": name,
        "lat": lat0, "lon": lon0, "source": "Официальная сеть наблюдений; точка в центре населённого пункта",
        "station_id": "", "exact": False,
    } for name, lat0, lon0 in MONITORING_SETTLEMENT_FALLBACK]
    return {"stations": fallback, "exact": False,
            "source": "Kazhydromet monitoring-settlement list; approximate town-centre markers"}


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def aqi_color(value):
    value = numeric(value)
    if value is None:
        return "#8A9185"
    if value <= 50:
        return "#2E9D58"   # green
    if value <= 100:
        return "#E6C229"   # yellow
    if value <= 150:
        return "#F28C28"   # orange
    if value <= 200:
        return "#D94141"   # red
    if value <= 300:
        return "#713E9A"   # purple
    return "#7E0023"       # maroon


def aqi_category_ru(value):
    value = numeric(value)
    if value is None:
        return "Нет данных"
    if value <= 50:
        return "Низкий уровень · хороший"
    if value <= 100:
        return "Умеренный уровень"
    if value <= 150:
        return "Повышенный · чувствительные группы"
    if value <= 200:
        return "Высокий уровень"
    if value <= 300:
        return "Очень высокий уровень"
    return "Опасный уровень"


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
    """Classify the supplied modelled AQI; this is not a facility risk assessment."""
    current = air.get("current", {})
    us_aqi = numeric(current.get("us_aqi"))
    eu_aqi = numeric(current.get("european_aqi"))
    if us_aqi is not None:
        if us_aqi <= 50:
            return t("risk_low"), "green", "US AQI", us_aqi
        if us_aqi <= 100:
            return t("risk_mid"), "orange", "US AQI", us_aqi
        if us_aqi <= 150:
            return t("risk_sensitive"), "orange", "US AQI", us_aqi
        if us_aqi <= 200:
            return t("risk_high"), "red", "US AQI", us_aqi
        if us_aqi <= 300:
            return t("risk_very_high"), "red", "US AQI", us_aqi
        return t("risk_hazardous"), "red", "US AQI", us_aqi
    if eu_aqi is not None:
        if eu_aqi <= 20:
            return t("risk_low"), "green", "European AQI", eu_aqi
        if eu_aqi <= 40:
            return t("risk_fair"), "green", "European AQI", eu_aqi
        if eu_aqi <= 60:
            return t("risk_mid"), "orange", "European AQI", eu_aqi
        if eu_aqi <= 80:
            return t("risk_poor"), "orange", "European AQI", eu_aqi
        if eu_aqi <= 100:
            return t("risk_very_high"), "red", "European AQI", eu_aqi
        return t("risk_extreme"), "red", "European AQI", eu_aqi
    return t("risk_unknown"), "gray", "—", None


def current_hourly_value(data, key):
    """Return hourly value aligned with API current.time (used for CO2)."""
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    values = hourly.get(key, [])
    if not times or not values:
        return None
    target = data.get("current", {}).get("time")
    if target in times:
        idx = times.index(target)
        return numeric(values[idx]) if idx < len(values) else None
    return numeric(values[0])

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

# Prefer an enterprise result returned directly by the name search; otherwise
# use a normalized name match among the nearby OSM industrial objects.
q = re.sub(r"[^a-zа-яәіңғүұқөһ0-9]", "", factory_query.casefold())
factory_matches = []
if q:
    for obj in osm_data:
        name_key = re.sub(r"[^a-zа-яәіңғүұқөһ0-9]", "", obj.get("name", "").casefold())
        display_key = re.sub(r"[^a-zа-яәіңғүұқөһ0-9]", "", obj.get("display_name", "").casefold())
        # Do not treat a nearby office, government building, or generic place
        # returned by geocoding as an industrial enterprise.
        if obj.get("direct_search_result"):
            obj_type = f"{obj.get('type', '')}".casefold()
            industrial_terms = ("industrial", "works", "manufactur", "factory", "plant", "power", "mine", "quarry")
            if not any(term in obj_type for term in industrial_terms):
                continue
        if q in name_key or q in display_key or name_key in q:
            factory_matches.append(obj)

station_registry = get_monitoring_station_registry()
monitoring_stations = station_registry.get("stations", [])

# If the requested enterprise was located, request model data at its mapped
# coordinates. If not, keep the city-centre grid and label it explicitly.
assessment_lat, assessment_lon = lat, lon
assessment_name = city_name
assessment_is_factory = False
if factory_matches:
    selected_for_assessment = factory_matches[0]
    assessment_lat = float(selected_for_assessment["lat"])
    assessment_lon = float(selected_for_assessment["lon"])
    assessment_name = selected_for_assessment["name"]
    assessment_is_factory = True
    try:
        air_data = get_air_quality(assessment_lat, assessment_lon)
        weather_data = get_weather(assessment_lat, assessment_lon)
    except Exception:
        # Keep the already retrieved city data if point-level data is unavailable.
        assessment_lat, assessment_lon = lat, lon
        assessment_name = city_name
        assessment_is_factory = False

current_air = air_data.get("current", {})
current_weather = weather_data.get("current", {})
risk_text, risk_color, risk_source, risk_value = risk_label(air_data)

st.markdown(f"### {city_name} — {city_data.get('admin1', 'Kazakhstan')}")
st.markdown(f"<span class='eco-pill'>{t('model_notice')}</span>", unsafe_allow_html=True)
st.caption(t("official_notice"))

tabs = st.tabs([t("map"), t("pollution_map"), t("air"), t("wind"), t("company"), t("risk"), t("analysis"), t("team")])

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

    # Monitoring-post layer: exact post coordinates when the registry is available;
    # otherwise clearly labelled approximate settlement-centre markers.
    station_group = folium.FeatureGroup(name="Станции мониторинга / Monitoring network", show=True)
    for station in monitoring_stations:
        detail = (
            f"<b>{station['name']}</b><br>Населённый пункт: {station['city']}<br>"
            f"Источник: {station['source']}<br>"
            + ("Координаты поста из реестра." if station.get("exact") else
               "Приблизительная точка в центре населённого пункта; не точный адрес поста.")
        )
        folium.CircleMarker(
            location=[station["lat"], station["lon"]], radius=5,
            color="#246B8A", weight=1.5, fill=True,
            fill_color="#54A6C8", fill_opacity=0.95,
            tooltip=f"Станция мониторинга · {station['city']}",
            popup=folium.Popup(detail, max_width=320),
        ).add_to(station_group)
    station_group.add_to(fmap)

    folium.LayerControl(collapsed=False).add_to(fmap)
    st_folium(fmap, use_container_width=True, height=560, returned_objects=[])
    st.caption("Карта: ©️ OpenStreetMap contributors. " + t("map_regions"))
    if station_registry.get("exact"):
        st.caption(f"Слой станций: загружены координаты {len(monitoring_stations)} постов из реестра AirData.kz / Kazhydromet network.")
    else:
        st.caption("Слой мониторинга: показаны населённые пункты, где ведётся наблюдение; значки стоят примерно в центре города, а не по точному адресу каждого поста.")
    st.markdown("[Официальная интерактивная карта Казгидромета](https://www.kazhydromet.kz/en/interactive_cards) · [Реестр станций AirData.kz](https://github.com/qazybekb/AirDatakz-OpenData)")
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

# 2. Countrywide modelled pollution overview — one additional page only.
with tabs[1]:
    st.subheader(t("pollution_map"))
    st.markdown(
        "Цветные точки показывают текущую модельную оценку US AQI в выбранных городах. "
        "Это ориентир по городским координатам, а не измерение на каждом заводе или посту мониторинга."
    )
    try:
        with st.spinner("Загружаем модельные данные по городам Казахстана..."):
            national_air_points = get_national_air_overview()
    except Exception as national_exc:
        national_air_points = []
        st.warning("Не удалось загрузить общую карту загрязнения: " + str(national_exc)[:220])

    pollution_map = folium.Map(
        location=[48.0, 67.0], zoom_start=5, tiles="OpenStreetMap", control_scale=True
    )
    Fullscreen(position="topright").add_to(pollution_map)

    pollution_layer = folium.FeatureGroup(name="Модельный индекс качества воздуха (US AQI)", show=True)
    usable_points = []
    for point in national_air_points:
        aqi = numeric(point.get("aqi"))
        if aqi is None:
            continue
        usable_points.append(point)
        colour = aqi_color(aqi)
        popup_text = (
            f"<b>{point['name']}</b><br>US AQI: {aqi:.0f} — {aqi_category_ru(aqi)}<br>"
            f"PM2.5: {numeric(point.get('pm25')) if numeric(point.get('pm25')) is not None else '—'} µg/m³<br>"
            f"PM10: {numeric(point.get('pm10')) if numeric(point.get('pm10')) is not None else '—'} µg/m³<br>"
            f"Время модели: {point.get('time') or '—'}<br>"
            "Источник: Open-Meteo / CAMS, расчётная точка в городе."
        )
        folium.CircleMarker(
            location=[point["lat"], point["lon"]],
            radius=8 + min(aqi / 45.0, 7),
            color=colour, weight=2, fill=True, fill_color=colour, fill_opacity=0.82,
            tooltip=f"{point['name']} · AQI {aqi:.0f}",
            popup=folium.Popup(popup_text, max_width=330),
        ).add_to(pollution_layer)
    pollution_layer.add_to(pollution_map)

    station_layer_pollution = folium.FeatureGroup(name="Станции мониторинга", show=True)
    for station in monitoring_stations:
        popup = (
            f"<b>{station['name']}</b><br>{station['city']}<br>{station['source']}<br>"
            + ("Координаты поста из реестра." if station.get("exact") else
               "Приблизительная точка населённого пункта, не адрес поста.")
        )
        folium.CircleMarker(
            location=[station["lat"], station["lon"]], radius=4,
            color="#246B8A", weight=1, fill=True,
            fill_color="#54A6C8", fill_opacity=1,
            tooltip=f"Пост мониторинга · {station['city']}",
            popup=folium.Popup(popup, max_width=300),
        ).add_to(station_layer_pollution)
    station_layer_pollution.add_to(pollution_map)
    folium.LayerControl(collapsed=False).add_to(pollution_map)

    st_folium(pollution_map, use_container_width=True, height=590, returned_objects=[])
    st.markdown("#### Легенда качества воздуха · US AQI")
    legend_items = [
        ("#2E9D58", "0–50", "Низкий / хороший"),
        ("#E6C229", "51–100", "Умеренный"),
        ("#F28C28", "101–150", "Повышенный · чувствительные группы"),
        ("#D94141", "151–200", "Высокий"),
        ("#713E9A", "201–300", "Очень высокий"),
        ("#7E0023", "301+", "Опасный"),
    ]
    legend_html = "<div style='display:flex;flex-wrap:wrap;gap:10px 18px;margin:8px 0 14px 0;'>"
    for colour, band, label in legend_items:
        legend_html += (
            f"<div style='display:flex;align-items:center;gap:7px;min-width:180px;'>"
            f"<span style='display:inline-block;width:13px;height:13px;border-radius:50%;background:{colour};'></span>"
            f"<span style='font-size:13px;color:#34402C;'><b>{band}</b> — {label}</span></div>"
        )
    legend_html += "</div>"
    st.markdown(legend_html, unsafe_allow_html=True)
    if usable_points:
        ranked = sorted(usable_points, key=lambda item: numeric(item.get("aqi")) or -1, reverse=True)
        st.markdown("#### Города с наибольшим значением среди показанных точек")
        st.dataframe(pd.DataFrame([
            {"Город": item["name"], "US AQI": round(float(item["aqi"])),
             "PM2.5, µg/m³": round(float(item["pm25"]), 2) if numeric(item.get("pm25")) is not None else "—",
             "Оценка": aqi_category_ru(item["aqi"])}
            for item in ranked
        ]), use_container_width=True, hide_index=True)
    else:
        st.info("Сейчас нет доступных значений для окраски точек. Карта не подставляет вымышленные показатели.")
    st.caption(
        "Важно: сравниваются только представленные города и текущие модельные значения Open-Meteo / CAMS. "
        "Это не полный рейтинг загрязнения всех населённых пунктов и не официальный протокол измерений."
    )
    st.markdown("[Методика категорий US AQI — US EPA](https://www.airnow.gov/aqi/aqi-basics/) · "
                "[Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api)")


# 3. Air quality
with tabs[2]:
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
    co2_value = current_hourly_value(air_data, "carbon_dioxide")
    st.metric("CO₂ (углекислый газ)", f"{co2_value:.1f} ppm" if co2_value is not None else "—")
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
    st.caption("CO — угарный газ (carbon monoxide, µg/m³). CO₂ — углекислый газ (carbon dioxide, ppm); это отдельный часовой модельный показатель.")

# 3. Wind — animated map with moving wind particles and a forecast timeline
with tabs[3]:
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

    # Windy provides the animated wind field and its own forecast timeline.
    windy_url = (
        "https://embed.windy.com/embed.html?"
        f"lat={assessment_lat:.5f}&lon={assessment_lon:.5f}"
        f"&detailLat={assessment_lat:.5f}&detailLon={assessment_lon:.5f}"
        "&width=1000&height=600&zoom=6&level=surface&overlay=wind"
        "&product=ecmwf&menu=&message=&marker=true&calendar=now"
        "&pressure=true&type=map&location=coordinates&detail="
        "&metricWind=km%2Fh&metricTemp=%C2%B0C&radarRange=-1"
    )
    iframe = (
        '<iframe title="Animated wind map" '
        f'src="{windy_url}" '
        'style="width:100%;height:610px;border:0;border-radius:16px;" '
        'loading="lazy" allowfullscreen></iframe>'
    )
    components.html(iframe, height=620, scrolling=False)
    st.caption(t("wind_map_caption"))
    st.markdown("[Windy — интерактивная карта ветра](https://www.windy.com/) · [Open-Meteo Weather API](https://open-meteo.com/en/docs)")

# 5. Enterprise profile — extended only in the existing profile tab.
with tabs[4]:
    st.subheader(t("company"))
    if factory_matches:
        selected = factory_matches[0]
        st.markdown(f"### {selected['name']}")

        location_text = selected.get("display_name") or selected.get("operator") or city_name
        object_type = str(selected.get("type") or "Промышленный объект").replace("_", " ").strip()
        industry_map = {
            "chemical": "Химическая промышленность",
            "metal": "Металлургия / обработка металлов",
            "steel": "Чёрная металлургия / сталь",
            "mineral": "Минеральное сырьё / материалы",
            "food": "Пищевая промышленность",
            "power": "Энергетика",
            "oil": "Нефтегазовая промышленность",
            "mine": "Добывающая промышленность",
            "quarry": "Карьер / добыча сырья",
            "works": "Производственный объект",
            "industrial": "Промышленный объект (категория не уточнена)",
        }
        object_type_lower = object_type.casefold()
        industry_label = next((label for key, label in industry_map.items() if key in object_type_lower), object_type.title())

        detail_cols = st.columns(2)
        with detail_cols[0]:
            st.markdown("**Местоположение**")
            st.write(location_text)
            st.markdown("**Вид промышленности**")
            st.write(industry_label)
        with detail_cols[1]:
            st.markdown("**Координаты объекта**")
            st.write(f"{selected['lat']:.5f}, {selected['lon']:.5f}")
            st.markdown("**Оператор / организация**")
            st.write(selected.get("operator") or "Не указан в открытых картографических данных")
        if selected.get("website"):
            st.markdown(f"**Сайт:** [{selected['website']}]({selected['website']})")
        if selected.get("osm_type") and selected.get("osm_id"):
            st.markdown(
                f"[Открыть запись объекта в OpenStreetMap](https://www.openstreetmap.org/{selected['osm_type']}/{selected['osm_id']})"
            )
        st.caption("Источник названия и типа объекта: OpenStreetMap. Карта сообщества не является государственным реестром предприятий.")

        st.markdown("#### Выбросы и качество воздуха рядом с объектом")
        st.info(
            "Подтверждённый отчёт о фактических выбросах этого предприятия к приложению не подключён. "
            "Показатели ниже описывают модельное состояние атмосферного воздуха в координатах объекта, "
            "а не массу выбросов завода."
        )
        profile_pollutants = [
            ("PM2.5", "pm2_5", "µg/m³"), ("PM10", "pm10", "µg/m³"),
            ("NO₂", "nitrogen_dioxide", "µg/m³"), ("SO₂", "sulphur_dioxide", "µg/m³"),
            ("O₃", "ozone", "µg/m³"), ("CO", "carbon_monoxide", "µg/m³"),
        ]
        profile_cols = st.columns(3)
        for i, (label, key, unit) in enumerate(profile_pollutants):
            value = numeric(current_air.get(key))
            with profile_cols[i % 3]:
                st.metric(label, f"{value:.2f} {unit}" if value is not None else "—")
        st.caption("CO — угарный газ. Он не является CO₂. Значения получены из модели Open-Meteo / CAMS.")

        st.markdown("#### Ближайшие станции мониторинга")
        nearby_stations = sorted(
            monitoring_stations,
            key=lambda station: haversine_km(selected["lat"], selected["lon"], station["lat"], station["lon"])
        )[:3]
        if nearby_stations:
            for station in nearby_stations:
                distance = haversine_km(selected["lat"], selected["lon"], station["lat"], station["lon"])
                accuracy_note = "координаты поста из реестра" if station.get("exact") else "ориентировочная точка населённого пункта"
                st.markdown(
                    f"- **{station['name']}** — {station['city']}, примерно {distance:.1f} км "
                    f"({accuracy_note})"
                )
            if station_registry.get("exact"):
                st.caption("Координаты постов получены из реестра AirData.kz; доступность и актуальные показания конкретного поста уточняются в официальной карте Казгидромета.")
            else:
                st.caption("Точные координаты отдельных постов не загрузились. Показаны ближайшие населённые пункты, где ведётся мониторинг; расстояние ориентировочное.")
        else:
            st.write("Сведения о координатах ближайших постов сейчас недоступны.")
        st.markdown("[Официальная карта наблюдений Казгидромета](https://www.kazhydromet.kz/en/interactive_cards)")

        st.markdown("#### Изменение концентраций и сравнение периодов")
        hourly = air_data.get("hourly", {})
        times = hourly.get("time", [])
        profile_options = {
            "PM2.5": ("pm2_5", "µg/m³"),
            "PM10": ("pm10", "µg/m³"),
            "NO₂": ("nitrogen_dioxide", "µg/m³"),
            "SO₂": ("sulphur_dioxide", "µg/m³"),
            "O₃": ("ozone", "µg/m³"),
            "US AQI": ("us_aqi", "индекс"),
            "European AQI": ("european_aqi", "индекс"),
        }
        available_options = [label for label, (key, unit) in profile_options.items()
                             if len(hourly.get(key, [])) == len(times) and len(times) > 0]
        if available_options:
            choose_col, period_col = st.columns(2)
            with choose_col:
                chosen_pollutant = st.selectbox("Показатель", available_options, key="company_pollutant")
            with period_col:
                chosen_period = st.selectbox(
                    "Период прогноза",
                    ["Все доступные 48 часов", "Первые 24 часа", "Следующие 24 часа"],
                    key="company_period",
                )
            key, unit = profile_options[chosen_pollutant]
            values = hourly.get(key, [])
            chart_frame = pd.DataFrame({"Время": times, "Значение": values})
            chart_frame["Значение"] = pd.to_numeric(chart_frame["Значение"], errors="coerce")
            if chosen_period == "Первые 24 часа":
                chart_frame = chart_frame.iloc[:24]
            elif chosen_period == "Следующие 24 часа":
                chart_frame = chart_frame.iloc[24:48]
            else:
                chart_frame = chart_frame.iloc[:48]
            chart_frame = chart_frame.dropna()
            if not chart_frame.empty:
                profile_fig = px.line(
                    chart_frame, x="Время", y="Значение", markers=True,
                    title=f"{chosen_pollutant} · прогноз · {unit}",
                )
                profile_fig.update_traces(line_color=GREEN, marker_color=DARK)
                profile_fig.update_layout(paper_bgcolor=BG, plot_bgcolor="#fffef8", margin=dict(t=55, b=20))
                st.plotly_chart(profile_fig, use_container_width=True)

            if key not in ("us_aqi", "european_aqi") and len(values) >= 48:
                first_period = pd.to_numeric(pd.Series(values[:24]), errors="coerce").dropna()
                second_period = pd.to_numeric(pd.Series(values[24:48]), errors="coerce").dropna()
                compare_cols = st.columns(2)
                compare_cols[0].metric(
                    "Среднее за первые 24 часа",
                    f"{first_period.mean():.2f} {unit}" if not first_period.empty else "—",
                )
                compare_cols[1].metric(
                    "Среднее за следующие 24 часа",
                    f"{second_period.mean():.2f} {unit}" if not second_period.empty else "—",
                )
            st.caption("Доступно сравнение двух последовательных 24-часовых периодов прогноза. Это не исторический ряд фактических измерений.")
        else:
            st.info("Почасовой ряд для сравнения сейчас не предоставлен API.")
    else:
        st.warning(t("not_found"))
        st.write("Предприятие может отсутствовать в OpenStreetMap или быть записано под другим названием. Чтобы не приписывать экологические данные неверному объекту, карточка не подставляет случайное предприятие.")
        st.write("Фактические выбросы и ближайшие посты можно показывать только при подтверждённой связи с конкретным предприятием и станцией.")
        st.markdown("[Официальная карта наблюдений Казгидромета](https://www.kazhydromet.kz/en/interactive_cards)")

# 6. Environmental risk screening — retained as before
with tabs[5]:
    st.subheader(t("risk"))
    st.info(t("risk_detail_note"))
    point_label = t("risk_factory_point") if assessment_is_factory else t("risk_city_point")
    st.write(f"**{t('risk_site')}:** {assessment_name} — {point_label}")
    st.write(f"**{t('coordinates')}:** {assessment_lat:.5f}, {assessment_lon:.5f}")

    if risk_value is None:
        st.warning(t("risk_missing_notice"))
    else:
        metric_col, label_col = st.columns([1, 2])
        with metric_col:
            st.metric(risk_source, f"{risk_value:.0f}")
        with label_col:
            st.markdown(f"### {risk_text}")
            st.caption("AQI = modelled Air Quality Index at the selected coordinate.")
        if risk_color == "green":
            st.success(risk_text)
        elif risk_color == "orange":
            st.warning(risk_text)
        else:
            st.error(risk_text)

    st.markdown("#### " + t("risk_pollutants_title"))
    st.markdown(
        """
        <div style="background:#eef4e7;border:1px solid #d9e7ca;border-radius:14px;
                    padding:14px 16px;margin:8px 0 18px 0;color:#405536;">
          <b>Что означает «модельные данные»?</b><br>
          Это расчёт компьютером по атмосферной модели и метеорологическим данным.
          Это <b>не показания датчика</b>, не лабораторный анализ и не измерение выбросов завода.
          Поэтому ниже убран технический статус у каждой строки: источник и ограничение
          указаны один раз здесь.
        </div>
        """,
        unsafe_allow_html=True,
    )
    risk_pollutants = [
        ("PM2.5", "pm2_5", "µg/m³", "Мелкие частицы"),
        ("PM10", "pm10", "µg/m³", "Взвешенные частицы"),
        ("NO₂", "nitrogen_dioxide", "µg/m³", "Диоксид азота"),
        ("SO₂", "sulphur_dioxide", "µg/m³", "Диоксид серы"),
        ("O₃", "ozone", "µg/m³", "Озон"),
        ("CO", "carbon_monoxide", "µg/m³", "Угарный газ"),
        ("CO₂", "carbon_dioxide", "ppm", "Углекислый газ"),
    ]
    pollutant_values = []
    for pollutant_name, key, unit, description in risk_pollutants:
        value = numeric(current_air.get(key))
        if key == "carbon_dioxide":
            value = current_hourly_value(air_data, key)
        pollutant_values.append((pollutant_name, value, unit, description))

    available_values = [item for item in pollutant_values if item[1] is not None]
    if not available_values:
        st.info(t("data_missing"))
    else:
        # Display as compact cards, without a repetitive technical status column.
        for row_start in range(0, len(available_values), 3):
            cols = st.columns(3)
            for col, item in zip(cols, available_values[row_start:row_start + 3]):
                pollutant_name, value, unit, description = item
                with col:
                    st.markdown(
                        f"""
                        <div style="background:#fffef8;border:1px solid #e1e8d8;
                                    border-radius:16px;padding:18px 18px 16px 18px;
                                    min-height:132px;margin-bottom:12px;
                                    box-shadow:0 2px 8px rgba(60,80,40,.05);">
                          <div style="font-size:13px;color:#718064;font-weight:600;letter-spacing:.3px;">
                            {pollutant_name}
                          </div>
                          <div style="font-size:29px;font-weight:700;color:#426b31;margin:8px 0 3px 0;">
                            {value:.2f} <span style="font-size:14px;font-weight:500;color:#718064;">{unit}</span>
                          </div>
                          <div style="font-size:12px;color:#7b806f;">{description}</div>
                          <div style="font-size:11px;color:#8b927f;margin-top:9px;">Расчётная оценка</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # Only compare pollutants with the same unit (µg/m³); CO₂ in ppm is excluded.
    chart_rows = [
        {"Pollutant": name, "Concentration": value}
        for name, value, unit, _ in pollutant_values
        if value is not None and unit == "µg/m³"
    ]
    if chart_rows:
        chart_df = pd.DataFrame(chart_rows).sort_values("Concentration", ascending=True)
        risk_fig = px.bar(
            chart_df, x="Concentration", y="Pollutant", orientation="h",
            title="Концентрации загрязнителей · µg/m³",
            text_auto=".1f",
        )
        risk_fig.update_traces(marker_color=GREEN, textposition="outside", cliponaxis=False)
        risk_fig.update_layout(
            paper_bgcolor=BG, plot_bgcolor="#fffef8",
            font=dict(family="Roboto, Arial", color="#34402C"),
            margin=dict(l=10, r=35, t=55, b=15),
            xaxis_title="Концентрация, µg/m³", yaxis_title="",
            showlegend=False,
        )
        st.plotly_chart(risk_fig, use_container_width=True)

    st.caption(t("risk_aqi_legend"))
    st.write("Индекс AQI описывает краткосрочное качество воздуха по модели. Он не является проверкой соблюдения казахстанских нормативов и не доказывает, что конкретный завод вызвал загрязнение.")
    st.write("Для официального вывода нужны данные аккредитованных постов наблюдения, применимые нормативы Казахстана и подтверждённая методика оценки предприятия.")
    st.markdown(
    "[Методика US AQI — US EPA](https://www.airnow.gov/aqi/aqi-basics/) · "
    "[European AQI — EEA](https://www.eea.europa.eu/)"
)
