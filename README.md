[weather_ai_5.py](https://github.com/user-attachments/files/25385819/weather_ai_5.py)[weather_ai_5.py](https://github.com/user-attachments/files/25385803/weather_ai_5.py)[weather_ai_5.py](https://github.com/user-attachments/files/25385786/weather_ai_5.py)# AEROO-AI-WEATHER-ANALYSIS
we are team TOBELI DARYN and we will win this competition


№1____The Documentation:



№2____The code:
1.Кодтын бәрін көшіруге ұсыныс беремін немесе кодтын файлын жүктеп алыныздар
2.WIN+R батырмасын басып іздеу жолына cmd деп жазыныздар
3.команда терезесі ашылған кезде мына команданы жазыныз:streamlit run weather_ai_5.py , себебі F5 бұл жерде істемейді сол себепті команданы енгізуге ұсыныс береміз
4.сайт ашылған кезде іздеу жоланы керек қаланы,ауылды жазыныз
[weather_ai_5.py]

import stimport streamlit as st
import requests
import pandas as pd
from datetime import datetime

# =========================================================
# 🧭 КӨМЕКШІ ЛОГИКА
# =========================================================
def get_wind_direction(degrees):
    directions = ['⬆️ Солтүстік', '↗️ С-Шығыс', '➡️ Шығыс', '↘️ О-Шығыс', '⬇️ Оңтүстік', '↙️ О-Батыс', '⬅️ Батыс', '↖️ С-Батыс']
    index = round(degrees / 45) % 8
    return directions[index]

# =========================================================
# 🧠 ЖИ ТАЛДАУ (SMART LOGIC)
# =========================================================
def advanced_ai_advisor(current):
    t = current.get('temperature_2m', 0)
    w = current.get('wind_speed_10m', 0)
    uv = current.get('uv_index', 0)
    rh = current.get('relative_humidity_2m', 0)
    
    advice = {"outfit": "", "activity": "", "health": ""}
    
    # 👕 Киім бойынша кеңес
    if t > 25: advice["outfit"] = "Жеңіл футболка, шорты немесе зығыр матадан тігілген киімдер. Күннен қорғайтын көзілдірік."
    elif 15 <= t <= 25: advice["outfit"] = "Жеңіл жемпір, джинсы немесе ұзын жеңді көйлек."
    elif 5 <= t < 15: advice["outfit"] = "Күздік күрте (ветровка), жеңіл пальто және жабық аяқ киім."
    elif -5 <= t < 5: advice["outfit"] = "Жылы куртка, бас киім және шарф."
    else: advice["outfit"] = "Қалың пуховик, қолғап, термо-іш киім және жылы етік."

    # 🏃 Спорт және белсенділік
    if 10 < t < 25 and w < 15: advice["activity"] = "Сыртта спортпен шұғылдануға тамаша уақыт! Жүгіруге немесе паркке шығыңыз."
    elif t > 30 or t < -15: advice["activity"] = "Сырттағы белсенділікті шектеген жөн. Жаттығуды залда жасаңыз."
    else: advice["activity"] = "Қысқа серуенге қолайлы, бірақ желден қорғаныңыз."

    # 🏥 Денсаулық ескертулері
    health_alerts = []
    if uv >= 6: health_alerts.append("☀️ Ультракүлгін жоғары: SPF 30+ кремін қолданыңыз.")
    if rh > 80: health_alerts.append("💧 Ылғалдылық жоғары: Тыныс алу жолдарына күш түсуі мүмкін.")
    if w > 40: health_alerts.append("🌬️ Дауылды жел: Қан қысымы бар жандарға абай болу керек.")
    
    advice["health"] = health_alerts if health_alerts else ["✅ Жағдай тұрақты."]
    
    return advice

# =========================================================
# 📡 ДЕРЕКТЕРДІ АЛУ
# =========================================================
def fetch_weather(city):
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en").json()
        if 'results' not in geo: return None
        loc = geo['results'][0]
        
        url = (f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}"
               f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,wind_direction_10m,uv_index"
               f"&hourly=temperature_2m,precipitation_probability&timezone=auto")
        
        data = requests.get(url).json()
        data.update({'full_name': f"{loc['name']}, {loc['country']}", 'lat': loc['latitude'], 'lon': loc['longitude']})
        return data
    except: return None

# =========================================================
# 🖥️ STREAMLIT ИНТЕРФЕЙСІ
# =========================================================
st.set_page_config(page_title="Guardian AI Weather", layout="wide", page_icon="🌤️")

# Стильдерді реттеу
st.markdown("""<style> .stMetric { background: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #ddd; } </style>""", unsafe_allow_html=True)

st.title("🛡️ Guardian AI: Ақылды Метео-талдау")
st.write(f"Бүгінгі күн: **{datetime.now().strftime('%d.%m.%Y')}**")

with st.sidebar:
    st.header("📍 Локация")
    city = st.text_input("Қала атын жазыңыз:", "Astana")
    run = st.button("Анализ жасау", use_container_width=True)

if run:
    data = fetch_weather(city)
    if data:
        curr = data['current']
        ai = advanced_ai_advisor(curr)
        
        st.header(f"🏙️ {data['full_name']}")
        
        # 1-БӨЛІМ: Негізгі метрикалар
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌡️ Температура", f"{curr['temperature_2m']}°C", f"Сезілуі: {curr['apparent_temperature']}°C")
        col2.metric("🌬️ Жел", f"{curr['wind_speed_10m']} км/с", get_wind_direction(curr['wind_direction_10m']))
        col3.metric("☀️ UV Индекс", f"{curr.get('uv_index', 0)}")
        col4.metric("💧 Ылғалдылық", f"{curr['relative_humidity_2m']}%")
        
        st.divider()
        
        # 2-БӨЛІМ: ЖИ Кеңестері
        st.subheader("🤖 ЖИ Кеңесшінің қорытындысы")
        
        c_outfit, c_activity, c_health = st.columns(3)
        
        with c_outfit:
            st.info(f"**👕 Не кию керек?**\n\n{ai['outfit']}")
        
        with c_activity:
            st.success(f"**🏃 Белсенділік:**\n\n{ai['activity']}")
            
        with c_health:
            st.warning("**⚠️ Денсаулық ескертулері:**\n\n" + "\n".join(ai['health']))

        # 3-БӨЛІМ: Графиктер
        st.divider()
        st.subheader("📊 Тәуліктік болжам")
        chart_data = pd.DataFrame({
            "Уақыт": data['hourly']['time'][:24],
            "Температура": data['hourly']['temperature_2m'][:24],
            "Жауын-шашын %": data['hourly']['precipitation_probability'][:24]
        })
        st.line_chart(chart_data.set_index("Уақыт"))

        # 4-БӨЛІМ: Карта
        st.subheader("🌍 Аймақтық карта")
        st.components.v1.iframe(f"https://www.windy.com/embed2.html?lat={data['lat']}&lon={data['lon']}&zoom=6", height=450)

    else:
        st.error("Қала деректері табылмады. Жазылуын тексеріңіз (мысалы: Almaty, London, Istanbul).")

st.markdown("---")
st.caption("Guardian AI — деректер ашық Open-Meteo API арқылы алынады.")
[weather_ai_5.py](https://github.com/user-attachments/files/25385809/weather_ai_5.py)
reamlit as st
import requests
import pandas as pd
from datetime import datetime

# =========================================================
# 🧭 КӨМЕКШІ ЛОГИКА
# =========================================================
def get_wind_direction(degrees):
    directions = ['⬆️ Солтүстік', '↗️ С-Шығыс', '➡️ Шығыс', '↘️ О-Шығыс', '⬇️ Оңтүстік', '↙️ О-Батыс', '⬅️ Батыс', '↖️ С-Батыс']
    index = round(degrees / 45) % 8
    return directions[index]

# =========================================================
# 🧠 ЖИ ТАЛДАУ (SMART LOGIC)
# =========================================================
def advanced_ai_advisor(current):
    t = current.get('temperature_2m', 0)
    w = current.get('wind_speed_10m', 0)
    uv = current.get('uv_index', 0)
    rh = current.get('relative_humidity_2m', 0)
    
    advice = {"outfit": "", "activity": "", "health": ""}
    
    # 👕 Киім бойынша кеңес
    if t > 25: advice["outfit"] = "Жеңіл футболка, шорты немесе зығыр матадан тігілген киімдер. Күннен қорғайтын көзілдірік."
    elif 15 <= t <= 25: advice["outfit"] = "Жеңіл жемпір, джинсы немесе ұзын жеңді көйлек."
    elif 5 <= t < 15: advice["outfit"] = "Күздік күрте (ветровка), жеңіл пальто және жабық аяқ киім."
    elif -5 <= t < 5: advice["outfit"] = "Жылы куртка, бас киім және шарф."
    else: advice["outfit"] = "Қалың пуховик, қолғап, термо-іш киім және жылы етік."

    # 🏃 Спорт және белсенділік
    if 10 < t < 25 and w < 15: advice["activity"] = "Сыртта спортпен шұғылдануға тамаша уақыт! Жүгіруге немесе паркке шығыңыз."
    elif t > 30 or t < -15: advice["activity"] = "Сырттағы белсенділікті шектеген жөн. Жаттығуды залда жасаңыз."
    else: advice["activity"] = "Қысқа серуенге қолайлы, бірақ желден қорғаныңыз."

    # 🏥 Денсаулық ескертулері
    health_alerts = []
    if uv >= 6: health_alerts.append("☀️ Ультракүлгін жоғары: SPF 30+ кремін қолданыңыз.")
    if rh > 80: health_alerts.append("💧 Ылғалдылық жоғары: Тыныс алу жолдарына күш түсуі мүмкін.")
    if w > 40: health_alerts.append("🌬️ Дауылды жел: Қан қысымы бар жандарға абай болу керек.")
    
    advice["health"] = health_alerts if health_alerts else ["✅ Жағдай тұрақты."]
    
    return advice

# =========================================================
# 📡 ДЕРЕКТЕРДІ АЛУ
# =========================================================
def fetch_weather(city):
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en").json()
        if 'results' not in geo: return None
        loc = geo['results'][0]
        
        url = (f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}"
               f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,wind_direction_10m,uv_index"
               f"&hourly=temperature_2m,precipitation_probability&timezone=auto")
        
        data = requests.get(url).json()
        data.update({'full_name': f"{loc['name']}, {loc['country']}", 'lat': loc['latitude'], 'lon': loc['longitude']})
        return data
    except: return None

# =========================================================
# 🖥️ STREAMLIT ИНТЕРФЕЙСІ
# =========================================================
st.set_page_config(page_title="Guardian AI Weather", layout="wide", page_icon="🌤️")

# Стильдерді реттеу
st.markdown("""<style> .stMetric { background: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #ddd; } </style>""", unsafe_allow_html=True)

st.title("🛡️ Guardian AI: Ақылды Метео-талдау")
st.write(f"Бүгінгі күн: **{datetime.now().strftime('%d.%m.%Y')}**")

with st.sidebar:
    st.header("📍 Локация")
    city = st.text_input("Қала атын жазыңыз:", "Astana")
    run = st.button("Анализ жасау", use_container_width=True)

if run:
    data = fetch_weather(city)
    if data:
        curr = data['current']
        ai = advanced_ai_advisor(curr)
        
        st.header(f"🏙️ {data['full_name']}")
        
        # 1-БӨЛІМ: Негізгі метрикалар
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌡️ Температура", f"{curr['temperature_2m']}°C", f"Сезілуі: {curr['apparent_temperature']}°C")
        col2.metric("🌬️ Жел", f"{curr['wind_speed_10m']} км/с", get_wind_direction(curr['wind_direction_10m']))
        col3.metric("☀️ UV Индекс", f"{curr.get('uv_index', 0)}")
        col4.metric("💧 Ылғалдылық", f"{curr['relative_humidity_2m']}%")
        
        st.divider()
        
        # 2-БӨЛІМ: ЖИ Кеңестері
        st.subheader("🤖 ЖИ Кеңесшінің қорытындысы")
        
        c_outfit, c_activity, c_health = st.columns(3)
        
        with c_outfit:
            st.info(f"**👕 Не кию керек?**\n\n{ai['outfit']}")
        
        with c_activity:
            st.success(f"**🏃 Белсенділік:**\n\n{ai['activity']}")
            
        with c_health:
            st.warning("**⚠️ Денсаулық ескертулері:**\n\n" + "\n".join(ai['health']))

        # 3-БӨЛІМ: Графиктер
        st.divider()
        st.subheader("📊 Тәуліктік болжам")
        chart_data = pd.DataFrame({
            "Уақыт": data['hourly']['time'][:24],
            "Температура": data['hourly']['temperature_2m'][:24],
            "Жауын-шашын %": data['hourly']['precipitation_probability'][:24]
        })
        st.line_chart(chart_data.set_index("Уақыт"))

        # 4-БӨЛІМ: Карта
        st.subheader("🌍 Аймақтық карта")
        st.components.v1.iframe(f"https://www.windy.com/embed2.html?lat={data['lat']}&lon={data['lon']}&zoom=6", height=450)

    else:
        st.error("Қала деректері табылмады. Жазылуын тексеріңіз (мысалы: Almaty, London, Istanbul).")

st.markdown("---")
st.caption("Guardian AI — деректер ашық Open-Meteo API арқылы алынады.")
 weather_ai_5.py…]()




№3____The pitch-deck:


№4____The MVP:
