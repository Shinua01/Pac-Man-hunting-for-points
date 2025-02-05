import pygame
import random
import time

# Инициализация Pygame и микшера
pygame.init()
pygame.mixer.init()

# Параметры окна и блока
TILE_SIZE = 40
MAP_WIDTH = 25
MAP_HEIGHT = 12
WIDTH = TILE_SIZE * MAP_WIDTH
HEIGHT = TILE_SIZE * MAP_HEIGHT
FPS = 8

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

pygame.mixer.music.load("background_music.mp3")  # Фоновая музыка
eat_dot_sound = pygame.mixer.Sound("eat_dot.wav")
bonus_life_sound = pygame.mixer.Sound("bonus_life.wav")
power_pellet_sound = pygame.mixer.Sound("power_pellet.wav")
game_over_sound = pygame.mixer.Sound("game_over.wav")
you_win_sound = pygame.mixer.Sound("you_win.wav")

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man: hunting for points")
clock = pygame.time.Clock()

# Загрузка изображений Пакмана
pacman_images = {
    'up': {
        'open': pygame.image.load("pacman_up_open.png"),
        'closed': pygame.image.load("pacman_up_closed.png")
    },
    'down': {
        'open': pygame.image.load("pacman_down_open.png"),
        'closed': pygame.image.load("pacman_down_closed.png")
    },
    'left': {
        'open': pygame.image.load("pacman_left_open.png"),
        'closed': pygame.image.load("pacman_left_closed.png")
    },
    'right': {
        'open': pygame.image.load("pacman_right_open.png"),
        'closed': pygame.image.load("pacman_right_closed.png")
    }
}

for direction in pacman_images:
    for state in pacman_images[direction]:
        pacman_images[direction][state] = pygame.transform.scale(pacman_images[direction][state],
                                                                 (TILE_SIZE, TILE_SIZE))

# Загрузка изображений привидений
ghost_images = [
    pygame.image.load("red_ghost.png"),
    pygame.image.load("green_ghost.png"),
    pygame.image.load("orange_ghost.png"),
    pygame.image.load("pink_ghost.png")
]
ghost_images = [pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE)) for img in ghost_images]

# Загрузка изображений бонусов
bonus_image = pygame.image.load("bonus.png")
bonus_image = pygame.transform.scale(bonus_image, (TILE_SIZE, TILE_SIZE))
power_bonus_image = pygame.image.load("power_pellet.png")
power_bonus_image = pygame.transform.scale(power_bonus_image, (TILE_SIZE, TILE_SIZE))

# Уровни игры
levels = [
    {  # Уровень 1
        "map": [
            "#########################",
            "#...............#.......#",
            "#.#####.#####.#.#.#####.#",
            "#.#.....#.....#.#.#.....#",
            "#.#.###.#.#####.#.#.###.#",
            "#.#.#...#.........#.#.#.#",
            "#...#.#.#########.#.#...#",
            "###.#.#.....#.....#.#.###",
            "#.....#.###.#.###.#.....#",
            "#.#####.#.......#.#.#####",
            "#.......#####.###.......#",
            "#########################"
        ],
        "player_start": (1, 1),
        "ghost_positions": [(5, 5), (10, 8), (15, 10), (20, 6)],
        "wall_color": BLUE,
        "dot_color": WHITE
    },
    {  # Уровень 2
        "map": [
            "#########################",
            "#...#.......#.......#...#",
            "#.#.#.#####.#.#####.#.#.#",
            "#.#.#....... .......#.#.#",
            "#.#.#####.# #####.#.### #",
            "#.#.....#.#     #.#.....#",
            "#.#####.# ####### ##### #",
            "#.......#    #    #.....#",
            "#.#####.######.#####.####",
            "#.....#..............#..#",
            "#.....#############.....#",
            "#########################"
        ],
        "player_start": (1, 1),
        "ghost_positions": [(5, 5), (10, 5), (15, 5), (20, 5)],
        "wall_color": PURPLE,
        "dot_color": YELLOW
    },
    {  # Уровень 3
        "map": [
            "#########################",
            "#......##.....##........#",
            "#.###.............###...#",
            "#...#.###########.###...#",
            "##..#....... .....#.....#",
            "#...#.### ##### ###.#...#",
            "#.###...#.     .#...###.#",
            "#...###.#       #.###...#",
            "###.#...# ##### #...#.###",
            "#...#.###.......###.#...#",
            "#.......................#",
            "#########################"
        ],
        "player_start": (1, 1),
        "ghost_positions": [(5, 5), (15, 5), (20, 9), (10, 7)],
        "wall_color": RED,
        "dot_color": CYAN
    }
]


class Player:#Пакмэн
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.direction = (0, 0)
        self.score = 0
        self.lives = 3
        self.last_change_time = time.time()
        self.is_open = True
        self.animation_delay = 0.1
        self.power_active = False
        self.power_end_time = 0

    def move(self, walls):#Размеры
        new_rect = self.rect.move(self.direction[0] * TILE_SIZE, self.direction[1] * TILE_SIZE)
        if not any(new_rect.colliderect(wall) for wall in walls):
            self.rect = new_rect

    def reset_position(self):#Сброс позиции
        self.rect.topleft = (self.start_x, self.start_y)
        self.direction = (0, 0)

    def activate_power(self): #Яблоко
        self.power_active = True
        self.power_end_time = time.time() + 5
        power_pellet_sound.play()

    def update_power(self):#Яблоко
        if self.power_active and time.time() > self.power_end_time:
            self.power_active = False

    def draw(self):
        current_time = time.time()
        if current_time - self.last_change_time >= 1:
            self.is_open = not self.is_open
            self.last_change_time = current_time

        if self.direction == (0, -1):
            pacman_state = 'up'
        elif self.direction == (0, 1):
            pacman_state = 'down'
        elif self.direction == (-1, 0):
            pacman_state = 'left'
        elif self.direction == (1, 0):
            pacman_state = 'right'
        else:
            pacman_state = 'right'

        pacman_image = pacman_images.get(pacman_state, {}).get('open' if self.is_open else 'closed',
                                                               pacman_images['right']['open'])
        screen.blit(pacman_image, self.rect.topleft)


class Ghost:#Призраки
    def __init__(self, x, y, image):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        self.direction = random.choice(self.directions)
        self.image = image
        self.active = True

    def move(self, walls, ghosts, player):
        if not self.active:
            return

        new_rect = self.rect.move(self.direction[0] * TILE_SIZE, self.direction[1] * TILE_SIZE)
        if not any(new_rect.colliderect(wall) for wall in walls) and not any(
                new_rect.colliderect(ghost.rect) for ghost in ghosts if ghost.active):
            self.rect = new_rect
        else:
            self.direction = random.choice(self.directions)

    def draw(self):
        if self.active:
            screen.blit(self.image, self.rect.topleft)


class GameState:#Новые уровни
    def __init__(self):
        self.current_level = 0
        self.walls = []
        self.dots = []
        self.player = None
        self.ghosts = []
        self.bonus = None
        self.bonus_spawn_time = time.time()
        self.power_bonus = None
        self.power_bonus_spawn_time = time.time()
        self.wall_color = BLUE
        self.dot_color = WHITE

    def load_level(self, level_number): #Функция отвечающая за карту
        self.current_level = level_number
        level_data = levels[level_number]

        self.walls.clear()
        self.dots.clear()
        self.ghosts.clear()
        self.wall_color = level_data["wall_color"]
        self.dot_color = level_data["dot_color"]

        for row_index, row in enumerate(level_data["map"]):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if tile == "#":
                    self.walls.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif tile == "." or tile == " ":
                    self.dots.append(pygame.Rect(x + TILE_SIZE // 4, y + TILE_SIZE // 4,
                                                 TILE_SIZE // 2, TILE_SIZE // 2))

        start_x = level_data["player_start"][0] * TILE_SIZE
        start_y = level_data["player_start"][1] * TILE_SIZE
        self.player = Player(start_x, start_y)

        for i, pos in enumerate(level_data["ghost_positions"]):
            x = pos[0] * TILE_SIZE
            y = pos[1] * TILE_SIZE
            self.ghosts.append(Ghost(x, y, ghost_images[i % len(ghost_images)]))

    def spawn_bonus(self, bonus_type): #Функция отвечающая появление бонусов
        while True:
            x = random.randint(0, MAP_WIDTH - 1) * TILE_SIZE
            y = random.randint(0, MAP_HEIGHT - 1) * TILE_SIZE
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            if not any(rect.colliderect(wall) for wall in self.walls):
                if bonus_type == "life":
                    self.bonus = rect
                    self.bonus_spawn_time = time.time()
                else:
                    self.power_bonus = rect
                    self.power_bonus_spawn_time = time.time()
                break


def show_game_over(player): #Функция отвечающая за окно поражения
    pygame.mixer.music.stop()
    game_over_sound.play()
    font = pygame.font.Font(None, 72)
    text = font.render("GAME OVER", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
    screen.blit(text, text_rect)

    font_score = pygame.font.Font(None, 36)
    score_text = font_score.render(f"Score: {player.score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
    screen.blit(score_text, score_rect)

    pygame.display.flip()
    pygame.time.wait(3000)


def show_you_win(player): #Функция отвечающая за победное окно
    pygame.mixer.music.stop()
    you_win_sound.play()
    font = pygame.font.Font(None, 72)
    text = font.render("YOU WIN", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
    screen.blit(text, text_rect)

    font_score = pygame.font.Font(None, 36)
    score_text = font_score.render(f"Score: {player.score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
    screen.blit(score_text, score_rect)

    pygame.display.flip()
    pygame.time.wait(3000)


class StartMenu:#Стартовое меню
    def __init__(self):
        self.background = pygame.image.load("background.jpg")
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
        self.title_font = pygame.font.Font(None, 74)
        self.button_font = pygame.font.Font(None, 36)
        self.start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
        self.instruction_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
        self.show_instructions = False

    def draw_instructions(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 36)
        lines = [
            "Инструкция к игре:",
            "Цель: собрать все точки на уровне",
            "Управление стрелками",
            "Собирайте белые точки для очков",
            "Избегайте призраков",
            "Вишня-дает дополнительную жизнь",
            "Вишня появляется каждые 10 секунд",
            "Яблоко-дает неуязвимость и возможность съедать призраков",
            "Яблоко появляется каждые 25 секунд",
            "Нажмите ESC для возврата в меню"
        ]

        y_offset = HEIGHT // 2 - 150
        for line in lines:
            text = font.render(line, True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 40

    def draw(self):
        screen.blit(self.background, (0, 0))

        # Заголовок
        title_text = self.title_font.render("PAC-MAN", True, YELLOW)
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 150))
        screen.blit(title_text, title_rect)

        # Кнопка Start
        pygame.draw.rect(screen, GREEN, self.start_button)
        start_text = self.button_font.render("СТАРТ", True, WHITE)
        screen.blit(start_text, start_text.get_rect(center=self.start_button.center))

        # Кнопка Инструкция
        pygame.draw.rect(screen, BLUE, self.instruction_button)
        instr_text = self.button_font.render("ИНСТРУКЦИЯ", True, WHITE)
        screen.blit(instr_text, instr_text.get_rect(center=self.instruction_button.center))

        if self.show_instructions:
            self.draw_instructions()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button.collidepoint(event.pos):
                return "start"
            elif self.instruction_button.collidepoint(event.pos):
                self.show_instructions = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.show_instructions = False
        return None


# Инициализация игры
game_state = GameState()
start_menu = StartMenu()

# Основной игровой цикл
running = True
in_menu = True

while running:
    if in_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            result = start_menu.handle_event(event)
            if result == "start":
                in_menu = False
                game_state.load_level(0)
                pygame.mixer.music.play(-1)

        start_menu.draw()
        pygame.display.flip()
        clock.tick(FPS)
    else:
        screen.fill(BLACK)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game_state.player.direction = (0, -1)
                elif event.key == pygame.K_DOWN:
                    game_state.player.direction = (0, 1)
                elif event.key == pygame.K_LEFT:
                    game_state.player.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game_state.player.direction = (1, 0)

        # Обновление состояний
        game_state.player.move(game_state.walls)
        game_state.player.update_power()

        for ghost in game_state.ghosts:
            ghost.move(game_state.walls, game_state.ghosts, game_state.player)

        # Проверка столкновений с точками
        for dot in game_state.dots[:]:
            if game_state.player.rect.colliderect(dot):
                game_state.dots.remove(dot)
                game_state.player.score += 10
                eat_dot_sound.play()

        # Проверка на победу
        if not game_state.dots:
            if game_state.current_level < len(levels) - 1:
                game_state.load_level(game_state.current_level + 1)
            else:
                show_you_win(game_state.player)
                running = False

        # Проверка столкновений с призраками
        for ghost in game_state.ghosts:
            if ghost.active and game_state.player.rect.colliderect(ghost.rect):
                if game_state.player.power_active:
                    ghost.active = False
                    game_state.player.score += 200
                else:
                    game_state.player.lives -= 1
                    if game_state.player.lives > 0:
                        game_state.player.reset_position()
                    else:
                        show_game_over(game_state.player)
                        running = False
                    break

        # Отрисовка объектов
        for wall in game_state.walls:
            pygame.draw.rect(screen, game_state.wall_color, wall)
        for dot in game_state.dots:
            pygame.draw.ellipse(screen, game_state.dot_color, dot)

        game_state.player.draw()
        for ghost in game_state.ghosts:
            ghost.draw()

        # Бонусы
        if game_state.bonus is None and time.time() - game_state.bonus_spawn_time >= 10:
            game_state.spawn_bonus("life")

        if game_state.bonus:
            screen.blit(bonus_image, game_state.bonus.topleft)
            if game_state.player.rect.colliderect(game_state.bonus):
                game_state.player.lives += 1
                bonus_life_sound.play()
                game_state.bonus = None

        if game_state.power_bonus is None and time.time() - game_state.power_bonus_spawn_time >= 25:
            game_state.spawn_bonus("power")

        if game_state.power_bonus:
            screen.blit(power_bonus_image, game_state.power_bonus.topleft)
            if game_state.player.rect.colliderect(game_state.power_bonus):
                game_state.player.activate_power()
                game_state.power_bonus = None

        # Отображение информации
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {game_state.player.score}", True, WHITE)
        lives_text = font.render(f"Lives: {game_state.player.lives}", True, GREEN)
        level_text = font.render(f"Level: {game_state.current_level + 1}", True, WHITE)
        power_text = font.render("POWER!", True, RED) if game_state.player.power_active else font.render("", True,
                                                                                                             WHITE)

        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (150, 10))
        screen.blit(level_text, (WIDTH - 150, 10))
        screen.blit(power_text, (WIDTH // 2 - 50, 10))

        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()
