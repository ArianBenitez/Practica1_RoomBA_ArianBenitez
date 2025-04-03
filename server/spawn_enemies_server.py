# server/spawn_enemies_server.py
import threading
import random
import time

class EnemiesThread(threading.Thread):
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self._stop_event = threading.Event()

    def run(self):
        print("[EnemiesThread] Iniciando aparición de enemigos rojos...")
        while not self._stop_event.is_set():
            with self.game_state.lock:
                if self.game_state.state['game_over']:
                    break
            time.sleep(random.uniform(2.0, 4.0))

            with self.game_state.lock:
                zona_key = random.choice(list(self.game_state.zonas.keys()))
                ancho, alto = self.game_state.zonas[zona_key]
                ox, oy = self.game_state.zona_offsets[zona_key]

            x = random.randint(ox, ox + ancho - 1)
            y = random.randint(oy, oy + alto - 1)
            enemy = {
                'x': x,
                'y': y,
                'active': True,
                'color': 'red'
            }

            with self.game_state.lock:
                self.game_state.shared_enemies.append(enemy)
            print(f"[EnemiesThread] Nuevo enemigo en {zona_key}: ({x}, {y})")

    def stop(self):
        self._stop_event.set()
