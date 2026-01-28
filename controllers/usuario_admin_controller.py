# controllers/usuario_admin_controller.py
from database import db
from models import Usuario, RolUsuario
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from flask import flash
from datetime import datetime
import re

class UsuarioAdminController:
    """Controlador para operaciones CRUD de Usuarios (Administrador)"""

    @staticmethod
    def obtener_todos_paginados(pagina=1, por_pagina=25, filtros=None):
        """Obtiene usuarios con paginación"""
        session = db.get_session()
        try:
            query = session.query(Usuario).\
                options(joinedload(Usuario.rol))
            
            # Aplicar filtros si existen
            if filtros:
                if filtros.get('nombre'):
                    query = query.filter(Usuario.Nombre.ilike(f'%{filtros["nombre"]}%'))
                if filtros.get('apellidos'):
                    query = query.filter(Usuario.Apellidos.ilike(f'%{filtros["apellidos"]}%'))
                if filtros.get('correo'):
                    query = query.filter(Usuario.CorreoElectronico.ilike(f'%{filtros["correo"]}%'))
                if filtros.get('rol_id'):
                    query = query.filter(Usuario.IdRol == filtros['rol_id'])
            
            # Ordenar por nombre
            query = query.order_by(Usuario.Nombre, Usuario.Apellidos)
            
            # Paginación
            usuarios = query.offset((pagina - 1) * por_pagina).limit(por_pagina).all()
            total = query.count()
            
            return {
                'usuarios': usuarios,
                'total': total,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'paginas': (total + por_pagina - 1) // por_pagina
            }
        except Exception as e:
            flash(f'Error al obtener usuarios: {str(e)}', 'danger')
            return {'usuarios': [], 'total': 0, 'pagina': 1, 'por_pagina': por_pagina, 'paginas': 0}
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_id(id):
        """Obtiene un usuario por su ID"""
        session = db.get_session()
        try:
            usuario = session.query(Usuario).\
                options(joinedload(Usuario.rol)).\
                filter(Usuario.Id == id).first()
            
            return usuario
        except Exception as e:
            flash(f'Error al obtener usuario: {str(e)}', 'danger')
            return None
        finally:
            session.close()
    
    @staticmethod
    def crear(data):
        """Crea un nuevo usuario (administrativo)"""
        session = db.get_session()
        try:
            # Validaciones
            if not data.get('Nombre') or len(data['Nombre'].strip()) < 2:
                return False, 'El nombre debe tener al menos 2 caracteres', None
            if not data.get('Apellidos') or len(data['Apellidos'].strip()) < 2:
                return False, 'Los apellidos deben tener al menos 2 caracteres', None
            if not data.get('CorreoElectronico'):
                return False, 'El correo electrónico es requerido', None
            
            # Validar formato de correo
            if not UsuarioAdminController._validar_correo(data['CorreoElectronico']):
                return False, 'El correo electrónico no tiene un formato válido', None
            
            if not data.get('IdRol'):
                return False, 'Debe seleccionar un rol', None
            
            # Validar fecha de nacimiento si se proporciona
            fecha_nacimiento = None
            if data.get('FechaNacimiento'):
                try:
                    fecha_nacimiento = datetime.strptime(data['FechaNacimiento'], '%Y-%m-%d').date()
                    hoy = datetime.now().date()
                    edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
                    
                    if edad < 13:
                        return False, 'El usuario debe tener al menos 13 años', None
                    if edad > 120:
                        return False, 'Fecha de nacimiento no válida', None
                except ValueError:
                    return False, 'Formato de fecha de nacimiento no válido. Use YYYY-MM-DD', None
            
            # Verificar que el rol exista y esté activo
            rol = session.query(RolUsuario).filter(
                RolUsuario.Id == int(data['IdRol']), 
                RolUsuario.Activo == True
            ).first()
            if not rol:
                return False, 'El rol seleccionado no existe o no está activo', None
            
            # Verificar si ya existe un usuario con ese correo
            existente = session.query(Usuario).\
                filter(Usuario.CorreoElectronico.ilike(data['CorreoElectronico'].strip())).first()
            
            if existente:
                return False, 'Ya existe un usuario con ese correo electrónico', None
            
            # Crear nuevo
            nuevo_usuario = Usuario(
                Nombre=data['Nombre'].strip(),
                Apellidos=data['Apellidos'].strip(),
                CorreoElectronico=data['CorreoElectronico'].strip().lower(),
                IdRol=int(data['IdRol']),
                Telefono=data.get('Telefono', '').strip() if data.get('Telefono') else None,
                FechaNacimiento=fecha_nacimiento
            )
            
            # Si se proporciona contraseña, encriptarla
            if data.get('Contrasena'):
                contrasena_valida, mensaje_contrasena = UsuarioAdminController._validar_contrasena(data['Contrasena'])
                if not contrasena_valida:
                    return False, mensaje_contrasena, None
                nuevo_usuario.guardar_contrasena(data['Contrasena'])
            else:
                # Contraseña por defecto (debe ser cambiada en primer login)
                nuevo_usuario.guardar_contrasena('Temp1234!')
            
            session.add(nuevo_usuario)
            session.commit()
            return True, 'Usuario creado exitosamente', nuevo_usuario
            
        except IntegrityError:
            session.rollback()
            return False, 'Ya existe un usuario con ese correo electrónico', None
        except Exception as e:
            session.rollback()
            return False, f'Error al crear usuario: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def actualizar(id, data):
        """Actualiza un usuario existente"""
        session = db.get_session()
        try:
            usuario = session.query(Usuario).\
                filter(Usuario.Id == id).first()
            
            if not usuario:
                return False, 'Usuario no encontrado', None
            
            # Validaciones
            if not data.get('Nombre') or len(data['Nombre'].strip()) < 2:
                return False, 'El nombre debe tener al menos 2 caracteres', None
            if not data.get('Apellidos') or len(data['Apellidos'].strip()) < 2:
                return False, 'Los apellidos deben tener al menos 2 caracteres', None
            if not data.get('IdRol'):
                return False, 'Debe seleccionar un rol', None
            
            # Validar fecha de nacimiento si se proporciona
            fecha_nacimiento = None
            if data.get('FechaNacimiento'):
                try:
                    fecha_nacimiento = datetime.strptime(data['FechaNacimiento'], '%Y-%m-%d').date()
                    hoy = datetime.now().date()
                    edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
                    
                    if edad < 13:
                        return False, 'El usuario debe tener al menos 13 años', None
                    if edad > 120:
                        return False, 'Fecha de nacimiento no válida', None
                except ValueError:
                    return False, 'Formato de fecha de nacimiento no válido. Use YYYY-MM-DD', None
            
            # Verificar que el rol exista y esté activo
            rol = session.query(RolUsuario).filter(
                RolUsuario.Id == int(data['IdRol']), 
                RolUsuario.Activo == True
            ).first()
            if not rol:
                return False, 'El rol seleccionado no existe o no está activo', None
            
            # Verificar si ya existe otro usuario con el mismo correo
            if data.get('CorreoElectronico'):
                # Validar formato de correo
                if not UsuarioAdminController._validar_correo(data['CorreoElectronico']):
                    return False, 'El correo electrónico no tiene un formato válido', None
                
                existente = session.query(Usuario).\
                    filter(
                        Usuario.CorreoElectronico.ilike(data['CorreoElectronico'].strip()),
                        Usuario.Id != id
                    ).first()
                
                if existente:
                    return False, 'Ya existe otro usuario con ese correo electrónico', None
                
                usuario.CorreoElectronico = data['CorreoElectronico'].strip().lower()
            
            # Actualizar
            usuario.Nombre = data['Nombre'].strip()
            usuario.Apellidos = data['Apellidos'].strip()
            usuario.IdRol = int(data['IdRol'])
            usuario.Telefono = data.get('Telefono', '').strip() if data.get('Telefono') else None
            
            if fecha_nacimiento:
                usuario.FechaNacimiento = fecha_nacimiento
            
            # Actualizar contraseña si se proporciona
            if data.get('Contrasena') and data['Contrasena'].strip():
                contrasena_valida, mensaje_contrasena = UsuarioAdminController._validar_contrasena(data['Contrasena'])
                if not contrasena_valida:
                    return False, mensaje_contrasena, None
                usuario.guardar_contrasena(data['Contrasena'])
            
            session.commit()
            return True, 'Usuario actualizado exitosamente', usuario
            
        except Exception as e:
            session.rollback()
            return False, f'Error al actualizar usuario: {str(e)}', None
        finally:
            session.close()
    
    @staticmethod
    def eliminar(id):
        """Elimina (desactiva) un usuario"""
        session = db.get_session()
        try:
            usuario = session.query(Usuario).\
                filter(Usuario.Id == id).first()
            
            if not usuario:
                return False, 'Usuario no encontrado'
            
            # Verificar si el usuario tiene boletos
            from models import Boleto
            boletos = session.query(Boleto).\
                filter(Boleto.IdUsuario == id).count()
            
            if boletos > 0:
                return False, f'No se puede eliminar el usuario porque tiene {boletos} boleto(s) asociado(s)'
            
            # No podemos eliminar físicamente porque tiene contraseña, así que desactivamos
            # Marcamos como inactivo eliminando la contraseña (para que no pueda iniciar sesión)
            usuario.ContrasenaHash = ''
            session.commit()
            
            return True, 'Usuario desactivado exitosamente'
            
        except Exception as e:
            session.rollback()
            return False, f'Error al eliminar usuario: {str(e)}'
        finally:
            session.close()
    
    @staticmethod
    def _validar_contrasena(contrasena):
        """Valida que la contraseña cumpla con los requisitos de seguridad"""
        mensajes_error = []
        
        # Verificar longitud mínima
        if len(contrasena) < 10:
            mensajes_error.append("Mínimo 10 caracteres")
        
        # Verificar mayúscula
        if not re.search(r'[A-Z]', contrasena):
            mensajes_error.append("Al menos una mayúscula")
        
        # Verificar minúscula
        if not re.search(r'[a-z]', contrasena):
            mensajes_error.append("Al menos una minúscula")
        
        # Verificar número
        if not re.search(r'\d', contrasena):
            mensajes_error.append("Al menos un número")
        
        # Verificar carácter especial
        if not re.search(r'[!@#$%^&*()\-_=+{};:,<.>]', contrasena):
            mensajes_error.append("Al menos un carácter especial (!@#$%^&*()-_=+{};:,<.>)")
        
        if mensajes_error:
            mensaje = "La contraseña debe contener: " + ", ".join(mensajes_error)
            return False, mensaje
        
        return True, "Contraseña válida"
    
    @staticmethod
    def _validar_correo(correo):
        """Valida el formato de un correo electrónico"""
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, correo) is not None