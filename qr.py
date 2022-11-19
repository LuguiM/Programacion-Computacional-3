import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import CircleModuleDrawer, GappedSquareModuleDrawer, HorizontalBarsDrawer, RoundedModuleDrawer, SquareModuleDrawer, VerticalBarsDrawer
import argparse
import os
from urllib import parse
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler


#Preparamos el formato para el codigo QR
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
    valorQR #= input("introduzca el valor del codigo QR: ")
    
#Obtenemos el parametro -t(tipo)
if args.tipo:
    tipoQR = args.tipo
else:
    #tipoQR = input("Introuzca el tipo de qr: ")
    tipoQR = tipoQR.upper()

#Obtenemos el parametro -i(fichero de imagen QR)
if args.imagen:
    imagenQR=args.imagen
else:
    #name = input("Ingrese el nombre con el que quiera guardar la imagen: ")
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

    
def creadroqr(dato,tipo,name):
    if args.dato:
        valorQR = args.dato
    else:
        valorQR 
    
    #Obtenemos el parametro -t(tipo)
    if args.tipo:
        tipoQR = args.tipo
    else:
        tipoQR = tipoQR.upper()

    #Obtenemos el parametro -i(fichero de imagen QR)
    if args.imagen:
        imagenQR=args.imagen
    else:
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
        
    img = qr.make_image(image_factory=StyledPilImage, module_drawer=tipoQRC)
    f = open(imagenQR, "wb")
    mg.save(f)
    
#FIN DE PRUEBA NO REAL
    

class servidorBasico(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        
        crearQr = valorQR
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(data.encode())

server = HTTPServer(('localhost', 3004), servidorBasico)
server.serve_forever()