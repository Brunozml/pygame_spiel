import pygame
import typing as t
import math
import site
from pathlib import Path
import numpy as np

from pygame_spiel.games import base

class Dominoes(base.Game):
    def __init__(self, name, current_player):
        super().__init__(name, current_player)

        self._player_color = "b" if self._current_player == 0 else "w"
        self._n_rows, self._n_cols, self._n_directions = 8, 8, 6
        # package_path = site.getsitepackages()[0]
        # for development-mode install, ho up one level to the 'pygame_spiel' directory
        project_root = Path(__file__).resolve().parents[2]
        self._text_font = pygame.font.SysFont("Arial", 20)

        # Load images
        self._background = pygame.image.load(
            project_root / "pygame_spiel/images/breakthrough/chess_board.png"
        ).convert_alpha()

        self._edges = [
            pygame.image.load(
                project_root / "pygame_spiel" / "images" / "block_dominoes" / f"{i}.png").convert_alpha()
                  for i in range(7)
        ]
        self._space_between_tiles = 20
        self._selected_tile = None

        self._pawn_white = pygame.image.load(
            project_root / "pygame_spiel/images/breakthrough/pawn_white.png"
        ).convert_alpha()
        self._pawn_white_selected = pygame.image.load(
            project_root
            / "pygame_spiel/images/breakthrough/pawn_white_selected.png"
        ).convert_alpha()
        self._pawn_black = pygame.image.load(
            project_root / "pygame_spiel/images/breakthrough/pawn_black.png"
        ).convert_alpha()

        self._pawn_white = pygame.transform.scale(self._pawn_white, (95, 95))
        self._pawn_white_selected = pygame.transform.scale(
            self._pawn_white_selected, (95, 95)
        )
        self._pawn_black = pygame.transform.scale(self._pawn_black, (95, 95))

        self._selected_row, self._selected_col = None, None

        # Next two lists are from (lines 36-40):
        # https://github.com/google-deepmind/open_spiel/blob/efa004d8c5f5088224e49fdc198c5d74b6b600d0/open_spiel/games/breakthrough.cc#L36
        self._k_dir_row_offsets = [1, 1, 1, -1, -1, -1]
        self._k_dir_col_offsets = [-1, 0, 1, -1, 0, 1]

    def _draw_board(self):
        """
        Draws the board on the screen.

        This function is used to draw the board on the screen. It's called at each iteration
        to update the screen with the current state of the game.
        """

        # Fill the screen with green
        self._screen.fill((3,250,10))

        # print the board

        if self._state.is_chance_node():
            outcomes = self._state.chance_outcomes()
            action_list, prob_list = zip(*outcomes)
            outcome = np.random.choice(action_list, p=prob_list)
            print(f"Chance chose: {outcome} ({self._state.action_to_string(outcome)})")
            print(self._state.hands)
            self._state.apply_action(outcome)

        # Get the hands of the players
        hand1 = self._state.hands[0]
        hand2 = self._state.hands[1]
        # Render the text
        text_surface1 = self._text_font.render(f"{hand1}", True, (255, 255, 255))
        text_surface2 = self._text_font.render(f"{hand2}", True, (255, 255, 255))

        screen_height = self._screen.get_height()
        self._screen.blit(text_surface1, (0, screen_height - text_surface1.get_height()))
        self._screen.blit(text_surface2, (0, 0))

        # draw the played hands
    
    def _draw_hand(self, player_id):
        hand = self._state.hands[player_id]
        tile_width = self._edges[0].get_width() * 2  # assuming all tiles have the same width

        # Calculate the total width of the hand
        hand_width = len(hand) * (tile_width + self._space_between_tiles) - self._space_between_tiles

        # Calculate the starting x-coordinate to center the hand
        start_x = (self._screen.get_width() - hand_width) // 2

        # Calculate the y-coordinate based on the player_id
        if player_id == 0:
            y = self._screen.get_height() - self._edges[0].get_height()  # bottom of the screen
        else:
            y = 0  # top of the screen

            # Draw the tiles
        for i, tile in enumerate(hand):
            x = start_x + i * (tile_width + self._space_between_tiles)
            self._draw_tile(tile, x, y)

    
    def _draw_tile(self, tile, x, y):
        """
        Draws a tile horizonatlly on the screen.

        This function is used to draw a tile on the screen. It's called at each iteration
        to update the screen with the current state of the game.

        Parameters:
            tile (int): tile to draw
            x (int): x coordinate
            y (int): y coordinate
        """
        if tile == self._selected_tile:
            # Draw a blue blob
            pygame.draw.circle(self._screen, (0, 0, 255), (x + self._edges[0].get_width() // 2, y + self._edges[0].get_height() // 2), self._edges[0].get_width() // 2)
        else:
            # Select the images for the tile's values
            image1 = self._edges[int(tile[0])]
            image2 = self._edges[int(tile[1])]

            # Draw the images
            self._screen.blit(image1, (x, y))
            self._screen.blit(image2, (x + image1.get_width(), y))

    # TODO: improve this function so that it doens't count the empty space between tiles as part of the tile
    def _get_tile_at_pos(self, pos):
        tile_width = self._edges[0].get_width() * 2  # assuming all tiles have the same width
        space_between_tiles = 20  # adjust this value to your liking

        # Calculate the x-coordinate of the first tile in the hand
        hand = self._state.hands[self._current_player]
        hand_width = len(hand) * (tile_width + space_between_tiles) - space_between_tiles
        start_x = (self._screen.get_width() - hand_width) // 2

        # Calculate the index of the tile based on the x-coordinate of the position
        index = (pos[0] - start_x) // (tile_width + space_between_tiles) # + space_between_tiles)
        if 0 <= index < len(hand):
            return hand[index]
        else:
            return None
        
    def _convert_mouse_position_to_grid(
        self, mouse_pos: t.Tuple[int, int]
    ) -> t.Tuple[int, int]:
        """
        Maps mouse x/y position to cell's row/column coordinates on the board.

        This function is used to retrieve the coordinates of the mouse position, which
        is used to determine whether the mouse's arrow is touching a selected token or
        empty cell.

        Parameters:
            mouse_pos (tuple): contains the x/y position of the mouse (0: X, 1: Y)

        Returns:
            row (int): cell's row
            col (int): cell's column
        """

        offset = 246
        cell_size = 84
        border_size = 6

        row = math.floor(
            (mouse_pos[1] - offset + border_size) / (cell_size + border_size)
        )
        col = math.floor(
            (mouse_pos[0] - offset + border_size) / (cell_size + border_size)
        )
        return row, col

    def _get_token_by_position(self, row: int, col: int) -> int:
        """
        Returns the token position given the tokens row and column.

        This function is used to simplify the mapping of the token position
        in the grid. Open_spiel uses an integer number to represent the position
        of a token in the grid, but it's sometimes simpler to represent the position
        as a row/column coordinate.

        Parameters:
            row (int): Token's row
            col (int): Token's column

        Returns:
            res (int): token's position id
        """

        return row * 10 + col + 1

    def _get_direction(
        self, selected_pawn_col: int, dest_col: int, player_color: str
    ) -> int:
        """
        Returns the direction of a selected token given a destination column.

        The output of this function is used to convert a token's move into an action id. This
        is because the implementation of breakthrough in open_spiel represents each possible
        action with a unique integer id.

        Parameters:
            selected_pawn_col (int): token's column
            dest_col (int): destination column of the token
            player_color (str): player's color

        Returns:
            dir (int): token's direction (value between 0 and 5)
        """

        directions = {"b": [0, 1, 2], "w": [3, 4, 5]}

        if selected_pawn_col - dest_col == 1:
            dir = directions[player_color][0]
        elif selected_pawn_col - dest_col == 0:
            dir = directions[player_color][1]
        elif selected_pawn_col - dest_col == -1:
            dir = directions[player_color][2]
        else:
            dir = 7  # Invalid direction
        return dir

    def _unrank_action_mixed_base(self, action: int) -> t.List[int]:
        """
        Converts the action value to a the position and values used to get the position and direction of the pawn.

        Example: _unrank_action_mixed_base(2) = [1, 0, 1, 0]
        Example: _unrank_action_mixed_base(100) = [1, 0, 2, 0]

        This function is currently not used, but it's useful for debugging purposes, which is why is kept in this file.
        This function is a copy of:
        https://github.com/google-deepmind/open_spiel/blob/efa004d8c5f5088224e49fdc198c5d74b6b600d0/open_spiel/spiel_utils.cc#L69

        Parameters:
            action (int): player's action.

        Returns:
            digits (list): list containing 4 values
        """

        action_bases = [self._n_rows, self._n_rows, self._n_directions, 2]
        digits = [0] * len(action_bases)
        for i in range(len(action_bases) - 1, -1, -1):
            digits[i] = action % action_bases[i]
            action //= action_bases[i]
        return digits

    def _action_to_string(self, action: int) -> str:
        """
        Converts the action value to a string representing start and end position.

        Example: _action_to_string(2) = a8a7
        Example: _action_to_string(100) = a7b6

        This function is currently not used, but it's useful for debugging purposes, which is why is kept in this file.
        This function is a copy of:
        https://github.com/google-deepmind/open_spiel/blob/efa004d8c5f5088224e49fdc198c5d74b6b600d0/open_spiel/games/breakthrough.cc#L196

        Parameters:
            action (int): player's action.

        Returns:
            digits (str): start/end position of the player
        """

        values = self._unrank_action_mixed_base(action)
        r1, c1 = values[0], values[1]
        dir = values[2]
        capture = values[3] == 1
        r2 = r1 + self._k_dir_row_offsets[dir]
        c2 = c1 + self._k_dir_col_offsets[dir]

        def col_label(col: int) -> str:
            return chr(ord("a") + col)

        def row_label(row: int) -> str:
            return chr(ord("1") + self._n_rows - 1 - row)

        action_string = ""
        action_string += col_label(c1)
        action_string += row_label(r1)
        action_string += col_label(c2)
        action_string += row_label(r2)
        action_string += "*" if capture else ""

        return action_string

    def _from_action_string_to_int(
        self,
        selected_pawn_row: int,
        selected_pawn_col: int,
        dest_row: int,
        dest_col: int,
        token: "str",
    ) -> int:
        """
        Returns the action id given token's actual and destination position.

        This function returns the numerical action id given a selected token's
        current and destination position. This is because the implementation of breakthrough
        in open_spiel represents each possible action with a unique integer id, which is uniquely
        linked to the token's current and destination position.

        To better understand the logic in this function, please refer to the following links in open_spiel
        which have been used as inspiration:
        * https://github.com/deepmind/open_spiel/blob/efa004d8c5f5088224e49fdc198c5d74b6b600d0/open_spiel/spiel_utils.cc#L50-L64
        * https://github.com/deepmind/open_spiel/blob/efa004d8c5f5088224e49fdc198c5d74b6b600d0/open_spiel/games/breakthrough.cc#L243

        Parameters:
            selected_pawn_row (int): current token's row
            selected_pawn_col (int): current token's column
            dest_row (int): destination token's row
            dest_col (int): destination token's column
            token (str): token in the destination cell (can be ".", "w" or "b")

        Returns:
            action (int): breakthrough's unique action id
        """

        if abs(selected_pawn_row - dest_row) > 1:
            # Pawns cannot jump for more than 1 step
            return None

        action_bases = [self._n_rows, self._n_rows, self._n_directions, 2]

        dir = self._get_direction(selected_pawn_col, dest_col, self._player_color)

        # Black diagonal directions are 0 and 2. White diagonal directiosn are 3 and 5
        diagonal_dir = True if dir in [0, 2, 3, 5] else False
        if dir == 7:
            # Pawns can only move in front or direct diagonal positions
            return None

        if self._player_color == "b" and token == "w" and diagonal_dir:
            capture = 1
        elif self._player_color == "w" and token == "b" and diagonal_dir:
            capture = 1
        else:
            capture = 0

        digits = [selected_pawn_row, selected_pawn_col, dir, capture]

        action = 0
        one_plus_max = 1
        for i in range(len(action_bases) - 1, -1, -1):
            action += digits[i] * one_plus_max
            one_plus_max *= action_bases[i]

        return action

    def _get_coordinates_by_position(self, row: int, col: int) -> t.Tuple[int, int]:
        """
        Maps token's row/column coordinates to real coordinates in 2D plan (pygame screen).

        This function is used to retrieve the coordinates of a token on the screen,
        which are used to draw the token on the screen with PyGame.

        Parameters:
            row (int): Token's row
            col (int): Token's column

        Returns:
            x (int): token's X position on the screen
            y (int): token's Y position on the screen
        """

        offset = 240
        unit = 89
        x = col * unit + offset
        y = row * unit + offset
        return x, y

    def play(self, mouse_pos, mouse_pressed):
        """
        Abstact interface of the function play(). At each iteration, it requires the mouse position
        and state (which button was pressed, if any).
        
        Parameters:
            mouse_pos (tuple): Position of the mouse (X,Y coordinates)
            mouse_pressed (tuple): 1 if the i-th button is pressed (i.e. right click left click)
        """
        state = self._state
        if mouse_pressed[0]:  # left mouse button
            self._selected_tile = self._get_tile_at_pos(mouse_pos)
        else:
            self._selected_tile = None
        if (
            (self._current_player == 0 and self._player_color == "b") # human player
            or (self._current_player == 1 and self._player_color == "w")
        ) and (mouse_pressed[0]):
            row, col = self._convert_mouse_position_to_grid(mouse_pos)
            token = self._state_string[self._get_token_by_position(row, col)]
            if self._selected_row is None and token == self._player_color:
                self._selected_row, self._selected_col = row, col
            elif self._selected_row is not None and token == self._player_color:
                self._selected_row, self._selected_col = None, None
            elif self._selected_row is not None and token != self._player_color:
                # A pawn has been selected. If no other pawn is chosen, do not change assignment.
                action = self._from_action_string_to_int(
                    self._selected_row, self._selected_col, row, col, token
                )
                if action is not None and action in self._state.legal_actions():
                    self._state.apply_action(action)
                    self._bots[1].inform_action(
                        self._state, self._current_player, action
                    )
                    self._selected_row, self._selected_col = None, None
        elif (self._current_player == 1 and self._player_color == "b") or (
            self._current_player == 0 and self._player_color == "w"
        ):
            action = self._bots[1].step(self._state)
            self._state.apply_action(action)

        self._current_player = self._state.current_player()
        self._state_string = self._state.to_string()

        # Visualization

        # background
        # self._screen.blit(self._background, (0, 0))
        # Fill the screen with green
        self._screen.fill((3,250,10))

        # print the board
        self._draw_board()

        self._draw_tile((6,5), 500, 500)
        self._draw_hand(0)
        # if state.is_chance_node():
        #     outcomes = state.chance_outcomes()
        #     action_list, prob_list = zip(*outcomes)
        #     outcome = np.random.choice(action_list, p=prob_list)
        #     print(f"Chance chose: {outcome} ({state.action_to_string(outcome)})")
        #     print(self._state.hands)
        #     state.apply_action(outcome)

        # # Get the hands of the players
        # hand1 = state.hands[0]
        # hand2 = state.hands[1]
        # # Render the text
        # text_surface1 = self._text_font.render(f"{hand1}", True, (255, 255, 255))  # Change the color as needed
        # text_surface2 = self._text_font.render(f"{hand2}", True, (255, 255, 255))  # Change the color as needed
        # # Get the screen height
        # screen_height = self._screen.get_height()
        # # Blit the text surface onto the screen at the bottom
        # self._screen.blit(text_surface1, (0, screen_height - text_surface1.get_height()))
        # self._screen.blit(text_surface2, (0, 0))
        # # show the hand of the players
        # # for player in range(2):
        # #     hand = state.legal_actions(player)


        # for row in range(8):
        #     for col in range(8):
        #         token = self._state_string[self._get_token_by_position(row, col)]
        #         x, y = self._get_coordinates_by_position(row, col)

        #         if token == "b":
        #             if row == self._selected_row and col == self._selected_col:
        #                 self._screen.blit(self._pawn_white_selected, (x, y))
        #             else:
        #                 self._screen.blit(self._pawn_black, (x, y))
        #         elif token == "w":
        #             if row == self._selected_row and col == self._selected_col:
        #                 self._screen.blit(self._pawn_white_selected, (x, y))
        #             else:
        #                 self._screen.blit(self._pawn_white, (x, y))
