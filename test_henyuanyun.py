#!/usr/local/miniconda3/bin/python3
from http.server import SimpleHTTPRequestHandler, HTTPServer

host = '0.0.0.0' #定义web项目的监听地址，必须写为0.0.0.0，否则无法将公网正确转发到该项目中，坚决不能写为127.0.0.1，否则无法转发到实例对应的服务中
port = 8080      #定义web项目的监听端口，必须写为8080，否则无法将公网正确转发到该项目中

class MyRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            response = f'PONG BY {host}:{port}'
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            response = 'HELLO, GPUSHARE!'
            self.wfile.write(response.encode('utf-8'))

if __name__ == '__main__':
    server_address = (host, port)
    httpd = HTTPServer(server_address, MyRequestHandler)
    print(f'Starting server on {host}:{port}')
    httpd.serve_forever()