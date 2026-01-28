# controllers/tipo_boleto_controller.py
from database import db
from models import TipoBoleto, Boleto
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash

class TipoBoletoController:
    """Controlador para operaciones CRUD de Tipos de Boleto"""

    @staticmethod
    def obtener_todos():
        """Obtiene todos los tipos de boleto activos"""
        session = db.get_session()
        try:
            tipos = session.query(TipoBoleto).\
                filter(TipoBoleto.Activo == True).\
                order_by(TipoBoleto.TipoBoleto).all()
            return tipos
        except Exception as e:
            flash(f'Error al obtener tipos de boleto: {str(e)}', 'danger')
            return []
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene un tipo de boleto por su ID con sus boletos"""
        session = db.get_session()
        try:
            tipo = session.query(TipoBoleto).\
                options(joinedload(TipoBoleto.boletos)).\
                filter(TipoBoleto.Id == id).first()
            
            if tipo and hasattr(tipo, 'boletos'):
                _ = list(tipo.boletos)
            
            return tipo
        except Exception as e:
            flash(f'Error al obtener tipo de boleto: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """Crea un nuevo tipo de boleto"""
        session = db.get_session()
        try:
            if not data.get('TipoBoleto') or len(data['TipoBoleto'].strip()) < 2:
                return False, 'El tipo de boleto debe tener al menos 2 caracteres', None
            
            existente = session.query(TipoBoleto).\
                filter(TipoBoleto.TipoBoleto.ilike(data['TipoBoleto'].strip())).first()
            
            if existente:
                if existente.Activo:
                    return False, 'Ya existe un tipo de boleto con ese nombre', None
                else:
                    existente.Activo = True
                    session.commit()
                    return True, 'Tipo de boleto reactivado exitosamente', existente
            
            nuevo_tipo = TipoBoleto(
                TipoBoleto=data['TipoBoleto'].strip(),
                Activo=True
            )
            
            session.add(nuevo_tipo)
            session.commit()
            return True, 'Tipo de boleto creado exitosamente', nuevo_tipo
            
        except IntegrityError:
            session.rollback()
            return False, 'Ya existe un tipo de boleto con ese nombre', None
        except Exception as e:
            session.rollback()
            return False, f'Error al crear tipo de boleto: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza un tipo de boleto existente"""
        session = db.get_session()
        try:
            tipo = session.query(TipoBoleto).\
                filter(TipoBoleto.Id == id).first()
            
            if not tipo:
                return False, 'Tipo de boleto no encontrado', None
            
            if not data.get('TipoBoleto') or len(data['TipoBoleto'].strip()) < 2:
                return False, 'El tipo de boleto debe tener al menos 2 caracteres', None
            
            existente = session.query(TipoBoleto).\
                filter(
                    TipoBoleto.TipoBoleto.ilike(data['TipoBoleto'].strip()),
                    TipoBoleto.Id != id
                ).first()
            
            if existente:
                return False, 'Ya existe otro tipo de boleto con ese nombre', None
            
            tipo.TipoBoleto = data['TipoBoleto'].strip()
            
            if 'Activo' in data:
                tipo.Activo = data['Activo'] == 'on' if isinstance(data['Activo'], str) else bool(data['Activo'])
            
            session.commit()
            return True, 'Tipo de boleto actualizado exitosamente', tipo
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar tipo de boleto: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina (desactiva) un tipo de boleto"""
        session = db.get_session()
        try:
            tipo = session.query(TipoBoleto).\
                filter(TipoBoleto.Id == id).first()
            
            if not tipo:
                return False, 'Tipo de boleto no encontrado'
            
            boletos = session.query(Boleto).\
                filter(Boleto.IdTipoBoleto == id).count()
            
            if boletos > 0:
                return False, f'No se puede eliminar el tipo de boleto porque está siendo usado por {boletos} boleto(s)'
            
            tipo.Activo = False
            session.commit()
            
            return True, 'Tipo de boleto eliminado exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar tipo de boleto: {str(e)}'
        finally:
            session.close()
    
    @staticmethod
    def obtener_para_select():
        """Obtiene tipos de boleto para usar en selects (comboboxes)"""
        session = db.get_session()
        try:
            tipos = session.query(
                TipoBoleto.Id,
                TipoBoleto.TipoBoleto
            ).filter(
                TipoBoleto.Activo == True
            ).order_by(
                TipoBoleto.TipoBoleto
            ).all()
            
            return [(c.Id, c.TipoBoleto) for c in tipos]
        except Exception as e:
            print(f"Error al obtener tipos de boleto para select: {e}")
            return []
        finally:
            session.close()