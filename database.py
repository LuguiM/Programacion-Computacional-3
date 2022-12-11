import mysql.connector as db
import json

with open('keys.json') as json_file:
    keys = json.load(json_file)

def convertToBinaryData(filename):

   

    try:
        with open(filename, 'rb') as file:
            binaryData = file.read()
        return binaryData
    except:
        return 0


def write_file(data, path):

    with open(path, 'wb') as file:
        file.write(data)

def registerUser(usuario, cimagen):
    id = 0
    inserted = 0


    try:
        con = db.connect(host=keys["host"], user=keys["user"], password=keys["password"], database=keys["database"])
        cursor = con.cursor()
        sql = "INSERT INTO `login_facial`(usuario, cimagen) VALUES (%s,%s)"
        pic = convertToBinaryData(cimagen)
         
        if pic:
            cursor.execute(sql, (usuario, pic))
            con.commit()
            inserted = cursor.rowcount
            id = cursor.lastrowid
    except db.Error as e:
        print(f"Fallo al insertar la imagen: {e}")
    finally:
        if con.is_connected():
            cursor.close()
            con.close()
    return {"id": id, "affected":inserted}


def getlogin(usuario, path):
    id = 0
    rows = 0

    try:
        con = db.connect(host=keys["host"], user=keys["user"], password=keys["password"], database=keys["database"])
        cursor = con.cursor()
        sql = "SELECT * FROM `login_facial` WHERE usuario = %s"


        cursor.execute(sql, (usuario,))
        records = cursor.fetchall()


        for row in records:
            id = row[0]
            write_file(row[2], path)
        rows = len(records)
    except db.Error as e:
        print(f"Fallo al leer la imagen: {e}")
    finally:
        if con.is_connected():
            cursor.close()
            con.close()
    return{  "id": id, "affected": rows}
