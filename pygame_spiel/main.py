#!/usr/bin/env python

import pygame
import pygame_menu
from pygame_menu import themes

from pygame_spiel.games.settings import GAMES_BOTS
from pygame_spiel.games.factory import GameFactory
from pygame_spiel.menu import Menu


def select_game(game, index):
    pass


def pygame_spiel():
    menu = Menu()
    menu.display()
    game_name = menu.get_selected_game()
    bot_type = menu.get_selected_opponent()

    player_id = 0 # this doesn't really seem to matter

    assert (
        bot_type in GAMES_BOTS[game_name].keys()
    ), f"""Bot type {bot_type} not available for game {game_name}. List of 
        available bots: {list(GAMES_BOTS[game_name].keys())}"""

    # # # THIS DEFINITELY DOES SOMETHING 
    game = GameFactory.get_game(game_name, current_player=player_id)
    game.set_bots(
        bot1_type="human",
        bot1_params=None,
        bot2_type=bot_type,
        bot2_params=None,
    )
    # game.set_bots(
    #     bot1_type=bot_type,
    #     bot1_params=None,
    #     bot2_type="human",
    #     bot2_params=None,
    # )


    done = False
    clock = pygame.time.Clock()

    # Main loop
    while not done:
        clock.tick(10)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                done = True

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        game.play(mouse_pos=mouse_pos, mouse_pressed=mouse_pressed)

        pygame.display.flip()