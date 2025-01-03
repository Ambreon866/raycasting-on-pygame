import pygame
import math
import sys

# Инициализация модуля pygame
pygame.init()

# Задаем размеры экрана и параметры карты
WIDTH, HEIGHT = 640, 480
PROJECTION_PLANE_WIDTH = WIDTH
PROJECTION_PLANE_HEIGHT = HEIGHT
TILE_SIZE = 64
MAP_WIDTH, MAP_HEIGHT = 8, 8

# Параметры движения игрока
player_x, player_y = 300, 300
player_dir = 0
FOV = math.pi / 3
HALF_FOV = FOV / 2

# Параметры графики
graphics_quality = 'medium'
graphics_settings = {
    'low': {'NUM_RAYS': 30, 'MAX_DEPTH': 200},
    'medium': {'NUM_RAYS': 60, 'MAX_DEPTH': 400},
    'high': {'NUM_RAYS': 120, 'MAX_DEPTH': 800}
}

# Задать уровни графики начальным
NUM_RAYS = graphics_settings[graphics_quality]['NUM_RAYS']
MAX_DEPTH = graphics_settings[graphics_quality]['MAX_DEPTH']
DELTA_ANGLE = FOV / NUM_RAYS
SCALE = PROJECTION_PLANE_WIDTH // NUM_RAYS

# Карта
mini_map = [
    '########',
    '#......#',
    '###D####',
    '#......#',
    '#......#',
    '#......#',
    '#..P...#',
    '########'
]

# Цвета
BACKGROUND_COLOR = (30, 30, 30)
WALL_COLOR = (160, 160, 160)

# Состояние двери
door_active = True
door_open_time = 0

# Создание окна игры
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Raycasting Game")

# Основной игровой цикл
clock = pygame.time.Clock()

def initialize_player_position():
    global player_x, player_y
    for y, row in enumerate(mini_map):
        for x, tile in enumerate(row):
            if tile == 'P':
                player_x = x * TILE_SIZE + TILE_SIZE // 2
                player_y = y * TILE_SIZE + TILE_SIZE // 2
                return

def ray_casting():
    start_angle = player_dir - HALF_FOV
    for ray in range(NUM_RAYS):
        sin_a = math.sin(start_angle)
        cos_a = math.cos(start_angle)
        
        for depth in range(MAX_DEPTH):
            target_x = player_x + depth * cos_a
            target_y = player_y + depth * sin_a

            map_x = int(target_x / TILE_SIZE)
            map_y = int(target_y / TILE_SIZE)

            if 0 <= map_x < MAP_WIDTH and 0 <= map_y < MAP_HEIGHT:
                if mini_map[map_y][map_x] == '#':
                    adjusted_depth = depth * math.cos(player_dir - start_angle)
                    wall_height = 21000 / (adjusted_depth + 0.0001)
                    
                    color_intensity = 255 / (1 + adjusted_depth * adjusted_depth * 0.0001)
                    wall_color = (color_intensity, color_intensity, color_intensity)

                    pygame.draw.rect(screen, wall_color, 
                                     (ray * SCALE, HEIGHT // 2 - wall_height // 2, SCALE, wall_height))
                    break
                elif mini_map[map_y][map_x] == 'D':
                    if door_active:
                        adjusted_depth = depth * math.cos(player_dir - start_angle)
                        wall_height = 21000 / (adjusted_depth + 0.0001)
                        pygame.draw.rect(screen, (0, 100, 100), 
                                         (ray * SCALE, HEIGHT // 2 - wall_height // 2, SCALE, wall_height))
                        break

        start_angle += DELTA_ANGLE

def handle_player_movement(keys):
    global player_x, player_y, player_dir, door_active, door_open_time
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_dir -= 0.04
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_dir += 0.04
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        new_x = player_x + 5 * math.cos(player_dir)
        new_y = player_y + 5 * math.sin(player_dir)
        map_x = int(new_x / TILE_SIZE)
        map_y = int(new_y / TILE_SIZE)
        if mini_map[map_y][map_x] != '#' or (mini_map[map_y][map_x] == 'D' and not door_active):
            player_x = new_x
            player_y = new_y
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        new_x = player_x - 5 * math.cos(player_dir)
        new_y = player_y - 5 * math.sin(player_dir)
        map_x = int(new_x / TILE_SIZE)
        map_y = int(new_y / TILE_SIZE)
        if mini_map[map_y][map_x] != '#' or (mini_map[map_y][map_x] == 'D' and not door_active):
            player_x = new_x
            player_y = new_y

    if keys[pygame.K_SPACE] and door_active:
        door_active = False
        door_open_time = pygame.time.get_ticks()

def check_door_status():
    global door_active, door_open_time
    if not door_active and pygame.time.get_ticks() - door_open_time > 5000:
        door_active = True

def change_graphics_quality(quality):
    global NUM_RAYS, MAX_DEPTH, DELTA_ANGLE, SCALE, graphics_quality
    graphics_quality = quality
    settings = graphics_settings[quality]
    NUM_RAYS = settings['NUM_RAYS']
    MAX_DEPTH = settings['MAX_DEPTH']
    DELTA_ANGLE = FOV / NUM_RAYS
    SCALE = PROJECTION_PLANE_WIDTH // NUM_RAYS

# Инициализация позиции игрока перед главным циклом
initialize_player_position()

# Главный цикл игры
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                change_graphics_quality('low')
            elif event.key == pygame.K_F2:
                change_graphics_quality('medium')
            elif event.key == pygame.K_F3:
                change_graphics_quality('high')

    screen.fill(BACKGROUND_COLOR)

    keys = pygame.key.get_pressed()
    handle_player_movement(keys)

    check_door_status()

    ray_casting()

    pygame.display.flip()
    clock.tick(60)
