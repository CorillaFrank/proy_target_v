from sqlalchemy import text
from src.db import engine

with engine.connect() as conn:
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'olap_target'"))
    tables = [row[0] for row in result]
    print("Tablas en tu base de datos:")
    for t in tables:
        print(f"  - {t}")
# ejecutar cm: python ver_tablas.py