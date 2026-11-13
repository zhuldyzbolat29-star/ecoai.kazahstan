import math
import requests
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

# EcoAI Kazakhstan — учебный проект
st.set_page_config(
    page_title="EcoAI Kazakhstan",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BG = "#F6F6E9"
GREEN = "#5A9A3A"
DARK = "#365B2A"
PALE = "#E8F5D8"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Manrope', Arial, sans-serif; }}
    .stApp {{ background: {BG}; color: #24351E; }}
    [data-testid="stHeader"] {{ background: transparent; }}
    .block-container {{ max-width: 1320px; padding-top: 1.2rem; padding-bottom: 3rem; }}
    .eco-header {{ display:flex; align-items:center; gap:14px; padding:14px 0 22px; }}
    .eco-mark {{ width:48px; height:48px; border-radius:15px; display:flex; align-items:center;
      justify-content:center; background:{PALE}; color:{DARK}; font-size:27px; }}
    .eco-name {{ font-size:25px; font-weight:800; letter-spacing:-.7px; color:{DARK}; }}
    .eco-sub {{ color:#718267; font-size:12px; letter-spacing:1.5px; font-weight:700; }}
    .hero {{ background:linear-gradient(120deg,#E8F5D8,#F8F8EF); border:1px solid #DCE9CE;
      border-radius:24px; padding:28px 30px; margin-bottom:18px; }}
    .hero h1 {{ color:{DARK}; font-size:clamp(27px,4vw,42px); line-height:1.12; margin:0 0 9px; }}
    .hero p {{ color:#64745B; margin:0; font-size:15px; }}
    .section-title {{ color:{DARK}; font-size:21px; font-weight:800; margin:14px 0 8px; }}
    .metric-card {{ background:#FFFFFF; border:1px solid #E3E8D9; border-radius:18px;
      padding:17px 18px; min-height:112px; }}
    .metric-label {{ color:#74816C; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.6px; }}
    .metric-value {{ color:{DARK}; font-size:29px; font-weight:800; margin-top:7px; }}
    .metric-note {{ color:#87927F; font-size:11px; margin-top:2px; }}
    .source-note {{ color:#74816C; font-size:12px; }}
    div.stButton > button {{ background:{GREEN}; color:white; border:0; border-radius:12px;
      font-weight:700; min-height:44px; }}
    div.stButton > button:hover {{ background:{DARK}; color:white; border:0; }}
    div[data-testid="stTextInput"] input {{ border-radius:11px; }}
    div[data-testid="stTabs"] button {{ color:{DARK}; font-weight:700; }}
    .disclaimer {{ background:#FFF8E7; border:1px solid #F0DCA7; border-radius:13px;
      padding:12px 15px; color:#725C2D; font-size:12px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

LANG = {
    "Русский": {
        "tagline": "ЭКОЛОГИЧЕСКАЯ ИНФОРМАЦИОННАЯ ПЛАТФОРМА",
        "hero": "Данные об окружающей среде — понятнее и доступнее",
        "intro": "Исследуйте качество воздуха, погоду и промышленные объекты городов Казахстана.",
        "city": "Город Казахстана",
        "factory": "Название предприятия (необязательно)",
        "search": "НАЙТИ ИССЛЕДУЕМУЮ ТЕРРИТОРИЮ",
        "map": "Карта",
        "air": "Качество воздуха",
        "weather": "Погода и ветер",
        "industry": "Промышленные объекты",
        "analysis": "Анализ",
        "waiting": "Введите город и нажмите кнопку поиска.",
        "notfound": "Не удалось определить город. Проверьте написание названия.",
        "airtitle": "Текущие модельные показатели качества воздуха",
        "weathertitle": "Текущие погодные условия",
        "industrialtitle": "Объекты OpenStreetMap поблизости",
        "noindustry": "В OpenStreetMap не найдены объекты по этому запросу. Это не доказывает отсутствие предприятия.",
        "risk": "Ориентировочная категория AQI",
        "voice": "Голосовой помощник",
        "start": "Запустить голосовое управление",
        "disclaimer": "Важно: данные Open-Meteo — модельные оценки, а не показания официальных станций или датчиков у завода. OpenStreetMap не является полным официальным реестром предприятий. EcoAI — учебный проект.",
    },
    "Қазақша": {
        "tagline": "ЭКОЛОГИЯЛЫҚ АҚПАРАТТЫҚ ПЛАТФОРМА",
        "hero": "Қоршаған орта туралы деректер — түсінікті әрі қолжетімді",
        "intro": "Қазақстан қалаларының ауа сапасын, ауа райын және өнеркәсіп нысандарын зерттеңіз.",
        "city": "Қазақстан қаласы",
        "factory": "Кәсіпорын атауы (міндетті емес)",
        "search": "ЗЕРТТЕЛЕТІН АУМАҚТЫ ТАБУ",
        "map": "Карта",
        "air": "Ауа сапасы",
        "weather": "Ауа райы және жел",
        "industry": "Өнеркәсіп нысандары",
        "analysis": "Талдау",
        "waiting": "Қаланы енгізіп, іздеу түймесін басыңыз.",
        "notfound": "Қаланы анықтау мүмкін болмады. Атауын тексеріңіз.",
        "airtitle": "Ауа сапасының ағымдағы модельдік көрсеткіштері",
        "weathertitle": "Ағымдағы ауа райы",
        "industrialtitle": "OpenStreetMap маңындағы нысандар",
        "noindustry": "OpenStreetMap ішінде нысандар табылмады. Бұл кәсіпорын жоқ дегенді білдірмейді.",
        "risk": "AQI шамамен санаты",
        "voice": "Дауыстық көмекші",
        "start": "Дауыспен басқаруды бастау",
        "disclaimer": "Маңызды: Open-Meteo деректері — модельдік бағалар, зауыт жанындағы ресми станция немесе датчик өлшемдері емес. OpenStreetMap кәсіпорындардың толық ресми тізілімі емес. EcoAI — оқу жобасы.",
    },
    "English": {
        "tagline": "ENVIRONMENTAL INFORMATION PLATFORM",
        "hero": "Environmental data, made clearer and more accessible",
        "intro": "Explore air quality, weather and industrial locations across Kazakhstan.",
        "city": "City in Kazakhstan",
        "factory": "Enterprise name (optional)",
        "search": "SEARCH THIS AREA",
        "map": "Map",
        "air": "Air quality",
        "weather": "Weather & wind",
        "industry": "Industrial locations",
        "analysis": "Analysis",
        "waiting": "Enter a city and press search.",
        "notfound": "Could not locate the city. Check the spelling.",
        "airtitle": "Current modelled air-quality indicators",
        "weathertitle": "Current weather conditions",
        "industrialtitle": "Nearby OpenStreetMap locations",
        "noindustry": "No matching objects were found in OpenStreetMap. This does not prove that an enterprise is absent.",
        "risk": "Approximate AQI category",
        "voice": "Voice assistant",
        "start": "Start voice controls",
        "disclaimer": "Important: Open-Meteo values are model estimates, not official station or factory-site sensor measurements. OpenStreetMap is not a complete official register of enterprises. EcoAI is an educational project.",
    },
}

if "language" not in st.session_state:
    st.session_state.language = "Русский"
if "result" not in st.session_state:
    st.session_state.result = None

header_left, header_right = st.columns([5, 1])
with header_left:
    st.markdown(
        '<div class="eco-header"><div class="eco-mark">✳</div><div>'
        '<div class="eco-name">EcoAI Kazakhstan</div>'
        f'<div class="eco-sub">{LANG[st.session_state.language]["tagline"]}</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
with header_right:
    st.session_state.language = st.selectbox(
        "Language", list(LANG.keys()), index=list(LANG.keys()).index(st.session_state.language)
    )

T = LANG[st.session_state.language]
st.markdown(
    f'<div class="hero"><h1>{T["hero"]}</h1><p>{T["intro"]}</p></div>',
    unsafe_allow_html=True,
)

st.markdown(f'<div class="disclaimer">{T["disclaimer"]}</div>', unsafe_allow_html=True)
st.write("")

with st.form("eco_search", clear_on_submit=False):
    c1, c2 = st.columns([1, 1])
    with c1:
        city = st.text_input(T["city"], placeholder="Тараз / Алматы / Теміртау / Astana")
    with c2:
        enterprise = st.text_input(T["factory"], placeholder="Казфосфат / Qarmet")
    submitted = st.form_submit_button(T["search"], use_container_width=True)

def get_json(url, params=None, timeout=25):
    response = requests.get(url, params=params, timeout=timeout, headers={"User-Agent": "EcoAI-Kazakhstan-Student/1.0"})
    response.raise_for_status()
    return response.json()

def locate_city(name):
    data = get_json(
        "https://geocoding-api.open-meteo.com/v1/search",
        {"name": name, "count": 10, "language": "ru", "format": "json"},
    )
    results = data.get("results", [])
    matches = [x for x in results if x.get("country_code") == "KZ"]
    return matches[0] if matches else None

def get_air(lat, lon):
    return get_json(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
        {
            "latitude": lat, "longitude": lon,
            "current": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi",
            "hourly": "pm10,pm2_5,us_aqi",
            "forecast_days": 1,
            "timezone": "auto",
        },
    )

def get_weather(lat, lon):
    return get_json(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": lat, "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,wind_direction_10m",
            "hourly": "temperature_2m,wind_speed_10m",
            "forecast_days": 1,
            "timezone": "auto",
        },
    )

def get_industry(lat, lon, search_name=""):
    # Поиск ограничен радиусом 25 км; OSM может содержать неполные сведения.
    query = f"""
    [out:json][timeout:20];
    (
      nwr(around:25000,{lat},{lon})["industrial"];
      nwr(around:25000,{lat},{lon})["man_made"="works"];
      nwr(around:25000,{lat},{lon})["landuse"="industrial"];
    );
    out center tags;
    """
    try:
        data = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
            timeout=30,
            headers={"User-Agent": "EcoAI-Kazakhstan-Student/1.0"},
        )
        data.raise_for_status()
        elements = data.json().get("elements", [])
    except Exception:
        return []
    found = []
    needle = search_name.casefold().strip()
    for item in elements:
        tags = item.get("tags", {})
        name = tags.get("name") or tags.get("name:ru") or tags.get("operator") or tags.get("industrial") or "Промышленный объект без названия"
        if needle and needle not in name.casefold() and needle not in str(tags).casefold():
            continue
        center = item.get("center", item)
        if "lat" in center and "lon" in center:
            found.append({"name": name, "lat": center["lat"], "lon": center["lon"], "type": tags.get("industrial", tags.get("man_made", tags.get("landuse", "industrial")))})
    return found[:150]

def compass(degrees):
    names = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]
    return names[int((float(degrees) + 22.5) // 45) % 8]

if submitted:
    if not city.strip():
        st.warning(T["waiting"])
    else:
        with st.spinner("Получаем данные из открытых источников…"):
            try:
                place = locate_city(city.strip())
                if not place:
                    st.error(T["notfound"])
                    st.session_state.result = None
                else:
                    lat, lon = float(place["latitude"]), float(place["longitude"])
                    air = get_air(lat, lon)
                    weather = get_weather(lat, lon)
                    objects = get_industry(lat, lon, enterprise.strip())
                    st.session_state.result = {
                        "place": place, "lat": lat, "lon": lon,
                        "air": air, "weather": weather, "objects": objects,
                        "enterprise": enterprise.strip(),
                    }
            except requests.RequestException as exc:
                st.error(f"Ошибка подключения к открытому источнику: {exc}")
            except Exception as exc:
                st.error(f"Не удалось обработать ответ источника: {exc}")

result = st.session_state.result

if result:
    place = result["place"]
    air = result["air"]
    weather = result["weather"]
    current_air = air.get("current", {})
    current_weather = weather.get("current", {})
    city_label = f'{place.get("name", city)}, {place.get("admin1", "Казахстан")}'
    st.markdown(f'<div class="section-title">{city_label}</div>', unsafe_allow_html=True)

    def metric(label, value, unit="", note=""):
        shown = "—" if value is None else f"{value}{unit}"
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">{label}</div>'
            f'<div class="metric-value">{shown}</div><div class="metric-note">{note}</div></div>',
            unsafe_allow_html=True,
        )

    tabs = st.tabs([T["map"], T["air"], T["weather"], T["industry"], T["analysis"]])

    with tabs[0]:
        st.markdown(f'<div class="section-title">{T["map"]}</div>', unsafe_allow_html=True)
        points = [{"name": city_label, "lat": result["lat"], "lon": result["lon"], "kind": "Выбранный город"}]
        points.extend(result["objects"])
        map_df = pd.DataFrame(points)
        st.map(map_df, latitude="lat", longitude="lon")
        st.caption("Карта показывает найденные точки, а не официальные границы экологических зон.")
        if len(map_df) > 1:
            st.dataframe(map_df[["name", "lat", "lon"]], use_container_width=True, hide_index=True)

    with tabs[1]:
        st.markdown(f'<div class="section-title">{T["airtitle"]}</div>', unsafe_allow_html=True)
        pollutants = [
            ("PM2.5", "pm2_5", "µg/m³"), ("PM10", "pm10", "µg/m³"),
            ("CO", "carbon_monoxide", "µg/m³"), ("NO₂", "nitrogen_dioxide", "µg/m³"),
            ("SO₂", "sulphur_dioxide", "µg/m³"), ("O₃", "ozone", "µg/m³"),
            ("US AQI", "us_aqi", ""),
        ]
        cols = st.columns(4)
        for i, (label, key, unit) in enumerate(pollutants):
            with cols[i % 4]:
                metric(label, current_air.get(key), f" {unit}" if unit else "", "модельная оценка")
        aqi = current_air.get("us_aqi")
        if aqi is not None:
            if aqi <= 50:
                category = "Хорошее"
            elif aqi <= 100:
                category = "Умеренное"
            elif aqi <= 150:
                category = "Нездоровое для чувствительных групп"
            elif aqi <= 200:
                category = "Нездоровое"
            elif aqi <= 300:
                category = "Очень нездоровое"
            else:
                category = "Опасное"
            st.info(f'{T["risk"]}: **{category}** (US AQI {aqi})')
        hourly = air.get("hourly", {})
        if hourly.get("time") and hourly.get("pm2_5"):
            chart_df = pd.DataFrame({
                "Время": pd.to_datetime(hourly["time"]),
                "PM2.5": hourly["pm2_5"],
                "PM10": hourly.get("pm10", [None] * len(hourly["time"])),
            })
            st.plotly_chart(px.line(chart_df, x="Время", y=["PM2.5", "PM10"], markers=True, title="Почасовая динамика частиц"), use_container_width=True)

    with tabs[2]:
        st.markdown(f'<div class="section-title">{T["weathertitle"]}</div>', unsafe_allow_html=True)
        weather_items = [
            ("Температура", "temperature_2m", " °C"),
            ("Ощущается как", "apparent_temperature", " °C"),
            ("Влажность", "relative_humidity_2m", " %"),
            ("Скорость ветра", "wind_speed_10m", " км/ч"),
            ("Направление ветра", "wind_direction_10m", "°"),
        ]
        cols = st.columns(3)
        for i, (label, key, unit) in enumerate(weather_items):
            with cols[i % 3]:
                val = current_weather.get(key)
                note = compass(val) if key == "wind_direction_10m" and val is not None else "Open-Meteo"
                metric(label, val, unit, note)
        st.caption("Скорость ветра и температура получены из прогноза Open-Meteo; это не данные локальной метеостанции.")

    with tabs[3]:
        st.markdown(f'<div class="section-title">{T["industrialtitle"]}</div>', unsafe_allow_html=True)
        objects = result["objects"]
        if objects:
            st.success(f"Найдено объектов: {len(objects)}")
            st.dataframe(pd.DataFrame(objects), use_container_width=True, hide_index=True)
        else:
            st.info(T["noindustry"])
        st.caption("Источник: OpenStreetMap / Overpass API. Поиск охватывает окрестность около 25 км.")

    with tabs[4]:
        st.markdown(f'<div class="section-title">{T["analysis"]}</div>', unsafe_allow_html=True)
        st.write("Сводка строится только на доступных модельных показателях и объектах открытой карты.")
        if aqi is not None:
            st.metric("US AQI", aqi, help="Индекс качества воздуха по модельным данным Open-Meteo.")
        st.write("**Ограничения:** приложение не измеряет выбросы конкретного предприятия и не устанавливает причинную связь между заводом и качеством воздуха.")

    st.markdown("---")
    st.markdown(f'<div class="section-title">{T["voice"]}</div>', unsafe_allow_html=True)
    voice_text = (
        f"{city_label}. "
        f"PM2.5: {current_air.get('pm2_5', 'нет данных')}. "
        f"PM10: {current_air.get('pm10', 'нет данных')}. "
        f"US AQI: {current_air.get('us_aqi', 'нет данных')}. "
        f"Температура: {current_weather.get('temperature_2m', 'нет данных')} градусов. "
        f"Ветер: {current_weather.get('wind_speed_10m', 'нет данных')} километров в час."
    )
    speech_lang = {"Русский": "ru-RU", "Қазақша": "kk-KZ", "English": "en-US"}[st.session_state.language]
    safe_text = voice_text.replace("\\", "\\\\").replace("`", "'").replace("</", "<\\/")
    components.html(
        f"""
        <div style="font-family:Arial,sans-serif;background:#E8F5D8;border:1px solid #D5E7C5;border-radius:14px;padding:14px;color:#365B2A">
          <div style="font-weight:700;margin-bottom:8px">EcoAI Voice</div>
          <button id="speak" style="background:#5A9A3A;color:white;border:0;border-radius:9px;padding:10px 14px;margin-right:8px;cursor:pointer">▶️ Озвучить сводку</button>
          <button id="stop" style="background:#fff;color:#365B2A;border:1px solid #b8cda8;border-radius:9px;padding:10px 14px;cursor:pointer">■ Остановить</button>
          <div id="status" style="font-size:12px;margin-top:9px">Нажмите «Озвучить сводку».</div>
        </div>
        <script>
          const summary = `{safe_text}`;
          const lang = "{speech_lang}";
          document.getElementById("speak").onclick = () => {{
            if (!("speechSynthesis" in window)) {{
              document.getElementById("status").textContent = "Озвучивание не поддерживается этим браузером.";
              return;
            }}
            window.speechSynthesis.cancel();
            const msg = new SpeechSynthesisUtterance(summary);
            msg.lang = lang;
            msg.rate = 0.92;
            window.speechSynthesis.speak(msg);
            document.getElementById("status").textContent = "Сводка озвучивается.";
          }};
          document.getElementById("stop").onclick = () => {{
            if ("speechSynthesis" in window) window.speechSynthesis.cancel();
            document.getElementById("status").textContent = "Озвучивание остановлено.";
          }};
        </script>
        """,
        height=125,
    )
else:
    st.info(T["waiting"])

st.markdown("---")
st.caption("EcoAI Kazakhstan · Учебный проект · Открытые источники: Open-Meteo и OpenStreetMap")
