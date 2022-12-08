from flask import Flask,render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL, MySQLdb
import re

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import CircleModuleDrawer, GappedSquareModuleDrawer, HorizontalBarsDrawer, RoundedModuleDrawer, SquareModuleDrawer, VerticalBarsDrawer
import argparse
import os
from os import path #pip install notify-py
from notifypy import Notify


#https://github.com/Daniela8426/App_Citas/blob/main/app.py LOGIN

#SERvidor
app = Flask("QrWorld")

#CONEXION BASE DE DATOS
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'qr_world'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("historial.html")

@app.route("/QrWorld/loginFacial")
def shows():
    return render_template("login_facial.html")

@app.route("/QrWorld/login", methods=["GET", "POST"])
def login():
    msg = ''
    
    notificacion = Notify()

    if request.method == 'POST' and "usuario" in request.form and "passwordd" in request.form:
        usuario = request.form['usuario']
        pasword = request.form['passwordd']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM login_tradicional WHERE usuario = %s AND contrasena = %s', (usuario, pasword,))
        account = cursor.fetchone()
        
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id_usuario'] = account['id_usuario']
            session['usuario'] = account['usuario']
            
            notificacion.title='Logged in successfully!'
            notificacion.message="Bienvenido al sistema"
            notificacion.send()
            return render_template('home.html')
        else:
            msg = 'Usuario o Contraseña Incorrectas!'
            notificacion.title = "Error de Acceso"
            notificacion.message="Correo o contraseña no valida"
            notificacion.send()
            #return render_template("login.html")
    else:
        return render_template("login.html",msg=msg)

@app.route('/QrWorld/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id_usuario', None)
   session.pop('usuario', None)
   return redirect(url_for('login'))

@app.route("/QrWorld/registro", methods=["GET", "POST"])
def registro():
    
    msg = ''
    
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'usuario' in request.form and 'password' in request.form:
        name = request.form['name']
        email = request.form['email']
        usuario = request.form['usuario']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM login_tradicional WHERE usuario = %s',(usuario,))
        account = cursor.fetchone()
        
        if account:
            msg = 'El Usuario Ya Existe!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            msg = 'Dirrecion de Correo Invalida!'
        elif not re.match(r'[A-Za-z0-9]+', usuario):
            msg = 'El Usuario solo debe contener Caracteres y Numeros!'
        elif not usuario or not password or not email:
            msg = 'Rellene el formulario'
        else:
            cursor.execute("INSERT INTO login_tradicional(nombre, correo_electronico, usuario, contrasena) VALUES (%s, %s, %s,%s)",(name,email,usuario,password,))
            mysql.connection.commit()
            msg = 'Te Has Registrado Correctamente!'
            return render_template('registro.html', msg=msg)
            
    elif request.method == 'POST':
        msg = 'Por favor llena todos los campos!'
    return render_template('registro.html', msg=msg)
    
    #PRIMER CODIGO DE REGISRO
    
    
@app.route('/QrWorld/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html',username=session['usuario'])
    
    return redirect(url_for('login'))

@app.route('/QrWorld/profile')
def profile():
   
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM login_tradicional WHERE id_usuario = %s', (session['id_usuario'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

@app.route("/QrWorld/generador", methods=["GET", "POST"])
def generador():
    return render_template("ppp.html")

@app.route("/QrWorld/creacionQR", methods=['GET','POST'])
def creacionQR():
    if request.method == "POST":
        qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
            )

        #Obtenemos el valor del codigo QR o bien por parametro o bien pidiendo al usuario
        parser = argparse.ArgumentParser()
        parser.add_argument("-d","--dato", type=str,
                            help="Dato con el que se generara el codigo QR(URL,TEXTO,...)")
        parser.add_argument("-t","--tipo", type=str,
                            help="Tipo de QR[Circulo, cuadrado,Barra_Verticañ,Barra_horizontal,redondeado,Cuadrado_Grande]")
        parser.add_argument("-i", "--imagen", type=str,
                            help="Ruta y nombre de fichero de imagen .png con QR que se generara")
        args = parser.parse_args()

        #Obtenemos el parametro -d(dato)
        if args.dato:
            valorQR = args.dato
        else:
            valorQR = request.form['txtdato']
            
        #Obtenemos el parametro -t(tipo)
        if args.tipo:
            tipoQR = args.tipo
        else:
            tipoQR = request.form['tipoQr']
            tipoQR = tipoQR.upper()

        #Obtenemos el parametro -i(fichero de imagen QR)
        if args.imagen:
            imagenQR=args.imagen
        else:
            name = input("Ingrese el nombre con el que quiera guardar la imagen: ")
            if name == "":
                imagenQR = os.path.dirname(os.path.abspath(__file__)) + '\ ' + "qr" + '.png'
            else:
                imagenQR = os.path.dirname(os.path.abspath(__file__)) + '\ ' + name + '.png' #"C:\Program Files\Downloand" os.path.abspath(__file__)

        #Aplicamos el valor al objeto QR
        qr.add_data(valorQR)

        #Establecemos el tipo de QR segun el indicado por el parametro -t
        if tipoQR == 'CIRCULO':
            tipoQRC = CircleModuleDrawer()
        elif tipoQR == 'CUADRADO':
            tipoQRC = GappedSquareModuleDrawer()
        elif tipoQR == 'BARRA_VERTICAL':
            tipoQRC = VerticalBarsDrawer()
        elif tipoQR == 'BARRA_HORIZONTAL':
            tipoQRC = HorizontalBarsDrawer()
        elif tipoQR == 'REDONDEADO':
            tipoQRC = RoundedModuleDrawer()
        elif tipoQR == 'CUADRADO_GRANDE':
            tipoQRC = SquareModuleDrawer() 
            
        #Generamos el codigo Qr y lo almacenamos en el fichero de imagen PNG
        img = qr.make_image(image_factory=StyledPilImage, module_drawer=tipoQRC)
        f = open(imagenQR, "wb")
        img.save(f)
        
        return render_template("ppp.html")
    else:
        return render_template("ppp.html")


if __name__ == "__main__":
    app.secret_key = "llaveSecreta"
    app.run(debug=True,host='localhost', port='5000')