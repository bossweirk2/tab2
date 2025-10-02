import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

Expert=" "
profile_imgenh=" "

# Inicializar session_state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""
if 'base64_image' not in st.session_state:
    st.session_state.base64_image = ""

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Configuración de página
st.set_page_config(page_title='Tablero Inteligente')
st.title('🖌️ Tablero Inteligente')

# Barra lateral
with st.sidebar:
    st.subheader("⚙️ Propiedades del Tablero")

    # Dimensiones del canvas
    canvas_width = st.slider("Ancho del tablero", 300, 700, 400, 50)
    canvas_height = st.slider("Alto del tablero", 200, 600, 300, 50)

    # Modo de dibujo
    drawing_mode = st.selectbox(
        "Herramienta de Dibujo:",
        ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"),
    )

    # Grosor de línea
    stroke_width = st.slider('Selecciona el ancho de línea', 1, 30, 5)

    # Color del trazo
    stroke_color = st.color_picker("Color de trazo", "#000000")

    # Color de fondo
    bg_color = st.color_picker("Color de fondo", "#FFFFFF")

st.subheader("✏️ Dibuja el boceto en el panel y presiona el botón para analizarlo")

# Canvas dinámico
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=canvas_height,
    width=canvas_width,
    drawing_mode=drawing_mode,
    key=f"canvas_{canvas_width}_{canvas_height}",  # clave dinámica
)

# API Key
ke = st.text_input('🔑 Ingresa tu Clave de OpenAI', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

# Inicializar cliente
if api_key:
    client = OpenAI(api_key=api_key)

analyze_button = st.button("🔍 Analiza la imagen", type="secondary")

# Analizar imagen
if canvas_result.image_data is not None and api_key and analyze_button:
    with st.spinner("Analizando ..."):
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
        input_image.save('img.png')

        # Codificar en base64
        base64_image = encode_image_to_base64("img.png")
        st.session_state.base64_image = base64_image

        prompt_text = "Describe en español brevemente el dibujo"

        try:
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )

            full_response = response.choices[0].message.content or "No se obtuvo descripción"
            message_placeholder.markdown(full_response)

            st.session_state.full_response = full_response
            st.session_state.analysis_done = True

            if Expert == profile_imgenh:
                st.session_state.mi_respuesta = response.choices[0].message.content

        except Exception as e:
            st.error(f"❌ Ocurrió un error: {e}")

# Crear historia infantil a partir del análisis
if st.session_state.analysis_done:
    st.divider()
    st.subheader("📚 ¿Quieres crear una historia?")
    
    if st.button("✨ Crear historia infantil"):
        with st.spinner("Creando historia..."):
            story_prompt = f"Basándote en esta descripción: '{st.session_state.full_response}', crea una historia infantil breve y entretenida. La historia debe ser creativa y apropiada para niños."
            
            story_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": story_prompt}],
                max_tokens=500,
            )
            
            st.markdown("**📖 Tu historia:**")
            st.write(story_response.choices[0].message.content)

# Advertencia si falta API Key
if not api_key:
    st.warning("⚠️ Por favor ingresa tu API key de OpenAI.")
