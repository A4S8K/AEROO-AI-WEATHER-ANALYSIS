# AEROO-AI-WEATHER-ANALYSIS
we are team TOBELI DARYN and we will win this competition


№1____The Documentation:



№2____The code:
1.Кодтын бәрін көшіруге ұсыныс беремін немесе кодтын файлын жүктеп алыныздар
2.WIN+R батырмасын басып іздеу жолына cmd деп жазыныздар
3.команда терезесі ашылған кезде мына команданы жазыныз:streamlit run weather_ai_4.py , себебі F5 бұл жерде істемейді сол себепті команданы енгізуге ұсыныс береміз
4.сайт ашылған кезде іздеу жоланы керек қаланы,ауылды жазыныз
[weather_ai_4.py](https://github.com/user-attachments/files/25205635/weather_ai_4.py)


import streamlit as st
import requests
#streamlit run weather_ai_4.py
# =========================================================
# 🧭 ҚОСЫМША ФУНКЦИЯЛАР
# =========================================================
def get_wind_direction(degrees):
    directions = ['⬆️ С', '↗️ СШ', '➡️ Ш', '↘️ ОШ', '⬇️ О', '↙️ ОБ', '⬅️ Б', '↖️ СБ']
    index = round(degrees / 45) % 8
    return directions[index]

# =========================================================
# 🧠 ЖИ-ТАЛДАУ (АВТОМАТТЫ ЛОГИКА)
# =========================================================
def ai_weather_analysis(current):
    alerts = []
    recs = []
    
    temp = current.get('temperature_2m', 0)
    wind = current.get('wind_speed_10m', 0)
    precip = current.get('precipitation', 0)
    hum = current.get('relative_humidity_2m', 0)

    # Температура талдауы
    if temp > 35:
        alerts.append(f"🔥 **Аномальды ыстық:** {temp}°C. Күн өту қаупі бар.")
        recs.append("Көбірек су ішіп, көлеңкеде болыңыз.")
    elif temp < -20:
        alerts.append(f"🥶 **Қатты аяз:** {temp}°C. Үсік шалу қаупі.")
        recs.append("Жылы киініңіз, далада ұзақ тұрмаңыз.")

    # Жел мен Жауын талдауы
    if wind > 40:
        alerts.append(f"🌬️ **Күшті жел:** {wind} км/сағ. Дауылды ескерту!")
        recs.append("Ағаштар мен билбордтардан алыс жүріңіз.")
    
    if precip > 5:
        alerts.append(f"🌧️ **Жауын-шашын:** Жаңбыр/Қар жауып тұр.")
        if temp < 2 and temp > -2:
            alerts.append("⛸️ **Көктайғақ қаупі:** Жолдар тайғақ болуы мүмкін.")

    # Қалыпты жағдай
    if not alerts:
        alerts.append("✅ Ауа райы тұрақты, қауіпті құбылыстар байқалмайды.")
        recs.append("Күнделікті жоспарыңызды жалғастыра беріңіз.")
        
    return alerts, recs

# =========================================================
# 📡 ДЕРЕКТЕРДІ АЛУ
# =========================================================
def get_weather(city):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"
        res = requests.get(geo_url).json()
        if not res.get('results'): return None
        loc = res['results'][0]
        
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,precipitation&timezone=auto"
        weather = requests.get(w_url).json()
        weather.update({'name': f"{loc['name']}, {loc['country']}", 'lat': loc['latitude'], 'lon': loc['longitude']})
        return weather
    except: return None

# =========================================================
# 🖥️ ИНТЕРФЕЙС
# =========================================================
st.set_page_config(page_title="Guardian AI", layout="wide")
st.title("🛡️ Guardian AI: Метео-талдау")

with st.sidebar:
    city_name = st.text_input("📍 Қаланы енгізіңіз:", "Astana")
    start = st.button("АНАЛИЗ ЖАСАУ")

if start:
    data = get_weather(city_name)
    if data:
        c = data['current']
        alerts, recs = ai_weather_analysis(c)
        
        st.header(f"📍 {data['name']}")
        
        # Метрикалар
        col = st.columns(4)
        col[0].metric("🌡️ Температура", f"{c['temperature_2m']}°C")
        col[1].metric("🌬️ Жел", f"{c['wind_speed_10m']} км/с")
        col[2].metric("🧭 Бағыты", get_wind_direction(c['wind_direction_10m']))
        col[3].metric("💧 Ылғалдылық", f"{c['relative_humidity_2m']}%")

        st.divider()
        
        # ЖИ Анализ бөлімі
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🔎 ЖИ Талдау:")
            for a in alerts: st.info(a)
        with c2:
            st.subheader("💡 Ұсыныстар:")
            for r in recs: st.write(f"- {r}")

        st.divider()
        st.subheader("🌍 Карта")
        st.components.v1.iframe(f"https://www.windy.com/embed2.html?lat={data['lat']}&lon={data['lon']}&zoom=5", height=400)
    else:
        st.error("Қала табылмады.")




№3____The pitch-deck:


№4____The MVP:
