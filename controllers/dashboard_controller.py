# controllers/dashboard_controller.py
from database import db
from models import Cine, Genero, Pelicula, Funcion
from sqlalchemy import text
import pandas as pd
from io import BytesIO
from datetime import datetime, date
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import json

class DashboardController:
    
    @staticmethod
    def obtener_datos_filtros():
        """Obtiene opciones para los filtros del dashboard"""
        session = db.get_session()
        try:
            cines = session.query(Cine).filter_by(Activo=True).all()
            generos = session.query(Genero).filter_by(Activo=True).all()
            peliculas = session.query(Pelicula).filter_by(Activo=True).all()
            
            # Obtener funciones futuras y pasadas recientes (últimos 3 meses)
            tres_meses_atras = date.today().replace(day=1)
            funciones = session.query(Funcion).filter(
                Funcion.FechaHora >= tres_meses_atras,
                Funcion.Activo == True
            ).all()
            
            return {
                'cines': cines,
                'generos': generos,
                'peliculas': peliculas,
                'funciones': funciones
            }
        finally:
            session.close()
    
    @staticmethod
    def ejecutar_consulta_dashboard(funcion_nombre, params):
        """Ejecuta una función SQL del dashboard con parámetros"""
        session = db.get_session()
        try:
            # Construir la consulta
            query = text(f"SELECT * FROM dbo.{funcion_nombre}("
                        "@fecha_inicio, @fecha_fin, @cine_ids, "
                        "@genero_ids, @pelicula_ids, @funcion_ids, "
                        "@dias_semana, @agrupacion)")
            
            result = session.execute(query, params)
            
            # Convertir a lista de diccionarios
            columns = result.keys()
            data = [dict(zip(columns, row)) for row in result]
            
            return data
        finally:
            session.close()
    
    @staticmethod
    def obtener_datos_dashboard(filtros):
        """Obtiene todos los datos del dashboard según filtros"""
        # Preparar parámetros para SQL
        params = {
            'fecha_inicio': filtros.get('fecha_inicio'),
            'fecha_fin': filtros.get('fecha_fin'),
            'cine_ids': ','.join(map(str, filtros.get('cine_ids', []))) if filtros.get('cine_ids') else None,
            'genero_ids': ','.join(map(str, filtros.get('genero_ids', []))) if filtros.get('genero_ids') else None,
            'pelicula_ids': ','.join(map(str, filtros.get('pelicula_ids', []))) if filtros.get('pelicula_ids') else None,
            'funcion_ids': ','.join(map(str, filtros.get('funcion_ids', []))) if filtros.get('funcion_ids') else None,
            'dias_semana': ','.join(map(str, filtros.get('dias_semana', []))) if filtros.get('dias_semana') else None,
            'agrupacion': filtros.get('agrupacion', 'dia')
        }
        
        # Obtener datos de cada gráfico
        ingresos = DashboardController.ejecutar_consulta_dashboard('fn_Dashboard_Ingresos', params)
        ocupacion = DashboardController.ejecutar_consulta_dashboard('fn_Dashboard_Ocupacion', params)
        boletos_usados = DashboardController.ejecutar_consulta_dashboard('fn_Dashboard_BoletosUsados', params)
        cancelaciones = DashboardController.ejecutar_consulta_dashboard('fn_Dashboard_Cancelaciones', params)
        
        # Formatear datos para ECharts
        def formatear_datos_echarts(datos, campo_valor, campo_periodo='Periodo'):
            return {
                'periodos': [str(d[campo_periodo]) for d in datos],
                'valores': [float(d[campo_valor]) for d in datos]
            }
        
        return {
            'ingresos': {
                'datos': ingresos,
                'echarts': formatear_datos_echarts(ingresos, 'Ingresos')
            },
            'ocupacion': {
                'datos': ocupacion,
                'echarts': formatear_datos_echarts(ocupacion, 'PorcentajeOcupacion')
            },
            'boletos_usados': {
                'datos': boletos_usados,
                'echarts': formatear_datos_echarts(boletos_usados, 'PorcentajeUsados')
            },
            'cancelaciones': {
                'datos': cancelaciones,
                'echarts': formatear_datos_echarts(cancelaciones, 'PorcentajeCancelaciones')
            },
            'filtros': filtros
        }
    
    @staticmethod
    def generar_excel_raw_data(filtros):
        """Genera Excel con datos sin procesar para exportación"""
        session = db.get_session()
        try:
            # Preparar parámetros
            params = {
                'fecha_inicio': filtros.get('fecha_inicio'),
                'fecha_fin': filtros.get('fecha_fin'),
                'cine_ids': ','.join(map(str, filtros.get('cine_ids', []))) if filtros.get('cine_ids') else None,
                'genero_ids': ','.join(map(str, filtros.get('genero_ids', []))) if filtros.get('genero_ids') else None,
                'pelicula_ids': ','.join(map(str, filtros.get('pelicula_ids', []))) if filtros.get('pelicula_ids') else None,
                'funcion_ids': ','.join(map(str, filtros.get('funcion_ids', []))) if filtros.get('funcion_ids') else None,
                'dias_semana': ','.join(map(str, filtros.get('dias_semana', []))) if filtros.get('dias_semana') else None
            }
            
            # Ejecutar consulta raw data
            query = text("SELECT * FROM dbo.fn_Dashboard_RawData("
                        "@fecha_inicio, @fecha_fin, @cine_ids, "
                        "@genero_ids, @pelicula_ids, @funcion_ids, @dias_semana)")
            
            result = session.execute(query, params)
            
            # Convertir a DataFrame de pandas
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            # Crear archivo Excel en memoria
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Hoja principal
                df.to_excel(writer, sheet_name='Datos_Detallados', index=False)
                
                # Hojas resumidas por métrica
                if not df.empty:
                    # Resumen de ingresos
                    ingresos_resumen = df.groupby('FechaHora').agg({
                        'ValorPagado': 'sum',
                        'BoletoId': 'count'
                    }).reset_index()
                    ingresos_resumen.to_excel(writer, sheet_name='Resumen_Ingresos', index=False)
                    
                    # Resumen de cancelaciones
                    if 'Cancelado' in df.columns:
                        cancel_resumen = df.groupby('FechaHora').agg({
                            'BoletoId': 'count',
                            'Cancelado': 'sum'
                        }).reset_index()
                        cancel_resumen['PorcentajeCancel'] = cancel_resumen['Cancelado'] / cancel_resumen['BoletoId'] * 100
                        cancel_resumen.to_excel(writer, sheet_name='Resumen_Cancelaciones', index=False)
            
            output.seek(0)
            return output
        finally:
            session.close()
    
    @staticmethod
    def generar_pdf_dashboard(datos_dashboard, filtros):
        """Genera PDF del dashboard completo"""
        buffer = BytesIO()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title = Paragraph("Dashboard Administrativo - CineFlow", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Fecha de generación
        fecha_gen = Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal'])
        elements.append(fecha_gen)
        elements.append(Spacer(1, 12))
        
        # Filtros aplicados
        filtros_text = Paragraph("Filtros aplicados:", styles['Heading2'])
        elements.append(filtros_text)
        
        filtros_info = [
            ["Parámetro", "Valor"],
            ["Fecha Inicio", filtros.get('fecha_inicio', 'No especificado')],
            ["Fecha Fin", filtros.get('fecha_fin', 'No especificado')],
            ["Agrupación", filtros.get('agrupacion', 'día').capitalize()]
        ]
        
        if filtros.get('cine_ids'):
            filtros_info.append(["Cines", f"{len(filtros['cine_ids'])} seleccionados"])
        if filtros.get('genero_ids'):
            filtros_info.append(["Géneros", f"{len(filtros['genero_ids'])} seleccionados"])
        
        filtros_table = Table(filtros_info)
        filtros_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(filtros_table)
        elements.append(Spacer(1, 20))
        
        # Resumen de métricas
        for nombre_metrica, datos in datos_dashboard.items():
            if nombre_metrica == 'filtros':
                continue
                
            # Título de la métrica
            titulo_map = {
                'ingresos': 'Ingresos por Boletos',
                'ocupacion': '% Ocupación de Sala',
                'boletos_usados': '% Boletos Usados',
                'cancelaciones': '% de Cancelaciones'
            }
            
            titulo = Paragraph(titulo_map.get(nombre_metrica, nombre_metrica), styles['Heading3'])
            elements.append(titulo)
            
            # Crear tabla con datos
            if datos.get('datos'):
                tabla_data = [["Periodo", "Valor"]]
                for fila in datos['datos']:
                    if nombre_metrica == 'ingresos':
                        valor = f"${fila.get('Ingresos', 0):,.2f}"
                    else:
                        valor = f"{fila.get(f'Porcentaje{nombre_metrica.capitalize()}', 0):.2f}%"
                    tabla_data.append([str(fila.get('Periodo', '')), valor])
                
                tabla = Table(tabla_data)
                tabla.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(tabla)
                elements.append(Spacer(1, 12))
        
        # Construir PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer