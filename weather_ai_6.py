import streamlit as st
import requests
import pandas as pd
from openai import OpenAI

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="Guardian AI Weather PRO", layout="wide", page_icon="🌍")

# 🔹 OpenAI клиенті
API_KEY = "АПИ КЕЙ осы жерге қойылсын"
client = OpenAI(api_key=API_KEY)

API_TIMEOUT = 15
LANGUAGES = {"Қазақша": "kk", "Русский": "ru", "English": "en"}

# =====================================================
# TRANSLATIONS
# =====================================================
TRANSLATIONS = {
    "Қазақша": {
        "language_label": "🌐 Тіл", "enter_city": "📍 Қаланы енгізіңіз", "search": "Іздеу",
        "select_city": "Нақты мекенжайды таңдаңыз:", "temp": "🌡 Температура", 
        "humidity": "💧 Ылғалдылық", "wind": "🌬 Жел", "uv": "☀️ UV",
        "pressure": "🌊 Қысым", "clouds": "☁️ Бұлттылық", "rain": "🌧 Жаңбыр", "aqi": "🌪 AQI",
        "temp_24h": "📈 24 сағат температурасы", "forecast_7d": "📅 7 күндік болжам",
        "gpt_analysis": "🤖 GPT Ауа райы талдауы", "map_layer": "Карта қабаты",
        "windy_map": "🌍 Windy Жаңбыр/Жел картасы", "location_not_found": "Орналасқан жер табылмады"
    },
    "Русский": {
        "language_label": "🌐 Язык", "enter_city": "📍 Введите город", "search": "Поиск",
        "select_city": "Выберите точное местоположение:", "temp": "🌡 Температура", 
        "humidity": "💧 Влажность", "wind": "🌬 Ветер", "uv": "☀️ UV",
        "pressure": "🌊 Давление", "clouds": "☁️ Облачность", "rain": "🌧 Дождь", "aqi": "🌪 AQI",
        "temp_24h": "📈 Температура за 24 часа", "forecast_7d": "📅 Прогноз на 7 дней",
        "gpt_analysis": "🤖 GPT Анализ погоды", "map_layer": "Слой карты",
        "windy_map": "🌍 Windy карта дождя/ветра", "location_not_found": "Местоположение не найдено"
    },
    "English": {
        "language_label": "🌐 Language", "enter_city": "📍 Enter city", "search": "Search",
        "select_city": "Select precise location:", "temp": "🌡 Temp", 
        "humidity": "💧 Humidity", "wind": "🌬 Wind", "uv": "☀️ UV",
        "pressure": "🌊 Pressure", "clouds": "☁️ Clouds", "rain": "🌧 Rain", "aqi": "🌪 AQI",
        "temp_24h": "📈 24h Temperature", "forecast_7d": "📅 7 Day Forecast",
        "gpt_analysis": "🤖 GPT Weather Analysis", "map_layer": "Map Layer",
        "windy_map": "🌍 Windy Rain/Wind Map", "location_not_found": "Location not found"
    }
}

# =====================================================
# FUNCTIONS
# =====================================================
@st.cache_data(ttl=3600)
def search_location(query, lang):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=10&language={lang}&format=json"
    try:
        res = requests.get(url, timeout=API_TIMEOUT)
        res.raise_for_status()
        return res.json().get("results", [])
    except:
        return []

@st.cache_data(ttl=900)
def fetch_weather(lat, lon):
    url = (f"https://api.open-meteo.com/v1/forecast?"
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
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi"
    try:
        res = requests.get(url, timeout=API_TIMEOUT)
        res.raise_for_status()
        return res.json()
    except:
        return None

def gpt_analysis(current, daily, language):
    prompt = f"""
    Analyze the weather professionally. 
    Current: Temp: {current['temperature_2m']}°C, Wind: {current['wind_speed_10m']} m/s, Humidity: {current['relative_humidity_2m']}%
    7-day: Max: {daily['temperature_2m_max']}, Min: {daily['temperature_2m_min']}, Rain: {daily['precipitation_sum']}
    Provide insights on what to wear and any precautions. Respond in {language}.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Analysis Error: {str(e)}"

# =====================================================
# UI & SESSION STATE
# =====================================================
if "selected_location" not in st.session_state: st.session_state.selected_location = None
if "weather_data" not in st.session_state: st.session_state.weather_data = None

selected_lang = st.sidebar.selectbox("🌐 Language", list(LANGUAGES.keys()))
t = TRANSLATIONS[selected_lang]

city_query = st.sidebar.text_input(t["enter_city"])

if city_query:
    locations = search_location(city_query, LANGUAGES[selected_lang])
    
    if locations:
        # Бірдей атты қалаларды ажырату үшін тізім жасау
        loc_options = {f"{l['name']} ({l.get('admin1', '')}, {l.get('country', '')})": l for l in locations}
        selected_name = st.sidebar.selectbox(t["select_city"], list(loc_options.keys()))
        
        if selected_name:
            loc = loc_options[selected_name]
            # Тек қала ауысқанда ғана деректерді жаңарту
            if st.session_state.selected_location != loc:
                st.session_state.selected_location = loc
                with st.spinner("Fetching data..."):
                    st.session_state.weather_data = fetch_weather(loc["latitude"], loc["longitude"])
                    st.session_state.air_data = fetch_air_quality(loc["latitude"], loc["longitude"])
                    st.session_state.gpt_analysis_result = None
    else:
        st.sidebar.error(t["location_not_found"])

# =====================================================
# DASHBOARD
# =====================================================
if st.session_state.selected_location and st.session_state.weather_data:
    loc = st.session_state.selected_location
    weather = st.session_state.weather_data
    current = weather["current"]
    
    st.title(f"🌍 {loc['name']}, {loc.get('country', '')}")
    
    # Негізгі көрсеткіштер
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(t["temp"], f"{current['temperature_2m']}°C")
    m2.metric(t["humidity"], f"{current['relative_humidity_2m']}%")
    m3.metric(t["wind"], f"{current['wind_speed_10m']} m/s")
    m4.metric(t["uv"], current.get("uv_index", 0))

    # Қосымша көрсеткіштер
    with st.expander("More Details"):
        c1, c2, c3 = st.columns(3)
        c1.metric(t["pressure"], f"{current['pressure_msl']} hPa")
        c2.metric(t["clouds"], f"{current['cloud_cover']}%")
        c3.metric(t["rain"], f"{current['precipitation']} mm")

    # График және Кесте
    tab1, tab2 = st.tabs([t["temp_24h"], t["forecast_7d"]])
    
    with tab1:
        df = pd.DataFrame({"Time": weather["hourly"]["time"][:24], "Temp": weather["hourly"]["temperature_2m"][:24]})
        st.line_chart(df.set_index("Time"))

    with tab2:
        daily_df = pd.DataFrame({
            "Date": weather["daily"]["time"],
            "Max (°C)": weather["daily"]["temperature_2m_max"],
            "Min (°C)": weather["daily"]["temperature_2m_min"],
            "Rain (mm)": weather["daily"]["precipitation_sum"]
        })
        st.table(daily_df)

    # GPT Талдау
    if st.button(t["gpt_analysis"]):
        with st.spinner("AI is thinking..."):
            analysis = gpt_analysis(current, weather["daily"], selected_lang)
            st.info(analysis)

    # Windy Картасы
    st.subheader(t["windy_map"])
    map_type = st.selectbox(t["map_layer"], ["rain", "wind", "clouds"])
    st.components.v1.iframe(f"https://www.windy.com/embed2.html?lat={loc['latitude']}&lon={loc['longitude']}&zoom=5&overlay={map_type}", height=450)
