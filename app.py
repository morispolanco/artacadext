import streamlit as st
import requests
import os

# Configuración de las APIs
KLUSTER_API_URL = "https://api.kluster.ai/v1/chat/completions"
KLUSTER_API_KEY = st.secrets["KLUSTER_API_KEY"]

EXA_API_URL = "https://api.exa.ai/search"
EXA_API_KEY = st.secrets["EXA_API_KEY"]

# Función para generar contenido usando la API de Kluster.ai
def generate_kluster_content(prompt):
    headers = {
        "Authorization": f"Bearer {KLUSTER_API_KEY}",
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
    response = requests.post(KLUSTER_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}, {response.text}"

# Función para buscar research papers usando la API de Exa.ai
def search_exa_papers(query):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": EXA_API_KEY
    }
    data = {
        "query": query,
        "type": "neural",
        "category": "research paper",
        "useAutoprompt": True
    }
    response = requests.post(EXA_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        return f"Error: {response.status_code}, {response.text}"

# Interfaz de Streamlit
st.title("Generador de Tesis y Búsqueda de Research Papers")

# Campo de entrada único
area = st.text_input("Ingresa el área científica o filosófica de tu interés:")

if area:
    # Generar tesis con Kluster.ai
    st.subheader("Tesis Generada")
    tesis_prompt = f"Genera una tesis original en el área de {area}."
    tesis = generate_kluster_content(tesis_prompt)
    st.write(tesis)

    # Generar plan de desarrollo con Kluster.ai
    st.subheader("Plan de Desarrollo")
    plan_prompt = f"Genera un plan para desarrollar la siguiente tesis: {tesis}"
    plan = generate_kluster_content(plan_prompt)
    st.write(plan)

    # Buscar research papers con Exa.ai
    st.subheader("Research Papers Relacionados")
    papers = search_exa_papers(area)
    if isinstance(papers, list):
        for paper in papers:
            title = paper.get("title", "Sin título")
            authors = ", ".join(paper.get("authors", ["Autor desconocido"]))
            url = paper.get("url", "#")
            date = paper.get("publication_date", "Fecha desconocida")
            # Formatear la cita en estilo APA
            citation = f"{authors} ({date}). {title}. Recuperado de {url}"
            st.write(citation)
    else:
        st.error(papers)  # Mostrar error si la búsqueda falla
