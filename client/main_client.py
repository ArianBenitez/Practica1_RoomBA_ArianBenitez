# client/main_client.py
import pygame
import sys
import time
import threading
from net_client import NetClient

def network_listener(client, state_container, stop_event):
    while not stop_event.is_set():
        try:
            new_state = client.send_cmd({'cmd': 'GET_STATE'})
            if new_state is None:
                continue
            with state_container['lock']:
                state_container['state'] = new_state
        except Exception as e:
            print("Error in network listener:", e)
        time.sleep(0.05)

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 800))
    pygame.display.set_caption("RoomBA - Cliente")
    clock = pygame.time.Clock()

    net_client = NetClient()
    net_client.connect()
    if not net_client.sock:
        print("No se pudo conectar al servidor. Saliendo.")
        pygame.quit()
        sys.exit()

    # Contenedor compartido para el estado recibido
    state_container = {'state': {}, 'lock': threading.Lock()}
    stop_event = threading.Event()
    net_thread = threading.Thread(target=network_listener, args=(net_client, state_container, stop_event))
    net_thread.start()

    font = pygame.font.SysFont(None, 24)
    prime_font = pygame.font.SysFont(None, 30)
    
    # Variable para almacenar el resultado de la verificación de primos
    prime_result = ""

    running = True
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    net_client.send_cmd({'cmd': 'MOVE', 'direction': 'UP'})
                elif event.key == pygame.K_DOWN:
                    net_client.send_cmd({'cmd': 'MOVE', 'direction': 'DOWN'})
                elif event.key == pygame.K_LEFT:
                    net_client.send_cmd({'cmd': 'MOVE', 'direction': 'LEFT'})
                elif event.key == pygame.K_RIGHT:
                    net_client.send_cmd({'cmd': 'MOVE', 'direction': 'RIGHT'})
                elif event.key == pygame.K_p:
                    # Bloquea el ciclo principal para solicitar el número (esto es temporal)
                    numero = input("Ingrese número para verificar si es primo: ").strip()
                    response = net_client.send_cmd({'cmd': 'CHECK_PRIME', 'numero': numero})
                    # Almacenar el resultado en la variable para mostrarlo en pantalla
                    prime_result = response if isinstance(response, str) else str(response)
                    print("Resultado de verificación:", prime_result)

        with state_container['lock']:
            state = state_container.get('state', {})

        screen.fill((211, 211, 211))
        # Extraer datos del estado
        x = state.get('x', 200)
        y = state.get('y', 180)
        vidas = state.get('vidas', 0)
        rad = state.get('radiacion', 0)
        score = state.get('score', 0)
        zonas = state.get('zonas', {})
        zona_offsets = state.get('zona_offsets', {})

        # Dibujar zonas
        for zona, size in zonas.items():
            offset = zona_offsets.get(zona, (0, 0))
            pygame.draw.rect(screen, (100, 100, 200), (offset[0], offset[1], size[0], size[1]), 2)

        # Dibujar el robot
        pygame.draw.rect(screen, (0, 255, 0), (x, y, 20, 20))

        # Dibujar HUD
        txt_vidas = font.render(f"Vidas: {vidas}", True, (0, 0, 0))
        txt_rad = font.render(f"Radiación: {rad:.1f}", True, (255, 0, 0))
        txt_score = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(txt_vidas, (10, 10))
        screen.blit(txt_rad, (10, 30))
        screen.blit(txt_score, (10, 50))
        
        # Dibujar el resultado de la verificación de número primo
        if prime_result:
            prime_text = prime_font.render(f"Primo: {prime_result}", True, (0, 0, 255))
            screen.blit(prime_text, (10, 80))

        if state.get('game_over', False):
            go_text = font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(go_text, (250, 400))

        pygame.display.flip()

    stop_event.set()
    net_thread.join()
    net_client.send_cmd({'cmd': 'EXIT'})
    net_client.close()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
