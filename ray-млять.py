import pygame
import math
import sys

# инициализация модуля pygame
pygame.init()

# задаем размеры экрана и параметры карты
WIDTH, HEIGHT = 640, 480
PROJECTION_PLANE_WIDTH = WIDTH  # ширина плоскости проекции (экран)
PROJECTION_PLANE_HEIGHT = HEIGHT  # высота плоскости проекции (экран)
TILE_SIZE = 64  # размер одной плитки карты в пикселях
MAP_WIDTH, MAP_HEIGHT = 8, 8  # размеры карты

# параметры движения игрока
player_x, player_y = 300, 300  # начальная позиция игрока
player_dir = 0  # направление взгляда игрока в радианах
FOV = math.pi / 3  # поле зрения (60 градусов)
HALF_FOV = FOV / 2  # половина поля зрения
NUM_RAYS = 120  # количество лучей для расчета
DELTA_ANGLE = FOV / NUM_RAYS  # изменение угла между соседними лучами
MAX_DEPTH = 800  # максимальная глубина проверки для луча
SCALE = PROJECTION_PLANE_WIDTH // NUM_RAYS  # ширина полосы проекции для каждого луча

# карта, определяющая стены ('#') и свободное просранство ('.')
mini_map = [
    '########',
    '#......#',
    '#......#',
    '#......#',
    '#......#',
    '#......#',
    '#......#',
    '########'
]

# цвета
BLACK = (0, 0, 0)  # черный цвет
GOLD = (255, 215, 0)  # золотой цвет потому что дорого-богато

# создание окна игры
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2.5D Raycasting Demo")  # Заголовок окна

# основной игровой цикл
clock = pygame.time.Clock()  # Часы для контроля времени

def ray_casting(): 
    # начальный угол луча (направление игрока минус половина поля зрения)
    start_angle = player_dir - HALF_FOV
    # проход по каждому лучу
    for ray in range(NUM_RAYS):
        # для каждого луча проверяем его длину (глубину)
        for depth in range(MAX_DEPTH):
            # вычисляем предполагаемую цель (точку на карте) для текущей глубины
            target_x = player_x + depth * math.cos(start_angle)
            target_y = player_y + depth * math.sin(start_angle)

            # переводим координаты в индексы карты
            map_x = int(target_x / TILE_SIZE)
            map_y = int(target_y / TILE_SIZE)

            # если луч наткнулся на стену
            if mini_map[map_y][map_x] == '#':
                # корректируем глубину для устранения эффекта "рыбьего глаза"
                depth *= math.cos(player_dir - start_angle) 
                # рассчитываем высоту стены
                wall_height = 21000 / (depth + 0.0001)
                # рисуем прямоугольник, представляющий стену
                pygame.draw.rect(screen, GOLD, (ray * SCALE, HEIGHT // 2 - wall_height // 2, SCALE, wall_height))
                break  # прекращаем дальнейшую проверку, так как стена найдена
        
        # Переходим к следующему углу для следующего луча
        start_angle += DELTA_ANGLE

# Главный цикл игры
while True:
    # Обрабатываем события
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # очищаем экран от грязи всякой и заполняем черным
    screen.fill(BLACK)

    # получаем нажатия клавиш для управления игроком
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_dir -= 0.04  # поворот влево
    if keys[pygame.K_RIGHT]:
        player_dir += 0.04  # поворот вправо
    if keys[pygame.K_UP]:
        # двигалка вперде
        player_x += 5 * math.cos(player_dir)
        player_y += 5 * math.sin(player_dir)
    if keys[pygame.K_DOWN]:
        # двигалка назад
        player_x -= 5 * math.cos(player_dir)
        player_y -= 5 * math.sin(player_dir)

    # рендеринг мира с помощью алгоритма трассировки лучей
    ray_casting()

    # обновляем экран
    pygame.display.flip()
    # 60 фпс а то игра слишком быстрой будет
    clock.tick(60)