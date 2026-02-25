import streamlit as st  # Веб-интерфейс жасауға арналған негізгі кітапхана
import requests         # API-ге (ауа райы серверіне) сұраныс жіберу үшін
import pandas as pd     # Деректерді кесте түрінде өңдеу және графиктер үшін
from openai import OpenAI # Жасанды интеллектпен (ChatGPT) байланыс орнату үшін

# =====================================================
# 1. КОНФИГУРАЦИЯ (БАПТАУЛАР)
# =====================================================
# Сайттың тақырыбын, белгішесін және беттің орналасуын реттейміз
st.set_page_config(page_title="Guardian AI Weather PRO", layout="wide", page_icon="🌍")

# OpenAI API кілтін Streamlit Secrets (бұлттық сақтау) арқылы қауіпсіз түрде аламыз
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=API_KEY) # AI клиентін іске қосу
except:
    client = None # Егер кілт табылмаса, AI бөлімі жұмыс істемейді

API_TIMEOUT = 15 # Серверден жауап күтудің максималды уақыты (секунд)
# Қолдау көрсетілетін тілдер тізімі
LANGUAGES = {"Қазақша":"kk", "Русский":"ru", "English":"en"}

# =====================================================
# 2. АУДАРМАЛАР (Көптілділік механизмі)
# =====================================================
# Әр тілге сәйкес интерфейс мәтіндерін сөздік ретінде сақтаймыз
TRANSLATIONS = {
    "Қазақша": {
        "enter_city":"📍 Қала атын жазыңыз", "select_city":"🏘 Нақты жерді таңдаңыз",
        "search":"Іздеу", "temp":"🌡 Температура", "humidity":"💧 Ылғалдылық", 
        "wind":"🌬 Жел", "uv":"☀️ UV", "aqi":"🌪 Ауа сапасы (AQI)",
        "temp_24h":"📈 24 сағаттық болжам", "forecast_7d":"📅 7 күндік болжам",
        "gpt_analysis":"🤖 AI Ауа райы талдауы", "map_layer":"Карта түрі",
        "windy_map":"🌍 Windy Интерактивті картасы", "no_ai":"API кілті табылмады"
    },
    "Русский": {
        "enter_city":"📍 Введите название города", "select_city":"🏘 Выберите локацию",
        "search":"Поиск", "temp":"🌡 Температура", "humidity":"💧 Влажность",
        "wind":"🌬 Ветер", "uv":"☀️ UV", "aqi":"🌪 Качество воздуха (AQI)",
        "temp_24h":"📈 Прогноз на 24 часа", "forecast_7d":"📅 Прогноз на 7 дней",
        "gpt_analysis":"🤖 AI Анализ погоды", "map_layer":"Слой карты",
        "windy_map":"🌍 Интерактивная карта Windy", "no_ai":"API ключ не найден"
    },
    "English": {
        "enter_city":"📍 Enter city name", "select_city":"🏘 Select exact location",
        "search":"Search", "temp":"🌡 Temperature", "humidity":"💧 Humidity",
        "wind":"🌬 Wind", "uv":"☀️ UV", "aqi":"🌪 Air Quality (AQI)",
        "temp_24h":"📈 24h Forecast", "forecast_7d":"📅 7 Day Forecast",
        "gpt_analysis":"🤖 AI Weather Analysis", "map_layer":"Map Layer",
        "windy_map":"🌍 Windy Interactive Map", "no_ai":"API Key not found"
    }
}

# =====================================================
# 3. API ФУНКЦИЯЛАРЫ (Деректерді алу)
# =====================================================
# Қала аты бойынша оның координаталарын (ендік пен бойлық) іздеу функциясы
@st.cache_data(ttl=3600) # Нәтижені 1 сағатқа жадта сақтайды (сайт тез жұмыс істеуі үшін)
def search_location(query, lang):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=10&language={lang}&format=json"
    try:
        res = requests.get(url, timeout=API_TIMEOUT)
        return res.json().get("results", []) # Табылған қалалар тізімін қайтарады
    except: return []

# Координаталар бойынша ауа райы мен ауа сапасын алу функциясы
@st.cache_data(ttl=900) # Деректерді 15 минут сайын жаңартып тұрады
def fetch_data(lat, lon):
    # Ауа райы деректеріне сұраныс (температура, жел, ылғалдылық, 7 күндік болжам)
    weather_url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                   f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,uv_index,pressure_msl,cloud_cover,precipitation"
                   f"&hourly=temperature_2m&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto")
    # Ауа сапасына (AQI) арналған бөлек сұраныс
    air_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi"
    
    try:
        w_res = requests.get(weather_url).json()
        a_res = requests.get(air_url).json()
        return w_res, a_res # Екі дерек көзін де қайтарады
    except: return None, None

# =====================================================
# 4. СЕССИЯ ЖӘНЕ ИНТЕРФЕЙС
# =====================================================
# Sidebar (сол жақ панель) арқылы тілді таңдау
selected_lang = st.sidebar.selectbox("🌐 Language", list(LANGUAGES.keys()))
t = TRANSLATIONS[selected_lang] # Таңдалған тілге сәйкес мәтіндерді жүктеу

# Қала атын енгізу жолағы
city_input = st.sidebar.text_input(t["enter_city"])

# Қалаларды тізіммен таңдау логикасы (Бірдей атты қалалар болса)
if city_input:
    locations = search_location(city_input, LANGUAGES[selected_lang])
    if locations:
        # Пайдаланушы ажырата алуы үшін: "Қала (Облыс, Ел)" форматында тізім жасау
        loc_options = {f"{l.get('name')} ({l.get('admin1', '')}, {l.get('country', '')})": l for l in locations}
        selected_option = st.sidebar.selectbox(t["select_city"], list(loc_options.keys()))
        
        # "Іздеу" батырмасын басқанда деректерді жүктеу
        if st.sidebar.button(t["search"]):
            target = loc_options[selected_option]
            w_data, a_data = fetch_data(target["latitude"], target["longitude"])
            # Деректерді сессияда сақтаймыз (бет жаңартылғанда жоғалмауы үшін)
            st.session_state.current_data = {"loc": target, "weather": w_data, "air": a_data}
    else:
        st.sidebar.error("❌ Ештеңе табылмады")

# ЕГЕР ДЕРЕКТЕР ЖҮКТЕЛГЕН БОЛСА, НӘТИЖЕНІ ШЫҒАРУ
if "current_data" in st.session_state:
    data = st.session_state.current_data
    loc = data["loc"]
    w = data["weather"]
    cur = w["current"] # Қазіргі сәттегі ауа райы
    
    # Қала мен елдің атын басты тақырып етіп шығару
    st.title(f"📍 {loc['name']}, {loc.get('country', '')}")

    # Негізгі көрсеткіштерді 5 бағанға бөліп көрсету
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(t["temp"], f"{cur['temperature_2m']}°C")
    m2.metric(t["humidity"], f"{cur['relative_humidity_2m']}%")
    m3.metric(t["wind"], f"{cur['wind_speed_10m']} m/s")
    m4.metric(t["uv"], cur.get("uv_index", 0))
    
    # Ауа сапасын (AQI) тексеріп шығару
    aqi = data["air"]["current"]["us_aqi"] if data["air"] else "N/A"
    m5.metric(t["aqi"], aqi)

    # AQI деңгейіне қарай түсті хабарлама шығару (Денсаулық ескертуі)
    if isinstance(aqi, int):
        if aqi <= 50: st.success("✅ Ауа өте таза (Good)")
        elif aqi <= 100: st.warning("⚠️ Орташа сапа (Moderate)")
        else: st.error("🚨 Денсаулыққа зиянды деңгей (Unhealthy)")

    st.divider() # Көлденең сызық

    # ГРАФИК ПЕН БОЛЖАМ КЕСТЕСІ (2-ге 1 қатынасындағы бағандар)
    col_chart, col_table = st.columns([2, 1])
    
    with col_chart:
        st.subheader(t["temp_24h"])
        # Алдағы 24 сағаттың температурасын графикке айналдыру
        df_24h = pd.DataFrame({
            "Time": pd.to_datetime(w["hourly"]["time"][:24]),
            "Temp": w["hourly"]["temperature_2m"][:24]
        }).set_index("Time")
        st.line_chart(df_24h) # Сызықтық график

    with col_table:
        st.subheader(t["forecast_7d"])
        # 7 күндік болжамды кесте түрінде шығару
        df_7d = pd.DataFrame({
            "Date": w["daily"]["time"],
            "Max": w["daily"]["temperature_2m_max"],
            "Min": w["daily"]["temperature_2m_min"]
        })
        st.dataframe(df_7d, use_container_width=True)

    # AI ТАЛДАУ БӨЛІМІ (Жасанды интеллект кеңесі)
    if st.button(t["gpt_analysis"]):
        if client:
            with st.spinner("AI талдау жасауда..."):
                # AI-ға тапсырма (промпт) дайындау
                prompt = (f"Analyze weather for {loc['name']}. Current temp: {cur['temperature_2m']}C, "
                          f"AQI: {aqi}, Wind: {cur['wind_speed_10m']}m/s. "
                          f"Provide advice for the day in {selected_lang}.")
                # GPT моделінен жауап алу
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.info(response.choices[0].message.content) # Жауапты экранға шығару
        else:
            st.warning(t["no_ai"])

    # КАРТА БӨЛІМІ (Интерактивті Windy картасы)
    st.subheader(t["windy_map"])
    # Картаның қабатын таңдау (жаңбыр, жел немесе бұлт)
    layer = st.selectbox(t["map_layer"], ["rain", "wind", "clouds"])
    # Windy картасын iframe арқылы сайтқа кіріктіру
    map_url = f"https://www.windy.com/embed2.html?lat={loc['latitude']}&lon={loc['longitude']}&zoom=6&overlay={layer}"
    st.components.v1.iframe(map_url, height=500)
