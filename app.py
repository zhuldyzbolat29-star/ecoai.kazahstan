import streamlit as st
import pandas as pd
import plotly.express as px
import requests

from search_service import search_enterprise, SearchError

st.set_page_config(
    page_title="ECOAI KAZAKHSTAN",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==================== DESIGN ====================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background: linear-gradient(135deg, #070B18, #101A35, #17132F);
    color: #FFFFFF;
    font-family: 'Inter', sans-serif;
}
.block-container {
    max-width: 1400px;
    padding-top: 2rem;
}
h1, h2, h3, p, label {
    color: #F7F9FF !important;
}
.brand {
    font-size: 34px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #FFFFFF;
}
.subtitle {
    color: #80A5FF;
    letter-spacing: 3px;
    font-size: 12px;
}
.panel {
    background: linear-gradient(135deg, #142448, #211B45);
    border: 1px solid #354A80;
    border-radius: 16px;
    padding: 22px;
    margin: 12px 0;
}
div[data-testid="stMetric"] {
    background: #111D39;
    border: 1px solid #354A80;
    padding: 18px;
    border-radius: 14px;
}
.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(100deg, #4338A8, #245AC7);
    color: white;
    border: 1px solid #648DFF;
    border-radius: 9px;
    min-height: 45px;
    font-weight: 700;
}
.stTextInput input {
    background: #0B1429;
    color: white;
    border: 1px solid #354A80;
    border-radius: 8px;
}
div[data-testid="stTabs"] button {
    color: #B7C9F7;
    font-weight: 700;
}
hr {
    border-color: #354A80;
}
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================

st.markdown(
    '<div class="brand">ECOAI KAZAKHSTAN</div>'
    '<div class="subtitle">ENVIRONMENTAL INTELLIGENCE PLATFORM</div>',
    unsafe_allow_html=True,
)

st.write("")
st.markdown(
    "МОНИТОРИНГ ЭКОЛОГИЧЕСКОГО СОСТОЯНИЯ ПРЕДПРИЯТИЙ КАЗАХСТАНА"
)

# ==================== TWO TABS ====================

search_tab, dashboard_tab = st.tabs([
    "01 / ПОИСК ЗАВОДА",
    "02 / ПАНЕЛЬ МОНИТОРИНГА",
])

with search_tab:
    st.markdown("## ПОИСК ПРЕДПРИЯТИЯ")
    st.write("Введите название завода и город для начала анализа.")

    with st.form("plant_form"):
        plant = st.text_input(
            "НАЗВАНИЕ ЗАВОДА",
            placeholder="Например, металлургический завод",
        )
        city = st.text_input(
            "ГОРОД",
            placeholder="Например, Темиртау",
        )
        submitted = st.form_submit_button(
            "НАЧАТЬ АНАЛИЗ",
            use_container_width=True,
        )

    if submitted:
        if not plant.strip() or not city.strip():
            st.error("Введите название завода и город.")
        else:
            st.session_state["plant"] = plant.strip()
            st.session_state["city"] = city.strip()
            st.session_state["analysis_ready"] = True
            st.success(
                "Данные сохранены. Откройте вкладку "
                "«02 / ПАНЕЛЬ МОНИТОРИНГА»."
            )

    st.markdown("""
    <div class="panel">
        <b>СИСТЕМА АНАЛИЗА</b><br><br>
        01. Загрязнение воздуха<br>
        02. Экологические риски<br>
        03. Превышение ориентиров за месяц<br>
        04. Динамика загрязнения
    </div>
    """, unsafe_allow_html=True)


# ==================== AIR QUALITY API ====================

@st.cache_data(ttl=1800)
def get_coordinates(city_name):
    response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={
            "name": city_name,
            "count": 10,
            "language": "en",
            "format": "json",
        },
        timeout=20,
    )
    response.raise_for_status()
    places = response.json().get("results", [])

    kazakhstan_places = [
        place for place in places
        if place.get("country_code") == "KZ"
    ]

    return kazakhstan_places or places


@st.cache_data(ttl=1800)
def get_air_quality(latitude, longitude):
    response = requests.get(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "hourly": (
                "pm2_5,pm10,nitrogen_dioxide,"
                "sulphur_dioxide,ozone"
            ),
            "past_days": 30,
            "timezone": "auto",
        },
        timeout=30,
    )
    response.raise_for_status()

    hourly = response.json().get("hourly", {})
    if not hourly.get("time"):
        return pd.DataFrame()

    data = pd.DataFrame(hourly)
    data["time"] = pd.to_datetime(data["time"])

    return data.set_index("time").sort_index()


# ==================== DASHBOARD ====================

with dashboard_tab:
    st.markdown("## ПАНЕЛЬ МОНИТОРИНГА")

    if not st.session_state.get("analysis_ready", False):
        st.info(
            "Сначала откройте первую вкладку, "
            "введите завод и город, затем начните анализ."
        )
    else:
        plant = st.session_state["plant"]
        city = st.session_state["city"]

        st.markdown(f"### {plant.upper()}")
        st.caption(f"ГОРОД: {city.upper()}")

        # 01: AIR POLLUTION
        st.markdown("---")
        st.markdown("### 01 / ЗАГРЯЗНЕНИЕ ВОЗДУХА")

        try:
            places = get_coordinates(city)

            if not places:
                st.warning(
                    "Город не найден. Попробуйте другое написание."
                )
            else:
                place = places[0]

                air = get_air_quality(
                    place["latitude"],
                    place["longitude"],
                )

                if air.empty:
                    st.warning("Данные о качестве воздуха отсутствуют.")
                else:
                    latest = air.dropna(how="all").iloc[-1]

                    columns = st.columns(4)

                    pollutants = [
                        ("PM2.5", "pm2_5"),
                        ("PM10", "pm10"),
                        ("NO2", "nitrogen_dioxide"),
                        ("SO2", "sulphur_dioxide"),
                    ]

                    for column, (label, key) in zip(
                        columns, pollutants
                    ):
                        value = latest.get(key)

                        if pd.notna(value):
                            column.metric(
                                label,
                                f"{value:.1f} µg/m³",
                            )
                        else:
                            column.metric(label, "НЕТ ДАННЫХ")

                    daily = air.resample("D").mean(numeric_only=True)

                    # 02: ECOLOGICAL RISKS
                    st.markdown("---")
                    st.markdown("### 02 / ЭКОЛОГИЧЕСКИЕ РИСКИ")

                    guidelines = {
                        "PM2.5": ("pm2_5", 15),
                        "PM10": ("pm10", 45),
                    }

                    for label, (key, limit) in guidelines.items():
                        values = daily[key].dropna()

                        if values.empty:
                            st.info(f"{label}: недостаточно данных.")
                            continue

                        average = values.mean()

                        if average > limit:
                            st.warning(
                                f"{label}: среднее значение "
                                f"{average:.1f} µg/m³ выше ориентира "
                                f"ВОЗ {limit} µg/m³."
                            )
                        else:
                            st.info(
                                f"{label}: среднее значение "
                                f"{average:.1f} µg/m³ ниже ориентира "
                                f"ВОЗ {limit} µg/m³."
                            )

                    st.caption(
                        "Ориентиры ВОЗ не являются юридическими "
                        "нормативами выбросов предприятий Казахстана."
                    )

                    # 03: MONTHLY EXCEEDANCES
                    st.markdown("---")
                    st.markdown(
                        "### 03 / ПРЕВЫШЕНИЕ ОРИЕНТИРОВ ЗА МЕСЯЦ"
                    )

                    for label, (key, limit) in guidelines.items():
                        values = daily[key].dropna()
                        if values.empty:
                            continue

                        exceeded = int((values > limit).sum())

                        left, middle, right = st.columns(3)
                        left.metric(
                            f"{label}: ДНЕЙ ВЫШЕ ОРИЕНТИРА",
                            exceeded,
                        )
                        middle.metric(
                            "ДНЕЙ С ДАННЫМИ",
                            len(values),
                        )
                        right.metric(
                            "ОРИЕНТИР, µg/m³",
                            limit,
                        )

                    # 04: POLLUTION DYNAMICS
                    st.markdown("---")
                    st.markdown("### 04 / ДИНАМИКА ЗАГРЯЗНЕНИЯ")

                    chart_columns = {
                        "PM2.5": "pm2_5",
                        "PM10": "pm10",
                        "NO2": "nitrogen_dioxide",
                        "SO2": "sulphur_dioxide",
                        "O3": "ozone",
                    }

                    selected = st.multiselect(
                        "ВЫБЕРИТЕ ПОКАЗАТЕЛИ",
                        list(chart_columns.keys()),
                        default=["PM2.5", "PM10"],
                    )

                    if selected:
                        chart_data = daily[
                            [chart_columns[name] for name in selected]
                        ].copy()

                        chart_data.columns = selected
                        chart_data.index.name = "ДАТА"
                        chart_data = chart_data.reset_index()

                        chart_data = chart_data.melt(
                            id_vars="ДАТА",
                            var_name="ПОКАЗАТЕЛЬ",
                            value_name="КОНЦЕНТРАЦИЯ, µg/m³",
                        )

                        figure = px.line(
                            chart_data,
                            x="ДАТА",
                            y="КОНЦЕНТРАЦИЯ, µg/m³",
                            color="ПОКАЗАТЕЛЬ",
                            markers=True,
                            color_discrete_sequence=[
                                "#3478F6",
                                "#8B7CFF",
                                "#6CC8FF",
                                "#FFFFFF",
                                "#A9B9DF",
                            ],
                        )

                        figure.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="#101A35",
                            plot_bgcolor="#101A35",
                            font_color="#F7F9FF",
                        )

                        st.plotly_chart(
                            figure,
                            use_container_width=True,
                        )

                    # PUBLIC WEB SEARCH
                    st.markdown("---")
                    st.markdown("### ОТКРЫТЫЕ ПУБЛИКАЦИИ")

                    try:
                        articles = search_enterprise(
                            plant=plant,
                            city=city,
                            limit=12,
                        )

                        if not articles:
                            st.info(
                                "Подходящие публикации не найдены. "
                                "Это не означает отсутствия рисков."
                            )

                        for article in articles:
                            with st.container(border=True):
                                st.markdown(
                                    f"**{article.get('title', 'Без названия')}**"
                                )

                                if article.get("snippet"):
                                    st.write(article["snippet"])

                                if article.get("url"):
                                    st.markdown(
                                        f"[ОТКРЫТЬ ИСТОЧНИК]"
                                        f"({article['url']})"
                                    )

                    except SearchError:
                        st.warning(
                            "Поиск публикаций временно недоступен."
                        )

        except requests.RequestException:
            st.error(
                "Не удалось получить данные из внешнего сервиса. "
                "Проверьте подключение и попробуйте снова."
            )

        st.caption(
            "Данные воздуха относятся к географической точке города "
            "и не доказывают, что загрязнение вызвано конкретным заводом."
        )

st.markdown("---")
st.caption(
    "ECOAI KAZAKHSTAN | ЭКОЛОГИЧЕСКИЙ МОНИТОРИНГ"
)