import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from datetime import date
from functools import wraps
import MySQLdb.cursors


app = Flask(__name__)
app.secret_key = '1f3e9f870d33a713248d13d3e8dfc6bc2cbd68ea7f387a6d824bc7f4892f9b2a'  # Usá una cadena larga y únic



# Config MySQL
app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST")
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")
mysql = MySQL(app)



def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorada

@app.route('/')
def index():
    return render_template('index.html', data={'titulo': 'Inicio', 'bienvenida': 'Bienvenido al sistema de la cooperadora'})

# LISTADO DE SOCIOS


@app.route('/socios')
@login_requerido
def listar_socios():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM socio ORDER BY apellido, nombre")
    socios = cursor.fetchall()
    return render_template('socios/listar.html', socios=socios)


# NUEVO SOCIO - FORMULARIO
@app.route('/socios/nuevo')
@login_requerido
def nuevo_socio():
    return render_template('socios/nuevo.html')

# NUEVO SOCIO - GUARDAR
@app.route('/socios/guardar', methods=['POST'])
@login_requerido
def guardar_socio():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    dni = request.form['dni']
    email = request.form['email']
    telefono = request.form['telefono']
    fecha_alta = request.form['fecha_alta']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        INSERT INTO socio (nombre, apellido, dni, email, telefono, fecha_alta)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nombre, apellido, dni, email, telefono, fecha_alta))
    mysql.connection.commit()
    return redirect(url_for('listar_socios'))

# EDITAR SOCIO
@app.route('/socios/editar/<int:id>')
@login_requerido
def editar_socio(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM socio WHERE id = %s", (id,))
    socio = cursor.fetchone()
    return render_template('socios/editar.html', socio=socio)

# ACTUALIZAR SOCIO
@app.route('/socios/actualizar/<int:id>', methods=['POST'])
@login_requerido
def actualizar_socio(id):
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    dni = request.form['dni']
    email = request.form['email']
    telefono = request.form['telefono']
    fecha_alta = request.form['fecha_alta']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        UPDATE socio
        SET nombre=%s, apellido=%s, dni=%s, email=%s, telefono=%s, fecha_alta=%s
        WHERE id=%s
    """, (nombre, apellido, dni, email, telefono, fecha_alta, id))
    mysql.connection.commit()
    return redirect(url_for('listar_socios'))

# ELIMINAR SOCIO
@app.route('/socios/eliminar/<int:id>')
@login_requerido
def eliminar_socio(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM socio WHERE id = %s", (id,))
    mysql.connection.commit()
    return redirect(url_for('listar_socios'))

# VER PAGOS DE UN SOCIO
@app.route('/socios/<int:socio_id>/pagos')
@login_requerido
def ver_pagos(socio_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM pago WHERE socio_id = %s", (socio_id,))
    pagos = cursor.fetchall()
    cursor.execute("SELECT * FROM socio WHERE id = %s", (socio_id,))
    socio = cursor.fetchone()
    return render_template('pagos/listar.html', pagos=pagos, socio=socio)

# NUEVO PAGO - FORMULARIO
@app.route('/socios/<int:socio_id>/pagos/nuevo')
@login_requerido
def nuevo_pago(socio_id):
    return render_template('pagos/nuevo.html', socio_id=socio_id)

# GUARDAR NUEVO PAGO
@app.route('/socios/<int:socio_id>/pagos/guardar', methods=['POST'])
@login_requerido
def guardar_pago(socio_id):
    monto = request.form['monto']
    forma_pago = request.form['forma_pago']
    periodo = request.form['periodo']
    fecha_pago = request.form['fecha_pago']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        INSERT INTO pago (socio_id, monto, forma_pago, periodo, fecha_pago)
        VALUES (%s, %s, %s, %s, %s)
    """, (socio_id, monto, forma_pago, periodo, fecha_pago))
    mysql.connection.commit()
    return redirect(url_for('ver_pagos', socio_id=socio_id))

@app.route('/pagos')
@login_requerido
def listar_todos_pagos():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT pago.*, socio.nombre, socio.apellido
        FROM pago
        JOIN socio ON pago.socio_id = socio.id
        ORDER BY fecha_pago DESC
    """)
    pagos = cursor.fetchall()
    return render_template('pagos/todos.html', pagos=pagos)



# EDITAR PAGO
@app.route('/pagos/editar/<int:id>')
@login_requerido
def editar_pago(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM pago WHERE id = %s", (id,))
    pago = cursor.fetchone()
    return render_template('pagos/editar.html', pago=pago)

# ACTUALIZAR PAGO
@app.route('/pagos/actualizar/<int:id>', methods=['POST'])
@login_requerido
def actualizar_pago(id):
    monto = request.form['monto']
    forma_pago = request.form['forma_pago']
    periodo = request.form['periodo']
    fecha_pago = request.form['fecha_pago']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        UPDATE pago
        SET monto=%s, forma_pago=%s, periodo=%s, fecha_pago=%s
        WHERE id=%s
    """, (monto, forma_pago, periodo, fecha_pago, id))
    mysql.connection.commit()
    return redirect(request.referrer or url_for('dashboard'))

# ELIMINAR PAGO
@app.route('/pagos/eliminar/<int:id>')
@login_requerido
def eliminar_pago(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT socio_id FROM pago WHERE id = %s", (id,))
    socio_id = cursor.fetchone()['socio_id']
    cursor.execute("DELETE FROM pago WHERE id = %s", (id,))
    mysql.connection.commit()
    return redirect(url_for('ver_pagos', socio_id=socio_id))


@app.errorhandler(404)
def pagina_no_encontrada(e):
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuario WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        if usuario and check_password_hash(usuario[3], password):
            session['usuario_id'] = usuario[0]
            session['usuario_nombre'] = usuario[1]
            session['rol'] = usuario[4]
            return redirect(url_for('dashboard'))
        else:
            mensaje = 'Credenciales inválidas'
    return render_template('index.html', mensaje=mensaje)

@app.route('/logout')
def logout():
    session.clear()  # Borra toda la sesión
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_requerido
def dashboard():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT s.id, s.nombre, s.apellido,
               IFNULL(SUM(p.monto), 0) AS total_pagado
        FROM socio s
        LEFT JOIN pago p ON p.socio_id = s.id
        GROUP BY s.id
        ORDER BY total_pagado ASC
    """)
    socios = cursor.fetchall()
    return render_template('dashboard.html', socios=socios, usuario=session['usuario_nombre'])

@app.route('/prueba_bd')
def prueba_bd():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT COUNT(*) AS total_socios FROM socio")
        resultado = cursor.fetchone()
        return f"Conexión exitosa. Total de socios: {resultado[0]}"
    except Exception as e:
        return f"Error de conexión: {e}"

if __name__ == '__main__':
    app.run(debug=True, port=4000)