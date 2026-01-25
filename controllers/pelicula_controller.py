# controllers/pelicula_controller.py
# Controlador para operaciones de películas

from models import Pelicula, Funcion, Boleto, PeliculaGenero, Genero, Sala, TipoSala, Idioma, Clasificacion
from database import db
from sqlalchemy import desc, func
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
import traceback

class PeliculaController:
    """Controlador para operaciones de películas"""

    def __init__(self):
        pass


    @staticmethod
    def ultimas_3_pelis():
        """
        Obtiene las últimas 3 películas registradas que están disponibles en cartelera
        
        Returns:
            list: Lista de diccionarios con información de películas
        """
        session = db.get_session()
        try:
            # Primero obtenemos todas las películas en cartelera usando el método existente
            resultado_cartelera = PeliculaController.filtrar_pelis_cartelera()
            peliculas_cartelera = resultado_cartelera.get('peliculas', [])
            
            if not peliculas_cartelera:
                return []
            
            # Ordenamos por ID descendente (las más recientes primero)
            peliculas_cartelera.sort(key=lambda x: x['id'], reverse=True)
            
            # Tomamos las primeras 3
            ultimas_3 = peliculas_cartelera[:3]
            
            # Para mantener compatibilidad con el formato esperado,
            # agregamos información adicional si es necesario
            for pelicula in ultimas_3:
                # Ya obtenemos la próxima función desde el método filtrar_pelis_cartelera
                # Si necesitamos más datos específicos, los agregamos aquí
                pass
                
            return ultimas_3
            
        except Exception as e:
            print(f"Error al obtener últimas películas: {e}")
            traceback.print_exc()
            return []
        finally:
            session.close()


    @staticmethod
    def top_3_pelis():
        """
        Obtiene las 3 películas más populares basadas en ventas de boletos
        que están disponibles en cartelera
        
        Returns:
            list: Lista de diccionarios con información de películas
        """
        session = db.get_session()
        try:
            # Primero obtenemos todas las películas en cartelera
            resultado_cartelera = PeliculaController.filtrar_pelis_cartelera()
            peliculas_cartelera = resultado_cartelera.get('peliculas', [])
            
            if not peliculas_cartelera:
                return PeliculaController.ultimas_3_pelis()
            
            # Extraemos los IDs de las películas en cartelera
            peliculas_cartelera_ids = [p['id'] for p in peliculas_cartelera]
            
            # Subconsulta para contar boletos SOLO de películas en cartelera
            subquery = session.query(
                Funcion.IdPelicula,
                func.count(Boleto.Id).label('total_boletos')
            ).join(Boleto, Funcion.Id == Boleto.IdFuncion
            ).filter(
                Funcion.Activo == True,
                Funcion.IdPelicula.in_(peliculas_cartelera_ids),
                Funcion.FechaHora > datetime.now()
            ).group_by(Funcion.IdPelicula).subquery()

            # Obtenemos las películas con más boletos vendidos
            peliculas_populares = session.query(
                Pelicula.Id,
                func.coalesce(subquery.c.total_boletos, 0).label('total_boletos')
            ).outerjoin(subquery, Pelicula.Id == subquery.c.IdPelicula
            ).filter(
                Pelicula.Activo == True,
                Pelicula.Id.in_(peliculas_cartelera_ids)
            ).order_by(desc(func.coalesce(subquery.c.total_boletos, 0))).limit(3).all()

            resultado = []
            for pelicula_id, total_boletos in peliculas_populares:
                # Buscamos la información completa de la película en nuestros datos ya filtrados
                pelicula_info = next((p for p in peliculas_cartelera if p['id'] == pelicula_id), None)
                
                if not pelicula_info:
                    continue
                    
                # Enriquecer con información adicional si es necesario
                pelicula_info['total_boletos'] = total_boletos or 0
                pelicula_info['popularidad'] = PeliculaController._calcular_popularidad(total_boletos or 0)
                
                resultado.append(pelicula_info)
            
            # Si no hay películas con boletos, devolver las últimas 3 en cartelera
            if not resultado:
                return PeliculaController.ultimas_3_pelis()
                
            return resultado
            
        except Exception as e:
            print(f"Error al obtener películas populares: {e}")
            traceback.print_exc()
            return PeliculaController.ultimas_3_pelis()
        finally:
            session.close()

    @staticmethod
    def _calcular_popularidad(total_boletos):
        """
        Calcula el nivel de popularidad basado en ventas de boletos
        
        Args:
            total_boletos (int): Cantidad total de boletos vendidos
            
        Returns:
            str: Nivel de popularidad (Alta, Media, Baja)
        """
        if total_boletos > 100:
            return "Alta"
        elif total_boletos > 50:
            return "Media"
        else:
            return "Baja"


    @staticmethod
    def obtener_por_id(pelicula_id):
        """
        Obtiene una película por su ID
        
        Args:
            pelicula_id (int): ID de la película
            
        Returns:
            dict: Diccionario con información de la película o None
        """
        session = db.get_session()
        try:
            pelicula = session.query(Pelicula).options(
                joinedload(Pelicula.clasificacion),
                joinedload(Pelicula.idioma),
                joinedload(Pelicula.generos).joinedload(PeliculaGenero.genero)
            ).filter(Pelicula.Id == pelicula_id).first()
            
            if pelicula:
                generos = [pg.genero.Genero for pg in pelicula.generos]
                
                pelicula_dict = {
                    'id': pelicula.Id,
                    'titulo': pelicula.Titulo,
                    'descripcion_corta': pelicula.DescripcionCorta,
                    'descripcion_larga': pelicula.DescripcionLarga,
                    'duracion_minutos': pelicula.DuracionMinutos,
                    'generos': generos,
                    'clasificacion': pelicula.clasificacion.Clasificacion if pelicula.clasificacion else None,
                    'idioma': pelicula.idioma.Idioma if pelicula.idioma else None,
                    'link_to_banner': pelicula.LinkToBanner,
                    'link_to_bajante': pelicula.LinkToBajante,
                    'link_to_trailer': pelicula.LinkToTrailer
                }
                
                session.expunge(pelicula)
                return pelicula_dict
                
            return None
            
        except Exception as e:
            print(f"Error al obtener película: {e}")
            return None
        finally:
            session.close()

    @staticmethod
    def filtrar_pelis_cartelera(dia=None, genero_list=None, sala_tipo_list=None, 
                                idioma_list=None, clasificacion_list=None):
        """
        Filtra películas para la cartelera basándose en los criterios proporcionados.
        Lógica: OR dentro de cada categoría, AND entre categorías.
        
        Args:
            dia (str, opcional): Fecha en formato 'YYYY-MM-DD'. 
                Por defecto es hoy o mañana si no hay funciones activas hoy.
            genero_list (list, opcional): Lista de IDs de géneros (OR).
            sala_tipo_list (list, opcional): Lista de IDs de tipos de sala (OR).
            idioma_list (list, opcional): Lista de IDs de idiomas (OR).
            clasificacion_list (list, opcional): Lista de IDs de clasificaciones (OR).
            
        Returns:
            dict: Diccionario con películas filtradas y metadatos
        """
        
        session = db.get_session()
        try:
            # 1. Determinar la fecha base para el filtro
            ahora = datetime.now()
            
            if dia:
                # Si se proporciona una fecha específica
                fecha_filtro = datetime.strptime(dia, '%Y-%m-%d').date()
            else:
                # Por defecto: hoy
                fecha_hoy = ahora.date()
                
                # Verificar si hay funciones hoy después de la hora actual
                funciones_hoy = session.query(Funcion).filter(
                    Funcion.FechaHora >= ahora,
                    Funcion.FechaHora < fecha_hoy + timedelta(days=1),
                    Funcion.Activo == True
                ).first()
                
                if funciones_hoy:
                    fecha_filtro = fecha_hoy
                else:
                    # No hay funciones hoy, usar mañana
                    fecha_filtro = fecha_hoy + timedelta(days=1)
            
            # Rango de fechas: desde fecha_filtro hasta +12 días
            fecha_fin = fecha_filtro + timedelta(days=12)
            
            # Convertir a datetime para la consulta
            fecha_inicio_dt = datetime.combine(fecha_filtro, datetime.min.time())
            fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time())
            
            # 2. Construir la consulta base
            query = session.query(Pelicula).options(
                joinedload(Pelicula.clasificacion),
                joinedload(Pelicula.idioma),
                joinedload(Pelicula.generos).joinedload(PeliculaGenero.genero)
            ).filter(
                Pelicula.Activo == True
            )
            
            # 3. Subconsulta para películas con funciones en el rango de fechas
            subquery_funciones = session.query(Funcion.IdPelicula).filter(
                Funcion.FechaHora >= fecha_inicio_dt,
                Funcion.FechaHora <= fecha_fin_dt,
                Funcion.Activo == True
            ).distinct().subquery()
            
            query = query.join(subquery_funciones, Pelicula.Id == subquery_funciones.c.IdPelicula)
            
            # 4. Aplicar filtros con lógica OR dentro de cada categoría
            
            # GÉNEROS (OR) - Películas que tengan AL MENOS UNO de los géneros seleccionados
            if genero_list and len(genero_list) > 0:
                subquery_genero = session.query(PeliculaGenero.IdPelicula).filter(
                    PeliculaGenero.IdGenero.in_(genero_list)
                ).distinct().subquery()
                query = query.join(subquery_genero, Pelicula.Id == subquery_genero.c.IdPelicula)
            
            # TIPO DE SALA (OR) - Películas con funciones en AL MENOS UNO de los tipos de sala
            if sala_tipo_list and len(sala_tipo_list) > 0:
                subquery_sala = session.query(Funcion.IdPelicula).join(
                    Sala, Funcion.IdSala == Sala.Id
                ).join(
                    TipoSala, Sala.IdTipo == TipoSala.Id
                ).filter(
                    TipoSala.Id.in_(sala_tipo_list),
                    Funcion.FechaHora >= fecha_inicio_dt,
                    Funcion.FechaHora <= fecha_fin_dt,
                    Funcion.Activo == True
                ).distinct().subquery()
                query = query.join(subquery_sala, Pelicula.Id == subquery_sala.c.IdPelicula)
            
            # IDIOMA (OR) - Películas en AL MENOS UNO de los idiomas seleccionados
            if idioma_list and len(idioma_list) > 0:
                query = query.filter(Pelicula.IdIdioma.in_(idioma_list))
            
            # CLASIFICACIÓN (OR) - Películas con AL MENOS UNA de las clasificaciones
            if clasificacion_list and len(clasificacion_list) > 0:
                query = query.filter(Pelicula.IdClasificacion.in_(clasificacion_list))
            
            # 5. Ordenar por título y obtener resultados
            query = query.order_by(Pelicula.Titulo).distinct()
            peliculas = query.all()
            
            # 6. Obtener los tipos de sala por película (CON IDs)
            tipos_sala_por_pelicula = {}
            tipos_sala_ids_por_pelicula = {}
            
            if peliculas:
                pelicula_ids = [p.Id for p in peliculas]
                
                # Consulta para obtener los tipos de sala por película
                resultados_tipos_sala = session.query(
                    Funcion.IdPelicula,
                    TipoSala.Id,
                    TipoSala.Tipo
                ).join(
                    Sala, Funcion.IdSala == Sala.Id
                ).join(
                    TipoSala, Sala.IdTipo == TipoSala.Id
                ).filter(
                    Funcion.IdPelicula.in_(pelicula_ids),
                    Funcion.FechaHora >= fecha_inicio_dt,
                    Funcion.FechaHora <= fecha_fin_dt,
                    Funcion.Activo == True
                ).distinct().all()
                
                for id_pelicula, id_tipo_sala, tipo_sala_nombre in resultados_tipos_sala:
                    # Guardar nombres para mostrar
                    if id_pelicula not in tipos_sala_por_pelicula:
                        tipos_sala_por_pelicula[id_pelicula] = []
                    tipos_sala_por_pelicula[id_pelicula].append(tipo_sala_nombre)
                    
                    # Guardar IDs para filtrado
                    if id_pelicula not in tipos_sala_ids_por_pelicula:
                        tipos_sala_ids_por_pelicula[id_pelicula] = []
                    tipos_sala_ids_por_pelicula[id_pelicula].append(id_tipo_sala)
            
            # 7. Formatear resultados
            peliculas_filtradas = []
            for pelicula in peliculas:
                generos = [pg.genero.Genero for pg in pelicula.generos]
                
                pelicula_dict = {
                    'id': pelicula.Id,
                    'titulo': pelicula.Titulo,
                    'descripcion_corta': pelicula.DescripcionCorta,
                    'descripcion_larga': pelicula.DescripcionLarga,
                    'duracion_minutos': pelicula.DuracionMinutos,
                    'generos': generos,
                    'clasificacion': pelicula.clasificacion.Clasificacion if pelicula.clasificacion else None,
                    'idioma': pelicula.idioma.Idioma if pelicula.idioma else None,
                    'link_to_banner': pelicula.LinkToBanner,
                    'link_to_bajante': pelicula.LinkToBajante,
                    'link_to_trailer': pelicula.LinkToTrailer,
                    'salas_tipos': tipos_sala_por_pelicula.get(pelicula.Id, []),
                    'salas_tipos_ids': tipos_sala_ids_por_pelicula.get(pelicula.Id, [])
                }
                
                peliculas_filtradas.append(pelicula_dict)
                session.expunge(pelicula)
            
            # 8. Preparar respuesta con metadatos
            hoy = datetime.now().date()
            fecha_minima = hoy
            fecha_maxima = hoy + timedelta(days=12)
            
            if dia:
                try:
                    fecha_seleccionada = datetime.strptime(dia, '%Y-%m-%d').date()
                    if fecha_seleccionada < fecha_minima:
                        fecha_seleccionada = fecha_minima
                    elif fecha_seleccionada > fecha_maxima:
                        fecha_seleccionada = fecha_maxima
                except ValueError:
                    fecha_seleccionada = hoy
            else:
                fecha_seleccionada = hoy
            
            return {
                'peliculas': peliculas_filtradas,
                'fecha_seleccionada': fecha_seleccionada.strftime('%Y-%m-%d'),
                'fecha_minima': fecha_minima.strftime('%Y-%m-%d'),
                'fecha_maxima': fecha_maxima.strftime('%Y-%m-%d'),
                'fecha_mostrada': fecha_filtro.strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            print(f"Error al filtrar películas para cartelera: {e}")
            traceback.print_exc()
            
            return {
                'peliculas': [],
                'fecha_seleccionada': datetime.now().date().strftime('%Y-%m-%d'),
                'fecha_minima': datetime.now().date().strftime('%Y-%m-%d'),
                'fecha_maxima': (datetime.now().date() + timedelta(days=12)).strftime('%Y-%m-%d'),
                'fecha_mostrada': datetime.now().date().strftime('%Y-%m-%d')
            }
        finally:
            session.close()

    @staticmethod
    def obtener_opciones_filtros_por_fecha(resultado_cartelera):
        """
        Obtiene opciones de filtro basadas en las películas ya obtenidas.
        Extrae los IDs reales desde los datos de películas para evitar consultas adicionales.
        
        Args:
            resultado_cartelera (dict): Resultado del método filtrar_pelis_cartelera
                
        Returns:
            dict: Diccionario con las opciones de filtro disponibles
        """
        peliculas_filtradas = resultado_cartelera.get('peliculas', [])
        
        # Si no hay películas, retornar listas vacías
        if not peliculas_filtradas:
            return {
                'generos': [],
                'salas': [],
                'idiomas': [],
                'clasificaciones': []
            }
        
        session = db.get_session()
        try:
            # Paso 1: Recopilar nombres únicos e IDs de las películas filtradas
            generos_nombres = set()
            idiomas_nombres = set()
            clasificaciones_nombres = set()
            salas_ids = set()  # Aquí guardamos los IDs directamente
            
            for pelicula in peliculas_filtradas:
                # Recopilar géneros
                for genero in pelicula.get('generos', []):
                    generos_nombres.add(genero)
                
                # Recopilar idiomas
                if pelicula.get('idioma'):
                    idiomas_nombres.add(pelicula['idioma'])
                
                # Recopilar clasificaciones
                if pelicula.get('clasificacion'):
                    clasificaciones_nombres.add(pelicula['clasificacion'])
                
                # Recopilar IDs de tipos de sala
                for sala_id in pelicula.get('salas_tipos_ids', []):
                    salas_ids.add(sala_id)
            
            # Paso 2: Consultar la BD para obtener objetos con IDs reales
            
            # Obtener géneros
            generos_objs = []
            if generos_nombres:
                generos_objs = session.query(Genero).filter(
                    Genero.Genero.in_(generos_nombres),
                    Genero.Activo == True
                ).order_by(Genero.Genero).all()
            
            # Obtener idiomas
            idiomas_objs = []
            if idiomas_nombres:
                idiomas_objs = session.query(Idioma).filter(
                    Idioma.Idioma.in_(idiomas_nombres),
                    Idioma.Activo == True
                ).order_by(Idioma.Idioma).all()
            
            # Obtener clasificaciones
            clasificaciones_objs = []
            if clasificaciones_nombres:
                clasificaciones_objs = session.query(Clasificacion).filter(
                    Clasificacion.Clasificacion.in_(clasificaciones_nombres),
                    Clasificacion.Activo == True
                ).order_by(Clasificacion.Clasificacion).all()
            
            # Obtener tipos de sala usando los IDs que ya tenemos
            salas_objs = []
            if salas_ids:
                salas_objs = session.query(TipoSala).filter(
                    TipoSala.Id.in_(salas_ids),
                    TipoSala.Activo == True
                ).order_by(TipoSala.Tipo).all()
            
            return {
                'generos': generos_objs,
                'salas': salas_objs,
                'idiomas': idiomas_objs,
                'clasificaciones': clasificaciones_objs
            }
            
        except Exception as e:
            print(f"Error al obtener opciones de filtros: {e}")
            traceback.print_exc()
            
            return {
                'generos': [],
                'salas': [],
                'idiomas': [],
                'clasificaciones': []
            }
        finally:
            session.close()

    @staticmethod
    def convertir_parametros_filtro(parametros):
        """
        Convierte listas de strings de parámetros a listas de enteros.
        
        Args:
            parametros (list): Lista de strings de parámetros
            
        Returns:
            list: Lista de enteros válidos (o lista vacía si no hay parámetros válidos)
        """
        resultado = []
        if not parametros:
            return resultado
            
        for param in parametros:
            if param and str(param).strip().isdigit():
                resultado.append(int(param))
        return resultado

    @staticmethod
    def filtrar_pelis_prox(genero_list=None, idioma_list=None, clasificacion_list=None):
        """
        Filtra películas que tienen funciones programadas para dentro de 13 días o más.
        
        Args:
            genero_list (list, opcional): Lista de IDs de géneros (OR).
            idioma_list (list, opcional): Lista de IDs de idiomas (OR).
            clasificacion_list (list, opcional): Lista de IDs de clasificaciones (OR).
            
        Returns:
            list: Lista de diccionarios con información de películas próximas
        """
        
        session = db.get_session()
        try:
            # Fecha actual
            ahora = datetime.now()
            # Fecha mínima para considerarse "próximamente": 13 días a partir de ahora
            fecha_minima = ahora + timedelta(days=13)
            
            # 1. Construir la consulta base
            query = session.query(Pelicula).options(
                joinedload(Pelicula.clasificacion),
                joinedload(Pelicula.idioma),
                joinedload(Pelicula.generos).joinedload(PeliculaGenero.genero)
            ).filter(
                Pelicula.Activo == True
            )
            
            # 2. Subconsulta para películas con funciones futuras (13+ días)
            subquery_funciones = session.query(Funcion.IdPelicula).filter(
                Funcion.FechaHora >= fecha_minima,
                Funcion.Activo == True
            ).distinct().subquery()
            
            query = query.join(subquery_funciones, Pelicula.Id == subquery_funciones.c.IdPelicula)
            
            # 3. Aplicar filtros con lógica OR dentro de cada categoría
            
            # GÉNEROS (OR) - Películas que tengan AL MENOS UNO de los géneros seleccionados
            if genero_list and len(genero_list) > 0:
                subquery_genero = session.query(PeliculaGenero.IdPelicula).filter(
                    PeliculaGenero.IdGenero.in_(genero_list)
                ).distinct().subquery()
                query = query.join(subquery_genero, Pelicula.Id == subquery_genero.c.IdPelicula)
            
            # IDIOMA (OR) - Películas en AL MENOS UNO de los idiomas seleccionados
            if idioma_list and len(idioma_list) > 0:
                query = query.filter(Pelicula.IdIdioma.in_(idioma_list))
            
            # CLASIFICACIÓN (OR) - Películas con AL MENOS UNA de las clasificaciones
            if clasificacion_list and len(clasificacion_list) > 0:
                query = query.filter(Pelicula.IdClasificacion.in_(clasificacion_list))
            
            # 4. Obtener fecha de lanzamiento (primera función programada) para cada película
            peliculas = query.order_by(Pelicula.Titulo).distinct().all()
            
            # 5. Obtener fecha de lanzamiento para cada película (la función más temprana)
            fechas_lanzamiento = {}
            if peliculas:
                pelicula_ids = [p.Id for p in peliculas]
                
                # Consulta para obtener la primera función programada para cada película
                resultados_fechas = session.query(
                    Funcion.IdPelicula,
                    func.min(Funcion.FechaHora).label('fecha_lanzamiento')
                ).filter(
                    Funcion.IdPelicula.in_(pelicula_ids),
                    Funcion.FechaHora >= fecha_minima,
                    Funcion.Activo == True
                ).group_by(Funcion.IdPelicula).all()
                
                for id_pelicula, fecha_lanzamiento in resultados_fechas:
                    fechas_lanzamiento[id_pelicula] = fecha_lanzamiento
            
            # 6. Formatear resultados
            peliculas_proximas = []
            for pelicula in peliculas:
                generos = [pg.genero.Genero for pg in pelicula.generos]
                
                fecha_lanz = fechas_lanzamiento.get(pelicula.Id)
                fecha_lanz_formateada = fecha_lanz.strftime('%d/%m/%Y') if fecha_lanz else 'Por definir'
                
                pelicula_dict = {
                    'id': pelicula.Id,
                    'titulo': pelicula.Titulo,
                    'descripcion_corta': pelicula.DescripcionCorta,
                    'descripcion_larga': pelicula.DescripcionLarga,
                    'duracion_minutos': pelicula.DuracionMinutos,
                    'generos': generos,
                    'clasificacion': pelicula.clasificacion.Clasificacion if pelicula.clasificacion else None,
                    'idioma': pelicula.idioma.Idioma if pelicula.idioma else None,
                    'link_to_banner': pelicula.LinkToBanner,
                    'link_to_bajante': pelicula.LinkToBajante,
                    'link_to_trailer': pelicula.LinkToTrailer,
                    'fecha_lanzamiento': fecha_lanz,
                    'fecha_lanzamiento_formateada': fecha_lanz_formateada
                }
                
                peliculas_proximas.append(pelicula_dict)
                session.expunge(pelicula)
            
            return peliculas_proximas
            
        except Exception as e:
            print(f"Error al filtrar películas próximas: {e}")
            traceback.print_exc()
            return []
        finally:
            session.close()

    @staticmethod
    def obtener_opciones_filtros_proximamente(peliculas_filtradas):
        """
        Obtiene opciones de filtro basadas en las películas próximas ya obtenidas.
        Solo muestra los filtros (géneros, idiomas, clasificaciones) que están disponibles
        en las películas que se están mostrando actualmente.
        
        Args:
            peliculas_filtradas (list): Lista de diccionarios con información de películas próximas
                
        Returns:
            dict: Diccionario con las opciones de filtro disponibles
        """
        # Si no hay películas, retornar listas vacías
        if not peliculas_filtradas:
            return {
                'generos': [],
                'idiomas': [],
                'clasificaciones': []
            }
        
        session = db.get_session()
        try:
            # Paso 1: Recopilar nombres únicos de los elementos presentes en las películas filtradas
            generos_nombres = set()
            idiomas_nombres = set()
            clasificaciones_nombres = set()
            
            for pelicula in peliculas_filtradas:
                # Recopilar géneros (puede haber múltiples por película)
                for genero in pelicula.get('generos', []):
                    if genero:  # Solo agregar si no está vacío
                        generos_nombres.add(genero)
                
                # Recopilar idiomas
                idioma = pelicula.get('idioma')
                if idioma:
                    idiomas_nombres.add(idioma)
                
                # Recopilar clasificaciones
                clasificacion = pelicula.get('clasificacion')
                if clasificacion:
                    clasificaciones_nombres.add(clasificacion)
            
            # Paso 2: Consultar la base de datos para obtener objetos completos con IDs
            
            # Obtener géneros activos que coincidan con los nombres encontrados
            generos_objs = []
            if generos_nombres:
                generos_objs = session.query(Genero).filter(
                    Genero.Genero.in_(list(generos_nombres)),
                    Genero.Activo == True
                ).order_by(Genero.Genero).all()
            
            # Obtener idiomas activos que coincidan con los nombres encontrados
            idiomas_objs = []
            if idiomas_nombres:
                idiomas_objs = session.query(Idioma).filter(
                    Idioma.Idioma.in_(list(idiomas_nombres)),
                    Idioma.Activo == True
                ).order_by(Idioma.Idioma).all()
            
            # Obtener clasificaciones activas que coincidan con los nombres encontrados
            clasificaciones_objs = []
            if clasificaciones_nombres:
                clasificaciones_objs = session.query(Clasificacion).filter(
                    Clasificacion.Clasificacion.in_(list(clasificaciones_nombres)),
                    Clasificacion.Activo == True
                ).order_by(Clasificacion.Clasificacion).all()
            
            return {
                'generos': generos_objs,
                'idiomas': idiomas_objs,
                'clasificaciones': clasificaciones_objs
            }
            
        except Exception as e:
            print(f"Error al obtener opciones de filtros para próximamente: {e}")
            traceback.print_exc()
            
            return {
                'generos': [],
                'idiomas': [],
                'clasificaciones': []
            }
        finally:
            session.close()