from flask import Flask,render_template, request, redirect, url_for, flash,session,Response,jsonify
from flask_mysqldb import MySQL, MySQLdb
import re
import controlador
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import CircleModuleDrawer, GappedSquareModuleDrawer, HorizontalBarsDrawer, RoundedModuleDrawer, SquareModuleDrawer, VerticalBarsDrawer
import argparse
import os
from os import path #pip install notify-py
from notifypy import Notify
import sys
import uuid
import os
import cv2
from matplotlib import pyplot as plt
from mtcnn.mtcnn import MTCNN
import database as db

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
    return render_template("home.html")

@app.route("/QrWorld/loginFacial")
def loginfacial():
    return render_template("login_facial.html")

@app.route("/QrWorld/RegistroFacial")
def Registrofacial():
    return render_template("Registro_Facial.html")

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
        usuario = request.form.get['usuario']
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

@app.route("/QrWorld/historial")
def historial():
    qr = controlador.obtener_qr()
    return render_template("historial_prueba.html", qr=qr)

@app.route("/eliminar_qr", methods=["POST"])
def eliminar_qr():
    controlador.eliminar_qr(request.form["id"])
    return redirect("/QrWorld/historial")

@app.route("/QrWorld/creacionQR", methods=['GET','POST'])
def creacionQR():
    msg = ''
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
        
        
       
        controlador.insertar_qr(name, valorQR, tipoQR, img)
       
            
        
        
        #cur = mysql.connection.cursor()
        #cur.execute("INSERT INTO historial(nombre,contenido,tipo,img) VALUES (%s,%s,%s,%s)", (name,valorQR,tipoQR,imagenQR))
        #cur.connection.commit()
        msg = "se han podido insertar los datos"
        #flash('Qr agregado')
        return render_template("creacionQR.html",msg=msg)
    else:
        return render_template("creacionQR.html",msg=msg)
        
#LOGIN Y REGISTRO FACIAL


camara = cv2.VideoCapture(0)

res_bd = {"id": 0, "affected": 0}

color_success = "\033[1;32;40m"
color_error = "\033[1;31;40m"
color_normal = "\033[0;37;40m"

def face(img, faces):
    data = plt.imread(img)
    for i in range(len(faces)):
        x1, y1, ancho, alto = faces[i]["box"]
        x2, y2 = x1 + ancho, y1 + alto
        plt.subplot(1,len(faces), i + 1)
        plt.axis("off")
        face = cv2.resize(data[y1:y2, x1:x2],(150,200), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(img, face)
        plt.imshow(data[y1:y2, x1:x2])
        
# REGISTER #
def register_face_db(img):
    name_user = img.replace(".jpg","").replace(".png","")
    res_bd = db.registerUser(name_user, img)

    #getEnter(screen1)#
    if(res_bd["affected"]== True):
        print("¡Éxito! Se ha registrado correctamente", 1)#
        return render_template("Registro_Facial.html")
    else:
        print("¡Error! No se ha registrado correctamente", 0)#
        return render_template("Registro_facial.html")
    os.remove(img)
    
    
@app.route("/tomar_foto_guardar", methods=["GET", "POST"])    
def register_capture():
    cap = camara
    user_reg_img = request.form['usuario']
    img = f"{user_reg_img}.jpg"

    ret, frame = cap.read()
    cv2.imwrite(img, frame)
    cap.release()
    
    pixels = plt.imread(img)
    faces = MTCNN().detect_faces(pixels)
    face(img, faces)
    if register_face_db(img) == True:
        return render_template("home.html")
    else:
        return render_template("Registro_Facial.html")
    

# LOGIN #
def compatibility(img1, img2):
    orb = cv2.ORB_create()

    kpa, dac1 = orb.detectAndCompute(img1, None)
    kpa, dac2 = orb.detectAndCompute(img2, None)

    comp = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    matches = comp.match(dac1, dac2)

    similar = [x for x in matches if x.distance < 70]
    if len(matches) == 0:
        return 0
    return len(similar)/len(matches)

@app.route("/tomar_foto_login",methods=["GET", "POST"])
def login_capture():
    msg = ''
    cap = camara
    user_login = request.form['login']
    img = f"{user_login}_login.jpg"
    img_user = f"{user_login}.jpg"

    ret, frame = cap.read()
    cv2.imwrite(img, frame)
    cap.release()
    
    pixels = plt.imread(img)
    faces = MTCNN().detect_faces(pixels)

    
    face(img, faces) 


    res_db = db.getlogin(user_login, img_user)
    if(res_db["affected"]):
        my_files = os.listdir()
        if img_user in my_files:
            face_reg = cv2.imread(img_user, 0)
            face_log = cv2.imread(img, 0)

            comp = compatibility(face_reg, face_log)
            
            if comp >= 0.94:
                print("{}Compatibilidad del {:.1%}{}".format(color_success, float(comp), color_normal))
                print(f"Bienvenido, {user_login}", 1)
                return render_template("home.html")
            else:
                print("{}Compatibilidad del {:.1%}{}".format(color_error, float(comp), color_normal))
                print("¡Error! Incopatibilidad de datos", 0)
                return render_template("login_facial.html")
            os.remove(img_user)
    
        else:
            print("¡Error! Usuario no encontrado", 0)
    else:
        print("¡Error! Usuario no encontrado", 0)
    os.remove(img)


def generador_frames():
    while True:
        ok, imagen = obtener_frame_camara()
        if not ok:
            break
        else:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + imagen + b"\r\n"


def obtener_frame_camara():
    ok, frame = camara.read()
    if not ok:
        return False, None
    _, bufer = cv2.imencode(".jpg", frame)
    imagen = bufer.tobytes()
    return True, imagen


# Cuando visiten la ruta
@app.route("/streaming_camara")
def streaming_camara():
    return Response(generador_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Cuando toman la foto
#@app.route("/tomar_foto_descargar")
def descargar_foto():
    ok, frame = obtener_frame_camara()
    if not ok:
        abort(500)
        return
    respuesta = Response(frame)
    respuesta.headers["Content-Type"] = "image/jpeg"
    respuesta.headers["Content-Transfer-Encoding"] = "Binary"
    respuesta.headers["Content-Disposition"] = "attachment; filename=\"foto.jpg\""
    return respuesta


#@app.route("/tomar_foto_guardar")
def guardar_foto():
    nombre_foto = str(uuid.uuid4()) + ".jpg"
    ok, frame = camara.read()
    if ok:
        cv2.imwrite(nombre_foto, frame)
    return jsonify({
        "ok": ok,
        "nombre_foto": nombre_foto,
    })


if __name__ == "__main__":
    app.secret_key = "llaveSecreta"
    app.run(debug=True,host='localhost', port='5000')