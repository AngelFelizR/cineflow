# controllers/boleto_controller.py
from database import db
from models import Funcion, Sala, Asiento, Boleto, BoletoCancelado, TipoBoleto
from sqlalchemy.orm import joinedload


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