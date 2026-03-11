from core.utils import load_env

# Solo cargar entorno, el resto se maneja en subprocesos
load_env()


if __name__ == "__main__":
    import time
    import subprocess
    import sys

    print("=" * 50)
    print("🚀 AXIE CLASIFIER - ORQUESTADOR PRINCIPAL")
    print("=" * 50)

    # 1. Iniciar servidor web en segundo plano
    print("\n[1/3] Iniciando servidor web...")
    from interfaces.server import start_web_background

    web_thread = start_web_background(port=5000)
    print("    ✓ Servidor web iniciado en puerto 5000")

    # 2. Lanzar Bot de Telegram en segundo plano
    print("\n[2/3] Iniciando Bot de Telegram...")
    bot_process = subprocess.Popen([sys.executable, "interfaces/bot.py"])
    # El bot mostrará "🚀 Bot de Telegram iniciado..." cuando llegue a run_polling()

    # 3. Lanzar Menú de consola
    print("\n[3/3] Iniciando Menú de consola...")
    menu_process = subprocess.Popen([sys.executable, "interfaces/menu.py"])

    # 4. Mantener el orquestador vivo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\\nCerrando procesos...")
        # if web_thread:
        #     web_thread.shutdown(wait=False) # web_thread no tiene shutdown. Se cerrará con el proceso principal
        if bot_process:
            bot_process.terminate()
        if menu_process:
            menu_process.terminate()
        print("    ✓ Todos los procesos terminados.")

    # Esperar a que cualquiera de los procesos termine
    try:
        # Monitorear los procesos
        while True:
            time.sleep(1)

            # Verificar si el menú terminó (usuario salió)
            if menu_process.poll() is not None:
                print("\n[!] El menú de consola se ha cerrado. Cerrando aplicación...")
                break

            # Verificar si el bot murió
            if bot_process.poll() is not None:
                print("\n[!] El bot de Telegram se ha cerrado. Cerrando aplicación...")
                break

    except KeyboardInterrupt:
        print("\n\n[!] Deteniendo todos los servicios...")

    # Limpieza: terminar procesos hijos
    print("    → Cerrando Bot de Telegram...")
    bot_process.terminate()

    print("    → Cerrando Menú de consola...")
    menu_process.terminate()

    print("\n👋 Aplicación cerrada correctamente.")
