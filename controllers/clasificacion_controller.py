# controllers/clasificacion_controller.py
from database import db
from models import Clasificacion
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
        """Obtiene una clasificación por su ID"""
        session = db.get_session()
        try:
            clasificacion = session.query(Clasificacion).\
                filter(Clasificacion.Id == id).first()
            return clasificacion
        except Exception as e:
            flash(f'Error al obtener clasificación: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """
        Crea una nueva clasificación
        
        Args:
            data: Diccionario con datos de la clasificación
                - Clasificacion (str): Nombre de la clasificación
                
        Returns:
            tuple: (success, message, clasificacion)
        """
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
                    session.expunge(existente)
                    return True, 'Clasificación reactivada exitosamente', existente
            
            # Crear nueva
            nueva_clasificacion = Clasificacion(
                Clasificacion=data['Clasificacion'].strip(),
                Activo=True
            )
            
            session.add(nueva_clasificacion)
            session.commit()
            session.expunge(nueva_clasificacion)
            
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
        """
        Actualiza una clasificación existente
        
        Args:
            id: ID de la clasificación a actualizar
            data: Diccionario con datos actualizados
            
        Returns:
            tuple: (success, message, clasificacion)
        """
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
            
            session.commit()
            session.expunge(clasificacion)
            
            return True, 'Clasificación actualizada exitosamente', clasificacion
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar clasificación: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """
        Elimina (desactiva) una clasificación
        
        Args:
            id: ID de la clasificación a eliminar
            
        Returns:
            tuple: (success, message)
        """
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