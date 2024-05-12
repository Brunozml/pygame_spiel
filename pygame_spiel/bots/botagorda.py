from open_spiel.python import rl_environment
import pyspiel
from open_spiel.python.games.block_dominoes import _ACTIONS


class BotaGorda(pyspiel.Bot):
    """Dominoes bot that uses largest tiles. Only supports block domiones"""

    def __init__(
            self,
            game,
            player_id
    ):
        pyspiel.Bot.__init__(self)
        self._player_id = player_id
        # if game == "python_block_dominoes": # game is a pyspiel.Game, not a str
        #     self._game = game
        # else:
        #     raise ValueError("Invalid game: %s. BotaGorda only supports dominoes" % game)
    
    def restart_at(self, state):
        pass

    def player_id(self):
        return self._player_id
    
    def step(self, state):
        """Returns bot's action at given state."""
        legal_action_indexes = state.legal_actions(self._player_id)
        legal_actions = [_ACTIONS[i] for i in legal_action_indexes]
        if not legal_actions: # No legal actions; im not sure if this is the correct way to handle this
            return None
            # Find the action with the highest sum of edges in its tile
        best_action = max(legal_actions, key=lambda a: sum(a.tile))
        # Return the index of the best action
        return _ACTIONS.index(best_action)

    
