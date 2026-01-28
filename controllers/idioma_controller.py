# controllers/idioma_controller.py
from database import db
from models import Idioma, Pelicula
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash

class IdiomaController:
    """Controlador para operaciones CRUD de Idiomas"""

    @staticmethod
    def obtener_todos():
        """Obtiene todos los idiomas activos"""
        session = db.get_session()
        try:
            idiomas = session.query(Idioma).\
                filter(Idioma.Activo == True).\
                order_by(Idioma.Idioma).all()
            return idiomas
        except Exception as e:
            flash(f'Error al obtener idiomas: {str(e)}', 'danger')
            return []
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene un idioma por su ID con sus películas"""
        session = db.get_session()
        try:
            idioma = session.query(Idioma).\
                options(joinedload(Idioma.peliculas)).\
                filter(Idioma.Id == id).first()
            
            if idioma and hasattr(idioma, 'peliculas'):
                _ = list(idioma.peliculas)
            
            return idioma
        except Exception as e:
            flash(f'Error al obtener idioma: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """Crea un nuevo idioma"""
        session = db.get_session()
        try:
            if not data.get('Idioma') or len(data['Idioma'].strip()) < 2:
                return False, 'El idioma debe tener al menos 2 caracteres', None
            
            existente = session.query(Idioma).\
                filter(Idioma.Idioma.ilike(data['Idioma'].strip())).first()
            
            if existente:
                if existente.Activo:
                    return False, 'Ya existe un idioma con ese nombre', None
                else:
                    existente.Activo = True
                    session.commit()
                    return True, 'Idioma reactivado exitosamente', existente
            
            nuevo_idioma = Idioma(
                Idioma=data['Idioma'].strip(),
                Activo=True
            )
            
            session.add(nuevo_idioma)
            session.commit()
            return True, 'Idioma creado exitosamente', nuevo_idioma
            
        except IntegrityError:
            session.rollback()
            return False, 'Ya existe un idioma con ese nombre', None
        except Exception as e:
            session.rollback()
            return False, f'Error al crear idioma: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza un idioma existente"""
        session = db.get_session()
        try:
            idioma = session.query(Idioma).\
                filter(Idioma.Id == id).first()
            
            if not idioma:
                return False, 'Idioma no encontrado', None
            
            if not data.get('Idioma') or len(data['Idioma'].strip()) < 2:
                return False, 'El idioma debe tener al menos 2 caracteres', None
            
            existente = session.query(Idioma).\
                filter(
                    Idioma.Idioma.ilike(data['Idioma'].strip()),
                    Idioma.Id != id
                ).first()
            
            if existente:
                return False, 'Ya existe otro idioma con ese nombre', None
            
            idioma.Idioma = data['Idioma'].strip()
            
            if 'Activo' in data:
                idioma.Activo = data['Activo'] == 'on' if isinstance(data['Activo'], str) else bool(data['Activo'])
            
            session.commit()
            return True, 'Idioma actualizado exitosamente', idioma
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar idioma: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina (desactiva) un idioma"""
        session = db.get_session()
        try:
            idioma = session.query(Idioma).\
                filter(Idioma.Id == id).first()
            
            if not idioma:
                return False, 'Idioma no encontrado'
            
            peliculas = session.query(Pelicula).\
                filter(Pelicula.IdIdioma == id).\
                filter(Pelicula.Activo == True).count()
            
            if peliculas > 0:
                return False, f'No se puede eliminar el idioma porque está siendo usado por {peliculas} película(s)'
            
            idioma.Activo = False
            session.commit()
            
            return True, 'Idioma eliminado exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar idioma: {str(e)}'
        finally:
            session.close()
    
    @staticmethod
    def obtener_para_select():
        """Obtiene idiomas para usar en selects (comboboxes)"""
        session = db.get_session()
        try:
            idiomas = session.query(
                Idioma.Id,
                Idioma.Idioma
            ).filter(
                Idioma.Activo == True
            ).order_by(
                Idioma.Idioma
            ).all()
            
            return [(c.Id, c.Idioma) for c in idiomas]
        except Exception as e:
            print(f"Error al obtener idiomas para select: {e}")
            return []
        finally:
            session.close()