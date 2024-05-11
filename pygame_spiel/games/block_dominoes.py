import pygame
import typing as t
import math
import collections
import site
from pathlib import Path
import numpy as np
from pygame_spiel.games import base
from open_spiel.python.games.block_dominoes import Action, _ACTIONS, _ACTIONS_STR

LEFT_MOUSE_BUTTON = 0
HUMAN_PLAYER = 0

class Dominoes(base.Game):
    def __init__(self, name, current_player):
        super().__init__(name, current_player)

        self._text_font = pygame.font.SysFont("Arial", 20)
        self._space_between_tiles = 20
        self._selected_tile = None
        self._selected_tile_has_multiple_actions = False
        self.game_over = False
        self._arrow_positions = None # determined by the _draw_arrows() function
        self._selected_arrow = None

        # Load images

        # package_path = site.getsitepackages()[0]
        # for development-mode install, ho up one level to the 'pygame_spiel' directory
        project_root = Path(__file__).resolve().parents[2]
        self._edges = [
            pygame.image.load(
                project_root / "pygame_spiel" / "images" / "block_dominoes" / f"{i}.png").convert_alpha()
                  for i in range(7)
        ]
        self._arrows = [
            pygame.image.load(
                project_root / "pygame_spiel" / "images" / "block_dominoes" / f"left.png").convert_alpha(), 
            pygame.image.load(
                project_root / "pygame_spiel" / "images" / "block_dominoes" / f"right.png").convert_alpha()
        ]

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
        
    def _draw_text(self, text: str):
        """
        Draws a text on the board. Used to write whether the player has won or
        lost the game

        Parameters:
            text (str): text to visualize
        """
        text_col = (0, 0, 0)  # Set a default color for the text
        img = self._text_font.render(text, True, text_col)
        text_rect = img.get_rect(center=(self._screen.get_width() / 2, self._screen.get_height() * 0.7))
        self._screen.blit(img, text_rect)

    def _draw_arrows(self):
        """ Draws the arrows on the screen and sets the arrow positions attribute."""
        arrow_width = self._arrows[0].get_width()
        arrow_height = self._arrows[0].get_height()

        screen_width = self._screen.get_width()
        screen_height = self._screen.get_height()

        # Calculate the x-coordinate for the left arrow so that it's centered
        left_arrow_x = (screen_width - arrow_width * 2) / 3
        # Calculate the x-coordinate for the right arrow so that it's centered
        right_arrow_x = left_arrow_x * 2 + arrow_width

        # Calculate the y-coordinate for the arrows so that they're a bit up vertically
        arrow_y = screen_height / 2 - arrow_height

        self._arrow_positions = [(left_arrow_x, arrow_y), (right_arrow_x, arrow_y)]

        # Draw the arrows
        for i, (arrow_x, arrow_y) in enumerate(self._arrow_positions):
            if i == self._selected_arrow:
                pygame.draw.circle(self._screen, (255, 0, 0), 
                                   (arrow_x + self._arrows[0].get_width() // 2, 
                                    arrow_y + self._arrows[0].get_height() // 2), 
                                    min(self._arrows[0].get_height() // 2, 
                                        self._arrows[0].get_height() // 2))
            else:
                self._screen.blit(self._arrows[i], (arrow_x, arrow_y))

    def _draw_hand(self, player_id):
        """
        Draw the hand of a player on the screen.

        Args:
            player_id (int): The ID of the player whose hand is being drawn. 0 or 1
        """
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
    
    def _draw_board(self):
        board = self._get_board()
        tile_width = self._edges[0].get_width() * 2  # Assuming this is the width of a tile
        total_width = len(board) * tile_width  # Total width of all tiles

        # Calculate the starting x-coordinate so that the tiles are centered
        start_x = (self._screen.get_width() - total_width) / 2

        for i, tile in enumerate(board):
            x = start_x + i * tile_width
            y = (self._screen.get_height() - self._edges[0].get_height()) / 2
            self._draw_tile(tile, x, y)
    
    def _draw_game_state(self):
        self._screen.fill((255,255,255))  # Fill the screen with white
        self._draw_board()
        self._draw_hand(0)
        self._draw_hand(1)

        if self._selected_tile_has_multiple_actions:
            self._draw_arrows()

        if self.game_over:
            self._draw_game_over_text()

    def _draw_game_over_text(self):
        rewards = self._state.rewards()
        if rewards[0] == rewards[1]:
            self._draw_text("It's a draw!")
        elif rewards[0] > 0:
            self._draw_text(f"Human wins! {rewards[0]} points")
        elif rewards[1] > 0:
            self._draw_text(f"Player 2 wins! {rewards[1]} points")
    
    def _get_action_indices(self, tile):
        """Returns the indices of the actions in the list of actions."""
        state = self._state
        actions = []

        if not state.open_edges:  # first move
            actions.append(Action(0, tile, None))
        else:
            # can play on both edges
            if (tile[0] == state.open_edges[0] and tile[1] == state.open_edges[1]) or (tile[1] == state.open_edges[0] and tile[0] == state.open_edges[1]):
                actions.append(Action(0, tile, state.open_edges[1]))
                actions.append(Action(0, tile, state.open_edges[0]))
            # can play only on the left edge
            elif tile[0] == state.open_edges[0] or tile[1] == state.open_edges[0]:
                actions.append(Action(0, tile, state.open_edges[0]))
            # can play only on the right edge
            elif tile[0] == state.open_edges[1] or tile[1] == state.open_edges[1]:
                actions.append(Action(0, tile, state.open_edges[1]))

        # Convert actions to indices
        action_indices = [_ACTIONS_STR.index(str(action)) for action in actions]

        return action_indices

    # TODO: improve this function so that it doens't count the empty space between tiles as part of the tile
    def _get_tile_at_pos(self, pos):
        """
        Get the tile at the given position.
        Returns:
            tile (object): The tile object at the given position, or None if no tile is found.
        """
        tile_width = self._edges[0].get_width() * 2  # assuming all tiles have the same width
        space_between_tiles = 20  # adjust this value to your liking

        # Calculate the y-coordinate of the hand
        hand_y = self._screen.get_height() - self._edges[0].get_height() - 10  # adjust this value to your liking

        # If the y-coordinate of the position is not within a certain range from the bottom of the screen, return None
        if not (hand_y <= pos[1] <= hand_y + self._edges[0].get_height()):
            return None

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
    
    def _get_board(self):
        """
        Returns the current state of the board.

        This function is used to retrieve the current state of the board, which is
        used to draw the board on the screen with PyGame.

        Returns:
            board (list): list of tile tuples containing the current state of the board
        """
        board = collections.deque()
        current_open_edges = None
        for action in self._state.actions_history:
        # check if action is played on an empty board
            if action.edge is None:
                board.append(action.tile)
                current_open_edges = list(action.tile)
            # check if action edge matches last played edge in the left or right
            elif action.edge == current_open_edges[0]:
                # invert the tile if the edge is on the right:
                tile = (action.tile[1], action.tile[0]) if action.tile[0] == current_open_edges[0] else action.tile
                board.appendleft(tile)

            elif action.edge == current_open_edges[1]:
                # invert the tile if the edge is on the left:
                tile = (action.tile[1], action.tile[0]) if action.tile[1] == current_open_edges[1] else action.tile
                board.append(tile)

            current_open_edges = board[0][0], board[-1][1]
        return board
    
    
    def _handle_mouse_press(self, mouse_pos, mouse_pressed):
        if mouse_pressed[LEFT_MOUSE_BUTTON]:
            # If a tile is selected and has multiple actions
            if self._selected_tile is not None and self._selected_tile_has_multiple_actions:
                for i, (arrow_x, arrow_y) in enumerate(self._arrow_positions):
                    # If the mouse click is within the area of the arrow
                    if arrow_x <= mouse_pos[0] <= arrow_x + self._arrows[0].get_width() and arrow_y <= mouse_pos[1] <= arrow_y + self._arrows[0].get_height():
                        # Set the selected arrow
                        self._selected_arrow = i
                        return
            # If the mouse click is on a tile
            tile = self._get_tile_at_pos(mouse_pos)
            if tile is not None:
                self._selected_tile = tile
            else:
                # If the mouse click is somewhere else on the screen
                self._selected_tile = None
                self._selected_arrow = None
    
    def _handle_tile_selection(self):
        if self.game_over: # game is over
            return
        actions = self._get_action_indices(self._selected_tile)
        print("actions: ", actions)
        if not actions:
            print("No legal actions")
            return
        elif len(actions) == 1:
            action = actions[0]
            self._state.apply_action(action)
            self._selected_tile = None
            self._selected_arrow = None
            self._selected_tile_has_multiple_actions = False
        elif len(actions) == 2:  # can play on both edges
            self._selected_tile_has_multiple_actions = True
            if self._selected_arrow is not None:
                action = actions[self._selected_arrow]
                self._state.apply_action(action)
                self._selected_tile = None
                self._selected_arrow = None
                self._selected_tile_has_multiple_actions = False
            print("can play on both sides!")


    def _update_state(self, mouse_pos, mouse_pressed):
        if self._state.is_chance_node():
            outcomes = self._state.chance_outcomes()
            action_list, prob_list = zip(*outcomes)
            outcome = np.random.choice(action_list, p=prob_list)
            print(f"Chance chose: {outcome} ({self._state.action_to_string(outcome)})")
            print(self._state.hands)
            self._state.apply_action(outcome)
        else:
            self._handle_mouse_press(mouse_pos, mouse_pressed)
            if self._current_player == HUMAN_PLAYER and (self._selected_tile is not None):
                print(f"Selected tile: {self._selected_tile}, ")
                self._handle_tile_selection()
            elif self._current_player == 1:
                action = self._bots[1].step(self._state)
                self._state.apply_action(action)
                print(f"bot applied action: {action}" if action is not None else "No action applied")

        self._current_player = self._state.current_player()
        self._state_string = self._state.to_string()

        if self._current_player == -4:  # game is over
            self.game_over = True


    def play(self, mouse_pos, mouse_pressed):
        if self.game_over:
            self._draw_game_over_text()
            return

        self._update_state(mouse_pos, mouse_pressed)
        self._draw_game_state()

