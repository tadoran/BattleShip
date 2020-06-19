import pygame
import sys
from pygame.locals import *

import sounds
from timer import Timer
from settings import *
from visual_logic.sprites import BattleOverlay, scope

pygame.init()


s = pygame.display.set_mode(((WIDTH * TILE_WIDTH) * 2 + 30, (HEIGHT * TILE_HEIGHT) + 20))
s.fill((255, 255, 255))
pygame.display.set_caption('Water')
pygame.mouse.set_cursor((8, 8), (4, 4), (24, 24, 24, 231, 231, 24, 24, 24), (0, 0, 0, 0, 0, 0, 0, 0))

FPS = 12
FramePerSec = pygame.time.Clock()


from field_status import FieldStatus
from player.computer_player import ComputerPlayer
from player.player import HumanPlayer


class HumanPlayer_interactive(HumanPlayer):
    def select_shoot_coord(self):
        coords_missing = True
        events = pygame.event.get()
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                coords_missing = False


        x, y = pygame.mouse.get_pos()
        player_cell = bo_enemy.cell_selected(x, y)
        if player_cell is not None:
                x_selected, y_selected = player_cell
                bo_enemy.draw(s)
                s.blit(scope, (bo_enemy.x + (x_selected * TILE_WIDTH), bo_enemy.y + (y_selected * TILE_HEIGHT)))
                pygame.display.flip()
        else:
            pygame.mouse.set_visible(True)

        if not coords_missing:
            self.last_shot_coords = player_cell
            return self.last_shot_coords


def game_logic():
    global no_action_before
    global bo_player
    bo_player = BattleOverlay(WIDTH, HEIGHT)
    bo_player.draw(s)

    global bo_enemy
    bo_enemy = BattleOverlay((WIDTH * TILE_WIDTH) + 20, HEIGHT)
    bo_enemy.draw(s)

    me = HumanPlayer_interactive("Kostia")
    # me = ComputerPlayer("Kostia")
    me.generate_field()
    [bo_player.add_visible_ship(ship) for ship in me.get_ships()]
    bo_player.update_from_matrix(me.field.field)
    enemy = ComputerPlayer("Vassia")
    enemy.generate_field()
    bo_enemy.update_from_matrix(enemy.field.field)


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

        print(f"{current_player.name.capitalize()} shoots.")
        coords = None
        while coords is None:
            coords = current_player.select_shoot_coord()
            if coords:
                x, y = coords
                sounds.cannon_sound()
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
            # yield
        else:
            print(f"{current_player.name.capitalize()} hits {enemy_player.name.capitalize()}'s ship.")
            current_player.last_shot_successful = True
            if current_player is me:
                [enemy_screen.add_visible_ship(ship) for ship in enemy_player.field.destroyed_ships]
                bo_enemy.draw(s)
                pygame.display.update()
            yield
            if enemy_player.ships_left() == 0:
                sounds.explosion_sound()
                print(f"{enemy_player.name.capitalize()} has no more ships.")
                print(f"{current_player.name.capitalize()} is winner!")
                game_running = False
                yield
            else:
                sounds.sunk_sound()
                print(f"{enemy_player.ships_left()} ships remain. {current_player.name.capitalize()} shoots again.")
                yield
        if isinstance(current_player, ComputerPlayer):
            no_action_before.start(0.1)
        FramePerSec.tick(FPS)
        turn += 1
        yield

    no_action_before.start(5)
    FramePerSec.tick(FPS)
    yield
    pygame.quit()
    sys.exit()

global no_action_before
no_action_before = Timer()

global bo_enemy
global bo_player
bo_player, bo_enemy = None, None
gl = game_logic()

while True:
    try:
        bo_player.draw(s)
        bo_enemy.draw(s)
    except:
        pass

    if no_action_before.check():
        next(gl)

    # print(FramePerSec.get_time(), no_action_before)
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)
