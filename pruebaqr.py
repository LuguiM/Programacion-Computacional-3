from flask import Flask,render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL, MySQLdb

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import CircleModuleDrawer, GappedSquareModuleDrawer, HorizontalBarsDrawer, RoundedModuleDrawer, SquareModuleDrawer, VerticalBarsDrawer
import argparse
import os





#SERvidor
app = Flask("my_first_website")

#CONEXION BASE DE DATOS
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'qr_world'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route("/", methods=["GET", "POST"])
def show_signup_form():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    
    notificacion = Notify()
    
    if request.method == 'POST':
        usuario = request.form['usuario']
        pasword = request.form['passwordd']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM login_tradicional WHERE usuario=%s", (usuario))
        user = cur.fetchone()
        cur.close()
        
        if len(user)>0:
            if password == user["password"]:
                session['name'] = user['name']
                session['password'] = user['password']
                
            else:
                notificacion.title = "error de Acceso"
                notificacion.message = "Usuario o Contraseña no Valida"
                notificacion.send()
                return render_template("login.html")
        else:
            notificacion.title = "error de Acceso"
            notificacion.message = "Usuario o Contraseña no Valida"
            notificacion.send()
            return render_template("login.html")
    else:
        return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM registro")
    tipo = cur.fetchall()
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM login_tradicional")
    tipo = cur.fetchall()
    
    cur.close()
    
    notificacion = Notify()
    
    if request.method == 'GET':
        return render_template("registro.html")
    else:
        name = request.form['name']
        apellido = request.form['apellido']
        email = request.form['email']
        usuario = request.form['usuario']
        password = request.form['password']
        password2 = request.form['password2']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO registro(nombre, apellido, correo) VALUES(%s,%s,%s,%s)", (name, apellido, email))
        cur.execute("INSERT INTO login_tradicional(usuario, contrasena, password2 VALUES(%s,%s,%s)", (usuario, password, password2))
        mysql.connection.commit()
        notificacion.title = "Registro Exitoso"
        notificacion.message = "Ya te encuentras registrado en QR_WORLD, for favor inicia sesion y empieza a crear."
        notificacion.send()
        return redirect(url_for('login'))
    
    

@app.route("/generador", methods=["GET", "POST"])
def generador():
    return render_template("generador.html")

@app.route("/creacionQR", methods=['GET','POST'])
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
            name = request.form['txtname']
            imagenQR = os.path.dirname(os.path.abspath(__file__)) + '\\' + name + '.png' #"C:\Program Files\Downloand" os.path.abspath(__file__)

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
        
        return render_template("prueba.html")
    else:
        return render_template("prueba.html")


if __name__ == "__main__":
    app.secret_key = "llaveSecreta"
    app.run(debug=True,host='localhost', port='5000')