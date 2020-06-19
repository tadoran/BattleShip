from field_status import FieldStatus, ShipStatus, ShipClass


class Ship:
    def __init__(self, start_segment: tuple, length: int, is_horizontal: bool, field):
        self.field = field
        self.part_positions = [start_segment]
        self.surroundings = []
        self.length = length
        self.horizontal = is_horizontal

        self.set_position()
        self.get_surroundings()

    def __repr__(self):
        horizontality = "S"
        if self.length > 1:
            horizontality = "Horizontal s" if self.horizontal else "Vertical s"
        return f"{horizontality}hip({self.length}) at {self.part_positions}"

    def validate_surroundings(self):
        return sum([self.field.field[y][x] for (x, y) in self.surroundings]) == 0

    def apply_field_mask(self, field_mask):
        for position in self.part_positions + self.surroundings:
            x, y = position
            field_mask[y][x] = FieldStatus.OCCUPIED

    def get_position(self):
        x1, y1 = self.part_positions[0]
        if self.horizontal:
            search_points = {xn: (xn, y1) for xn in range(x1 + 1, min(x1 + 4, self.field.width))}
        else:
            search_points = {yn: (x1, yn) for yn in range(y1 + 1, min(y1 + 4, self.field.height))}

        for point in sorted(search_points):
            x, y = search_points[point]
            if self.field[y][x] == 1:
                self.part_positions.append((x, y))
                self.length += 1
            else:
                break

    def set_position(self):
        start_x, start_y = self.part_positions[0]
        if self.horizontal:
            if start_x + self.length > self.field.width:
                raise IndexError("Ship is out of x boundaries")
            for x in range(start_x, start_x + self.length):
                self.field.field[start_y][x] = FieldStatus.SHIP_FIXED
                if x > start_x: self.part_positions.append((x, start_y))
        else:
            if start_y + self.length > self.field.width:
                raise IndexError("Ship is out of y boundaries")
            for y in range(start_y, start_y + self.length):
                self.field.field[y][start_x] = FieldStatus.SHIP_FIXED
                if y > start_y: self.part_positions.append((start_x, y))

    def is_segment_damaged(self, i: int) -> bool:
        x, y = self.part_positions[i]
        if self.field.coord_status(x, y) == FieldStatus.SHIP_DESTROYED:
            return True
        return False

    def count_damaged_segments(self):
        damaged_count = 0
        for i, _ in enumerate(self.part_positions):
            if self.is_segment_damaged(i):
                damaged_count += 1
        return damaged_count

    def mark_damaged(self, x, y):
        pass

    def get_surroundings(self):
        surroundings = set()
        for position in self.part_positions:
            surroundings.update(self.get_neighbours(position))
        self.surroundings = list(surroundings.difference(self.part_positions))
        return self.surroundings

    def get_neighbours(self, position) -> list:
        x, y = position
        min_pos = 0
        max_pos_x = self.field.width
        max_pos_y = self.field.height

        return [
            (xn, yn)
            for xn in range(max(x - 1, min_pos), min(x + 2, max_pos_x))
            for yn in range(max(y - 1, min_pos), min(y + 2, max_pos_y))
            if not ((xn == x) and (yn == y))
        ]

    def status(self):
        damaged_segments_count = self.count_damaged_segments()
        if damaged_segments_count == 0:
            return ShipStatus.FIXED
        elif 0 < damaged_segments_count < self.length:
            return ShipStatus.DAMAGED
        else:
            return ShipStatus.DESTROYED

    def classname(self):
        return ShipClass(self.length).name


# def validate_battlefield(field):
#     # write your magic here
#
#     possible_dict = {4: {"max_count": 1, "items": []},
#                      3: {"max_count": 2, "items": []},
#                      2: {"max_count": 3, "items": []},
#                      1: {"max_count": 4, "items": []}
#                      }
#
#     # all_ships = []
#     field_mask = [[0 for _ in range(0, battleField.width + 1)] for __ in range(0, battleField.height + 1)]
#     for y in range(0, len(field)):
#         for x in range(0, len(field)):
#             # print(f"{(x,y)}")
#             if field_mask[y][x] == 0:
#                 # print(f"{(x,y)} not masked")
#                 if field[y][x] == 1:
#                     print(f"{(x, y)} has a ship start entry")
#                     a_ship = Ship((x, y), field)
#                     print(f"Ship of size {a_ship.length} is located in {a_ship.part_positions}")
#                     if not a_ship.validate_surroundings:
#                         print(f"Ship's surroundings are not empty {a_ship.surroundings}. RETURN FALSE")
#                         return False
#                     else:
#                         print(f"Ship's surroundings are empty. OK.")
#                     print(f"Applying mask of the ship to global mask")
#                     a_ship.apply_field_mask(field_mask)
#                     print("Applied:")
#                     repr_field(field_mask)
#                     possible_dict[a_ship.length]["items"].append(a_ship)
#             else:
#                 pass
#
#     for ship_class, details in possible_dict.items():
#         if details["max_count"] != len(details["items"]):
#             print(
#                 f'There should be {details["max_count"]} ships of length {ship_class}, {len(details["items"])} are available')
#             return False
#
#     pprint(possible_dict)
#     print()
#     return True


from pprint import pprint
from copy import deepcopy


def repr_field(field):
    bf2 = deepcopy(field)
    for yi, y in enumerate(bf2):
        for xi, x in enumerate(y):
            bf2[yi][xi] = " " + str(bf2[yi][xi]) + " "
    horizontal_line = ([f"-{x}-" for x in range(0, 11)])
    print("   " + str(horizontal_line))
    for y, row in enumerate(bf2):
        print(f"{y:2} {row}")


# if __name__ == "__main__":
#     battleField = [[1, 0, 0, 0, 0, 1, 1, 0, 0, 0],
#                    [1, 0, 1, 0, 0, 0, 0, 0, 1, 0],
#                    [1, 0, 1, 0, 1, 1, 1, 0, 1, 0],
#                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
#                    [0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
#                    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
#                    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
#                    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
#                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
#
#     print(validate_battlefield(battleField))
