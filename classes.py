import re
import os
from console import Console
from config import locations, game_map, game_map_key, items, combinations
from typing import Any
import math

console = Console()

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def from_direction(position, direction: tuple[int, int]):
        return Position(position.x + direction[0], position.y + direction[1])
    
    def xy(self):
        return self.x, self.y


class Item:
    def __init__(self, item_name, item_config):
        self.name = item_name
        self.item_config = item_config
        self.needs = item_config.get("needs", None)
        self.edibility = item_config.get("edibility", -3)
        self.count = 1
        
    def can_collect(self, items):
        if self.needs == None:
            return True
        for item_name in items:
            if item_name == self.needs:
                return True
        return False
    
    def copy(self):
        return Item(self.name, self.item_config)


class Location:
    def __init__(self, location_name, location_config, item_config):
        self.name = location_name
        self.description = location_config["description"]
        self.details = location_config["details"]
        self.items: list[Item] = []
        self._setup_items(location_config["items"], item_config)

    def _setup_items(self, items, item_config):
        for item in items:
            self.items.append(Item(item, item_config[item]))

    def find_item(self, item_name):
        for item in self.items:
            if item.name == item_name:
                return item


class Status:
    def __init__(self, status_name, duration=1, degree=1):
        self.name = status_name
        self.duration = duration
        self.degree = degree

    def update(self, duration=None, degree=None):
        self.duration = duration or self.duration
        self.degree = degree or self.degree


class Inventory:
    def __init__(self):
        self.items: dict[str, Item] = {}
    
    def add(self, item: Item):
        if item.name in self.items:
            self.items[item.name].count += 1
        else:
            self.items[item.name] = item

    def find_item(self, item_name):
        return self.items.get(item_name, None)
    
    def drop(self, item_name, drop_all=False):
        if self.items[item_name].count > 1 and not drop_all:
            self.items[item_name].count -= 1
        else:
            del self.items[item_name]


class Actions:
    def __init__(self, player):
        self.actions = {}
        self._set_actions()
        self.player: Player = player

    def _set_actions(self):
        self.actions = {
            r"^look around$": self.do_look_around,
            # r"^go to (\w+)$": self.do_go_to,
            r"^(go|walk|travel) (\w+)$": self.do_travel,
            r"^gather (\w+)( from (\w+))?$": self.do_gather,
            r"^inventory$": self.do_inventory,
            r"^combine (\w+) (with|and) (\w+)$": self.do_combine,
            r"^(eat|drink|consume) (\w+)$": self.do_consume,
            r"^drop (all )?(\w+)$": self.do_drop,
        }

    def find_action(self, command):
        for pattern, action in self.actions.items():
            match = re.match(pattern, command)
            if match:
                return action, match.groups()
        return None, None

    def do_look_around(self, *args):
        console.print(self.player.location.description)
        console.print(self.player.location.details)

    def do_travel(self, *args):
        directions = {
            "north": (-1, 0),
            "south": (1, 0),
            "east": (0, 1),
            "west": (0, -1),
        }
        direction = args[1]
        if direction not in directions:
            console.print("I can't go that way.")
            return

        new_pos = Position.from_direction(self.player.position, directions[direction])
        if not self.player.world.map.is_valid_position(new_pos):
            console.print("I can't go that way.")
            return
        self.player.position = new_pos
        self.player.location = self.player.world.map.location_at_position(new_pos)
        console.print(self.player.location.description)

    def do_go_to(self, *args):
        location_name = args[0]
        location = self.player.world.find_location(location_name)
        if not location:
            console.print("I can't go there.")
            return
        self.player.location = location
        console.print(self.player.location.description)

    def do_gather(self, *args):
        target_item = self.player.location.find_item(args[0])
        if target_item is None:
            console.print(f"There's no {args[0]} here.")
        elif target_item.can_collect(self.player.inventory.items):
            self.player.inventory.add(target_item.copy())
            console.print(f"You gather a {args[0]}")
        else:
            console.print(f"I can't collect {args[0]} without {target_item.needs}.")

    def do_inventory(self, *args):
        if self.player.inventory.items:
            console.print("You have the following:")
            for item_name, item in self.player.inventory.items.items():
                console.print(f"{item_name} x{item.count}")
        else:
            console.print("You have nothing.")

    def do_drop(self, *args):
        drop_all = args[0] == "all "
        target_item = self.player.inventory.find_item(args[1])

        if target_item is None:
            console.print(f"You don't have {args[1]}.")
            return
        
        self.player.inventory.drop(target_item.name, drop_all)
        console.print(f"You dropped {'all ' * drop_all}your {args[1]}")

        pass

    def do_consume(self, *args):
        verb = args[0]
        target_item = self.player.inventory.find_item(args[1])
        if target_item is None:
            console.print(f"You don't have {args[1]}.")
            return
        
        degree, edibility = math.modf(target_item.edibility)
        degree, edibility = abs(degree), int(edibility)
        if target_item.edibility == -3:
            console.print(f"You can't consume {args[1]}.")
        elif target_item.edibility in [-2, -1]:
            if verb in ['eat', 'consume']:
                console.print(f"You've eaten {args[1]} and feel weird.")
                self.player.inventory.drop(target_item.name)
                self.player.add_status("poisioned", duration=5, degree=degree)
            else:
                console.print(f"You can't drink {args[1]}.")
        elif target_item.edibility in [0, 1, 2]:
            if verb in ['eat', 'consume']:
                console.print(f"You've eaten {args[1]}.")
                self.player.inventory.drop(target_item.name)
                self.player.add_status("eaten", duration=10, degree=degree)
            else:
                console.print(f"You can't drink {args[1]}.")
        elif target_item.edibility == 3:
            if verb in ['drink', 'consume']:
                console.print(f"You've drunk {args[1]}.")
                self.player.inventory.drop(target_item.name)
                self.player.add_status("drank", duration=6, degree=degree)
            else:
                console.print(f"You can't eat {args[1]}.")

    def do_combine(self, *args):
        item_name1, item_name2 = args[0], args[2]
        item_1 = self.player.inventory.find_item(item_name1)
        item_2 = self.player.inventory.find_item(item_name2)

        if item_1 is None:
            console.print(f"You do not have {item_name1}")
            return
        if item_2 is None:
            console.print(f"You do not have {item_name2}")

        combination = "+".join(sorted([item_name1, item_name2]))
        result = combinations.get(combination, None)

        if result is not None:
            console.print(f"You have created {result}")
            self.player.inventory.drop(item_name1)
            self.player.inventory.drop(item_name2)
            self.player.inventory.add(Item(result, item_config=items))

class Player:
    def __init__(self, world):
        self.position: Position = Position(7, 6)
        self.actions: Actions = Actions(self)
        self.world: World = world
        self.location: Location = None
        self.inventory: Inventory = Inventory()
        self.statuses: dict[str, Status] = {}
        self.experience = 0

    def set_location(self):
        self.location = self.world.map.location_at_position(self.position)

    def add_status(self, status_name, duration=1, degree=1):
        if status_name in self.statuses:
            self.statuses[status_name].update(duration=duration, degree=degree)
            # TODO: detect when status has reach it's threshold
        else:
            self.statuses[status_name] = Status(status_name, duration, degree)

    def update(self):
        for status_name, status in self.statuses.items():
            status.duration -= 1
            if status.duration <= 0:
                del self.statuses[status_name]


class Map:
    def __init__(self, data, key):
        self.data: list[list[str]] = data
        self.key = key
        self.width = len(self.data[0])
        self.height = len(self.data)
        self.locations = []
        self.add_locations(locations, items)
    
    def add_locations(self, locations: dict[str, str], items: dict[str, Any]):
        for location_name, location_config in locations.items():
            new_location = Location(location_name, location_config, items)
            self.locations.append(new_location)

    def is_valid_position(self, position: Position):
        x, y = position.xy()
        return 0 <= x <= self.width and 0 <= y <= self.height
    
    def find_location(self, name):
        for location in self.locations:
            if location.name == name:
                return location
        return None
    
    def location_at_position(self, position: Position):
        x, y = position.xy()
        return self.find_location(self.key[self.data[y][x]])

class World:
    def __init__(self):
        self.locations: list[Location] = []
        self.player: Player = None
        self.map: Map = None

    def generate_map(self, game_map_string: str, game_map_key):
        map_data = [list(line) for line in game_map_string.split("\n")]
        self.map = Map(map_data, game_map_key)
            
    def parse_input(self, input_string: str):
        console.print(">", input_string)
        command = input_string.lower().strip()

        action, args = self.player.actions.find_action(command)
        if action:
            action(*args)
            return
        else: 
            console.print("I don't understand that.")

    def update(self):
        self.player.update()