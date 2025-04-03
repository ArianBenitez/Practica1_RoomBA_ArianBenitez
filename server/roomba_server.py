# server/roomba_server.py
import threading
import time
import math
from collections import deque

# Ajustar a tus valores originales
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800
HUECO_RECT = (151, 280, 89, 260)
BARRERA = (50, 130, 550, 760)
GRID_STEP = 10

class RoombaThread(threading.Thread):
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self._stop_event = threading.Event()

        # Para ruta BFS
        self.current_path = None
        self.current_target = None
        self.path_index = 0

        # Para detectar atascos
        self.stuck_counter = 0
        with self.game_state.lock:
            self.last_position = (self.game_state.state['x'], self.game_state.state['y'])

        # Tiempos de limpieza
        self.cleaning_started = False
        self.start_time = None
        self.end_time = None

    def run(self):
        print("[RoombaThread] Iniciando hilo del robot...")
        while not self._stop_event.is_set():
            with self.game_state.lock:
                # Si game_over o vidas <= 0, salimos
                if (self.game_state.state['vidas'] <= 0 or
                    self.game_state.state['game_over']):
                    break

                mode = self.game_state.state['control_mode']

            if mode == 'auto':
                self.automatic_logic()
            else:
                # Modo manual: el movimiento lo hace move_robot_manual()
                # Sólo revisamos colisiones cada cierto tiempo
                self.check_collisions()
                time.sleep(0.1)

        print("[RoombaThread] Finalizado.")

    def stop(self):
        self._stop_event.set()

    def automatic_logic(self):
        """
        BFS para buscar el virus más cercano, avanzar hacia él, etc.
        """
        self.check_collisions()
        # Si no hay ruta o el target se desactivó, buscar nuevo
        if not self.current_path or not self.current_target or not self.current_target.get('active', True):
            target, path = self.get_reachable_mite()
            if target and path:
                self.current_target = target
                self.current_path = path
                self.path_index = 0

        # Avanzar un paso en la ruta
        if self.current_path:
            self.path_index += 1
            if self.path_index < len(self.current_path):
                nx, ny = self.current_path[self.path_index]
                with self.game_state.lock:
                    self.game_state.state['x'] = nx
                    self.game_state.state['y'] = ny
                self.check_collisions()
            else:
                self.current_path = None

        time.sleep(0.1)

    # -----------------------------
    # LÓGICA DE BÚSQUEDA DE VIRUS
    # -----------------------------
    def get_reachable_mite(self):
        with self.game_state.lock:
            mites = [m for m in self.game_state.shared_mites if m.get('active', True)]
            if not mites:
                return None, None
            # Tomar el más cercano
            rx, ry = self.game_state.state['x'], self.game_state.state['y']
            best_dist = float('inf')
            best_mite = None
            best_path = []
            for m in mites:
                dist = math.hypot(m['x'] - rx, m['y'] - ry)
                path = self.compute_path_to(m['x'], m['y'])
                if path and len(path) > 1 and dist < best_dist:
                    best_dist = dist
                    best_mite = m
                    best_path = path
        return best_mite, best_path

    def compute_path_to(self, tx, ty):
        with self.game_state.lock:
            start = (self.snap(self.game_state.state['x']), self.snap(self.game_state.state['y']))
        goal = (self.snap(tx), self.snap(ty))

        queue = deque([start])
        visited = set([start])
        parent = {}

        while queue:
            current = queue.popleft()
            if current == goal:
                return self.build_path(parent, start, goal)
            for neighbor in self.get_neighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)
        return []

    def snap(self, val):
        return int(round(val / GRID_STEP) * GRID_STEP)

    def get_neighbors(self, cx, cy):
        neighbors = []
        for dx, dy in [(GRID_STEP, 0), (-GRID_STEP, 0), (0, GRID_STEP), (0, -GRID_STEP)]:
            nx = cx + dx
            ny = cy + dy
            if self.in_barrera(nx, ny, 10) and not self.in_hueco(nx, ny, 10):
                neighbors.append((nx, ny))
        return neighbors

    def in_barrera(self, x, y, r):
        min_x, min_y, max_x, max_y = BARRERA
        return (x - r >= min_x and x + r < max_x and
                y - r >= min_y and y + r < max_y)

    def in_hueco(self, x, y, r):
        hx, hy, hw, hh = HUECO_RECT
        closest_x = max(hx, min(x, hx+hw))
        closest_y = max(hy, min(y, hy+hh))
        dist_sq = (x - closest_x)**2 + (y - closest_y)**2
        return dist_sq < (r*r)

    def build_path(self, parent, start, goal):
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = parent[current]
        path.append(start)
        path.reverse()
        return path

    # -----------------------------
    # COLISIONES
    # -----------------------------
    def check_collisions(self):
        with self.game_state.lock:
            rx, ry = self.game_state.state['x'], self.game_state.state['y']
            rradius = self.game_state.state['radius']

            # Virus
            for mite in self.game_state.shared_mites:
                if mite.get('active', True):
                    dx = mite['x'] - rx
                    dy = mite['y'] - ry
                    if (dx*dx + dy*dy) < (rradius + 3)**2:
                        mite['active'] = False
                        self.game_state.state['score'] += 10
                        # Si es verde, reduce radiación
                        if mite.get('color') == 'green':
                            self.game_state.state['radiacion'] *= 0.9

            # Enemigos
            for enemy in self.game_state.shared_enemies:
                if enemy.get('active', True):
                    dx = enemy['x'] - rx
                    dy = enemy['y'] - ry
                    if (dx*dx + dy*dy) < (rradius + 10)**2:
                        enemy['active'] = False
                        self.game_state.state['vidas'] -= 1
                        if self.game_state.state['vidas'] <= 0:
                            self.game_state.state['vidas'] = 0
                            self.game_state.state['game_over'] = True
