# controllers/boleto_controller.py
from database import db
from models import Funcion, Sala, Asiento, Boleto, BoletoCancelado, TipoBoleto, Pelicula, Cine, BoletoUsado
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from datetime import datetime, timedelta
import traceback


class BoletoController:
    @staticmethod
    def crear_boletos(funcion_id: int, usuario_id: int, asientos_seleccionados: list, tipos_asientos: dict):
        """
        Crea boletos en la base de datos para una función
        
        Args:
            funcion_id: ID de la función
            usuario_id: ID del usuario que compra
            asientos_seleccionados: Lista de códigos de asientos seleccionados
            tipos_asientos: Diccionario con código_asiento -> tipo ('adulto' o 'nino')
            
        Returns:
            tuple: (success: bool, message: str, boletos_creados: list or None)
        """
        session = db.get_session()
        
        try:
            # Obtener la función con la sala y tipo de sala
            funcion = session.query(Funcion).options(
                joinedload(Funcion.sala).joinedload(Sala.tipo_sala)
            ).filter(Funcion.Id == funcion_id).first()
            
            if not funcion:
                return False, "La función no existe", None
            
            # Obtener IDs de tipos de boleto
            tipo_adulto = session.query(TipoBoleto).filter_by(TipoBoleto="Adulto").first()
            tipo_nino = session.query(TipoBoleto).filter_by(TipoBoleto="Niño").first()
            
            if not tipo_adulto or not tipo_nino:
                return False, "Error en tipos de boleto", None
            
            # Verificar que todos los asientos estén disponibles
            for codigo_asiento in asientos_seleccionados:
                # Buscar el asiento por código en la sala
                asiento = session.query(Asiento).filter_by(
                    IdSala=funcion.IdSala,
                    CodigoAsiento=codigo_asiento
                ).first()
                
                if not asiento:
                    return False, f"Asiento {codigo_asiento} no encontrado", None
                
                if not asiento.Activo:
                    return False, f"Asiento {codigo_asiento} no está activo", None
                
                # Verificar si ya está vendido (y no cancelado)
                boleto_existente = session.query(Boleto).filter_by(
                    IdFuncion=funcion_id,
                    IdAsiento=asiento.Id
                ).first()
                
                if boleto_existente:
                    # Verificar si fue cancelado
                    boleto_cancelado = session.query(BoletoCancelado).filter_by(
                        IdBoleto=boleto_existente.Id
                    ).first()
                    
                    if not boleto_cancelado:
                        return False, f"Asiento {codigo_asiento} ya está ocupado", None
            
            boletos_creados = []
            
            # Crear boletos
            for codigo_asiento in asientos_seleccionados:
                # Obtener el asiento
                asiento = session.query(Asiento).filter_by(
                    IdSala=funcion.IdSala,
                    CodigoAsiento=codigo_asiento
                ).first()
                
                # Determinar precio según tipo
                tipo = tipos_asientos.get(codigo_asiento, 'adulto')
                if tipo == 'nino':
                    id_tipo_boleto = tipo_nino.Id
                    precio = funcion.sala.tipo_sala.PrecioNino
                else:
                    id_tipo_boleto = tipo_adulto.Id
                    precio = funcion.sala.tipo_sala.PrecioAdulto
                
                # Crear boleto
                boleto = Boleto(
                    IdFuncion=funcion_id,
                    IdAsiento=asiento.Id,
                    IdUsuario=usuario_id,
                    IdTipoBoleto=id_tipo_boleto,
                    ValorPagado=float(precio)
                )
                
                session.add(boleto)
                session.flush()  # Para obtener el ID
                boletos_creados.append(boleto.Id)
            
            # Confirmar transacción
            session.commit()
            
            return True, f"{len(boletos_creados)} boletos creados exitosamente", boletos_creados
            
        except Exception as e:
            session.rollback()
            print(f"Error al crear boletos: {e}")
            return False, f"Error al crear boletos: {str(e)}", None
            
        finally:
            session.close()

    @staticmethod
    def obtener_boletos_usuario(usuario_id: int):
        """
        Obtiene los boletos del usuario que no están cancelados ni usados,
        organizados por película, función y tipo de boleto
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            dict: Diccionario con boletos organizados
        """
        session = db.get_session()
        try:
            # Subconsultas para boletos cancelados y usados
            subquery_cancelados = session.query(BoletoCancelado.IdBoleto).subquery()
            subquery_usados = session.query(BoletoUsado.IdBoleto).subquery()
            
            # Consulta principal: boletos del usuario que no están cancelados ni usados
            boletos = session.query(Boleto).options(
                joinedload(Boleto.funcion).joinedload(Funcion.pelicula),
                joinedload(Boleto.funcion).joinedload(Funcion.sala).joinedload(Sala.cine),
                joinedload(Boleto.asiento),
                joinedload(Boleto.tipo_boleto)
            ).filter(
                Boleto.IdUsuario == usuario_id,
                ~Boleto.Id.in_(subquery_cancelados),
                ~Boleto.Id.in_(subquery_usados),
                Funcion.FechaHora > datetime.now()  # Solo funciones futuras
            ).order_by(
                Funcion.FechaHora.asc()
            ).all()
            
            if not boletos:
                return {}
            
            # Organizar por película -> función -> tipo de boleto
            boletos_organizados = {}
            
            for boleto in boletos:
                pelicula_id = boleto.funcion.IdPelicula
                funcion_id = boleto.funcion.Id
                tipo_boleto_id = boleto.tipo_boleto.Id
                
                # Inicializar estructura si no existe
                if pelicula_id not in boletos_organizados:
                    boletos_organizados[pelicula_id] = {
                        'pelicula_info': {
                            'id': boleto.funcion.pelicula.Id,
                            'titulo': boleto.funcion.pelicula.Titulo,
                            'link_to_bajante': boleto.funcion.pelicula.LinkToBajante
                        },
                        'funciones': {}
                    }
                
                if funcion_id not in boletos_organizados[pelicula_id]['funciones']:
                    boletos_organizados[pelicula_id]['funciones'][funcion_id] = {
                        'funcion_info': {
                            'id': boleto.funcion.Id,
                            'fecha_hora': boleto.funcion.FechaHora,
                            'cine': boleto.funcion.sala.cine.Cine,
                            'sala_numero': boleto.funcion.sala.NumeroDeSala
                        },
                        'tipos_boletos': {}
                    }
                
                if tipo_boleto_id not in boletos_organizados[pelicula_id]['funciones'][funcion_id]['tipos_boletos']:
                    boletos_organizados[pelicula_id]['funciones'][funcion_id]['tipos_boletos'][tipo_boleto_id] = {
                        'tipo_boleto_info': {
                            'id': boleto.tipo_boleto.Id,
                            'nombre': boleto.tipo_boleto.TipoBoleto
                        },
                        'boletos': []
                    }
                
                # Agregar boleto específico
                boletos_organizados[pelicula_id]['funciones'][funcion_id]['tipos_boletos'][tipo_boleto_id]['boletos'].append({
                    'id': boleto.Id,
                    'asiento': boleto.asiento.CodigoAsiento,
                    'valor_pagado': float(boleto.ValorPagado),
                    'fecha_compra': boleto.FechaCreacion
                })
            
            return boletos_organizados
            
        except Exception as e:
            print(f"Error al obtener boletos del usuario: {e}")
            traceback.print_exc()
            return {}
        finally:
            session.close()

    @staticmethod
    def obtener_saldo_usuario(usuario_id: int) -> float:
        """
        Obtiene el saldo disponible del usuario (suma de ValorAcreditado 
        de boletos cancelados en los últimos 3 meses que no han sido canjeados)
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            float: Saldo disponible
        """
        session = db.get_session()
        try:
            # Fecha límite: 3 meses atrás desde hoy
            fecha_limite = datetime.now() - timedelta(days=90)
            
            # Consulta para obtener el saldo disponible
            saldo = session.query(
                func.sum(BoletoCancelado.ValorAcreditado)
            ).join(
                Boleto, BoletoCancelado.IdBoleto == Boleto.Id
            ).filter(
                Boleto.IdUsuario == usuario_id,
                BoletoCancelado.Canjeado == False,
                BoletoCancelado.FechaCancelacion >= fecha_limite
            ).scalar()
            
            return float(saldo) if saldo else 0.0
            
        except Exception as e:
            print(f"Error al obtener saldo del usuario: {e}")
            traceback.print_exc()
            return 0.0
        finally:
            session.close()

    @staticmethod
    def cancelar_boletos(boletos_ids: list, usuario_id: int):
        """
        Cancela una lista de boletos del usuario
        
        Args:
            boletos_ids: Lista de IDs de boletos a cancelar
            usuario_id: ID del usuario que realiza la cancelación
            
        Returns:
            tuple: (success: bool, message: str, total_acreditado: float)
        """
        session = db.get_session()
        try:
            if not boletos_ids:
                return False, "No se han seleccionado boletos para cancelar", 0.0
            
            total_acreditado = 0.0
            boletos_cancelados = []
            errores = []
            
            for boleto_id in boletos_ids:
                # Verificar que el boleto existe y pertenece al usuario
                boleto = session.query(Boleto).options(
                    joinedload(Boleto.funcion)
                ).filter(
                    Boleto.Id == boleto_id,
                    Boleto.IdUsuario == usuario_id
                ).first()
                
                if not boleto:
                    errores.append(f"Boleto {boleto_id} no encontrado o no te pertenece")
                    continue
                
                # Verificar que no esté cancelado
                cancelado = session.query(BoletoCancelado).filter_by(IdBoleto=boleto_id).first()
                if cancelado:
                    errores.append(f"Boleto {boleto_id} ya ha sido cancelado")
                    continue
                
                # Verificar que no esté usado
                usado = session.query(BoletoUsado).filter_by(IdBoleto=boleto_id).first()
                if usado:
                    errores.append(f"Boleto {boleto_id} ya ha sido usado")
                    continue
                
                # Verificar que la función no haya comenzado
                if boleto.funcion.FechaHora <= datetime.now():
                    errores.append(f"Boleto {boleto_id} no se puede cancelar porque la función ya comenzó")
                    continue
                
                # Calcular valor acreditado (100% si es 2+ horas antes, 50% si es menos)
                tiempo_restante = boleto.funcion.FechaHora - datetime.now()
                horas_restantes = tiempo_restante.total_seconds() / 3600
                
                if horas_restantes >= 2:
                    valor_acreditado = float(boleto.ValorPagado)
                else:
                    valor_acreditado = float(boleto.ValorPagado) * 0.5
                
                # Crear registro de cancelación
                boleto_cancelado = BoletoCancelado(
                    IdBoleto=boleto_id,
                    ValorAcreditado=valor_acreditado,
                    Canjeado=False
                )
                
                session.add(boleto_cancelado)
                total_acreditado += valor_acreditado
                boletos_cancelados.append(boleto_id)
            
            if errores:
                session.rollback()
                return False, "; ".join(errores), 0.0
            
            if not boletos_cancelados:
                return False, "No se pudo cancelar ningún boleto", 0.0
            
            # Confirmar transacción
            session.commit()
            
            mensaje = f"{len(boletos_cancelados)} boleto(s) cancelado(s) exitosamente. Se ha acreditado ${total_acreditado:.2f} a tu saldo."
            return True, mensaje, total_acreditado
            
        except Exception as e:
            session.rollback()
            print(f"Error al cancelar boletos: {e}")
            traceback.print_exc()
            return False, f"Error al cancelar boletos: {str(e)}", 0.0
        finally:
            session.close()