# controllers/boleto_usado_controller.py
from database import db
from models import BoletoUsado, Boleto, Funcion, Pelicula, Usuario
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash
from datetime import datetime, timedelta

class BoletoUsadoController:
    """Controlador para operaciones CRUD de Boletos Usados"""

    @staticmethod
    def obtener_todos_paginados(pagina=1, por_pagina=25, filtros=None):
        """Obtiene boletos usados con paginación"""
        session = db.get_session()
        try:
            query = session.query(BoletoUsado).\
                options(
                    joinedload(BoletoUsado.boleto).joinedload(Boleto.funcion).joinedload(Funcion.pelicula),
                    joinedload(BoletoUsado.boleto).joinedload(Boleto.usuario),
                    joinedload(BoletoUsado.encargado)
                )
            
            # Aplicar filtros si existen
            if filtros:
                if filtros.get('usuario_id'):
                    query = query.join(Boleto, BoletoUsado.IdBoleto == Boleto.Id).\
                        filter(Boleto.IdUsuario == filtros['usuario_id'])
                if filtros.get('encargado_id'):
                    query = query.filter(BoletoUsado.IdEncargado == filtros['encargado_id'])
                if filtros.get('fecha_desde'):
                    fecha_desde = datetime.strptime(filtros['fecha_desde'], '%Y-%m-%d')
                    query = query.filter(BoletoUsado.FechaUso >= fecha_desde)
                if filtros.get('fecha_hasta'):
                    fecha_hasta = datetime.strptime(filtros['fecha_hasta'], '%Y-%m-%d')
                    fecha_hasta = fecha_hasta.replace(hour=23, minute=59, second=59)
                    query = query.filter(BoletoUsado.FechaUso <= fecha_hasta)
            
            # Ordenar por fecha de uso más reciente primero
            query = query.order_by(BoletoUsado.FechaUso.desc())
            
            # Paginación
            usados = query.offset((pagina - 1) * por_pagina).limit(por_pagina).all()
            total = query.count()
            
            return {
                'usados': usados,
                'total': total,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'paginas': (total + por_pagina - 1) // por_pagina
            }
        except Exception as e:
            flash(f'Error al obtener boletos usados: {str(e)}', 'danger')
            return {'usados': [], 'total': 0, 'pagina': 1, 'por_pagina': por_pagina, 'paginas': 0}
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene un boleto usado por su ID"""
        session = db.get_session()
        try:
            usado = session.query(BoletoUsado).\
                options(
                    joinedload(BoletoUsado.boleto).joinedload(Boleto.funcion).joinedload(Funcion.pelicula),
                    joinedload(BoletoUsado.boleto).joinedload(Boleto.usuario),
                    joinedload(BoletoUsado.encargado)
                ).\
                filter(BoletoUsado.Id == id).first()
            
            return usado
        except Exception as e:
            flash(f'Error al obtener boleto usado: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """Crea un nuevo registro de boleto usado"""
        session = db.get_session()
        try:
            # Validaciones
            if not data.get('IdBoleto'):
                return False, 'Debe seleccionar un boleto', None
            if not data.get('IdEncargado'):
                return False, 'Debe seleccionar un encargado', None
            
            # Verificar que el boleto exista
            boleto = session.query(Boleto).filter(Boleto.Id == int(data['IdBoleto'])).first()
            if not boleto:
                return False, 'El boleto seleccionado no existe', None
            
            # Verificar que el boleto no esté cancelado
            from models import BoletoCancelado
            cancelado = session.query(BoletoCancelado).\
                filter(BoletoCancelado.IdBoleto == int(data['IdBoleto'])).first()
            
            if cancelado:
                return False, 'Este boleto ha sido cancelado', None
            
            # Verificar que el boleto no haya sido usado ya
            existente = session.query(BoletoUsado).\
                filter(BoletoUsado.IdBoleto == int(data['IdBoleto'])).first()
            
            if existente:
                return False, 'Este boleto ya ha sido usado', None
            
            # Verificar que el encargado exista y sea un encargado de entrada
            encargado = session.query(Usuario).filter(Usuario.Id == int(data['IdEncargado'])).first()
            if not encargado:
                return False, 'El encargado seleccionado no existe', None
            
            from models import RolUsuario
            rol_encargado = session.query(RolUsuario).filter(RolUsuario.Rol == "Encargado de Entrada").first()
            if not rol_encargado or encargado.IdRol != rol_encargado.Id:
                return False, 'El usuario seleccionado no es un encargado de entrada', None
            
            # Crear nuevo
            nuevo_usado = BoletoUsado(
                IdBoleto=int(data['IdBoleto']),
                IdEncargado=int(data['IdEncargado'])
            )
            
            session.add(nuevo_usado)
            session.commit()
            return True, 'Boleto usado registrado exitosamente', nuevo_usado
            
        except IntegrityError:
            session.rollback()
            return False, 'Este boleto ya ha sido usado', None
        except Exception as e:
            session.rollback()
            return False, f'Error al registrar boleto usado: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza un registro de boleto usado"""
        session = db.get_session()
        try:
            usado = session.query(BoletoUsado).\
                filter(BoletoUsado.Id == id).first()
            
            if not usado:
                return False, 'Registro de boleto usado no encontrado', None
            
            # Validaciones
            if not data.get('IdEncargado'):
                return False, 'Debe seleccionar un encargado', None
            
            # Verificar que el encargado exista y sea un encargado de entrada
            encargado = session.query(Usuario).filter(Usuario.Id == int(data['IdEncargado'])).first()
            if not encargado:
                return False, 'El encargado seleccionado no existe', None
            
            from models import RolUsuario
            rol_encargado = session.query(RolUsuario).filter(RolUsuario.Rol == "Encargado de Entrada").first()
            if not rol_encargado or encargado.IdRol != rol_encargado.Id:
                return False, 'El usuario seleccionado no es un encargado de entrada', None
            
            # Actualizar
            usado.IdEncargado = int(data['IdEncargado'])
            
            session.commit()
            return True, 'Registro de boleto usado actualizado exitosamente', usado
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar registro de boleto usado: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina un registro de boleto usado"""
        session = db.get_session()
        try:
            usado = session.query(BoletoUsado).\
                filter(BoletoUsado.Id == id).first()
            
            if not usado:
                return False, 'Registro de boleto usado no encontrado'
            
            # Eliminar (eliminación física)
            session.delete(usado)
            session.commit()
            
            return True, 'Registro de boleto usado eliminado exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar registro de boleto usado: {str(e)}'
        finally:
            session.close()