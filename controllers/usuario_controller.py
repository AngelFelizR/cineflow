# controllers/usuario_controller.py
# Controlador para operaciones de usuarios

import re
from datetime import datetime
from models import Usuario, RolUsuario, db
from sqlalchemy.exc import IntegrityError
from flask import flash

class UsuarioController:
    """Controlador para operaciones de usuarios"""

    @staticmethod
    def crear_usuario(data):
        """
        Crea un nuevo usuario en el sistema
        
        Args:
            data (dict): Diccionario con los datos del usuario:
                - correo_electronico (str)
                - correo_confirmacion (str)
                - contrasena (str)
                - contrasena_confirmacion (str)
                - nombre (str)
                - apellidos (str)
                - fecha_nacimiento (str) en formato YYYY-MM-DD
                - telefono (str, opcional)
                
        Returns:
            tuple: (success: bool, message: str, usuario: Usuario or None)
        """
        # Validaciones básicas
        errores = []
        
        # 1. Validar que los correos coincidan
        if data['correo_electronico'] != data['correo_confirmacion']:
            errores.append("Los correos electrónicos no coinciden.")
        
        # 2. Validar que las contraseñas coincidan
        if data['contrasena'] != data['contrasena_confirmacion']:
            errores.append("Las contraseñas no coinciden.")
        
        # 3. Validar fortaleza de la contraseña
        contrasena_valida, mensaje_contrasena = UsuarioController._validar_contrasena(data['contrasena'])
        if not contrasena_valida:
            errores.append(mensaje_contrasena)
        
        # 4. Validar formato de correo principal
        if not UsuarioController._validar_correo(data['correo_electronico']):
            errores.append("El correo electrónico principal no tiene un formato válido.")
        
        # 5. Validar formato de correo de confirmación
        if not UsuarioController._validar_correo(data['correo_confirmacion']):
            errores.append("El correo de confirmación no tiene un formato válido.")
        
        # 6. Validar fecha de nacimiento (debe ser una fecha válida y el usuario debe tener al menos 13 años)
        try:
            fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
            hoy = datetime.now().date()
            edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            
            if edad < 13:
                errores.append("Debes tener al menos 13 años para registrarte.")
            if edad > 120:
                errores.append("Fecha de nacimiento no válida.")
        except ValueError:
            errores.append("Formato de fecha de nacimiento no válido. Use YYYY-MM-DD")
        
        # Si hay errores, retornar sin crear el usuario
        if errores:
            for error in errores:
                flash(error, 'danger')
            return False, "Error en los datos del formulario", None
        
        try:
            # Obtener sesión de base de datos
            session = db.get_session()
            
            # Obtener el rol de Cliente
            rol_cliente = session.query(RolUsuario).filter_by(Rol="Cliente").first()
            
            if not rol_cliente:
                flash("Error crítico: No se pudo encontrar ni crear el rol Cliente.", 'danger')
                session.close()
                return False, "Error en el sistema: Rol no disponible", None
            
            # Crear nuevo usuario
            nuevo_usuario = Usuario(
                IdRol=rol_cliente.Id,
                Nombre=data['nombre'].strip(),
                Apellidos=data['apellidos'].strip(),
                CorreoElectronico=data['correo_electronico'].strip().lower(),
                Telefono=data['telefono'].strip() if data['telefono'] else None,
                FechaNacimiento=fecha_nacimiento
            )
            
            # Encriptar y guardar contraseña
            nuevo_usuario.guardar_contrasena(data['contrasena'])
            
            # Guardar en la base de datos
            session.add(nuevo_usuario)
            session.commit()
            
            # Expungir el objeto de la sesión para evitar problemas
            session.expunge(nuevo_usuario)
            
            flash(f"¡Usuario {data['nombre']} registrado exitosamente! Ahora puedes iniciar sesión.", 'success')
            return True, "Usuario creado exitosamente", nuevo_usuario
            
        except IntegrityError as e:
            session.rollback()
            if "UNIQUE" in str(e).upper() and "CORREOELECTRÓNICO" in str(e).upper():
                flash("El correo electrónico ya está registrado.", 'danger')
            else:
                flash(f"Error al crear el usuario: {str(e)}", 'danger')
            return False, "Error de integridad en la base de datos", None
            
        except Exception as e:
            session.rollback() if 'session' in locals() else None
            flash(f"Error inesperado: {str(e)}", 'danger')
            return False, f"Error inesperado: {str(e)}", None
            
        finally:
            if 'session' in locals():
                session.close()
    
    @staticmethod
    def _validar_contrasena(contrasena):
        """
        Valida que la contraseña cumpla con los requisitos de seguridad
        
        Args:
            contrasena (str): Contraseña a validar
            
        Returns:
            tuple: (valida: bool, mensaje: str)
        """
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
        """
        Valida el formato de un correo electrónico
        
        Args:
            correo (str): Correo a validar
            
        Returns:
            bool: True si el formato es válido
        """
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, correo) is not None
    
    @staticmethod
    def obtener_por_correo(correo):
        """
        Obtiene un usuario por su correo electrónico
        
        Args:
            correo (str): Correo electrónico del usuario
            
        Returns:
            Usuario: Objeto Usuario o None
        """
        session = db.get_session()
        try:
            usuario = session.query(Usuario).filter_by(CorreoElectronico=correo.lower()).first()
            return usuario
        except Exception as e:
            print(f"Error al obtener usuario por correo: {e}")
            return None
        finally:
            session.close()