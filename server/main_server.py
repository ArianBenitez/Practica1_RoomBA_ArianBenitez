# server/main_server.py
import socket
import threading
import json
import sys
import os

# Función para verificar si un número es primo (usada para el comando CHECK_PRIME)
def isprime(n):
    """Determina si n es un número primo."""
    try:
        n = int(n)
    except:
        return False
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

from game_state import GameState
from areas_server import AreaThread
from roomba_server import RoombaThread
from spawn_mites_server import MitesThread
from spawn_enemies_server import EnemiesThread
from radiation_server import RadiationThread

HOST = 'localhost'
PORT = 5000

class GameServer:
    def __init__(self, control_mode):
        self.game_state = GameState()
        # Inicialización de variables críticas
        with self.game_state.lock:
            self.game_state.state['x'] = 200
            self.game_state.state['y'] = 180
            self.game_state.state['radius'] = 10
            self.game_state.state['vidas'] = 3
            self.game_state.state['score'] = 0
            self.game_state.state['game_over'] = False
            self.game_state.state['radiacion'] = 10
            self.game_state.state['control_mode'] = control_mode

        # Hilos de lógica
        self.area_thread = AreaThread(self.game_state)
        self.roomba_thread = RoombaThread(self.game_state)
        self.mites_thread = MitesThread(self.game_state)
        self.enemies_thread = EnemiesThread(self.game_state)
        self.radiation_thread = RadiationThread(self.game_state)

        # Socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(5)
        print(f"[Server] Escuchando en {HOST}:{PORT}")

    def start_threads(self):
        self.area_thread.start()
        self.roomba_thread.start()
        self.mites_thread.start()
        self.enemies_thread.start()
        self.radiation_thread.start()

    def stop_threads(self):
        self.area_thread.stop()
        self.roomba_thread.stop()
        self.mites_thread.stop()
        self.enemies_thread.stop()
        self.radiation_thread.stop()

        self.area_thread.join()
        self.roomba_thread.join()
        self.mites_thread.join()
        self.enemies_thread.join()
        self.radiation_thread.join()

    def handle_client(self, conn, addr):
        print(f"[Server] Cliente conectado: {addr}")
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break

                msg = json.loads(data.decode('utf-8'))
                comando = msg.get('cmd')

                if comando == 'GET_STATE':
                    state = self.game_state.get_state_dict()
                    conn.sendall(json.dumps(state).encode('utf-8'))

                elif comando == 'MOVE':
                    direction = msg.get('direction')
                    self.game_state.move_robot_manual(direction)
                    state = self.game_state.get_state_dict()
                    conn.sendall(json.dumps(state).encode('utf-8'))

                elif comando == 'SET_MODE':
                    mode = msg.get('mode')
                    with self.game_state.lock:
                        self.game_state.state['control_mode'] = mode
                    state = self.game_state.get_state_dict()
                    conn.sendall(json.dumps(state).encode('utf-8'))

                elif comando == 'CHECK_PRIME':
                    try:
                        numero = int(msg.get('numero'))
                    except (ValueError, TypeError):
                        respuesta = "Error: Entrada no es un número entero."
                        conn.sendall(respuesta.encode('utf-8'))
                        continue
                    if isprime(numero):
                        respuesta = f"El número {numero} es primo."
                    else:
                        respuesta = f"El número {numero} no es primo."
                    conn.sendall(respuesta.encode('utf-8'))

                elif comando == 'EXIT':
                    break

                else:
                    pass

        except Exception as e:
            print(f"[Server] Error con el cliente {addr}: {e}")
        finally:
            conn.close()
            print(f"[Server] Cliente desconectado: {addr}")

    def run(self):
        self.start_threads()
        try:
            while True:
                conn, addr = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.start()
        except KeyboardInterrupt:
            print("\n[Server] Cerrando servidor...")
        finally:
            self.stop_threads()
            self.server_socket.close()

if __name__ == "__main__":
    # Si se pasa un argumento, se usa ese modo; de lo contrario se hace el input interactivo.
    if len(sys.argv) > 1:
        control_mode = sys.argv[1].lower()
        if control_mode not in ['manual', 'auto']:
            control_mode = 'auto'
    else:
        mode_input = input("Seleccione modo (M)anual o (A)utomático: ").strip().lower()
        control_mode = 'manual' if mode_input == 'm' else 'auto'
    server = GameServer(control_mode)
    server.run()
