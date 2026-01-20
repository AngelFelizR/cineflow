# app.py
# Aplicación web Flask para el Sistema de Biblioteca

from controllers.pelicula_controller import PeliculaController
from controllers.usuario_controller import UsuarioController
from models import login_manager, bcrypt, Usuario
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
from flask_login import login_user, logout_user, current_user, login_required
import random

app = Flask(__name__)
app.secret_key = 'cineflow_secret_key_change_in_production_2025'

login_manager.init_app(app)
login_manager.login_view = 'inicio_sesion'
bcrypt.init_app(app)

# Fechas futuras para las próximas funciones
ahora = datetime.now()

# ==================== RUTAS PRINCIPALES ====================

@app.route('/')
@app.route('/index')
def index():
    
    # Obtener datos para la página de inicio
    peliculas_populares = PeliculaController.top_3_pelis()
    ultimas_peliculas = PeliculaController.ultimas_3_pelis()
    
    # Verificar si hay datos disponibles
    if not peliculas_populares and not ultimas_peliculas:
        flash('No hay películas disponibles en este momento', 'warning')
    
    return render_template('index.html',
                           peliculas_populares=peliculas_populares,
                           ultimas_peliculas=ultimas_peliculas)

@app.route('/cartelera')
def lista_cartelera():
    # Esta es la ruta que causaba el error BuildError
    return render_template('funciones/lista_cartelera.html')

@app.route('/proximamente')
def lista_proximamente():
    return render_template('funciones/lista_proximamente.html')

# =========================
# Rutas de Autenticación
# =========================

@app.route('/logout')
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('index'))

# =========================
# Rutas de Usuario
# =========================

@app.route('/crear_usuario', methods=['GET', 'POST'])
def crear_usuario():
    """Ruta para crear un nuevo usuario"""

    # Si el usuario ya está autenticado, redirigir al inicio
    if current_user.is_authenticated:
        flash('Para registrar un nuevo usuario debes cerrar sesion del usuario actual.', 'info')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Obtener datos del formulario
        data = {
            'correo_electronico': request.form.get('correo_electronico'),
            'correo_confirmacion': request.form.get('correo_confirmacion'),
            'contrasena': request.form.get('contrasena'),
            'contrasena_confirmacion': request.form.get('contrasena_confirmacion'),
            'nombre': request.form.get('nombre'),
            'apellidos': request.form.get('apellidos'),
            'fecha_nacimiento': request.form.get('fecha_nacimiento'),
            'telefono': request.form.get('telefono')
        }
        
        # Crear usuario usando el controlador
        success, message, usuario = UsuarioController.crear_usuario(data)
        
        if success:
            # Redirigir a login después de registro exitoso
            return redirect(url_for('inicio_sesion'))
    
    # Si es GET o si hubo error en POST, mostrar el formulario
    return render_template('usuario/crear_usuario.html')

@app.route('/inicio_sesion', methods=['GET', 'POST'])
def inicio_sesion():
    """Ruta para iniciar sesión"""
    
    # Si el usuario ya está autenticado, redirigir al inicio
    if current_user.is_authenticated:
        flash('Ya has iniciado sesion, retornando a la pagina de inicio.', 'info')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Obtener datos del formulario
        correo = request.form.get('correo')
        contrasena = request.form.get('contrasena')
        
        # Intentar iniciar sesión usando el controlador
        success, message, usuario = UsuarioController.iniciar_sesion(correo, contrasena)
        
        if success:
            # Iniciar sesión con Flask-Login
            login_user(usuario, remember=False)
            flash(message, 'success')
            return redirect(url_for('index'))
        else:
            flash(message, 'danger')
    
    # Si es GET o si hubo error en POST, mostrar el formulario
    return render_template('usuario/inicio_sesion.html')

@app.route('/perfil/actualizar_datos', methods=['GET', 'POST'])
@login_required
def usuario_actualizar_datos():
    """Ruta para actualizar los datos del usuario"""
    
    if request.method == 'POST':
        # Obtener datos del formulario
        data = {
            'nombre': request.form.get('nombre', '').strip(),
            'apellidos': request.form.get('apellidos', '').strip(),
            'fecha_nacimiento': request.form.get('fecha_nacimiento', '').strip(),
            'telefono': request.form.get('telefono', '').strip()
        }
        
        # Actualizar usuario usando el controlador
        success, message, usuario_dict = UsuarioController.actualizar_usuario(current_user.Id, data)
        
        if success:
            # Actualizar el objeto current_user con los nuevos datos
            # Necesitamos recargar el usuario desde la base de datos para actualizar la sesión
            from database import db
            session = db.get_session()
            try:
                usuario_actualizado = session.query(Usuario).filter_by(Id=current_user.Id).first()
                if usuario_actualizado:
                    # Actualizar current_user
                    current_user.Nombre = usuario_actualizado.Nombre
                    current_user.Apellidos = usuario_actualizado.Apellidos
                    current_user.FechaNacimiento = usuario_actualizado.FechaNacimiento
                    current_user.Telefono = usuario_actualizado.Telefono
                    
                    # Recargar el usuario en la sesión de Flask-Login
                    from flask_login import logout_user, login_user
                    logout_user()
                    login_user(usuario_actualizado)
            finally:
                session.close()
            
            flash(message, 'success')
            return redirect(url_for('usuario_actualizar_datos'))
        else:
            flash(message, 'danger')
    
    # Si es GET, mostrar el formulario con los datos actuales
    return render_template('usuario/actualizar_datos.html')

@app.route('/perfil/actualizar_password', methods=['GET', 'POST'])
@login_required
def usuario_actualizar_password():
    """Ruta para actualizar la contraseña del usuario"""
    
    if request.method == 'POST':
        # Obtener datos del formulario
        contrasena_actual = request.form.get('contrasena_actual')
        nueva_contrasena = request.form.get('nueva_contrasena')
        confirmar_contrasena = request.form.get('confirmar_contrasena')
        
        # Actualizar contraseña usando el controlador
        success, message = UsuarioController.actualizar_contrasena(
            current_user.Id,
            contrasena_actual,
            nueva_contrasena,
            confirmar_contrasena
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('usuario_actualizar_password'))
        else:
            flash(message, 'danger')
    
    # Si es GET, mostrar el formulario
    return render_template('usuario/actualizar_contraseña.html')

# =========================
# Rutas de Boletos
# =========================

@app.route('/mis-boletos')
@login_required
def boletos_lista():
    return render_template('boletos_lista.html')

@app.route('/boletos/devueltos')
@login_required
def boletos_devueltos():
    return render_template('boletos_devueltos.html')


# ==================== RUTAS DE PELÍCULAS ====================

@app.route('/pelicula/<int:pelicula_id>/funciones')
def funciones_pelicula(pelicula_id):
    # Aquí puedes agregar lógica para obtener funciones de la película
    return render_template('funciones_pelicula.html', pelicula_id=pelicula_id)

# ==================== RUTAS DE API PARA DESARROLLO ====================

@app.route('/api/sample-data')
def api_sample_data():
    """Endpoint para obtener datos de muestra durante desarrollo"""
    return jsonify({
        'peliculas_populares': peliculas_populares,  # Tus datos de muestra
        'ultimas_peliculas': ultimas_peliculas
    })


# ==================== EJECUCIÓN ====================

if __name__ == '__main__':
    print("=" * 80)
    print("CineFlow - APLICACIÓN WEB")
    print("=" * 80)
    print("\nIniciando servidor Flask...")
    print("Accede a la aplicación en: http://localhost:5000")
    print("\nPresiona Ctrl+C para detener el servidor")
    print("=" * 80)

    app.run(debug=True, host='0.0.0.0', port=5000)
