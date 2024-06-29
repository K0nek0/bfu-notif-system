import http.server
import os


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = os.path.join('..', 'pages', 'index.html')
        elif self.path == '/admin':
            self.path = os.path.join('..', 'pages', 'admin.html')
        elif self.path.startswith('/static/'):
            self.path = os.path.join('..', self.path[1:])
        else:
            self.send_error(404, "File not found")
            return

        try:
            file_to_open = open(self.path, 'rb').read()
            self.send_response(200)
            if self.path.endswith('.html'):
                self.send_header('content_type', 'text/html')
            elif self.path.endswith('.css'):
                self.send_header('content_type', 'text/css')
            elif self.path.endswith('.js'):
                self.send_header('content_type', 'application/javascript')
            self.end_headers()
            self.wfile.write(file_to_open)
        except FileNotFoundError:
            self.send_error(404, "File not found")
