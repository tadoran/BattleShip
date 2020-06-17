from itertools import cycle
from random import choice

import pygame
import sys
from pygame.locals import *

from ship import Ship

pygame.init()

TILE_WIDTH = 32
TILE_HEIGHT = 32

WIDTH = 10
HEIGHT = 10
WHITE = (255, 255, 255)


class SeaBackground:
    water_tiles_imgs = [
        'watrtl21.png', 'watrtl22.png', 'watrtl23.png', 'watrtl24.png',
        'watrtl25.png', 'watrtl26.png', 'watrtl27.png', 'watrtl28.png',
        'watrtl29.png', 'watrtl30.png', 'watrtl31.png', 'watrtl32.png',
        'watrtl33.png'
    ]

    def __init__(self):
        self.surf = pygame.Surface((TILE_WIDTH * WIDTH, TILE_HEIGHT * HEIGHT))
        self.rect = self.surf.get_rect()
        self.load_images()
        self.next_img = cycle(self.water_tiles_objs)
        self.generate()

    def load_images(self):
        self.water_tiles_objs = []
        for i, img_name in enumerate(self.water_tiles_imgs):
            img = pygame.image.load(f'images/water_tiles/{img_name}')
            img = pygame.transform.scale(img, (TILE_WIDTH, TILE_HEIGHT))
            self.water_tiles_objs.append(img)

    def generate(self):
        for y in range(HEIGHT + 1):
            for x in range(WIDTH + 1):
                self.surf.blit(next(self.next_img),
                               (TILE_WIDTH * x - (TILE_WIDTH // 2), TILE_HEIGHT * y - (TILE_HEIGHT // 2)))

        for y in range(HEIGHT + 1):
            for x in range(WIDTH + 1):
                pygame.draw.rect(self.surf, (0, 46, 70), (TILE_WIDTH * x, TILE_HEIGHT * y, TILE_WIDTH, TILE_HEIGHT), 1)

    def draw(self, surface):
        surface.blit(self.surf, self.rect)


class MissedCell:
    def __init__(self):
        self.surf = pygame.image.load("images/missed.png")
        self.surf.set_alpha(150)
        self.scale = 0.7
        self.surf = pygame.transform.scale(self.surf, (int(TILE_WIDTH * self.scale), int(TILE_HEIGHT * self.scale)))

    def draw(self, surface, x_cell, y_cell):
        img = pygame.transform.rotate(self.surf, choice([0, 90, 180, 270]))
        x_offset, y_offset = (TILE_WIDTH * (1 - self.scale)) // 2, (TILE_HEIGHT * (1 - self.scale)) // 2
        surface.blit(img, (x_cell * TILE_WIDTH + x_offset, y_cell * TILE_HEIGHT + y_offset))


class BlownCell:
    def __init__(self):
        self.surf = pygame.image.load("images/explosion.png")
        self.scale = 1.7
        self.surf = pygame.transform.smoothscale(self.surf,
                                                 (int(TILE_WIDTH * self.scale), int(TILE_HEIGHT * self.scale)))

    def draw(self, surface, x_cell, y_cell):
        img = pygame.transform.rotate(self.surf, choice([0, 90, 180, 270]))
        x_offset, y_offset = (TILE_WIDTH * (1 - self.scale)) // 2, (TILE_HEIGHT * (1 - self.scale)) // 2
        surface.blit(img, (x_cell * TILE_WIDTH + x_offset, y_cell * TILE_HEIGHT + y_offset))


class BattleOverlay:
    def __init__(self, x, y):
        self.surf = pygame.Surface((TILE_WIDTH * WIDTH, TILE_HEIGHT * HEIGHT))
        self.rect = self.surf.get_rect()
        self.x = x
        self.y = y
        self.bg = SeaBackground()
        self.cells = [[() for x in range(0, WIDTH)] for y in range(0, HEIGHT)]

        self.ship_imgs = []
        self.visible_ships = dict()
        self.preproccess_ship_imgs()

    def preproccess_ship_imgs(self):
        ships_img_files = ["1k.png", "2k.png", "3k.png", "4k.png"]
        ships_objs = []
        for ship_size, img_name in enumerate(ships_img_files, 1):
            img = pygame.image.load(f'images/{img_name}')
            img = pygame.transform.smoothscale(img, (TILE_WIDTH, TILE_HEIGHT * ship_size + (TILE_HEIGHT // 2)))
            ships_objs.append(img)
        self.ship_imgs = ships_objs

    def update_from_matrix(self, matrix: list):
        for y, row in enumerate(matrix):
            for x, col_row in enumerate(row):
                if self.cells[y][x] != matrix[y][x]:
                    self.cells[y][x] = matrix[y][x]

    def add_visible_ship(self, ship: Ship):
        ship_x, ship_y = ship.part_positions[0]
        horizontal = ship.horizontal
        self.visible_ships[(ship_x, ship_y, horizontal)] = ShipImage(self.ship_imgs[ship.length - 1])

    def draw(self, surface):
        # Background
        self.bg.draw(self.surf)

        # Ships
        for key, ship in self.visible_ships.items():
            ship_x, ship_y, horizontal = key
            ship_surf = ship
            ship_surf.draw(self.surf, ship_x, ship_y, horizontal)

        # Overlay
        for y, row in enumerate(self.cells):
            for x, col_row in enumerate(row):
                self.redraw_cell(x, y, col_row)
        surface.blit(self.surf, (self.x, self.y))

    def redraw_cell(self, x_cell, y_cell, value=None):
        sprite = None
        if value == FieldStatus.SHOT:
            sprite = MissedCell()
        elif value == FieldStatus.SHIP_DESTROYED:
            sprite = BlownCell()

        if sprite: sprite.draw(self.surf, x_cell, y_cell)

    def cell_selected(self, x, y):
        if self.x <= x < self.x + self.surf.get_width() and self.y <= y < self.y + self.surf.get_height():
            x, y = x - self.x, y - self.y
            return x // TILE_WIDTH, y // TILE_HEIGHT
        else:
            return None


class ShipImage():
    def __init__(self, image):
        self.image = image
        self.surf = self.image
        self.spin = None

    def get_image(self, horizontal=True):
        if horizontal and self.spin is None:
            self.spin = choice([-90, 90])
        elif not horizontal and self.spin is None:
            self.spin = choice([0, 180])

        if self.spin != 0:
            return pygame.transform.rotate(self.image, self.spin)
        else:
            return self.image

    def draw(self, surface, x_cell, y_cell, horizontal=True):
        img = self.get_image(horizontal=horizontal)
        if horizontal:
            x_offset, y_offset = TILE_WIDTH // 4, 0
        else:
            x_offset, y_offset = 0, TILE_HEIGHT // 4

        position = (TILE_WIDTH * x_cell) - x_offset, (TILE_HEIGHT * y_cell) - y_offset
        surface.blit(img, position)


s = pygame.display.set_mode(((10 * TILE_WIDTH) * 2 + 30, (10 * TILE_HEIGHT) + 20))
s.fill((255, 255, 255))
pygame.display.set_caption('Water')

FPS = 120
FramePerSec = pygame.time.Clock()

from field_status import FieldStatus
from player.computer_player import ComputerPlayer
from player.player import HumanPlayer
from field import join_multiline_strings

from time import sleep


class HumanPlayer_interactive(HumanPlayer):
    def select_shoot_coord(self):
        global bo_enemy

        coords_missing = True
        events = pygame.event.get()

        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                player_cell = bo_enemy.cell_selected(x, y)
                coords_missing = False

        if coords_missing:
            # FramePerSec.tick(FPS)
            return None
        else:
            self.last_shot_coords = player_cell
            return self.last_shot_coords


def game_logic():
    me = HumanPlayer_interactive("Kostia")
    # me = ComputerPlayer("Kostia")
    enemy = ComputerPlayer("Vassia")

    me.generate_field()
    global bo_player
    bo_player = BattleOverlay(10, 10)
    bo_player.update_from_matrix(me.field.field)
    [bo_player.add_visible_ship(ship) for ship in me.get_ships()]
    bo_player.draw(s)

    enemy.generate_field()
    global bo_enemy
    bo_enemy = BattleOverlay((10 * TILE_WIDTH) + 20, 10)
    bo_enemy.update_from_matrix(enemy.field.field)
    bo_enemy.draw(s)

    gameboard_positions = [me, enemy]
    screen_fields = [bo_player, bo_enemy]

    gameboard_positions[0].select_target(gameboard_positions[1])
    gameboard_positions[1].select_target(gameboard_positions[0])

    game_running = True
    turn = 0
    yield
    print(f"Game starts!")
    # While my or enemy has any ship
    while game_running:
        print(f"Turn #{turn}")
        current_player, enemy_player = gameboard_positions
        current_screen, enemy_screen = screen_fields
        # if isinstance(current_player, HumanPlayer):
        if True:
            print(
                join_multiline_strings(
                    current_player.field.repr_field(),
                    # enemy_player.field.repr_field(enemy_player.field.enemy_view)
                    enemy_player.field.repr_field(enemy_player.field.field)
                )

            )

        print(f"{current_player.name.capitalize()} shoots.")
        coords = None
        while coords is None:
            coords = current_player.select_shoot_coord()
            if coords:
                x, y = coords
            yield
        yield
        shoot_result = current_player.fire(x, y)
        current_screen.update_from_matrix(current_player.field.field)
        enemy_screen.update_from_matrix(enemy_player.field.field)

        current_screen.draw(s)
        enemy_screen.draw(s)
        yield
        print(f"{current_player.name.capitalize()} shoots at {(x, y)}")

        if shoot_result == FieldStatus.SHOT:
            print(f"{current_player.name.capitalize()} missed.")
            current_player.last_shot_successful = False
            gameboard_positions.reverse()
            screen_fields.reverse()
            yield
        else:
            print(f"{current_player.name.capitalize()} hits {enemy_player.name.capitalize()}'s ship.")
            current_player.last_shot_successful = True
            if current_player is me:
                [enemy_screen.add_visible_ship(ship) for ship in enemy_player.field.destroyed_ships]
                bo_enemy.draw(s)
                pygame.display.update()
            yield
            if enemy_player.ships_left() == 0:
                print(f"{enemy_player.name.capitalize()} has no more ships.")
                print(f"{current_player.name.capitalize()} is winner!")
                game_running = False
                yield
            else:
                print(f"{enemy_player.ships_left()} ships remain. {current_player.name.capitalize()} shoots again.")
                yield
        if isinstance(current_player, ComputerPlayer):
            # sleep(0.5)
            pass
        turn += 1
        yield

    sleep(3)
    pygame.quit()
    sys.exit()


gl = game_logic()

while True:
    next(gl)
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            player_cell = bo_player.cell_selected(x, y)
            enemy_cell = bo_enemy.cell_selected(x, y)
            if player_cell: print("Player", *player_cell)
            if enemy_cell:  print("Enemy", *enemy_cell)

    pygame.display.update()
    FramePerSec.tick(FPS)
