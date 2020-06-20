from random import choice

from field_status import FieldStatus
from players.abstract_player import PlayerABS


def get_neighbour_coordinates(x: int, y: int) -> list:
    return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]


def trim_to_boundaries(coords: list, lower_boundary: int = 0, max_x: int = 10, max_y: int = 10) -> list:
    filtered = {
        (x, y)
        for x, y in coords
        if lower_boundary <= x <= max_x and
           lower_boundary <= y <= max_y
    }
    return list(filtered)


class ComputerPlayer(PlayerABS):

    def select_shoot_coord(self):
        enemy_field = self.target.field.enemy_view
        possible_coords = []
        field_size_x = self.field.width
        field_size_y = self.field.height

        if self.last_shot_successful or self.has_wounded_enemy_ship:
            if self.last_shot_successful:
                self.last_successful_shot_coord = self.last_shot_coords

            last_shot_neighbours = trim_to_boundaries(
                get_neighbour_coordinates(
                    self.last_successful_shot_coord[0],
                    self.last_successful_shot_coord[1]
                ),
                0,
                field_size_x - 1,
                field_size_y - 1
            )
            neighbours_empty_coords_count = sum(
                1 for x, y in last_shot_neighbours
                if enemy_field[y][x] == FieldStatus.EMPTY
            )
            if neighbours_empty_coords_count == 0:
                self.has_wounded_enemy_ship = False
            else:
                self.has_wounded_enemy_ship = True
                # Coordinates that are shot ship
                entry_coords = [self.last_successful_shot_coord]

                # Repeat while new damaged neighbours are found
                entry_coords_extended = True  # Entering a cycle for the first time
                while entry_coords_extended:
                    entry_coords_extended = False  # If this is reloaded - we shall repeat
                    for x, y in entry_coords:
                        neighbours = trim_to_boundaries(
                            get_neighbour_coordinates(x, y),
                            0,
                            field_size_x - 1,
                            field_size_y - 1
                        )

                        for x_n, y_n in neighbours:
                            # New damaged neighbours
                            if (x_n, y_n) not in entry_coords and enemy_field[y_n][x_n] == FieldStatus.SHIP_DESTROYED:
                                entry_coords.append((x_n, y_n))
                                entry_coords_extended = True

                            # New empty neighbours
                            elif (x_n, y_n) not in possible_coords and enemy_field[y_n][x_n] == FieldStatus.EMPTY:
                                possible_coords.append((x_n, y_n))

                # Only new empty neighbours without duplicates
                possible_coords = list({coord for coord in possible_coords if coord not in entry_coords})

                if len(entry_coords) > 1:  # We have a ship with known direction, so we can filter out another direction
                    if entry_coords[0][0] - entry_coords[1][0] != 0:  # Horizontal
                        y_fix = entry_coords[0][1]
                        possible_coords = [(x, y) for x, y in possible_coords if y == y_fix]

                    else:  # Vertical
                        x_fix = entry_coords[0][0]
                        possible_coords = [(x, y) for x, y in possible_coords if x == x_fix]

                # If there are no empty surroundings - ship was destroyed. Resume to normal random strategy
                if len(possible_coords) == 0:
                    self.has_wounded_enemy_ship = False
                else:
                    self.last_shot_coords = choice(possible_coords)
                    return self.last_shot_coords

        # Normal random empty coordinate strategy
        for y, row in enumerate(enemy_field):
            for x, col_row in enumerate(row):
                if col_row not in [FieldStatus.SHOT, FieldStatus.SHIP_DESTROYED]:
                    possible_coords.append((x, y))
        self.last_shot_coords = choice(possible_coords)
        return self.last_shot_coords

