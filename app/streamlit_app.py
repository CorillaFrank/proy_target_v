import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.append(str(SRC_PATH))

from db import run_query
from semantic_loader import load_semantic_dictionary
from prompt_builder import build_prompt
from llm_client import generate_sql
from sql_validator import validate_sql
from business_explainer import explain_result
from chart_recommender import recommend_chart_type
from chart_generator import render_chart

from semantic_context_retriever import retrieve_semantic_context
from dashboard_planner import generate_dashboard_plan
from plan_validator import validate_dashboard_plan
from query_orchestrator import execute_dashboard_plan
from dashboard_renderer import render_generated_dashboard
from dashboard_insight_generator import generate_dashboard_insight


st.set_page_config(
    page_title="GenBI MVP",
    layout="wide"
)

st.title("GenBI MVP")
st.caption("La IA propone. El sistema valida. El sistema ejecuta.")

mode = st.sidebar.radio(
    "Modo GenBI",
    [
        "Pregunta individual",
        "Dashboard Generator"
    ]
)


def render_single_question_mode():
    st.header("Pregunta individual")
    st.caption("Pregunta → IA → SQL → Validación → PostgreSQL → Resultado → Interpretación → Visualización")

    question = st.text_input(
        "Pregunta de negocio",
        placeholder="Ejemplo: ¿Cuál es la venta total por ciudad?"
    )

    if st.button("Generar consulta"):
        if not question.strip():
            st.warning("Escribe una pregunta de negocio.")
            st.stop()

        semantic_dictionary = load_semantic_dictionary()
        prompt = build_prompt(question, semantic_dictionary)
        response = generate_sql(prompt)

        st.subheader("Respuesta IA")
        st.code(response)

        if response == "UNSAFE_REQUEST":
            st.error("Solicitud bloqueada: la pregunta intenta modificar o borrar datos.")
            st.stop()

        if response == "OUT_OF_SCOPE":
            st.warning("No puedo responder esa pregunta con el Data Mart disponible.")
            st.stop()

        sql = response

        if sql.startswith("SQL_SELECT"):
            sql = sql.replace("SQL_SELECT", "", 1).strip()

        st.subheader("SQL generado")
        st.code(sql, language="sql")

        is_valid, message = validate_sql(sql, semantic_dictionary)

        st.subheader("Validación SQL")

        if not is_valid:
            st.error(message)
            st.stop()

        st.success(message)

        df = run_query(sql)

        st.subheader("Resultado")
        st.dataframe(df, use_container_width=True)

        business_explanation = explain_result(
            question=question,
            sql=sql,
            df=df
        )

        st.subheader("Interpretación de negocio")
        st.info(business_explanation)

        st.subheader("Visualización")
        chart_type = recommend_chart_type(question, df)
        st.subheader(f"Visualización sugerida: {chart_type}")
        render_chart(df, chart_type)


def render_dashboard_generator_mode():
    st.header("Dashboard Generator")
    st.caption(
        "Pregunta ejecutiva → Contexto semántico → Planner → Plan JSON → "
        "Validación → Múltiples SQL → Dashboard → Insight ejecutivo"
    )

    dashboard_question = st.text_area(
        "Pregunta ejecutiva de negocio",
        placeholder=(
            "Ejemplo: Genera un dashboard ejecutivo para analizar la venta total, "
            "ticket promedio y número de ventas por mes, categoría y ciudad."
        ),
        height=120
    )

    if st.button("Generar dashboard"):
        if not dashboard_question.strip():
            st.warning("Escribe una pregunta ejecutiva de negocio.")
            st.stop()

        semantic_dictionary = load_semantic_dictionary()
        semantic_context = retrieve_semantic_context(dashboard_question)

        with st.expander("Contexto semántico recuperado", expanded=False):
            st.markdown(semantic_context)

        with st.spinner("Generando plan analítico..."):
            dashboard_plan = generate_dashboard_plan(
                question=dashboard_question,
                semantic_dictionary=semantic_dictionary,
                semantic_context=semantic_context
            )

        st.subheader("Plan generado por la IA")
        st.json(dashboard_plan)

        is_valid_plan, plan_message = validate_dashboard_plan(
            dashboard_plan,
            semantic_dictionary
        )

        st.subheader("Validación del plan")

        if not is_valid_plan:
            st.error(plan_message)
            st.stop()

        st.success(plan_message)

        st.subheader("Lectura pedagógica del plan")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### KPIs propuestos")
            for kpi in dashboard_plan.get("kpis", []):
                st.markdown(f"- **{kpi.get('title')}** `{kpi.get('metric')}`")
                st.caption(kpi.get("query_intent", ""))

        with col2:
            st.markdown("### Visualizaciones propuestas")
            for visual in dashboard_plan.get("visuals", []):
                st.markdown(
                    f"- **{visual.get('title')}** — `{visual.get('chart_type')}`"
                )
                st.caption(visual.get("query_intent", ""))

        st.info(
            "El plan ya fue validado. Ahora el sistema genera, valida y ejecuta "
            "una SQL por cada KPI y visualización propuesta."
        )

        st.subheader("Ejecución del plan")

        with st.spinner("Generando y ejecutando múltiples consultas SQL..."):
            execution_results = execute_dashboard_plan(
                dashboard_plan,
                semantic_dictionary
            )

        render_generated_dashboard(
            plan=dashboard_plan,
            execution_results=execution_results
        )

        st.divider()
        st.subheader("Insight ejecutivo generado por IA")

        with st.spinner("Generando insight ejecutivo..."):
            dashboard_insight = generate_dashboard_insight(
                question=dashboard_question,
                dashboard_plan=dashboard_plan,
                execution_results=execution_results,
                semantic_context=semantic_context
            )

        with st.container(border=True):
            st.markdown(dashboard_insight)


if mode == "Pregunta individual":
    render_single_question_mode()

if mode == "Dashboard Generator":
    render_dashboard_generator_mode()