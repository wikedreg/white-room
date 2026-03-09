import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import random
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SME - Master of Strategy", page_icon="♟️", layout="wide")

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
            "horario_diario": [],
            "conductas_log": []
        }

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f)

data = load_data()
peso_actual = data["peso_historial"][-1]["peso"]
meta_proteina_base = round(peso_actual * 2.0, 1)

# --- INTERFAZ PRINCIPAL ---
st.title("♟️ Sistema de Monitoreo de Estrategia v2.3")
nivel = np.sqrt(sum(data['stats'].values())) / 10
st.markdown(f"**Estratega:** Santos | **Nivel:** {nivel:.2f} | **Peso:** {peso_actual}kg")

tabs = st.tabs(["🕒 Protocolo Diario", "🧠 Asimilación de Conductas", "🥩 Nutrición Master", "📊 Atributos & Peso"])

# --- TAB 1: PROTOCOLO DIARIO (LINEA DE TIEMPO) ---
with tabs[0]:
    st.subheader("📅 Gestión de Bloques de Tiempo")
    with st.expander("➕ Añadir Actividad"):
        c1, c2, c3 = st.columns([1, 2, 1])
        rango = c1.text_input("Rango (ej. 07:00 - 14:00)")
        act = c2.text_input("Actividad")
        ico = c3.selectbox("Icono", ["🎓", "🚶", "🥩", "🏋️", "🏀", "💻", "😴", "📚"])
        if st.button("Actualizar Cronograma"):
            data["horario_diario"].append({"hora": rango, "actividad": act, "icono": ico})
            save_data(data)
            st.rerun()
    
    for item in data["horario_diario"]:
        st.write(f"**{item['hora']}** | {item['icono']} {item['actividad']}")
    if st.button("🗑️ Limpiar Todo"):
        data["horario_diario"] = []
        save_data(data); st.rerun()

# --- TAB 2: ASIMILACIÓN DE CONDUCTAS (NUEVO) ---
with tabs[1]:
    st.header("🎭 Módulo de Sincronización de Conductas")
    st.info("Entrena tu mente y comportamiento basándote en los perfiles maestros.")
    
    col_char, col_log_c = st.columns([1, 1])
    
    with col_char:
        personaje = st.selectbox("Selecciona el modelo a asimilar:", ["Sora (Estrategia)", "Ayanokōji (Eficiencia)", "Sakuta (Resiliencia)", "Masachika (Percepción)"])
        
        if personaje == "Sora (Estrategia)":
            st.write("**Directiva:** 'Aschente'. Gana antes de empezar. Visualiza todos los escenarios posibles.")
            meta_c = "Realizar una tarea compleja usando lógica lateral o un 'atajo' inteligente."
        elif personaje == "Ayanokōji (Eficiencia)":
            st.write("**Directiva:** Prioriza el resultado. Mantén tus verdaderas capacidades en reserva.")
            meta_c = "Completar una tarea universitaria en tiempo récord sin distracciones."
        elif personaje == "Sakuta (Resiliencia)":
            st.write("**Directiva:** Sé honesto contigo mismo. No dejes que la atmósfera social te controle.")
            meta_c = "Expresar una verdad honesta o mantener la calma ante una presión social."
        else: # Masachika
            st.write("**Directiva:** Observa lo que otros ignoran. Controla el ritmo de la conversación.")
            meta_c = "Identificar un rasgo no verbal en alguien durante una conversación."

        if st.button(f"Registrar Éxito: {personaje}"):
            puntos = {"Sora (Estrategia)": ("INT", 30), "Ayanokōji (Eficiencia)": ("RES", 30), 
                      "Sakuta (Resiliencia)": ("RES", 25), "Masachika (Percepción)": ("CHA", 30)}
            stat, val = puntos[personaje]
            data["stats"][stat] += val
            data["conductas_log"].append({"fecha": datetime.now().strftime("%Y-%m-%d"), "modelo": personaje, "meta": meta_c})
            save_data(data)
            st.success(f"Sincronización exitosa con {personaje}. +{val} XP en {stat}")

    with col_log_c:
        st.subheader("Historial de Asimilación")
        if data["conductas_log"]:
            st.dataframe(pd.DataFrame(data["conductas_log"]).tail(5))

# --- TAB 3: NUTRICIÓN MASTER (ACTUALIZADO) ---
with tabs[2]:
    st.header("🥩 Nutrición y Combustible")
    
    col_combos, col_custom = st.columns(2)
    
    with col_combos:
        st.subheader("Combos Rápidos")
        c1, c2 = st.columns(2)
        if c1.button("🌮 Tacos (32g Pro)"):
            data["consumo_proteina"].append({"fecha": datetime.now().strftime("%Y-%m-%d"), "gramos": 32, "item": "Tacos"})
            save_data(data); st.rerun()
        if c2.button("🥪 Torta (28g Pro)"):
            data["consumo_proteina"].append({"fecha": datetime.now().strftime("%Y-%m-%d"), "gramos": 28, "item": "Torta"})
            save_data(data); st.rerun()
            
    with col_custom:
        st.subheader("Entrada Personalizada")
        alimento_c = st.text_input("¿Qué comiste diferente?")
        pro_c = st.number_input("Gramos de proteína:", 0, 100, 15)
        if st.button("Registrar Alimento"):
            data["consumo_proteina"].append({"fecha": datetime.now().strftime("%Y-%m-%d"), "gramos": pro_c, "item": alimento_c})
            save_data(data); st.success(f"{alimento_c} registrado."); st.rerun()

    hoy = datetime.now().strftime("%Y-%m-%d")
    total_hoy = sum(log["gramos"] for log in data["consumo_proteina"] if log["fecha"] == hoy)
    st.metric("Proteína de Hoy", f"{total_hoy}g / {meta_proteina_base}g")
    st.progress(min(total_hoy/meta_proteina_base, 1.0))

# --- TAB 4: ATRIBUTOS & PESO ---
with tabs[3]:
    st.subheader("📊 Perfil del Jugador")
    df_peso = pd.DataFrame(data["peso_historial"])
    st.line_chart(df_peso.set_index("fecha"))
    
    with st.expander("Actualizar Peso"):
        np_peso = st.number_input("Peso actual (kg):", 40.0, 120.0, float(peso_actual))
        if st.button("Guardar"):
            data["peso_historial"].append({"fecha": datetime.now().strftime("%Y-%m-%d"), "peso": np_peso})
            save_data(data); st.rerun()
