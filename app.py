# app.py
# Aplicación web Flask para el Sistema de Biblioteca

from controllers.pelicula_controller import PeliculaController
from controllers.usuario_controller import UsuarioController
from controllers.funcion_controller import FuncionController
from controllers.boleto_controller import BoletoController
from controllers.dashboard_controller import DashboardController
from controllers.clasificacion_controller import ClasificacionController
from controllers.idioma_controller import IdiomaController
from controllers.pelicula_genero_controller import PeliculaGeneroController
from controllers.genero_controller import GeneroController
from controllers.pelicula_admin_controller import PeliculaAdminController
from models import login_manager, bcrypt
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from datetime import datetime, date, timedelta
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps
import traceback

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol_nombre != "Administrador":
            flash('Acceso restringido.', 'danger')
            return redirect(url_for('inicio_sesion'))
        return f(*args, **kwargs)
    return decorated_function
    

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
    
    # Obtener saldo disponible del usuario
    saldo_disponible = BoletoController.obtener_saldo_usuario(current_user.Id)
    
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
            ninos=ninos,
            saldo_disponible=saldo_disponible
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
        
        # Obtener si se desea usar saldo (el checkbox devuelve 'on' cuando está marcado)
        usar_saldo = request.form.get('usar_saldo') == 'on'
        
        # Obtener método de pago
        metodo_pago = request.form.get('metodo_pago', 'tarjeta')
        
        # Crear boletos en la base de datos (incluyendo lógica de saldo si se solicitó)
        success, message, boletos_ids, monto_saldo_usado = BoletoController.crear_boletos(
            funcion_id=funcion_id,
            usuario_id=current_user.Id,
            asientos_seleccionados=asientos_codigos,
            tipos_asientos=tipos_asientos,
            usar_saldo=usar_saldo
        )
        
        if success:
            # Limpiar sesión temporal
            session.pop('compra_temporal', None)
            
            # Preparar mensaje detallado
            total_float = float(compra_temporal['total'])
            
            if usar_saldo and monto_saldo_usado > 0:
                resto_pagado = total_float - monto_saldo_usado
                if resto_pagado > 0:
                    # Se usó saldo pero no cubrió todo
                    message = f'¡Pago confirmado! {message} Se usó ${monto_saldo_usado:.2f} de saldo y se pagó ${resto_pagado:.2f} con {metodo_pago}. Tu número de transacción: {", ".join(map(str, boletos_ids))}'
                else:
                    # El saldo cubrió todo
                    message = f'¡Pago confirmado! {message} Se usó ${monto_saldo_usado:.2f} de saldo. Tu número de transacción: {", ".join(map(str, boletos_ids))}'
            else:
                # No se usó saldo
                message = f'¡Pago confirmado! {message} Se pagó ${total_float:.2f} con {metodo_pago}. Tu número de transacción: {", ".join(map(str, boletos_ids))}'
            
            flash(message, 'success')
            return redirect(url_for('index'))
        else:
            flash(f'Error al procesar el pago: {message}', 'danger')
            return redirect(url_for('seleccion_asientos', funcion_id=funcion_id))


# ==================== RUTAS DEL DASHBOARD ADMINISTRATIVO ====================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Página principal del dashboard administrativo"""
    
    # Obtener opciones para los filtros
    opciones_filtros = DashboardController.obtener_opciones_filtros()
    
    # Establecer fechas por defecto (últimos 30 días)
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=30)
    
    return render_template('admin_dashboard.html',
                           opciones_filtros=opciones_filtros,
                           fecha_inicio_default=fecha_inicio.strftime('%Y-%m-%d'),
                           fecha_fin_default=fecha_fin.strftime('%Y-%m-%d'))

@app.route('/admin/dashboard/data', methods=['POST'])
@login_required
def dashboard_data():
    """Endpoint para obtener datos del dashboard (AJAX)"""
    if current_user.rol_nombre != "Administrador":
        return jsonify({'error': 'Acceso denegado'}), 403
    
    try:
        data = request.get_json()
        
        # Validar fechas
        if not data.get('fecha_inicio') or not data.get('fecha_fin'):
            return jsonify({'error': 'Fechas de inicio y fin son requeridas'}), 400
        
        # Convertir tipos de datos
        filtros = {
            'fecha_inicio': data.get('fecha_inicio'),
            'fecha_fin': data.get('fecha_fin'),
            'agrupacion': data.get('agrupacion', 'dia')
        }
        
        # Listas de IDs (si están presentes)
        if data.get('cine_ids'):
            filtros['cine_ids'] = [int(id) for id in data['cine_ids'] if str(id).isdigit()]
        
        if data.get('genero_ids'):
            filtros['genero_ids'] = [int(id) for id in data['genero_ids'] if str(id).isdigit()]
        
        if data.get('pelicula_ids'):
            filtros['pelicula_ids'] = [int(id) for id in data['pelicula_ids'] if str(id).isdigit()]
        
        if data.get('funcion_ids'):
            filtros['funcion_ids'] = [int(id) for id in data['funcion_ids'] if str(id).isdigit()]
        
        if data.get('dias_semana'):
            filtros['dias_semana'] = [int(dia) for dia in data['dias_semana'] if str(dia).isdigit()]
        
        datos = DashboardController.obtener_datos_completos(filtros)
        
        return jsonify(datos)
        
    except Exception as e:
        print(f"Error en dashboard_data: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/dashboard/export/excel')
@login_required
def dashboard_export_excel():
    """Exporta datos del dashboard a Excel"""
    if current_user.rol_nombre != "Administrador":
        return jsonify({'error': 'Acceso denegado'}), 403

    try:
        # Obtener parámetros de filtro
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        agrupacion = request.args.get('agrupacion', 'dia')
        
        # Listas de IDs
        cine_ids = request.args.getlist('cine_ids[]')
        genero_ids = request.args.getlist('genero_ids[]')
        pelicula_ids = request.args.getlist('pelicula_ids[]')
        funcion_ids = request.args.getlist('funcion_ids[]')
        dias_semana = request.args.getlist('dias_semana[]')
        
        # Construir diccionario de filtros
        filtros = {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'agrupacion': agrupacion,
            'cine_ids': [int(id) for id in cine_ids if id and str(id).isdigit()],
            'genero_ids': [int(id) for id in genero_ids if id and str(id).isdigit()],
            'pelicula_ids': [int(id) for id in pelicula_ids if id and str(id).isdigit()],
            'funcion_ids': [int(id) for id in funcion_ids if id and str(id).isdigit()],
            'dias_semana': [int(dia) for dia in dias_semana if dia and str(dia).isdigit()]
        }
        
        # Generar Excel
        excel_data = DashboardController.generar_excel(filtros)
        
        # Nombre del archivo
        filename = f"cineflow_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            excel_data,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error en exportación Excel: {e}")
        flash(f'Error al exportar Excel: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/dashboard/export/pdf')
@login_required
def dashboard_export_pdf():
    """Exporta dashboard completo a PDF"""
    if current_user.rol_nombre != "Administrador":
        return jsonify({'error': 'Acceso denegado'}), 403

    try:
        # Obtener parámetros de filtro
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        agrupacion = request.args.get('agrupacion', 'dia')
        
        # Listas de IDs
        cine_ids = request.args.getlist('cine_ids[]')
        genero_ids = request.args.getlist('genero_ids[]')
        pelicula_ids = request.args.getlist('pelicula_ids[]')
        funcion_ids = request.args.getlist('funcion_ids[]')
        dias_semana = request.args.getlist('dias_semana[]')
        
        # Construir diccionario de filtros
        filtros = {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'agrupacion': agrupacion,
            'cine_ids': [int(id) for id in cine_ids if id and str(id).isdigit()],
            'genero_ids': [int(id) for id in genero_ids if id and str(id).isdigit()],
            'pelicula_ids': [int(id) for id in pelicula_ids if id and str(id).isdigit()],
            'funcion_ids': [int(id) for id in funcion_ids if id and str(id).isdigit()],
            'dias_semana': [int(dia) for dia in dias_semana if dia and str(dia).isdigit()]
        }
        
        # Obtener datos del dashboard
        datos_dashboard = DashboardController.obtener_datos_completos(filtros)
        
        # Generar PDF
        pdf_data = DashboardController.generar_pdf(datos_dashboard, filtros)
        
        # Nombre del archivo
        filename = f"cineflow_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            pdf_data,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error en exportación PDF: {e}")
        flash(f'Error al exportar PDF: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))

# ==========================================
# RUTAS ADMINISTRATIVAS (CRUD LISTAS)
# ==========================================

# --- Rutas de Gestión (CRUD) ---
# Cada ruta renderiza el archivo 'lista.html' dentro de su subcarpeta correspondiente

# ==================== RUTAS CRUD PARA CLASIFICACIÓN ====================

@app.route('/admin/clasificaciones')
@admin_required
def clasificacion_lista():
    """Lista todas las clasificaciones"""
    clasificaciones = ClasificacionController.obtener_todas()
    return render_template('clasificacion/lista.html', clasificaciones=clasificaciones)

@app.route('/admin/clasificaciones/nuevo')
@admin_required
def clasificacion_nuevo():
    """Formulario para nueva clasificación"""
    return render_template('clasificacion/nuevo.html')

@app.route('/admin/clasificaciones/crear', methods=['POST'])
@admin_required
def clasificacion_crear():
    """Crea una nueva clasificación"""
    controller = ClasificacionController()
    success, message, clasificacion = controller.crear(request.form)
    
    if success:
        flash(message, 'success')
        return redirect(url_for('clasificacion_lista'))  # Redirige a la lista
    else:
        flash(message, 'danger')
        return redirect(url_for('clasificacion_nuevo'))

@app.route('/admin/clasificaciones/<int:id>')
@admin_required
def clasificacion_detalle(id):
    """Muestra el detalle de una clasificación"""
    clasificacion = ClasificacionController.obtener_por_id(id)  # Llamar directamente al método estático
    
    if not clasificacion:
        flash('Clasificación no encontrada', 'danger')
        return redirect(url_for('clasificacion_lista'))
    
    return render_template('clasificacion/detalle.html', clasificacion=clasificacion)

@app.route('/admin/clasificaciones/<int:id>/editar')
@admin_required
def clasificacion_editar(id):
    """Formulario para editar clasificación"""
    controller = ClasificacionController()
    clasificacion = controller.obtener_por_id(id)
    
    if not clasificacion:
        flash('Clasificación no encontrada', 'danger')
        return redirect(url_for('clasificacion_lista'))
    
    return render_template('clasificacion/editar.html', clasificacion=clasificacion)

@app.route('/admin/clasificaciones/<int:id>/actualizar', methods=['POST'])
@admin_required
def clasificacion_actualizar(id):
    """Actualiza una clasificación existente"""
    controller = ClasificacionController()
    success, message, clasificacion = controller.actualizar(id, request.form)
    
    if success:
        flash(message, 'success')
        # CORREGIDO: Agregar el parámetro id
        return redirect(url_for('clasificacion_detalle', id=id))
    else:
        flash(message, 'danger')
        return redirect(url_for('clasificacion_editar', id=id))

@app.route('/admin/clasificaciones/<int:id>/eliminar', methods=['POST'])
@admin_required
def clasificacion_eliminar(id):
    """Elimina (desactiva) una clasificación"""
    controller = ClasificacionController()
    success, message = controller.eliminar(id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('clasificacion_lista'))

# ==================== RUTAS CRUD PARA IDIOMA ====================

@app.route('/admin/idiomas')
@admin_required
def idioma_lista():
    """Lista todos los idiomas"""
    idiomas = IdiomaController.obtener_todos()
    return render_template('idioma/lista.html', idiomas=idiomas)

@app.route('/admin/idiomas/nuevo')
@admin_required
def idioma_nuevo():
    """Formulario para nuevo idioma"""
    return render_template('idioma/nuevo.html')

@app.route('/admin/idiomas/crear', methods=['POST'])
@admin_required
def idioma_crear():
    """Crea un nuevo idioma"""
    success, message, idioma = IdiomaController.crear(request.form)
    
    if success:
        flash(message, 'success')
        return redirect(url_for('idioma_lista'))
    else:
        flash(message, 'danger')
        return redirect(url_for('idioma_nuevo'))

@app.route('/admin/idiomas/<int:id>')
@admin_required
def idioma_detalle(id):
    """Muestra el detalle de un idioma"""
    idioma = IdiomaController.obtener_por_id(id)
    
    if not idioma:
        flash('Idioma no encontrado', 'danger')
        return redirect(url_for('idioma_lista'))
    
    return render_template('idioma/detalle.html', idioma=idioma)

@app.route('/admin/idiomas/<int:id>/editar')
@admin_required
def idioma_editar(id):
    """Formulario para editar idioma"""
    idioma = IdiomaController.obtener_por_id(id)
    
    if not idioma:
        flash('Idioma no encontrado', 'danger')
        return redirect(url_for('idioma_lista'))
    
    return render_template('idioma/editar.html', idioma=idioma)

@app.route('/admin/idiomas/<int:id>/actualizar', methods=['POST'])
@admin_required
def idioma_actualizar(id):
    """Actualiza un idioma existente"""
    success, message, idioma = IdiomaController.actualizar(id, request.form)
    
    if success:
        flash(message, 'success')
        return redirect(url_for('idioma_detalle', id=id))
    else:
        flash(message, 'danger')
        return redirect(url_for('idioma_editar', id=id))

@app.route('/admin/idiomas/<int:id>/eliminar', methods=['POST'])
@admin_required
def idioma_eliminar(id):
    """Elimina (desactiva) un idioma"""
    success, message = IdiomaController.eliminar(id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('idioma_lista'))


# ==================== RUTAS CRUD PARA PELICULA_GENERO ====================

@app.route('/admin/peliculas-generos')
@admin_required
def pelicula_genero_lista():
    """Lista todas las relaciones película-género con paginación"""
    try:
        # Obtener parámetros de filtro
        pagina = request.args.get('page', 1, type=int)
        pelicula_id = request.args.get('pelicula_id', '')
        genero_id = request.args.get('genero_id', '')
        
        # Preparar filtros
        filtros = {}
        if pelicula_id:
            filtros['pelicula_id'] = int(pelicula_id)
        if genero_id:
            filtros['genero_id'] = int(genero_id)
        
        # Obtener datos paginados del controlador
        resultado = PeliculaGeneroController.obtener_todos_paginados(
            pagina=pagina, 
            por_pagina=25,
            filtros=filtros
        )
        
        # Obtener datos adicionales para filtros
        peliculas_filtro = PeliculaAdminController.obtener_todas_activas()
        generos_filtro = GeneroController.obtener_todos()
        
        # Calcular estadísticas
        total_peliculas = len(set([rel.IdPelicula for rel in resultado['relaciones']]))
        total_generos = len(set([rel.IdGenero for rel in resultado['relaciones']]))
        
        # Calcular promedio de géneros por película
        if total_peliculas > 0:
            promedio_generos = round(len(resultado['relaciones']) / total_peliculas, 1)
        else:
            promedio_generos = 0
        
        return render_template(
            'pelicula_genero/lista.html',
            relaciones=resultado['relaciones'],
            total_relaciones=resultado['total'],
            total_peliculas=total_peliculas,
            total_generos=total_generos,
            promedio_generos=promedio_generos,
            peliculas_filtro=peliculas_filtro,
            generos_filtro=generos_filtro,
            pelicula_id=pelicula_id,
            genero_id=genero_id,
            pagination={
                'page': resultado['pagina'],
                'per_page': resultado['por_pagina'],
                'total': resultado['total'],
                'pages': resultado['paginas'],
                'has_prev': resultado['pagina'] > 1,
                'has_next': resultado['pagina'] < resultado['paginas'],
                'prev_num': resultado['pagina'] - 1 if resultado['pagina'] > 1 else None,
                'next_num': resultado['pagina'] + 1 if resultado['pagina'] < resultado['paginas'] else None,
                'iter_pages': range(1, resultado['paginas'] + 1) if resultado['paginas'] > 0 else []
            }
        )
    except Exception as e:
        flash(f'Error al obtener relaciones: {str(e)}', 'danger')
        return render_template('pelicula_genero/lista.html', relaciones=[], total_relaciones=0)

@app.route('/admin/peliculas-generos/nuevo')
@admin_required
def pelicula_genero_nuevo():
    """Formulario para nueva relación película-género"""
    
    peliculas = PeliculaController.obtener_todas_con_generos()
    generos = GeneroController.obtener_todos()
    
    return render_template(
        'pelicula_genero/nuevo.html',
        peliculas=peliculas,
        generos=generos
    )

@app.route('/admin/peliculas-generos/crear', methods=['POST'])
@admin_required
def pelicula_genero_crear():
    """Crea una nueva relación película-género"""
    success, message, relacion = PeliculaGeneroController.crear(request.form)
    
    if success:
        flash(message, 'success')
        return redirect(url_for('pelicula_genero_lista'))
    else:
        flash(message, 'danger')
        return redirect(url_for('pelicula_genero_nuevo'))

@app.route('/admin/peliculas-generos/<int:id>')
@admin_required
def pelicula_genero_detalle(id):
    """Muestra el detalle de una relación"""
    
    relacion = PeliculaGeneroController.obtener_por_id(id)
    
    if not relacion:
        flash('Relación no encontrada', 'danger')
        return redirect(url_for('pelicula_genero_lista'))
    
    # Obtener estadísticas adicionales
    # Total de géneros que tiene esta película
    total_generos_pelicula = PeliculaController.contar_generos_por_pelicula(relacion.IdPelicula)
    
    # Total de películas que tienen este género
    total_peliculas_genero = GeneroController.contar_peliculas_por_genero(relacion.IdGenero)
    
    return render_template(
        'pelicula_genero/detalle.html',
        relacion=relacion,
        total_generos_pelicula=total_generos_pelicula,
        total_peliculas_genero=total_peliculas_genero
    )

@app.route('/admin/peliculas-generos/<int:id>/editar')
@admin_required
def pelicula_genero_editar(id):
    """Formulario para editar relación película-género"""

    relacion = PeliculaGeneroController.obtener_por_id(id)
    
    if not relacion:
        flash('Relación no encontrada', 'danger')
        return redirect(url_for('pelicula_genero_lista'))
    
    peliculas = PeliculaAdminController.obtener_todas_activas()
    generos = GeneroController.obtener_todos()
    
    return render_template(
        'pelicula_genero/editar.html',
        relacion=relacion,
        peliculas=peliculas,
        generos=generos
    )

@app.route('/admin/peliculas-generos/<int:id>/actualizar', methods=['POST'])
@admin_required
def pelicula_genero_actualizar(id):
    """Actualiza una relación existente"""
    success, message, relacion = PeliculaGeneroController.actualizar(id, request.form)
    
    if success:
        flash(message, 'success')
        return redirect(url_for('pelicula_genero_detalle', id=id))
    else:
        flash(message, 'danger')
        return redirect(url_for('pelicula_genero_editar', id=id))

@app.route('/admin/peliculas-generos/<int:id>/eliminar', methods=['POST'])
@admin_required
def pelicula_genero_eliminar(id):
    """Elimina una relación película-género"""
    success, message = PeliculaGeneroController.eliminar(id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('pelicula_genero_lista'))

# ==================== RUTAS CRUD PARA GENERO ====================

@app.route('/admin/generos')
@admin_required
def genero_lista():
    """Lista todos los géneros"""
    generos = GeneroController.obtener_todos()
    return render_template('genero/lista.html', generos=generos)

@app.route('/admin/generos/nuevo')
@admin_required
def genero_nuevo():
    """Formulario para nuevo género"""
    return render_template('genero/nuevo.html')

@app.route('/admin/generos/crear', methods=['POST'])
@admin_required
def genero_crear():
    """Crea un nuevo género"""
    success, message, genero = GeneroController.crear(request.form)
    
    if success:
        flash(message, 'success')
        return redirect(url_for('genero_lista'))
    else:
        flash(message, 'danger')
        return redirect(url_for('genero_nuevo'))

@app.route('/admin/generos/<int:id>')
@admin_required
def genero_detalle(id):
    """Muestra el detalle de un género"""
    genero = GeneroController.obtener_por_id(id)
    
    if not genero:
        flash('Género no encontrado', 'danger')
        return redirect(url_for('genero_lista'))
    
    return render_template('genero/detalle.html', genero=genero)

@app.route('/admin/generos/<int:id>/editar')
@admin_required
def genero_editar(id):
    """Formulario para editar género"""
    genero = GeneroController.obtener_por_id(id)
    
    if not genero:
        flash('Género no encontrado', 'danger')
        return redirect(url_for('genero_lista'))
    
    return render_template('genero/editar.html', genero=genero)

@app.route('/admin/generos/<int:id>/actualizar', methods=['POST'])
@admin_required
def genero_actualizar(id):
    """Actualiza un género existente"""
    success, message, genero = GeneroController.actualizar(id, request.form)
    
    if success:
        flash(message, 'success')
        return redirect(url_for('genero_detalle', id=id))
    else:
        flash(message, 'danger')
        return redirect(url_for('genero_editar', id=id))

@app.route('/admin/generos/<int:id>/eliminar', methods=['POST'])
@admin_required
def genero_eliminar(id):
    """Elimina (desactiva) un género"""
    success, message = GeneroController.eliminar(id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('genero_lista'))

@app.route('/admin/roles')
@admin_required
def rol_lista():
    return render_template('rol_usuario/lista.html')

@app.route('/admin/tipos-boleto')
@admin_required
def tipo_boleto_lista():
    return render_template('tipo_boleto/lista.html')

@app.route('/admin/cines')
@admin_required
def cine_lista():
    return render_template('cine/lista.html')

@app.route('/admin/tipos-sala')
@admin_required
def tipo_sala_lista():
    return render_template('tipo_sala/lista.html')

@app.route('/admin/salas')
@admin_required
def sala_lista():
    return render_template('sala/lista.html')

@app.route('/admin/asientos')
@admin_required
def asiento_lista():
    return render_template('asiento/lista.html')

@app.route('/admin/peliculas')
@admin_required
def pelicula_lista():
    return render_template('pelicula/lista.html')

@app.route('/admin/funciones')
@admin_required
def funcion_lista():
    return render_template('funcion/lista.html')

@app.route('/admin/usuarios')
@admin_required
def usuario_lista():
    return render_template('usuario/lista.html')

@app.route('/admin/boletos')
@admin_required
def boleto_lista():
    return render_template('boleto/lista.html')

@app.route('/admin/boletos-cancelados')
@admin_required
def boleto_cancelado_lista():
    return render_template('boleto_cancelado/lista.html')

@app.route('/admin/boletos-usados')
@admin_required
def boleto_usado_lista():
    return render_template('boleto_usado/lista.html')

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
