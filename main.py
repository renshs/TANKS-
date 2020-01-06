import sys
from os import path

import pygame

pygame.init()

TURN_1 = False  # поворачиваем мы сейчас или нет
TURN_2 = False
FPS = 50  # fps началного экрана
clock = pygame.time.Clock()

# настройка экрана заставки
size = widt, heigh = 800, 800
screen = pygame.display.set_mode(size)

DIRECTIONS = {  # словарь, с помощью которого мы находим угол поворота
    'up': 1,
    'left': 2,
    'down': 3,
    'right': 4
}


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):  # функция для загрузки изображений
    fullname = path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def start_screen():
    intro_text = ["ТАНКИ", "", "",
                  "", "",
                  "Танк1", "",
                  "Танк2"]

    fon = pygame.transform.scale(load_image('tank-sssr-red-krasnyy.jpg'), (widt, heigh))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    p1_image = load_image('tank_small.png')
    p2_image = load_image('enemy_tank_small.png')
    screen.blit(p1_image, (80, 210))
    screen.blit(p2_image, (80, 265))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


start_screen()  # вызываем начальный экран


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {'wall': load_image('brick_wall.png'), 'stone_wall': load_image('stone_wall.png')}
player_image = load_image('tank_small.png', -1)
enemy_image = load_image('enemy_tank_small.png', -1)

tile_width = tile_height = 50

player_size = 34


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.type = tile_type
        self.x = pos_x * tile_width
        self.y = pos_y * tile_height
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        if self.type == 'wall':
            self.hp = 15

    def type_of_tile(self):
        return self.type

    def get_shot(self):
        if self.type == 'wall':
            self.hp -= 1

            if self.hp <= 10:
                self.image = load_image('brick_wall_brocken_1.png')

            if self.hp <= 5:
                self.image = load_image('brick_wall_brocken.png')

            if self.hp == 0:
                self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        self.x = pos_x
        self.y = pos_y
        self.direction = 1
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * self.x, tile_height * self.y + 1)
        self.speed_y = 0
        self.speed_x = 0
        self.movement_direction = None
        self.hp = 10

    def update(self):
        global TURN_1
        if self.movement_direction:
            if not TURN_1:
                angle = (DIRECTIONS[self.movement_direction]) - self.direction
                self.image = pygame.transform.rotate(self.image, angle * 90)
                self.direction = DIRECTIONS[self.movement_direction]
                TURN_1 = True
            self.rect.y += self.speed_y
            self.rect.x += self.speed_x
            back = pygame.sprite.spritecollideany(self, tiles_group)
            if back:
                self.collide(back)

    def collide(self, wall):
        if self.movement_direction == 'up':
            self.rect.y = wall.y + tile_height

        if self.movement_direction == 'down':
            self.rect.y = wall.y - player_size

        if self.movement_direction == 'left':
            self.rect.x = wall.x + tile_width

        if self.movement_direction == 'right':
            self.rect.x = wall.x - player_size

    # Эта функция отвечает за поиск координат пушки

    def launcher_coords(self):
        if self.direction == 1:
            return self.rect.x + 16, self.rect.y
        elif self.direction == 2:
            return self.rect.x, self.rect.y + 16
        elif self.direction == 3:
            return self.rect.x + 16, self.rect.y + player_size
        elif self.direction == 4:
            return self.rect.x + player_size, self.rect.y + 16

    def shoot(self):
        x, y = self.launcher_coords()
        bullet = Bullet(x, y, self.direction)

    def get_shot(self):
        self.hp -= 1
        if self.hp == 0:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direct):
        super().__init__(bullets, all_sprites)
        self.direct = direct
        if self.direct == 1 or self.direct == 3:
            self.image = pygame.Surface((4, 3))
        else:
            self.image = pygame.Surface((4, 3))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        if self.direct == 1:
            self.rect.bottom = y
            self.rect.centerx = x
        elif self.direct == 2:
            self.rect.bottom = y + 2
            self.rect.right = x
        elif self.direct == 3:
            self.rect.top = y
            self.rect.centerx = x
        elif self.direct == 4:
            self.rect.bottom = y + 2
            self.rect.left = x

    def update(self):
        if pygame.sprite.spritecollideany(self, tiles_group):
            pygame.sprite.spritecollideany(self, tiles_group).get_shot()
            self.kill()
        if pygame.sprite.spritecollideany(self, enemy_group):
            pygame.sprite.spritecollideany(self, enemy_group).get_shot()
            self.kill()
        if pygame.sprite.spritecollideany(self, player_group):
            pygame.sprite.spritecollideany(self, player_group).get_shot()
            self.kill()
        if self.direct == 1:
            self.rect = self.rect.move(0, -4)
        elif self.direct == 2:
            self.rect = self.rect.move(-4, 0)
        elif self.direct == 3:
            self.rect = self.rect.move(0, 4)
        elif self.direct == 4:
            self.rect = self.rect.move(4, 0)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        self.x = pos_x
        self.y = pos_y
        self.direction = 3
        super().__init__(enemy_group, all_sprites)
        self.image = enemy_image
        self.image = pygame.transform.rotate(self.image, 180)
        self.rect = self.image.get_rect().move(tile_width * self.x, tile_height * self.y + 1)
        self.speed_y = 0
        self.speed_x = 0
        self.movement_direction = None
        self.hp = 10

    def update(self):
        global TURN_2
        if self.movement_direction:
            if not TURN_2:
                angle = (DIRECTIONS[self.movement_direction]) - self.direction
                self.image = pygame.transform.rotate(self.image, angle * 90)
                self.direction = DIRECTIONS[self.movement_direction]
                TURN_2 = True
            self.rect.y += self.speed_y
            self.rect.x += self.speed_x
            back = pygame.sprite.spritecollideany(self, tiles_group)
            if back:
                self.collide(back)

    def collide(self, wall):
        if self.movement_direction == 'up':
            self.rect.y = wall.y + tile_height

        if self.movement_direction == 'down':
            self.rect.y = wall.y - player_size

        if self.movement_direction == 'left':
            self.rect.x = wall.x + tile_width

        if self.movement_direction == 'right':
            self.rect.x = wall.x - player_size

    # Эта функция отвечает за поиск координат пушки

    def launcher_coords(self):
        if self.direction == 1:
            return self.rect.x + 16, self.rect.y
        elif self.direction == 2:
            return self.rect.x, self.rect.y + 16
        elif self.direction == 3:
            return self.rect.x + 16, self.rect.y + player_size
        elif self.direction == 4:
            return self.rect.x + player_size, self.rect.y + 16

    def shoot(self):
        x, y = self.launcher_coords()
        bullet = Bullet(x, y, self.direction)

    def get_shot(self):
        self.hp -= 1
        if self.hp == 0:
            self.kill()



player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '$':
                Tile('stone_wall', x, y)
            elif level[y][x] == '*':
                enemy = Enemy(x, y)
            elif level[y][x] == '@':
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, enemy, x, y


player, enemy, level_x, level_y = generate_level(load_level('map_2.txt'))

size = widt, heigh = 750, 800
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()
FPS = 30
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # управление играка1
            if event.key == pygame.K_LEFT:
                if not TURN_1:
                    player.movement_direction = 'left'
                    player.speed_x = -3
            if event.key == pygame.K_RIGHT:
                if not TURN_1:
                    player.movement_direction = 'right'
                    player.speed_x = 3
            if event.key == pygame.K_DOWN:
                if not TURN_1:
                    player.movement_direction = 'down'
                    player.speed_y = 3
            if event.key == pygame.K_UP:
                if not TURN_1:
                    player.movement_direction = 'up'
                    player.speed_y = -3
            if event.key == pygame.K_SPACE:
                player.shoot()
            # управление игроком2
            if event.key == pygame.K_a:
                if not TURN_2:
                    enemy.movement_direction = 'left'
                    enemy.speed_x = -3
            if event.key == pygame.K_d:
                if not TURN_2:
                    enemy.movement_direction = 'right'
                    enemy.speed_x = 3
            if event.key == pygame.K_s:
                if not TURN_2:
                    enemy.movement_direction = 'down'
                    enemy.speed_y = 3
            if event.key == pygame.K_w:
                if not TURN_2:
                    enemy.movement_direction = 'up'
                    enemy.speed_y = -3
            if event.key == pygame.K_LSHIFT:
                enemy.shoot()
        if event.type == pygame.KEYUP:
            # управление игроком1
            if event.key == pygame.K_DOWN:
                if player.movement_direction == 'down':
                    player.movement_direction = None
                    TURN_1 = False
                    player.speed_y = 0
            if event.key == pygame.K_UP:
                if player.movement_direction == 'up':
                    player.movement_direction = None
                    TURN_1 = False
                    player.speed_y = 0
            if event.key == pygame.K_LEFT:
                if player.movement_direction == 'left':
                    player.movement_direction = None
                    TURN_1 = False
                    player.speed_x = 0
            if event.key == pygame.K_RIGHT:
                if player.movement_direction == 'right':
                    player.movement_direction = None
                    TURN_1 = False
                    player.speed_x = 0

            # управление игроком2

            if event.key == pygame.K_s:
                if enemy.movement_direction == 'down':
                    enemy.movement_direction = None
                    TURN_2 = False
                    enemy.speed_y = 0
            if event.key == pygame.K_w:
                if enemy.movement_direction == 'up':
                    enemy.movement_direction = None
                    TURN_2 = False
                    enemy.speed_y = 0
            if event.key == pygame.K_a:
                if enemy.movement_direction == 'left':
                    enemy.movement_direction = None
                    TURN_2 = False
                    enemy.speed_x = 0
            if event.key == pygame.K_d:
                if enemy.movement_direction == 'right':
                    enemy.movement_direction = None
                    TURN_2 = False
                    enemy.speed_x = 0

    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()
    screen.fill((0, 0, 0))

pygame.quit()
