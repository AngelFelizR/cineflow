# controllers/pelicula_admin_controller.py (VERSIÓN CORREGIDA)
from database import db
from models import Pelicula, Clasificacion, Idioma, PeliculaGenero, Genero, Funcion, Sala
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash
from datetime import datetime
from sqlalchemy import func, desc
import traceback

class PeliculaAdminController:
    """Controlador para operaciones CRUD de Películas (Administrador)"""

    @staticmethod
    def obtener_todas_paginadas(pagina=1, por_pagina=25, filtros=None):
        """Obtiene películas con paginación"""
        session = db.get_session()
        try:
            query = session.query(Pelicula).options(
                joinedload(Pelicula.clasificacion),
                joinedload(Pelicula.idioma),
                joinedload(Pelicula.generos).joinedload(PeliculaGenero.genero)
            )
            
            if filtros:
                if filtros.get('titulo'):
                    titulo_busqueda = f"%{filtros['titulo'].strip()}%"
                    query = query.filter(Pelicula.Titulo.ilike(titulo_busqueda))
                
                if 'activo' in filtros:
                    if filtros['activo'] is True:
                        query = query.filter(Pelicula.Activo == True)
                    elif filtros['activo'] is False:
                        query = query.filter(Pelicula.Activo == False)
            
            query = query.order_by(Pelicula.Titulo)
            
            total = query.count()
            
            offset = (pagina - 1) * por_pagina
            peliculas = query.offset(offset).limit(por_pagina).all()
            
            peliculas_procesadas = []
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
                    'activo': pelicula.Activo
                }
                peliculas_procesadas.append(pelicula_dict)
            
            return {
                'peliculas': peliculas_procesadas,
                'total': total,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'paginas': (total + por_pagina - 1) // por_pagina
            }
            
        except Exception as e:
            flash(f'Error al obtener películas: {str(e)}', 'danger')
            print(f"Error en obtener_todas_paginadas: {e}")
            traceback.print_exc()
            return {
                'peliculas': [],
                'total': 0,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'paginas': 0
            }
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene una película por su ID con todas sus relaciones"""
        session = db.get_session()
        try:
            pelicula = session.query(Pelicula).options(
                joinedload(Pelicula.clasificacion),
                joinedload(Pelicula.idioma),
                joinedload(Pelicula.generos).joinedload(PeliculaGenero.genero)
            ).filter(Pelicula.Id == id).first()
            
            if pelicula:
                # Crear un objeto wrapper con todos los atributos necesarios
                class PeliculaWrapper:
                    def __init__(self, pelicula_obj):
                        self.Id = pelicula_obj.Id
                        self.Titulo = pelicula_obj.Titulo
                        self.DescripcionCorta = pelicula_obj.DescripcionCorta
                        self.DescripcionLarga = pelicula_obj.DescripcionLarga
                        self.DuracionMinutos = pelicula_obj.DuracionMinutos
                        self.LinkToBanner = pelicula_obj.LinkToBanner
                        self.LinkToBajante = pelicula_obj.LinkToBajante
                        self.LinkToTrailer = pelicula_obj.LinkToTrailer
                        self.Activo = pelicula_obj.Activo
                        self.IdClasificacion = pelicula_obj.IdClasificacion
                        self.IdIdioma = pelicula_obj.IdIdioma
                        # Mantener las relaciones
                        self.generos = pelicula_obj.generos
                        self.clasificacion = pelicula_obj.clasificacion
                        self.idioma = pelicula_obj.idioma
                
                return PeliculaWrapper(pelicula)
            return None
            
        except Exception as e:
            flash(f'Error al obtener película: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """Crea una nueva película"""
        session = db.get_session()
        try:
            # Validaciones (simplificadas para coincidir con el formulario)
            if not data.get('Titulo') or len(data['Titulo'].strip()) < 1:
                return False, 'El título es requerido', None
            if not data.get('IdClasificacion'):
                return False, 'Debe seleccionar una clasificación', None
            if not data.get('IdIdioma'):
                return False, 'Debe seleccionar un idioma', None
            
            # Convertir duración
            try:
                duracion = int(data.get('DuracionMinutos', 0))
                if duracion <= 0:
                    return False, 'La duración debe ser mayor a 0', None
            except (ValueError, TypeError):
                return False, 'La duración debe ser un número válido', None
            
            # Verificar que la clasificación exista
            clasificacion = session.query(Clasificacion).filter(
                Clasificacion.Id == int(data['IdClasificacion']), 
                Clasificacion.Activo == True
            ).first()
            if not clasificacion:
                return False, 'La clasificación seleccionada no existe o no está activa', None
            
            # Verificar que el idioma exista
            idioma = session.query(Idioma).filter(
                Idioma.Id == int(data['IdIdioma']), 
                Idioma.Activo == True
            ).first()
            if not idioma:
                return False, 'El idioma seleccionado no existe o no está activo', None
            
            # Verificar si ya existe una película con ese título (activa)
            existente = session.query(Pelicula).filter(
                Pelicula.Titulo.ilike(data['Titulo'].strip()),
                Pelicula.Activo == True
            ).first()
            
            if existente:
                return False, 'Ya existe una película activa con ese título', None
            
            # Crear nueva película
            nueva_pelicula = Pelicula(
                Titulo=data['Titulo'].strip(),
                IdClasificacion=int(data['IdClasificacion']),
                IdIdioma=int(data['IdIdioma']),
                DuracionMinutos=duracion,
                DescripcionCorta=data.get('DescripcionCorta', '').strip(),
                DescripcionLarga=data.get('DescripcionLarga', '').strip(),
                LinkToBanner=data.get('LinkToBanner', '').strip(),
                LinkToBajante=data.get('LinkToBajante', '').strip(),
                LinkToTrailer=data.get('LinkToTrailer', '').strip(),
                Activo=True
            )
            
            session.add(nueva_pelicula)
            session.flush()  # Para obtener el ID
            
            # Procesar géneros si existen
            if 'generos' in data:
                generos_ids = []
                # Manejar tanto list como string individual
                if isinstance(data['generos'], list):
                    generos_ids = [int(g) for g in data['generos'] if g]
                else:
                    if data['generos']:
                        generos_ids = [int(data['generos'])]
                
                for genero_id in generos_ids:
                    genero = session.query(Genero).filter(
                        Genero.Id == genero_id, 
                        Genero.Activo == True
                    ).first()
                    if genero:
                        pelicula_genero = PeliculaGenero(
                            IdPelicula=nueva_pelicula.Id,
                            IdGenero=genero_id
                        )
                        session.add(pelicula_genero)
            
            session.commit()
            return True, 'Película creada exitosamente', nueva_pelicula
            
        except IntegrityError as e:
            session.rollback()
            print(f"IntegrityError: {e}")
            return False, 'Error de integridad en la base de datos', None
        except Exception as e:
            session.rollback()
            print(f"Error al crear película: {e}")
            traceback.print_exc()
            return False, f'Error al crear película: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza una película existente"""
        session = db.get_session()
        try:
            pelicula = session.query(Pelicula).filter(Pelicula.Id == id).first()
            
            if not pelicula:
                return False, 'Película no encontrada', None
            
            # Validaciones
            if not data.get('Titulo') or len(data['Titulo'].strip()) < 1:
                return False, 'El título es requerido', None
            if not data.get('IdClasificacion'):
                return False, 'Debe seleccionar una clasificación', None
            if not data.get('IdIdioma'):
                return False, 'Debe seleccionar un idioma', None
            
            # Verificar que no exista otra película activa con el mismo título
            existente = session.query(Pelicula).filter(
                Pelicula.Titulo.ilike(data['Titulo'].strip()),
                Pelicula.Activo == True,
                Pelicula.Id != id
            ).first()
            
            if existente:
                return False, 'Ya existe otra película activa con ese título', None
            
            # Actualizar campos básicos
            pelicula.Titulo = data['Titulo'].strip()
            pelicula.IdClasificacion = int(data['IdClasificacion'])
            pelicula.IdIdioma = int(data['IdIdioma'])
            
            # Solo actualizar duración si se proporciona
            if 'DuracionMinutos' in data:
                try:
                    pelicula.DuracionMinutos = int(data['DuracionMinutos'])
                except (ValueError, TypeError):
                    pass
            
            if 'DescripcionCorta' in data:
                pelicula.DescripcionCorta = data['DescripcionCorta'].strip()
            
            if 'DescripcionLarga' in data:
                pelicula.DescripcionLarga = data['DescripcionLarga'].strip()
            
            if 'LinkToBanner' in data:
                pelicula.LinkToBanner = data['LinkToBanner'].strip()
            
            if 'LinkToBajante' in data:
                pelicula.LinkToBajante = data['LinkToBajante'].strip()
            
            if 'LinkToTrailer' in data:
                pelicula.LinkToTrailer = data['LinkToTrailer'].strip()
            
            # Actualizar estado
            if 'Activo' in data:
                if isinstance(data['Activo'], str):
                    pelicula.Activo = data['Activo'].lower() in ['true', '1', 'yes', 'on']
                else:
                    pelicula.Activo = bool(data['Activo'])
            
            # Actualizar géneros
            if 'generos' in data:
                # Eliminar géneros actuales
                session.query(PeliculaGenero).filter(PeliculaGenero.IdPelicula == id).delete()
                
                # Agregar nuevos géneros
                generos_ids = []
                if isinstance(data['generos'], list):
                    generos_ids = [int(g) for g in data['generos'] if g]
                elif data['generos']:
                    generos_ids = [int(data['generos'])]
                
                for genero_id in generos_ids:
                    genero = session.query(Genero).filter(
                        Genero.Id == genero_id, 
                        Genero.Activo == True
                    ).first()
                    if genero:
                        pelicula_genero = PeliculaGenero(
                            IdPelicula=id,
                            IdGenero=genero_id
                        )
                        session.add(pelicula_genero)
            
            session.commit()
            
            # Cargar la película actualizada con relaciones
            pelicula_actualizada = session.query(Pelicula).options(
                joinedload(Pelicula.clasificacion),
                joinedload(Pelicula.idioma),
                joinedload(Pelicula.generos).joinedload(PeliculaGenero.genero)
            ).filter(Pelicula.Id == id).first()
            
            return True, 'Película actualizada exitosamente', pelicula_actualizada
            
        except Exception as e:
            session.rollback()
            print(f"Error al actualizar película: {e}")
            traceback.print_exc()
            return False, f'Error al actualizar película: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina (desactiva) una película"""
        session = db.get_session()
        try:
            pelicula = session.query(Pelicula).filter(Pelicula.Id == id).first()
            
            if not pelicula:
                return False, 'Película no encontrada'
            
            # Verificar si tiene funciones activas futuras
            funciones_futuras = session.query(Funcion).filter(
                Funcion.IdPelicula == id,
                Funcion.Activo == True,
                Funcion.FechaHora > datetime.now()
            ).count()
            
            if funciones_futuras > 0:
                return False, f'No se puede eliminar la película porque tiene {funciones_futuras} función(es) futuras programada(s)'
            
            # Desactivar (eliminación lógica)
            pelicula.Activo = False
            session.commit()
            
            return True, 'Película desactivada exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar película: {str(e)}'
        finally:
            session.close()
    
    @staticmethod
    def obtener_funciones_por_pelicula(pelicula_id):
        """Obtiene funciones de una película"""
        session = db.get_session()
        try:
            funciones = session.query(Funcion).options(
                joinedload(Funcion.sala).joinedload(Sala.cine),
                joinedload(Funcion.sala).joinedload(Sala.tipo_sala)
            ).filter(
                Funcion.IdPelicula == pelicula_id
            ).order_by(Funcion.FechaHora).all()
            
            return funciones
        except Exception as e:
            print(f"Error al obtener funciones: {e}")
            return []
        finally:
            session.close()
    
    @staticmethod
    def contar_boletos_por_pelicula(pelicula_id):
        """Cuenta boletos vendidos para una película"""
        session = db.get_session()
        try:
            from models import Boleto
            count = session.query(Boleto).join(Funcion).filter(
                Funcion.IdPelicula == pelicula_id
            ).count()
            return count
        except Exception as e:
            print(f"Error al contar boletos: {e}")
            return 0
        finally:
            session.close()

    @staticmethod
    def obtener_todas_simple():
        """Obtiene todas las películas (solo ID y título) para selects"""
        session = db.get_session()
        try:
            peliculas = session.query(Pelicula.Id, Pelicula.Titulo).\
                filter(Pelicula.Activo == True).\
                order_by(Pelicula.Titulo).all()
            
            return [(p.Id, p.Titulo) for p in peliculas]
        except Exception as e:
            print(f"Error al obtener películas simples: {e}")
            return []
        finally:
            session.close()