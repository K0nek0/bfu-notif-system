import socketserver
from request_handler import RequestHandler
from database import Database

PORT = 8000
Handler = RequestHandler
db = Database()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
