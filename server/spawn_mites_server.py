# server/spawn_mites_server.py
import threading
import random
import time

class MitesThread(threading.Thread):
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self._stop_event = threading.Event()

    def run(self):
        print("[MitesThread] Iniciando dispersión de virus...")
        while not self._stop_event.is_set():
            with self.game_state.lock:
                if self.game_state.state['game_over']:
                    break
            time.sleep(random.uniform(0.5, 1.5))

            # Elegir una zona al azar
            with self.game_state.lock:
                zona_key = random.choice(list(self.game_state.zonas.keys()))
                ancho, alto = self.game_state.zonas[zona_key]
                ox, oy = self.game_state.zona_offsets[zona_key]

            x = random.randint(ox, ox + ancho - 1)
            y = random.randint(oy, oy + alto - 1)
            virus_color = 'green' if random.random() < 0.2 else 'white'
            virus = {
                'x': x,
                'y': y,
                'active': True,
                'color': virus_color
            }

            with self.game_state.lock:
                self.game_state.shared_mites.append(virus)

            color_txt = "VERDE" if virus_color == 'green' else "BLANCO"
            print(f"[MitesThread] Nuevo virus {color_txt} en {zona_key}: ({x}, {y})")

    def stop(self):
        self._stop_event.set()
