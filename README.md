# AEROO-AI-WEATHER-ANALYSIS
we are team TOLEBI DARYN and we will win this competition


№1____The Documentation:



№2____The code:
[weather_ai_4.py](https://github.com/user-attachments/files/25122231/weather_ai_4.py)
import streamlit as st
import requests
#streamlit run weather_ai_4.py команда экранына енгізу керек
# =========================================================
# 🧭 ҚОСЫМША ФУНКЦИЯЛАР (Жел бағыты)
# =========================================================
def get_wind_direction(degrees):
    directions = ['⬆️ С', '↗️ СШ', '➡️ Ш', '↘️ ОШ', '⬇️ О', '↙️ ОБ', '⬅️ Б', '↖️ СБ']
    index = round(degrees / 45) % 8
    return directions[index]

# =========================================================
# 🧠 ЖИ-МОНИТОРИНГ ЖӘНЕ ТАБИҒИ АПАТТАРДЫ БОЛЖАУ
# =========================================================
def disaster_ai_analysis(current, daily):
    alerts = []
    recommendations = []
    danger_level = "Қалыпты"
    
    # Деректерді алу
    wind = current.get('wind_speed_10m', 0)
    gusts = current.get('wind_gusts_10m', 0)
    temp = current.get('temperature_2m', 0)
    precip = current.get('precipitation', 0)
    humidity = current.get('relative_humidity_2m', 0)
    uv = daily.get('uv_index_max', [0])[0]

    # 1. СУ ТАСҚЫНЫ ҚАУПІ (Жауын-шашын анализі)
    if precip > 10:
        alerts.append("🌊 **ҚАУІП:** Нөсер жауын! Су тасқыны қаупі жоғары.")
        recommendations.append("📢 Төмен аймақтардан аулақ болыңыз, эвакуация жоспарын дайындаңыз.")
        danger_level = "Жоғары"

    # 2. ӨРТ ҚАУПІ (Ыстық + Құрғақшылық + Жел)
    if temp > 30 and humidity < 30 and wind > 15:
        alerts.append("🔥 **ҚАУІП:** Орман өрті қаупі өте жоғары (Құрғақ әрі желді).")
        recommendations.append("🚫 Табиғатта от жағуға қатаң тыйым салынады!")
        danger_level = "Көтеріңкі"

    # 3. ДАУЫЛ ЖӘНЕ ҚИРАТУШЫ ЖЕЛ
    if gusts > 70:
        alerts.append(f"🌪️ **АПАТТЫ ЖЕЛ:** {gusts} км/сағ жылдамдықпен ұруы мүмкін!")
        recommendations.append("🏠 Үйден шықпаңыз, терезелерден алыс тұрыңыз.")
        danger_level = "Экстремалды"
    elif wind > 40:
        alerts.append("🚩 **КҮШТІ ДАУЫЛ:** Ғимараттар мен ағаштарға зақым келуі мүмкін.")
        danger_level = "Жоғары"

    # 4. АНОМАЛЬДЫ ЫСТЫҚ/СУЫҚ
    if temp > 40:
        alerts.append("🥵 **ЭКСТРЕМАЛДЫ ЫСТЫҚ:** Күн өту және жүрек-қан тамырларына салмақ.")
    elif temp < -30:
        alerts.append("🥶 **АНОМАЛЬДЫ СУЫҚ:** Гипотермия қаупі жоғары.")

    if not alerts:
        alerts.append("✅ Қазіргі уақытта апаттық қауіп тіркелген жоқ.")
        recommendations.append("🌤️ Күнделікті істерді жалғастыра беріңіз.")

    return alerts, recommendations, danger_level

# =========================================================
# 📡 ДЕРЕКТЕРДІ АЛУ (Open-Meteo API)
# =========================================================
def get_weather_data(city):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"
        geo_res = requests.get(geo_url).json()
        if not geo_res.get('results'): return None
        loc = geo_res['results'][0]
        
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}"
            f"&current=temperature_2m,relative_humidity_2m,pressure_msl,wind_speed_10m,wind_direction_10m,wind_gusts_10m,precipitation"
            f"&daily=uv_index_max,precipitation_sum&timezone=auto"
        )
        w_res = requests.get(weather_url).json()
        w_res.update({'full_name': f"{loc.get('name')}, {loc.get('country')}", 'lat': loc['latitude'], 'lon': loc['longitude']})
        return w_res
    except: return None

# =========================================================
# 🖥️ ИНТЕРФЕЙС
# =========================================================
st.set_page_config(page_title="Guardian AI - Disaster Monitor", layout="wide")

st.title("🛡️ Guardian AI: Табиғи апаттарды болжау жүйесі")
st.markdown("---")

city = st.text_input("Бақылау аймағын (қала) енгізіңіз:", "Astana")

if st.button("СЕРУЕНДІ БАСТАУ (AI SCAN)"):
    data = get_weather_data(city)
    
    if data:
        c = data['current']
        d = data['daily']
        alerts, recs, level = disaster_ai_analysis(c, d)

        # Статусты көрсету
        st.subheader(f"📍 Нысан: {data['full_name']}")
        
        # Қауіп деңгейіне қарай түс таңдау
        status_colors = {"Қалыпты": "green", "Көтеріңкі": "blue", "Жоғары": "orange", "Экстремалды": "red"}
        st.markdown(f"### Қауіп деңгейі: :{status_colors[level]}[{level}]")

        # Негізгі көрсеткіштер
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Температура", f"{c['temperature_2m']}°C")
        col2.metric("Жел жылдамдығы", f"{c['wind_speed_10m']} км/сағ")
        col3.metric("Ылғалдылық", f"{c['relative_humidity_2m']}%")
        col4.metric("Жауын-шашын", f"{c['precipitation']} мм")

        # ЖИ Аналитика бөлімі
        st.divider()
        a_col, r_col = st.columns(2)
        with a_col:
            st.error("⚠️ **Табылған қауіп-қатерлер:**")
            for a in alerts: st.write(a)
        with r_col:
            st.success("💡 **Қорғану шаралары (ЖИ ұсынысы):**")
            for r in recs: st.write(r)

        # Карта (Windy - Апаттарды визуалды көру үшін)
        st.divider()
        st.write("### 🌍 Аймақтың спутниктік картасы")
        windy_url = f"https://www.windy.com/embed2.html?lat={data['lat']}&lon={data['lon']}&zoom=6&overlay=capalerts&product=capalerts"
        st.components.v1.iframe(windy_url, height=500)
    else:
        st.error("Деректерді алу мүмкін болмады. Қала атын тексеріңіз.")

st.sidebar.info("Бұл жүйе Open-Meteo деректерін пайдалана отырып, ЖИ алгоритмдері арқылы табиғи апаттардың алдын алуға көмектеседі.")


№3____The pitch-deck:


№4____The MVP:
