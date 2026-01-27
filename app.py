# app.py
# Aplicación web Flask para el Sistema de Biblioteca

from controllers.pelicula_controller import PeliculaController
from controllers.usuario_controller import UsuarioController
from controllers.funcion_controller import FuncionController
from controllers.boleto_controller import BoletoController
from models import login_manager, bcrypt
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime, date
from flask_login import login_user, logout_user, current_user, login_required
import traceback

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
    """Ruta para mostrar la cartelera con filtros dinámicos"""
    
    # Obtener parámetros de filtro de la solicitud GET
    dia = request.args.get('dia')
    generos = request.args.getlist('genero')
    salas = request.args.getlist('sala')
    idiomas = request.args.getlist('idioma')
    clasificaciones = request.args.getlist('clasificacion')
    
    # Convertir listas de strings a enteros usando el controlador
    generos_ids = PeliculaController.convertir_parametros_filtro(generos)
    salas_ids = PeliculaController.convertir_parametros_filtro(salas)
    idiomas_ids = PeliculaController.convertir_parametros_filtro(idiomas)
    clasificaciones_ids = PeliculaController.convertir_parametros_filtro(clasificaciones)
    
    # 1. Obtener películas filtradas usando el controlador
    resultado_cartelera = PeliculaController.filtrar_pelis_cartelera(
        dia=dia,
        genero_list=generos_ids if generos_ids else None,
        sala_tipo_list=salas_ids if salas_ids else None,
        idioma_list=idiomas_ids if idiomas_ids else None,
        clasificacion_list=clasificaciones_ids if clasificaciones_ids else None
    )
    
    # 2. Obtener opciones de filtro dinámicas basadas en las películas ya obtenidas
    opciones_filtros = PeliculaController.obtener_opciones_filtros_por_fecha(
        resultado_cartelera=resultado_cartelera
    )
    
    # 3. Verificar si hay filtros seleccionados que ya no están disponibles
    # y filtrar solo los que están disponibles
    generos_seleccionados_filtrados = []
    if generos_ids:
        generos_disponibles_ids = [g.Id for g in opciones_filtros['generos']]
        generos_seleccionados_filtrados = [g for g in generos_ids if g in generos_disponibles_ids]
    
    salas_seleccionadas_filtradas = []
    if salas_ids:
        salas_disponibles_ids = [s.Id for s in opciones_filtros['salas']]
        salas_seleccionadas_filtradas = [s for s in salas_ids if s in salas_disponibles_ids]
    
    idiomas_seleccionados_filtrados = []
    if idiomas_ids:
        idiomas_disponibles_ids = [i.Id for i in opciones_filtros['idiomas']]
        idiomas_seleccionados_filtrados = [i for i in idiomas_ids if i in idiomas_disponibles_ids]
    
    clasificaciones_seleccionadas_filtradas = []
    if clasificaciones_ids:
        clasificaciones_disponibles_ids = [c.Id for c in opciones_filtros['clasificaciones']]
        clasificaciones_seleccionadas_filtradas = [c for c in clasificaciones_ids if c in clasificaciones_disponibles_ids]
    
    # 4. Combinar todos los datos para la template
    return render_template(
        'peliculas/lista_cartelera.html',
        peliculas=resultado_cartelera['peliculas'],
        fecha_seleccionada=resultado_cartelera['fecha_seleccionada'],
        fecha_minima=resultado_cartelera['fecha_minima'],
        fecha_maxima=resultado_cartelera['fecha_maxima'],
        fecha_mostrada=resultado_cartelera['fecha_mostrada'],
        generos_opciones=opciones_filtros['generos'],
        salas_opciones=opciones_filtros['salas'],
        idiomas_opciones=opciones_filtros['idiomas'],
        clasificaciones_opciones=opciones_filtros['clasificaciones'],
        generos_seleccionados=generos_seleccionados_filtrados,
        salas_seleccionados=salas_seleccionadas_filtradas,
        idiomas_seleccionados=idiomas_seleccionados_filtrados,
        clasificaciones_seleccionados=clasificaciones_seleccionadas_filtradas
    )

@app.route('/proximamente')
def lista_proximamente():
    """Ruta para mostrar la cartelera de próximos estrenos"""
    
    # Obtener parámetros de filtro de la solicitud GET
    generos = request.args.getlist('genero')
    idiomas = request.args.getlist('idioma')
    clasificaciones = request.args.getlist('clasificacion')
    
    # Convertir parámetros usando el método del controlador
    generos_ids = PeliculaController.convertir_parametros_filtro(generos)
    idiomas_ids = PeliculaController.convertir_parametros_filtro(idiomas)
    clasificaciones_ids = PeliculaController.convertir_parametros_filtro(clasificaciones)
    
    # 1. Obtener películas próximas usando el nuevo método del controlador
    peliculas_proximas = PeliculaController.filtrar_pelis_prox(
        genero_list=generos_ids if generos_ids else None,
        idioma_list=idiomas_ids if idiomas_ids else None,
        clasificacion_list=clasificaciones_ids if clasificaciones_ids else None
    )
    
    # 2. Obtener opciones de filtro dinámicas basadas en las películas ya obtenidas
    opciones_filtros = PeliculaController.obtener_opciones_filtros_proximamente(
        peliculas_filtradas=peliculas_proximas
    )
    
    # 3. Verificar si hay filtros seleccionados que ya no están disponibles
    # y filtrar solo los que están disponibles
    generos_seleccionados_filtrados = []
    if generos_ids:
        generos_disponibles_ids = [g.Id for g in opciones_filtros['generos']]
        generos_seleccionados_filtrados = [g for g in generos_ids if g in generos_disponibles_ids]
    
    idiomas_seleccionados_filtrados = []
    if idiomas_ids:
        idiomas_disponibles_ids = [i.Id for i in opciones_filtros['idiomas']]
        idiomas_seleccionados_filtrados = [i for i in idiomas_ids if i in idiomas_disponibles_ids]
    
    clasificaciones_seleccionadas_filtradas = []
    if clasificaciones_ids:
        clasificaciones_disponibles_ids = [c.Id for c in opciones_filtros['clasificaciones']]
        clasificaciones_seleccionadas_filtradas = [c for c in clasificaciones_ids if c in clasificaciones_disponibles_ids]
    
    # 4. Combinar todos los datos para la template
    return render_template(
        'peliculas/lista_proximamente.html',
        peliculas=peliculas_proximas,
        generos_opciones=opciones_filtros['generos'],
        idiomas_opciones=opciones_filtros['idiomas'],
        clasificaciones_opciones=opciones_filtros['clasificaciones'],
        generos_seleccionados=generos_seleccionados_filtrados,
        idiomas_seleccionados=idiomas_seleccionados_filtrados,
        clasificaciones_seleccionados=clasificaciones_seleccionadas_filtradas
    )

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
        data = {
            'nombre': request.form.get('nombre', '').strip(),
            'apellidos': request.form.get('apellidos', '').strip(),
            'fecha_nacimiento': request.form.get('fecha_nacimiento', '').strip(),
            'telefono': request.form.get('telefono', '').strip()
        }
        
        success, message, usuario_actualizado = UsuarioController.actualizar_usuario(
            current_user.Id, data
        )
        
        if success and usuario_actualizado:
            from flask_login import logout_user, login_user
            logout_user()
            login_user(usuario_actualizado)
            flash(message, 'success')
            return redirect(url_for('usuario_actualizar_datos'))
        else:
            flash(message, 'danger')
    
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
    """Ruta para mostrar los boletos del usuario"""
    if current_user.rol_nombre != "Cliente":
        flash('Esta sección es solo para clientes.', 'danger')
        return redirect(url_for('index'))
    
    # Obtener boletos organizados
    boletos_organizados = BoletoController.obtener_boletos_usuario(current_user.Id)
    
    # Obtener saldo disponible
    saldo_disponible = BoletoController.obtener_saldo_usuario(current_user.Id)
    
    return render_template(
        'boletos/boletos_lista.html',
        boletos_organizados=boletos_organizados,
        saldo_disponible=saldo_disponible,
        ahora=datetime.now() 
    )

@app.route('/cancelar-boletos', methods=['POST'])
@login_required
def cancelar_boletos():
    """Ruta para cancelar boletos seleccionados"""
    if current_user.rol_nombre != "Cliente":
        flash('Esta sección es solo para clientes.', 'danger')
        return redirect(url_for('index'))
    
    # Obtener boletos seleccionados del formulario
    boletos_seleccionados = request.form.getlist('boletos_seleccionados')
    
    if not boletos_seleccionados:
        flash('No se han seleccionado boletos para cancelar.', 'warning')
        return redirect(url_for('boletos_lista'))
    
    # Convertir a enteros
    boletos_ids = [int(boleto_id) for boleto_id in boletos_seleccionados if boleto_id.isdigit()]
    
    if not boletos_ids:
        flash('No se han seleccionado boletos válidos.', 'warning')
        return redirect(url_for('boletos_lista'))
    
    # Cancelar boletos
    saldo_disponible = BoletoController.obtener_saldo_usuario(current_user.Id)
    success, message, total_acreditado = BoletoController.cancelar_boletos(
        boletos_ids, current_user.Id
    )
    
    if success:
        total = saldo_disponible + total_acreditado
        flash(f'{message} Nuevo Saldo: ${saldo_disponible:.2f} + ${total_acreditado:.2f} = ${total:.2f}', 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('boletos_lista'))

@app.route('/boletos/devueltos')
@login_required
def boletos_devueltos():
    return render_template('boletos_devueltos.html')


# ==================== RUTAS DE PELÍCULAS ====================

@app.route('/pelicula/<int:pelicula_id>')
def detalle_pelicula(pelicula_id):
    """
    Ruta para mostrar el detalle de una película con sus funciones
    """
    # 1. Verificar si la película existe y está activa
    pelicula_detalle = PeliculaController.obtener_peli_detalle(pelicula_id)
    
    if not pelicula_detalle:
        flash('La película no existe o no está disponible.', 'danger')
        return redirect(url_for('lista_cartelera'))
    
    # 2. Verificar si la película está en cartelera (tiene funciones futuras)
    # Primero, verificar si tiene funciones futuras
    tiene_funciones = FuncionController.pelicula_tiene_funciones(pelicula_id)
    
    if not tiene_funciones:
        # Verificar si está en la cartelera filtrada
        resultado_cartelera = PeliculaController.filtrar_pelis_cartelera()
        peliculas_en_cartelera_ids = [p['Id'] for p in resultado_cartelera['peliculas']]
        
        if pelicula_id not in peliculas_en_cartelera_ids:
            flash('Esta película no está actualmente en cartelera.', 'warning')
            return redirect(url_for('lista_cartelera'))
    
    # 3. Obtener funciones organizadas por fecha y cine
    funciones_data = FuncionController.obtener_funciones_por_pelicula(pelicula_id)
    
    if funciones_data['total_funciones'] == 0:
        flash('No hay funciones disponibles para esta película en este momento.', 'warning')
        return redirect(url_for('lista_cartelera'))
    
    # 4. Renderizar template con todos los datos
    return render_template(
        'peliculas/detalle.html',
        pelicula=pelicula_detalle,
        funciones_data=funciones_data,
        hoy=date.today().isoformat()
    )

@app.route('/funcion/<int:funcion_id>/asientos')
@login_required
def seleccion_asientos(funcion_id):
    """
    Ruta para seleccionar asientos
    """
    # Verificar que el usuario sea cliente
    if current_user.rol_nombre != "Cliente":
        flash('Esta sección es solo para clientes.', 'danger')
        return redirect(url_for('index'))
    
    # Obtener detalles de la función
    funcion_detalle = FuncionController.obtener_funcion_por_id(funcion_id)
    
    if not funcion_detalle:
        flash('La función no existe o no está disponible.', 'danger')
        return redirect(url_for('lista_cartelera'))
    
    # Obtener asientos con disponibilidad
    asientos = FuncionController.obtener_asientos_con_disponibilidad(funcion_id)
    
    return render_template(
        'funciones/seleccion_asientos.html',
        funcion=funcion_detalle,
        asientos=asientos
    )

# ==================== CONFIRMACIÓN DEL PAGO ====================

@app.route('/funcion/<int:funcion_id>/confirmar-pago', methods=['GET', 'POST'])
@login_required
def confirmar_pago(funcion_id):
    """
    Ruta para confirmar y procesar el pago
    """
    if current_user.rol_nombre != "Cliente":
        flash('Esta sección es solo para clientes.', 'danger')
        return redirect(url_for('index'))
    
    # Obtener detalles de la función
    funcion_detalle = FuncionController.obtener_funcion_por_id(funcion_id)
    
    if not funcion_detalle:
        flash('La función no existe o no está disponible.', 'danger')
        return redirect(url_for('lista_cartelera'))
    
    if request.method == 'GET':
        # Obtener parámetros de la compra desde GET
        asientos_params = []
        tipos_asientos = {}
        
        for key, value in request.args.items():
            if key.startswith('asiento_'):
                codigo = key.replace('asiento_', '')
                tipo = value
                asientos_params.append((codigo, tipo))
                tipos_asientos[codigo] = tipo
        
        total = request.args.get('total', '0.00')
        adultos = request.args.get('adultos', '0')
        ninos = request.args.get('ninos', '0')
        
        # Validar que haya al menos un asiento
        if not asientos_params:
            flash('No se han seleccionado asientos.', 'danger')
            return redirect(url_for('seleccion_asientos', funcion_id=funcion_id))
        
        # Guardar temporalmente en sesión para procesar POST
        session['compra_temporal'] = {
            'asientos': asientos_params,
            'tipos': tipos_asientos,
            'total': total,
            'funcion_id': funcion_id
        }
        
        return render_template(
            'funciones/confirmar_pago.html',
            funcion=funcion_detalle,
            asientos=asientos_params,
            total=total,
            adultos=adultos,
            ninos=ninos
        )
    
    elif request.method == 'POST':
        # Procesar el pago
        compra_temporal = session.get('compra_temporal')
        
        if not compra_temporal or compra_temporal.get('funcion_id') != funcion_id:
            flash('Sesión de compra expirada o inválida.', 'danger')
            return redirect(url_for('seleccion_asientos', funcion_id=funcion_id))
        
        # Extraer datos
        asientos_params = compra_temporal['asientos']  # Lista de tuplas (código, tipo)
        tipos_asientos = compra_temporal['tipos']      # Dict código -> tipo
        
        # Extraer solo los códigos de asientos
        asientos_codigos = [codigo for codigo, _ in asientos_params]
        
        # Crear boletos en la base de datos
        success, message, boletos_ids = BoletoController.crear_boletos(
            funcion_id=funcion_id,
            usuario_id=current_user.Id,
            asientos_seleccionados=asientos_codigos,
            tipos_asientos=tipos_asientos
        )
        
        if success:
            # Limpiar sesión temporal
            session.pop('compra_temporal', None)
            
            flash(f'¡Pago confirmado! {message} Tu número de transacción: {", ".join(map(str, boletos_ids))}', 'success')
            return redirect(url_for('index'))
        else:
            flash(f'Error al procesar el pago: {message}', 'danger')
            return redirect(url_for('seleccion_asientos', funcion_id=funcion_id))


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
