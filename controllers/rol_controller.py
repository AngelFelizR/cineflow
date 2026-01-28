# controllers/rol_controller.py
from database import db
from models import RolUsuario, Usuario
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash

class RolController:
    """Controlador para operaciones CRUD de Roles de Usuario"""

    @staticmethod
    def obtener_todos():
        """Obtiene todos los roles activos"""
        session = db.get_session()
        try:
            roles = session.query(RolUsuario).\
                filter(RolUsuario.Activo == True).\
                order_by(RolUsuario.Rol).all()
            return roles
        except Exception as e:
            flash(f'Error al obtener roles: {str(e)}', 'danger')
            return []
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene un rol por su ID con sus usuarios"""
        session = db.get_session()
        try:
            rol = session.query(RolUsuario).\
                options(joinedload(RolUsuario.usuarios)).\
                filter(RolUsuario.Id == id).first()
            
            if rol and hasattr(rol, 'usuarios'):
                _ = list(rol.usuarios)
            
            return rol
        except Exception as e:
            flash(f'Error al obtener rol: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """Crea un nuevo rol"""
        session = db.get_session()
        try:
            if not data.get('Rol') or len(data['Rol'].strip()) < 2:
                return False, 'El rol debe tener al menos 2 caracteres', None
            
            existente = session.query(RolUsuario).\
                filter(RolUsuario.Rol.ilike(data['Rol'].strip())).first()
            
            if existente:
                if existente.Activo:
                    return False, 'Ya existe un rol con ese nombre', None
                else:
                    existente.Activo = True
                    session.commit()
                    return True, 'Rol reactivado exitosamente', existente
            
            nuevo_rol = RolUsuario(
                Rol=data['Rol'].strip(),
                Activo=True
            )
            
            session.add(nuevo_rol)
            session.commit()
            return True, 'Rol creado exitosamente', nuevo_rol
            
        except IntegrityError:
            session.rollback()
            return False, 'Ya existe un rol con ese nombre', None
        except Exception as e:
            session.rollback()
            return False, f'Error al crear rol: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza un rol existente"""
        session = db.get_session()
        try:
            rol = session.query(RolUsuario).\
                filter(RolUsuario.Id == id).first()
            
            if not rol:
                return False, 'Rol no encontrado', None
            
            if not data.get('Rol') or len(data['Rol'].strip()) < 2:
                return False, 'El rol debe tener al menos 2 caracteres', None
            
            existente = session.query(RolUsuario).\
                filter(
                    RolUsuario.Rol.ilike(data['Rol'].strip()),
                    RolUsuario.Id != id
                ).first()
            
            if existente:
                return False, 'Ya existe otro rol con ese nombre', None
            
            rol.Rol = data['Rol'].strip()
            
            if 'Activo' in data:
                rol.Activo = data['Activo'] == 'on' if isinstance(data['Activo'], str) else bool(data['Activo'])
            
            session.commit()
            return True, 'Rol actualizado exitosamente', rol
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar rol: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina (desactiva) un rol"""
        session = db.get_session()
        try:
            rol = session.query(RolUsuario).\
                filter(RolUsuario.Id == id).first()
            
            if not rol:
                return False, 'Rol no encontrado'
            
            usuarios = session.query(Usuario).\
                filter(Usuario.IdRol == id).count()
            
            if usuarios > 0:
                return False, f'No se puede eliminar el rol porque está siendo usado por {usuarios} usuario(s)'
            
            rol.Activo = False
            session.commit()
            
            return True, 'Rol eliminado exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar rol: {str(e)}'
        finally:
            session.close()
    
    @staticmethod
    def obtener_para_select():
        """Obtiene roles para usar en selects (comboboxes)"""
        session = db.get_session()
        try:
            roles = session.query(
                RolUsuario.Id,
                RolUsuario.Rol
            ).filter(
                RolUsuario.Activo == True
            ).order_by(
                RolUsuario.Rol
            ).all()
            
            return [(c.Id, c.Rol) for c in roles]
        except Exception as e:
            print(f"Error al obtener roles para select: {e}")
            return []
        finally:
            session.close()