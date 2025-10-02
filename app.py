import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import base64
import openai
import os

# --- Funciones auxiliares ---
def encode_image_to_base64(image):
    """Convierte una imagen PIL a base64."""
    from io import BytesIO
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def describir_dibujo(base64_img, api_key):
    """Usa la IA para describir el dibujo."""
    client = openai.OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe este dibujo de forma breve y artística en español."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_img}"},
                        },
                    ],
                }
            ],
            max_tokens=80,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"(Error al describir: {e})"


# --- Configuración inicial ---
st.set_page_config(page_title="🎨 Galería Instantánea")
st.title("🎨 Galería Instantánea con IA")

if "galeria" not in st.session_state:
    st.session_state.galeria = []  # lista de (imagen, descripción)


# --- Sidebar de opciones ---
with st.sidebar:
    st.subheader("Opciones del Tablero")
    canvas_width = st.slider("Ancho", 300, 700, 500, 50)
    canvas_height = st.slider("Alto", 200, 600, 300, 50)
    stroke_width = st.slider("Ancho del trazo", 1, 30, 5)
    stroke_color = st.color_picker("Color de trazo", "#FFFFFF")
    bg_color = st.color_picker("Color de fondo", "#000000")

# --- Canvas de dibujo ---
canvas_result = st_canvas(
    fill_color="rgba(255,165,0,0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=canvas_height,
    width=canvas_width,
    drawing_mode="freedraw",
    key="canvas"
)

# --- Ingreso de API Key ---
api_key = st.text_input("🔑 Ingresa tu API Key de OpenAI", type="password")

# --- Botón para guardar dibujo ---
if st.button("💾 Guardar en galería") and canvas_result.image_data is not None:
    if not api_key:
        st.warning("Necesitas ingresar tu API Key de OpenAI.")
    else:
        # Convertimos el dibujo en imagen
        img_array = np.array(canvas_result.image_data)
        img_pil = Image.fromarray(img_array.astype("uint8"), "RGBA")
        
        # Lo pasamos a base64
        base64_img = encode_image_to_base64(img_pil)
        
        # Obtenemos descripción de la IA
        descripcion = describir_dibujo(base64_img, api_key)
        
        # Guardamos en galería
        st.session_state.galeria.append((img_pil, descripcion))
        st.success("✅ Dibujo guardado en la galería")


# --- Mostrar galería ---
if st.session_state.galeria:
    st.subheader("🖼️ Mi Galería")
    for i, (img, desc) in enumerate(st.session_state.galeria):
        st.image(img, caption=f"Obra {i+1}: {desc}", use_container_width=True)
