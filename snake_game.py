"""A small, standard-library Snake game in a separate window."""

import random
import time
from typing import Dict, List, Optional, Tuple


Point = Tuple[int, int]
Direction = Tuple[int, int]

UP: Direction = (0, -1)
DOWN: Direction = (0, 1)
LEFT: Direction = (-1, 0)
RIGHT: Direction = (1, 0)

MIN_SPEED = 1
MAX_MANUAL_SPEED = 20
MAX_AUTOMATIC_SPEED = 100
DEFAULT_SPEED = 10


class SnakeGame:
    """Game state and rules, independent of terminal input and rendering."""

    def __init__(
        self, width: int = 24, height: int = 12, rng: Optional[random.Random] = None
    ) -> None:
        if width < 5 or height < 5:
            raise ValueError("The board must be at least 5 cells wide and high.")

        self.width = width
        self.height = height
        self._rng = rng or random.Random()
        center = (width // 2, height // 2)
        self.snake = [center, (center[0] - 1, center[1]), (center[0] - 2, center[1])]
        self.direction = RIGHT
        self.score = 0
        self.game_over = False
        self.won = False
        self.food: Optional[Point] = None
        self._place_food()

    def set_direction(self, direction: Direction) -> None:
        """Change direction unless it would reverse into the snake."""
        if direction not in (UP, DOWN, LEFT, RIGHT):
            raise ValueError("Direction must be UP, DOWN, LEFT, or RIGHT.")
        if direction != (-self.direction[0], -self.direction[1]):
            self.direction = direction

    def step(self) -> None:
        """Advance the snake by one cell, updating score or game-over state."""
        if self.game_over:
            return

        head_x, head_y = self.snake[0]
        next_head = (head_x + self.direction[0], head_y + self.direction[1])
        eating = next_head == self.food

        if (
            next_head[0] < 0
            or next_head[0] >= self.width
            or next_head[1] < 0
            or next_head[1] >= self.height
        ):
            self.game_over = True
            return

        body = self.snake if eating else self.snake[:-1]
        if next_head in body:
            self.game_over = True
            return

        self.snake.insert(0, next_head)
        if eating:
            self.score += 1
            self._place_food()
            if self.food is None:
                self.game_over = True
                self.won = True
        else:
            self.snake.pop()

    def _place_food(self) -> None:
        occupied = set(self.snake)
        available = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in occupied
        ]
        self.food = self._rng.choice(available) if available else None


def _hamiltonian_cycle(width: int, height: int) -> List[Point]:
    if height % 2:
        if width % 2:
            raise ValueError(
                "Automatic mode requires at least one even board dimension."
            )
        return [(y, x) for x, y in _hamiltonian_cycle(height, width)]

    cycle = [(x, 0) for x in range(width)]
    for y in range(1, height):
        xs = range(width - 1, 0, -1) if y % 2 else range(1, width)
        cycle.extend((x, y) for x in xs)
    cycle.append((0, height - 1))
    cycle.extend((0, y) for y in range(height - 2, 0, -1))
    return cycle


class AutomaticPlayer:
    """Follow a safe board-wide cycle to collect every food item."""

    def __init__(self, game: SnakeGame) -> None:
        self.cycle = _hamiltonian_cycle(game.width, game.height)
        self._next_point: Dict[Point, Point] = {
            point: self.cycle[(index + 1) % len(self.cycle)]
            for index, point in enumerate(self.cycle)
        }

    def start(self, game: SnakeGame) -> None:
        """Reset the game with the snake aligned to the cycle."""
        game.snake = [self.cycle[0], self.cycle[-1], self.cycle[-2]]
        game.direction = (
            self.cycle[1][0] - self.cycle[0][0],
            self.cycle[1][1] - self.cycle[0][1],
        )
        game.score = 0
        game.game_over = False
        game.won = False
        game._place_food()

    def steer(self, game: SnakeGame) -> None:
        next_head = self._next_point[game.snake[0]]
        game.set_direction(
            (next_head[0] - game.snake[0][0], next_head[1] - game.snake[0][1])
        )


def _tick_delay(speed: int, automatic: bool) -> int:
    max_speed = MAX_AUTOMATIC_SPEED if automatic else MAX_MANUAL_SPEED
    if not MIN_SPEED <= speed <= max_speed:
        raise ValueError(
            "Speed must be between {} and {}.".format(MIN_SPEED, max_speed)
        )
    base_delay = 15 if automatic else 120
    return max(1, int(base_delay * DEFAULT_SPEED / speed))


def main() -> None:
    import tkinter as tk

    game = SnakeGame()
    automatic_player: Optional[AutomaticPlayer] = None
    speed = DEFAULT_SPEED
    game_started_at = time.monotonic()
    score_history: List[Tuple[float, int]] = [(0.0, 0)]
    chart_window: Optional[tk.Toplevel] = None
    cell_size = 24
    status_height = 42
    window = tk.Tk()
    window.title("Snake")
    window.resizable(False, False)
    tick_after_id: Optional[str] = None
    speed_display = tk.StringVar(window, value="Speed: {:.1f}x".format(speed / 10))

    canvas = tk.Canvas(
        window,
        width=game.width * cell_size,
        height=game.height * cell_size + status_height,
        background="#18212b",
        highlightthickness=0,
    )
    canvas.pack()

    controls = {
        "w": UP,
        "s": DOWN,
        "a": LEFT,
        "d": RIGHT,
        "up": UP,
        "down": DOWN,
        "left": LEFT,
        "right": RIGHT,
    }

    def handle_key(event: tk.Event) -> None:
        key = event.keysym.lower()
        if key == "q":
            window.destroy()
        elif key in controls:
            game.set_direction(controls[key])

    def draw() -> None:
        canvas.delete("all")
        for x, y in game.snake:
            x1, y1 = x * cell_size, y * cell_size
            color = "#7ee787" if (x, y) == game.snake[0] else "#3fb950"
            canvas.create_rectangle(
                x1 + 1,
                y1 + 1,
                x1 + cell_size - 1,
                y1 + cell_size - 1,
                fill=color,
                outline="",
            )

        if game.food is not None:
            food_x, food_y = game.food
            inset = cell_size // 4
            canvas.create_oval(
                food_x * cell_size + inset,
                food_y * cell_size + inset,
                (food_x + 1) * cell_size - inset,
                (food_y + 1) * cell_size - inset,
                fill="#ff7b72",
                outline="",
            )

        controls_text = (
            "Score: {}    Automatic mode    Quit: Q".format(game.score)
            if automatic_player is not None
            else "Score: {}    Move: WASD / arrows    Quit: Q".format(game.score)
        )
        canvas.create_text(
            12,
            game.height * cell_size + status_height // 2,
            anchor="w",
            fill="#f0f6fc",
            font=("Segoe UI", 11),
            text=controls_text,
        )

        if game.game_over:
            message = (
                "You filled the board!"
                if game.won
                else "Game over!"
            )
            canvas.create_rectangle(
                0,
                game.height * cell_size // 2 - 36,
                game.width * cell_size,
                game.height * cell_size // 2 + 36,
                fill="#18212b",
                outline="",
            )
            canvas.create_text(
                game.width * cell_size // 2,
                game.height * cell_size // 2,
                fill="#f0f6fc",
                font=("Segoe UI", 18, "bold"),
                text="{}  Final score: {}".format(message, game.score),
            )

    def close_chart() -> None:
        nonlocal chart_window
        if chart_window is not None:
            if chart_window.winfo_exists():
                chart_window.destroy()
            chart_window = None

    def reset_run_history() -> None:
        nonlocal game_started_at
        close_chart()
        game_started_at = time.monotonic()
        score_history.clear()
        score_history.append((0.0, 0))

    def show_score_chart() -> None:
        nonlocal chart_window
        close_chart()
        chart_window = tk.Toplevel(window)
        chart_window.title("Snake - Balls eaten over time")

        chart_width = 640
        chart_height = 420
        chart = tk.Canvas(
            chart_window,
            width=chart_width,
            height=chart_height,
            background="#18212b",
            highlightthickness=0,
        )
        chart.pack()

        left, right, top, bottom = 72, chart_width - 24, 48, chart_height - 64
        duration = max(score_history[-1][0], 1.0)
        max_balls = max(game.score, 1)
        y_step = max(1, (max_balls + 4) // 5)
        y_ticks = list(range(0, max_balls + 1, y_step))
        if y_ticks[-1] != max_balls:
            y_ticks.append(max_balls)

        chart.create_text(
            chart_width // 2,
            20,
            fill="#f0f6fc",
            font=("Segoe UI", 14, "bold"),
            text="Balls eaten over time",
        )

        for value in y_ticks:
            y = bottom - (value / max_balls) * (bottom - top)
            chart.create_line(left, y, right, y, fill="#34404d")
            chart.create_text(
                left - 10,
                y,
                anchor="e",
                fill="#f0f6fc",
                text=str(value),
            )

        for index in range(6):
            elapsed = duration * index / 5
            x = left + (right - left) * index / 5
            chart.create_line(x, top, x, bottom, fill="#34404d")
            chart.create_text(
                x,
                bottom + 16,
                fill="#f0f6fc",
                text="{:.1f}".format(elapsed),
            )

        chart.create_line(left, top, left, bottom, fill="#f0f6fc", width=2)
        chart.create_line(left, bottom, right, bottom, fill="#f0f6fc", width=2)
        chart.create_text(
            (left + right) // 2,
            chart_height - 16,
            fill="#f0f6fc",
            text="Time (seconds)",
        )
        chart.create_text(
            18,
            (top + bottom) // 2,
            angle=90,
            fill="#f0f6fc",
            text="Balls eaten",
        )

        points = []
        for elapsed, balls in score_history:
            x = left + (elapsed / duration) * (right - left)
            y = bottom - (balls / max_balls) * (bottom - top)
            points.extend((x, y))
        if len(points) >= 4:
            chart.create_line(*points, fill="#7ee787", width=3)
        else:
            x, y = points
            chart.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#7ee787", outline="")

    def tick() -> None:
        nonlocal tick_after_id
        tick_after_id = None
        if not game.game_over:
            if automatic_player is not None:
                automatic_player.steer(game)
            previous_score = game.score
            game.step()
            if game.score > previous_score:
                score_history.append((time.monotonic() - game_started_at, game.score))
            draw()
            if game.game_over:
                elapsed = time.monotonic() - game_started_at
                if elapsed > score_history[-1][0]:
                    score_history.append((elapsed, game.score))
                show_score_chart()
            else:
                tick_after_id = window.after(
                    _tick_delay(speed, automatic_player is not None), tick
                )

    def adjust_speed(change: int) -> None:
        nonlocal speed, tick_after_id
        max_speed = (
            MAX_AUTOMATIC_SPEED
            if automatic_player is not None
            else MAX_MANUAL_SPEED
        )
        speed = max(MIN_SPEED, min(max_speed, speed + change))
        speed_display.set("Speed: {:.1f}x".format(speed / 10))
        if tick_after_id is not None:
            window.after_cancel(tick_after_id)
            tick_after_id = window.after(
                _tick_delay(speed, automatic_player is not None), tick
            )

    def restart() -> None:
        nonlocal game, automatic_player, speed, tick_after_id
        if tick_after_id is not None:
            window.after_cancel(tick_after_id)
        game = SnakeGame(width=game.width, height=game.height)
        automatic_player = None
        speed = min(speed, MAX_MANUAL_SPEED)
        speed_display.set("Speed: {:.1f}x".format(speed / 10))
        reset_run_history()
        draw()
        tick_after_id = window.after(_tick_delay(speed, False), tick)

    def start_automatic() -> None:
        nonlocal game, automatic_player, tick_after_id
        if tick_after_id is not None:
            window.after_cancel(tick_after_id)
        game = SnakeGame(width=game.width, height=game.height)
        automatic_player = AutomaticPlayer(game)
        automatic_player.start(game)
        reset_run_history()
        draw()
        tick_after_id = window.after(_tick_delay(speed, True), tick)

    window.bind("<KeyPress>", handle_key)
    window.focus_set()
    button_bar = tk.Frame(window)
    button_bar.pack(pady=8)
    tk.Button(button_bar, text="Restart Game", command=restart).pack(
        side=tk.LEFT, padx=4
    )
    tk.Button(button_bar, text="Automatic", command=start_automatic).pack(
        side=tk.LEFT, padx=4
    )
    tk.Button(button_bar, text="Slower", command=lambda: adjust_speed(-1)).pack(
        side=tk.LEFT, padx=4
    )
    tk.Label(button_bar, textvariable=speed_display, width=11).pack(
        side=tk.LEFT, padx=4
    )
    tk.Button(button_bar, text="Faster", command=lambda: adjust_speed(1)).pack(
        side=tk.LEFT, padx=4
    )
    draw()
    tick_after_id = window.after(_tick_delay(speed, False), tick)
    window.mainloop()


if __name__ == "__main__":
    main()
