from itertools import cycle
from random import choice

import pygame

from field_status import FieldStatus
from settings import TILE_WIDTH, TILE_HEIGHT, WIDTH, HEIGHT
from ship import Ship


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


scope = pygame.image.load("./images/scope.png")
scope = pygame.transform.scale(scope, (TILE_WIDTH,TILE_HEIGHT))

point = pygame.image.load("./images/point.png")
point = pygame.transform.scale(point, (TILE_WIDTH,TILE_HEIGHT))
