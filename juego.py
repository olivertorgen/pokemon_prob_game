import pygame
import random
import sys
import time 

# --- 1. CONFIGURACIÓN INICIAL Y COLORES ---
pygame.init()
pygame.mixer.init() 

# Definir estados del juego
STATE_MENU = 0
STATE_GAME = 1
estado_actual = STATE_MENU

# Definir colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS_OSCURO = (50, 50, 50)
AZUL_FONDO = (30, 60, 150)
AZUL_BOTON = (30, 50, 160)
VERDE_APUESTA = (100, 200, 100)
ROJO_APUESTA = (200, 100, 100)
AMARILLO_POKEMON = (255, 203, 5)
ROJO_ERROR = (255, 0, 0)

# Configuración de la pantalla (1200x720 para el diseño wide)
ANCHO = 1200
ALTO = 720
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Pokémon Probability Dice Game")

# Fuente
fuente_titulo = pygame.font.Font(None, 80)
fuente_seccion = pygame.font.Font(None, 45)
fuente_cuerpo = pygame.font.Font(None, 30)

# Temporizador para animaciones
reloj = pygame.time.Clock()
FPS = 60

# --- 2. CONFIGURACIÓN DEL JUEGO DE PROBABILIDAD ---
CARAS_DADO = ["Pikachu", "Jigglypuff", "Squirtle", "Pikachu", "Jigglypuff", "Squirtle"]
POKEMON_NOMBRES = sorted(list(set(CARAS_DADO))) 

# Variables de estado del juego
contadores = {nombre: 0 for nombre in POKEMON_NOMBRES}
total_lanzamientos = 0
probabilidad_a_priori = 2 / 6 
apuesta_jugador = POKEMON_NOMBRES[1] 
ganadas_subjetiva = 0 
apuestas_totales = 0 
resultado_actual = "Ninguno" 
resultado_siguiente = "Ninguno" # Variable temporal para el resultado antes de la animación

# Variables para la animación del resultado (la imagen del Pokémon)
animando_lanzamiento = False
anim_start_time = 0
anim_duration = 0.5 # segundos

# --- 3. CARGA DE IMÁGENES Y LOGO ---
def cargar_imagen(nombre, ancho=None, alto=None):
    """Carga y escala una imagen. Si falla, retorna un cuadrado de color ROJO."""
    try:
        imagen = pygame.image.load(nombre).convert_alpha()
        if ancho and alto:
            imagen = pygame.transform.scale(imagen, (ancho, alto))
        return imagen
    except pygame.error as e:
        print(f"Error al cargar la imagen {nombre}: {e}")
        superficie_error = pygame.Surface((ancho if ancho else 100, alto if alto else 100), pygame.SRCALPHA) 
        superficie_error.fill(ROJO_ERROR + (128,))
        return superficie_error

# Logo
logo_pokemon = cargar_imagen("logo_pokemon.png", 350, 150) 
fondo_imagen = cargar_imagen("fondo.jpeg", ANCHO, ALTO) 

# Imágenes de Pokémon
imagenes_pokemon_game = {}
imagenes_pokemon_menu = {}
for nombre in POKEMON_NOMBRES:
    filename = f"{nombre.lower()}.png" 
    imagenes_pokemon_game[nombre] = cargar_imagen(filename, 250, 250)
    imagenes_pokemon_menu[nombre] = cargar_imagen(filename, 180, 180)

# Imagen de Pokebola (Tamaño ajustado para la animación)
pokebola_imagen = cargar_imagen("pokeball.png", 80, 80) # Optimizado a 80x80

# --- 4. CARGA Y REPRODUCCIÓN DE MÚSICA (CORREGIDO) ---
MUSICA_FONDO = "pokemon_music.mp3" 

def cargar_musica(nombre_archivo): # CORRECCIÓN: Usar 'nombre_archivo' como parámetro
    """Carga y reproduce la música de fondo en bucle."""
    try:
        pygame.mixer.music.load(nombre_archivo) # CORRECCIÓN: Usar 'nombre_archivo'
        pygame.mixer.music.play(-1) 
        pygame.mixer.music.set_volume(0.3) 
        print(f"Música {nombre_archivo} cargada y reproduciéndose.")
    except pygame.error as e:
        print(f"Error al cargar o reproducir la música {nombre_archivo}: {e}")

cargar_musica(MUSICA_FONDO) # CORRECCIÓN: Llamar con la variable string MUSICA_FONDO

# --- 5. FUNCIONES DE LÓGICA DEL JUEGO ---

def lanzar_dado():
    """Simula el lanzamiento del dado, actualiza contadores y evalúa la apuesta."""
    global total_lanzamientos, resultado_actual, apuestas_totales, ganadas_subjetiva
    global animando_lanzamiento, anim_start_time
    global animando_pokebola, pokebola_start_time, resultado_siguiente
    
    # 1. Lanzamiento (solo se simula aquí, la actualización de contadores se hace después de la animación)
    nuevo_resultado = random.choice(CARAS_DADO)
    
    # 2. Guardar el resultado temporalmente
    resultado_siguiente = nuevo_resultado

    # 3. Iniciar animación de la Pokebola
    animando_pokebola = True
    pokebola_start_time = time.time()
    
def completar_lanzamiento():
    """Actualiza las estadísticas después de que la animación de la Pokebola termina."""
    global total_lanzamientos, resultado_actual, apuestas_totales, ganadas_subjetiva
    global animando_lanzamiento, anim_start_time, resultado_siguiente
    
    # 1. Actualizar resultado
    resultado_actual = resultado_siguiente
    
    # 2. Actualizar estadísticas de probabilidad objetiva (Frecuencia relativa)
    contadores[resultado_actual] += 1
    total_lanzamientos += 1
    
    # 3. Actualizar estadísticas de probabilidad subjetiva (Apuesta)
    apuestas_totales += 1
    if resultado_actual == apuesta_jugador:
        ganadas_subjetiva += 1

    # 4. Iniciar animación del Pokémon (la que ya tenías)
    animando_lanzamiento = True
    anim_start_time = time.time()


def cambiar_apuesta():
    """Cambia la apuesta del jugador al siguiente Pokémon en la lista."""
    global apuesta_jugador
    
    try:
        idx_actual = POKEMON_NOMBRES.index(apuesta_jugador)
    except ValueError:
        apuesta_jugador = POKEMON_NOMBRES[0]
        return
    
    nuevo_idx = (idx_actual + 1) % len(POKEMON_NOMBRES)
    apuesta_jugador = POKEMON_NOMBRES[nuevo_idx]

# --- 6. FUNCIONES DE DIBUJO GENERALES ---
def dibujar_texto(superficie, texto, fuente, color, x, y, centrar_x=False, centrar_y=False):
    """Función auxiliar para dibujar texto con opciones de centrado."""
    texto_superficie = fuente.render(texto, True, color)
    rect = texto_superficie.get_rect()
    if centrar_x:
        rect.centerx = x
    else:
        rect.topleft = (x, y)
        
    if centrar_y:
        rect.centery = y
    
    superficie.blit(texto_superficie, rect)

def fade_transition(duration=0.5):
    """Realiza un efecto de fundido de pantalla."""
    fade_surface = pygame.Surface((ANCHO, ALTO))
    fade_surface.fill(NEGRO)
    
    for alpha in range(0, 255, 5):
        fade_surface.set_alpha(alpha)
        pantalla.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)
    
    for alpha in range(255, 0, -5):
        fade_surface.set_alpha(alpha)
        if estado_actual == STATE_GAME: 
            dibujar_juego_sin_flip()
        else: 
            dibujar_menu_sin_flip()
        pantalla.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)
        
# --- 7. FUNCIONES DE DIBUJO DE ESTADOS (MENU) ---

# Función auxiliar para dibujar el menú sin el flip, usada en la transición
def dibujar_menu_sin_flip():
    pantalla.blit(fondo_imagen, (0, 0))
    logo_rect = logo_pokemon.get_rect(center=(ANCHO // 2, 100))
    pantalla.blit(logo_pokemon, logo_rect)
    dibujar_texto(pantalla, "¿Por quién apostás?", fuente_seccion, AMARILLO_POKEMON, ANCHO // 2, 220, centrar_x=True)
    
    spacing = 250
    y_poke = 350
    
    nombres = POKEMON_NOMBRES 
    pantalla.blit(imagenes_pokemon_menu[nombres[0]], (ANCHO // 2 - spacing, y_poke)) 
    pantalla.blit(imagenes_pokemon_menu[nombres[1]], (ANCHO // 2 - 90, y_poke)) 
    pantalla.blit(imagenes_pokemon_menu[nombres[2]], (ANCHO // 2 + spacing - 180, y_poke)) 
    
    # Botón JUGAR con animación de escala
    boton_rect = pygame.Rect(ANCHO // 2 - 150, ALTO - 150, 300, 70)
    
    mouse_pos = pygame.mouse.get_pos()
    scale_factor = 1.0
    if boton_rect.collidepoint(mouse_pos):
        scale_factor = 1.05 
        
    scaled_width = int(boton_rect.width * scale_factor)
    scaled_height = int(boton_rect.height * scale_factor)
    scaled_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
    scaled_rect.center = boton_rect.center

    pygame.draw.rect(pantalla, AZUL_BOTON, scaled_rect, border_radius=10)
    dibujar_texto(pantalla, "JUGAR", fuente_seccion, BLANCO, scaled_rect.centerx, scaled_rect.centery, centrar_x=True, centrar_y=True)

def dibujar_menu():
    """Dibuja la pantalla de bienvenida."""
    dibujar_menu_sin_flip()
    pygame.display.flip()

# --- 8. VARIABLES DE ANIMACIÓN DE LA POKEBOLA ---
animando_pokebola = False
pokebola_start_time = 0
pokebola_duration = 0.4 # Animación rápida de 0.4 segundos
pokebola_start_pos = (225, ALTO - 50) # Centro del botón "Presiona ESPACIO"
pokebola_end_pos = (225, 325) # Centro de la imagen grande de apuesta

def dibujar_pokebola_animacion(current_time):
    """Dibuja la Pokebola en su trayectoria de lanzamiento."""
    global animando_pokebola
    
    elapsed_time = current_time - pokebola_start_time
    progress = elapsed_time / pokebola_duration
    
    if progress >= 1.0:
        # Animación terminada
        animando_pokebola = False
        completar_lanzamiento() # Llama a la lógica de actualización y la animación del Pokémon
        return

    # Posición X (Interpolación lineal simple)
    start_x, start_y = pokebola_start_pos
    end_x, end_y = pokebola_end_pos
    
    current_x = start_x + (end_x - start_x) * progress
    
    # Posición Y (Simulación de arco parabólico)
    arc_height = 200 # Altura máxima del arco en píxeles
    arc_y_offset = -4 * arc_height * (progress - 0.5)**2 + arc_height
    
    # Interpolar la posición vertical base
    base_y = start_y + (end_y - start_y) * progress
    
    current_y = base_y - arc_y_offset
    
    # Rotación (para simular el giro)
    rotation_angle = progress * 720 # Gira 2 veces completas
    rotated_pokebola = pygame.transform.rotate(pokebola_imagen, rotation_angle)
    
    # Dibujar la pokebola en su posición actual
    pokebola_rect = rotated_pokebola.get_rect(center=(current_x, current_y))
    pantalla.blit(rotated_pokebola, pokebola_rect)


# --- 9. FUNCIONES DE DIBUJO DE ESTADOS (GAME) ---

def dibujar_juego_sin_flip():
    """Dibuja la interfaz principal del juego (sin Pygame.display.flip)."""
    global total_lanzamientos, apuesta_jugador, ganadas_subjetiva, apuestas_totales
    global animando_lanzamiento, anim_start_time, resultado_actual

    pantalla.blit(fondo_imagen, (0, 0))
    current_time = time.time() # Obtener el tiempo actual
    
    # --- Columna Izquierda (Apuesta y Controles) ---
    IZQ_WIDTH = 450
    
    logo_rect_small = cargar_imagen("logo_pokemon.png", 250, 100)
    pantalla.blit(logo_rect_small, (IZQ_WIDTH // 2 - 125, 20))
    dibujar_texto(pantalla, "¿Por quién apostás?", fuente_seccion, AMARILLO_POKEMON, IZQ_WIDTH // 2, 140, centrar_x=True)
    
    # 3. Imagen de la apuesta actual (Grande)
    # NO DIBUJAMOS la imagen del Pokémon si la Pokebola está volando.
    if not animando_pokebola:
        pantalla.blit(imagenes_pokemon_game[apuesta_jugador], (IZQ_WIDTH // 2 - 125, 200))
    
    # DIBUJAR ANIMACIÓN DE POKEBOLA
    if animando_pokebola:
        dibujar_pokebola_animacion(current_time)
    else:
        # Lógica de animación del resultado (la que ya tenías)
        if resultado_actual != "Ninguno":
            if animando_lanzamiento:
                elapsed_time = current_time - anim_start_time
                if elapsed_time < anim_duration:
                    progress = elapsed_time / anim_duration
                    anim_scale = 0.5 + 0.5 * progress 
                    anim_alpha = int(255 * progress)
                    
                    img_base = imagenes_pokemon_game[resultado_actual]
                    temp_img = pygame.transform.scale(img_base, (int(img_base.get_width() * anim_scale), int(img_base.get_height() * anim_scale)))
                    temp_img.set_alpha(anim_alpha)
                    
                    img_rect = temp_img.get_rect(center=(IZQ_WIDTH // 2, 325))
                    pantalla.blit(temp_img, img_rect)
                else:
                    animando_lanzamiento = False 

            # Dibujar el resultado de texto y rendimiento
            texto_apuesta_resultado = f"Último: {resultado_actual}"
            color = VERDE_APUESTA if resultado_actual == apuesta_jugador else ROJO_APUESTA
            
            resultado_rect = pygame.Rect(IZQ_WIDTH // 2 - 150, 480, 300, 50) 
            pygame.draw.rect(pantalla, color, resultado_rect, border_radius=5)
            dibujar_texto(pantalla, texto_apuesta_resultado, fuente_seccion, NEGRO, IZQ_WIDTH // 2, 505, centrar_x=True, centrar_y=True)
            
            if apuestas_totales > 0:
                rendimiento = (ganadas_subjetiva / apuestas_totales) * 100
                texto_rendimiento = f"Rendimiento: {ganadas_subjetiva}/{apuestas_totales} ({rendimiento:.1f}%)"
                dibujar_texto(pantalla, texto_rendimiento, fuente_cuerpo, BLANCO, IZQ_WIDTH // 2, 550, centrar_x=True)


    # --- Columna Derecha (Tabla de Estadísticas) ---
    dibujar_texto(pantalla, f"Lanzamientos totales = {total_lanzamientos}", fuente_seccion, AMARILLO_POKEMON, 850, 110, centrar_x=True)

    tabla_rect = pygame.Rect(500, 170, ANCHO - 550, ALTO - 250)
    pygame.draw.rect(pantalla, AZUL_FONDO, tabla_rect, border_radius=15)
    
    X_COL_START = 530
    Y_HEADER = 200
    X_COL_OFFSET = [0, 140, 280, 420] 
    HEADERS = ["Pokémon", "Conteo", "A priori", "A posteriori"]
    
    for i, header in enumerate(HEADERS):
        dibujar_texto(pantalla, header, fuente_cuerpo, BLANCO, X_COL_START + X_COL_OFFSET[i], Y_HEADER)
    
    y_pos = Y_HEADER + 45
    for i, pokemon in enumerate(POKEMON_NOMBRES):
        conteo = contadores[pokemon]
        prob_a_posteriori = (conteo / total_lanzamientos) if total_lanzamientos > 0 else 0
        
        if i > 0:
            pygame.draw.line(pantalla, GRIS_OSCURO, (510, y_pos - 10), (ANCHO - 50, y_pos - 10), 1)

        datos = [
            pokemon,
            str(conteo),
            f"{probabilidad_a_priori * 100:.1f}%",
            f"{prob_a_posteriori * 100:.1f}%"
        ]

        color_dato = AMARILLO_POKEMON if pokemon == apuesta_jugador else BLANCO 

        for j, dato in enumerate(datos):
            dibujar_texto(pantalla, dato, fuente_cuerpo, color_dato, X_COL_START + X_COL_OFFSET[j], y_pos)
        
        y_pos += 45

    # 6. Controles (Sección inferior)
    espacio_rect = pygame.Rect(50, ALTO - 80, 350, 60)
    pygame.draw.rect(pantalla, AZUL_FONDO, espacio_rect, border_radius=10)
    dibujar_texto(pantalla, "Presiona ESPACIO para lanzar", fuente_cuerpo, BLANCO, 225, ALTO - 50, centrar_x=True, centrar_y=True)
    
    cambio_rect = pygame.Rect(ANCHO - 400, ALTO - 80, 350, 60)
    pygame.draw.rect(pantalla, AZUL_FONDO, cambio_rect, border_radius=10)
    dibujar_texto(pantalla, "Presiona C para cambiar la apuesta", fuente_cuerpo, BLANCO, ANCHO - 225, ALTO - 50, centrar_x=True, centrar_y=True)

def dibujar_juego():
    """Dibuja la interfaz principal del juego y actualiza la pantalla."""
    dibujar_juego_sin_flip()
    pygame.display.flip()

# --- 10. BUCLE PRINCIPAL DEL JUEGO ---

ejecutando = True
while ejecutando:
    
    # --- Manejo de Eventos ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        
        if estado_actual == STATE_MENU:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    ejecutando = False
            if evento.type == pygame.MOUSEBUTTONDOWN:
                boton_rect = pygame.Rect(ANCHO // 2 - 150, ALTO - 150, 300, 70)
                if boton_rect.collidepoint(pygame.mouse.get_pos()):
                    estado_anterior = estado_actual
                    estado_actual = STATE_GAME 
                    if estado_anterior != estado_actual:
                        fade_transition() 
        
        elif estado_actual == STATE_GAME:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and not animando_pokebola: # Solo si no hay animación en curso
                    lanzar_dado()
                
                if evento.key == pygame.K_c and not animando_pokebola:
                    cambiar_apuesta()
                
                if evento.key == pygame.K_ESCAPE:
                    ejecutando = False 

    # --- Dibujo del Estado Actual ---
    if estado_actual == STATE_MENU:
        dibujar_menu()

    elif estado_actual == STATE_GAME:
        dibujar_juego()
    
    reloj.tick(FPS) 

# --- Salir de Pygame ---
pygame.quit()
sys.exit()