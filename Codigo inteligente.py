import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# Inicializar session_state
if 'descriptions' not in st.session_state:
    st.session_state.descriptions = []   # Lista para acumular descripciones
if 'story_done' not in st.session_state:
    st.session_state.story_done = False

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Configuración
st.set_page_config(page_title='Tablero Colaborativo')
st.title('🖌️ Tablero Colaborativo de Historias')

# Barra lateral
with st.sidebar:
    st.subheader("⚙️ Propiedades del Tablero")
    canvas_width = st.slider("Ancho del tablero", 300, 700, 400, 50)
    canvas_height = st.slider("Alto del tablero", 200, 600, 300, 50)
    drawing_mode = st.selectbox("Herramienta de Dibujo:",
        ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"))
    stroke_width = st.slider('Selecciona el ancho de línea', 1, 30, 5)
    stroke_color = st.color_picker("Color de trazo", "#000000")
    bg_color = st.color_picker("Color de fondo", "#FFFFFF")

st.subheader("✏️ Dibuja algo, analízalo y aporta a la historia colaborativa")

# Canvas
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=canvas_height,
    width=canvas_width,
    drawing_mode=drawing_mode,
    key=f"canvas_{canvas_width}_{canvas_height}",
)

# API Key
ke = st.text_input('🔑 Ingresa tu Clave de OpenAI', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

if api_key:
    client = OpenAI(api_key=api_key)

# Botones
analyze_button = st.button("➕ Añadir mi dibujo a la historia")
story_button = st.button("📖 Generar historia completa")

# Paso 1: Analizar cada dibujo
if canvas_result.image_data is not None and api_key and analyze_button:
    input_numpy_array = np.array(canvas_result.image_data)
    input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
    input_image.save('img.png')

    base64_image = encode_image_to_base64("img.png")

    prompt_text = "Describe en español brevemente este dibujo en máximo 2 frases."

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url",
                         "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                    ],
                }
            ],
            max_tokens=200,
        )

        description = response.choices[0].message.content or "Descripción no generada"
        st.session_state.descriptions.append(description)
        st.success(f"✅ Tu aporte se añadió a la historia: {description}")

    except Exception as e:
        st.error(f"❌ Error: {e}")

# Paso 2: Generar historia colaborativa con todos los aportes
if story_button and st.session_state.descriptions:
    with st.spinner("Creando historia colectiva..."):
        story_prompt = (
            "Crea una historia creativa y entretenida para niños "
            "usando las siguientes descripciones de dibujos, en el orden dado: "
            + " | ".join(st.session_state.descriptions)
        )

        story_response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": story_prompt}],
            max_tokens=600,
        )

        st.subheader("📖 Historia Colaborativa:")
        st.write(story_response.choices[0].message.content)
        st.session_state.story_done = True

# Mostrar aportes acumulados
if st.session_state.descriptions:
    st.divider()
    st.subheader("📝 Aportes acumulados:")
    for i, desc in enumerate(st.session_state.descriptions, 1):
        st.write(f"{i}. {desc}")

# Advertencia si no hay clave
if not api_key:
    st.warning("⚠️ Por favor ingresa tu API key de OpenAI.")
