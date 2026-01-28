# controllers/boleto_cancelado_controller.py
from database import db
from models import BoletoCancelado, Boleto, Funcion, Pelicula, Usuario
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash
from datetime import datetime, timedelta

class BoletoCanceladoController:
    """Controlador para operaciones CRUD de Boletos Cancelados"""

    @staticmethod
    def obtener_todos_paginados(pagina=1, por_pagina=25, filtros=None):
        """Obtiene boletos cancelados con paginación"""
        session = db.get_session()
        try:
            query = session.query(BoletoCancelado).\
                options(
                    joinedload(BoletoCancelado.boleto).joinedload(Boleto.funcion).joinedload(Funcion.pelicula),
                    joinedload(BoletoCancelado.boleto).joinedload(Boleto.usuario)
                )
            
            # Aplicar filtros si existen
            if filtros:
                if filtros.get('usuario_id'):
                    query = query.join(Boleto, BoletoCancelado.IdBoleto == Boleto.Id).\
                        filter(Boleto.IdUsuario == filtros['usuario_id'])
                if filtros.get('fecha_desde'):
                    fecha_desde = datetime.strptime(filtros['fecha_desde'], '%Y-%m-%d')
                    query = query.filter(BoletoCancelado.FechaCancelacion >= fecha_desde)
                if filtros.get('fecha_hasta'):
                    fecha_hasta = datetime.strptime(filtros['fecha_hasta'], '%Y-%m-%d')
                    fecha_hasta = fecha_hasta.replace(hour=23, minute=59, second=59)
                    query = query.filter(BoletoCancelado.FechaCancelacion <= fecha_hasta)
                if filtros.get('canjeado') is not None:
                    query = query.filter(BoletoCancelado.Canjeado == (filtros['canjeado'] == 'true'))
            
            # Ordenar por fecha de cancelación más reciente primero
            query = query.order_by(BoletoCancelado.FechaCancelacion.desc())
            
            # Paginación
            cancelados = query.offset((pagina - 1) * por_pagina).limit(por_pagina).all()
            total = query.count()
            
            return {
                'cancelados': cancelados,
                'total': total,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'paginas': (total + por_pagina - 1) // por_pagina
            }
        except Exception as e:
            flash(f'Error al obtener boletos cancelados: {str(e)}', 'danger')
            return {'cancelados': [], 'total': 0, 'pagina': 1, 'por_pagina': por_pagina, 'paginas': 0}
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene un boleto cancelado por su ID"""
        session = db.get_session()
        try:
            cancelado = session.query(BoletoCancelado).\
                options(
                    joinedload(BoletoCancelado.boleto).joinedload(Boleto.funcion).joinedload(Funcion.pelicula),
                    joinedload(BoletoCancelado.boleto).joinedload(Boleto.usuario)
                ).\
                filter(BoletoCancelado.Id == id).first()
            
            return cancelado
        except Exception as e:
            flash(f'Error al obtener boleto cancelado: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """Crea un nuevo registro de boleto cancelado"""
        session = db.get_session()
        try:
            # Validaciones
            if not data.get('IdBoleto'):
                return False, 'Debe seleccionar un boleto', None
            if not data.get('ValorAcreditado') or float(data['ValorAcreditado']) < 0:
                return False, 'El valor acreditado debe ser mayor o igual a 0', None
            
            # Verificar que el boleto exista
            boleto = session.query(Boleto).filter(Boleto.Id == int(data['IdBoleto'])).first()
            if not boleto:
                return False, 'El boleto seleccionado no existe', None
            
            # Verificar que el boleto no esté ya cancelado
            existente = session.query(BoletoCancelado).\
                filter(BoletoCancelado.IdBoleto == int(data['IdBoleto'])).first()
            
            if existente:
                return False, 'Este boleto ya ha sido cancelado', None
            
            # Verificar que el boleto no haya sido usado
            from models import BoletoUsado
            usado = session.query(BoletoUsado).\
                filter(BoletoUsado.IdBoleto == int(data['IdBoleto'])).first()
            
            if usado:
                return False, 'Este boleto ya ha sido usado', None
            
            # Crear nuevo
            nuevo_cancelado = BoletoCancelado(
                IdBoleto=int(data['IdBoleto']),
                ValorAcreditado=float(data['ValorAcreditado']),
                Canjeado=False
            )
            
            session.add(nuevo_cancelado)
            session.commit()
            return True, 'Boleto cancelado registrado exitosamente', nuevo_cancelado
            
        except IntegrityError:
            session.rollback()
            return False, 'Este boleto ya ha sido cancelado', None
        except Exception as e:
            session.rollback()
            return False, f'Error al registrar boleto cancelado: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza un registro de boleto cancelado"""
        session = db.get_session()
        try:
            cancelado = session.query(BoletoCancelado).\
                filter(BoletoCancelado.Id == id).first()
            
            if not cancelado:
                return False, 'Registro de boleto cancelado no encontrado', None
            
            # Validaciones
            if not data.get('ValorAcreditado') or float(data['ValorAcreditado']) < 0:
                return False, 'El valor acreditado debe ser mayor o igual a 0', None
            
            # Actualizar
            cancelado.ValorAcreditado = float(data['ValorAcreditado'])
            
            if 'Canjeado' in data:
                cancelado.Canjeado = data['Canjeado'] == 'on' if isinstance(data['Canjeado'], str) else bool(data['Canjeado'])
            
            session.commit()
            return True, 'Registro de boleto cancelado actualizado exitosamente', cancelado
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar registro de boleto cancelado: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina un registro de boleto cancelado"""
        session = db.get_session()
        try:
            cancelado = session.query(BoletoCancelado).\
                filter(BoletoCancelado.Id == id).first()
            
            if not cancelado:
                return False, 'Registro de boleto cancelado no encontrado'
            
            # Eliminar (eliminación física)
            session.delete(cancelado)
            session.commit()
            
            return True, 'Registro de boleto cancelado eliminado exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar registro de boleto cancelado: {str(e)}'
        finally:
            session.close()