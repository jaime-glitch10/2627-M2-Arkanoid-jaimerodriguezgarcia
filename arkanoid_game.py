"""Plantilla del juego Arkanoid para el hito M2.

Completa los métodos marcados con TODO respetando las anotaciones de tipo y la
estructura de la clase. El objetivo es construir un prototipo jugable usando
pygame que cargue bloques desde un fichero de nivel basado en caracteres.
"""
from arkanoid_core import *
from pathlib import Path
import sys
import pygame
# --------------------------------------------------------------------- #
# Métodos a completar por el alumnado
# --------------------------------------------------------------------- #

@arkanoid_method
def cargar_nivel(self, level_path: str = None) -> list[str]:
    """Lee el fichero de nivel y devuelve la cuadrícula como lista de filas."""
    # - Comprueba que `self.level_path` existe y es fichero.
    # - Lee su contenido, filtra líneas vacías y valida que todas tienen el mismo ancho.
    # - Guarda el resultado en `self.layout` y devuélvelo.
    path = Path(self.level_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"El archivo no existe: {self.level_path}")

    contenido = path.read_text(encoding='utf-8')
    lineas = [linea for linea in contenido.splitlines() if linea.strip() != ""]

    if not lineas:
        self.layout = []
        return []

    ancho_esperado = len(lineas[0])
    for fila in lineas:
        if len(fila) != ancho_esperado:
            raise ValueError("Las filas no tienen un ancho uniforme")

    self.layout = lineas
    return self.layout

@arkanoid_method
def preparar_entidades(self) -> None:
    """Posiciona paleta y bola, y reinicia puntuación y vidas."""
    # - Ajusta el tamaño de `self.paddle` y céntrala usando `midbottom`.
    # - Reinicia `self.score`, `self.lives` y `self.end_message`.
    # - Llama a `self.reiniciar_bola()` para colocar la bola sobre la paleta.
    self.paddle = self.crear_rect(0, 0, 100, 15)
    self.paddle.midbottom = self.screen.get_rect().midbottom

    self.score = 0
    self.lives = 3
    self.end_message = ""

    self.reiniciar_bola()

@arkanoid_method
def crear_bloques(self) -> None:
    """Genera los rectángulos de los bloques en base a la cuadrícula."""
    # - Limpia `self.blocks`, `self.block_colors` y `self.block_symbols`.
    # - Recorre `self.layout` para detectar símbolos de bloque.
    # - Usa `self.calcular_posicion_bloque` y rellena las listas paralelas.
    self.blocks = []
    self.block_colors = []
    self.block_symbols = []

    for r, fila in enumerate(self.layout):
        for c, simbolo in enumerate(fila):
            if simbolo != " ":
                rect = self.calcular_posicion_bloque(r, c)
                color = self.BLOCK_COLORS.get(simbolo, (255, 255, 255))

                self.blocks.append(rect)
                self.block_colors.append(color)
                self.block_symbols.append(simbolo)

@arkanoid_method
def procesar_input(self) -> None:
    """Gestiona la entrada de teclado para mover la paleta."""
    # - Obtén el estado de teclas con `self.obtener_estado_teclas()`.
    # - Desplaza la paleta con `self.PADDLE_SPEED` si se pulsan las teclas izquierda/derecha.
    # - Limita la posición para que no salga de la pantalla.
    keys = self.obtener_estado_teclas()

    if keys[self.KEY_LEFT] or keys[self.KEY_A]:
        self.paddle.x -= self.PADDLE_SPEED
    if keys[self.KEY_RIGHT] or keys[self.KEY_D]:
        self.paddle.x += self.PADDLE_SPEED

    if self.paddle.left < 0:
        self.paddle.left = 0
    if self.paddle.right > self.SCREEN_WIDTH:
        self.paddle.right = self.SCREEN_WIDTH

@arkanoid_method
def actualizar_bola(self) -> None:
    """Actualiza la posición de la bola y resuelve colisiones."""
    # - Suma `self.ball_velocity` a `self.ball_pos` y genera `ball_rect` con `self.obtener_rect_bola()`.
    # - Gestiona rebotes con paredes, paleta y bloques, modificando velocidad y puntuación.
    # - Controla fin de nivel cuando no queden bloques y resta vidas si la bola cae.
    if self.end_message != "":
        return
    
    self.ball_pos[0] += self.ball_velocity[0]
    self.ball_pos[1] += self.ball_velocity[1]
    ball_rect = self.obtener_rect_bola()

    if ball_rect.left <= 0 or ball_rect.right >= self.SCREEN_WIDTH:
        self.ball_velocity[0] = -self.ball_velocity[0]
    if ball_rect.top <= 0:
        self.ball_velocity[1] = -self.ball_velocity[1]

    if ball_rect.colliderect(self.paddle):
        self.ball_velocity[1] = -abs(self.ball_velocity[1])
        diferencia_centro = ball_rect.centerx - self.paddle.centerx
        mitad_pala = self.paddle.width / 2
        factor_impacto = diferencia_centro / mitad_pala
        self.ball_velocity[0] = factor_impacto * self.BALL_SPEED

    for i in range(len(self.blocks) - 1, -1, -1):
        if ball_rect.colliderect(self.blocks[i]):
            self.ball_velocity[1] = -self.ball_velocity[1]

            del self.blocks[i]
            del self.block_colors[i]
            del self.block_symbols[i]

            self.score += 10

            if len(self.blocks) == 0:
                self.end_message = "¡HAS GANADO!"

            break   

    if ball_rect.top >= self.SCREEN_HEIGHT:
        self.lives -= 1
        self.reiniciar_bola()

        if self.lives <= 0:
            self.lives = 0
            self.end_message = "GAME OVER"
        else:
            self.reiniciar_bola()

@arkanoid_method
def dibujar_escena(self) -> None:
    """Renderiza fondo, bloques, paleta, bola y HUD."""
    # - Rellena el fondo y dibuja cada bloque con `self.dibujar_rectangulo`.
    # - Pinta la paleta y la bola con las utilidades proporcionadas.
    # - Muestra puntuación, vidas y mensajes usando `self.dibujar_texto`.
    self.screen.fill((0, 0, 0))
    for rect, color in zip(self.blocks, self.block_colors):
        self.dibujar_rectangulo(rect, color)

    self.dibujar_rectangulo(self.paddle, self.PADDLE_COLOR)
    self.dibujar_circulo(self.ball_pos, self.BALL_RADIUS, self.BALL_COLOR)

    self.dibujar_texto(f"Puntos: {self.score}", (10, 10), (255, 255, 255))
    self.dibujar_texto(f"Vidas: {self.lives}", (400, 10), (255, 255, 255))

    if self.end_message != "":
        fuente = pygame.font.SysFont("Arial", 48, bold=True)
        texto = fuente.render(self.end_message, True, (255, 255, 255))
        rect_texto = texto.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))
        self.screen.blit(texto, rect_texto)

    pygame.display.flip()

@arkanoid_method
def run(self) -> None:
    """Ejecuta el bucle principal del juego."""
    # - Inicializa recursos (`self.inicializar_pygame`, `self.cargar_nivel`, etc.).
    # - Procesa eventos de `self.iterar_eventos()` y llama a los métodos de actualización/dibujo.
    # - Refresca la pantalla con `self.actualizar_pantalla()` y cierra con `self.finalizar_pygame()`.
    self.inicializar_pygame()
    self.cargar_nivel()
    self.crear_bloques()
    self.preparar_entidades()
   
    running = True

    while running:
        print("Entrando en el bucle principal...")
        for event in self.iterar_eventos():
            if event.type == self.EVENT_QUIT:
                running = False

        self.procesar_input()
        self.actualizar_bola()
        self.dibujar_escena()

        self.actualizar_pantalla()
        self.clock.tick(self.FPS)

    self.finalizar_pygame()


def main() -> None:
    """Permite ejecutar el juego desde la línea de comandos."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Plantilla del hito M2: Arkanoid con pygame.",
    )
    parser.add_argument(
        "level",
        type=str,
        help="Ruta al fichero de nivel (texto con # para bloques y . para huecos).",
    )
    args = parser.parse_args()

    game = ArkanoidGame(args.level)
    game.run()


if __name__ == "__main__":
    print("1. Creando el juego...")
    juego = ArkanoidGame("niveles/demo.txt")
    print("2. Iniciando el bucle run()...")
    juego.run()
    print("3. El juego ha terminado.")
