import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import random
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SME - Blank Mode", page_icon="♟️", layout="wide")

# --- SISTEMA DE DATOS ---
def load_data():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"stats": {"STR": 0, "INT": 0, "CHA": 0, "RES": 0}, "logs": []}

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f)

data = load_data()

# --- LÓGICA DEL MODO DESAFÍO SORA ---
def get_sora_challenge():
    challenges = [
        {"pilar": "INT", "desc": "Explica un concepto de .NET a alguien (o un pato de goma) de forma simple.", "bonus": 25},
        {"pilar": "INT", "desc": "Refactoriza un código viejo o resuelve un ejercicio de lógica en Python.", "bonus": 30},
        {"pilar": "CHA", "desc": "Escucha a alguien sin interrumpir ni dar soluciones por 5 minutos.", "bonus": 40},
        {"pilar": "CHA", "desc": "Analiza el lenguaje corporal de 3 personas hoy y deduce su estado de ánimo.", "bonus": 35},
        {"pilar": "RES", "desc": "Realiza esa tarea que has estado procrastinando durante 20 minutos.", "bonus": 50},
        {"pilar": "STR", "desc": "Récord personal: Haz una repetición extra o añade peso en tu ejercicio principal.", "bonus": 45},
    ]
    return random.choice(challenges)

# --- INTERFAZ PRINCIPAL ---
st.title("♟️ Sistema de Monitoreo de Estrategia")
nivel_actual = np.sqrt(sum(data['stats'].values())) / 10
st.markdown(f"**Usuario:** Santos | **Rango:** Nivel {nivel_actual:.2f}")

# Dashboard de Stats
stats = data["stats"]
c1, c2, c3, c4 = st.columns(4)
c1.metric("STR (Físico)", f"{stats['STR']} XP")
c2.metric("INT (Mente)", f"{stats['INT']} XP")
c3.metric("CHA (Social)", f"{stats['CHA']} XP")
c4.metric("RES (Espíritu)", f"{stats['RES']} XP")

st.divider()

# --- REGISTRO Y DESAFÍOS ---
col_reg, col_sora = st.columns(2)

with col_reg:
    st.subheader("📝 Registrar Avance")
    m_type = st.selectbox("Tipo de Misión", ["STR", "INT", "CHA", "RES"])
    xp = st.number_input("XP base", min_value=1, max_value=100, value=10)
    note = st.text_input("Nota del protocolo")
    if st.button("Confirmar Ejecución"):
        data["stats"][m_type] += xp
        data["logs"].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "type": m_type, "xp": xp, "note": note})
        save_data(data)
        st.success("Dato almacenado en el sistema.")
        st.rerun()

with col_sora:
    st.subheader("🎲 Desafío de Los Blancos")
    if 'current_challenge' not in st.session_state:
        st.session_state.current_challenge = None
    
    if st.button("Generar Reto"):
        st.session_state.current_challenge = get_sora_challenge()
    
    if st.session_state.current_challenge:
        c = st.session_state.current_challenge
        st.warning(f"**{c['pilar']}:** {c['desc']}")
        if st.button("✅ ¡Desafío Cumplido!"):
            data["stats"][c["pilar"]] += c["bonus"]
            data["logs"].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "type": c["pilar"], "xp": c["bonus"], "note": f"RETO CUMPLIDO: {c['desc']}"})
            save_data(data)
            st.session_state.current_challenge = None
            st.balloons()
            st.rerun()

# --- ANÁLISIS VISUAL ---
st.sidebar.title("📊 Laboratorio de Datos")
if st.sidebar.checkbox("Mostrar Análisis de Radar"):
    st.write("### Gráfico de Atributos")
    categories = ['STR', 'INT', 'CHA', 'RES']
    values = [data["stats"][c] for c in categories]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='#ff4b4b', alpha=0.3)
    ax.plot(angles, values, color='#ff4b4b', marker='o')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    st.pyplot(fig)

if st.sidebar.checkbox("Ver Historial Log"):
    if not data["logs"]:
        st.info("Aún no hay registros en la base de datos.")
    else:
        st.dataframe(pd.DataFrame(data["logs"]).sort_index(ascending=False))