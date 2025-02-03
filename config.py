game_map = '''\
wwwwwwwwwwwww
wbbbbbbbbbbbw
wbbbbbbffbbbw
wbbffffcfbbbw
wbbffcfffbbbw
wbbffffffbbbw
wbbbbbbffbbbw
wbbbbbbbbbbbw
wwwwwwwwwwwww'''

game_map_key = {
    "w": "water",
    "b": "beach",
    "f": "forest",
    "c": "cave"
}

locations = {
    "beach": {
        "description": "You are on the beach.",
        "details": "You see the ocean and the shore.",
        "items": [
            "water",
            "rock",
            "sand",
            "fish",
            "stone",
            "stick"
        ],
    },
    "forest": {
        "description": "You are in the forest.",
        "details": "You see trees in all directions.",
        "items": [
            "rock",
            "wood",
            "stick",
            "leaf",
            "dirt",
            "grass"
        ]
    },
    "cave": {
        "description": "You are in the cave.",
        "details": "You see a stone and some ores.",
        "items": [
            "stone",
            "iron ore",
        ]
    },
    "water": {
        "description": "You are in the water.",
        "details": "You see some fish swimming.",
        "items": [
            "fish",
            "rock"
        ]
    }
}

'''
Edibility:
-3 = can't be eaten
-2 = poisonous
-1 = should not eat raw
0  = should eat raw
1  = should eat cooked
2 = better cooked but can be eaten raw
3 = can be drunk
'''

items = {
    "water": {"needs": "bucket", "edibility": 3.5},
    "rock": {},
    "sand": {},
    "fish": {"edibility": 2.5},
    "stone": {},
    "stick": {},
    "wood": {"needs": "axe"},
    "leaf": {"edibility": -2.15},
    "dirt": {},
    "grass": {"edibility": -2.1},
    "axe": {"stacks": False},
    "long stick": {},
    "vine": {},
    "bucket": {"stacks": False},
    "iron ore": {"needs": "pickaxe"},
}

combinations = {
    "stick+stone": "axe",
    "stick+stick": "long stick",
    "grass+grass": "vine",
    "stone+stone": "bucket"
}

statuses = {
    "poisioned": {"threshold": 1},
    "eaten": {"threshold": 2},
    "hungry": {"threshold": 3},
    "thirsty": {"threshold": 2},
    "drank": {"threshold": 2}
}