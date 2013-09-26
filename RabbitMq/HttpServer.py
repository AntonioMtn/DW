import BaseHTTPServer
import time

HOST_NAME = '127.0.0.1'
PORT_NUMBER = 8000

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
     def do_HEAD(s):
         s.send_response(200)
         s.send_header("Content-type", "text/html")
         s.end_headers()
     def do_GET(s):
         """Respond to a GET request."""
         s.send_response(200)
         s.send_header("Content-type", "text/html")
         s.end_headers()
         s.wfile.write("<html><head><title>Here is a pong</title></head>")
         s.wfile.write("<body><p>PONG</p>")
         # If someone went to "http://something.somewhere.net/foo/bar/",
         # then s.path equals "/foo/bar/".
         s.wfile.write("<p>You accessed path: %s</p>" % s.path)
         s.wfile.write("</body></html>")

if __name__ == '__main__':
     server_class = BaseHTTPServer.HTTPServer
     httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
     print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
     try:
         httpd.serve_forever()
     except KeyboardInterrupt:
         pass
     httpd.server_close()
     print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)