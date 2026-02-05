# AEROO-AI-WEATHER-ANALYSIS
we are team TOLEBI DARYN and we will win this competition


the code AI:
[weather ai.py](https://github.com/user-attachments/files/25103227/weather.ai.py)
import streamlit as st
import requests

# =========================================================
# 🧭 ЖЕЛ БАҒЫТЫН АНЫҚТАУ ФУНКЦИЯСЫ
# =========================================================
def get_wind_direction(degrees):
    """Градусты мәтіндік бағытқа айналдыру"""
    directions = ['⬆️ С (Солтүстік)', '↗️ СШ (Солтүстік-Шығыс)', '➡️ Ш (Шығыс)', 
                  '↘️ ОШ (Оңтүстік-Шығыс)', '⬇️ О (Оңтүстік)', '↙️ ОБ (Оңтүстік-Батыс)', 
                  '⬅️ Б (Батыс)', '↖️ СБ (Солтүстік-Батыс)']
    index = round(degrees / 45) % 8
    return directions[index]

# =========================================================
# 🧠 ЖАНДАНДЫРЫЛҒАН ЖИ-ТАЛДАУ ЛОГИКАСЫ
# =========================================================
def ai_analyze(c, d):
    alerts = []
    recommendations = []
    
    wind_speed = c.get('wind_speed_10m', 0) or 0
    wind_gusts = c.get('wind_gusts_10m', 0) or 0
    temp = c.get('temperature_2m', 0) or 0
    uv_list = d.get('uv_index_max', [0])
    uv = uv_list[0] if uv_list and uv_list[0] is not None else 0

    # Жел бойынша талдау
    if wind_speed > 40 or wind_gusts > 60:
        alerts.append(f"🚩 **ҚАУІПТІ ЖЕЛ:** Жел жылдамдығы {wind_speed} км/сағ! Ғимараттардан алыс болыңыз.")
        recommendations.append("🚗 Көлікті ағаштардың астына қоймаңыз.")
    elif wind_speed > 20:
        alerts.append("🌬️ **КҮШТІ ЖЕЛ:** Далада абай болыңыз.")

    if temp > 35:
        alerts.append("🔥 **АНОМАЛЬДЫ ЫСТЫҚ:** Күн өту қаупі бар.")
        recommendations.append("🥤 Көбірек су ішіңіз.")
    
    if uv > 7:
        alerts.append(f"☀️ **ЖОҒАРЫ УК-ИНДЕКС ({uv}):** Тері үшін қауіпті.")
        recommendations.append("🧴 SPF 30+ қорғаныс кремін қолданыңыз.")

    if not alerts:
        alerts.append("✅ Ауа райы параметрлері қалыпты.")
        recommendations.append("🌤️ Серуендеуге жақсы күн.")
        
    return alerts, recommendations

# =========================================================
# 📡 ДЕРЕКТЕРДІ АЛУ
# =========================================================
def get_weather(city, model="best_match"):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"
        geo_res = requests.get(geo_url, timeout=10).json()
        if not geo_res.get('results'): return None
        loc = geo_res['results'][0]
        
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}"
            f"&current=temperature_2m,relative_humidity_2m,pressure_msl,wind_speed_10m,wind_direction_10m,wind_gusts_10m,precipitation"
            f"&daily=uv_index_max&timezone=auto"
        )
        
        if model != "best_match":
            weather_url += f"&models={model}"

        w_res = requests.get(weather_url, timeout=10).json()
        w_res.update({
            'full_name': f"{loc.get('name')}, {loc.get('country')}",
            'lat': loc['latitude'], 'lon': loc['longitude']
        })
        return w_res
    except: return None

# =========================================================
# 🖥️ ИНТЕРФЕЙС
# =========================================================
st.set_page_config(page_title="AI Weather Satellite", layout="wide")
st.title("🤖 ЖИ Метео-Спутник және анализ")

city = st.text_input("Қаланы енгізіңіз:", "Astana")
selected_model = st.sidebar.selectbox("Болжам моделі:", ["best_match", "ecmwf_ifs025", "gfs_seamless"])

if st.button("МОНИТОРИНГТІ ІСКЕ ҚОСУ"):
    data = get_weather(city, selected_model)
    
    if data and "current" in data:
        c = data['current']
        d = data['daily']
        
        st.subheader(f"📍 {data['full_name']}")
        
        # 1. НЕГІЗГІ МЕТРИКАЛАР
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Температура", f"{c['temperature_2m']}°C")
        col2.metric("Ылғалдылық", f"{c['relative_humidity_2m']}%")
        col3.metric("Қысым", f"{int(c['pressure_msl'] * 0.75)} мм")
        uv_val = d['uv_index_max'][0] if d['uv_index_max'][0] is not None else "Н/Д"
        col4.metric("УК-индекс", uv_val)

        # 2. ЖЕЛ ПАРАМЕТРЛЕРІ (ЖАҢА БӨЛІМ)
        st.write("### 🌬️ Жел жағдайы")
        w_col1, w_col2, w_col3 = st.columns(3)
        w_col1.metric("Жел жылдамдығы", f"{c['wind_speed_10m']} км/сағ")
        w_col2.metric("Жел екпіні (макс)", f"{c['wind_gusts_10m']} км/сағ")
        w_col3.metric("Жел бағыты", get_wind_direction(c['wind_direction_10m']))
            
        # 3. ЖИ-ТАЛДАУ
        st.divider()
        alerts, recommendations = ai_analyze(c, d)
        a_col, r_col = st.columns(2)
        with a_col:
            st.info("🔎 **Талдау:**")
            for a in alerts: st.write(a)
        with r_col:
            st.success("💡 **Ұсыныстар:**")
            for r in recommendations: st.write(r)

        # 4. КАРТА
        st.divider()
        windy_url = f"https://www.windy.com/embed2.html?lat={data['lat']}&lon={data['lon']}&zoom=5&overlay=wind&product=wind"
        st.components.v1.iframe(windy_url, height=500)
        
    else:
        st.error("Қала табылмады немесе деректерді алу мүмкін емес.")
