from data_model import data_to_csv, data_from_csv
from metadata import read_files
import psycopg2
from psycopg2 import extras

def push_metadata(args):
    files = read_files(args["dir"])
    try:
        with psycopg2.connect(f"postgres://denodo_user:denodo_password@{args["host"]}:{args["port"]}/my_database")as conn:
            with conn.cursor() as cur:
                query = "delete from files;"
                cur.execute(query)

                query = "insert into files(name, contents, creation_date, extra) values %s;"
                extras.execute_values(cur, query, [(f.name, f.contents, f.creation_date, f.extra) for f in files])

                print("updated database")

    except psycopg2.Error as e:
        print(f"A psycopg2 error occurred: {e}")

def send_query(args):
    pass

