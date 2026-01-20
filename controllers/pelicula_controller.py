# controllers/pelicula_controller.py
# Controlador para operaciones de películas

from models import Pelicula, Funcion, Boleto, PeliculaGenero, Genero
from database import db
from sqlalchemy import desc, func
from sqlalchemy.orm import joinedload
from datetime import datetime

class PeliculaController:
    """Controlador para operaciones de películas"""

    def __init__(self):
        pass

    @staticmethod
    def ultimas_3_pelis():
        """
        Obtiene las últimas 3 películas con funciones próximas
        
        Returns:
            list: Lista de diccionarios con información de películas
        """
        session = db.get_session()
        try:
            # Obtener películas que tienen funciones futuras
            peliculas = session.query(Pelicula).options(
                joinedload(Pelicula.clasificacion),
                joinedload(Pelicula.idioma),
                joinedload(Pelicula.generos).joinedload(PeliculaGenero.genero)
            ).filter(
                Pelicula.Activo == True
            ).order_by(desc(Pelicula.Id)).limit(3).all()

            resultado = []
            for pelicula in peliculas:
                # Obtener nombres de géneros
                generos = [pg.genero.Genero for pg in pelicula.generos]
                
                # Obtener próxima función
                proxima_funcion = session.query(Funcion).filter(
                    Funcion.IdPelicula == pelicula.Id,
                    Funcion.FechaHora > datetime.now(),
                    Funcion.Activo == True
                ).order_by(Funcion.FechaHora).first()
                
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
                    'proxima_funcion': proxima_funcion.FechaHora if proxima_funcion else None
                }
                
                resultado.append(pelicula_dict)
                session.expunge(pelicula)
                
            return resultado
            
        except Exception as e:
            print(f"Error al obtener últimas películas: {e}")
            return []
        finally:
            session.close()

    @staticmethod
    def top_3_pelis():
        """
        Obtiene las 3 películas más populares basadas en ventas de boletos
        
        Returns:
            list: Lista de diccionarios con información de películas
        """
        session = db.get_session()
        try:
            # SOLUCIÓN 1: Usar subconsulta para evitar problemas de GROUP BY
            # Primero obtenemos los IDs de las películas más populares
            subquery = session.query(
                Funcion.IdPelicula,
                func.count(Boleto.Id).label('total_boletos')
            ).join(Boleto, Funcion.Id == Boleto.IdFuncion
            ).filter(
                Funcion.Activo == True,
                Funcion.FechaHora > datetime.now()
            ).group_by(Funcion.IdPelicula).subquery()

            # Luego obtenemos las películas con más boletos
            peliculas_populares = session.query(
                Pelicula.Id,
                func.coalesce(subquery.c.total_boletos, 0).label('total_boletos')
            ).outerjoin(subquery, Pelicula.Id == subquery.c.IdPelicula
            ).filter(
                Pelicula.Activo == True
            ).order_by(desc(func.coalesce(subquery.c.total_boletos, 0))).limit(3).all()

            resultado = []
            for pelicula_id, total_boletos in peliculas_populares:
                # Cargar la película completa con sus relaciones
                pelicula_completa = session.query(Pelicula).options(
                    joinedload(Pelicula.clasificacion),
                    joinedload(Pelicula.idioma),
                    joinedload(Pelicula.generos).joinedload(PeliculaGenero.genero)
                ).filter(Pelicula.Id == pelicula_id).first()
                
                if not pelicula_completa:
                    continue
                    
                # Obtener nombres de géneros
                generos = [pg.genero.Genero for pg in pelicula_completa.generos]
                
                pelicula_dict = {
                    'id': pelicula_completa.Id,
                    'titulo': pelicula_completa.Titulo,
                    'descripcion_corta': pelicula_completa.DescripcionCorta,
                    'descripcion_larga': pelicula_completa.DescripcionLarga,
                    'duracion_minutos': pelicula_completa.DuracionMinutos,
                    'generos': generos,
                    'clasificacion': pelicula_completa.clasificacion.Clasificacion if pelicula_completa.clasificacion else None,
                    'idioma': pelicula_completa.idioma.Idioma if pelicula_completa.idioma else None,
                    'link_to_banner': pelicula_completa.LinkToBanner,
                    'link_to_bajante': pelicula_completa.LinkToBajante,
                    'link_to_trailer': pelicula_completa.LinkToTrailer,
                    'total_boletos': total_boletos or 0,
                    'popularidad': PeliculaController._calcular_popularidad(total_boletos or 0)
                }
                
                resultado.append(pelicula_dict)
                session.expunge(pelicula_completa)
            
            # Si no hay películas con boletos, devolver las últimas 3
            if not resultado:
                return PeliculaController.ultimas_3_pelis()
                
            return resultado
            
        except Exception as e:
            print(f"Error al obtener películas populares: {e}")
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