# controllers/pelicula_admin_controller.py
from database import db
from models import Pelicula, Clasificacion, Idioma, PeliculaGenero, Genero, Funcion
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash
from datetime import datetime

class PeliculaAdminController:
    """Controlador para operaciones CRUD de Películas (Administrador)"""

    @staticmethod
    def obtener_todas_paginadas(pagina=1, por_pagina=25, filtros=None):
        """Obtiene películas con paginación"""
        session = db.get_session()
        try:
            query = session.query(Pelicula).\
                options(joinedload(Pelicula.clasificacion), joinedload(Pelicula.idioma)).\
                filter(Pelicula.Activo == True)
            
            # Aplicar filtros si existen
            if filtros:
                if filtros.get('titulo'):
                    query = query.filter(Pelicula.Titulo.ilike(f'%{filtros["titulo"]}%'))
                if filtros.get('clasificacion_id'):
                    query = query.filter(Pelicula.IdClasificacion == filtros['clasificacion_id'])
                if filtros.get('idioma_id'):
                    query = query.filter(Pelicula.IdIdioma == filtros['idioma_id'])
            
            # Ordenar por título
            query = query.order_by(Pelicula.Titulo)
            
            # Paginación
            peliculas = query.offset((pagina - 1) * por_pagina).limit(por_pagina).all()
            total = query.count()
            
            return {
                'peliculas': peliculas,
                'total': total,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'paginas': (total + por_pagina - 1) // por_pagina
            }
        except Exception as e:
            flash(f'Error al obtener películas: {str(e)}', 'danger')
            return {'peliculas': [], 'total': 0, 'pagina': 1, 'por_pagina': por_pagina, 'paginas': 0}
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene una película por su ID con todas sus relaciones"""
        session = db.get_session()
        try:
            pelicula = session.query(Pelicula).\
                options(
                    joinedload(Pelicula.clasificacion),
                    joinedload(Pelicula.idioma),
                    joinedload(Pelicula.generos).joinedload(PeliculaGenero.genero)
                ).\
                filter(Pelicula.Id == id).first()
            
            return pelicula
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
            # Validaciones
            if not data.get('Titulo') or len(data['Titulo'].strip()) < 1:
                return False, 'El título es requerido', None
            if not data.get('IdClasificacion'):
                return False, 'Debe seleccionar una clasificación', None
            if not data.get('IdIdioma'):
                return False, 'Debe seleccionar un idioma', None
            if not data.get('DuracionMinutos') or int(data['DuracionMinutos']) <= 0:
                return False, 'La duración debe ser mayor a 0', None
            if not data.get('DescripcionCorta') or len(data['DescripcionCorta'].strip()) < 10:
                return False, 'La descripción corta debe tener al menos 10 caracteres', None
            if not data.get('DescripcionLarga') or len(data['DescripcionLarga'].strip()) < 20:
                return False, 'La descripción larga debe tener al menos 20 caracteres', None
            
            # Verificar que la clasificación exista y esté activa
            clasificacion = session.query(Clasificacion).filter(
                Clasificacion.Id == int(data['IdClasificacion']), 
                Clasificacion.Activo == True
            ).first()
            if not clasificacion:
                return False, 'La clasificación seleccionada no existe o no está activa', None
            
            # Verificar que el idioma exista y esté activo
            idioma = session.query(Idioma).filter(
                Idioma.Id == int(data['IdIdioma']), 
                Idioma.Activo == True
            ).first()
            if not idioma:
                return False, 'El idioma seleccionado no existe o no está activo', None
            
            # Verificar si ya existe una película con ese título
            existente = session.query(Pelicula).\
                filter(Pelicula.Titulo.ilike(data['Titulo'].strip())).first()
            
            if existente:
                if existente.Activo:
                    return False, 'Ya existe una película con ese título', None
                else:
                    # Reactivar la existente
                    existente.Activo = True
                    existente.IdClasificacion = int(data['IdClasificacion'])
                    existente.IdIdioma = int(data['IdIdioma'])
                    existente.DuracionMinutos = int(data['DuracionMinutos'])
                    existente.DescripcionCorta = data['DescripcionCorta'].strip()
                    existente.DescripcionLarga = data['DescripcionLarga'].strip()
                    existente.LinkToBanner = data.get('LinkToBanner', '').strip()
                    existente.LinkToBajante = data.get('LinkToBajante', '').strip()
                    existente.LinkToTrailer = data.get('LinkToTrailer', '').strip()
                    session.commit()
                    return True, 'Película reactivada exitosamente', existente
            
            # Crear nueva
            nueva_pelicula = Pelicula(
                Titulo=data['Titulo'].strip(),
                IdClasificacion=int(data['IdClasificacion']),
                IdIdioma=int(data['IdIdioma']),
                DuracionMinutos=int(data['DuracionMinutos']),
                DescripcionCorta=data['DescripcionCorta'].strip(),
                DescripcionLarga=data['DescripcionLarga'].strip(),
                LinkToBanner=data.get('LinkToBanner', '').strip(),
                LinkToBajante=data.get('LinkToBajante', '').strip(),
                LinkToTrailer=data.get('LinkToTrailer', '').strip(),
                Activo=True
            )
            
            session.add(nueva_pelicula)
            session.flush()  # Para obtener el ID
            
            # Procesar géneros si existen
            if 'generos' in data:
                generos_ids = [int(g) for g in data.getlist('generos') if g]
                for genero_id in generos_ids:
                    # Verificar que el género exista
                    genero = session.query(Genero).filter(Genero.Id == genero_id, Genero.Activo == True).first()
                    if genero:
                        pelicula_genero = PeliculaGenero(
                            IdPelicula=nueva_pelicula.Id,
                            IdGenero=genero_id
                        )
                        session.add(pelicula_genero)
            
            session.commit()
            return True, 'Película creada exitosamente', nueva_pelicula
            
        except IntegrityError:
            session.rollback()
            return False, 'Ya existe una película con ese título', None
        except Exception as e:
            session.rollback()
            return False, f'Error al crear película: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza una película existente"""
        session = db.get_session()
        try:
            pelicula = session.query(Pelicula).\
                filter(Pelicula.Id == id).first()
            
            if not pelicula:
                return False, 'Película no encontrada', None
            
            # Validaciones
            if not data.get('Titulo') or len(data['Titulo'].strip()) < 1:
                return False, 'El título es requerido', None
            if not data.get('IdClasificacion'):
                return False, 'Debe seleccionar una clasificación', None
            if not data.get('IdIdioma'):
                return False, 'Debe seleccionar un idioma', None
            if not data.get('DuracionMinutos') or int(data['DuracionMinutos']) <= 0:
                return False, 'La duración debe ser mayor a 0', None
            if not data.get('DescripcionCorta') or len(data['DescripcionCorta'].strip()) < 10:
                return False, 'La descripción corta debe tener al menos 10 caracteres', None
            if not data.get('DescripcionLarga') or len(data['DescripcionLarga'].strip()) < 20:
                return False, 'La descripción larga debe tener al menos 20 caracteres', None
            
            # Verificar que la clasificación exista y esté activa
            clasificacion = session.query(Clasificacion).filter(
                Clasificacion.Id == int(data['IdClasificacion']), 
                Clasificacion.Activo == True
            ).first()
            if not clasificacion:
                return False, 'La clasificación seleccionada no existe o no está activa', None
            
            # Verificar que el idioma exista y esté activo
            idioma = session.query(Idioma).filter(
                Idioma.Id == int(data['IdIdioma']), 
                Idioma.Activo == True
            ).first()
            if not idioma:
                return False, 'El idioma seleccionado no existe o no está activo', None
            
            # Verificar si ya existe otra película con ese título
            existente = session.query(Pelicula).\
                filter(
                    Pelicula.Titulo.ilike(data['Titulo'].strip()),
                    Pelicula.Id != id
                ).first()
            
            if existente:
                return False, 'Ya existe otra película con ese título', None
            
            # Actualizar
            pelicula.Titulo = data['Titulo'].strip()
            pelicula.IdClasificacion = int(data['IdClasificacion'])
            pelicula.IdIdioma = int(data['IdIdioma'])
            pelicula.DuracionMinutos = int(data['DuracionMinutos'])
            pelicula.DescripcionCorta = data['DescripcionCorta'].strip()
            pelicula.DescripcionLarga = data['DescripcionLarga'].strip()
            pelicula.LinkToBanner = data.get('LinkToBanner', '').strip()
            pelicula.LinkToBajante = data.get('LinkToBajante', '').strip()
            pelicula.LinkToTrailer = data.get('LinkToTrailer', '').strip()
            
            if 'Activo' in data:
                pelicula.Activo = data['Activo'] == 'on' if isinstance(data['Activo'], str) else bool(data['Activo'])
            
            # Actualizar géneros
            if 'generos' in data:
                # Eliminar géneros actuales
                session.query(PeliculaGenero).filter(PeliculaGenero.IdPelicula == id).delete()
                
                # Agregar nuevos géneros
                generos_ids = [int(g) for g in data.getlist('generos') if g]
                for genero_id in generos_ids:
                    # Verificar que el género exista
                    genero = session.query(Genero).filter(Genero.Id == genero_id, Genero.Activo == True).first()
                    if genero:
                        pelicula_genero = PeliculaGenero(
                            IdPelicula=id,
                            IdGenero=genero_id
                        )
                        session.add(pelicula_genero)
            
            session.commit()
            return True, 'Película actualizada exitosamente', pelicula
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar película: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina (desactiva) una película"""
        session = db.get_session()
        try:
            pelicula = session.query(Pelicula).\
                filter(Pelicula.Id == id).first()
            
            if not pelicula:
                return False, 'Película no encontrada'
            
            # Verificar si hay funciones usando esta película
            funciones = session.query(Funcion).\
                filter(Funcion.IdPelicula == id).\
                filter(Funcion.Activo == True).count()
            
            if funciones > 0:
                return False, f'No se puede eliminar la película porque tiene {funciones} función(es) programada(s)'
            
            # Desactivar (eliminación lógica)
            pelicula.Activo = False
            session.commit()
            
            return True, 'Película eliminada exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar película: {str(e)}'
        finally:
            session.close()

    @staticmethod
    def contar_generos_por_pelicula(pelicula_id):
        """Cuenta cuántos géneros tiene una película"""
        session = db.get_session()
        try:
            count = session.query(PeliculaGenero).\
                filter(PeliculaGenero.IdPelicula == pelicula_id).count()
            return count
        except Exception as e:
            print(f"Error al contar géneros: {e}")
            return 0
        finally:
            session.close()

    # Método para obtener películas con sus géneros precargados
    @staticmethod
    def obtener_todas_con_generos():
        """Obtiene todas las películas activas con sus géneros"""
        session = db.get_session()
        try:
            peliculas = session.query(Pelicula).\
                options(
                    joinedload(Pelicula.generos).joinedload(PeliculaGenero.genero)
                ).\
                filter(Pelicula.Activo == True).\
                order_by(Pelicula.Titulo).all()
            
            return peliculas
        except Exception as e:
            flash(f'Error al obtener películas: {str(e)}', 'danger')
            return []
        finally:
            session.close()