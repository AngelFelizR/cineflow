# controllers/funcion_controller.py
from database import db
from models import Funcion, Sala, Pelicula, Boleto, BoletoCancelado
from sqlalchemy.orm import joinedload
from datetime import datetime, date
from typing import List, Dict, Any, Optional


class FuncionController:
    
    @staticmethod
    def obtener_funciones_por_pelicula(pelicula_id: int, desde_fecha: date = None) -> Dict[str, Any]:
        """
        Obtiene todas las funciones futuras de una película, organizadas por cine y fecha
        
        Args:
            pelicula_id: ID de la película
            desde_fecha: Fecha desde la cual buscar funciones (por defecto hoy)
        
        Returns:
            Dict con funciones organizadas y metadatos
        """
        session = db.get_session()
        try:
            # Si no se especifica fecha, usar hoy
            if desde_fecha is None:
                desde_fecha = date.today()
            
            # Convertir a datetime para la consulta
            desde_datetime = datetime.combine(desde_fecha, datetime.min.time())
            
            # Obtener funciones futuras para esta película
            funciones = session.query(Funcion).\
                options(
                    joinedload(Funcion.sala).joinedload(Sala.cine),
                    joinedload(Funcion.sala).joinedload(Sala.tipo_sala),
                    joinedload(Funcion.pelicula).joinedload(Pelicula.idioma),
                    joinedload(Funcion.pelicula).joinedload(Pelicula.clasificacion)
                ).\
                filter(Funcion.IdPelicula == pelicula_id).\
                filter(Funcion.FechaHora >= desde_datetime).\
                filter(Funcion.Activo == True).\
                order_by(Funcion.FechaHora).\
                all()
            
            if not funciones:
                return {
                    'organizadas': {},
                    'cines': [],
                    'fechas': [],
                    'total_funciones': 0
                }
            
            # Organizar funciones por fecha y cine
            funciones_organizadas = {}
            cines_unicos = set()
            fechas_unicas = set()
            
            for funcion in funciones:
                # Extraer fecha (sin hora)
                fecha_str = funcion.FechaHora.date().isoformat()
                fecha_display = funcion.FechaHora.strftime('%d/%m/%Y')
                
                # Obtener datos del cine
                cine = funcion.sala.cine
                cine_id = cine.Id
                
                # Formatear hora
                hora_str = funcion.FechaHora.strftime('%H:%M')
                
                # Crear estructura de función
                funcion_data = {
                    'id': funcion.Id,
                    'hora': hora_str,
                    'fecha_completa': funcion.FechaHora,
                    'sala_numero': funcion.sala.NumeroDeSala,
                    'tipo_sala': funcion.sala.tipo_sala.Tipo,
                    'tipo_sala_id': funcion.sala.tipo_sala.Id,
                    'precio_adulto': float(funcion.sala.tipo_sala.PrecioAdulto),
                    'precio_nino': float(funcion.sala.tipo_sala.PrecioNino),
                    'funcion_obj': funcion  # Referencia al objeto original
                }
                
                # Inicializar estructura si no existe
                if fecha_str not in funciones_organizadas:
                    funciones_organizadas[fecha_str] = {
                        'fecha_display': fecha_display,
                        'cines': {}
                    }
                
                if cine_id not in funciones_organizadas[fecha_str]['cines']:
                    funciones_organizadas[fecha_str]['cines'][cine_id] = {
                        'cine_id': cine_id,
                        'cine_nombre': cine.Cine,
                        'cine_direccion': cine.Direccion,
                        'funciones': []
                    }
                
                # Agregar función
                funciones_organizadas[fecha_str]['cines'][cine_id]['funciones'].append(funcion_data)
                
                # Agregar a conjuntos únicos
                cines_unicos.add((cine_id, cine.Cine, cine.Direccion))
                fechas_unicas.add((fecha_str, fecha_display))
            
            # Convertir sets a listas ordenadas
            cines_lista = sorted([{
                'id': c[0],
                'nombre': c[1],
                'direccion': c[2]
            } for c in cines_unicos], key=lambda x: x['nombre'])
            
            fechas_lista = sorted([{
                'fecha_str': f[0],
                'fecha_display': f[1]
            } for f in fechas_unicas], key=lambda x: x['fecha_str'])
            
            # Ordenar funciones dentro de cada cine por hora
            for fecha_str in funciones_organizadas:
                for cine_id in funciones_organizadas[fecha_str]['cines']:
                    funciones_organizadas[fecha_str]['cines'][cine_id]['funciones'].sort(
                        key=lambda x: x['fecha_completa']
                    )
            
            return {
                'organizadas': funciones_organizadas,
                'cines': cines_lista,
                'fechas': fechas_lista,
                'total_funciones': len(funciones)
            }
            
        except Exception as e:
            print(f"Error en obtener_funciones_por_pelicula: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def pelicula_tiene_funciones(pelicula_id: int) -> bool:
        """
        Verifica si una película tiene funciones futuras activas
        
        Args:
            pelicula_id: ID de la película
            
        Returns:
            True si tiene funciones futuras, False en caso contrario
        """
        session = db.get_session()
        try:
            count = session.query(Funcion).\
                filter(Funcion.IdPelicula == pelicula_id).\
                filter(Funcion.FechaHora >= datetime.now()).\
                filter(Funcion.Activo == True).\
                count()
            
            return count > 0
            
        except Exception as e:
            print(f"Error en pelicula_tiene_funciones: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def obtener_funcion_por_id(funcion_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de una función específica
        
        Args:
            funcion_id: ID de la función
            
        Returns:
            Dict con detalles de la función o None si no existe
        """
        session = db.get_session()
        try:
            funcion = session.query(Funcion).\
                options(
                    joinedload(Funcion.sala).joinedload(Sala.cine),
                    joinedload(Funcion.sala).joinedload(Sala.tipo_sala),
                    joinedload(Funcion.pelicula).joinedload(Pelicula.idioma),
                    joinedload(Funcion.pelicula).joinedload(Pelicula.clasificacion)
                ).\
                filter(Funcion.Id == funcion_id).\
                filter(Funcion.Activo == True).\
                first()
            
            if not funcion:
                return None
            
            return {
                'id': funcion.Id,
                'fecha_hora': funcion.FechaHora,
                'fecha_display': funcion.FechaHora.strftime('%d/%m/%Y'),
                'hora_display': funcion.FechaHora.strftime('%H:%M'),
                'pelicula': {
                    'id': funcion.pelicula.Id,
                    'titulo': funcion.pelicula.Titulo,
                    'duracion': funcion.pelicula.DuracionMinutos,
                    'idioma': funcion.pelicula.idioma.Idioma,
                    'clasificacion': funcion.pelicula.clasificacion.Clasificacion,
                    'link_to_banner': funcion.pelicula.LinkToBanner
                },
                'sala': {
                    'id': funcion.sala.Id,
                    'numero': funcion.sala.NumeroDeSala,
                    'tipo_sala': funcion.sala.tipo_sala.Tipo,
                    'precio_adulto': float(funcion.sala.tipo_sala.PrecioAdulto),
                    'precio_nino': float(funcion.sala.tipo_sala.PrecioNino)
                },
                'cine': {
                    'id': funcion.sala.cine.Id,
                    'nombre': funcion.sala.cine.Cine,
                    'direccion': funcion.sala.cine.Direccion,
                    'telefono': funcion.sala.cine.Telefono
                },
                'asientos_disponibles': FuncionController.contar_asientos_disponibles(funcion_id)
            }
            
        except Exception as e:
            print(f"Error en obtener_funcion_por_id: {e}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def contar_asientos_disponibles(funcion_id: int) -> int:
        """
        Cuenta los asientos disponibles para una función
        
        Args:
            funcion_id: ID de la función
            
        Returns:
            Número de asientos disponibles
        """
        session = db.get_session()
        try:
            # Obtener la función y la sala
            funcion = session.query(Funcion).\
                options(joinedload(Funcion.sala).joinedload(Sala.asientos)).\
                filter(Funcion.Id == funcion_id).\
                first()
            
            if not funcion:
                return 0
            
            # Contar asientos totales en la sala
            asientos_totales = len(funcion.sala.asientos)
            
            # Contar boletos vendidos para esta función
            from models import Boleto
            boletos_vendidos = session.query(Boleto).\
                filter(Boleto.IdFuncion == funcion_id).\
                count()
            
            return max(0, asientos_totales - boletos_vendidos)
            
        except Exception as e:
            print(f"Error en contar_asientos_disponibles: {e}")
            return 0
        finally:
            session.close()


# Agregar al archivo funcion_controller.py (en la clase FuncionController)

    @staticmethod
    def obtener_asientos_con_disponibilidad(funcion_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los asientos de la sala de una función, con indicador de disponibilidad.
        Un asiento está disponible si está activo y no tiene un boleto vendido (no cancelado).
        
        Args:
            funcion_id: ID de la función
            
        Returns:
            Lista de diccionarios con información de cada asiento
        """
        session = db.get_session()
        try:
            # Obtener la función con la sala
            funcion = session.query(Funcion).options(
                joinedload(Funcion.sala).joinedload(Sala.asientos)
            ).filter(Funcion.Id == funcion_id).first()
            
            if not funcion:
                return []
            
            subquery = session.query(BoletoCancelado.IdBoleto).subquery()
            asientos_vendidos = session.query(Boleto.IdAsiento).filter(
                Boleto.IdFuncion == funcion_id
            ).filter(
                ~Boleto.Id.in_(subquery)
            ).all()
            asientos_vendidos_ids = {av[0] for av in asientos_vendidos}
            
            # Construir la lista de asientos con su estado
            asientos_info = []
            for asiento in funcion.sala.asientos:
                # El asiento está disponible si está activo y no ha sido vendido
                disponible = (asiento.Activo and asiento.Id not in asientos_vendidos_ids)
                asientos_info.append({
                    'id': asiento.Id,
                    'codigo_asiento': asiento.CodigoAsiento,
                    'disponible': disponible
                })
            
            return asientos_info
            
        except Exception as e:
            print(f"Error al obtener asientos con disponibilidad: {e}")
            return []
        finally:
            session.close()
