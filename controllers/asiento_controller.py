# controllers/asiento_controller.py
from database import db
from models import Asiento, Sala
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash, request

class AsientoController:
    """Controlador para operaciones CRUD de Asientos"""

    @staticmethod
    def obtener_todos_paginados(pagina=1, por_pagina=25, filtros=None):
        """Obtiene asientos con paginación"""
        session = db.get_session()
        try:
            query = session.query(Asiento).\
                options(joinedload(Asiento.sala)).\
                filter(Asiento.Activo == True)
            
            # Aplicar filtros si existen
            if filtros:
                if filtros.get('sala_id'):
                    query = query.filter(Asiento.IdSala == filtros['sala_id'])
                if filtros.get('codigo'):
                    query = query.filter(Asiento.CodigoAsiento.ilike(f'%{filtros["codigo"]}%'))
            
            # Ordenar por sala y código de asiento
            query = query.order_by(Asiento.IdSala, Asiento.CodigoAsiento)
            
            # Paginación
            asientos = query.offset((pagina - 1) * por_pagina).limit(por_pagina).all()
            total = query.count()
            
            return {
                'asientos': asientos,
                'total': total,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'paginas': (total + por_pagina - 1) // por_pagina
            }
        except Exception as e:
            flash(f'Error al obtener asientos: {str(e)}', 'danger')
            return {'asientos': [], 'total': 0, 'pagina': 1, 'por_pagina': por_pagina, 'paginas': 0}
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene un asiento por su ID"""
        session = db.get_session()
        try:
            asiento = session.query(Asiento).\
                options(joinedload(Asiento.sala)).\
                filter(Asiento.Id == id).first()
            
            return asiento
        except Exception as e:
            flash(f'Error al obtener asiento: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """Crea un nuevo asiento"""
        session = db.get_session()
        try:
            # Validaciones
            if not data.get('IdSala'):
                return False, 'Debe seleccionar una sala', None
            if not data.get('CodigoAsiento') or len(data['CodigoAsiento'].strip()) < 1:
                return False, 'El código del asiento es requerido', None
            
            # Verificar que la sala exista y esté activa
            sala = session.query(Sala).filter(Sala.Id == int(data['IdSala']), Sala.Activo == True).first()
            if not sala:
                return False, 'La sala seleccionada no existe o no está activa', None
            
            # Verificar si ya existe un asiento con ese código en la misma sala
            existente = session.query(Asiento).\
                filter(
                    Asiento.IdSala == int(data['IdSala']),
                    Asiento.CodigoAsiento == data['CodigoAsiento'].strip()
                ).first()
            
            if existente:
                if existente.Activo:
                    return False, 'Ya existe un asiento con ese código en esta sala', None
                else:
                    # Reactivar el existente
                    existente.Activo = True
                    session.commit()
                    return True, 'Asiento reactivado exitosamente', existente
            
            # Crear nuevo
            nuevo_asiento = Asiento(
                IdSala=int(data['IdSala']),
                CodigoAsiento=data['CodigoAsiento'].strip(),
                Activo=True
            )
            
            session.add(nuevo_asiento)
            session.commit()
            return True, 'Asiento creado exitosamente', nuevo_asiento
            
        except IntegrityError:
            session.rollback()
            return False, 'Ya existe un asiento con ese código en esta sala', None
        except Exception as e:
            session.rollback()
            return False, f'Error al crear asiento: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza un asiento existente"""
        session = db.get_session()
        try:
            asiento = session.query(Asiento).\
                filter(Asiento.Id == id).first()
            
            if not asiento:
                return False, 'Asiento no encontrado', None
            
            # Validaciones
            if not data.get('IdSala'):
                return False, 'Debe seleccionar una sala', None
            if not data.get('CodigoAsiento') or len(data['CodigoAsiento'].strip()) < 1:
                return False, 'El código del asiento es requerido', None
            
            # Verificar que la sala exista y esté activa
            sala = session.query(Sala).filter(Sala.Id == int(data['IdSala']), Sala.Activo == True).first()
            if not sala:
                return False, 'La sala seleccionada no existe o no está activa', None
            
            # Verificar si ya existe otro asiento con ese código en la misma sala
            existente = session.query(Asiento).\
                filter(
                    Asiento.IdSala == int(data['IdSala']),
                    Asiento.CodigoAsiento == data['CodigoAsiento'].strip(),
                    Asiento.Id != id
                ).first()
            
            if existente:
                return False, 'Ya existe otro asiento con ese código en esta sala', None
            
            # Actualizar
            asiento.IdSala = int(data['IdSala'])
            asiento.CodigoAsiento = data['CodigoAsiento'].strip()
            
            if 'Activo' in data:
                asiento.Activo = data['Activo'] == 'on' if isinstance(data['Activo'], str) else bool(data['Activo'])
            
            session.commit()
            return True, 'Asiento actualizado exitosamente', asiento
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar asiento: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina (desactiva) un asiento"""
        session = db.get_session()
        try:
            asiento = session.query(Asiento).\
                filter(Asiento.Id == id).first()
            
            if not asiento:
                return False, 'Asiento no encontrado'
            
            # Verificar si hay boletos usando este asiento
            from models import Boleto
            boletos = session.query(Boleto).\
                filter(Boleto.IdAsiento == id).count()
            
            if boletos > 0:
                return False, f'No se puede eliminar el asiento porque está siendo usado por {boletos} boleto(s)'
            
            # Desactivar (eliminación lógica)
            asiento.Activo = False
            session.commit()
            
            return True, 'Asiento eliminado exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar asiento: {str(e)}'
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_sala(sala_id):
        """Obtiene todos los asientos de una sala"""
        session = db.get_session()
        try:
            asientos = session.query(Asiento).\
                filter(Asiento.IdSala == sala_id, Asiento.Activo == True).\
                order_by(Asiento.CodigoAsiento).all()
            return asientos
        except Exception as e:
            print(f"Error al obtener asientos por sala: {e}")
            return []
        finally:
            session.close()