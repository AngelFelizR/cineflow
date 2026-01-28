# controllers/boleto_admin_controller.py
from database import db
from models import Boleto, Funcion, Pelicula, Sala, Cine, Asiento, Usuario, TipoBoleto
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash
from datetime import datetime, timedelta

class BoletoAdminController:
    """Controlador para operaciones CRUD de Boletos (Administrador)"""

    @staticmethod
    def obtener_todos_paginados(pagina=1, por_pagina=25, filtros=None):
        """Obtiene boletos con paginación"""
        session = db.get_session()
        try:
            query = session.query(Boleto).\
                options(
                    joinedload(Boleto.funcion).joinedload(Funcion.pelicula),
                    joinedload(Boleto.funcion).joinedload(Funcion.sala).joinedload(Sala.cine),
                    joinedload(Boleto.asiento),
                    joinedload(Boleto.usuario),
                    joinedload(Boleto.tipo_boleto)
                )
            
            # Aplicar filtros si existen
            if filtros:
                if filtros.get('funcion_id'):
                    query = query.filter(Boleto.IdFuncion == filtros['funcion_id'])
                if filtros.get('usuario_id'):
                    query = query.filter(Boleto.IdUsuario == filtros['usuario_id'])
                if filtros.get('fecha_desde'):
                    fecha_desde = datetime.strptime(filtros['fecha_desde'], '%Y-%m-%d')
                    query = query.filter(Boleto.FechaCreacion >= fecha_desde)
                if filtros.get('fecha_hasta'):
                    fecha_hasta = datetime.strptime(filtros['fecha_hasta'], '%Y-%m-%d')
                    fecha_hasta = fecha_hasta.replace(hour=23, minute=59, second=59)
                    query = query.filter(Boleto.FechaCreacion <= fecha_hasta)
            
            # Ordenar por fecha más reciente primero
            query = query.order_by(Boleto.FechaCreacion.desc())
            
            # Paginación
            boletos = query.offset((pagina - 1) * por_pagina).limit(por_pagina).all()
            total = query.count()
            
            return {
                'boletos': boletos,
                'total': total,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'paginas': (total + por_pagina - 1) // por_pagina
            }
        except Exception as e:
            flash(f'Error al obtener boletos: {str(e)}', 'danger')
            return {'boletos': [], 'total': 0, 'pagina': 1, 'por_pagina': por_pagina, 'paginas': 0}
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene un boleto por su ID"""
        session = db.get_session()
        try:
            boleto = session.query(Boleto).\
                options(
                    joinedload(Boleto.funcion).joinedload(Funcion.pelicula),
                    joinedload(Boleto.funcion).joinedload(Funcion.sala).joinedload(Sala.cine),
                    joinedload(Boleto.asiento),
                    joinedload(Boleto.usuario),
                    joinedload(Boleto.tipo_boleto)
                ).\
                filter(Boleto.Id == id).first()
            
            return boleto
        except Exception as e:
            flash(f'Error al obtener boleto: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """Crea un nuevo boleto (administrativo)"""
        session = db.get_session()
        try:
            # Validaciones
            if not data.get('IdFuncion'):
                return False, 'Debe seleccionar una función', None
            if not data.get('IdAsiento'):
                return False, 'Debe seleccionar un asiento', None
            if not data.get('IdUsuario'):
                return False, 'Debe seleccionar un usuario', None
            if not data.get('IdTipoBoleto'):
                return False, 'Debe seleccionar un tipo de boleto', None
            if not data.get('ValorPagado') or float(data['ValorPagado']) <= 0:
                return False, 'El valor pagado debe ser mayor a 0', None
            
            # Verificar que la función exista y esté activa
            funcion = session.query(Funcion).filter(
                Funcion.Id == int(data['IdFuncion']), 
                Funcion.Activo == True
            ).first()
            if not funcion:
                return False, 'La función seleccionada no existe o no está activa', None
            
            # Verificar que el asiento exista y esté activo
            asiento = session.query(Asiento).filter(
                Asiento.Id == int(data['IdAsiento']), 
                Asiento.Activo == True
            ).first()
            if not asiento:
                return False, 'El asiento seleccionado no existe o no está activo', None
            
            # Verificar que el usuario exista
            usuario = session.query(Usuario).filter(
                Usuario.Id == int(data['IdUsuario'])
            ).first()
            if not usuario:
                return False, 'El usuario seleccionado no existe', None
            
            # Verificar que el tipo de boleto exista y esté activo
            tipo_boleto = session.query(TipoBoleto).filter(
                TipoBoleto.Id == int(data['IdTipoBoleto']), 
                TipoBoleto.Activo == True
            ).first()
            if not tipo_boleto:
                return False, 'El tipo de boleto seleccionado no existe o no está activo', None
            
            # Verificar que el asiento esté en la sala de la función
            if asiento.IdSala != funcion.IdSala:
                return False, 'El asiento no pertenece a la sala de la función', None
            
            # Verificar si el asiento ya está ocupado para esta función
            boleto_existente = session.query(Boleto).\
                filter(
                    Boleto.IdFuncion == int(data['IdFuncion']),
                    Boleto.IdAsiento == int(data['IdAsiento'])
                ).first()
            
            if boleto_existente:
                # Verificar si fue cancelado
                from models import BoletoCancelado
                cancelado = session.query(BoletoCancelado).\
                    filter(BoletoCancelado.IdBoleto == boleto_existente.Id).first()
                
                if not cancelado:
                    return False, 'El asiento ya está ocupado para esta función', None
            
            # Crear nuevo
            nuevo_boleto = Boleto(
                IdFuncion=int(data['IdFuncion']),
                IdAsiento=int(data['IdAsiento']),
                IdUsuario=int(data['IdUsuario']),
                IdTipoBoleto=int(data['IdTipoBoleto']),
                ValorPagado=float(data['ValorPagado'])
            )
            
            session.add(nuevo_boleto)
            session.commit()
            return True, 'Boleto creado exitosamente', nuevo_boleto
            
        except IntegrityError:
            session.rollback()
            return False, 'Error de integridad al crear boleto', None
        except Exception as e:
            session.rollback()
            return False, f'Error al crear boleto: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza un boleto existente"""
        session = db.get_session()
        try:
            boleto = session.query(Boleto).\
                filter(Boleto.Id == id).first()
            
            if not boleto:
                return False, 'Boleto no encontrado', None
            
            # Validaciones
            if not data.get('IdFuncion'):
                return False, 'Debe seleccionar una función', None
            if not data.get('IdAsiento'):
                return False, 'Debe seleccionar un asiento', None
            if not data.get('IdUsuario'):
                return False, 'Debe seleccionar un usuario', None
            if not data.get('IdTipoBoleto'):
                return False, 'Debe seleccionar un tipo de boleto', None
            if not data.get('ValorPagado') or float(data['ValorPagado']) <= 0:
                return False, 'El valor pagado debe ser mayor a 0', None
            
            # Verificar que la función exista y esté activa
            funcion = session.query(Funcion).filter(
                Funcion.Id == int(data['IdFuncion']), 
                Funcion.Activo == True
            ).first()
            if not funcion:
                return False, 'La función seleccionada no existe o no está activa', None
            
            # Verificar que el asiento exista y esté activo
            asiento = session.query(Asiento).filter(
                Asiento.Id == int(data['IdAsiento']), 
                Asiento.Activo == True
            ).first()
            if not asiento:
                return False, 'El asiento seleccionado no existe o no está activo', None
            
            # Verificar que el usuario exista
            usuario = session.query(Usuario).filter(
                Usuario.Id == int(data['IdUsuario'])
            ).first()
            if not usuario:
                return False, 'El usuario seleccionado no existe', None
            
            # Verificar que el tipo de boleto exista y esté activo
            tipo_boleto = session.query(TipoBoleto).filter(
                TipoBoleto.Id == int(data['IdTipoBoleto']), 
                TipoBoleto.Activo == True
            ).first()
            if not tipo_boleto:
                return False, 'El tipo de boleto seleccionado no existe o no está activo', None
            
            # Verificar que el asiento esté en la sala de la función
            if asiento.IdSala != funcion.IdSala:
                return False, 'El asiento no pertenece a la sala de la función', None
            
            # Verificar si otro boleto ya ocupa este asiento para esta función
            boleto_existente = session.query(Boleto).\
                filter(
                    Boleto.IdFuncion == int(data['IdFuncion']),
                    Boleto.IdAsiento == int(data['IdAsiento']),
                    Boleto.Id != id
                ).first()
            
            if boleto_existente:
                # Verificar si fue cancelado
                from models import BoletoCancelado
                cancelado = session.query(BoletoCancelado).\
                    filter(BoletoCancelado.IdBoleto == boleto_existente.Id).first()
                
                if not cancelado:
                    return False, 'El asiento ya está ocupado para esta función', None
            
            # Actualizar
            boleto.IdFuncion = int(data['IdFuncion'])
            boleto.IdAsiento = int(data['IdAsiento'])
            boleto.IdUsuario = int(data['IdUsuario'])
            boleto.IdTipoBoleto = int(data['IdTipoBoleto'])
            boleto.ValorPagado = float(data['ValorPagado'])
            
            session.commit()
            return True, 'Boleto actualizado exitosamente', boleto
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar boleto: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina un boleto (solo si no ha sido usado o cancelado)"""
        session = db.get_session()
        try:
            boleto = session.query(Boleto).\
                filter(Boleto.Id == id).first()
            
            if not boleto:
                return False, 'Boleto no encontrado'
            
            # Verificar si el boleto ha sido cancelado
            from models import BoletoCancelado
            cancelado = session.query(BoletoCancelado).\
                filter(BoletoCancelado.IdBoleto == id).first()
            
            if cancelado:
                return False, 'No se puede eliminar un boleto que ha sido cancelado'
            
            # Verificar si el boleto ha sido usado
            from models import BoletoUsado
            usado = session.query(BoletoUsado).\
                filter(BoletoUsado.IdBoleto == id).first()
            
            if usado:
                return False, 'No se puede eliminar un boleto que ha sido usado'
            
            # Eliminar (eliminación física, ya que es un registro de venta)
            session.delete(boleto)
            session.commit()
            
            return True, 'Boleto eliminado exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar boleto: {str(e)}'
        finally:
            session.close()