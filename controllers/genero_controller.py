# controllers/genero_controller.py
from database import db
from models import Genero, PeliculaGenero
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash

class GeneroController:
    """Controlador para operaciones CRUD de Géneros"""

    @staticmethod
    def obtener_todos():
        """Obtiene todos los géneros activos"""
        session = db.get_session()
        try:
            generos = session.query(Genero).\
                filter(Genero.Activo == True).\
                order_by(Genero.Genero).all()
            return generos
        except Exception as e:
            flash(f'Error al obtener géneros: {str(e)}', 'danger')
            return []
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene un género por su ID con sus películas"""
        session = db.get_session()
        try:
            genero = session.query(Genero).\
                options(joinedload(Genero.peliculas)).\
                filter(Genero.Id == id).first()
            
            if genero and hasattr(genero, 'peliculas'):
                _ = list(genero.peliculas)
            
            return genero
        except Exception as e:
            flash(f'Error al obtener género: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """Crea un nuevo género"""
        session = db.get_session()
        try:
            if not data.get('Genero') or len(data['Genero'].strip()) < 2:
                return False, 'El género debe tener al menos 2 caracteres', None
            
            existente = session.query(Genero).\
                filter(Genero.Genero.ilike(data['Genero'].strip())).first()
            
            if existente:
                if existente.Activo:
                    return False, 'Ya existe un género con ese nombre', None
                else:
                    existente.Activo = True
                    session.commit()
                    return True, 'Género reactivado exitosamente', existente
            
            nuevo_genero = Genero(
                Genero=data['Genero'].strip(),
                Activo=True
            )
            
            session.add(nuevo_genero)
            session.commit()
            return True, 'Género creado exitosamente', nuevo_genero
            
        except IntegrityError:
            session.rollback()
            return False, 'Ya existe un género con ese nombre', None
        except Exception as e:
            session.rollback()
            return False, f'Error al crear género: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza un género existente"""
        session = db.get_session()
        try:
            genero = session.query(Genero).\
                filter(Genero.Id == id).first()
            
            if not genero:
                return False, 'Género no encontrado', None
            
            if not data.get('Genero') or len(data['Genero'].strip()) < 2:
                return False, 'El género debe tener al menos 2 caracteres', None
            
            existente = session.query(Genero).\
                filter(
                    Genero.Genero.ilike(data['Genero'].strip()),
                    Genero.Id != id
                ).first()
            
            if existente:
                return False, 'Ya existe otro género con ese nombre', None
            
            genero.Genero = data['Genero'].strip()
            
            if 'Activo' in data:
                genero.Activo = data['Activo'] == 'on' if isinstance(data['Activo'], str) else bool(data['Activo'])
            
            session.commit()
            return True, 'Género actualizado exitosamente', genero
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar género: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina (desactiva) un género"""
        session = db.get_session()
        try:
            genero = session.query(Genero).\
                filter(Genero.Id == id).first()
            
            if not genero:
                return False, 'Género no encontrado'
            
            peliculas = session.query(PeliculaGenero).\
                filter(PeliculaGenero.IdGenero == id).count()
            
            if peliculas > 0:
                return False, f'No se puede eliminar el género porque está siendo usado por {peliculas} película(s)'
            
            genero.Activo = False
            session.commit()
            
            return True, 'Género eliminado exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar género: {str(e)}'
        finally:
            session.close()
    
    @staticmethod
    def obtener_para_select():
        """Obtiene géneros para usar en selects (comboboxes)"""
        session = db.get_session()
        try:
            generos = session.query(
                Genero.Id,
                Genero.Genero
            ).filter(
                Genero.Activo == True
            ).order_by(
                Genero.Genero
            ).all()
            
            return [(c.Id, c.Genero) for c in generos]
        except Exception as e:
            print(f"Error al obtener géneros para select: {e}")
            return []
        finally:
            session.close()