from field import Field
from field_status import ShipStatus


class PlayerABS:
    def __init__(self, name):
        self.self_visual_field = None
        self.enemy_visual_field = None
        self.visual_surface = None

        self.name = name
        self.field = Field()
        self.target = None
        self.last_shot_coords = ()
        self.last_successful_shot_coord = ()
        self.last_shot_successful = False
        self.has_wounded_enemy_ship = False

        self.generate_field()
        self.ships = self.get_ships()

    def generate_field(self):
        self.field.generate_ships_randomly()


    def get_ships(self):
        ships = []
        for ship_class in self.field.possible_dict.values():
            for ship in ship_class["items"]:
                ships.append(ship)

        return ships

    def validate_field(self):
        pass

    def select_target(self, target):
        self.target = target

    def select_shoot_coord(self):
        raise NotImplementedError

    def fire(self, x, y):
        return self.target.field.register_shot(x, y)

    def ships_left(self):
        return sum(1 for ship in self.ships if ship.status() != ShipStatus.DESTROYED)

    def ships_damaged(self):
        return sum(1 for ship in self.ships if ship.status() == ShipStatus.DAMAGED)

    def ships_destroyed(self):
        return sum(1 for ship in self.ships if ship.status() == ShipStatus.DESTROYED)