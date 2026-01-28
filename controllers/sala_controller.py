# controllers/sala_controller.py
from database import db
from models import Sala, Cine, TipoSala, Asiento, Funcion
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash

class SalaController:
    """Controlador para operaciones CRUD de Salas"""

    @staticmethod
    def obtener_todas():
        """Obtiene todas las salas activas"""
        session = db.get_session()
        try:
            salas = session.query(Sala).\
                options(joinedload(Sala.cine), joinedload(Sala.tipo_sala)).\
                filter(Sala.Activo == True).\
                order_by(Sala.IdCine, Sala.NumeroDeSala).all()
            return salas
        except Exception as e:
            flash(f'Error al obtener salas: {str(e)}', 'danger')
            return []
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene una sala por su ID con sus relaciones"""
        session = db.get_session()
        try:
            sala = session.query(Sala).\
                options(joinedload(Sala.cine), joinedload(Sala.tipo_sala), joinedload(Sala.asientos)).\
                filter(Sala.Id == id).first()
            
            return sala
        except Exception as e:
            flash(f'Error al obtener sala: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """Crea una nueva sala"""
        session = db.get_session()
        try:
            # Validaciones
            if not data.get('IdCine'):
                return False, 'Debe seleccionar un cine', None
            if not data.get('IdTipo'):
                return False, 'Debe seleccionar un tipo de sala', None
            if not data.get('NumeroDeSala'):
                return False, 'El número de sala es requerido', None
            
            # Verificar que el cine exista y esté activo
            cine = session.query(Cine).filter(Cine.Id == int(data['IdCine']), Cine.Activo == True).first()
            if not cine:
                return False, 'El cine seleccionado no existe o no está activo', None
            
            # Verificar que el tipo de sala exista y esté activo
            tipo_sala = session.query(TipoSala).filter(TipoSala.Id == int(data['IdTipo']), TipoSala.Activo == True).first()
            if not tipo_sala:
                return False, 'El tipo de sala seleccionado no existe o no está activo', None
            
            # Verificar si ya existe una sala con ese número en el mismo cine
            existente = session.query(Sala).\
                filter(
                    Sala.IdCine == int(data['IdCine']),
                    Sala.NumeroDeSala == int(data['NumeroDeSala'])
                ).first()
            
            if existente:
                if existente.Activo:
                    return False, 'Ya existe una sala con ese número en este cine', None
                else:
                    # Reactivar la existente
                    existente.Activo = True
                    existente.IdTipo = int(data['IdTipo'])
                    session.commit()
                    return True, 'Sala reactivada exitosamente', existente
            
            # Crear nueva
            nueva_sala = Sala(
                IdCine=int(data['IdCine']),
                IdTipo=int(data['IdTipo']),
                NumeroDeSala=int(data['NumeroDeSala']),
                Activo=True
            )
            
            session.add(nueva_sala)
            session.commit()
            return True, 'Sala creada exitosamente', nueva_sala
            
        except IntegrityError:
            session.rollback()
            return False, 'Ya existe una sala con ese número en este cine', None
        except Exception as e:
            session.rollback()
            return False, f'Error al crear sala: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza una sala existente"""
        session = db.get_session()
        try:
            sala = session.query(Sala).\
                filter(Sala.Id == id).first()
            
            if not sala:
                return False, 'Sala no encontrada', None
            
            # Validaciones
            if not data.get('IdCine'):
                return False, 'Debe seleccionar un cine', None
            if not data.get('IdTipo'):
                return False, 'Debe seleccionar un tipo de sala', None
            if not data.get('NumeroDeSala'):
                return False, 'El número de sala es requerido', None
            
            # Verificar que el cine exista y esté activo
            cine = session.query(Cine).filter(Cine.Id == int(data['IdCine']), Cine.Activo == True).first()
            if not cine:
                return False, 'El cine seleccionado no existe o no está activo', None
            
            # Verificar que el tipo de sala exista y esté activo
            tipo_sala = session.query(TipoSala).filter(TipoSala.Id == int(data['IdTipo']), TipoSala.Activo == True).first()
            if not tipo_sala:
                return False, 'El tipo de sala seleccionado no existe o no está activo', None
            
            # Verificar si ya existe otra sala con ese número en el mismo cine
            existente = session.query(Sala).\
                filter(
                    Sala.IdCine == int(data['IdCine']),
                    Sala.NumeroDeSala == int(data['NumeroDeSala']),
                    Sala.Id != id
                ).first()
            
            if existente:
                return False, 'Ya existe otra sala con ese número en este cine', None
            
            # Actualizar
            sala.IdCine = int(data['IdCine'])
            sala.IdTipo = int(data['IdTipo'])
            sala.NumeroDeSala = int(data['NumeroDeSala'])
            
            if 'Activo' in data:
                sala.Activo = data['Activo'] == 'on' if isinstance(data['Activo'], str) else bool(data['Activo'])
            
            session.commit()
            return True, 'Sala actualizada exitosamente', sala
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar sala: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina (desactiva) una sala"""
        session = db.get_session()
        try:
            sala = session.query(Sala).\
                filter(Sala.Id == id).first()
            
            if not sala:
                return False, 'Sala no encontrada'
            
            # Verificar si hay funciones usando esta sala
            funciones = session.query(Funcion).\
                filter(Funcion.IdSala == id).\
                filter(Funcion.Activo == True).count()
            
            if funciones > 0:
                return False, f'No se puede eliminar la sala porque tiene {funciones} función(es) programada(s)'
            
            # Verificar si hay asientos en esta sala
            asientos = session.query(Asiento).\
                filter(Asiento.IdSala == id).\
                filter(Asiento.Activo == True).count()
            
            if asientos > 0:
                return False, f'No se puede eliminar la sala porque tiene {asientos} asiento(s)'
            
            # Desactivar (eliminación lógica)
            sala.Activo = False
            session.commit()
            
            return True, 'Sala eliminada exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar sala: {str(e)}'
        finally:
            session.close()

    @staticmethod
    def obtener_todas_con_capacidad():
        """Obtiene todas las salas activas con su capacidad calculada"""
        session = db.get_session()
        try:
            # Obtener salas con cine y tipo_sala cargados
            salas = session.query(Sala).\
                options(joinedload(Sala.cine), joinedload(Sala.tipo_sala)).\
                filter(Sala.Activo == True).\
                order_by(Sala.NumeroDeSala).all()
            
            # Obtener conteos de asientos por sala
            sala_ids = [sala.Id for sala in salas]
            capacidad_dict = {}
            
            if sala_ids:
                counts = session.query(
                    Asiento.IdSala,
                    func.count(Asiento.Id).label('cantidad')
                ).filter(
                    Asiento.IdSala.in_(sala_ids),
                    Asiento.Activo == True
                ).group_by(Asiento.IdSala).all()
                
                # Convertir a diccionario para búsqueda rápida
                capacidad_dict = {sala_id: cantidad for sala_id, cantidad in counts}
            
            # Asignar capacidad a cada sala
            for sala in salas:
                sala.capacidad = capacidad_dict.get(sala.Id, 0)
            
            return salas
        except Exception as e:
            print(f"Error al obtener salas con capacidad: {e}")
            # En caso de error, asignar capacidad 0
            for sala in salas:
                if hasattr(sala, 'capacidad'):
                    sala.capacidad = 0
            return salas
        finally:
            session.close()