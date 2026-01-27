# controllers/admin_controller.py
# Controlador para operaciones del dashboard administrativo

from database import db
from models import Cine, Genero, Pelicula, Funcion, Sala, Usuario, Boleto, TipoSala
from sqlalchemy import text, func, and_, or_, case
from sqlalchemy.orm import joinedload, aliased
from datetime import datetime, date, timedelta
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import traceback
import json
from typing import List, Dict, Any, Optional

class DashboardController:
    """Controlador para operaciones del dashboard administrativo"""
    
    @staticmethod
    def obtener_opciones_filtros():
        """Obtiene todas las opciones disponibles para los filtros del dashboard"""
        session = db.get_session()
        try:
            # Cines activos
            cines = session.query(Cine).filter_by(Activo=True).order_by(Cine.Cine).all()
            
            # Géneros activos
            generos = session.query(Genero).filter_by(Activo=True).order_by(Genero.Genero).all()
            
            # Películas activas
            peliculas = session.query(Pelicula).filter_by(Activo=True).order_by(Pelicula.Titulo).all()
            
            # Funciones futuras y recientes (últimos 3 meses)
            fecha_limite = datetime.now() - timedelta(days=90)
            
            # Cargar funciones con sus relaciones sala y película
            funciones = session.query(Funcion).options(
                joinedload(Funcion.sala).joinedload(Sala.cine),
                joinedload(Funcion.pelicula)
            ).filter(
                Funcion.FechaHora >= fecha_limite,
                Funcion.Activo == True
            ).order_by(Funcion.FechaHora.desc()).limit(100).all()
            
            # Días de la semana
            dias_semana = [
                {'id': 1, 'nombre': 'Lunes'},
                {'id': 2, 'nombre': 'Martes'},
                {'id': 3, 'nombre': 'Miércoles'},
                {'id': 4, 'nombre': 'Jueves'},
                {'id': 5, 'nombre': 'Viernes'},
                {'id': 6, 'nombre': 'Sábado'},
                {'id': 7, 'nombre': 'Domingo'}
            ]
            
            return {
                'cines': cines,
                'generos': generos,
                'peliculas': peliculas,
                'funciones': funciones,
                'dias_semana': dias_semana
            }
            
        except Exception as e:
            print(f"Error en obtener_opciones_filtros: {e}")
            traceback.print_exc()
            return {
                'cines': [],
                'generos': [],
                'peliculas': [],
                'funciones': [],
                'dias_semana': []
            }
        finally:
            session.close()
    
    @staticmethod
    def construir_filtros_sql(params: Dict[str, Any]) -> str:
        """Construye cláusulas WHERE para SQL basadas en los filtros"""
        condiciones = []
        
        # Filtro de fechas (manejar fechas como strings)
        if params.get('fecha_inicio') and params.get('fecha_fin'):
            fecha_inicio = params['fecha_inicio']
            fecha_fin = params['fecha_fin']
            condiciones.append(f"f.FechaHora >= '{fecha_inicio}' AND f.FechaHora <= '{fecha_fin}'")
        
        # Filtro de cines
        if params.get('cine_ids') and len(params['cine_ids']) > 0:
            cine_ids = ','.join(map(str, params['cine_ids']))
            condiciones.append(f"s.IdCine IN ({cine_ids})")
        
        # Filtro de géneros
        if params.get('genero_ids') and len(params['genero_ids']) > 0:
            genero_ids = ','.join(map(str, params['genero_ids']))
            condiciones.append(f"pg.IdGénero IN ({genero_ids})")
        
        # Filtro de películas
        if params.get('pelicula_ids') and len(params['pelicula_ids']) > 0:
            pelicula_ids = ','.join(map(str, params['pelicula_ids']))
            condiciones.append(f"f.IdPelícula IN ({pelicula_ids})")
        
        # Filtro de funciones
        if params.get('funcion_ids') and len(params['funcion_ids']) > 0:
            funcion_ids = ','.join(map(str, params['funcion_ids']))
            condiciones.append(f"f.Id IN ({funcion_ids})")
        
        # Filtro de días de semana
        if params.get('dias_semana') and len(params['dias_semana']) > 0:
            dias_semana = ','.join(map(str, params['dias_semana']))
            condiciones.append(f"DATEPART(weekday, f.FechaHora) IN ({dias_semana})")
        
        return " AND ".join(condiciones) if condiciones else "1=1"
    
    @staticmethod
    def obtener_agrupacion_sql(agrupacion: str) -> str:
        """Devuelve la cláusula SQL para la agrupación temporal"""
        if agrupacion == 'semana':
            return "DATEADD(day, 1 - DATEPART(weekday, f.FechaHora), CONVERT(DATE, f.FechaHora))"
        elif agrupacion == 'mes':
            return "DATEFROMPARTS(YEAR(f.FechaHora), MONTH(f.FechaHora), 1)"
        else:  # 'dia'
            return "CONVERT(DATE, f.FechaHora)"
    
    @staticmethod
    def obtener_ingresos(filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Obtiene ingresos por período según los filtros aplicados"""
        session = db.get_session()
        try:
            # Construir filtros WHERE
            where_clause = DashboardController.construir_filtros_sql(filtros)
            agrupacion_sql = DashboardController.obtener_agrupacion_sql(filtros.get('agrupacion', 'dia'))
            
            # Query SQL para ingresos usando la función de la base de datos
            query = text(f"""
                SELECT 
                    {agrupacion_sql} AS Periodo,
                    SUM(b.ValorPagado) AS Ingresos,
                    COUNT(b.Id) AS BoletosVendidos
                FROM Funciones f
                INNER JOIN Salas s ON f.IdSala = s.Id
                INNER JOIN Películas p ON f.IdPelícula = p.Id
                LEFT JOIN PelículaGénero pg ON p.Id = pg.IdPelícula
                INNER JOIN Boletos b ON f.Id = b.IdFunción
                LEFT JOIN BoletosCancelados bc ON b.Id = bc.IdBoleto
                WHERE {where_clause}
                    AND f.Activo = 1
                    AND bc.Id IS NULL  -- Excluir boletos cancelados
                GROUP BY {agrupacion_sql}
                ORDER BY Periodo
            """)
            
            result = session.execute(query)
            datos = []
            
            for row in result:
                datos.append({
                    'Periodo': row.Periodo.isoformat() if hasattr(row.Periodo, 'isoformat') else str(row.Periodo),
                    'Ingresos': float(row.Ingresos) if row.Ingresos else 0.0,
                    'BoletosVendidos': row.BoletosVendidos or 0
                })
            
            return datos
            
        except Exception as e:
            print(f"Error en obtener_ingresos: {e}")
            traceback.print_exc()
            return []
        finally:
            session.close()
    
    @staticmethod
    def obtener_ocupacion(filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Obtiene porcentaje de ocupación por período según los filtros"""
        session = db.get_session()
        try:
            where_clause = DashboardController.construir_filtros_sql(filtros)
            agrupacion_sql = DashboardController.obtener_agrupacion_sql(filtros.get('agrupacion', 'dia'))
            
            # Query para ocupación
            query = text(f"""
                WITH CapacidadFunciones AS (
                    SELECT 
                        f.Id AS FuncionId,
                        f.FechaHora,
                        {agrupacion_sql} AS Periodo,
                        COUNT(DISTINCT a.Id) AS CapacidadTotal
                    FROM Funciones f
                    INNER JOIN Salas s ON f.IdSala = s.Id
                    INNER JOIN Asientos a ON s.Id = a.IdSala AND a.Activo = 1
                    INNER JOIN Películas p ON f.IdPelícula = p.Id
                    LEFT JOIN PelículaGénero pg ON p.Id = pg.IdPelícula
                    WHERE {where_clause}
                        AND f.Activo = 1
                    GROUP BY f.Id, f.FechaHora, {agrupacion_sql}
                ),
                BoletosVendidos AS (
                    SELECT 
                        f.Id AS FuncionId,
                        COUNT(b.Id) AS BoletosVendidos
                    FROM Funciones f
                    INNER JOIN Salas s ON f.IdSala = s.Id
                    INNER JOIN Películas p ON f.IdPelícula = p.Id
                    LEFT JOIN PelículaGénero pg ON p.Id = pg.IdPelícula
                    INNER JOIN Boletos b ON f.Id = b.IdFunción
                    LEFT JOIN BoletosCancelados bc ON b.Id = bc.IdBoleto
                    WHERE {where_clause}
                        AND f.Activo = 1
                        AND bc.Id IS NULL
                    GROUP BY f.Id
                )
                SELECT 
                    cf.Periodo,
                    SUM(cf.CapacidadTotal) AS CapacidadTotal,
                    SUM(ISNULL(bv.BoletosVendidos, 0)) AS BoletosVendidos,
                    CASE 
                        WHEN SUM(cf.CapacidadTotal) > 0 
                        THEN (SUM(ISNULL(bv.BoletosVendidos, 0)) * 100.0 / SUM(cf.CapacidadTotal))
                        ELSE 0 
                    END AS PorcentajeOcupacion
                FROM CapacidadFunciones cf
                LEFT JOIN BoletosVendidos bv ON cf.FuncionId = bv.FuncionId
                GROUP BY cf.Periodo
                ORDER BY cf.Periodo
            """)
            
            result = session.execute(query)
            datos = []
            
            for row in result:
                datos.append({
                    'Periodo': row.Periodo.isoformat() if hasattr(row.Periodo, 'isoformat') else str(row.Periodo),
                    'CapacidadTotal': row.CapacidadTotal or 0,
                    'BoletosVendidos': row.BoletosVendidos or 0,
                    'PorcentajeOcupacion': float(row.PorcentajeOcupacion) if row.PorcentajeOcupacion else 0.0
                })
            
            return datos
            
        except Exception as e:
            print(f"Error en obtener_ocupacion: {e}")
            traceback.print_exc()
            return []
        finally:
            session.close()
    
    @staticmethod
    def obtener_boletos_usados(filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Obtiene porcentaje de boletos usados por período"""
        session = db.get_session()
        try:
            where_clause = DashboardController.construir_filtros_sql(filtros)
            agrupacion_sql = DashboardController.obtener_agrupacion_sql(filtros.get('agrupacion', 'dia'))
            
            query = text(f"""
                WITH BoletosTotales AS (
                    SELECT 
                        f.Id AS FuncionId,
                        f.FechaHora,
                        {agrupacion_sql} AS Periodo,
                        COUNT(b.Id) AS BoletosTotales,
                        COUNT(bu.Id) AS BoletosUsados
                    FROM Funciones f
                    INNER JOIN Salas s ON f.IdSala = s.Id
                    INNER JOIN Películas p ON f.IdPelícula = p.Id
                    LEFT JOIN PelículaGénero pg ON p.Id = pg.IdPelícula
                    INNER JOIN Boletos b ON f.Id = b.IdFunción
                    LEFT JOIN BoletosCancelados bc ON b.Id = bc.IdBoleto
                    LEFT JOIN BoletosUsados bu ON b.Id = bu.IdBoleto
                    WHERE {where_clause}
                        AND f.Activo = 1
                        AND bc.Id IS NULL
                    GROUP BY f.Id, f.FechaHora, {agrupacion_sql}
                )
                SELECT 
                    Periodo,
                    SUM(BoletosTotales) AS BoletosTotales,
                    SUM(BoletosUsados) AS BoletosUsados,
                    CASE 
                        WHEN SUM(BoletosTotales) > 0 
                        THEN (SUM(BoletosUsados) * 100.0 / SUM(BoletosTotales))
                        ELSE 0 
                    END AS PorcentajeUsados
                FROM BoletosTotales
                GROUP BY Periodo
                ORDER BY Periodo
            """)
            
            result = session.execute(query)
            datos = []
            
            for row in result:
                datos.append({
                    'Periodo': row.Periodo.isoformat() if hasattr(row.Periodo, 'isoformat') else str(row.Periodo),
                    'BoletosTotales': row.BoletosTotales or 0,
                    'BoletosUsados': row.BoletosUsados or 0,
                    'PorcentajeUsados': float(row.PorcentajeUsados) if row.PorcentajeUsados else 0.0
                })
            
            return datos
            
        except Exception as e:
            print(f"Error en obtener_boletos_usados: {e}")
            traceback.print_exc()
            return []
        finally:
            session.close()
    
    @staticmethod
    def obtener_cancelaciones(filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Obtiene porcentaje de cancelaciones por período"""
        session = db.get_session()
        try:
            where_clause = DashboardController.construir_filtros_sql(filtros)
            agrupacion_sql = DashboardController.obtener_agrupacion_sql(filtros.get('agrupacion', 'dia'))
            
            query = text(f"""
                WITH BoletosVendidos AS (
                    SELECT 
                        f.Id AS FuncionId,
                        f.FechaHora,
                        {agrupacion_sql} AS Periodo,
                        COUNT(b.Id) AS BoletosVendidos,
                        COUNT(bc.Id) AS BoletosCancelados
                    FROM Funciones f
                    INNER JOIN Salas s ON f.IdSala = s.Id
                    INNER JOIN Películas p ON f.IdPelícula = p.Id
                    LEFT JOIN PelículaGénero pg ON p.Id = pg.IdPelícula
                    INNER JOIN Boletos b ON f.Id = b.IdFunción
                    LEFT JOIN BoletosCancelados bc ON b.Id = bc.IdBoleto
                    WHERE {where_clause}
                        AND f.Activo = 1
                    GROUP BY f.Id, f.FechaHora, {agrupacion_sql}
                )
                SELECT 
                    Periodo,
                    SUM(BoletosVendidos) AS BoletosVendidos,
                    SUM(BoletosCancelados) AS BoletosCancelados,
                    CASE 
                        WHEN SUM(BoletosVendidos) > 0 
                        THEN (SUM(BoletosCancelados) * 100.0 / SUM(BoletosVendidos))
                        ELSE 0 
                    END AS PorcentajeCancelaciones
                FROM BoletosVendidos
                GROUP BY Periodo
                ORDER BY Periodo
            """)
            
            result = session.execute(query)
            datos = []
            
            for row in result:
                datos.append({
                    'Periodo': row.Periodo.isoformat() if hasattr(row.Periodo, 'isoformat') else str(row.Periodo),
                    'BoletosVendidos': row.BoletosVendidos or 0,
                    'BoletosCancelados': row.BoletosCancelados or 0,
                    'PorcentajeCancelaciones': float(row.PorcentajeCancelaciones) if row.PorcentajeCancelaciones else 0.0
                })
            
            return datos
            
        except Exception as e:
            print(f"Error en obtener_cancelaciones: {e}")
            traceback.print_exc()
            return []
        finally:
            session.close()
    
    @staticmethod
    def obtener_datos_completos(filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene todos los datos del dashboard en un solo llamado"""
        try:
            ingresos = DashboardController.obtener_ingresos(filtros)
            ocupacion = DashboardController.obtener_ocupacion(filtros)
            boletos_usados = DashboardController.obtener_boletos_usados(filtros)
            cancelaciones = DashboardController.obtener_cancelaciones(filtros)
            
            return {
                'ingresos': ingresos,
                'ocupacion': ocupacion,
                'boletos_usados': boletos_usados,
                'cancelaciones': cancelaciones,
                'filtros': filtros
            }
            
        except Exception as e:
            print(f"Error en obtener_datos_completos: {e}")
            traceback.print_exc()
            return {
                'ingresos': [],
                'ocupacion': [],
                'boletos_usados': [],
                'cancelaciones': [],
                'filtros': filtros
            }
    
    @staticmethod
    def obtener_datos_raw(filtros: Dict[str, Any]) -> pd.DataFrame:
        """Obtiene datos sin procesar para exportación a Excel"""
        session = db.get_session()
        try:
            where_clause = DashboardController.construir_filtros_sql(filtros)
            
            query = text(f"""
                SELECT 
                    f.Id AS FuncionId,
                    f.FechaHora,
                    c.Cine,
                    c.Dirección AS DireccionCine,
                    s.NúmeroDeSala,
                    ts.Tipo AS TipoSala,
                    p.TítuloPelícula AS Pelicula,
                    cl.Clasificación,
                    i.Idioma,
                    g.Género,
                    b.Id AS BoletoId,
                    b.FechaCreacion,
                    tb.TipoBoleto,
                    b.ValorPagado,
                    CASE WHEN bc.Id IS NOT NULL THEN 1 ELSE 0 END AS Cancelado,
                    bc.FechaCancelacion,
                    bc.ValorAcreditado,
                    CASE WHEN bu.Id IS NOT NULL THEN 1 ELSE 0 END AS Usado,
                    bu.FechaUso,
                    u.Nombre + ' ' + u.Apellidos AS Cliente,
                    a.CódigoAsiento
                FROM Funciones f
                INNER JOIN Salas s ON f.IdSala = s.Id
                INNER JOIN Cines c ON s.IdCine = c.Id
                INNER JOIN TipoDeSala ts ON s.IdTipo = ts.Id
                INNER JOIN Películas p ON f.IdPelícula = p.Id
                INNER JOIN Clasificaciones cl ON p.IdClasificación = cl.Id
                INNER JOIN Idiomas i ON p.IdIdioma = i.Id
                LEFT JOIN PelículaGénero pg ON p.Id = pg.IdPelícula
                LEFT JOIN Géneros g ON pg.IdGénero = g.Id
                LEFT JOIN Boletos b ON f.Id = b.IdFunción
                LEFT JOIN TipoBoletos tb ON b.IdTipoBoleto = tb.Id
                LEFT JOIN BoletosCancelados bc ON b.Id = bc.IdBoleto
                LEFT JOIN BoletosUsados bu ON b.Id = bu.IdBoleto
                LEFT JOIN Usuarios u ON b.IdUsuario = u.Id
                LEFT JOIN Asientos a ON b.IdAsiento = a.Id
                WHERE {where_clause}
                    AND f.Activo = 1
                ORDER BY f.FechaHora, c.Cine, s.NúmeroDeSala
            """)
            
            result = session.execute(query)
            columns = result.keys()
            data = result.fetchall()
            
            df = pd.DataFrame(data, columns=columns)
            return df
            
        except Exception as e:
            print(f"Error en obtener_datos_raw: {e}")
            traceback.print_exc()
            return pd.DataFrame()
        finally:
            session.close()
    
    @staticmethod
    def generar_excel(filtros: Dict[str, Any]) -> BytesIO:
        """Genera archivo Excel con datos del dashboard"""
        try:
            # Obtener datos raw
            df_raw = DashboardController.obtener_datos_raw(filtros)
            
            # Obtener datos agregados
            datos_completos = DashboardController.obtener_datos_completos(filtros)
            
            # Crear buffer para Excel
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Hoja 1: Datos detallados
                if not df_raw.empty:
                    df_raw.to_excel(writer, sheet_name='Datos_Detallados', index=False)
                
                # Hoja 2: Resumen de ingresos
                if datos_completos['ingresos']:
                    df_ingresos = pd.DataFrame(datos_completos['ingresos'])
                    df_ingresos.to_excel(writer, sheet_name='Resumen_Ingresos', index=False)
                
                # Hoja 3: Resumen de ocupación
                if datos_completos['ocupacion']:
                    df_ocupacion = pd.DataFrame(datos_completos['ocupacion'])
                    df_ocupacion.to_excel(writer, sheet_name='Resumen_Ocupacion', index=False)
                
                # Hoja 4: Resumen de boletos usados
                if datos_completos['boletos_usados']:
                    df_usados = pd.DataFrame(datos_completos['boletos_usados'])
                    df_usados.to_excel(writer, sheet_name='Resumen_Boletos_Usados', index=False)
                
                # Hoja 5: Resumen de cancelaciones
                if datos_completos['cancelaciones']:
                    df_cancel = pd.DataFrame(datos_completos['cancelaciones'])
                    df_cancel.to_excel(writer, sheet_name='Resumen_Cancelaciones', index=False)
                
                # Hoja 6: Metadatos y filtros
                filtros_info = {
                    'Parámetro': [
                        'Fecha de generación',
                        'Fecha inicio',
                        'Fecha fin',
                        'Agrupación',
                        'Cines seleccionados',
                        'Géneros seleccionados',
                        'Películas seleccionadas',
                        'Funciones seleccionadas',
                        'Días de semana'
                    ],
                    'Valor': [
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        filtros.get('fecha_inicio', 'No especificado'),
                        filtros.get('fecha_fin', 'No especificado'),
                        filtros.get('agrupacion', 'día').capitalize(),
                        len(filtros.get('cine_ids', [])),
                        len(filtros.get('genero_ids', [])),
                        len(filtros.get('pelicula_ids', [])),
                        len(filtros.get('funcion_ids', [])),
                        len(filtros.get('dias_semana', []))
                    ]
                }
                
                df_metadatos = pd.DataFrame(filtros_info)
                df_metadatos.to_excel(writer, sheet_name='Metadatos', index=False)
            
            output.seek(0)
            return output
            
        except Exception as e:
            print(f"Error en generar_excel: {e}")
            traceback.print_exc()
            raise
    
    @staticmethod
    def generar_pdf(datos_dashboard: Dict[str, Any], filtros: Dict[str, Any]) -> BytesIO:
        """Genera PDF con reporte del dashboard"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Título
            titulo = Paragraph("Reporte del Dashboard - CineFlow", styles['Title'])
            elements.append(titulo)
            elements.append(Spacer(1, 12))
            
            # Fecha de generación
            fecha_gen = Paragraph(
                f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
                styles['Normal']
            )
            elements.append(fecha_gen)
            elements.append(Spacer(1, 20))
            
            # Sección de filtros aplicados
            filtros_titulo = Paragraph("Filtros Aplicados", styles['Heading2'])
            elements.append(filtros_titulo)
            
            filtros_data = [
                ["Parámetro", "Valor"],
                ["Fecha Inicio", filtros.get('fecha_inicio', 'No especificado')],
                ["Fecha Fin", filtros.get('fecha_fin', 'No especificado')],
                ["Agrupación", filtros.get('agrupacion', 'día').capitalize()],
                ["Cines", f"{len(filtros.get('cine_ids', []))} seleccionados"],
                ["Géneros", f"{len(filtros.get('genero_ids', []))} seleccionados"],
                ["Películas", f"{len(filtros.get('pelicula_ids', []))} seleccionados"],
                ["Funciones", f"{len(filtros.get('funcion_ids', []))} seleccionados"],
                ["Días de semana", f"{len(filtros.get('dias_semana', []))} seleccionados"]
            ]
            
            filtros_table = Table(filtros_data, colWidths=[200, 300])
            filtros_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(filtros_table)
            elements.append(Spacer(1, 30))
            
            # Sección de métricas
            metricas_titulo = Paragraph("Métricas del Dashboard", styles['Heading2'])
            elements.append(metricas_titulo)
            elements.append(Spacer(1, 15))
            
            # Ingresos
            ingresos_titulo = Paragraph("1. Ingresos por Boletos", styles['Heading3'])
            elements.append(ingresos_titulo)
            
            if datos_dashboard.get('ingresos') and datos_dashboard['ingresos']:
                ingresos_data = [["Periodo", "Ingresos ($)", "Boletos Vendidos"]]
                for item in datos_dashboard['ingresos']:
                    ingresos_data.append([
                        str(item.get('Periodo', '')),
                        f"${item.get('Ingresos', 0):,.2f}",
                        str(item.get('BoletosVendidos', 0))
                    ])
                
                ingresos_table = Table(ingresos_data, colWidths=[150, 100, 100])
                ingresos_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(ingresos_table)
                elements.append(Spacer(1, 15))
            else:
                elements.append(Paragraph("No hay datos de ingresos disponibles.", styles['Normal']))
                elements.append(Spacer(1, 15))
            
            # Ocupación
            ocupacion_titulo = Paragraph("2. Ocupación de Salas (%)", styles['Heading3'])
            elements.append(ocupacion_titulo)
            
            if datos_dashboard.get('ocupacion') and datos_dashboard['ocupacion']:
                ocupacion_data = [["Periodo", "Capacidad Total", "Boletos Vendidos", "Ocupación %"]]
                for item in datos_dashboard['ocupacion']:
                    ocupacion_data.append([
                        str(item.get('Periodo', '')),
                        str(item.get('CapacidadTotal', 0)),
                        str(item.get('BoletosVendidos', 0)),
                        f"{item.get('PorcentajeOcupacion', 0):.2f}%"
                    ])
                
                ocupacion_table = Table(ocupacion_data, colWidths=[150, 100, 100, 80])
                ocupacion_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(ocupacion_table)
                elements.append(Spacer(1, 15))
            else:
                elements.append(Paragraph("No hay datos de ocupación disponibles.", styles['Normal']))
                elements.append(Spacer(1, 15))
            
            # Boletos Usados
            usados_titulo = Paragraph("3. Boletos Usados (%)", styles['Heading3'])
            elements.append(usados_titulo)
            
            if datos_dashboard.get('boletos_usados') and datos_dashboard['boletos_usados']:
                usados_data = [["Periodo", "Boletos Totales", "Boletos Usados", "Porcentaje %"]]
                for item in datos_dashboard['boletos_usados']:
                    usados_data.append([
                        str(item.get('Periodo', '')),
                        str(item.get('BoletosTotales', 0)),
                        str(item.get('BoletosUsados', 0)),
                        f"{item.get('PorcentajeUsados', 0):.2f}%"
                    ])
                
                usados_table = Table(usados_data, colWidths=[150, 100, 100, 80])
                usados_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightyellow),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(usados_table)
                elements.append(Spacer(1, 15))
            else:
                elements.append(Paragraph("No hay datos de boletos usados disponibles.", styles['Normal']))
                elements.append(Spacer(1, 15))
            
            # Cancelaciones
            cancel_titulo = Paragraph("4. Cancelaciones (%)", styles['Heading3'])
            elements.append(cancel_titulo)
            
            if datos_dashboard.get('cancelaciones') and datos_dashboard['cancelaciones']:
                cancel_data = [["Periodo", "Boletos Vendidos", "Boletos Cancelados", "Porcentaje %"]]
                for item in datos_dashboard['cancelaciones']:
                    cancel_data.append([
                        str(item.get('Periodo', '')),
                        str(item.get('BoletosVendidos', 0)),
                        str(item.get('BoletosCancelados', 0)),
                        f"{item.get('PorcentajeCancelaciones', 0):.2f}%"
                    ])
                
                cancel_table = Table(cancel_data, colWidths=[150, 100, 100, 80])
                cancel_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightcoral),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(cancel_table)
            else:
                elements.append(Paragraph("No hay datos de cancelaciones disponibles.", styles['Normal']))
            
            # Construir PDF
            doc.build(elements)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            print(f"Error en generar_pdf: {e}")
            traceback.print_exc()
            raise