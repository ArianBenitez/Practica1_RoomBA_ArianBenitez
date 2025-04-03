# server/game_state.py
import threading

class GameState:
    def __init__(self):
        # Diccionario principal con info del robot, etc.
        self.state = {
            'x': 200,
            'y': 180,
            'radius': 10,
            'vidas': 3,          # Se inicializa con 3 vidas
            'score': 0,
            'clean_time': None,
            'control_mode': 'auto',  # 'auto' o 'manual'
            'game_over': False,
            'radiacion': 10       # Se inicializa la radiación en 10 (valor ajustable)
        }

        # Zonas y offsets (puedes ajustarlos según necesites)
        self.zonas = {
            'Zona 1': (500, 150),
            'Zona 2': (101, 480),
            'Zona 3': (309, 480),
            'Zona 4': (90, 220)
        }
        self.zona_offsets = {
            'Zona 1': (50, 130),
            'Zona 2': (50, 280),
            'Zona 3': (240, 280),
            'Zona 4': (151, 540),
        }

        # Listas compartidas de virus y enemigos
        self.shared_mites = []
        self.shared_enemies = []

        # Para cálculo de áreas
        self.areas_result = {}

        # Lock para sincronizar accesos
        self.lock = threading.Lock()

    def get_state_dict(self):
        """
        Retorna una copia 'segura' del estado para enviar al cliente.
        """
        with self.lock:
            data = dict(self.state)
            # Agrega conteo de virus y enemigos activos (opcional)
            mites_activos = sum(1 for m in self.shared_mites if m.get('active', True))
            enemies_activos = sum(1 for e in self.shared_enemies if e.get('active', True))
            data['mites_activos'] = mites_activos
            data['enemies_activos'] = enemies_activos
            return data

    def move_robot_manual(self, direction):
        """
        Mueve el robot en modo manual según la dirección recibida.
        """
        step = 5
        with self.lock:
            if direction == 'UP':
                self.state['y'] -= step
            elif direction == 'DOWN':
                self.state['y'] += step
            elif direction == 'LEFT':
                self.state['x'] -= step
            elif direction == 'RIGHT':
                self.state['x'] += step
