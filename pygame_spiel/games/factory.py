from pygame_spiel.games import *

DICT_GAMES = {"tic_tac_toe": "TicTacToe", "breakthrough": "Breakthrough", "python_block_dominoes": "Dominoes"}


class GameFactory:
    @classmethod
    def get_game(cls, name, current_player):
        assert (
            name in DICT_GAMES.keys()
        ), f"Game {name} not in list of available games: {DICT_GAMES.keys()}"
        Game_product = globals()[DICT_GAMES[name]]
        game = Game_product(name, current_player)
        return game
