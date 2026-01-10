# app.py
# Aplicación web Flask para el Sistema de Biblioteca

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from controllers import LibroController, UsuarioController, PrestamoController, CategoriaController, AutorController
from datetime import datetime
from database import db

app = Flask(__name__)
app.secret_key = 'biblioteca_secret_key_change_in_production_2025'

# Inicializar controladores
libro_controller = LibroController()
usuario_controller = UsuarioController()
prestamo_controller = PrestamoController()
categoria_controller = CategoriaController()
autor_controller = AutorController()

# ==================== RUTAS PRINCIPALES ====================

@app.route('/')
def index():
    """Página de inicio con estadísticas"""
    try:
        # Obtener datos para el dashboard
        libros = libro_controller.obtener_todos()
        usuarios = usuario_controller.obtener_todos()
        prestamos = prestamo_controller.obtener_prestamos_activos()
        prestamos_vencidos = prestamo_controller.obtener_prestamos_vencidos()
        disponibles = libro_controller.obtener_disponibles()

        stats = {
            'total_libros': len(libros),
            'total_usuarios': len(usuarios),
            'prestamos_activos': len(prestamos),
            'prestamos_vencidos': len(prestamos_vencidos),
            'libros_disponibles': len(disponibles)
        }

        return render_template('index.html', stats=stats)
    except Exception as e:
        flash(f'Error al cargar estadísticas: {e}', 'danger')
        return render_template('index.html', stats={})

# ==================== RUTAS DE LIBROS ====================

@app.route('/libros')
def libros_lista():
    """Lista todos los libros"""
    try:
        libros = libro_controller.obtener_todos()
        return render_template('libros/lista.html', libros=libros)
    except Exception as e:
        flash(f'Error al cargar libros: {e}', 'danger')
        return render_template('libros/lista.html', libros=[])

@app.route('/libros/buscar')
def libros_buscar():
    """Busca libros por término"""
    termino = request.args.get('q', '')
    try:
        if termino:
            libros = libro_controller.buscar(termino)
        else:
            libros = libro_controller.obtener_todos()
        return render_template('libros/lista.html', libros=libros, termino_busqueda=termino)
    except Exception as e:
        flash(f'Error en la búsqueda: {e}', 'danger')
        return render_template('libros/lista.html', libros=[], termino_busqueda=termino)

@app.route('/libros/<int:libro_id>')
def libro_detalle(libro_id):
    """Muestra los detalles de un libro"""
    try:
        libro = libro_controller.obtener_por_id(libro_id)
        if libro:
            # Obtener historial de préstamos del libro
            prestamos = prestamo_controller.obtener_por_libro(libro_id)
            return render_template('libros/detalle.html', libro=libro, prestamos=prestamos)
        else:
            flash('Libro no encontrado', 'warning')
            return redirect(url_for('libros_lista'))
    except Exception as e:
        flash(f'Error al cargar libro: {e}', 'danger')
        return redirect(url_for('libros_lista'))

@app.route('/libros/nuevo', methods=['GET', 'POST'])
def libro_nuevo():
    """Crea un nuevo libro"""
    if request.method == 'POST':
        try:
            datos = {
                'titulo': request.form['titulo'],
                'isbn': request.form['isbn'],
                'autor_id': int(request.form['autor_id']),
                'categoria_id': int(request.form['categoria_id']),
                'editorial': request.form.get('editorial'),
                'ano_publicacion': int(request.form['ano_publicacion']) if request.form.get('ano_publicacion') else None,
                'copias_total': int(request.form.get('copias_total', 1)),
                'copias_disponibles': int(request.form.get('copias_disponibles', 1))
            }

            exito, mensaje, libro_id = libro_controller.crear(datos)

            if exito:
                flash(mensaje, 'success')
                return redirect(url_for('libro_detalle', libro_id=libro_id))
            else:
                flash(mensaje, 'danger')
        except Exception as e:
            flash(f'Error al crear libro: {e}', 'danger')

    # Obtener autores y categorías para el formulario
    from models import Autor, Categoria
    session = db.get_session()
    try:
        autores = session.query(Autor).order_by(Autor.Nombre, Autor.Apellido).all()
        categorias = session.query(Categoria).order_by(Categoria.NombreCategoria).all()
        for autor in autores:
            session.expunge(autor)
        for categoria in categorias:
            session.expunge(categoria)
    finally:
        session.close()

    from datetime import datetime
    current_year = datetime.now().year

    return render_template('libros/form.html', libro=None, autores=autores,
                          categorias=categorias, current_year=current_year)

@app.route('/libros/<int:libro_id>/editar', methods=['GET', 'POST'])
def libro_editar(libro_id):
    """Edita un libro existente"""
    libro = libro_controller.obtener_por_id(libro_id)

    if not libro:
        flash('Libro no encontrado', 'warning')
        return redirect(url_for('libros_lista'))

    if request.method == 'POST':
        try:
            datos = {
                'Titulo': request.form['titulo'],
                'ISBN': request.form['isbn'],
                'AutorID': int(request.form['autor_id']),
                'CategoriaID': int(request.form['categoria_id']),
                'Editorial': request.form.get('editorial'),
                'AnoPublicacion': int(request.form['ano_publicacion']) if request.form.get('ano_publicacion') else None,
                'CopiasTotal': int(request.form.get('copias_total', 1)),
                'CopiasDisponibles': int(request.form.get('copias_disponibles', 0))
            }

            exito, mensaje = libro_controller.actualizar(libro_id, datos)

            if exito:
                flash(mensaje, 'success')
                return redirect(url_for('libro_detalle', libro_id=libro_id))
            else:
                flash(mensaje, 'danger')
        except Exception as e:
            flash(f'Error al actualizar libro: {e}', 'danger')

    # Obtener autores y categorías para el formulario
    from models import Autor, Categoria
    session = db.get_session()
    try:
        autores = session.query(Autor).order_by(Autor.Nombre, Autor.Apellido).all()
        categorias = session.query(Categoria).order_by(Categoria.NombreCategoria).all()
        for autor in autores:
            session.expunge(autor)
        for categoria in categorias:
            session.expunge(categoria)
    finally:
        session.close()

    from datetime import datetime
    current_year = datetime.now().year

    return render_template('libros/form.html', libro=libro, autores=autores,
                          categorias=categorias, current_year=current_year)

@app.route('/libros/<int:libro_id>/eliminar', methods=['POST'])
def libro_eliminar(libro_id):
    """Elimina un libro"""
    try:
        exito, mensaje = libro_controller.eliminar(libro_id)

        if exito:
            flash(mensaje, 'success')
        else:
            flash(mensaje, 'danger')
    except Exception as e:
        flash(f'Error al eliminar libro: {e}', 'danger')

    return redirect(url_for('libros_lista'))

# ==================== RUTAS DE USUARIOS ====================

@app.route('/usuarios')
def usuarios_lista():
    """Lista todos los usuarios"""
    try:
        usuarios = usuario_controller.obtener_todos()
        return render_template('usuarios/lista.html', usuarios=usuarios)
    except Exception as e:
        flash(f'Error al cargar usuarios: {e}', 'danger')
        return render_template('usuarios/lista.html', usuarios=[])

@app.route('/usuarios/<int:usuario_id>')
def usuario_detalle(usuario_id):
    """Muestra los detalles de un usuario"""
    try:
        usuario = usuario_controller.obtener_por_id(usuario_id)
        if usuario:
            prestamos = usuario_controller.obtener_prestamos_activos(usuario_id)
            return render_template('usuarios/detalle.html', usuario=usuario, prestamos=prestamos)
        else:
            flash('Usuario no encontrado', 'warning')
            return redirect(url_for('usuarios_lista'))
    except Exception as e:
        flash(f'Error al cargar usuario: {e}', 'danger')
        return redirect(url_for('usuarios_lista'))

@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
def usuario_nuevo():
    """Crea un nuevo usuario"""
    if request.method == 'POST':
        try:
            datos = {
                'numero_carnet': request.form['numero_carnet'],
                'nombre': request.form['nombre'],
                'apellido': request.form['apellido'],
                'email': request.form['email'],
                'telefono': request.form.get('telefono'),
                'direccion': request.form.get('direccion')
            }

            exito, mensaje, usuario_id = usuario_controller.crear(datos)

            if exito:
                flash(mensaje, 'success')
                return redirect(url_for('usuario_detalle', usuario_id=usuario_id))
            else:
                flash(mensaje, 'danger')
        except Exception as e:
            flash(f'Error al crear usuario: {e}', 'danger')

    return render_template('usuarios/form.html', usuario=None)

@app.route('/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
def usuario_editar(usuario_id):
    """Edita un usuario existente"""
    usuario = usuario_controller.obtener_por_id(usuario_id)

    if not usuario:
        flash('Usuario no encontrado', 'warning')
        return redirect(url_for('usuarios_lista'))

    if request.method == 'POST':
        try:
            datos = {
                'NumeroCarnet': request.form['numero_carnet'],
                'Nombre': request.form['nombre'],
                'Apellido': request.form['apellido'],
                'Email': request.form['email'],
                'Telefono': request.form.get('telefono'),
                'Direccion': request.form.get('direccion')
            }

            exito, mensaje = usuario_controller.actualizar(usuario_id, datos)

            if exito:
                flash(mensaje, 'success')
                return redirect(url_for('usuario_detalle', usuario_id=usuario_id))
            else:
                flash(mensaje, 'danger')
        except Exception as e:
            flash(f'Error al actualizar usuario: {e}', 'danger')

    return render_template('usuarios/form.html', usuario=usuario)

# ==================== RUTAS DE CATEGORÍAS ====================

@app.route('/categorias')
def categorias_lista():
    """Lista todas las categorías"""
    try:
        categorias = categoria_controller.obtener_todos()
        return render_template('categorias/lista.html', categorias=categorias)
    except Exception as e:
        flash(f'Error al cargar categorías: {e}', 'danger')
        return render_template('categorias/lista.html', categorias=[])

@app.route('/categorias/buscar')
def categorias_buscar():
    """Busca categorías por término"""
    termino = request.args.get('q', '')
    try:
        if termino:
            categorias = categoria_controller.buscar(termino)
        else:
            categorias = categoria_controller.obtener_todos()
        return render_template('categorias/lista.html', categorias=categorias, termino_busqueda=termino)
    except Exception as e:
        flash(f'Error en la búsqueda: {e}', 'danger')
        return render_template('categorias/lista.html', categorias=[], termino_busqueda=termino)

@app.route('/categorias/<int:categoria_id>')
def categoria_detalle(categoria_id):
    """Muestra los detalles de una categoría"""
    try:
        categoria = categoria_controller.obtener_por_id(categoria_id)
        if categoria:
            return render_template('categorias/detalle.html', categoria=categoria)
        else:
            flash('Categoría no encontrada', 'warning')
            return redirect(url_for('categorias_lista'))
    except Exception as e:
        flash(f'Error al cargar categoría: {e}', 'danger')
        return redirect(url_for('categorias_lista'))

@app.route('/categorias/nuevo', methods=['GET', 'POST'])
def categoria_nueva():
    """Crea una nueva categoría"""
    if request.method == 'POST':
        try:
            datos = {
                'nombre_categoria': request.form['nombre_categoria'],
                'descripcion': request.form.get('descripcion')
            }

            exito, mensaje, categoria_id = categoria_controller.crear(datos)

            if exito:
                flash(mensaje, 'success')
                return redirect(url_for('categoria_detalle', categoria_id=categoria_id))
            else:
                flash(mensaje, 'danger')
        except Exception as e:
            flash(f'Error al crear categoría: {e}', 'danger')

    return render_template('categorias/form.html', categoria=None)

@app.route('/categorias/<int:categoria_id>/editar', methods=['GET', 'POST'])
def categoria_editar(categoria_id):
    """Edita una categoría existente"""
    categoria = categoria_controller.obtener_por_id(categoria_id)

    if not categoria:
        flash('Categoría no encontrada', 'warning')
        return redirect(url_for('categorias_lista'))

    if request.method == 'POST':
        try:
            datos = {
                'NombreCategoria': request.form['nombre_categoria'],
                'Descripcion': request.form.get('descripcion')
            }

            exito, mensaje = categoria_controller.actualizar(categoria_id, datos)

            if exito:
                flash(mensaje, 'success')
                return redirect(url_for('categoria_detalle', categoria_id=categoria_id))
            else:
                flash(mensaje, 'danger')
        except Exception as e:
            flash(f'Error al actualizar categoría: {e}', 'danger')

    return render_template('categorias/form.html', categoria=categoria)

@app.route('/categorias/<int:categoria_id>/eliminar', methods=['POST'])
def categoria_eliminar(categoria_id):
    """Elimina una categoría"""
    try:
        exito, mensaje = categoria_controller.eliminar(categoria_id)

        if exito:
            flash(mensaje, 'success')
        else:
            flash(mensaje, 'danger')
    except Exception as e:
        flash(f'Error al eliminar categoría: {e}', 'danger')

    return redirect(url_for('categorias_lista'))

# ==================== RUTAS DE AUTORES ====================

@app.route('/autores')
def autores_lista():
    """Lista todos los autores"""
    try:
        autores = autor_controller.obtener_todos()
        return render_template('autores/lista.html', autores=autores)
    except Exception as e:
        flash(f'Error al cargar autores: {e}', 'danger')
        return render_template('autores/lista.html', autores=[])

@app.route('/autores/buscar')
def autores_buscar():
    """Busca autores por término"""
    termino = request.args.get('q', '')
    try:
        if termino:
            autores = autor_controller.buscar(termino)
        else:
            autores = autor_controller.obtener_todos()
        return render_template('autores/lista.html', autores=autores, termino_busqueda=termino)
    except Exception as e:
        flash(f'Error en la búsqueda: {e}', 'danger')
        return render_template('autores/lista.html', autores=[], termino_busqueda=termino)

@app.route('/autores/<int:autor_id>')
def autor_detalle(autor_id):
    """Muestra los detalles de un autor"""
    try:
        autor = autor_controller.obtener_por_id(autor_id)
        if autor:
            return render_template('autores/detalle.html', autor=autor)
        else:
            flash('Autor no encontrado', 'warning')
            return redirect(url_for('autores_lista'))
    except Exception as e:
        flash(f'Error al cargar autor: {e}', 'danger')
        return redirect(url_for('autores_lista'))

@app.route('/autores/nuevo', methods=['GET', 'POST'])
def autor_nuevo():
    """Crea un nuevo autor"""
    if request.method == 'POST':
        try:
            # Procesar fecha de nacimiento si existe
            fecha_nacimiento = None
            if request.form.get('fecha_nacimiento'):
                from datetime import datetime
                fecha_nacimiento = datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d').date()

            datos = {
                'nombre': request.form['nombre'],
                'apellido': request.form['apellido'],
                'nacionalidad': request.form.get('nacionalidad'),
                'fecha_nacimiento': fecha_nacimiento,
                'biografia': request.form.get('biografia')
            }

            exito, mensaje, autor_id = autor_controller.crear(datos)

            if exito:
                flash(mensaje, 'success')
                return redirect(url_for('autor_detalle', autor_id=autor_id))
            else:
                flash(mensaje, 'danger')
        except Exception as e:
            flash(f'Error al crear autor: {e}', 'danger')

    return render_template('autores/form.html', autor=None)

@app.route('/autores/<int:autor_id>/editar', methods=['GET', 'POST'])
def autor_editar(autor_id):
    """Edita un autor existente"""
    autor = autor_controller.obtener_por_id(autor_id)

    if not autor:
        flash('Autor no encontrado', 'warning')
        return redirect(url_for('autores_lista'))

    if request.method == 'POST':
        try:
            # Procesar fecha de nacimiento si existe
            fecha_nacimiento = None
            if request.form.get('fecha_nacimiento'):
                from datetime import datetime
                fecha_nacimiento = datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d').date()

            datos = {
                'Nombre': request.form['nombre'],
                'Apellido': request.form['apellido'],
                'Nacionalidad': request.form.get('nacionalidad'),
                'FechaNacimiento': fecha_nacimiento,
                'Biografia': request.form.get('biografia')
            }

            exito, mensaje = autor_controller.actualizar(autor_id, datos)

            if exito:
                flash(mensaje, 'success')
                return redirect(url_for('autor_detalle', autor_id=autor_id))
            else:
                flash(mensaje, 'danger')
        except Exception as e:
            flash(f'Error al actualizar autor: {e}', 'danger')

    return render_template('autores/form.html', autor=autor)

@app.route('/autores/<int:autor_id>/eliminar', methods=['POST'])
def autor_eliminar(autor_id):
    """Elimina un autor"""
    try:
        exito, mensaje = autor_controller.eliminar(autor_id)

        if exito:
            flash(mensaje, 'success')
        else:
            flash(mensaje, 'danger')
    except Exception as e:
        flash(f'Error al eliminar autor: {e}', 'danger')

    return redirect(url_for('autores_lista'))

# ==================== RUTAS DE PRÉSTAMOS ====================

@app.route('/prestamos')
def prestamos_lista():
    """Lista todos los préstamos activos"""
    try:
        prestamos = prestamo_controller.obtener_prestamos_activos()
        return render_template('prestamos/lista.html', prestamos=prestamos, titulo='Préstamos Activos')
    except Exception as e:
        flash(f'Error al cargar préstamos: {e}', 'danger')
        return render_template('prestamos/lista.html', prestamos=[], titulo='Préstamos Activos')

@app.route('/prestamos/vencidos')
def prestamos_vencidos():
    """Lista todos los préstamos vencidos"""
    try:
        prestamos = prestamo_controller.obtener_prestamos_vencidos()
        return render_template('prestamos/lista.html', prestamos=prestamos, titulo='Préstamos Vencidos')
    except Exception as e:
        flash(f'Error al cargar préstamos vencidos: {e}', 'danger')
        return render_template('prestamos/lista.html', prestamos=[], titulo='Préstamos Vencidos')

@app.route('/prestamos/nuevo', methods=['GET', 'POST'])
def prestamo_nuevo():
    """Crea un nuevo préstamo"""
    if request.method == 'POST':
        try:
            libro_id = int(request.form['libro_id'])
            usuario_id = int(request.form['usuario_id'])
            dias = int(request.form.get('dias_prestamo', 14))

            exito, mensaje, prestamo_id = prestamo_controller.crear_prestamo(libro_id, usuario_id, dias)

            if exito:
                flash(mensaje, 'success')
                return redirect(url_for('prestamos_lista'))
            else:
                flash(mensaje, 'danger')
        except Exception as e:
            flash(f'Error al crear préstamo: {e}', 'danger')

    # Obtener libros disponibles y usuarios activos para el formulario
    libros_disponibles = libro_controller.obtener_disponibles()
    usuarios_activos = [u for u in usuario_controller.obtener_todos() if u.Estado == 'Activo']

    return render_template('prestamos/form.html',
                          libros_disponibles=libros_disponibles,
                          usuarios_activos=usuarios_activos)

@app.route('/prestamos/<int:prestamo_id>/devolver', methods=['POST'])
def prestamo_devolver(prestamo_id):
    """Procesa la devolución de un libro"""
    try:
        exito, mensaje, multa = prestamo_controller.devolver_libro(prestamo_id)

        if exito:
            flash(mensaje, 'success')
        else:
            flash(mensaje, 'danger')
    except Exception as e:
        flash(f'Error al devolver libro: {e}', 'danger')

    return redirect(url_for('prestamos_lista'))

# ==================== API ENDPOINTS (JSON) ====================

@app.route('/api/libros')
def api_libros():
    """API endpoint para obtener libros en formato JSON"""
    try:
        libros = libro_controller.obtener_todos()

        libros_json = []
        for libro in libros:
            libros_json.append({
                'id': libro.LibroID,
                'titulo': libro.Titulo,
                'isbn': libro.ISBN,
                'autor': libro.autor.nombre_completo,
                'categoria': libro.categoria.NombreCategoria,
                'disponibles': libro.CopiasDisponibles,
                'total': libro.CopiasTotal
            })

        return jsonify(libros_json)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios')
def api_usuarios():
    """API endpoint para obtener usuarios en formato JSON"""
    try:
        usuarios = usuario_controller.obtener_todos()

        usuarios_json = []
        for usuario in usuarios:
            usuarios_json.append({
                'id': usuario.UsuarioID,
                'carnet': usuario.NumeroCarnet,
                'nombre': usuario.nombre_completo,
                'email': usuario.Email,
                'estado': usuario.Estado
            })

        return jsonify(usuarios_json)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prestamos')
def api_prestamos():
    """API endpoint para obtener préstamos en formato JSON"""
    try:
        prestamos = prestamo_controller.obtener_prestamos_activos()

        prestamos_json = []
        for prestamo in prestamos:
            prestamos_json.append({
                'id': prestamo.PrestamoID,
                'libro': prestamo.libro.Titulo,
                'usuario': prestamo.usuario.nombre_completo,
                'fecha_prestamo': prestamo.FechaPrestamo.strftime('%Y-%m-%d'),
                'fecha_devolucion': prestamo.FechaDevolucionEsperada.strftime('%Y-%m-%d'),
                'dias_restantes': prestamo.dias_restantes,
                'estado': prestamo.Estado
            })

        return jsonify(prestamos_json)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== MANEJO DE ERRORES ====================

@app.errorhandler(404)
def not_found(error):
    """Página de error 404"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Página de error 500"""
    return render_template('500.html'), 500

# ==================== FILTROS PERSONALIZADOS ====================

@app.template_filter('format_date')
def format_date(date):
    """Formatea una fecha"""
    if date:
        return date.strftime('%d/%m/%Y')
    return 'N/A'

@app.template_filter('format_datetime')
def format_datetime(dt):
    """Formatea una fecha y hora"""
    if dt:
        return dt.strftime('%d/%m/%Y %H:%M')
    return 'N/A'

# ==================== EJECUCIÓN ====================

if __name__ == '__main__':
    print("=" * 80)
    print("SISTEMA DE BIBLIOTECA - APLICACIÓN WEB")
    print("=" * 80)
    print("\nIniciando servidor Flask...")
    print("Accede a la aplicación en: http://localhost:5001")
    print("\nPresiona Ctrl+C para detener el servidor")
    print("=" * 80)

    app.run(debug=True, host='0.0.0.0', port=5001)
