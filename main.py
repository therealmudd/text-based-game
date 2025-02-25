from classes import *

# Setup
world = World()
world.generate_map(game_map, game_map_key)

player = Player(world)
player.set_location()
world.player = player


def run_game_loop():
    # Game loop
    console.print("You wake up on the shore of what seems to be a deserted island.")

    while True:
        input_string = console.input("\nWhat will you do next? \n> ")
        
        console.gray_out()
        world.parse_input(input_string)
        world.update()


if __name__ == "__main__":
    run_game_loop()