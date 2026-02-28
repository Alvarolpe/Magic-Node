import requests
from requests.auth import HTTPBasicAuth

#Primero getMetadata -> Pasarle la base de datos donde están las cosas 
#Segundo MetadataAnswer -> Aprende de una tabla específica
#Tercero DataAnswer -> Responde en base a lo que le has preguntado y la tabla
URL = "http://localhost:8008/answerMetadataQuestion/"
PREGUNTA = "Dime qué tablas hay disponibles y para qué sirve cada una"

payload = {
  "question": PREGUNTA,
  "plot": False,
  "plot_details": "",
  "embeddings_provider": "googleaistudio",
  "embeddings_model": "gemini-embedding-001",
  "vector_store_provider": "chroma",
  "llm_provider": "googleaistudio",
  "llm_model": "gemma-3-27b-it",
  "llm_temperature": 0,
  "llm_max_tokens": 4096,
  "vdp_database_names": "",
  "vdp_tag_names": "",
  "allow_external_associations": False,
  "use_views": "",
  "expand_set_views": True,
  "custom_instructions": "",
  "markdown_response": True,
  "vector_search_k": 5,
  "vector_search_sample_data_k": 3,
  "vector_search_total_limit": 20,
  "vector_search_column_description_char_limit": 200,
  "disclaimer": True,
  "verbose": True
}

try:
    print(f"Enviando pregunta: {PREGUNTA}...")

    response = requests.post(
        URL,
        json=payload,
        auth=HTTPBasicAuth("admin", "admin")
    )

    response.raise_for_status()

    resultado = response.json()

    print("\nRESPUESTA:")
    print("-----------------------")
    print(resultado.get("answer"))
    print("-----------------------")

except requests.exceptions.HTTPError as err:
    if err.response.status_code == 401:
        print("\nERROR 401: No autorizado.")
    else:
        print(f"\nERROR HTTP: {err}")
except Exception as e:
    print(f"\nERROR INESPERADO: {e}")