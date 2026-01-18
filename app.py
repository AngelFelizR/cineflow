# app.py
# Aplicación web Flask para el Sistema de Biblioteca

from controllers.pelicula_controller import PeliculaController
from controllers.usuario_controller import UsuarioController
from models import login_manager, bcrypt
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
    #controller = PeliculaController()
    
    # Obtener datos para la página de inicio
    # peliculas_populares = controller.top_3_pelis()
    # ultimas_peliculas = controller.ultimas_3_pelis()

        # Datos de ejemplo para desarrollo
    # Datos de ejemplo para desarrollo
    peliculas_populares = [
        {
            'id': 1,
            'titulo': 'Avatar: El Camino del Agua',
            'descripcion_corta': 'Jake Sully y Neytiri han formado una familia y hacen todo lo posible por permanecer juntos.',
            'descripcion_larga': 'Jake Sully y Neytiri han formado una familia y hacen todo lo posible por permanecer juntos. Sin embargo, deben abandonar su hogar y explorar las regiones de Pandora cuando una antigua amenaza reaparece.',
            'duracion_minutos': 192,
            'generos': ['Ciencia Ficción', 'Aventura', 'Acción'],
            'clasificacion': 'PG-13',
            'idioma': 'Español',
            'link_to_banner': 'https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fbigfanboy.com%2Fwp%2Fwp-content%2Fuploads%2F2012%2F06%2FAvatar-Banner.jpg&f=1&nofb=1&ipt=b1361d8a7f1cf48bd0e6bc9c102c9d3a18c53d938bebc38f40e4426d8c5a7f92',
            'link_to_bajante': 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fde.web.img3.acsta.net%2Fpictures%2F22%2F11%2F04%2F08%2F13%2F1380149.jpg&f=1&nofb=1&ipt=d92681862bf4a9c764c5f705030e0d254d400635eda8e60e75d11a49a394ebe2',
            'link_to_trailer': 'https://www.youtube.com/watch?v=d9MyW72ELq0',
            'total_boletos': random.randint(100, 200),
            'popularidad': 'Alta'
        },
        {
            'id': 2,
            'titulo': 'Agentes del Destino',
            'descripcion_corta': 'Un agente del FBI descubre una conspiración que amenaza con cambiar el curso de la historia.',
            'descripcion_larga': 'Un agente del FBI, después de descubrir una conspiración que amenaza con cambiar el curso de la historia, debe unirse a un misterioso grupo de viajeros en el tiempo para detenerla.',
            'duracion_minutos': 128,
            'generos': ['Acción', 'Ciencia Ficción', 'Thriller'],
            'clasificacion': 'PG-13',
            'idioma': 'Español',
            'link_to_banner': 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fis1-ssl.mzstatic.com%2Fimage%2Fthumb%2Fh2v9Hmk3UkkV8_ZKRT0TpA%2F1200x675.jpg&f=1&nofb=1&ipt=6524a91f8b1ef388814cac7566b3ed1c3864f1fb3466dd8b0becc8616d9eeb70',
            'link_to_bajante': 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fm.media-amazon.com%2Fimages%2FS%2Fpv-target-images%2Fa93e82dc61479d2ae92fdd049b2c7adc9abff3443384c483b72d9ece874a9378.jpg&f=1&nofb=1&ipt=d258152e71cc925a51f20aeb824bb1bdf4048b51b97030a2aeeda9ec12e9b66e',
            'link_to_trailer': 'https://www.youtube.com/watch?v=yad1dZNHBwY',
            'total_boletos': random.randint(50, 99),
            'popularidad': 'Media'
        },
        {
            'id': 3,
            'titulo': 'Guardianes de la Galaxia Vol. 3',
            'descripcion_corta': 'Los Guardianes deben proteger a uno de los suyos mientras se embarcan en una misión para defender el universo.',
            'descripcion_larga': 'Peter Quill, aún afectado por la pérdida de Gamora, debe reunir a su equipo para defender el universo y proteger a uno de los suyos. Una misión que, si no se completa con éxito, podría conducir al fin de los Guardianes tal como los conocemos.',
            'duracion_minutos': 150,
            'generos': ['Ciencia Ficción', 'Acción', 'Comedia'],
            'clasificacion': 'PG-13',
            'idioma': 'Inglés',
            'link_to_banner': 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.themoviedb.org%2Ft%2Fp%2Foriginal%2F5YZbUmjbMa3ClvSW1Wj3D6XGolb.jpg&f=1&nofb=1&ipt=8b5d5e6e6a0d7d0cc5b0f5a5c5e5c5a5e5c5a5e5c5a5e5c5a5e5c5a5e5c5a5e5c5a5',
            'link_to_bajante': 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimage.tmdb.org%2Ft%2Fp%2Foriginal%2F5YZbUmjbMa3ClvSW1Wj3D6XGolb.jpg&f=1&nofb=1&ipt=8b5d5e6e6a0d7d0cc5b0f5a5c5e5c5a5e5c5a5e5c5a5e5c5a5e5c5a5e5c5a5e5c5a5',
            'link_to_trailer': 'https://www.youtube.com/watch?v=u3V5KDHRQvk',
            'proxima_funcion': ahora + timedelta(days=2, hours=15, minutes=30)
        }
    ]


    
    ultimas_peliculas = peliculas_populares.copy()
    ultimas_peliculas.reverse()
    
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

@app.route('/perfil/actualizar')
@login_required
def usuario_actualizar_datos():
    return render_template('usuario/actualizar_datos.html')

@app.route('/perfil/password')
@login_required
def usuario_cambiar_password():
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
