from db import obtener_conexion
class crud:
   
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
    
    
    def insertar_qr(nombre,contenido,tipo,img):
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("INSERT INTO historial(nombre,contenido,tipo,img) VALUES (%s, %s, %s, %s)", (nombre,contenido,tipo,img))
            pic = convertToBinaryData(img)
            
            if pic:
                conexion.commit()
                inserted = cursor.rowcount
                id = cursor.lastrowid
            else:
                print("Fallo al insertar la imagen")
        conexion.close()
    
    def obtener_qr():
        conexion = obtener_conexion()
        qr = []
        with conexion.cursor() as cursor:
            cursor.execute("SELECT nombre,contenido,tipo,img FROM historial")
            qr = cursor.fetchall()
        conexion.close()
        return qr

    def eliminar_qr(id):
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM historial WHERE id_historial= %s",(id,))
        conexion.commit()
        conexion.close()
    
    def obtener_qr_por_id(id):
        conexion = obtener_conexion()
        qr = None
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM historial WHERE id_historial =%s",(id,))
            qr = cursor.fetchone()
        conexion.close()
        return qr

    def actualizar_qr(nombre, id):
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("UPDATE historial SET nombre=%s, WHERE id_historial=%s",(nombre,id))
        conexion.commit()
        conexion.close()