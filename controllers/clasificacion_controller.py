# controllers/clasificacion_controller.py
from database import db
from models import Clasificacion
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash

class ClasificacionController:
    """Controlador para operaciones CRUD de Clasificaciones"""

    @staticmethod
    def obtener_todas():
        """Obtiene todas las clasificaciones activas"""
        session = db.get_session()
        try:
            clasificaciones = session.query(Clasificacion).\
                filter(Clasificacion.Activo == True).\
                order_by(Clasificacion.Clasificacion).all()
            return clasificaciones
        except Exception as e:
            flash(f'Error al obtener clasificaciones: {str(e)}', 'danger')
            return []
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene una clasificación por su ID con sus películas"""
        session = db.get_session()
        try:
            # Cargar clasificación con películas relacionadas
            clasificacion = session.query(Clasificacion).\
                options(joinedload(Clasificacion.peliculas)).\
                filter(Clasificacion.Id == id).first()
            
            # Forzar la carga de la relación mientras la sesión está abierta
            if clasificacion and hasattr(clasificacion, 'peliculas'):
                _ = list(clasificacion.peliculas)  # Esto carga la relación
            
            return clasificacion
        except Exception as e:
            flash(f'Error al obtener clasificación: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """Crea una nueva clasificación"""
        session = db.get_session()
        try:
            # Validaciones
            if not data.get('Clasificacion') or len(data['Clasificacion'].strip()) < 2:
                return False, 'La clasificación debe tener al menos 2 caracteres', None
            
            # Verificar si ya existe
            existente = session.query(Clasificacion).\
                filter(Clasificacion.Clasificacion.ilike(data['Clasificacion'].strip())).first()
            
            if existente:
                if existente.Activo:
                    return False, 'Ya existe una clasificación con ese nombre', None
                else:
                    # Reactivar la existente
                    existente.Activo = True
                    session.commit()
                    return True, 'Clasificación reactivada exitosamente', existente
            
            # Crear nueva
            nueva_clasificacion = Clasificacion(
                Clasificacion=data['Clasificacion'].strip(),
                Activo=True
            )
            
            session.add(nueva_clasificacion)
            session.commit()
            return True, 'Clasificación creada exitosamente', nueva_clasificacion
            
        except IntegrityError:
            session.rollback()
            return False, 'Ya existe una clasificación con ese nombre', None
        except Exception as e:
            session.rollback()
            return False, f'Error al crear clasificación: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza una clasificación existente"""
        session = db.get_session()
        try:
            clasificacion = session.query(Clasificacion).\
                filter(Clasificacion.Id == id).first()
            
            if not clasificacion:
                return False, 'Clasificación no encontrada', None
            
            # Validaciones
            if not data.get('Clasificacion') or len(data['Clasificacion'].strip()) < 2:
                return False, 'La clasificación debe tener al menos 2 caracteres', None
            
            # Verificar si el nuevo nombre ya existe en otra clasificación
            existente = session.query(Clasificacion).\
                filter(
                    Clasificacion.Clasificacion.ilike(data['Clasificacion'].strip()),
                    Clasificacion.Id != id
                ).first()
            
            if existente:
                return False, 'Ya existe otra clasificación con ese nombre', None
            
            # Actualizar
            clasificacion.Clasificacion = data['Clasificacion'].strip()
            
            if 'Activo' in data:
                clasificacion.Activo = data['Activo'] == 'on' if isinstance(data['Activo'], str) else bool(data['Activo'])
            
            session.commit()
            return True, 'Clasificación actualizada exitosamente', clasificacion
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar clasificación: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina (desactiva) una clasificación"""
        session = db.get_session()
        try:
            clasificacion = session.query(Clasificacion).\
                filter(Clasificacion.Id == id).first()
            
            if not clasificacion:
                return False, 'Clasificación no encontrada'
            
            # Verificar si hay películas usando esta clasificación
            from models import Pelicula
            peliculas = session.query(Pelicula).\
                filter(Pelicula.IdClasificacion == id).\
                filter(Pelicula.Activo == True).count()
            
            if peliculas > 0:
                return False, f'No se puede eliminar la clasificación porque está siendo usada por {peliculas} película(s)'
            
            # Desactivar (eliminación lógica)
            clasificacion.Activo = False
            session.commit()
            
            return True, 'Clasificación eliminada exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar clasificación: {str(e)}'
        finally:
            session.close()
    
    @staticmethod
    def obtener_para_select():
        """Obtiene clasificaciones para usar en selects (comboboxes)"""
        session = db.get_session()
        try:
            clasificaciones = session.query(
                Clasificacion.Id,
                Clasificacion.Clasificacion
            ).filter(
                Clasificacion.Activo == True
            ).order_by(
                Clasificacion.Clasificacion
            ).all()
            
            return [(c.Id, c.Clasificacion) for c in clasificaciones]
        except Exception as e:
            print(f"Error al obtener clasificaciones para select: {e}")
            return []
        finally:
            session.close()