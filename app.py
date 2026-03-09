import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import random
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SME - Full Adaptive", page_icon="♟️", layout="wide")

def load_data():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "stats": {"STR": 0, "INT": 0, "CHA": 0, "RES": 0},
            "logs": [],
            "peso_historial": [{"fecha": datetime.now().strftime("%Y-%m-%d"), "peso": 62.0}],
            "rutinas": {dia: "" for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]},
            "consumo_proteina": [],
            "horario_diario": []
        }

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f)

data = load_data()
peso_actual = data["peso_historial"][-1]["peso"]
meta_proteina_base = round(peso_actual * 2.0, 1)

# --- DETECCIÓN DE DÍA ---
dias_map = {"Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", 
            "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"}
dia_hoy_en = datetime.now().strftime("%A")
dia_hoy_es = dias_map.get(dia_hoy_en, "Lunes")

# --- INTERFAZ ---
st.title("♟️ Sistema de Monitoreo de Estrategia v2.2")
nivel = np.sqrt(sum(data['stats'].values())) / 10
st.markdown(f"**Estratega:** Santos | **Nivel:** {nivel:.2f} | **Día:** {dia_hoy_es}")

tabs = st.tabs(["🕒 Protocolo Diario", "🏀 Modo Evento", "🥩 Nutrición", "📊 Atributos"])

# --- TAB 1: PROTOCOLO DIARIO (LINEA DE TIEMPO) ---
with tabs[0]:
    st.subheader(f"📅 Cronograma: {dia_hoy_es}")
    
    with st.expander("➕ Gestionar Bloques de Tiempo"):
        col_h, col_a, col_i = st.columns([1, 2, 1])
        rango = col_h.text_input("Rango (ej. 07:00 - 14:00)")
        act = col_a.text_input("Actividad")
        ico = col_i.selectbox("Icono", ["🎓", "🚶", "🥩", "🏋️", "🏀", "💻", "😴", "📚"])
        if st.button("Añadir al Horario"):
            data["horario_diario"].append({"hora": rango, "actividad": act, "icono": ico, "dia": dia_hoy_es})
            save_data(data)
            st.rerun()

    # Mostrar Timeline filtrada por el día actual
    horario_hoy = [h for h in data["horario_diario"] if h.get("dia") == dia_hoy_es]
    if horario_hoy:
        for item in horario_hoy:
            st.write(f"**{item['hora']}** | {item['icono']} {item['actividad']}")
    else:
        st.info("No hay actividades registradas para hoy.")
    
    if st.button("🗑️ Limpiar Horario del Día"):
        data["horario_diario"] = [h for h in data["horario_diario"] if h.get("dia") != dia_hoy_es]
        save_data(data)
        st.rerun()

# --- TAB 2: MODO EVENTO (ESPECIAL FIN DE SEMANA) ---
with tabs[1]:
    if dia_hoy_es in ["Sábado", "Domingo"]:
        st.warning("⚠️ **ALERTA DE FIN DE SEMANA DETECTADA**")
        st.subheader("¿Hay partido de Básquetbol o Entrenamiento Extra hoy?")
        
        col_b1, col_b2 = st.columns(2)
        if col_b1.button("🏀 SÍ, HAY PARTIDO"):
            st.session_state.evento_activo = "Básquet"
            st.success("Modo Básquet Activado: Meta de hidratación y carbohidratos aumentada.")
        if col_b2.button("🏋️ SÍ, GYM EXTRA"):
            st.session_state.evento_activo = "Gym"
            st.success("Modo Hipertrofia Activado: Meta de proteína +20g.")
    else:
        st.info("El Modo Evento se activa automáticamente los fines de semana, pero puedes forzarlo si tienes un partido entre semana.")
        if st.button("🚀 Forzar Modo Evento"):
            st.session_state.evento_activo = "Extra"

    if 'evento_activo' in st.session_state:
        st.write(f"**Evento Actual:** {st.session_state.evento_activo}")
        if st.button("✅ Finalizar Evento y Ganar XP"):
            data["stats"]["STR"] += 40
            data["stats"]["RES"] += 20
            save_data(data)
            del st.session_state.evento_activo
            st.balloons()
            st.rerun()

# --- TAB 3: NUTRICIÓN ---
with tabs[2]:
    # Ajuste de meta si hay evento
    ajuste_pro = 20 if st.session_state.get('evento_activo') == "Gym" else 0
    meta_final = meta_proteina_base + ajuste_pro
    
    st.header("🥩 Registro de Proteína Uni")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("🌮 Tacos (4)"): data["consumo_proteina"].append({"fecha": datetime.now().strftime("%Y-%m-%d"), "gramos": 32, "item": "Tacos"}); save_data(data)
    if c2.button("🥪 Torta"): data["consumo_proteina"].append({"fecha": datetime.now().strftime("%Y-%m-%d"), "gramos": 28, "item": "Torta"}); save_data(data)
    if c3.button("🌯 Burrito"): data["consumo_proteina"].append({"fecha": datetime.now().strftime("%Y-%m-%d"), "gramos": 24, "item": "Burrito"}); save_data(data)
    if c4.button("🧀 Gringa"): data["consumo_proteina"].append({"fecha": datetime.now().strftime("%Y-%m-%d"), "gramos": 26, "item": "Gringa"}); save_data(data)

    hoy = datetime.now().strftime("%Y-%m-%d")
    total_hoy = sum(log["gramos"] for log in data["consumo_proteina"] if log["fecha"] == hoy)
    st.metric("Proteína Acumulada", f"{total_hoy}g / {meta_final}g", delta=f"+{ajuste_pro}g por evento" if ajuste_pro > 0 else None)
    st.progress(min(total_hoy/meta_final, 1.0))

# --- TAB 4: ATRIBUTOS (RADAR) ---
with tabs[3]:
    st.subheader("📊 Perfil del Jugador")
    categories = ['STR', 'INT', 'CHA', 'RES']
    values = [data["stats"].get(c, 0) for c in categories]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    values += values[:1]; angles += angles[:1]
    fig, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='#ff4b4b', alpha=0.3)
    ax.plot(angles, values, color='#ff4b4b', marker='o')
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(categories)
    st.pyplot(fig)
