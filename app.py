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
        # Iniciamos con tus datos actuales
        return {
            "stats": {"STR": 0, "INT": 0, "CHA": 0, "RES": 0},
            "peso_historial": [{"fecha": datetime.now().strftime("%Y-%m-%d"), "peso": 62.0}],
            "rutinas": {dia: "" for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]},
            "consumo_proteina": []
        }

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f)

data = load_data()

# --- CÁLCULO DE METAS DINÁMICAS ---
# El sistema ahora toma el último peso registrado para calcular la meta
peso_actual = data["peso_historial"][-1]["peso"]
meta_proteina = round(peso_actual * 2.0, 1) 

# --- INTERFAZ ---
st.title("♟️ Sistema de Monitoreo de Estrategia v1.6")

tabs = st.tabs(["🏋️ Rutinas y Gym", "🥩 Nutrición y Alertas", "📊 Progreso Físico"])

# --- TAB 1: RUTINAS SEMANALES ---
with tabs[0]:
    st.header("📋 Plan de Entrenamiento")
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
                st.info(f"**{d}:** {data['rutinas'][d]}")

# --- TAB 2: NUTRICIÓN Y ALERTAS ---
with tabs[1]:
    st.header("🥩 Seguimiento de Nutrición")
    
    col_calc, col_log = st.columns(2)
    
    with col_calc:
        st.subheader("Registro de Ingesta")
        # Alerta visual de meta
        st.metric("Tu Meta de Proteína", f"{meta_proteina}g", delta=f"Basado en tus {peso_actual}kg")
        
        alimento = st.text_input("Alimento (ej: Batido, Pollo, Tacos)")
        gramos_pro = st.number_input("Gramos de proteína:", 0, 100, 25)
        hora_consumo = st.time_input("Hora del consumo", datetime.now())
        
        if st.button("Registrar Consumo"):
            nuevo_log = {
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "hora": hora_consumo.strftime("%H:%M"),
                "alimento": alimento,
                "gramos": gramos_pro
            }
            data["consumo_proteina"].append(nuevo_log)
            save_data(data)
            st.success("Proteína registrada.")

    with col_log:
        st.subheader("Estado de Hoy")
        hoy = datetime.now().strftime("%Y-%m-%d")
        logs_hoy = [c for c in data["consumo_proteina"] if c["fecha"] == hoy]
        total_hoy = sum(log["gramos"] for log in logs_hoy)
        
        # Lógica de Alertas
        if total_hoy < meta_proteina * 0.5:
            st.error(f"⚠️ Alerta: Estás muy bajo en proteína ({total_hoy}g). ¡Necesitas comer!")
        elif total_hoy < meta_proteina:
            st.warning(f"⚡ Casi llegas: Te faltan {round(meta_proteina - total_hoy, 1)}g para tu meta.")
        else:
            st.success(f"🏆 ¡Meta cumplida! Has consumido {total_hoy}g. Hipertrofia asegurada.")
            st.balloons()
            
        if logs_hoy:
            st.table(pd.DataFrame(logs_hoy)[["hora", "alimento", "gramos"]])

# --- TAB 3: PROGRESO ---
with tabs[2]:
    st.subheader("📈 Evolución de Masa Muscular")
    
    # Permitir actualizar peso rápido
    nuevo_peso = st.number_input("Registrar nuevo peso (kg):", 40.0, 120.0, float(peso_actual))
    if st.button("Actualizar Historial de Peso"):
        data["peso_historial"].append({"fecha": datetime.now().strftime("%Y-%m-%d"), "peso": nuevo_peso})
        save_data(data)
        st.rerun()

    df_peso = pd.DataFrame(data["peso_historial"])
    fig_peso, ax_peso = plt.subplots(figsize=(10, 4))
    ax_peso.plot(df_peso["fecha"], df_peso["peso"], marker='o', color='#00ff41', linewidth=2)
    ax_peso.set_ylabel("Peso (kg)")
    st.pyplot(fig_peso)
