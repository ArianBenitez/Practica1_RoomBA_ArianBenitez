# main_principal.py
import subprocess
import time

def main():
    # Definir el modo deseado: "manual" o "auto"
    control_mode = "manual"  # Puedes cambiar a "auto" si lo deseas

    print("[MAIN] Iniciando el servidor de RoomBA...")
    server_proc = subprocess.Popen(["python", "server/main_server.py", control_mode])
    
    # Esperar suficiente tiempo para que el servidor se inicie
    time.sleep(5)
    
    print("[MAIN] Iniciando el cliente de RoomBA...")
    client_proc = subprocess.Popen(["python", "client/main_client.py"])
    client_proc.wait()
    print("[MAIN] El cliente ha finalizado.")

    print("[MAIN] Terminando el servidor...")
    server_proc.terminate()
    server_proc.wait()
    print("[MAIN] El servidor ha finalizado.")

if __name__ == "__main__":
    main()