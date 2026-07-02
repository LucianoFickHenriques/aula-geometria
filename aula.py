import http.server, webbrowser, os, threading

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DIR, **kw)
    def log_message(self, *a): pass

def open_browser():
    webbrowser.open(f"http://localhost:{PORT}")

threading.Timer(0.5, open_browser).start()
print(f"Servidor rodando em http://localhost:{PORT}")
print("Pressione Ctrl+C para encerrar.")

with http.server.HTTPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
