import streamlit as st
import requests
import os
import re

# Configuración de la API de Kluster.ai (como antes)
API_URL = "https://api.kluster.ai/v1/chat/completions"
API_KEY = st.secrets["API_KEY"]

# Configuración de la API de Exa.ai
EXA_API_URL = "https://api.exa.ai/search"
EXA_API_KEY = st.secrets["EXA_API_KEY"]  # Asegúrate de agregar tu API key en Streamlit Secrets

# Función para generar contenido usando la API de Kluster.ai con manejo de errores
def generate_content(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "klusterai/Meta-Llama-3.1-405B-Instruct-Turbo",
        "max_completion_tokens": 1500,  # Ajustado para optimizar uso de tokens
        "temperature": 0.7,  # Ajustado para respuestas más coherentes
        "top_p": 0.9,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as http_err:
        return f"Error HTTP: {http_err}"
    except requests.exceptions.ConnectionError:
        return "Error de conexión. Por favor, verifica tu conexión a internet."
    except requests.exceptions.Timeout:
        return "La solicitud a la API ha excedido el tiempo de espera."
    except requests.exceptions.RequestException as err:
        return f"Ocurrió un error: {err}"
    except KeyError:
        return "Respuesta inesperada de la API."

# Función para citar research papers usando la API de Exa.ai
def citar_research_papers(query):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": EXA_API_KEY
    }
    payload = {
        "query": query,
        "type": "neural",
        "category": "research paper",
        "useAutoprompt": True
    }
    
    try:
        response = requests.post(EXA_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        resultados = response.json()
        return resultados
    except requests.exceptions.HTTPError as http_err:
        st.error(f"Error HTTP: {http_err}")
    except requests.exceptions.ConnectionError:
        st.error("Error de conexión. Por favor, verifica tu conexión a internet.")
    except requests.exceptions.Timeout:
        st.error("La solicitud ha excedido el tiempo de espera.")
    except requests.exceptions.RequestException as err:
        st.error(f"Ocurrió un error: {err}")
    except KeyError:
        st.error("Respuesta inesperada de la API.")
    return None

# Función cacheada para optimizar solicitudes
@st.cache_data(show_spinner=False)
def generate_content_cached(prompt):
    return generate_content(prompt)

@st.cache_data(show_spinner=False)
def citar_research_papers_cached(query):
    return citar_research_papers(query)

# Interfaz de Streamlit
st.title("Generador de Tesis y Artículos Académicos")

# Entrada del usuario
area = st.text_input("Ingresa el área científica o filosófica de tu interés:").strip()

if area:
    if len(area) < 3:
        st.warning("Por favor, ingresa un área de al menos 3 caracteres.")
    else:
        if st.button("Generar Tesis y Artículo"):
            # Generar tesis
            tesis_prompt = f"Genera una tesis original en el área de {area}."
            with st.spinner("Generando tesis..."):
                tesis = generate_content_cached(tesis_prompt)
            st.subheader("Tesis Generada")
            st.write(tesis)
        
            # Generar plan de desarrollo
            plan_prompt = f"Genera un plan para desarrollar la siguiente tesis: {tesis}"
            with st.spinner("Generando plan de desarrollo..."):
                plan = generate_content_cached(plan_prompt)
            st.subheader("Plan de Desarrollo")
            st.write(plan)
        
            # Generar apartados del artículo académico
            apartados_prompt = f"Genera los apartados que contendrá un artículo académico que desarrolle la siguiente tesis: {tesis}"
            with st.spinner("Generando apartados del artículo académico..."):
                apartados = generate_content_cached(apartados_prompt)
            st.subheader("Apartados del Artículo Académico")
            st.write(apartados)
        
            # Parsear los apartados
            apartados_list = re.split(r'\d+\.\s+', apartados)
            apartados_list = [apartado.strip() for apartado in apartados_list if apartado.strip()]
        
            # Escribir cada apartado
            st.subheader("Desarrollo de los Apartados")
            for apartado in apartados_list:
                if apartado:
                    st.markdown(f"**{apartado}**")
                    contenido_apartado = generate_content_cached(f"Escribe el contenido del apartado: {apartado} para la tesis: {tesis}")
                    st.write(contenido_apartado)

        st.markdown("---")
        st.header("Buscar y Citar Artículos de Investigación")
        
        # Entrada para la búsqueda de artículos
        query = st.text_input("Ingresa una consulta para buscar artículos de investigación:").strip()
        
        if query:
            if st.button("Buscar Artículos"):
                with st.spinner("Buscando artículos de investigación..."):
                    resultados = citar_research_papers_cached(query)
                if resultados:
                    st.subheader("Artículos Encontrados")
                    for idx, articulo in enumerate(resultados.get("results", []), 1):
                        titulo = articulo.get("title", "Sin título")
                        autores = articulo.get("authors", "Autores no disponibles")
                        resumen = articulo.get("abstract", "Resumen no disponible")
                        url = articulo.get("url", "#")
                        
                        st.markdown(f"### {idx}. {titulo}")
                        st.markdown(f"**Autores:** {autores}")
                        st.markdown(f"**Resumen:** {resumen}")
                        st.markdown(f"[Leer más]({url})")
                        st.markdown("---")
