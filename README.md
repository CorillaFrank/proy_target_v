# GenBI Text-to-SQL MVP (Controlado)

## Business Intelligence — GenBI Block  


# Objetivo del Proyecto

Construir un MVP (Minimum Viable Product) de GenBI capaz de:

1. Recibir preguntas en lenguaje natural.
2. Generar SQL usando IA Generativa.
3. Validar el SQL generado.
4. Bloquear consultas peligrosas o inválidas.
5. Ejecutar consultas seguras sobre PostgreSQL.
6. Mostrar resultados analíticos.

---

# Filosofía del Proyecto

Este proyecto NO busca:

- conectar libremente un LLM a una base de datos,
- permitir SQL arbitrario,
- ejecutar consultas sin validación,
- reemplazar el modelado dimensional.

Este proyecto busca enseñar:

- control semántico,
- gobernanza mínima,
- validación determinista,
- separación entre generación y ejecución,
- arquitectura básica GenBI.

---

# Principio Fundamental

> La IA no consulta libremente la base de datos.

La IA:

- propone SQL,
- opera bajo restricciones,
- utiliza contexto controlado,
- y el sistema valida antes de ejecutar.

---

# Arquitectura General

```text
Usuario
↓
Pregunta en lenguaje natural
↓
Prompt Builder
↓
LLM
↓
SQL generado
↓
SQL Validator
↓
PostgreSQL
↓
Resultado
```

---

# Stack Tecnológico

| Componente | Tecnología |
|---|---|
| Database | PostgreSQL |
| Backend | Python |
| ORM / Connection | SQLAlchemy |
| PostgreSQL Driver | psycopg2 |
| LLM | OpenAI GPT-4.1-mini |
| IDE | VS Code |
| Cliente DB | DBeaver |
| Data Processing | pandas |

---

# Estructura del Proyecto

```text
genbi-text-to-sql-mvp/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── sql/
│   ├── 01_create_database.sql
│   ├── 02_create_tables.sql
│   ├── 03_insert_sample_data.sql
│   └── 04_test_queries.sql
│
├── semantic/
│   └── semantic_dictionary.json
│
├── prompts/
│   └── text_to_sql_prompt.txt
│
├── src/
│   ├── config.py
│   ├── db.py
│   ├── semantic_loader.py
│   ├── prompt_builder.py
│   ├── llm_client.py
│   ├── sql_validator.py
│   └── main.py
│
├── docker-compose.yml
└── notebooks/
```

---

# Flujo del Sistema

## Paso 1 — Pregunta del usuario

Ejemplo:

```text
¿Cuál es la venta total por ciudad?
```

---

## Paso 2 — Prompt Engineering

El sistema construye un prompt controlado incluyendo:

- reglas SQL,
- restricciones,
- tablas permitidas,
- métricas oficiales,
- diccionario semántico.

---

## Paso 3 — Generación SQL

El LLM genera SQL únicamente si:

- la pregunta es válida,
- existe contexto suficiente,
- las tablas existen,
- las métricas existen.

---

## Paso 4 — Validación

El sistema valida:

- solo SELECT,
- no DELETE,
- no UPDATE,
- no DROP,
- tablas permitidas,
- columnas válidas,
- múltiples sentencias,
- fake columns.

---

## Paso 5 — Ejecución

Solo si el SQL pasa todas las validaciones:

```text
Validator → PostgreSQL → Resultado
```

---

# Tipos de Respuesta

## SQL_SELECT

La pregunta es válida y puede responderse.

Ejemplo:

```sql
SELECT
  ds.city,
  SUM(fs.total_amount) AS total_sales
FROM fact_sales fs
JOIN dim_store ds
  ON fs.store_id = ds.store_id
GROUP BY ds.city;
```

---

## UNSAFE_REQUEST

La solicitud intenta modificar datos.

Ejemplo:

```text
Borra todas las ventas.
```

Respuesta:

```text
UNSAFE_REQUEST
```

---

## OUT_OF_SCOPE

La información no existe en el Data Mart.

Ejemplo:

```text
¿Cuál es el salario promedio?
```

Respuesta:

```text
OUT_OF_SCOPE
```

---

# Semantic Dictionary

El diccionario semántico representa el contexto oficial del negocio.

Incluye:

- tablas permitidas,
- columnas válidas,
- relaciones,
- granularidad,
- métricas oficiales.

Ejemplo:

```json
{
  "metrics": {
    "total_sales": "SUM(fact_sales.total_amount)",
    "average_ticket": "SUM(fact_sales.total_amount) / COUNT(DISTINCT fact_sales.sale_id)"
  }
}
```

---

# Guardrails Implementados

## Guardrails de Prompt

- Solo SELECT.
- No inventar columnas.
- No inventar métricas.
- No operaciones destructivas.

---

## Guardrails Deterministas

Implementados en `sql_validator.py`.

Validaciones:

- forbidden keywords,
- allowlist de tablas,
- validación de columnas,
- múltiples statements,
- fake columns.

---

# Riesgos que el MVP Controla

| Riesgo | Mitigación |
|---|---|
| DELETE accidental | bloqueado |
| DROP TABLE | bloqueado |
| UPDATE masivo | bloqueado |
| columnas inventadas | bloqueado |
| tablas inexistentes | bloqueado |
| consultas fuera del dominio | OUT_OF_SCOPE |

---

# Modelo Dimensional Utilizado

## Fact Table

- `fact_sales`

## Dimensiones

- `dim_store`
- `dim_product`
- `dim_customer`
- `dim_date`

---

# Cómo Ejecutar el Proyecto

## 1. Crear entorno virtual

```bash
python -m venv .venv
```

Activar:

### Mac/Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

---

## 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 3. Levantar PostgreSQL vía Docker

```bash
docker compose up -d
```

---

## 4. Ejecutar scripts SQL

Orden:

```text
01_create_database.sql
02_create_tables.sql
03_insert_sample_data.sql
04_test_queries.sql
```

---

## 5. Configurar variables de entorno

El archivo `.env` contiene credenciales locales y **NO debe subirse a GitHub**.

Cada alumno debe crear su propio `.env` en la raíz del proyecto tomando como referencia `.env.example`.

### 5.1 Crear archivo `.env.example`

Este archivo sí puede estar en el repositorio porque no contiene secretos reales.

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini

DB_HOST=localhost
DB_PORT=5432
DB_NAME=genbi_dm
DB_USER=postgres
DB_PASSWORD=postgres
```

### 5.2 Crear archivo `.env` local

Cada alumno debe copiar el contenido de `.env.example` en un nuevo archivo llamado `.env` y reemplazar la API key por su valor real.

```bash
cp .env.example .env
```

Luego editar:

```env
OPENAI_API_KEY=tu_api_key_real
```

> Importante: `.env` debe estar incluido en `.gitignore`.

---

## 6. Verificar que `.env` no se sube

Antes de hacer commit, validar:

```bash
git status
```

Y comprobar los archivos versionados:

```bash
git ls-files
```

El archivo `.env` no debe aparecer en la lista.

---

## 7. Ejecutar el MVP

```bash
python src/main.py
```

---

# Ejemplos de Preguntas Válidas

```text
¿Cuál es la venta total por ciudad?
```

```text
¿Cuál es el ticket promedio por ciudad?
```

```text
¿Cuál es la venta total por categoría?
```

```text
¿Cuántas ventas hubo por mes?
```

---

# Ejemplos de Preguntas Bloqueadas

## Unsafe

```text
Borra todas las ventas.
```

## Out of Scope

```text
¿Cuál es el salario promedio?
```

## Fake Columns

```sql
SELECT fs.fake_column
FROM fact_sales fs;
```

---

# Conceptos Importantes Aprendidos

## SQL válido ≠ SQL correcto

Una consulta puede:

- ser sintácticamente válida,
- pero incorrecta analíticamente.

---

## Prompt Engineering ≠ Gobernanza

El prompt ayuda, pero no reemplaza:

- validaciones,
- restricciones,
- controles deterministas.

---

## El LLM NO es el sistema

El LLM:

- genera SQL,
- pero no decide ejecutarlo.

---

# Cómo Adaptar Este MVP al Modelo Dimensional de Cada Grupo

Cada grupo deberá adaptar:

## 1. Tablas del Data Mart

Actualizar:

```json
allowed_tables
```

Ejemplo:

```json
"allowed_tables": [
  "fact_orders",
  "dim_customer",
  "dim_branch"
]
```

---

## 2. Métricas Oficiales

Actualizar:

```json
"metrics"
```

Ejemplo:

```json
"average_order_value":
"SUM(fact_orders.total_amount) / COUNT(DISTINCT fact_orders.order_id)"
```

---

## 3. Columnas Permitidas

Actualizar:

```json
"columns"
```

según el modelo dimensional real del grupo.

---

## 4. Relaciones

Actualizar:

```json
"relationships"
```

Ejemplo:

```json
"fact_orders.customer_id = dim_customer.customer_id"
```

---

## 5. Preguntas de Negocio

Cada grupo deberá probar preguntas alineadas con:

- su dominio,
- sus métricas,
- su grano,
- sus dimensiones.

---

# Recomendaciones para Adaptación

## NO copiar el Data Mart demo

El objetivo es adaptar el MVP a:

- retail,
- salud,
- logística,
- fraude,
- educación,
- banca,
- etc.

---

## Mantener Gobernanza

Aunque cambie el dominio:

- debe mantenerse el validator,
- el semantic dictionary,
- los guardrails,
- y la separación generación/ejecución.

---

# Roadmap Futuro

## Próximas mejoras posibles

- Streamlit UI
- Chat conversacional
- RAG para documentación BI
- Semantic Layer avanzada
- SQL semantic validation
- Observabilidad
- Auditoría
- Multiusuario
- Arquitectura cloud

---

# Conclusión

Este MVP demuestra que GenBI no consiste en:

```text
“preguntarle cosas a ChatGPT”
```

sino en construir:

- contexto,
- semántica,
- validación,
- gobernanza,
- arquitectura controlada.

---

# Frases Finales

```text
La IA propone.
El sistema decide.
```

```text
SQL válido no siempre significa SQL correcto.
```

```text
GenBI requiere contexto, restricciones y gobernanza.
```