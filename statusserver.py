import http.server
import socketserver
import threading
import logging

class HttpStatusServer():
    """A simple HTTP server that open port for HAProxy health check."""

    def __init__(self, port=1992):
        self.port = port
        self.httpd = socketserver.TCPServer(("", port), MyHandler)

    def start(self):
        t = threading.Thread(target=self.httpd.serve_forever)
        logging.info('Start status server at port %s', self.port)
        t.start()

    def stop(self):
        logging.info('Stopping status server...')
        self.httpd.shutdown()

    def set_ready(self, is_ready):
        MyHandler.is_ready = is_ready
        logging.info('Status server change to %s', 
                     'ready' if is_ready else 'not ready')

class MyHandler(http.server.BaseHTTPRequestHandler):
    
    is_ready = False

    def __init__(self, *args, **kwargs):
        super(MyHandler, self).__init__(*args, **kwargs)

    def do_GET(self):
        if self.is_ready:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            output = "I'm ready"
            self.wfile.write(output.encode())
        else:
            self.send_error(404, "File not found")

if __name__ == '__main__':
    server = HttpStatusServer()
    server.start()
