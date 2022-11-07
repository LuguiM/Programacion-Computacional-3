from urllib import parse
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler

class servidorBasico(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        content_length = int(self.headers['content-Length'])
        data = self.rfile.read(content_length)
        data = data.decode()
        data = parse.unquote(data)
        print(data)
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(data.encode())
    
    print("Iniciando el servidor... en el puerto 3000")
    server = HTTPServer(('localhost', 3004), servidorBasico)
    server.server_forever()