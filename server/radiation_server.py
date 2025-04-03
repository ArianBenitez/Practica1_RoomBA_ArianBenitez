# server/radiation_server.py
import threading
import time

class RadiationThread(threading.Thread):
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self._stop_event = threading.Event()
        self.MAX_RADIATION = 100

    def run(self):
        print("[RadiationThread] Subida de radiación (1 punto cada 3s).")
        while not self._stop_event.is_set():
            with self.game_state.lock:
                if self.game_state.state['game_over']:
                    break
            time.sleep(3)

            with self.game_state.lock:
                rad = self.game_state.state['radiacion']
                rad += 1
                if rad >= self.MAX_RADIATION:
                    rad = self.MAX_RADIATION
                    self.game_state.state['game_over'] = True
                    print("[RadiationThread] ¡Radiación crítica! Game Over.")
                self.game_state.state['radiacion'] = rad

    def stop(self):
        self._stop_event.set()
