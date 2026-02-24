# AEROO-AI-WEATHER-ANALYSIS
Команда Төлеби Дарын

№1________Құжаттама

№2________Жұмыс коды жіне инструкциясы:
1.Win+R батырмасын басып іздеу жолына cmd деп жазамыз
2.команда жолына мына екі команданы жазамыз(егер сіздерде pip пайтон функциясы болмаса оныда орнатыныз):
[1] pip install streamlit pandas requests openai
[2] pip install plotly
[3]Жәнеде бұл кодқа АПИ КЕЙ керек оны былай орнатады:setx OPENAI_API_KEY "Апи кейді сайттан алыныз"(егер код жұмыс жасамаса мына сайттан АПИ-КЕЙ көшіріп алыныз:https://platform.openai.com/api-keys)
Егер сізде пайтоннын pip функциясы болмаса мына сілтеме арқылы өтіп орнатыныз:https://www.youtube.com/watch?v=hqLN2vKpq7Q
3.барлығын жасап болғансон кодты көшіріп алыныз
4.қайттан команда жолын ашыныз және іздеу жолына мына команданы терініз: streamlit run app.py
мыне код:
[app.py](https://github.com/user-attachments/files/25480264/app.py)
import streamlit as st
import requests
import pandas as pd
from openai import OpenAI

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="Guardian AI Weather PRO", layout="wide", page_icon="🌍")

# 🔹 OpenAI клиенті (тікелей кілт немесе environment variable)
API_KEY = "сайттан алынған апи кей осы жерге"
client = OpenAI(api_key=API_KEY)

API_TIMEOUT = 15
LANGUAGES = {"Қазақша":"kk","Русский":"ru","English":"en"}

# =====================================================
# TRANSLATIONS
# =====================================================
TRANSLATIONS = {
    "Қазақша": {
        "language_label":"🌐 Тіл", "enter_city":"📍 Қаланы енгізіңіз", "search":"Іздеу",
        "temp":"🌡 Температура", "humidity":"💧 Ылғалдылық", "wind":"🌬 Жел", "uv":"☀️ UV",
        "pressure":"🌊 Қысым", "clouds":"☁️ Бұлттылық", "rain":"🌧 Жаңбыр", "aqi":"🌪 AQI",
        "temp_24h":"📈 24 сағат температурасы", "forecast_7d":"📅 7 күндік болжам",
        "gpt_analysis":"🤖 GPT Ауа райы талдауы", "map_layer":"Карта қабаты",
        "windy_map":"🌍 Windy Жаңбыр/Жел картасы", "location_not_found":"Орналасқан жер табылмады"
    },
    "Русский": {
        "language_label":"🌐 Язык", "enter_city":"📍 Введите город", "search":"Поиск",
        "temp":"🌡 Температура", "humidity":"💧 Влажность", "wind":"🌬 Ветер", "uv":"☀️ UV",
        "pressure":"🌊 Давление", "clouds":"☁️ Облачность", "rain":"🌧 Дождь", "aqi":"🌪 AQI",
        "temp_24h":"📈 Температура за 24 часа", "forecast_7d":"📅 Прогноз на 7 дней",
        "gpt_analysis":"🤖 GPT Анализ погоды", "map_layer":"Слой карты",
        "windy_map":"🌍 Windy карта дождя/ветра", "location_not_found":"Местоположение не найдено"
    },
    "English": {
        "language_label":"🌐 Language", "enter_city":"📍 Enter city", "search":"Search",
        "temp":"🌡 Temp", "humidity":"💧 Humidity", "wind":"🌬 Wind", "uv":"☀️ UV",
        "pressure":"🌊 Pressure", "clouds":"☁️ Clouds", "rain":"🌧 Rain", "aqi":"🌪 AQI",
        "temp_24h":"📈 24h Temperature", "forecast_7d":"📅 7 Day Forecast",
        "gpt_analysis":"🤖 GPT Weather Analysis", "map_layer":"Map Layer",
        "windy_map":"🌍 Windy Rain/Wind Map", "location_not_found":"Location not found"
    }
}

# =====================================================
# FUNCTIONS
# =====================================================
@st.cache_data(ttl=3600)
def search_location(query, lang):
    url=f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=5&language={lang}&format=json"
    try:
        res = requests.get(url, timeout=API_TIMEOUT)
        res.raise_for_status()
        return res.json().get("results",[])
    except:
        return []

@st.cache_data(ttl=900)
def fetch_weather(lat, lon):
    url=(f"https://api.open-meteo.com/v1/forecast?"
         f"latitude={lat}&longitude={lon}"
         f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
         f"wind_speed_10m,wind_direction_10m,uv_index,pressure_msl,"
         f"cloud_cover,precipitation"
         f"&hourly=temperature_2m"
         f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
         f"&timezone=auto")
    try:
        res = requests.get(url, timeout=API_TIMEOUT)
        res.raise_for_status()
        return res.json()
    except:
        return None

@st.cache_data(ttl=900)
def fetch_air_quality(lat, lon):
    url=f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi"
    try:
        res = requests.get(url, timeout=API_TIMEOUT)
        res.raise_for_status()
        return res.json()
    except:
        return None

def gpt_analysis(current, daily, language):
    prompt=f"""
    Analyze the weather professionally.
    Current:
    Temp: {current['temperature_2m']}°C
    Wind: {current['wind_speed_10m']} m/s
    Humidity: {current['relative_humidity_2m']}%
    UV: {current.get('uv_index',0)}
    7-day forecast:
    Max temps: {daily['temperature_2m_max']}
    Min temps: {daily['temperature_2m_min']}
    Rain: {daily['precipitation_sum']}
    Respond in {language}.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

# =====================================================
# SESSION STATE
# =====================================================
for key in ["selected_location","weather_data","air_data","gpt_analysis_result"]:
    if key not in st.session_state:
        st.session_state[key]=None

# =====================================================
# UI
# =====================================================
selected_lang = st.sidebar.selectbox("🌐 Language", list(LANGUAGES.keys()))
t = TRANSLATIONS[selected_lang]

city = st.sidebar.text_input(t["enter_city"])
search_btn = st.sidebar.button(t["search"])

if search_btn and city:
    locations = search_location(city, LANGUAGES[selected_lang])
    if not locations:
        st.error(t["location_not_found"])
        for key in ["selected_location","weather_data","air_data","gpt_analysis_result"]:
            st.session_state[key] = None
    else:
        loc = locations[0]
        st.session_state.selected_location = loc
        lat, lon = loc["latitude"], loc["longitude"]
        st.session_state.weather_data = fetch_weather(lat, lon)
        st.session_state.air_data = fetch_air_quality(lat, lon)
        st.session_state.gpt_analysis_result = None

if st.session_state.selected_location and st.session_state.weather_data:
    loc = st.session_state.selected_location
    weather = st.session_state.weather_data
    air = st.session_state.air_data
    lat, lon = loc["latitude"], loc["longitude"]
    current = weather["current"]

    st.header(f"{loc['name']}, {loc['country']}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t["temp"], f"{current['temperature_2m']}°C")
    col2.metric(t["humidity"], f"{current['relative_humidity_2m']}%")
    col3.metric(t["wind"], f"{current['wind_speed_10m']} m/s")
    col4.metric(t["uv"], current.get("uv_index",0))

    st.divider()
    col5, col6, col7 = st.columns(3)
    col5.metric(t["pressure"], f"{current['pressure_msl']} hPa")
    col6.metric(t["clouds"], f"{current['cloud_cover']}%")
    col7.metric(t["rain"], f"{current['precipitation']} mm")

    if air:
        aqi = air["current"]["us_aqi"]
        st.metric(t["aqi"], aqi)

    st.subheader(t["temp_24h"])
    df = pd.DataFrame({"Time": weather["hourly"]["time"][:24],
                       "Temp": weather["hourly"]["temperature_2m"][:24]})
    df["Time"] = pd.to_datetime(df["Time"])
    df.set_index("Time", inplace=True)
    st.line_chart(df)

    st.subheader(t["forecast_7d"])
    daily_df = pd.DataFrame({
        "Date": weather["daily"]["time"],
        "Max": weather["daily"]["temperature_2m_max"],
        "Min": weather["daily"]["temperature_2m_min"],
        "Rain": weather["daily"]["precipitation_sum"]
    })
    st.dataframe(daily_df)

    if st.button(t["gpt_analysis"]):
        with st.spinner("AI analyzing..."):
            st.session_state.gpt_analysis_result = gpt_analysis(current, weather["daily"], selected_lang)

    if st.session_state.gpt_analysis_result:
        st.info(st.session_state.gpt_analysis_result)

    st.subheader(t["windy_map"])
    map_type = st.selectbox(t["map_layer"], ["rain","wind","clouds"], key="map_layer")
    st.components.v1.iframe(f"https://www.windy.com/embed2.html?lat={lat}&lon={lon}&zoom=7&overlay={map_type}", height=500)

№3________MVP:

№4________Pitch-deck





[requirements.txt](https://github.com/user-attachments/files/25515041/requirements.txt)
streamlit
requests
pandas
openai
