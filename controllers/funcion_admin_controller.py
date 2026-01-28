# controllers/funcion_admin_controller.py
from database import db
from models import Funcion, Pelicula, Sala, Cine, TipoSala, Asiento, Boleto, BoletoCancelado, BoletoUsado
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash
from datetime import datetime, timedelta

class FuncionAdminController:
    """Controlador para operaciones CRUD de Funciones (Administrador)"""

    @staticmethod
    def obtener_todas_paginadas(pagina=1, por_pagina=25, filtros=None):
        """Obtiene funciones con paginación"""
        session = db.get_session()
        try:
            query = session.query(Funcion).\
                options(
                    joinedload(Funcion.pelicula),
                    joinedload(Funcion.sala).joinedload(Sala.cine),
                    joinedload(Funcion.sala).joinedload(Sala.tipo_sala)
                ).\
                filter(Funcion.Activo == True)
            
            # Aplicar filtros si existen
            if filtros:
                if filtros.get('pelicula_id'):
                    query = query.filter(Funcion.IdPelicula == filtros['pelicula_id'])
                if filtros.get('sala_id'):
                    query = query.filter(Funcion.IdSala == filtros['sala_id'])
                if filtros.get('fecha_desde'):
                    fecha_desde = datetime.strptime(filtros['fecha_desde'], '%Y-%m-%d')
                    query = query.filter(Funcion.FechaHora >= fecha_desde)
                if filtros.get('fecha_hasta'):
                    fecha_hasta = datetime.strptime(filtros['fecha_hasta'], '%Y-%m-%d')
                    fecha_hasta = fecha_hasta.replace(hour=23, minute=59, second=59)
                    query = query.filter(Funcion.FechaHora <= fecha_hasta)
            
            # Ordenar por fecha más reciente primero
            query = query.order_by(Funcion.FechaHora.desc())
            
            # Paginación
            funciones = query.offset((pagina - 1) * por_pagina).limit(por_pagina).all()
            total = query.count()
            
            return {
                'funciones': funciones,
                'total': total,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'paginas': (total + por_pagina - 1) // por_pagina
            }
        except Exception as e:
            flash(f'Error al obtener funciones: {str(e)}', 'danger')
            return {'funciones': [], 'total': 0, 'pagina': 1, 'por_pagina': por_pagina, 'paginas': 0}
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene una función por su ID"""
        session = db.get_session()
        try:
            funcion = session.query(Funcion).\
                options(
                    joinedload(Funcion.pelicula),
                    joinedload(Funcion.sala).joinedload(Sala.cine),
                    joinedload(Funcion.sala).joinedload(Sala.tipo_sala)
                ).\
                filter(Funcion.Id == id).first()
            
            return funcion
        except Exception as e:
            flash(f'Error al obtener función: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """Crea una nueva función"""
        session = db.get_session()
        try:
            # Validaciones
            if not data.get('IdPelicula'):
                return False, 'Debe seleccionar una película', None
            if not data.get('IdSala'):
                return False, 'Debe seleccionar una sala', None
            if not data.get('FechaHora'):
                return False, 'La fecha y hora son requeridas', None
            
            # Parsear fecha y hora
            try:
                fecha_hora = datetime.strptime(data['FechaHora'], '%Y-%m-%dT%H:%M')
            except ValueError:
                return False, 'Formato de fecha y hora inválido. Use YYYY-MM-DDTHH:MM', None
            
            # Verificar que la fecha no sea en el pasado
            if fecha_hora < datetime.now():
                return False, 'No se pueden crear funciones en el pasado', None
            
            # Verificar que la película exista y esté activa
            pelicula = session.query(Pelicula).filter(
                Pelicula.Id == int(data['IdPelicula']), 
                Pelicula.Activo == True
            ).first()
            if not pelicula:
                return False, 'La película seleccionada no existe o no está activa', None
            
            # Verificar que la sala exista y esté activa
            sala = session.query(Sala).filter(
                Sala.Id == int(data['IdSala']), 
                Sala.Activo == True
            ).first()
            if not sala:
                return False, 'La sala seleccionada no existe o no está activa', None
            
            # Verificar si hay solapamiento de funciones en la misma sala
            # Considerar duración de la película (margen de 30 minutos entre funciones)
            duracion_total = pelicula.DuracionMinutos + 30  # Película + limpieza/preparación
            
            inicio_funcion = fecha_hora
            fin_funcion = fecha_hora + timedelta(minutes=duracion_total)
            
            # CORRECCIÓN: Obtener las funciones existentes y verificar solapamiento en Python
            funciones_existentes = session.query(Funcion).\
                join(Pelicula, Funcion.IdPelicula == Pelicula.Id).\
                filter(Funcion.IdSala == int(data['IdSala'])).\
                filter(Funcion.Activo == True).all()
            
            solapamiento = False
            for funcion_existente in funciones_existentes:
                # Calcular duración de la función existente
                duracion_existente = funcion_existente.pelicula.DuracionMinutos + 30
                
                # Calcular inicio y fin de la función existente
                inicio_existente = funcion_existente.FechaHora
                fin_existente = inicio_existente + timedelta(minutes=duracion_existente)
                
                # Verificar solapamiento
                if (inicio_funcion < fin_existente) and (fin_funcion > inicio_existente):
                    solapamiento = True
                    break
            
            if solapamiento:
                return False, 'La sala ya tiene una función programada en ese horario', None
            
            # Crear nueva función
            nueva_funcion = Funcion(
                IdPelicula=int(data['IdPelicula']),
                IdSala=int(data['IdSala']),
                FechaHora=fecha_hora,
                Activo=True
            )
            
            session.add(nueva_funcion)
            session.commit()
            return True, 'Función creada exitosamente', nueva_funcion
            
        except IntegrityError:
            session.rollback()
            return False, 'Error de integridad al crear función', None
        except Exception as e:
            session.rollback()
            return False, f'Error al crear función: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza una función existente"""
        session = db.get_session()
        try:
            funcion = session.query(Funcion).\
                filter(Funcion.Id == id).first()
            
            if not funcion:
                return False, 'Función no encontrada', None
            
            # Validaciones
            if not data.get('IdPelicula'):
                return False, 'Debe seleccionar una película', None
            if not data.get('IdSala'):
                return False, 'Debe seleccionar una sala', None
            if not data.get('FechaHora'):
                return False, 'La fecha y hora son requeridas', None
            
            # Parsear fecha y hora
            try:
                fecha_hora = datetime.strptime(data['FechaHora'], '%Y-%m-%dT%H:%M')
            except ValueError:
                return False, 'Formato de fecha y hora inválido. Use YYYY-MM-DDTHH:MM', None
            
            # Verificar que la fecha no sea en el pasado (solo si se cambia)
            if fecha_hora != funcion.FechaHora and fecha_hora < datetime.now():
                return False, 'No se pueden programar funciones en el pasado', None
            
            # Verificar que la película exista y esté activa
            pelicula = session.query(Pelicula).filter(
                Pelicula.Id == int(data['IdPelicula']), 
                Pelicula.Activo == True
            ).first()
            if not pelicula:
                return False, 'La película seleccionada no existe o no está activa', None
            
            # Verificar que la sala exista y esté activa
            sala = session.query(Sala).filter(
                Sala.Id == int(data['IdSala']), 
                Sala.Activo == True
            ).first()
            if not sala:
                return False, 'La sala seleccionada no existe o no está activa', None
            
            # Verificar si hay solapamiento de funciones en la misma sala (excluyendo esta función)
            duracion_total = pelicula.DuracionMinutos + 30
            
            inicio_funcion = fecha_hora
            fin_funcion = fecha_hora + timedelta(minutes=duracion_total)
            
            # CORRECCIÓN: Obtener funciones existentes (excluyendo esta) y verificar en Python
            funciones_existentes = session.query(Funcion).\
                join(Pelicula, Funcion.IdPelicula == Pelicula.Id).\
                filter(Funcion.IdSala == int(data['IdSala'])).\
                filter(Funcion.Activo == True).\
                filter(Funcion.Id != id).all()
            
            solapamiento = False
            for funcion_existente in funciones_existentes:
                # Calcular duración de la función existente
                duracion_existente = funcion_existente.pelicula.DuracionMinutos + 30
                
                # Calcular inicio y fin de la función existente
                inicio_existente = funcion_existente.FechaHora
                fin_existente = inicio_existente + timedelta(minutes=duracion_existente)
                
                # Verificar solapamiento
                if (inicio_funcion < fin_existente) and (fin_funcion > inicio_existente):
                    solapamiento = True
                    break
            
            if solapamiento:
                return False, 'La sala ya tiene otra función programada en ese horario', None
            
            # Actualizar
            funcion.IdPelicula = int(data['IdPelicula'])
            funcion.IdSala = int(data['IdSala'])
            funcion.FechaHora = fecha_hora
            
            if 'Activo' in data:
                funcion.Activo = data['Activo'] == 'on' if isinstance(data['Activo'], str) else bool(data['Activo'])
            
            session.commit()
            return True, 'Función actualizada exitosamente', funcion
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar función: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina (desactiva) una función"""
        session = db.get_session()
        try:
            funcion = session.query(Funcion).\
                filter(Funcion.Id == id).first()
            
            if not funcion:
                return False, 'Función no encontrada'
            
            # Verificar si hay boletos vendidos para esta función
            boletos = session.query(Boleto).\
                filter(Boleto.IdFuncion == id).count()
            
            if boletos > 0:
                return False, f'No se puede eliminar la función porque tiene {boletos} boleto(s) vendido(s)'
            
            # Desactivar (eliminación lógica)
            funcion.Activo = False
            session.commit()
            
            return True, 'Función eliminada exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar función: {str(e)}'
        finally:
            session.close()
    
    @staticmethod
    def obtener_estadisticas_boletos(funcion_id):
        """Obtiene estadísticas de boletos para una función"""
        session = db.get_session()
        try:            
            # Boletos vendidos para esta función
            boletos = session.query(Boleto).\
                options(
                    joinedload(Boleto.usuario),
                    joinedload(Boleto.asiento),
                    joinedload(Boleto.tipo_boleto)
                ).\
                filter(Boleto.IdFuncion == funcion_id).all()
            
            # Contar por tipo
            boletos_vendidos = len(boletos)
            boletos_adultos = sum(1 for b in boletos if b.tipo_boleto and b.tipo_boleto.TipoBoleto == 'Adulto')
            boletos_ninos = sum(1 for b in boletos if b.tipo_boleto and b.tipo_boleto.TipoBoleto == 'Niño')
            
            # Boletos cancelados
            boletos_cancelados = session.query(BoletoCancelado).\
                join(Boleto, BoletoCancelado.IdBoleto == Boleto.Id).\
                filter(Boleto.IdFuncion == funcion_id).count()
            
            # Boletos usados
            boletos_usados = session.query(BoletoUsado).\
                join(Boleto, BoletoUsado.IdBoleto == Boleto.Id).\
                filter(Boleto.IdFuncion == funcion_id).count()
            
            # Calcular ingresos
            ingresos_totales = sum(b.ValorPagado for b in boletos)
            ingresos_adultos = sum(b.ValorPagado for b in boletos if b.tipo_boleto and b.tipo_boleto.TipoBoleto == 'Adulto')
            ingresos_ninos = sum(b.ValorPagado for b in boletos if b.tipo_boleto and b.tipo_boleto.TipoBoleto == 'Niño')
            
            # Calcular capacidad de la sala
            funcion = session.query(Funcion).\
                options(joinedload(Funcion.sala)).\
                filter(Funcion.Id == funcion_id).first()
            
            capacidad_total = 0
            if funcion and funcion.sala:
                # Contar asientos activos directamente
                capacidad_total = session.query(Asiento).\
                    filter(Asiento.IdSala == funcion.sala.Id, Asiento.Activo == True).count()
                
            asientos_disponibles = capacidad_total - boletos_vendidos
            porcentaje_ocupacion = (boletos_vendidos / capacidad_total * 100) if capacidad_total > 0 else 0
            
            # Porcentajes
            porcentaje_adultos = (boletos_adultos / boletos_vendidos * 100) if boletos_vendidos > 0 else 0
            porcentaje_ninos = (boletos_ninos / boletos_vendidos * 100) if boletos_vendidos > 0 else 0
            
            return {
                'boletos': boletos,
                'boletos_vendidos': boletos_vendidos,
                'boletos_adultos': boletos_adultos,
                'boletos_ninos': boletos_ninos,
                'boletos_cancelados': boletos_cancelados,
                'boletos_usados': boletos_usados,
                'ingresos_totales': ingresos_totales,
                'ingresos_adultos': ingresos_adultos,
                'ingresos_ninos': ingresos_ninos,
                'capacidad_total': capacidad_total,
                'asientos_disponibles': asientos_disponibles,
                'porcentaje_ocupacion': porcentaje_ocupacion,
                'porcentaje_adultos': porcentaje_adultos,
                'porcentaje_ninos': porcentaje_ninos
            }
            
        except Exception as e:
            print(f"Error al obtener estadísticas de boletos: {e}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def obtener_funciones_con_estadisticas(funciones_list):
        """Agrega estadísticas a una lista de funciones"""
        session = db.get_session()
        try:
            for funcion in funciones_list:
                # Contar boletos vendidos
                total_boletos = session.query(Boleto).\
                    filter(Boleto.IdFuncion == funcion.Id).count()
                
                # Obtener capacidad de la sala - SOLUCIÓN SIMPLE
                capacidad = 0
                if funcion.sala:
                    capacidad = session.query(Asiento).\
                        filter(Asiento.IdSala == funcion.sala.Id, Asiento.Activo == True).count()
                
                # Calcular ocupación
                if capacidad > 0:
                    ocupacion = (total_boletos / capacidad * 100)
                else:
                    ocupacion = 0
                
                # Agregar estadísticas
                funcion.total_boletos = total_boletos
                funcion.boletos_vendidos = total_boletos
                funcion.asientos_disponibles = max(0, capacidad - total_boletos)
                funcion.ocupacion = round(ocupacion, 2)
            
            return funciones_list
            
        except Exception as e:
            print(f"Error al obtener estadísticas de funciones: {e}")
            for funcion in funciones_list:
                if not hasattr(funcion, 'total_boletos'):
                    funcion.total_boletos = 0
                if not hasattr(funcion, 'boletos_vendidos'):
                    funcion.boletos_vendidos = 0
                if not hasattr(funcion, 'asientos_disponibles'):
                    funcion.asientos_disponibles = 0
                if not hasattr(funcion, 'ocupacion'):
                    funcion.ocupacion = 0.0
            return funciones_list
        finally:
            session.close()