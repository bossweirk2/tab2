import streamlit as st
from streamlit_drawable_canvas import st_canvas
import random, time

# Lista de retos creativos
retos = [
    "🎭 Dibuja una máscara mágica",
    "🐉 Dibuja un dragón feliz",
    "🌌 Inventa un nuevo planeta",
    "🤖 Dibuja un robot haciendo yoga",
    "🐢 Dibuja una tortuga voladora",
    "🍕 Dibuja la pizza más extraña del mundo",
    "👑 Dibuja la corona de un rey alienígena",
]

st.title("⚡ Reto Creativo con Tiempo")

# Inicializamos variables de sesión
if "reto_actual" not in st.session_state:
    st.session_state.reto_actual = None
if "tiempo_inicio" not in st.session_state:
    st.session_state.tiempo_inicio = None
if "duracion" not in st.session_state:
    st.session_state.duracion = 30  # segundos por defecto

# --- CONFIGURACIÓN DEL RETO ---
col1, col2 = st.columns(2)

with col1:
    duracion = st.slider("⏱️ Duración del reto (segundos)", 10, 120, 30, 5)

with col2:
    if st.button("🎲 Nuevo reto"):
        st.session_state.reto_actual = random.choice(retos)
        st.session_state.tiempo_inicio = time.time()
        st.session_state.duracion = duracion

# Mostrar reto actual
if st.session_state.reto_actual:
    st.subheader(f"👉 Tu reto: {st.session_state.reto_actual}")

    # Calculamos tiempo restante
    tiempo_transcurrido = int(time.time() - st.session_state.tiempo_inicio)
    tiempo_restante = st.session_state.duracion - tiempo_transcurrido

    if tiempo_restante > 0:
        st.markdown(f"⏳ Tiempo restante: **{tiempo_restante} seg**")

        # --- CANVAS SOLO DISPONIBLE SI HAY TIEMPO ---
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=3,
            stroke_color="#FFFFFF",
            background_color="#000000",
            height=400,
            width=500,
            drawing_mode="freedraw",
            key=f"canvas_{tiempo_restante}",
        )
    else:
        st.error("⏰ ¡Se acabó el tiempo! Pasa al siguiente reto 🎉")
