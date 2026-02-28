
import requests
from requests.auth import HTTPBasicAuth
from metadata import read_files
import psycopg2
from psycopg2 import extras

AI_SDK_URL = "http://localhost:8008"
AUTH = HTTPBasicAuth("admin", "admin")

METADATA_PARAMS = {
    "vdp_database_names": "admin",
    "vdp_tag_names": "",
    "tags_to_ignore": "",
    "embeddings_provider": "googleaistudio",
    "embeddings_model": "gemini-embedding-001",
    "embeddings_token_limit": 0,
    "vector_store_provider": "chroma",
    "rate_limit_rpm": 0,
    "examples_per_table": 100,
    "view_descriptions": True,
    "column_descriptions": True,
    "associations": True,
    "view_prefix_filter": "",
    "view_suffix_filter": "",
    "insert": True,
    "views_per_request": 50,
    "incremental": True,
    "parallel": True
}

QUESTION_BODY = {
    "plot": False,
    "plot_details": "",
    "embeddings_provider": "googleaistudio",
    "embeddings_model": "gemini-embedding-001",
    "vector_store_provider": "chroma",
    "llm_provider": "googleaistudio",
    "llm_model": "gemma-3-27b-it",
    "llm_temperature": 0,
    "llm_max_tokens": 4096,
    "vdp_database_names": "admin",
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
    "verbose": True,
}

def push_metadata(args):
    files = read_files(args["dir"])
    try:
        with psycopg2.connect(f"postgres://denodo_user:denodo_password@{args['host']}:{args['port']}/my_database") as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM files;")
                extras.execute_values(
                    cur,
                    "INSERT INTO files(name, contents, creation_date, extra) VALUES %s;",
                    [(f.name, f.contents, f.creation_date, f.extra) for f in files],
                )
        print("updated database")
    except psycopg2.Error as e:
        print(f"A psycopg2 error occurred: {e}")


def _build_question(args: dict) -> str:
    parts = []

    if args.get("startDate") and args.get("endDate"):
        parts.append(f"creados entre {args['startDate']} y {args['endDate']}")
    elif args.get("startDate"):
        parts.append(f"creados a partir del {args['startDate']}")
    elif args.get("endDate"):
        parts.append(f"creados antes del {args['endDate']}")

    if args.get("usersMentioned"):
        users = ", ".join(args["usersMentioned"])
        parts.append(f"que mencionen a {users}")

    if args.get("reunionResult"):
        parts.append(f"con resultado '{args['reunionResult']}'")

    if parts:
        return "Dame los documentos " + " y ".join(parts)
    else:
        return "Dime qué tablas hay disponibles y para qué sirve cada una"

def send_query(args: dict):
    question = _build_question(args)
    print(f"Enviando pregunta: {question}...")

    try:
        getMetadata = requests.get(
            f"{AI_SDK_URL}/getMetadata/",
            params=METADATA_PARAMS,
            auth=AUTH,
        )
        getMetadata.raise_for_status()

        # ── Step 2: answerMetadataQuestion ─────────────────────────────────────
        r_meta = requests.post(
            f"{AI_SDK_URL}/answerMetadataQuestion/",
            json={**QUESTION_BODY, "question": question},
            auth=AUTH,
        )
        r_meta.raise_for_status()
        meta = r_meta.json()

        print("\nMETADATA ANSWER:")
        print(meta.get("answer", ""))

        r_data = requests.post(
            f"{AI_SDK_URL}/answerDataQuestion/",
            json={
                **QUESTION_BODY,
                "question": question,
                "check_ambiguity": True,
                "vql_execute_rows_limit": 100,
                "llm_response_rows_limit": 15,
            },
            auth=AUTH,
        )

        # Mostrar el error completo del servidor antes de raise_for_status
        if not r_data.ok:
            print(f"\nERROR {r_data.status_code} en answerDataQuestion:")
            try:
                err_body = r_data.json()
                print(f"  detail:  {err_body.get('detail', '')}")
                print(f"  message: {err_body.get('message', '')}")
                print(f"  error:   {err_body.get('error', '')}")
                print(f"  raw:     {err_body}")
            except Exception:
                print(f"  raw text: {r_data.text[:500]}")
            return None

        data = r_data.json()

        print("\nDATA ANSWER:")
        print("-" * 50)
        print(data.get("answer", ""))
        if data.get("vql"):
            print(f"\nVQL: {data['vql']}")
        print("-" * 50)

        return {
            "metadata_answer": meta.get("answer"),
            "data_answer":     data.get("answer"),
            "vql":             data.get("vql"),
        }

    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 401:
            print("\nERROR 401: No autorizado.")
        else:
            print(f"\nERROR HTTP {err.response.status_code}: {err.response.text[:500]}")
    except Exception as e:
        print(f"\nERROR INESPERADO: {e}")
