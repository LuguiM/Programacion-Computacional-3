import uuid
import os
#import cv2
from matplotlib import pyplot as plt
from mtcnn.mtcnn import MTCNN
import database as db

import cv2
from flask import Flask, render_template, request, Response, jsonify

app = Flask(__name__)

# Si tienes varias cámaras puedes acceder a ellas en 1, 2, etcétera (en lugar de 0)
camara = cv2.VideoCapture(0)

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

    getEnter(screen1)
    if(res_bd["affected"]):
        print("¡Éxito! Se ha registrado correctamente", 1)
    else:
        print("¡Error! No se ha registrado correctamente", 0)
    os.remove(img)
    
    
@app.route("/tomar_foto_guardar", methods=["GET", "POST"])    
def register_capture():
    cap = camara
    user_reg_img = request.form['usuario']
    img = f"{user_reg_img}.jpg"

    #while True:
        #ret, frame = cap.read()
        #cv2.imwrite(img, frame)
        #cv2.imwrite(user_reg_img, frame)
        #if cv2.waitKey(1) == 27:
            #break
    ret, frame = cap.read()
    cv2.imwrite(img, frame)
    cap.release()
    #cv2.destroyAllWindows()

    #user_entry1.delete(0, END)
    
    pixels = plt.imread(img)
    faces = MTCNN().detect_faces(pixels)
    face(img, faces)
    register_face_db(img)









# Una función generadora para stremear la cámara
# https://flask.palletsprojects.com/en/1.1.x/patterns/streaming/
def generador_frames():
    while True:
        ok, imagen = obtener_frame_camara()
        if not ok:
            break
        else:
            # Regresar la imagen en modo de respuesta HTTP
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + imagen + b"\r\n"


def obtener_frame_camara():
    ok, frame = camara.read()
    if not ok:
        return False, None
    # Codificar la imagen como JPG
    _, bufer = cv2.imencode(".jpg", frame)
    imagen = bufer.tobytes()
    return True, imagen


# Cuando visiten la ruta
@app.route("/streaming_camara")
def streaming_camara():
    return Response(generador_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Cuando toman la foto
@app.route("/tomar_foto_descargar")
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


# Cuando visiten /, servimos el index.html
@app.route('/')
def index():
    return render_template("camara.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")