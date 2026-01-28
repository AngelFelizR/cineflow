# controllers/pelicula_genero_controller.py
from database import db
from models import PeliculaGenero, Pelicula, Genero
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash

class PeliculaGeneroController:
    """Controlador para operaciones CRUD de Relaciones Película-Género"""

    @staticmethod
    def obtener_todos_paginados(pagina=1, por_pagina=25, filtros=None):
        """Obtiene relaciones película-género con paginación"""
        session = db.get_session()
        try:
            query = session.query(PeliculaGenero).\
                options(
                    joinedload(PeliculaGenero.pelicula),
                    joinedload(PeliculaGenero.genero)
                )
            
            # Aplicar filtros si existen
            if filtros:
                if filtros.get('pelicula_id'):
                    query = query.filter(PeliculaGenero.IdPelicula == filtros['pelicula_id'])
                if filtros.get('genero_id'):
                    query = query.filter(PeliculaGenero.IdGenero == filtros['genero_id'])
            
            # Ordenar por película y género
            query = query.order_by(PeliculaGenero.IdPelicula, PeliculaGenero.IdGenero)
            
            # Paginación
            relaciones = query.offset((pagina - 1) * por_pagina).limit(por_pagina).all()
            total = query.count()
            
            return {
                'relaciones': relaciones,
                'total': total,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'paginas': (total + por_pagina - 1) // por_pagina
            }
        except Exception as e:
            flash(f'Error al obtener relaciones película-género: {str(e)}', 'danger')
            return {'relaciones': [], 'total': 0, 'pagina': 1, 'por_pagina': por_pagina, 'paginas': 0}
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene una relación por su ID"""
        session = db.get_session()
        try:
            relacion = session.query(PeliculaGenero).\
                options(
                    joinedload(PeliculaGenero.pelicula),
                    joinedload(PeliculaGenero.genero)
                ).\
                filter(PeliculaGenero.Id == id).first()
            
            return relacion
        except Exception as e:
            flash(f'Error al obtener relación: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """Crea una nueva relación película-género"""
        session = db.get_session()
        try:
            # Validaciones
            if not data.get('IdPelicula'):
                return False, 'Debe seleccionar una película', None
            if not data.get('IdGenero'):
                return False, 'Debe seleccionar un género', None
            
            # Verificar que la película exista y esté activa
            pelicula = session.query(Pelicula).filter(
                Pelicula.Id == int(data['IdPelicula']), 
                Pelicula.Activo == True
            ).first()
            if not pelicula:
                return False, 'La película seleccionada no existe o no está activa', None
            
            # Verificar que el género exista y esté activo
            genero = session.query(Genero).filter(
                Genero.Id == int(data['IdGenero']), 
                Genero.Activo == True
            ).first()
            if not genero:
                return False, 'El género seleccionado no existe o no está activo', None
            
            # Verificar si ya existe la relación
            existente = session.query(PeliculaGenero).\
                filter(
                    PeliculaGenero.IdPelicula == int(data['IdPelicula']),
                    PeliculaGenero.IdGenero == int(data['IdGenero'])
                ).first()
            
            if existente:
                return False, 'Esta película ya tiene asignado este género', None
            
            # Crear nueva
            nueva_relacion = PeliculaGenero(
                IdPelicula=int(data['IdPelicula']),
                IdGenero=int(data['IdGenero'])
            )
            
            session.add(nueva_relacion)
            session.commit()
            return True, 'Relación creada exitosamente', nueva_relacion
            
        except IntegrityError:
            session.rollback()
            return False, 'Esta película ya tiene asignado este género', None
        except Exception as e:
            session.rollback()
            return False, f'Error al crear relación: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza una relación existente"""
        session = db.get_session()
        try:
            relacion = session.query(PeliculaGenero).\
                filter(PeliculaGenero.Id == id).first()
            
            if not relacion:
                return False, 'Relación no encontrada', None
            
            # Validaciones
            if not data.get('IdPelicula'):
                return False, 'Debe seleccionar una película', None
            if not data.get('IdGenero'):
                return False, 'Debe seleccionar un género', None
            
            # Verificar que la película exista y esté activa
            pelicula = session.query(Pelicula).filter(
                Pelicula.Id == int(data['IdPelicula']), 
                Pelicula.Activo == True
            ).first()
            if not pelicula:
                return False, 'La película seleccionada no existe o no está activa', None
            
            # Verificar que el género exista y esté activo
            genero = session.query(Genero).filter(
                Genero.Id == int(data['IdGenero']), 
                Genero.Activo == True
            ).first()
            if not genero:
                return False, 'El género seleccionado no existe o no está activo', None
            
            # Verificar si ya existe otra relación con los mismos datos
            existente = session.query(PeliculaGenero).\
                filter(
                    PeliculaGenero.IdPelicula == int(data['IdPelicula']),
                    PeliculaGenero.IdGenero == int(data['IdGenero']),
                    PeliculaGenero.Id != id
                ).first()
            
            if existente:
                return False, 'Esta película ya tiene asignado este género', None
            
            # Actualizar
            relacion.IdPelicula = int(data['IdPelicula'])
            relacion.IdGenero = int(data['IdGenero'])
            
            session.commit()
            return True, 'Relación actualizada exitosamente', relacion
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar relación: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina una relación película-género"""
        session = db.get_session()
        try:
            relacion = session.query(PeliculaGenero).\
                filter(PeliculaGenero.Id == id).first()
            
            if not relacion:
                return False, 'Relación no encontrada'
            
            # Guardar información para el mensaje
            pelicula_id = relacion.IdPelicula
            genero_id = relacion.IdGenero
            
            session.delete(relacion)
            session.commit()
            
            return True, f'Relación película-género eliminada exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar relación: {str(e)}'
        finally:
            session.close()