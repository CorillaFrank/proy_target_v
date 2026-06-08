import sys
from pathlib import Path

import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# ==================== RUTAS Y MODULOS ====================
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


# ==================== CONFIGURACION ====================
st.set_page_config(
    page_title="Target Corporation",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CSS SIMPLIFICADO ====================
st.markdown("""
<style>
* {
    font-family: 'Courier New', monospace !important;
}

/* Fondo oscuro */
.stApp {
    background: #0a0a0a;
}

/* Fondo de cuadritos (grid) */
.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
        linear-gradient(rgba(255, 50, 50, 0.08) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 50, 50, 0.08) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d0d0d;
    border-right: 2px solid #ff3333;
}

/* Ocultar boton de colapsar sidebar */
[data-testid="stSidebarHeader"] {
    display: none !important;
}

/* Tarjetas */
.glass-card {
    background: transparent;
    border-radius: 0;
    border: none;
    padding: 0.5rem 0;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 51, 51, 0.3);
    transition: all 0.3s ease;
}

.glass-card:hover {
    border-bottom-color: #ff3333;
    box-shadow: 0 2px 10px rgba(255, 51, 51, 0.3);
}

/* Títulos */
h1 {
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: #ff3333 !important;
    text-align: center;
}

h2, h3 {
    color: #ff3333 !important;
}

/* Texto */
p, span, label, .stMarkdown, .stCaption {
    color: #cccccc !important;
}

/* Inputs */
.stTextInput > div > div > input, 
.stTextArea > div > div > textarea {
    background: #1a1a1a !important;
    border: 1px solid #ff3333 !important;
    border-radius: 10px !important;
    color: #00ffcc !important;
}

/* Botones */
.stButton > button {
    background: #ff3333;
    color: white;
    border: none;
    border-radius: 30px;
    font-weight: 700;
    width: 100%;
}

.stButton > button:hover {
    background: #ff5555;
}

/* Metricas */
[data-testid="stMetricValue"] {
    color: #ff3333 !important;
}

[data-testid="stMetricLabel"] {
    color: #00ffcc !important;
}

/* Codigo */
.stCodeBlock {
    background: #0a0a0a !important;
    border: 1px solid #ff3333 !important;
    border-radius: 10px !important;
}

code {
    color: #00ffcc !important;
}

/* Dataframes */
.stDataFrame {
    border: 1px solid #ff3333;
    border-radius: 10px;
}

hr {
    border-color: #ff3333;
}

.info-card {
    background: #1a1a1a;
    border-left: 3px solid #ff3333;
    border-radius: 10px;
    padding: 0.8rem;
    margin: 0.5rem 0;
}

.stat-box {
    background: #1a1a1a;
    border-radius: 10px;
    padding: 0.6rem;
    text-align: center;
    border: 1px solid #ff3333;
}

.badge {
    background: #00ffcc;
    color: #0a0a0a;
    padding: 0.2rem 0.7rem;
    border-radius: 15px;
    font-size: 0.7rem;
}
            /* Scroll invisible pero funcional */
::-webkit-scrollbar {
    width: 0px !important;
    height: 0px !important;
    background: transparent !important;
    display: none !important;
}

::-webkit-scrollbar-track {
    background: transparent !important;
    display: none !important;
}

::-webkit-scrollbar-thumb {
    background: transparent !important;
    display: none !important;
}

/* Para Firefox */
* {
    scrollbar-width: none !important;
}

/* Para Edge/IE */
* {
    -ms-overflow-style: none !important;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
/* Eliminar espacio superior del contenedor principal */
.block-container {
    padding-top: 0rem !important;
    margin-top: -20px !important;
}

/* Eliminar espacio del header de Streamlit */
header {
    display: none !important;
}

/* Eliminar espacio del primer elemento */
.element-container:first-child {
    margin-top: 5px !important;
}

/* Eliminar padding del main */
.main .block-container {
    padding-top: 0 !important;
}
            /* Ocultar textos alternativos de íconos */
span[data-testid="stIconMaterial"] {
    display: none !important;
}

/* Ocultar el texto "keyboard double arrow" */
.st-emotion-cache-2x5h05 {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Contenedor centrado para logo y título
    col_centrado1, col_contenido, col_centrado2 = st.columns([1, 2, 1])
    
    with col_contenido:
        col_logo, col_titulo = st.columns([1, 3])
        
        with col_logo:
            # CORREGIDO: Usar Path para encontrar el logo correctamente
            logo_path = Path(__file__).parent / "logo.png"
            if logo_path.exists():
                st.image(str(logo_path), width=70)
            else:
                # Fallback: mostrar un emoji si no encuentra el logo
                st.markdown("<h1 style='font-size: 2.5rem; margin:0; color: #ff3333;'></h1>", unsafe_allow_html=True)
        
        with col_titulo:
            st.markdown("""
            <div style="display: flex; align-items: center; height: 100%; ">
                <span style="font-size: 3rem; font-weight: 900; 
                           background: linear-gradient(135deg, #FFFFFF, #FF3333, #FF8888);
                           -webkit-background-clip: text;
                           -webkit-text-fill-color: transparent;
                           letter-spacing: 4px;">
                    TARGET
                </span>
            </div>
            """, unsafe_allow_html=True)
    # Párrafo centrado debajo
    st.markdown("""
    <div style="text-align: center; margin-top: 10px;">
        <p style="margin: 0; font-size: 0.8rem; letter-spacing: 3px; color: #00ffcc;">
            BI-GENERATIVA | PREGUNTA • ANALIZA • DECIDE
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.markdown("""
<div style="text-align: center; margin-top: 10px;">
    <p style="margin: 0; font-size: 1.0rem; color: #888;">
        <strong style="font-size: 1.3rem; color: #ff3333;">Target Corporation</strong> es una de las empresas de comercio minorista más grandes y
        reconocidas de los Estados Unidos. Fundada en 1902, la compañía opera como una cadena de
        grandes almacenes de descuento, destacándose en el mercado por ofrecer una amplia variedad de productos
        desde moda y artículos para el hogar hasta tecnología y comestibles, 
        que combinan un diseño atractivo y de alta calidad con precios accesibles.
    </p>
</div>
""", unsafe_allow_html=True)
st.divider()



# ==================== MENU ====================
with st.container():
    col_m1, col_m2, col_m3 = st.columns([1, 2, 1])
    with col_m2:
        selected = option_menu(
            menu_title=None,
            options=["CONSULTAS", "PANEL DE CONTROL", "Centro de Análisis"],
            icons=["search", "grid", "activity"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background": "transparent"},
                "icon": {"color": "#FF3333", "font-size": "16px"},
                "nav-link": {
                    "font-size": "13px",
                    "text-align": "center",
                    "margin": "0px",
                    "--hover-color": "rgba(255, 51, 51, 0.15)",
                    "color": "#CCCCCC",
                    "border-radius": "10px",
                    "font-family": "'Courier New', monospace",
                    "font-weight": "600",
                },
                "nav-link-selected": {
                    "background": "#FF3333",
                    "color": "white",
                },
            }
        )
        
        if selected == "CONSULTAS":
            mode = "query"
        elif selected == "PANEL DE CONTROL":
            mode = "dashgen"
        else:
            mode = "hub"


# ==================== SIDEBAR ====================
with st.sidebar:
    # ===== TÍTULO ACERCA DE =====
    st.markdown("""
    <div style="text-align: center;">
        <h2 style="margin: 0; color: #FF3333; letter-spacing: 8px;">ACERCA DE</h2>
        <p style="margin: 0; color: #FF3333; letter-spacing: 8px;">TARGET</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # ===== DÓNDE ESTAMOS =====
    st.markdown("### 📍 Target en números")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Tiendas", "2,000+", delta="EE.UU.")
    with col_b:
        st.metric("Años", "124", delta="desde 1902")
    
    col_c, col_d = st.columns(2)
    with col_c:
        st.metric("Productos", "40+", delta="marcas propias")
    with col_d:
        st.metric("Cobertura", "75%", delta="a 10 millas")
    
    st.divider()
    
    # ===== LO QUE VENDEMOS =====
    st.markdown("### 🛒 Productos")
    st.markdown("""
    | Categoría | Ejemplos |
    |-----------|----------|
    | Alimentos | Comestibles, bebidas |
    | Indumentaria | Ropa hombre, mujer, niños |
    | Hogar | Muebles, decoración |
    | Electrónica | Tecnología |
    | Bebé | Productos infantiles |
    | Juguetes | Entretenimiento |
    """)
    
    st.divider()
    
    # ===== CÓMO COMPRAR =====
    st.markdown("### 🚚 Compra fácil")
    st.markdown("""
    - **En tienda** → Retiro en el local
    - **Online** → Envío a domicilio
    - **App** → iOS y Android
    - **Recogida** → Curbside pickup
    """)
    
    st.divider()
    
    # ===== REDES SOCIALES =====
    st.markdown("###  Redes Sociales")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("""
        <div style="background: #1a1a1a; border-radius: 8px; padding: 0.3rem; text-align: center;">
            <a href="https://www.instagram.com/target" target="_blank" style="text-decoration: none; color: write;">
                Instagram<br>
                <small></small>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    with col_r2:
        st.markdown("""
        <div style="background: #1a1a1a; border-radius: 8px; padding: 0.3rem; text-align: center;">
            <a href="https://www.facebook.com/target" target="_blank" style="text-decoration: none; color: write;">
                Facebook<br>
                <small></small>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    col_r3, col_r4 = st.columns(2)
    with col_r3:
        st.markdown("""
        <div style="background: #1a1a1a; border-radius: 8px; padding: 0.3rem; text-align: center;">
            <a href="https://twitter.com/target" target="_blank" style="text-decoration: none; color: write;">
                 Twitter<br>
                <small></small>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    with col_r4:
        st.markdown("""
        <div style="background: #1a1a1a; border-radius: 8px; padding: 0.3rem; text-align: center;">
            <a href="https://www.tiktok.com/@target" target="_blank" style="text-decoration: none; color: write;">
                TikTok<br>
                <small></small>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ===== FOOTER MEJORADO =====
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <div style="background: linear-gradient(90deg, transparent, #FF3333, #00ffcc, #FF3333, transparent); 
                    height: 1px; width: 100%; margin: 0 auto 0.5rem auto;"></div>
        <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap; margin: 0.5rem 0;">
            <small style="color: #888;">Target Corporation</small>
            <small style="color: #00ffcc;">Business Intelligence (BI)</small>
            <small style="color: #888;"></small>
        </div>
        <small style="color: #888; font-size: 0.8rem;">© 2026 | Todos los derechos reservados</small>
    </div>
    """, unsafe_allow_html=True)

# ==================== QUERY MODE ====================
def render_query_mode():
    # ... tu código existente ...
    
    
    st.markdown("### Consulta en Lenguaje Natural")
  
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Ejemplos Rapidos:**")
        st.caption("- Ventas por categoría")
        st.caption("- Los 5 mejores productos")
        st.caption("- Tendencia mensual")
    
    with col2:
        st.markdown("**Target KPIs:**")
        st.caption("- Ventas Totales")
        st.caption("- Margen Neto Post Descuento")
        st.caption("- Impacto del descuento")
        st.caption("- Ventas por Mes")
    
    question = st.text_area(
        "Tu Pregunta",
        placeholder="Ej: ¿Cuál es la tendencia de ventas por categoría?",
        height=80
    )
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        generate_btn = st.button("GENERAR CONSULTA", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if generate_btn:
        if not question.strip():
            st.warning("Please enter a question")
            return
        
        with st.spinner("Processing..."):
            semantic_dictionary = load_semantic_dictionary()
            prompt = build_prompt(question, semantic_dictionary)
            response = generate_sql(prompt)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### AI Response")
        
        if response == "UNSAFE_REQUEST":
            st.error("Blocked: Write operations not permitted")
            return
        if response == "OUT_OF_SCOPE":
            st.warning("Out of Scope: Cannot answer with available data")
            return
        
        st.success("Query generated successfully")
        st.markdown('</div>', unsafe_allow_html=True)
        
        sql = response
        if sql.startswith("SQL_SELECT"):
            sql = sql.replace("SQL_SELECT", "", 1).strip()
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### Generated SQL")
        st.code(sql, language="sql")
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.spinner("Validating..."):
            is_valid, message = validate_sql(sql, semantic_dictionary)
        
        if not is_valid:
            st.error(f"Validation Failed: {message}")
            return
        
        st.success(message)
        
        with st.spinner("Executing..."):
            df = run_query(sql)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### Results")
        st.dataframe(df, use_container_width=True)
        st.caption(f"Total Rows: {len(df)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.spinner("Generating insights..."):
            explanation = explain_result(question=question, sql=sql, df=df)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### Insights")
        st.info(explanation)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### Visualization")
        chart_type = recommend_chart_type(question, df)
        st.markdown(f"**Recommended Chart:** {chart_type}")
        render_chart(df, chart_type)
        st.markdown('</div>', unsafe_allow_html=True)


def render_dashgen_mode():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### Generador de paneles de control")
    st.caption("Generar paneles de control a partir de lenguaje natural")
    
    dashboard_question = st.text_area(
        "Pregunta ejecutiva",
        placeholder="Crear un panel de control para analizar las ventas por categoría y región",
        height=120
    )
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        generate_btn = st.button("Generar panel de control", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if generate_btn:
        if not dashboard_question.strip():
            st.warning("Please describe the dashboard")
            return
        
        with st.spinner("Analyzing..."):
            semantic_dictionary = load_semantic_dictionary()
            semantic_context = retrieve_semantic_context(dashboard_question)
        
        with st.expander("Semantic Context", expanded=False):
            st.markdown(semantic_context)
        
        with st.spinner("Generating plan..."):
            dashboard_plan = generate_dashboard_plan(
                question=dashboard_question,
                semantic_dictionary=semantic_dictionary,
                semantic_context=semantic_context
            )
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### Plan de panel de control")
        st.json(dashboard_plan)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.spinner("Validating..."):
            is_valid, message = validate_dashboard_plan(dashboard_plan, semantic_dictionary)
        
        if not is_valid:
            st.error(message)
            return
        
        st.success(message)
        
        with st.spinner("Executing..."):
            results = execute_dashboard_plan(dashboard_plan, semantic_dictionary)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### Panel de Control Generado")
        render_generated_dashboard(plan=dashboard_plan, execution_results=results)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.spinner("Generating insights..."):
            insight = generate_dashboard_insight(
                question=dashboard_question,
                dashboard_plan=dashboard_plan,
                execution_results=results,
                semantic_context=semantic_context
            )
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### Insights")
        st.info(insight)
        st.markdown('</div>', unsafe_allow_html=True)


def render_hub_mode():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### Centro de Análisis")
    st.caption("Dashboards predefinidos y análisis ejecutivo")
    
    st.markdown("---")
    
    # Selector de vistas estáticas
    vista_seleccionada = st.radio(
        "Selecciona una vista:",
        ["Ventas por Categoría", "Ventas por Trimestre", "Top 10 MNPD", "Evolución Anual"],
        horizontal=True
    )
    
    st.markdown("---")
    # ============ VISTA: VENTAS POR CATEGORÍA ============
    if vista_seleccionada == "Ventas por Categoría":
        st.markdown("## Ventas por Categoría de Producto")
        st.caption("Análisis de ventas brutas, impuestos y participación porcentual")
        
        # Datos estáticos (puedes reemplazar con consulta a DB)
        data = {
            "categoria_producto": ["Furniture", "Office Supplies", "Technology"],
            "total_ventas_brutas": [5_297_999.14, 3_764_929.18, 6_443_793.75],
            "total_impuestos": [4_989_310.57, 3_538_449.99, 6_104_531.82],
            "participacion_porcentual": [34.17, 24.28, 41.55]
        }
        
        df_ventas = pd.DataFrame(data)
        
        # Formatear números
        df_ventas["total_ventas_brutas"] = df_ventas["total_ventas_brutas"].apply(lambda x: f"${x:,.2f}")
        df_ventas["total_impuestos"] = df_ventas["total_impuestos"].apply(lambda x: f"${x:,.2f}")
        df_ventas["participacion_porcentual"] = df_ventas["participacion_porcentual"].apply(lambda x: f"{x:.2f}%")
        
        # Mostrar tabla
        st.dataframe(
            df_ventas,
            column_config={
                "categoria_producto": "Categoría",
                "total_ventas_brutas": "Ventas Brutas",
                "total_impuestos": "Impuestos",
                "participacion_porcentual": "Participación"
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Métricas clave
        st.markdown("---")
        st.markdown("###  Resumen Ejecutivo")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Categoría Líder", "Technology", delta="+41.55%")
        with col2:
            st.metric("Total Ventas Brutas", "$15,506,722.07")
        with col3:
            st.metric("Total Impuestos", "$14,632,292.38")
        
        # Gráfico de barras
        st.markdown("###  Distribución de Ventas por Categoría")
        
        # Reconstruir datos para gráfico
        df_chart = pd.DataFrame({
            "Categoría": ["Furniture", "Office Supplies", "Technology"],
            "Ventas Brutas": [5_297_999.14, 3_764_929.18, 6_443_793.75]
        })
        
        st.bar_chart(df_chart.set_index("Categoría"), use_container_width=True)
    
   
    # ============ VISTA: VENTAS POR TRIMESTRE (NUEVA) ============
    elif vista_seleccionada == "Ventas por Trimestre":
        st.markdown("## Ventas por Trimestre")
        st.caption("Análisis de ventas - Technology | Small Business | West")
        
        # Datos estáticos de la imagen
        data_trimestre = {
            "trimestre": [1, 2, 3, 4],
            "categoria_producto": ["Technology", "Technology", "Technology", "Technology"],
            "segmento_cliente": ["Small Business", "Small Business", "Small Business", "Small Business"],
            "region": ["West", "West", "West", "West"],
            "total_ventas_brutas": [48_431.95, 23_457.00, 11_369.29, 4_339.03],
            "total_impuestos": [45_091.03, 22_130.30, 10_410.79, 4_090.72],
            "numero_transacciones": [11, 5, 5, 2]
        }
        
        df_trimestre = pd.DataFrame(data_trimestre)
        
        # Formatear para mostrar
        df_display = df_trimestre.copy()
        df_display["total_ventas_brutas"] = df_display["total_ventas_brutas"].apply(lambda x: f"${x:,.2f}")
        df_display["total_impuestos"] = df_display["total_impuestos"].apply(lambda x: f"${x:,.2f}")
        df_display = df_display[["trimestre", "total_ventas_brutas", "total_impuestos", "numero_transacciones"]]
        df_display.columns = ["Trimestre", "Ventas Brutas", "Impuestos", "Transacciones"]
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Métricas clave
        st.markdown("---")
        st.markdown("###  Resumen Ejecutivo")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Ventas Totales", "$87,597.27")
        with col2:
            st.metric("Total Transacciones", "23")
        with col3:
            st.metric("Trimestre más alto", "Q1", delta="$48,431.95")
        with col4:
            st.metric("Tendencia", "Decreciente", delta="-91%")
        
        # Gráfico de tendencia
        st.markdown("###  Tendencia de Ventas por Trimestre")
        st.line_chart(df_trimestre.set_index("trimestre")["total_ventas_brutas"])
        
        # Insight adicional
        st.info(" **Insight:** Las ventas muestran una tendencia decreciente trimestre a trimestre, con una caída del 91% desde el Q1 al Q4.")
    
    # ============ VISTA: TOP PRODUCTOS ============
    
    elif vista_seleccionada == "Top 10 MNPD":
        st.markdown("## Top 10 Productos con Mayor Margen Neto Post Descuento (MNPD)")
        st.caption("Productos más rentables después de aplicar descuentos")
        
        # Datos estáticos de la imagen
        data_top10 = {
            "rank": list(range(1, 11)),
            "nombre_producto": [
                "Polycom ViewStation™ ISDN Videoconferencing Unit",
                "Global Troy™ Executive Leather Low-Back Tilter",
                "Canon PC940 Copier",
                "Riverside Palais Royal Lawyers Bookcase, Royale Cherry Finish",
                "Hewlett Packard LaserJet 3310 Copier",
                "Bretford CR8500 Series Meeting Room Furniture",
                "Hewlett-Packard cp1700 [D, PS] Series Color Inkjet Printers",
                "Sharp AL-1530CS Digital Copier",
                "GBC DocuBind 200 Manual Binding Machine",
                "Bretford CR4500 Series Slim Rectangular Table"
            ],
            "margen_neto_post_descuento": [451.64, 312.24, 669.55, 316.20, 954.02, 684.85, 164.84, 58.15, 1.15, 336.77]
        }
        
        df_top10 = pd.DataFrame(data_top10)
        
        # Formatear para mostrar
        df_display = df_top10.copy()
        df_display["margen_neto_post_descuento"] = df_display["margen_neto_post_descuento"].apply(lambda x: f"${x:,.2f}")
        df_display = df_display[["rank", "nombre_producto", "margen_neto_post_descuento"]]
        df_display.columns = ["#", "Producto", "MNPD"]
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Métricas clave
        st.markdown("---")
        st.markdown("###  Resumen Ejecutivo")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Producto con mayor MNPD", "Hewlett Packard LaserJet", delta="$954.02")
        with col2:
            st.metric("MNPD Promedio Top 10", f"${df_top10['margen_neto_post_descuento'].mean():,.2f}")
        with col3:
            st.metric("MNPD Total Top 10", f"${df_top10['margen_neto_post_descuento'].sum():,.2f}")
        
        # Gráfico de barras
        st.markdown("###  Top 10 Productos por MNPD")
        
        # Preparar datos para gráfico (nombres abreviados)
        df_chart = df_top10.copy()
        df_chart["nombre_corto"] = df_chart["nombre_producto"].apply(lambda x: x[:30] + "..." if len(x) > 30 else x)
        
        st.bar_chart(df_chart.set_index("nombre_corto")["margen_neto_post_descuento"], use_container_width=True)
        
        # Insight
        st.info("💡 **Insight:** Los productos de tecnología y equipos de oficina de alta gama generan los mayores márgenes netos post descuento. La fotocopiadora Hewlett Packard LaserJet 3310 destaca con un MNPD de $954.02.")
    
 # ============ VISTA: EVOLUCIÓN ANUAL (NUEVA) ============
    elif vista_seleccionada == "Evolución Anual":
        st.markdown("## Evolución de Ventas y MNPD año tras año")
        st.caption("Tendencia histórica de ventas totales y margen neto post descuento")
        
        # Datos estáticos de la imagen
        data_evolucion = {
            "año": [2022, 2023, 2024, 2025],
            "total_ventas": [4_354_696.71, 3_685_916.16, 3_597_484.15, 3_868_625.05],
            "total_mnpd": [4_119_753.08, 3_477_985.01, 3_386_751.36, 3_647_802.93]
        }
        
        df_evolucion = pd.DataFrame(data_evolucion)
        
        # Formatear para mostrar
        df_display = df_evolucion.copy()
        df_display["total_ventas"] = df_display["total_ventas"].apply(lambda x: f"${x:,.2f}")
        df_display["total_mnpd"] = df_display["total_mnpd"].apply(lambda x: f"${x:,.2f}")
        df_display.columns = ["Año", "Total Ventas", "Total MNPD"]
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Métricas clave
        st.markdown("---")
        st.markdown("###  Resumen Ejecutivo")
        
        # Calcular variaciones
        ventas_2022 = data_evolucion["total_ventas"][0]
        ventas_2025 = data_evolucion["total_ventas"][3]
        var_ventas = ((ventas_2025 - ventas_2022) / ventas_2022) * 100
        
        mnpd_2022 = data_evolucion["total_mnpd"][0]
        mnpd_2025 = data_evolucion["total_mnpd"][3]
        var_mnpd = ((mnpd_2025 - mnpd_2022) / mnpd_2022) * 100
        
        mejor_año_ventas = max(data_evolucion["total_ventas"])
        mejor_año_mnpd = max(data_evolucion["total_mnpd"])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Ventas Totales (2022-2025)", f"${ventas_2025:,.2f}", delta=f"{var_ventas:.1f}%")
        with col2:
            st.metric("MNPD Total (2022-2025)", f"${mnpd_2025:,.2f}", delta=f"{var_mnpd:.1f}%")
        with col3:
            st.metric("Mejor Año Ventas", "2022", delta=f"${mejor_año_ventas:,.2f}")
        with col4:
            st.metric("Mejor Año MNPD", "2022", delta=f"${mejor_año_mnpd:,.2f}")
        
        # Gráfico de líneas (evolución)
        st.markdown("###  Tendencia de Ventas vs MNPD (2022-2025)")
        
        # Gráfico combinado
        chart_data = df_evolucion.set_index("año")[["total_ventas", "total_mnpd"]]
        st.line_chart(chart_data, use_container_width=True)
        
        # Gráfico de barras
        st.markdown("###  Comparativa por Año")
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(df_evolucion.set_index("año")["total_ventas"], use_container_width=True)
        with col2:
            st.bar_chart(df_evolucion.set_index("año")["total_mnpd"], use_container_width=True)
        
        # Insights
        st.markdown("---")
        st.markdown("### 💡 Insights Estratégicos")
        
        if var_ventas < 0:
            insight_ventas = f" Las ventas totales disminuyeron un {abs(var_ventas):.1f}% entre 2022 y 2025, pasando de ${ventas_2022:,.2f} a ${ventas_2025:,.2f}."
        else:
            insight_ventas = f" Las ventas totales aumentaron un {var_ventas:.1f}% entre 2022 y 2025."
        
        if var_mnpd < 0:
            insight_mnpd = f" El MNPD disminuyó un {abs(var_mnpd):.1f}% en el mismo período."
        else:
            insight_mnpd = f" El MNPD aumentó un {var_mnpd:.1f}% en el mismo período."
        
        st.info(f" **Análisis:** {insight_ventas} {insight_mnpd}")
        
       
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== RENDER ====================
if mode == "query":
    render_query_mode()
elif mode == "dashgen":
    render_dashgen_mode()
elif mode == "hub":
    render_hub_mode()