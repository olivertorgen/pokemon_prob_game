import pygame
import random
import sys

# --- 1. CONFIGURACIÓN INICIAL DE PYGAME ---
# Inicializar Pygame
pygame.init()

# Definir colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL_CLARO = (173, 216, 230)
ROJO_APUESTA = (255, 100, 100)
VERDE_APUESTA = (100, 255, 100)

# Configuración de la pantalla
ANCHO = 800
ALTO = 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Pokémon Probability Dice Game")

# Fuente
fuente_titulo = pygame.font.Font(None, 48)
fuente_cuerpo = pygame.font.Font(None, 30)

# --- 2. CONFIGURACIÓN DEL JUEGO DE PROBABILIDAD ---
# Los 'dados' son un conjunto de 6 caras, con 3 Pokémon repitiéndose 2 veces
CARAS_DADO = ["Pikachu", "Jigglypuff", "Squirtle", "Pikachu", "Jigglypuff", "Squirtle"]

# Inicializar contadores y probabilidades
# ¡ATENCIÓN!: Se ha cambiado Charmander por Jigglypuff
contadores = {"Pikachu": 0, "Jigglypuff": 0, "Squirtle": 0}
total_lanzamientos = 0

# Probabilidad a Priori (Teórica): 2 de 6 caras para cada Pokémon
probabilidad_a_priori = 2 / 6  # ~0.333 o 33.3%

# Apuesta Subjetiva del Jugador (Inicialmente, apuesta a Pikachu)
apuesta_jugador = "Pikachu"
ganadas_subjetiva = 0
apuestas_totales = 0

# --- 3. CARGA DE IMÁGENES (ASSETS) ---
def cargar_imagen(nombre):
    """Carga y escala una imagen. Si falla, retorna un cuadrado de color."""
    try:
        # La imagen se escala a 100x100 para uniformidad
        imagen = pygame.image.load(nombre).convert_alpha()
        return pygame.transform.scale(imagen, (100, 100))
    except pygame.error as e:
        print(f"Error al cargar la imagen {nombre}: {e}")
        # Retorna una superficie roja si falla la carga
        return pygame.Surface((100, 100))

# ¡ATENCIÓN!: Se ha cambiado "charmander.png" por "jigglypuff.png"
imagenes_pokemon = {
    "Pikachu": cargar_imagen("pikachu.png"),
    "Jigglypuff": cargar_imagen("jigglypuff.png"),
    "Squirtle": cargar_imagen("squirtle.png"),
}

resultado_actual = "Pikachu" # Resultado inicial visible


# --- 4. FUNCIONES DEL JUEGO ---

def lanzar_dado():
    """Simula el lanzamiento y actualiza los contadores de probabilidad a posteriori."""
    global total_lanzamientos, resultado_actual, apuesta_jugador, ganadas_subjetiva, apuestas_totales
    
    # 1. Lanzar el "Dado" (Seleccionar una cara al azar)
    resultado = random.choice(CARAS_DADO)
    
    # 2. Actualizar contadores
    total_lanzamientos += 1
    contadores[resultado] += 1
    resultado_actual = resultado
    
    # 3. Evaluar Apuesta Subjetiva
    apuestas_totales += 1 # Contamos esta ronda como una apuesta
    if resultado == apuesta_jugador:
        ganadas_subjetiva += 1

def cambiar_apuesta():
    """Permite al jugador cambiar su apuesta subjetiva."""
    global apuesta_jugador
    
    opciones = list(contadores.keys())
    
    # Encuentra el índice actual y cambia al siguiente en la lista
    indice_actual = opciones.index(apuesta_jugador)
    nuevo_indice = (indice_actual + 1) % len(opciones)
    apuesta_jugador = opciones[nuevo_indice]
    
    # Reinicia la cuenta subjetiva si el jugador es estratégico y quiere comenzar de nuevo
    # (Opcional, pero hace la Probabilidad Subjetiva más dinámica)
    # global ganadas_subjetiva, apuestas_totales
    # ganadas_subjetiva = 0
    # apuestas_totales = 0


# --- 5. FUNCIONES DE DIBUJO ---

def dibujar_texto(superficie, texto, fuente, color, x, y, centrar_x=False):
    """Función auxiliar para dibujar texto."""
    texto_superficie = fuente.render(texto, True, color)
    rect = texto_superficie.get_rect()
    if centrar_x:
        rect.centerx = x
    else:
        rect.topleft = (x, y)
    superficie.blit(texto_superficie, rect)

def dibujar_probabilidades():
    """Dibuja los resultados, contadores y probabilidades."""
    
    # --- Columna Izquierda: Resultado y Apuesta ---
    
    # Título y Resultado Actual
    dibujar_texto(pantalla, "¡LANZAMIENTO!", fuente_titulo, NEGRO, 200, 50, centrar_x=True)
    pantalla.blit(imagenes_pokemon[resultado_actual], (150, 100))
    dibujar_texto(pantalla, f"Resultado: {resultado_actual}", fuente_cuerpo, NEGRO, 200, 210, centrar_x=True)

    # Bloque de Apuesta Subjetiva
    color_apuesta = VERDE_APUESTA if resultado_actual == apuesta_jugador and total_lanzamientos > 0 else ROJO_APUESTA
    pygame.draw.rect(pantalla, color_apuesta, (50, 250, 300, 150), border_radius=10)
    dibujar_texto(pantalla, "Apuesta Subjetiva", fuente_cuerpo, NEGRO, 200, 260, centrar_x=True)
    dibujar_texto(pantalla, f"Tu Apuesta: {apuesta_jugador}", fuente_cuerpo, NEGRO, 200, 300, centrar_x=True)
    
    prob_subjetiva = (ganadas_subjetiva / apuestas_totales) * 100 if apuestas_totales > 0 else 0
    dibujar_texto(pantalla, f"Efectividad: {prob_subjetiva:.1f}% ({ganadas_subjetiva}/{apuestas_totales})", fuente_cuerpo, NEGRO, 200, 340, centrar_x=True)

    dibujar_texto(pantalla, "Presiona ESPACIO para lanzar.", fuente_cuerpo, NEGRO, 200, 480, centrar_x=True)
    dibujar_texto(pantalla, "Presiona 'C' para cambiar tu apuesta.", fuente_cuerpo, NEGRO, 200, 520, centrar_x=True)


    # --- Columna Derecha: Estadísticas de Probabilidad ---
    
    x_stats = 400
    y_start = 50
    y_offset = 120
    
    dibujar_texto(pantalla, f"Lanzamientos Totales: {total_lanzamientos}", fuente_titulo, NEGRO, x_stats + 50, y_start)
    
    # Cabeceras de la tabla
    dibujar_texto(pantalla, "POKÉMON", fuente_cuerpo, NEGRO, x_stats + 20, y_start + 50)
    dibujar_texto(pantalla, "CONTEO", fuente_cuerpo, NEGRO, x_stats + 150, y_start + 50)
    dibujar_texto(pantalla, "P(A priori)", fuente_cuerpo, NEGRO, x_stats + 250, y_start + 50)
    dibujar_texto(pantalla, "P(a posteriori)", fuente_cuerpo, NEGRO, x_stats + 380, y_start + 50)
    
    # Datos de la tabla
    y_pos = y_start + 80
    
    for i, (pokemon, conteo) in enumerate(contadores.items()):
        # Probabilidad a Posteriori (Frecuencia Relativa)
        prob_a_posteriori = (conteo / total_lanzamientos) if total_lanzamientos > 0 else 0
        
        # Color de fondo alternado
        if i % 2 == 0:
            pygame.draw.rect(pantalla, AZUL_CLARO, (x_stats, y_pos, ANCHO - x_stats, 30))
            
        # Dibujar datos de fila
        dibujar_texto(pantalla, pokemon, fuente_cuerpo, NEGRO, x_stats + 20, y_pos)
        dibujar_texto(pantalla, str(conteo), fuente_cuerpo, NEGRO, x_stats + 150, y_pos)
        dibujar_texto(pantalla, f"{probabilidad_a_priori * 100:.1f}%", fuente_cuerpo, NEGRO, x_stats + 250, y_pos)
        dibujar_texto(pantalla, f"{prob_a_posteriori * 100:.1f}%", fuente_cuerpo, NEGRO, x_stats + 380, y_pos)
        
        y_pos += 40

    # Línea divisoria
    pygame.draw.line(pantalla, NEGRO, (ANCHO // 2, 0), (ANCHO // 2, ALTO), 2)
    

# --- 6. BUCLE PRINCIPAL DEL JUEGO ---

ejecutando = True
while ejecutando:
    # --- Manejo de Eventos ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                # Evento principal: lanzar el dado
                lanzar_dado()
            
            if evento.key == pygame.K_c:
                # Evento para la apuesta subjetiva
                cambiar_apuesta()
            
            if evento.key == pygame.K_ESCAPE:
                ejecutando = False


    # --- Dibujar en Pantalla ---
    pantalla.fill(BLANCO)
    dibujar_probabilidades()
    
    # Actualizar la pantalla
    pygame.display.flip()

# --- Salir de Pygame ---
pygame.quit()
sys.exit()