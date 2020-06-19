from random import choice

from field_status import FieldStatus, ShipStatus
from ship import Ship
from settings import *

class Field:
    # Possible ships on a field. key = ship length, max_count = ships on field, items = Ship objects
    def __init__(self, field=[]):
        self.width = WIDTH
        self.height = HEIGHT
        self.possible_dict = {4: {"max_count": 1, "items": []},
                              3: {"max_count": 2, "items": []},
                              2: {"max_count": 3, "items": []},
                              1: {"max_count": 4, "items": []}}

        self.field_mask = self.generate_prefilled("-")
        self.enemy_view = self.generate_prefilled(FieldStatus.EMPTY)
        self.ship_mask = self.generate_prefilled(None)
        if len(field) == 0:
            field = self.generate_prefilled(FieldStatus.EMPTY)
        self.field = field
        self.destroyed_ships = []

    def validate(self):
        pass

    def generate_prefilled(self, filler=FieldStatus.EMPTY):
        return [[filler] * self.width for _ in range(0, self.height)]

    def append_ship_by_start_segment(self, start_segment: tuple, length: int, is_horizontal: bool):
        ship = Ship(start_segment, length, is_horizontal, self)
        self.apply_ship(ship)

    def apply_ship(self, ship: Ship):
        ship.apply_field_mask(self.field_mask)
        self.possible_dict[ship.length]["items"].append(ship)
        for x, y in ship.part_positions:
            self.ship_mask[y][x] = ship

    def coord_status(self, x, y, field=[]):
        if len(field) == 0:
            field = self.field
        return field[y][x]

    def get_destroyed_ships(self):
        return self.destroyed_ships

    def register_shot(self, x, y):
        if self.coord_status(x, y, self.ship_mask):
            self.field[y][x] = FieldStatus.SHIP_DESTROYED
            self.coord_status(x, y, self.ship_mask).mark_damaged(x, y)
            self.enemy_view[y][x] = FieldStatus.SHIP_DESTROYED
            ship = self.coord_status(x, y, self.ship_mask)
            print(f"{ship} is damaged! There are {ship.count_damaged_segments()} damaged segments.")
            if ship.status() == ShipStatus.DESTROYED:
                self.destroyed_ships.append(ship)
                for x, y in ship.get_surroundings():
                    self.enemy_view[y][x] = FieldStatus.SHOT
                    self.field[y][x] = FieldStatus.SHOT
            return ship.status()
        else:
            self.field[y][x] = FieldStatus.SHOT
            self.enemy_view[y][x] = FieldStatus.SHOT
            return FieldStatus.SHOT

    def repr_field_plain(self):
        txt = ""
        txt += "\n".join(["\t".join([str(el.value) for el in line]) for line in self.field])
        return txt

    def repr_field(self, field=[], include_titles=True, coord_str_width: int = 3, sep: str = " "):
        txt = "\n"
        if len(field) == 0:
            field = self.field

        def line_sep():
            extra_chars = 0
            if include_titles: extra_chars = coord_str_width
            return "-" * (coord_str_width * len(field) + extra_chars) + "\n"

        if include_titles:
            txt += line_sep()
            txt += sep * coord_str_width
            for i in range(0, len(field)):
                txt += str(i).center(coord_str_width, sep)
            txt += "\n"
            txt += line_sep()

        for i, row in enumerate(field, 0):
            if include_titles:
                txt += str(i).center(coord_str_width - 1, sep) + "|"
            for col_row in row:
                if hasattr(col_row, "value"):
                    txt += str(col_row.value).center(coord_str_width, sep)
                else:
                    txt += str(col_row).center(coord_str_width, sep)
            if i < len(field): txt += "\n"

        if include_titles:
            txt += line_sep()
        return txt

    def occupied_region_is_clear(self, position, length, horizontality) -> bool:
        x, y = position
        min_pos = 0
        max_x, max_y = self.width, self.height

        if horizontality:
            if x + length > max_x:
                return False
            neighbours = [
                (xn, yn)
                for xn in range(max(x, min_pos), min(x + length + 1, max_x))
                for yn in range(max(y, min_pos), min(y + 1, max_y))
            ]

        else:
            if y + length > max_y:
                return False
            neighbours = [
                (xn, yn)
                for xn in range(max(x, min_pos), min(x + 1, max_x))
                for yn in range(max(y, min_pos), min(y + length + 1, max_y))
            ]

        for (xn, yn) in neighbours:
            if self.coord_status(xn, yn, self.field_mask) == FieldStatus.OCCUPIED:
                return False
        return True

    def generate_ships_randomly(self):
        for length, params in self.possible_dict.items():
            count, items = params["max_count"], params["items"]
            for n in range(len(self.possible_dict[length]["items"]), count):

                possible_entry_points = [
                    ((x, y), horizontality)
                    for y in range(0, self.height)
                    for x in range(0, self.width)
                    for horizontality in (True, False)
                    if self.occupied_region_is_clear((x, y), length, horizontality)
                ]
                if len(possible_entry_points) == 0:
                    print("No locations")
                    possible_entry_points = [
                        ((x, y), horizontality)
                        for y in range(0, self.height)
                        for x in range(0, self.width)
                        for horizontality in (True, False)
                        if self.occupied_region_is_clear((x, y), length, horizontality)
                    ]
                s = choice(possible_entry_points)
                ship = Ship(s[0], length, s[1], self)
                self.apply_ship(ship)


def join_multiline_strings(*args, sep=" ", sep_length=5) -> str:
    str_max_lens = []
    split_txt = [[]] * len(args)
    lines_count = 0
    for i, txt in enumerate(args):
        strings = [line for line in txt.split("\n")]
        split_txt[i].append(strings)
        lines_count = max(lines_count, len(strings))
        str_max_lens.append(max(len(line) for line in strings))
    txt = ""

    for n in range(0, lines_count):
        for i, line in enumerate(split_txt):
            txt += line[i][n].ljust(str_max_lens[i] + sep_length, sep)
        txt += "\n"
    return txt


if __name__ == "__main__":
    a = Field()
    a.generate_ships_randomly()
    b = Field()
    b.generate_ships_randomly()
    print(join_multiline_strings(a.repr_field(a.field), b.repr_field(b.field)))
    exl = a.repr_field_plain()
    print(exl)
