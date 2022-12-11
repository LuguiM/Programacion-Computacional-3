import os
import cv2
from matplotlib import pyplot as plt
from mtcnn.mtcnn import MTCNN
import database as db

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
    res_bd = db.registerUser(name_user, path + img)

    getEnter(screen1)
    if(res_bd["affected"]):
        print("¡Éxito! Se ha registrado correctamente", 1)
    else:
        print("¡Error! No se ha registrado correctamente", 0)
    os.remove(img)
    
def register_capture():
    cap = camara
    user_reg_img = request.form["usuario"]
    img = f"{user_reg_img}.jpg"

    while True:
        ret, frame = cap.read()
        cv2.imshow("Registro Facial", frame)
        if cv2.waitKey(1) == 27:
            break
    
    cv2.imwrite(img, frame)
    cap.release()
    #cv2.destroyAllWindows()

    user_entry1.delete(0, END)
    
    pixels = plt.imread(img)
    faces = MTCNN().detect_faces(pixels)
    face(img, faces)
    register_face_db(img)
    
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

def login_capture():
    cap = camara
    user_login = user2.get()
    img = f"{user_login}_login.jpg"
    img_user = f"{user_login}.jpg"

    while True:
        ret, frame = cap.read()
        cv2.imshow("Login Facial", frame)
        if cv2.waitKey(1) == 27:
            break
    
    cv2.imwrite(img, frame)
    cap.release()
    #cv2.destroyAllWindows()

    user_entry2.delete(0, END)
    
    pixels = plt.imread(img)
    faces = MTCNN().detect_faces(pixels)

    face(img, faces)
    #getEnter(screen2)

    res_db = db.getUser(user_login, path + img_user)
    if(res_db["affected"]):
        my_files = os.listdir()
        if img_user in my_files:
            face_reg = cv2.imread(img_user, 0)
            face_log = cv2.imread(img, 0)

            comp = compatibility(face_reg, face_log)
            
            if comp >= 0.94:
                print("{}Compatibilidad del {:.1%}{}".format(color_success, float(comp), color_normal))
                print(f"Bienvenido, {user_login}", 1)
            else:
                print("{}Compatibilidad del {:.1%}{}".format(color_error, float(comp), color_normal))
                print("¡Error! Incopatibilidad de datos", 0)
            os.remove(img_user)
    
        else:
            print("¡Error! Usuario no encontrado", 0)
    else:
        print("¡Error! Usuario no encontrado", 0)
    os.remove(img)
