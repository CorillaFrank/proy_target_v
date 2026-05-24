# test_prueba.py
import re
from src.db import run_query

def interpretar_pregunta(pregunta):
    """Traduce pregunta humana a SQL"""
    pregunta = pregunta.lower()
    
    # Pregunta 1: Ventas totales por categoría
    if "ventas totales" in pregunta and ("categoría" in pregunta or "categoria" in pregunta):
        sql = """
        SELECT 
            p.categoria_producto,
            ROUND(SUM(f.ventas), 2) AS total_ventas
        FROM olap_target.fact_ventas_promociones f
        JOIN olap_target.dim_producto p ON f.sk_producto = p.sk_producto
        GROUP BY p.categoria_producto
        ORDER BY total_ventas DESC
        """
        return sql, "VENTAS TOTALES POR CATEGORÍA"
    
    # Pregunta 2: Producto más vendido
    if "producto más vendido" in pregunta or "top producto" in pregunta:
        sql = """
        SELECT 
            p.nombre_producto,
            p.categoria_producto,
            ROUND(SUM(f.ventas), 2) AS total_ventas
        FROM olap_target.fact_ventas_promociones f
        JOIN olap_target.dim_producto p ON f.sk_producto = p.sk_producto
        GROUP BY p.nombre_producto, p.categoria_producto
        ORDER BY total_ventas DESC
        LIMIT 5
        """
        return sql, "TOP 5 PRODUCTOS MÁS VENDIDOS"
    
    # Pregunta 3: Ventas totales general
    if "ventas totales general" in pregunta or "total facturado" in pregunta:
        sql = """
        SELECT 
            ROUND(SUM(ventas), 2) AS total_ventas_generales
        FROM olap_target.fact_ventas_promociones
        """
        return sql, "TOTAL DE VENTAS GENERAL"
    
    # Pregunta 4: Margen por categoría
    if "margen" in pregunta or "mnod" in pregunta or "rentabilidad" in pregunta:
        sql = """
        SELECT 
            p.categoria_producto,
            ROUND(SUM(f.ventas - f.monto_descuento - f.costo_envio), 2) AS total_mnpd
        FROM olap_target.fact_ventas_promociones f
        JOIN olap_target.dim_producto p ON f.sk_producto = p.sk_producto
        GROUP BY p.categoria_producto
        ORDER BY total_mnpd DESC
        """
        return sql, "MNPD (RENTABILIDAD) POR CATEGORÍA"
    
    # Si no entiende la pregunta
    return None, None

def main():
    print("=" * 60)
    print("https://www.target.com/")
    print("=" * 60)
    print("\nPreguntas que puedes hacer:")
    print("  1. 'ventas totales por categoría'")
    print("  2. 'producto más vendido'")
    print("  3. 'ventas totales general'")
    print("  4. 'margen por categoría'")
    print("  5. 'salir'")
    print("-" * 60)
    
    while True:
        pregunta = input("\n💬 Tu pregunta: ").strip()
        
        if pregunta.lower() in ['salir', 'exit', 'quit']:
            print("Estas seguro?")
            break
        
        if not pregunta:
            print("Escribe una pregunta válida")
            continue
        
        # Interpretar la pregunta
        sql, titulo = interpretar_pregunta(pregunta)
        
        if sql is None:
            print(" No entendí tu pregunta. Prueba con: 'ventas totales por categoría'")
            continue
        
        # Ejecutar SQL
        print(f"\n🔍 {titulo}")
        print("-" * 40)
        try:
            df = run_query(sql)
            print(df.to_string(index=False))
            print("\nConsulta ejecutada con éxito")
        except Exception as e:
            print(f" Error: {e}")

if __name__ == "__main__":
    main()