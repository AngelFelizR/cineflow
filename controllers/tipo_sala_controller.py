# controllers/tipo_sala_controller.py
from database import db
from models import TipoSala, Sala
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash

class TipoSalaController:
    """Controlador para operaciones CRUD de Tipos de Sala"""

    @staticmethod
    def obtener_todos():
        """Obtiene todos los tipos de sala activos"""
        session = db.get_session()
        try:
            tipos = session.query(TipoSala).\
                filter(TipoSala.Activo == True).\
                order_by(TipoSala.Tipo).all()
            return tipos
        except Exception as e:
            flash(f'Error al obtener tipos de sala: {str(e)}', 'danger')
            return []
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene un tipo de sala por su ID con sus salas"""
        session = db.get_session()
        try:
            tipo = session.query(TipoSala).\
                options(joinedload(TipoSala.salas)).\
                filter(TipoSala.Id == id).first()
            
            if tipo and hasattr(tipo, 'salas'):
                _ = list(tipo.salas)
            
            return tipo
        except Exception as e:
            flash(f'Error al obtener tipo de sala: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """Crea un nuevo tipo de sala"""
        session = db.get_session()
        try:
            if not data.get('Tipo') or len(data['Tipo'].strip()) < 2:
                return False, 'El tipo de sala debe tener al menos 2 caracteres', None
            if not data.get('PrecioAdulto') or float(data['PrecioAdulto']) <= 0:
                return False, 'El precio para adulto debe ser mayor a 0', None
            if not data.get('PrecioNino') or float(data['PrecioNino']) <= 0:
                return False, 'El precio para niño debe ser mayor a 0', None
            
            existente = session.query(TipoSala).\
                filter(TipoSala.Tipo.ilike(data['Tipo'].strip())).first()
            
            if existente:
                if existente.Activo:
                    return False, 'Ya existe un tipo de sala con ese nombre', None
                else:
                    existente.Activo = True
                    session.commit()
                    return True, 'Tipo de sala reactivado exitosamente', existente
            
            nuevo_tipo = TipoSala(
                Tipo=data['Tipo'].strip(),
                PrecioAdulto=float(data['PrecioAdulto']),
                PrecioNino=float(data['PrecioNino']),
                Activo=True
            )
            
            session.add(nuevo_tipo)
            session.commit()
            return True, 'Tipo de sala creado exitosamente', nuevo_tipo
            
        except IntegrityError:
            session.rollback()
            return False, 'Ya existe un tipo de sala con ese nombre', None
        except Exception as e:
            session.rollback()
            return False, f'Error al crear tipo de sala: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza un tipo de sala existente"""
        session = db.get_session()
        try:
            tipo = session.query(TipoSala).\
                filter(TipoSala.Id == id).first()
            
            if not tipo:
                return False, 'Tipo de sala no encontrado', None
            
            if not data.get('Tipo') or len(data['Tipo'].strip()) < 2:
                return False, 'El tipo de sala debe tener al menos 2 caracteres', None
            if not data.get('PrecioAdulto') or float(data['PrecioAdulto']) <= 0:
                return False, 'El precio para adulto debe ser mayor a 0', None
            if not data.get('PrecioNino') or float(data['PrecioNino']) <= 0:
                return False, 'El precio para niño debe ser mayor a 0', None
            
            existente = session.query(TipoSala).\
                filter(
                    TipoSala.Tipo.ilike(data['Tipo'].strip()),
                    TipoSala.Id != id
                ).first()
            
            if existente:
                return False, 'Ya existe otro tipo de sala con ese nombre', None
            
            tipo.Tipo = data['Tipo'].strip()
            tipo.PrecioAdulto = float(data['PrecioAdulto'])
            tipo.PrecioNino = float(data['PrecioNino'])
            
            if 'Activo' in data:
                tipo.Activo = data['Activo'] == 'on' if isinstance(data['Activo'], str) else bool(data['Activo'])
            
            session.commit()
            return True, 'Tipo de sala actualizado exitosamente', tipo
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar tipo de sala: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina (desactiva) un tipo de sala"""
        session = db.get_session()
        try:
            tipo = session.query(TipoSala).\
                filter(TipoSala.Id == id).first()
            
            if not tipo:
                return False, 'Tipo de sala no encontrado'
            
            salas = session.query(Sala).\
                filter(Sala.IdTipo == id).\
                filter(Sala.Activo == True).count()
            
            if salas > 0:
                return False, f'No se puede eliminar el tipo de sala porque está siendo usado por {salas} sala(s)'
            
            tipo.Activo = False
            session.commit()
            
            return True, 'Tipo de sala eliminado exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar tipo de sala: {str(e)}'
        finally:
            session.close()