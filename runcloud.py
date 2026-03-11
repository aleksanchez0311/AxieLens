import os
import subprocess
import sys
import time
from threading import Thread
from interfaces.server import run_server
from core.utils import load_env

def start_bot():
    """Lanza el bot de Telegram como un subproceso"""
    print("🚀 Iniciando Bot de Telegram...")
    # Usamos subprocess para que el bot corra en paralelo
    return subprocess.Popen([sys.executable, "interfaces/bot.py"])

if __name__ == "__main__":
    load_env()
    
    # 1. Iniciar el servidor web en un hilo (Thread)
    # HF requiere el puerto 7860
    print("🌐 Iniciando servidor de monitoreo en puerto 7860...")
    daemon_server = Thread(target=run_server, kwargs={'port': 7860}, daemon=True)
    daemon_server.start()

    # 2. Iniciar el Bot
    bot_process = start_bot()

    # 3. Mantener el proceso principal vivo y monitorear el bot
    try:
        while True:
            # Si el bot muere por algún error, lo reiniciamos
            if bot_process.poll() is not None:
                print("⚠️ El bot se detuvo. Reiniciando...")
                bot_process = start_bot()
            time.sleep(10)
    except KeyboardInterrupt:
        bot_process.terminate()
        print("👋 Aplicación cerrada.")