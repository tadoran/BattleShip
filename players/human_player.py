import pygame
from pygame.constants import MOUSEBUTTONDOWN

from field_status import FieldStatus
from players.abstract_player import PlayerABS
from settings import TILE_WIDTH, TILE_HEIGHT
from visual_logic.sprites import scope


class HumanPlayer_interactive(PlayerABS):
    def select_shoot_coord(self):
        coords_missing = True
        events = pygame.event.get()
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                coords_missing = False


        x, y = pygame.mouse.get_pos()
        player_cell = self.enemy_visual_field.cell_selected(x, y)
        if player_cell is not None:
                x_selected, y_selected = player_cell
                self.enemy_visual_field.draw(self.visual_surface)
                if self.target.field.enemy_view[y_selected][x_selected] != FieldStatus.EMPTY:
                    coords_missing = True
                else:
                    (
                        self.visual_surface
                            .blit(
                                    scope,
                                    (self.enemy_visual_field.x + (x_selected * TILE_WIDTH),
                                     self.enemy_visual_field.y + (y_selected * TILE_HEIGHT)
                                    )
                                  )
                    )
                    pygame.display.flip()
        else:
            pass

        if not coords_missing:
            self.last_shot_coords = player_cell
            return self.last_shot_coords