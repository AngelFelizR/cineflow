# controllers/cine_controller.py
from database import db
from models import Cine, Sala
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash

class CineController:
    """Controlador para operaciones CRUD de Cines"""

    @staticmethod
    def obtener_todos():
        """Obtiene todos los cines activos"""
        session = db.get_session()
        try:
            cines = session.query(Cine).\
                filter(Cine.Activo == True).\
                order_by(Cine.Cine).all()
            return cines
        except Exception as e:
            flash(f'Error al obtener cines: {str(e)}', 'danger')
            return []
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene un cine por su ID con sus salas"""
        session = db.get_session()
        try:
            cine = session.query(Cine).\
                options(joinedload(Cine.salas)).\
                filter(Cine.Id == id).first()
            
            if cine and hasattr(cine, 'salas'):
                _ = list(cine.salas)
            
            return cine
        except Exception as e:
            flash(f'Error al obtener cine: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """Crea un nuevo cine"""
        session = db.get_session()
        try:
            if not data.get('Cine') or len(data['Cine'].strip()) < 2:
                return False, 'El nombre del cine debe tener al menos 2 caracteres', None
            if not data.get('Direccion') or len(data['Direccion'].strip()) < 5:
                return False, 'La dirección debe tener al menos 5 caracteres', None
            if not data.get('Telefono') or len(data['Telefono'].strip()) < 8:
                return False, 'El teléfono debe tener al menos 8 caracteres', None
            if not data.get('GoogleMapIframeSrc'):
                return False, 'El iframe de Google Maps es requerido', None
            
            existente_nombre = session.query(Cine).\
                filter(Cine.Cine.ilike(data['Cine'].strip())).first()
            
            if existente_nombre:
                if existente_nombre.Activo:
                    return False, 'Ya existe un cine con ese nombre', None
                else:
                    existente_nombre.Activo = True
                    session.commit()
                    return True, 'Cine reactivado exitosamente', existente_nombre
            
            existente_direccion = session.query(Cine).\
                filter(Cine.Direccion.ilike(data['Direccion'].strip())).first()
            
            if existente_direccion and existente_direccion.Activo:
                return False, 'Ya existe un cine con esa dirección', None
            
            nuevo_cine = Cine(
                Cine=data['Cine'].strip(),
                Direccion=data['Direccion'].strip(),
                Telefono=data['Telefono'].strip(),
                GoogleMapIframeSrc=data['GoogleMapIframeSrc'].strip(),
                Activo=True
            )
            
            session.add(nuevo_cine)
            session.commit()
            return True, 'Cine creado exitosamente', nuevo_cine
            
        except IntegrityError:
            session.rollback()
            return False, 'Ya existe un cine con ese nombre o dirección', None
        except Exception as e:
            session.rollback()
            return False, f'Error al crear cine: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza un cine existente"""
        session = db.get_session()
        try:
            cine = session.query(Cine).\
                filter(Cine.Id == id).first()
            
            if not cine:
                return False, 'Cine no encontrado', None
            
            if not data.get('Cine') or len(data['Cine'].strip()) < 2:
                return False, 'El nombre del cine debe tener al menos 2 caracteres', None
            if not data.get('Direccion') or len(data['Direccion'].strip()) < 5:
                return False, 'La dirección debe tener al menos 5 caracteres', None
            if not data.get('Telefono') or len(data['Telefono'].strip()) < 8:
                return False, 'El teléfono debe tener al menos 8 caracteres', None
            if not data.get('GoogleMapIframeSrc'):
                return False, 'El iframe de Google Maps es requerido', None
            
            existente_nombre = session.query(Cine).\
                filter(
                    Cine.Cine.ilike(data['Cine'].strip()),
                    Cine.Id != id
                ).first()
            
            if existente_nombre:
                return False, 'Ya existe otro cine con ese nombre', None
            
            existente_direccion = session.query(Cine).\
                filter(
                    Cine.Direccion.ilike(data['Direccion'].strip()),
                    Cine.Id != id
                ).first()
            
            if existente_direccion:
                return False, 'Ya existe otro cine con esa dirección', None
            
            cine.Cine = data['Cine'].strip()
            cine.Direccion = data['Direccion'].strip()
            cine.Telefono = data['Telefono'].strip()
            cine.GoogleMapIframeSrc = data['GoogleMapIframeSrc'].strip()
            
            if 'Activo' in data:
                cine.Activo = data['Activo'] == 'on' if isinstance(data['Activo'], str) else bool(data['Activo'])
            
            session.commit()
            return True, 'Cine actualizado exitosamente', cine
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar cine: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina (desactiva) un cine"""
        session = db.get_session()
        try:
            cine = session.query(Cine).\
                filter(Cine.Id == id).first()
            
            if not cine:
                return False, 'Cine no encontrado'
            
            salas = session.query(Sala).\
                filter(Sala.IdCine == id).\
                filter(Sala.Activo == True).count()
            
            if salas > 0:
                return False, f'No se puede eliminar el cine porque tiene {salas} sala(s) activa(s)'
            
            cine.Activo = False
            session.commit()
            
            return True, 'Cine eliminado exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar cine: {str(e)}'
        finally:
            session.close()
    
    @staticmethod
    def obtener_para_select():
        """Obtiene cines para usar en selects (comboboxes)"""
        session = db.get_session()
        try:
            cines = session.query(
                Cine.Id,
                Cine.Cine
            ).filter(
                Cine.Activo == True
            ).order_by(
                Cine.Cine
            ).all()
            
            return [(c.Id, c.Cine) for c in cines]
        except Exception as e:
            print(f"Error al obtener cines para select: {e}")
            return []
        finally:
            session.close()