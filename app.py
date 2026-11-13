import math
from datetime import datetime

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Roboto','Arial',sans-serif; }}
    .stApp {{ background:{BG}; }}
    [data-testid="stHeader"] {{ background:rgba(246,246,233,.96); }}
    h1,h2,h3 {{ color:{DARK}; font-weight:700; }}
    p,label,span {{ color:#34402C; }}
    div.stButton>button,div.stFormSubmitButton>button {{
      background:{GREEN};color:white;border:0;border-radius:12px;
      min-height:44px;font-weight:600;
    }}
    div.stButton>button:hover,div.stFormSubmitButton>button:hover {{
      background:{DARK};color:white;border:0;
    }}
    div[data-testid="stTextInput"] input {{
      background:#fffef8;border:1px solid #d4dfc8;border-radius:10px;
    }}
    .eco-card {{background:#fffef8;border:1px solid #e0e7d7;border-radius:16px;padding:18px;margin:8px 0;}}
    .eco-muted {{color:#66735e;font-size:.88rem;}}
    .eco-pill {{display:inline-block;background:{LIGHT};color:{DARK};padding:5px 10px;border-radius:20px;font-size:.82rem;font-weight:600;}}
    .brand {{color:{DARK};font-size:1.7rem;font-weight:800;letter-spacing:.04em;}}
    footer {{visibility:hidden;}}
    </style>
    """,
    unsafe_allow_html=True,
)

LANGS = {"Русский": "ru", "Қазақша": "kk", "English": "en"}
TEXT = {
    "ru": {
        "language":"Язык","login_title":"Добро пожаловать в ECO AI",
        "login_sub":"Экологическая информационная платформа Казахстана",
        "login":"Логин (демо)","password":"Пароль (демо)","continue":"Продолжить",
        "city":"Город Казахстана","factory":"Название предприятия / завода",
        "search":"Найти предприятие","map":"Карта","air":"Загрязнение воздуха",
        "wind":"Ветер и погода","company":"Карточка предприятия",
        "risk":"Экологические риски","analysis":"Анализ данных",
        "no_search":"Введите город и нажмите кнопку поиска.",
        "not_found":"Точное совпадение предприятия в открытых картографических данных не найдено.",
        "data_missing":"Подтверждённые измерения для конкретного предприятия не подключены.",
        "model_notice":"Модельные данные Open-Meteo/CAMS, не прямое измерение у завода.",
        "official_notice":"Официальные измерения показываются только при наличии подтверждённого источника.",
        "risk_low":"Низкий модельный индикатор","risk_mid":"Умеренный модельный индикатор",
        "risk_high":"Повышенный модельный индикатор","risk_unknown":"Недостаточно данных для оценки",
        "no_factory":"Предприятие не найдено среди объектов OpenStreetMap в выбранной окрестности.",
        "osm_found":"Промышленные объекты OpenStreetMap в окрестности города",
        "disclaimer":"ECO AI — информационный и учебный проект. Модельные данные не доказывают, что конкретный завод является источником загрязнения.",
        "temperature":"Температура","humidity":"Влажность","wind_speed":"Скорость ветра",
        "wind_dir":"Направление ветра","aqi":"Индекс качества воздуха",
        "factory_type":"Тип объекта","coordinates":"Координаты",
        "search_error":"Не удалось получить данные:","map_note":"Точки — региональные центры, выбранный город и объекты OpenStreetMap. Это не административные границы.",
    },
    "kk": {
        "language":"Тіл","login_title":"ECO AI платформасына қош келдіңіз",
        "login_sub":"Қазақстанның экологиялық ақпараттық платформасы",
        "login":"Логин (демо)","password":"Құпиясөз (демо)","continue":"Жалғастыру",
        "city":"Қазақстан қаласы","factory":"Кәсіпорын / зауыт атауы",
        "search":"Кәсіпорынды іздеу","map":"Карта","air":"Ауа ластануы",
        "wind":"Жел және ауа райы","company":"Кәсіпорын картасы",
        "risk":"Экологиялық тәуекелдер","analysis":"Деректерді талдау",
        "no_search":"Қаланы енгізіп, іздеу түймесін басыңыз.",
        "not_found":"Ашық карта деректерінен кәсіпорынның дәл сәйкестігі табылмады.",
        "data_missing":"Нақты кәсіпорын бойынша расталған өлшемдер қосылмаған.",
        "model_notice":"Open-Meteo/CAMS модельдік деректері, зауыт жанындағы тікелей өлшем емес.",
        "official_notice":"Ресми өлшемдер тек расталған дереккөз болғанда көрсетіледі.",
        "risk_low":"Модельдік көрсеткіш төмен","risk_mid":"Модельдік көрсеткіш орташа",
        "risk_high":"Модельдік көрсеткіш жоғары","risk_unknown":"Бағалау үшін дерек жеткіліксіз",
        "no_factory":"Таңдалған аумақта OpenStreetMap деректерінен кәсіпорын табылмады.",
        "osm_found":"Қала маңындағы OpenStreetMap өнеркәсіп нысандары",
        "disclaimer":"ECO AI — ақпараттық және оқу жобасы. Модельдік деректер нақты зауыттың ластау көзі екенін дәлелдемейді.",
        "temperature":"Температура","humidity":"Ылғалдылық","wind_speed":"Жел жылдамдығы",
        "wind_dir":"Жел бағыты","aqi":"Ауа сапасының индексі",
        "factory_type":"Нысан түрі","coordinates":"Координаттар",
        "search_error":"Деректерді алу мүмкін болмады:","map_note":"Нүктелер — өңірлік орталықтар, таңдалған қала және OpenStreetMap нысандары. Бұл әкімшілік шекаралар емес.",
    },
    "en": {
        "language":"Language","login_title":"Welcome to ECO AI",
        "login_sub":"Environmental information platform for Kazakhstan",
        "login":"Login (demo)","password":"Password (demo)","continue":"Continue",
        "city":"Kazakhstan city","factory":"Enterprise / factory name",
        "search":"Find enterprise","map":"Map","air":"Air quality",
        "wind":"Wind and weather","company":"Enterprise profile",
        "risk":"Environmental risks","analysis":"Data analysis",
        "no_search":"Enter a city and press Search.",
        "not_found":"No exact enterprise match was found in open map data.",
        "data_missing":"Verified measurements for this specific enterprise are not connected.",
        "model_notice":"Open-Meteo/CAMS model data, not a direct measurement at the factory.",
        "official_notice":"Official measurements are shown only when a verified source is available.",
        "risk_low":"Low model indicator","risk_mid":"Moderate model indicator",
        "risk_high":"Elevated model indicator","risk_unknown":"Not enough data to assess",
        "no_factory":"No enterprise was found in OpenStreetMap within the selected area.",
        "osm_found":"OpenStreetMap industrial objects near the city",
        "disclaimer":"ECO AI is an informational and educational project. Model data do not prove that a specific factory is a pollution source.",
        "temperature":"Temperature","humidity":"Humidity","wind_speed":"Wind speed",
        "wind_dir":"Wind direction","aqi":"Air quality index",
        "factory_type":"Object type","coordinates":"Coordinates",
        "search_error":"Could not retrieve data:","map_note":"Points show regional centres, the selected city and OpenStreetMap objects. These are not administrative boundaries.",
    },
}

REGIONS = [
    ("Семей",50.411,80.227),("Кокшетау",53.283,69.383),("Актобе",50.283,57.167),
    ("Қонаев",43.883,77.067),("Атырау",47.117,51.883),("Өскемен",49.948,82.628),
    ("Тараз",42.900,71.367),("Талдықорған",45.017,78.367),("Орал",51.233,51.367),
    ("Қарағанды",49.800,73.100),("Қостанай",53.217,63.633),("Қызылорда",44.850,65.483),
    ("Ақтау",43.650,51.167),("Павлодар",52.300,76.950),("Петропавл",54.867,69.150),
    ("Түркістан",43.300,68.250),("Жезқазған",47.783,67.717),("Алматы",43.238,76.945),
    ("Астана",51.169,71.449),("Шымкент",42.341,69.590),
]

HEADERS = {"User-Agent":"EcoAI-Kazakhstan-StudentProject/1.0 (educational demo)"}
SESSION = requests.Session()
retry = Retry(total=2, connect=2, read=1, status=1, backoff_factor=.4,
              status_forcelist=(429,500,502,503,504), allowed_methods=frozenset(["GET","POST"]))
adapter = HTTPAdapter(max_retries=retry)
SESSION.mount("https://", adapter)
SESSION.mount("http://", adapter)

CITY_FALLBACKS = {
    "тараз":("Taraz",42.9006,71.3667,"Zhambyl Region"),
    "taraz":("Taraz",42.9006,71.3667,"Zhambyl Region"),
    "темиртау":("Temirtau",50.0549,72.9646,"Karaganda Region"),
    "temirtau":("Temirtau",50.0549,72.9646,"Karaganda Region"),
    "астана":("Astana",51.1694,71.4491,"Astana"),
    "astana":("Astana",51.1694,71.4491,"Astana"),
    "алматы":("Almaty",43.2389,76.8897,"Almaty"),
    "almaty":("Almaty",43.2389,76.8897,"Almaty"),
    "шымкент":("Shymkent",42.3417,69.5901,"Shymkent"),
    "shymkent":("Shymkent",42.3417,69.5901,"Shymkent"),
    "караганда":("Karaganda",49.8064,73.0855,"Karaganda Region"),
    "karaganda":("Karaganda",49.8064,73.0855,"Karaganda Region"),
    "актобе":("Aktobe",50.2839,57.1670,"Aktobe Region"),
    "aktobe":("Aktobe",50.2839,57.1670,"Aktobe Region"),
    "павлодар":("Pavlodar",52.2873,76.9674,"Pavlodar Region"),
    "pavlodar":("Pavlodar",52.2873,76.9674,"Pavlodar Region"),
    "атырау":("Atyrau",47.1164,51.8833,"Atyrau Region"),
    "atyrau":("Atyrau",47.1164,51.8833,"Atyrau Region"),
    "семей":("Semey",50.4111,80.2275,"Abai Region"),
    "костанай":("Kostanay",53.2144,63.6246,"Kostanay Region"),
    "кызылорда":("Kyzylorda",44.8488,65.4823,"Kyzylorda Region"),
    "актау":("Aktau",43.6532,51.1975,"Mangystau Region"),
    "кокшетау":("Kokshetau",53.2833,69.3833,"Akmola Region"),
}

def tr(key):
    return TEXT[st.session_state.get("lang","ru")].get(key,key)

@st.cache_data(ttl=3600, show_spinner=False)
def geocode_city(city):
    key = city.strip().casefold()
    candidates = [city.strip()]
    if key in CITY_FALLBACKS:
        candidates.insert(0, CITY_FALLBACKS[key][0])
    last_error = None
    for candidate in dict.fromkeys(candidates):
        try:
            r = SESSION.get("https://geocoding-api.open-meteo.com/v1/search",
                params={"name":candidate,"count":20,"language":"en","format":"json","countryCode":"KZ"},
                headers=HEADERS,timeout=(8,20))
            r.raise_for_status()
            for place in r.json().get("results",[]):
                if place.get("country_code","").upper()=="KZ":
                    return place
        except requests.RequestException as e:
            last_error = e
    if key in CITY_FALLBACKS:
        name,lat,lon,region = CITY_FALLBACKS[key]
        return {"name":name,"latitude":lat,"longitude":lon,"country_code":"KZ","admin1":region,"is_fallback":True}
    if last_error:
        raise last_error
    raise ValueError("Город не найден в Казахстане. Проверьте написание.")

@st.cache_data(ttl=900, show_spinner=False)
def get_air(lat,lon):
    params={"latitude":lat,"longitude":lon,
      "current":"european_aqi,us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone",
      "hourly":"pm10,pm2_5,nitrogen_dioxide,sulphur_dioxide,ozone",
      "forecast_days":2,"timezone":"auto"}
    r=SESSION.get("https://air-quality-api.open-meteo.com/v1/air-quality",
                  params=params,headers=HEADERS,timeout=(8,30))
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=900, show_spinner=False)
def get_weather(lat,lon):
    params={"latitude":lat,"longitude":lon,
      "current":"temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
      "hourly":"wind_speed_10m,wind_direction_10m","forecast_days":2,"timezone":"auto"}
    r=SESSION.get("https://api.open-meteo.com/v1/forecast",
                  params=params,headers=HEADERS,timeout=(8,30))
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=1800, show_spinner=False)
def get_industry(lat,lon):
    query=f"""
    [out:json][timeout:20];
    (node(around:25000,{lat},{lon})["name"]["industrial"];
     way(around:25000,{lat},{lon})["name"]["industrial"];
     relation(around:25000,{lat},{lon})["name"]["industrial"];
     node(around:25000,{lat},{lon})["name"]["man_made"="works"];
     way(around:25000,{lat},{lon})["name"]["man_made"="works"];
     relation(around:25000,{lat},{lon})["name"]["man_made"="works"];
     node(around:25000,{lat},{lon})["name"]["landuse"="industrial"];
     way(around:25000,{lat},{lon})["name"]["landuse"="industrial"];
     relation(around:25000,{lat},{lon})["name"]["landuse"="industrial"];);
    out center tags;
    """
    for endpoint in ("https://overpass-api.de/api/interpreter","https://overpass.kumi.systems/api/interpreter"):
        try:
            r=SESSION.post(endpoint,data=query,headers=HEADERS,timeout=(8,28))
            r.raise_for_status()
            out={}
            for item in r.json().get("elements",[]):
                tags=item.get("tags",{})
                name=tags.get("name")
                center=item.get("center",item)
                if name and center.get("lat") is not None and center.get("lon") is not None:
                    obj={"name":name,"lat":float(center["lat"]),"lon":float(center["lon"]),
                         "type":tags.get("industrial") or tags.get("man_made") or tags.get("landuse") or "industrial",
                         "operator":tags.get("operator","Не указан в OSM"),
                         "website":tags.get("website",""),"osm_type":item.get("type",""),"osm_id":item.get("id","")}
                    out[(name.casefold(),round(obj["lat"],4),round(obj["lon"],4))]=obj
            return list(out.values())
        except (requests.RequestException,ValueError):
            continue
    return []

def num(v):
    try:
        x=float(v)
        return x if math.isfinite(x) else None
    except (TypeError,ValueError):
        return None

def compass(deg):
    if deg is None: return "—"
    return ["N","NE","E","SE","S","SW","W","NW"][int((float(deg)+22.5)//45)%8]

def get_risk(air):
    cur=air.get("current",{})
    value=num(cur.get("us_aqi"))
    source="US AQI"
    if value is None:
        value=num(cur.get("european_aqi")); source="European AQI"
    if value is None: return tr("risk_unknown"),"gray",None,source
    if source=="US AQI":
        band="low" if value<=50 else "mid" if value<=100 else "high"
    else:
        band="low" if value<=20 else "mid" if value<=40 else "high"
    return tr({"low":"risk_low","mid":"risk_mid","high":"risk_high"}[band]),band,value,source

for key,default in {
    "stage":"intro","lang":"ru","city_result":None,"air":{},"weather":{},
    "objects":[],"city_query":"","factory_query":"","api_warnings":[]
}.items():
    if key not in st.session_state: st.session_state[key]=default

def header():
    a,b=st.columns([5,1])
    with a:
        st.markdown('<div class="brand">◈ ECO AI KAZAKHSTAN</div>',unsafe_allow_html=True)
    with b:
        if st.button("← Home",use_container_width=True):
            st.session_state.stage="login"; st.rerun()
    st.divider()

if st.session_state.stage=="intro":
    st.markdown("<div style='height:7vh'></div>",unsafe_allow_html=True)
    _,mid,_=st.columns([1,2,1])
    with mid:
        st.markdown(f"""
        <div style="background:{BG};text-align:center;padding:50px 10px;border-radius:22px">
        <div style="font-size:100px;color:{GREEN};line-height:1">❧</div>
        <div style="font-size:46px;font-weight:800;color:{DARK}">ECO AI</div>
        <div style="font-size:18px;letter-spacing:5px;color:{DARK}">KAZAKHSTAN</div>
        </div>""",unsafe_allow_html=True)
        if st.button("Продолжить / Continue / Жалғастыру",use_container_width=True):
            st.session_state.stage="login"; st.rerun()
    st.stop()

if st.session_state.stage=="login":
    header()
    _,mid,_=st.columns([1,1.5,1])
    with mid:
        st.markdown(f"<h2 style='text-align:center'>{tr('login_title')}</h2>",unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center'>{tr('login_sub')}</p>",unsafe_allow_html=True)
        lang_label=st.selectbox(tr("language"),list(LANGS),index=list(LANGS.values()).index(st.session_state.lang),key="login_lang")
        st.session_state.lang=LANGS[lang_label]
        st.text_input(tr("login"),key="demo_login")
        st.text_input(tr("password"),type="password",key="demo_password")
        if st.button(tr("continue"),use_container_width=True):
            st.session_state.stage="app"; st.rerun()
        st.caption("Демо-вход: логин и пароль не проверяются и не сохраняются.")
    st.stop()

header()
with st.sidebar:
    st.markdown("### ECO AI")
    label=st.selectbox(tr("language"),list(LANGS),index=list(LANGS.values()).index(st.session_state.lang),key="main_lang")
    if LANGS[label]!=st.session_state.lang:
        st.session_state.lang=LANGS[label]; st.rerun()
    st.caption("Open-Meteo · CAMS · OpenStreetMap")

st.markdown(f"## {tr('search')}")
with st.form("search_form"):
    c1,c2=st.columns(2)
    city_in=c1.text_input(tr("city"),value=st.session_state.city_query,placeholder="Например: Тараз")
    factory_in=c2.text_input(tr("factory"),value=st.session_state.factory_query,placeholder="Например: Казфосфат")
    go=st.form_submit_button(tr("search"),use_container_width=True)

if go:
    if not city_in.strip():
        st.error(tr("no_search"))
    else:
        warnings=[]
        with st.spinner("Загружаем данные из открытых источников..."):
            try:
                place=geocode_city(city_in.strip())
                latitude,longitude=float(place["latitude"]),float(place["longitude"])
                try: air=get_air(latitude,longitude)
                except requests.RequestException as e: air={}; warnings.append("Air Quality API: "+type(e).__name__)
                try: weather=get_weather(latitude,longitude)
                except requests.RequestException as e: weather={}; warnings.append("Weather API: "+type(e).__name__)
                try: objects=get_industry(latitude,longitude)
                except Exception as e: objects=[]; warnings.append("OpenStreetMap: "+type(e).__name__)
                st.session_state.city_result=place
                st.session_state.air=air
                st.session_state.weather=weather
                st.session_state.objects=objects
                st.session_state.city_query=city_in.strip()
                st.session_state.factory_query=factory_in.strip()
                st.session_state.api_warnings=warnings
                st.success(f"{place['name']} — {latitude:.4f}, {longitude:.4f}")
            except (requests.RequestException,ValueError,KeyError,TypeError) as e:
                st.error(f"{tr('search_error')} {e}")

place=st.session_state.city_result
if not place:
    st.info(tr("no_search"))
    st.markdown(f"<div class='eco-card'>{tr('disclaimer')}</div>",unsafe_allow_html=True)
    st.stop()

lat,lon=float(place["latitude"]),float(place["longitude"])
city=place["name"]
air=st.session_state.air or {}
weather=st.session_state.weather or {}
objects=st.session_state.objects or []
query=st.session_state.factory_query.strip().casefold()
matches=[o for o in objects if query in o["name"].casefold()] if query else []
shown=matches if matches else objects[:100]
current_air=air.get("current",{})
current_weather=weather.get("current",{})
risk_text,risk_band,risk_value,risk_source=get_risk(air)

st.markdown(f"### {city} — {place.get('admin1','Kazakhstan')}")
st.markdown(f"<span class='eco-pill'>{tr('model_notice')}</span>",unsafe_allow_html=True)
st.caption(tr("official_notice"))
for warning in st.session_state.api_warnings:
    st.warning(f"Источник временно недоступен: {warning}")
if not air: st.info("Данные качества воздуха временно недоступны.")
if not weather: st.info("Погодные данные временно недоступны.")

tabs=st.tabs([tr("map"),tr("air"),tr("wind"),tr("company"),tr("risk"),tr("analysis")])

with tabs[0]:
    st.subheader(tr("map"))
    st.caption(tr("map_note"))
    points=[{"lat":a,"lon":b,"name":name,"kind":"Региональный центр"} for name,a,b in REGIONS]
    points.append({"lat":lat,"lon":lon,"name":city,"kind":"Выбранный город"})
    points += [{"lat":o["lat"],"lon":o["lon"],"name":o["name"],"kind":"Промышленный объект"} for o in shown]
    mapdf=pd.DataFrame(points).drop_duplicates(subset=["lat","lon","name"])
    st.map(mapdf,latitude="lat",longitude="lon")
    st.caption("Карта использует OpenStreetMap. Точки промышленных объектов неполные и добавлены сообществом.")
    if query and not matches: st.warning(tr("not_found"))
    st.write(f"**{tr('osm_found')}:** {len(objects)}")
    if shown:
        st.dataframe(pd.DataFrame([{"Объект":o["name"],"Тип":o["type"],"Широта":o["lat"],"Долгота":o["lon"]} for o in shown]),
                     use_container_width=True,hide_index=True)
    else: st.info(tr("no_factory"))

with tabs[1]:
    st.subheader(tr("air"))
    st.info(tr("model_notice"))
    pollutant_list=[("PM2.5","pm2_5","µg/m³"),("PM10","pm10","µg/m³"),
                    ("CO","carbon_monoxide","µg/m³"),("NO₂","nitrogen_dioxide","µg/m³"),
                    ("SO₂","sulphur_dioxide","µg/m³"),("O₃","ozone","µg/m³")]
    cols=st.columns(3)
    for i,(label,key,unit) in enumerate(pollutant_list):
        v=num(current_air.get(key))
        cols[i%3].metric(label,f"{v:.2f} {unit}" if v is not None else "—")
    aqi=num(current_air.get("us_aqi"))
    aqi_label="US AQI"
    if aqi is None: aqi=num(current_air.get("european_aqi")); aqi_label="European AQI"
    st.metric(f"{tr('aqi')} ({aqi_label})",f"{aqi:.0f}" if aqi is not None else "—")
    hourly=air.get("hourly",{})
    times=hourly.get("time",[])
    if times:
        chart=pd.DataFrame({"time":times})
        for label,key,_ in pollutant_list:
            vals=hourly.get(key,[])
            if vals and len(vals)==len(times): chart[label]=vals
        chart=chart.head(24)
        choices=[c for c in chart.columns if c!="time"]
        if choices:
            selected=st.multiselect("Показатели для графика / Chart indicators",choices,default=choices[:2])
            if selected:
                melted=chart.melt(id_vars="time",value_vars=selected,var_name="Показатель",value_name="µg/m³")
                fig=px.line(melted,x="time",y="µg/m³",color="Показатель",markers=True)
                fig.update_layout(paper_bgcolor=BG,plot_bgcolor="#fffef8")
                st.plotly_chart(fig,use_container_width=True)
        else: st.info("Нет достаточного набора часовых данных для графика.")
    else: st.info("Часовые данные недоступны.")
    st.caption("CO — угарный газ (carbon monoxide), это не CO₂.")
    st.markdown("[Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api)")

with tabs[2]:
    st.subheader(tr("wind"))
    speed=num(current_weather.get("wind_speed_10m"))
    direction=num(current_weather.get("wind_direction_10m"))
    temp=num(current_weather.get("temperature_2m"))
    humidity=num(current_weather.get("relative_humidity_2m"))
    a,b,c,d=st.columns(4)
    a.metric(tr("wind_speed"),f"{speed:.1f} km/h" if speed is not None else "—")
    b.metric(tr("wind_dir"),f"{direction:.0f}° {compass(direction)}" if direction is not None else "—")
    c.metric(tr("temperature"),f"{temp:.1f} °C" if temp is not None else "—")
    d.metric(tr("humidity"),f"{humidity:.0f}%" if humidity is not None else "—")
    if direction is not None:
        st.markdown(f"<div class='eco-card' style='text-align:center'><div style='font-size:58px;color:{GREEN};transform:rotate({direction}deg)'>↑</div><b>{compass(direction)} · {direction:.0f}°</b></div>",unsafe_allow_html=True)
    st.caption("Погодная модель не доказывает перенос загрязнения от конкретного завода.")
    st.markdown("[Open-Meteo Weather API](https://open-meteo.com/en/docs)")

with tabs[3]:
    st.subheader(tr("company"))
    if matches:
        selected=matches[0]
        st.markdown(f"### {selected['name']}")
        st.write(f"**{tr('factory_type')}:** {selected['type']}")
        st.write(f"**{tr('coordinates')}:** {selected['lat']:.5f}, {selected['lon']:.5f}")
        st.write(f"**Оператор:** {selected['operator']}")
        if selected["website"]: st.markdown(f"[Сайт предприятия]({selected['website']})")
        st.markdown(f"[Открыть объект в OpenStreetMap](https://www.openstreetmap.org/{selected['osm_type']}/{selected['osm_id']})")
        st.caption("Источник: OpenStreetMap. Это не официальный реестр предприятий.")
    else:
        st.warning(tr("not_found"))
        st.write("Предприятие может отсутствовать в OpenStreetMap или быть записано под другим названием.")
    st.markdown("#### Environmental measurements")
    st.info(tr("data_missing"))
    st.markdown("[Казгидромет — официальный сайт](https://www.kazhydromet.kz/)")

with tabs[4]:
    st.subheader(tr("risk"))
    st.info("Предварительный индикатор основан только на модельном индексе воздуха в координатах города. Это не официальная оценка риска и не оценка конкретного предприятия.")
    st.markdown(f"### {risk_text}")
    if risk_value is not None: st.metric(risk_source,risk_value)
    if risk_band=="low": st.success("Модельный индекс находится в нижнем диапазоне.")
    elif risk_band=="mid": st.warning("Модельный индекс находится в среднем диапазоне.")
    elif risk_band=="high": st.error("Модельный индекс находится в повышенном диапазоне.")
    else: st.info(tr("risk_unknown"))
    st.write("Для полноценной оценки нужны подтверждённые измерения, нормативы, временной период и проверенная методика.")

with tabs[5]:
    st.subheader(tr("analysis"))
    st.write("Показаны доступные текущие и почасовые модельные данные. Исторический тренд не создаётся без исторического источника.")
    st.json({"city":city,"coordinates":{"latitude":lat,"longitude":lon},
             "air_quality_model":current_air,"weather_model":current_weather,
             "retrieved_at_local":datetime.now().astimezone().isoformat(timespec="minutes")})

st.markdown("---")
st.markdown(f"<div class='eco-card'>{tr('disclaimer')}</div>",unsafe_allow_html=True)
st.markdown(
    "**Источники:** Open-Meteo / Copernicus Atmosphere Monitoring Service (CAMS), OpenStreetMap contributors. "
    "[Open-Meteo Air Quality](https://open-meteo.com/en/docs/air-quality-api) · "
    "[Open-Meteo Weather](https://open-meteo.com/en/docs) · "
    "[OpenStreetMap](https://www.openstreetmap.org/copyright) · "
    "[Казгидромет](https://www.kazhydromet.kz/)"
)
