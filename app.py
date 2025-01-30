import streamlit as st
import requests

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

# Función para buscar artículos académicos usando la API de Exa.ai
def search_exa_papers(query):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": EXA_API_KEY
    }
    data = {
        "query": query,
        "category": "research paper"
    }
    response = requests.post(EXA_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        return f"Error: {response.status_code}, {response.text}"

# Función para formatear citas en estilo APA
def format_apa_citation(paper):
    authors = ", ".join(paper.get("authors", ["Autor desconocido"]))
    date = paper.get("publication_date", "Fecha desconocida")
    title = paper.get("title", "Sin título")
    url = paper.get("url", "#")
    return f"{authors} ({date}). {title}. Recuperado de {url}"

# Interfaz de Streamlit
st.title("Generador de Artículos Académicos con Citas")

# Campo de entrada único
area = st.text_input("Ingresa el área científica o filosófica de tu interés:")

if area:
    # Buscar artículos académicos con Exa.ai
    st.subheader("Artículos Académicos Relacionados")
    papers = search_exa_papers(area)
    if isinstance(papers, list):
        # Mostrar las citas de los papers
        st.write("**Papers encontrados:**")
        for i, paper in enumerate(papers):
            st.write(f"{i + 1}. {format_apa_citation(paper)}")

        # Generar un artículo académico con Kluster.ai utilizando los papers como fuentes
        st.subheader("Artículo Académico Generado")
        papers_context = "\n".join([f"Paper {i + 1}: {format_apa_citation(paper)}" for i, paper in enumerate(papers)])
        article_prompt = (
            f"Escribe un artículo académico sobre '{area}' utilizando los siguientes papers como fuentes:\n"
            f"{papers_context}\n\n"
            "El artículo debe incluir una introducción, un marco teórico, una metodología, resultados, discusión y conclusiones. "
            "Cita los papers en formato APA dentro del texto."
        )
        article = generate_kluster_content(article_prompt)
        st.write(article)
    else:
        st.error(papers)  # Mostrar error si la búsqueda falla
