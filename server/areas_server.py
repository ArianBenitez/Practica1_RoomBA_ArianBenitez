# server/areas_server.py
import threading
import time

CLEANING_RATE = 200.0  # cm²/segundo

class AreaThread(threading.Thread):
    def __init__(self, game_state):
        """
        game_state: referencia a la clase GameState
        """
        super().__init__()
        self.game_state = game_state
        self._stop_event = threading.Event()

    def run(self):
        print("[AreaThread] Iniciando cálculo de superficie...")
        self.calcular_areas()
        self.estimar_tiempo_limpieza()

        # Bucle de espera
        while not self._stop_event.is_set():
            with self.game_state.lock:
                if self.game_state.state['game_over']:
                    break
            time.sleep(2)

    def calcular_areas(self):
        total = 0
        with self.game_state.lock:
            for _, (ancho, alto) in self.game_state.zonas.items():
                total += ancho * alto
            self.game_state.areas_result['superficie_total'] = total
        print(f"[AreaThread] Superficie total: {total} cm²")

    def estimar_tiempo_limpieza(self):
        with self.game_state.lock:
            total_area = self.game_state.areas_result.get('superficie_total', 0)
            if total_area > 0:
                time_seconds = total_area / CLEANING_RATE
                time_minutes = time_seconds / 60.0
                self.game_state.areas_result['tiempo_est_s'] = time_seconds
                self.game_state.areas_result['tiempo_est_m'] = time_minutes
                print(f"[AreaThread] Tiempo teórico de desinfección: {time_seconds:.2f}s")
            else:
                self.game_state.areas_result['tiempo_est_s'] = 0
                self.game_state.areas_result['tiempo_est_m'] = 0
                print("[AreaThread] No hay zonas contaminadas.")

    def stop(self):
        self._stop_event.set()
