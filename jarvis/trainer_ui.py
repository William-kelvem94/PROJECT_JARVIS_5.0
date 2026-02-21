"""Simple HTTP interface to inspect training logs."""

import http.server
import socketserver
import threading
import webbrowser
import os
import json

PORT = 8000

class TrainerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html;charset=utf-8")
            self.end_headers()
            html = ["<html><head><title>Jarvis Training Log</title></head><body>"]
            html.append("<h1>Training Log</h1>")
            path = os.path.join(os.path.dirname(__file__), "models", "local_brain", "training_log.json")
            if os.path.exists(path):
                try:
                    with open(path, encoding="utf-8") as f:
                        logs = json.load(f)
                    html.append("<pre>" + json.dumps(logs, indent=2, ensure_ascii=False) + "</pre>")
                except Exception as e:
                    html.append(f"<p>Erro ao ler log: {e}</p>")
            else:
                html.append("<p>Log de treinamento não encontrado.</p>")
            html.append("</body></html>")
            self.wfile.write("\n".join(html).encode("utf-8"))
        else:
            super().do_GET()


def start_server(port: int = PORT):
    """Start the HTTP server in a background thread and open the browser."""
    def _run():
        with socketserver.TCPServer(("", port), TrainerHandler) as httpd:
            httpd.serve_forever()
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    url = f"http://localhost:{port}/"
    try:
        webbrowser.open(url)
    except Exception:
        pass
    return url
