import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime

# --- CONFIGURACIÓN Y DATOS ---
st.set_page_config(page_title="SME - High Performance", page_icon="♟️", layout="wide")

def load_data():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "stats": {"STR": 0, "INT": 0, "CHA": 0, "RES": 0},
            "peso_historial": [{"fecha": "2026-03-08", "peso": 55.0}],
            "rutinas": {dia: "" for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]},
            "consumo_proteina": []
        }

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f)

data = load_data()

# --- CÁLCULO DE METAS (Basado en tus 1.85m y 55kg) ---
peso_actual = data["peso_historial"][-1]["peso"]
meta_proteina = round(peso_actual * 2.0, 1) # Meta estándar para ganar masa: 2g por kilo

# --- INTERFAZ ---
st.title("♟️ Sistema de Monitoreo de Estrategia v1.5")

tabs = st.tabs(["🏋️ Rutinas y Gym", "🥩 Nutrición y Macros", "📊 Progreso General"])

# --- TAB 1: RUTINAS SEMANALES ---
with tabs[0]:
    st.header("📋 Plan de Entrenamiento Semanal")
    col1, col2 = st.columns(2)
    
    dias = list(data["rutinas"].keys())
    with col1:
        dia_sel = st.selectbox("Selecciona el día para editar rutina:", dias)
        nueva_rutina = st.text_area(f"Rutina para el {dia_sel}:", data["rutinas"].get(dia_sel, ""))
        if st.button("Guardar Rutina"):
            data["rutinas"][dia_sel] = nueva_rutina
            save_data(data)
            st.success(f"Rutina de {dia_sel} actualizada.")

    with col2:
        st.subheader("Tu semana de un vistazo")
        for d in dias:
            if data["rutinas"][d]:
                st.write(f"**{d}:** {data['rutinas'][d]}")

# --- TAB 2: CALCULADORA Y REGISTRO DE PROTEÍNAS ---
with tabs[1]:
    st.header("🥩 Seguimiento de Nutrición")
    
    col_calc, col_log = st.columns(2)
    
    with col_calc:
        st.subheader("Calculadora de Ingesta")
        st.metric("Tu Meta Diaria de Proteína", f"{meta_proteina}g", delta="Para ganar masa")
        
        alimento = st.text_input("Alimento (ej: Pechuga de pollo, Batido)")
        gramos_pro = st.number_input("Gramos de proteína en esta comida:", 0, 100, 25)
        hora_consumo = st.time_input("¿A qué hora lo consumiste?", datetime.now())
        
        if st.button("Registrar Consumo"):
            nuevo_log = {
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "hora": hora_consumo.strftime("%H:%M"),
                "alimento": alimento,
                "gramos": gramos_pro
            }
            data["consumo_proteina"].append(nuevo_log)
            save_data(data)
            st.success("Proteína registrada en el sistema.")

    with col_log:
        st.subheader("Consumo de Hoy")
        hoy = datetime.now().strftime("%Y-%m-%d")
        df_hoy = pd.DataFrame([c for c in data["consumo_proteina"] if c["fecha"] == hoy])
        
        if not df_hoy.empty:
            st.table(df_hoy[["hora", "alimento", "gramos"]])
            total_hoy = df_hoy["gramos"].sum()
            progreso = total_hoy / meta_proteina
            st.progress(min(progreso, 1.0))
            st.write(f"Total hoy: {total_hoy}g / {meta_proteina}g")
        else:
            st.info("Aún no has registrado proteínas hoy.")

# --- TAB 3: PROGRESO ---
with tabs[2]:
    st.subheader("📈 Evolución Física")
    df_peso = pd.DataFrame(data["peso_historial"])
    fig_peso, ax_peso = plt.subplots(figsize=(10, 4))
    ax_peso.plot(df_peso["fecha"], df_peso["peso"], marker='o', color='#00ff41')
    ax_peso.set_title("Progreso de Peso (Meta: Ganar Masa)")
    st.pyplot(fig_peso)
