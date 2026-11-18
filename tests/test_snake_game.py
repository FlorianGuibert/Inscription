import random
import unittest

from snake_game import (
    MAX_AUTOMATIC_SPEED,
    MAX_MANUAL_SPEED,
    AutomaticPlayer,
    RIGHT,
    SnakeGame,
    _tick_delay,
)


class SnakeGameTests(unittest.TestCase):
    def test_snake_moves_one_cell_in_current_direction(self):
        game = SnakeGame(width=10, height=8)
        game.food = (0, 0)
        old_head = game.snake[0]

        game.step()

        self.assertEqual(game.snake[0], (old_head[0] + 1, old_head[1]))
        self.assertEqual(len(game.snake), 3)

    def test_eating_food_grows_snake_and_increases_score(self):
        game = SnakeGame(width=10, height=8)
        game.food = (game.snake[0][0] + 1, game.snake[0][1])

        game.step()

        self.assertEqual(len(game.snake), 4)
        self.assertEqual(game.score, 1)
        self.assertNotEqual(game.food, game.snake[0])

    def test_wall_collision_ends_game_without_moving(self):
        game = SnakeGame(width=5, height=5)
        game.snake = [(4, 2), (3, 2), (2, 2)]
        game.direction = RIGHT
        old_snake = list(game.snake)

        game.step()

        self.assertTrue(game.game_over)
        self.assertEqual(game.snake, old_snake)

    def test_self_collision_ends_game_without_moving(self):
        game = SnakeGame(width=8, height=8)
        game.snake = [(2, 2), (3, 2), (3, 3)]
        game.direction = RIGHT
        old_snake = list(game.snake)

        game.step()

        self.assertTrue(game.game_over)
        self.assertEqual(game.snake, old_snake)

    def test_automatic_player_fills_board_without_colliding(self):
        width = 24
        height = 12
        game = SnakeGame(width=width, height=height, rng=random.Random(1))
        player = AutomaticPlayer(game)
        player.start(game)

        for _ in range((width * height) ** 2):
            if game.game_over:
                break
            player.steer(game)
            game.step()

        self.assertTrue(game.won)
        self.assertEqual(game.score, width * height - 3)

    def test_tick_delay_changes_with_speed_in_both_modes(self):
        self.assertGreater(
            _tick_delay(1, automatic=False),
            _tick_delay(MAX_MANUAL_SPEED, automatic=False),
        )
        self.assertGreater(
            _tick_delay(1, automatic=True),
            _tick_delay(MAX_AUTOMATIC_SPEED, automatic=True),
        )
        self.assertLess(
            _tick_delay(MAX_AUTOMATIC_SPEED, automatic=True),
            _tick_delay(MAX_MANUAL_SPEED, automatic=False),
        )
        with self.assertRaises(ValueError):
            _tick_delay(0, automatic=False)
        with self.assertRaises(ValueError):
            _tick_delay(MAX_MANUAL_SPEED + 1, automatic=False)
        with self.assertRaises(ValueError):
            _tick_delay(MAX_AUTOMATIC_SPEED + 1, automatic=True)


if __name__ == "__main__":
    unittest.main()
