import os
import sys
from pathlib import Path
import threading
import logging

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from flask import Flask, render_template, send_from_directory

# Configurar Flask - buscar templates en la carpeta raíz
template_dir = root_dir / "templates"
app = Flask(__name__, template_folder=str(template_dir))

# Desactivar logs innecesarios de Flask para no ensuciar la consola
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/favicon.svg")
def favicon():
    return send_from_directory(os.path.join(root_dir, "templates"), "favicon.svg", mimetype="image/svg+xml")


def run_server(port=7860):
    """Función para correr el servidor en un puerto específico."""
    print("\n")
    print(f"🌐 Servidor Web disponible en: http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


def start_web_background(port=7860):
    """Inicia el servidor Flask en un hilo separado."""
    thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    # Ejecutar directamente si se llama python web/server.py
    run_server(port=7860)
