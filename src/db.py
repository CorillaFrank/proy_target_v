from sqlalchemy import create_engine, text
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

print(f"🔌 Conectando a: {DB_HOST}:{DB_PORT}/{DB_NAME}")

# Usar esquema olap_target por defecto
engine = create_engine(connection_string, connect_args={'options': '-csearch_path=olap_target'})

def run_query(sql: str):
    """Ejecuta una consulta SQL y retorna un DataFrame de pandas"""
    return pd.read_sql(text(sql), engine)

def execute_query(sql: str):
    """Ejecuta una consulta SQL sin retornar datos (DDL, DML)"""
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()