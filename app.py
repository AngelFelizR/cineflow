# app.py
# Aplicación web Flask para el Sistema de Biblioteca

from models import login_manager, bcrypt, db
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'cineflow_secret_key_change_in_production_2025'

login_manager.init_app(app)
bcrypt.init_app(app)

# ==================== RUTAS PRINCIPALES ====================

@app.route('/')
@app.route('/index')
def index():
    """Página de inicio con estadísticas"""
    return render_template('base.html')

@app.route('/cartelera')
def lista_cartelera():
    # Esta es la ruta que causaba el error BuildError
    return render_template('lista_cartelera.html')

@app.route('/proximamente')
def lista_proximamente():
    return render_template('lista_proximamente.html')

# =========================
# Rutas de Autenticación
# =========================

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/logout')
def logout():
    # Aquí usualmente rediriges tras cerrar sesión
    return redirect(url_for('lista_cartelera'))

# =========================
# Rutas de Usuario
# =========================

@app.route('/perfil/actualizar')
def usuario_actualizar_datos():
    return render_template('usuario_actualizar_datos.html')

@app.route('/perfil/password')
def usuario_cambiar_password():
    return render_template('usuario_cambiar_password.html')

# =========================
# Rutas de Boletos
# =========================

@app.route('/mis-boletos')
def boletos_lista():
    return render_template('boletos_lista.html')

@app.route('/boletos/devueltos')
def boletos_devueltos():
    return render_template('boletos_devueltos.html')

# ==================== RUTAS DE LIBROS ====================


# ==================== RUTAS DE USUARIOS ====================



# ==================== EJECUCIÓN ====================

if __name__ == '__main__':
    print("=" * 80)
    print("CineFlow - APLICACIÓN WEB")
    print("=" * 80)
    print("\nIniciando servidor Flask...")
    print("Accede a la aplicación en: http://localhost:5001")
    print("\nPresiona Ctrl+C para detener el servidor")
    print("=" * 80)

    app.run(debug=True, host='0.0.0.0', port=5001)
