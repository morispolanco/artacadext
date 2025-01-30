import streamlit as st
import requests
import os
import re

# Configuración de las APIs
KLUSTER_API_URL = "https://api.kluster.ai/v1/chat/completions"
KLUSTER_API_KEY = st.secrets["KLUSTER_API_KEY"]

EXA_API_URL = "https://api.exa.ai/search"
EXA_API_KEY = st.secrets["EXA_API_KEY"]

# Función para generar contenido usando la API de Kluster.ai con manejo de errores
def generate_content(prompt):
    headers = {
        "Authorization": f"Bearer {KLUSTER_API_KEY}",
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
        response = requests.post(KLUSTER_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as http_err:
        st.error(f"Error HTTP: {http_err}")
    except requests.exceptions.ConnectionError:
        st.error("Error de conexión. Por favor, verifica tu conexión a internet.")
    except requests.exceptions.Timeout:
        st.error("La solicitud a la API ha excedido el tiempo de espera.")
    except requests.exceptions.RequestException as err:
        st.error(f"Ocurrió un error: {err}")
    except KeyError:
        st.error("Respuesta inesperada de la API.")
    return None

# Función para buscar research papers usando la API de Exa.ai
def search_research_papers(query):
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
        response = requests.post(EXA_API_URL, headers=headers, json=payload, timeout=60)
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

# Funciones cacheadas para optimizar solicitudes a Kluster.ai
@st.cache_data(show_spinner=False)
def generate_content_cached(prompt):
    return generate_content(prompt)

# Función cacheada para optimizar solicitudes a Exa.ai
@st.cache_data(show_spinner=False)
def search_research_papers_cached(query):
    return search_research_papers(query)

# Función para formatear las citas en el texto
def format_citations(citations):
    """
    Formatea las citas obtenidas de Exa.ai para incluirlas en el contenido.
    """
    if citations and "results" in citations and citations["results"]:
        referencias = "\n\n## Referencias\n"
        for idx, cita in enumerate(citations["results"], 1):
            titulo = cita.get("title", "Sin título")
            autores = cita.get("authors", "Autores no disponibles")
            año = cita.get("year", "Año no disponible")
            url = cita.get("url", "#")
            resumen = cita.get("abstract", "Resumen no disponible")
            referencias += f"{idx}. **{titulo}**. {autores} ({año}). [Leer más]({url})\n"
        return referencias
    return ""

# Función para insertar citas en el contenido
def insert_citations(contenido, citas):
    """
    Inserta las citas al final del contenido.
    """
    referencias = format_citations(citas)
    if referencias:
        contenido += referencias
    return contenido

# Función principal para generar el artículo con citas
def generar_articulo(area):
    # Paso 1: Generar tesis
    tesis_prompt = f"Genera una tesis original en el área de {area}."
    tesis = generate_content_cached(tesis_prompt)
    if not tesis:
        st.error("No se pudo generar la tesis.")
        return
    st.subheader("1. Tesis Generada")
    st.write(tesis)

    # Buscar citas para la tesis
    st.info("Buscando citas relevantes para la tesis...")
    citas_tesis = search_research_papers_cached(tesis)
    tesis_con_citas = insert_citations(tesis, citas_tesis)
    st.markdown("**Tesis con Citas:**")
    st.write(tesis_con_citas)

    # Paso 2: Generar plan de desarrollo
    plan_prompt = f"Genera un plan detallado para desarrollar la siguiente tesis: {tesis}."
    plan = generate_content_cached(plan_prompt)
    if not plan:
        st.error("No se pudo generar el plan de desarrollo.")
        return
    st.subheader("2. Plan de Desarrollo")
    st.write(plan)

    # Buscar citas para el plan
    st.info("Buscando citas relevantes para el plan de desarrollo...")
    citas_plan = search_research_papers_cached(plan)
    plan_con_citas = insert_citations(plan, citas_plan)
    st.markdown("**Plan de Desarrollo con Citas:**")
    st.write(plan_con_citas)

    # Paso 3: Generar apartados del artículo académico
    apartados_prompt = f"Genera una lista de apartados que contendrá un artículo académico que desarrolle la siguiente tesis: {tesis}."
    apartados = generate_content_cached(apartados_prompt)
    if not apartados:
        st.error("No se pudieron generar los apartados del artículo académico.")
        return
    st.subheader("3. Apartados del Artículo Académico")
    st.write(apartados)

    # Parsear los apartados
    apartados_list = re.split(r'\d+\.\s+', apartados)
    apartados_list = [apartado.strip() for apartado in apartados_list if apartado.strip()]

    # Paso 4: Escribir cada apartado con citas
    st.subheader("4. Desarrollo de los Apartados con Citas")
    for apartado in apartados_list:
        st.markdown(f"### **{apartado}**")

        # Generar contenido del apartado
        contenido_prompt = f"Escribe el contenido del apartado '{apartado}' para la tesis: {tesis}. Asegúrate de citar fuentes relevantes y proporciona referencias al final."
        contenido = generate_content_cached(contenido_prompt)
        if not contenido:
            st.error(f"No se pudo generar el contenido para el apartado: {apartado}")
            continue

        # Buscar citas para el apartado
        st.info(f"Buscando citas relevantes para el apartado: {apartado}...")
        palabras_clave = f"{area}, {apartado}"
        citas_apartado = search_research_papers_cached(palabras_clave)

        # Insertar citas en el contenido
        contenido_con_citas = insert_citations(contenido, citas_apartado)
        st.write(contenido_con_citas)

# Interfaz de Streamlit
st.set_page_config(page_title="Generador de Tesis y Artículos Académicos", layout="wide")
st.title("Generador de Tesis y Artículos Académicos")

# Entrada del usuario
area = st.text_input("Ingresa el área científica o filosófica de tu interés:").strip()

if area:
    if len(area) < 3:
        st.warning("Por favor, ingresa un área de al menos 3 caracteres.")
    else:
        if st.button("Generar Tesis y Artículo"):
            with st.spinner("Generando contenido..."):
                generar_articulo(area)
