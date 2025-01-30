import streamlit as st
import requests

# Configuración de la API
API_URL = "https://api.kluster.ai/v1/chat/completions"
API_KEY = st.secrets["API_KEY"]

# Función para generar contenido usando la API de Kluster.ai
def generate_content(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "klusterai/Meta-Llama-3.1-405B-Instruct-Turbo",
        "max_completion_tokens": 5000,
        "temperature": 1,
        "top_p": 1,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()  # Lanza una excepción si el código de estado no es 200
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Error al conectar con la API: {e}"
    except KeyError:
        return "Error: La respuesta de la API no contiene los datos esperados."

# Interfaz de Streamlit
st.title("Generador de Tesis y Artículos Académicos")

# Entrada del usuario
area = st.text_input("Ingresa el área científica o filosófica de tu interés:")

if area:
    if st.button("Generar Tesis y Artículo"):
        # Generar tesis
        tesis_prompt = f"Genera una tesis original en el área de {area}."
        tesis = generate_content(tesis_prompt)
        st.subheader("Tesis Generada")
        st.write(tesis)

        # Generar el artículo académico basado en la tesis
        articulo_prompt = f"Desarrolla un artículo académico completo basado en la siguiente tesis: {tesis}. Incluye introducción, metodología, resultados, discusión y conclusión."
        articulo = generate_content(articulo_prompt)
        st.subheader("Artículo Académico Generado")
        st.write(articulo)
