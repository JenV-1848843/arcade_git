import arcade
import arcade.gui
from PIL import Image, ImageDraw

import random


# --- MODEL ---
class SnakeModel:
    COLS: int = 20
    ROWS: int = 20
    TICK_RATE: float = 1.0 / 8.0

    game_over: bool
    score: int
    high_score: int
    body: list[tuple[int, int]]
    food: tuple[int, int]

    def __init__(self):
        self.body = [(10, 10), (10, 9), (10, 8)]
        self.direction = (0,1)
        self.food = self.spawn_food()
        self.game_over = False
        self.score = 0
        self.high_score = 0
        self.tijd_verstreken = 0.0

    # Spawnen van een 'food' op een random plek. Voor makkelijkheid werken we met een dubbele
    # fo loop en daarna een random pakken van alle 'oke' vakjes
    def spawn_food(self) -> tuple[int, int]:
        vrije_vakjes = [(c, r) for c in range(self.COLS) for r in range(self.ROWS) if (c, r) not in self.body]
        return random.choice(vrije_vakjes)

    def tick(self, delta_time: float):
        if self.game_over:
            return

        self.tijd_verstreken += delta_time

        while self.tijd_verstreken >= self.TICK_RATE:
            self.update_game_logica()
            self.tijd_verstreken -= self.TICK_RATE

    def update_game_logica(self):
        head_col = self.body[0][0]
        head_row = self.body[0][1]

        d_col = self.direction[0]
        d_row = self.direction[1]

        new_head_col = head_col + d_col
        new_head_row = head_row + d_row
        new_head = (new_head_col, new_head_row)

        # Checken als het een valid nieuwe positie is
        if self.illegal_position(new_head_col, new_head_row):
            self.game_over = True
            self.update_high_score()
            return

        # Toevoegen aan body
        self.body.insert(0, new_head)

        # Als we NIET op een food plekje uitkwamen, dan doen we poppen van onze staart
        if new_head == self.food:
            self.food = self.spawn_food()
        else:
            self.body.pop()

        self.update_score()

    def illegal_position(self, x: int, y: int) -> bool:
        if not (0 <= x < self.COLS and 0 <= y < self.ROWS):
            return True
        elif (x, y) in self.body:
            return True
        return False

    def set_direction(self, new_direction: tuple[int, int]):
        # Hij mag niet in zichzelf terug bewegen
        if self.direction[0] != -new_direction[0] or self.direction[1] != -new_direction[1]:
            self.direction = new_direction

    def reset(self):
        self.body = [(10, 10), (10, 9), (10, 8)]
        self.direction = (0,1)
        self.food = self.spawn_food()
        self.game_over = False
        self.update_high_score()
        self.score = 0

    def update_score(self):
        self.score = self.get_score()

    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score

    def get_score(self) -> int:
        return len(self.body) - 3


# --- VIEW ---
class SnakeView:
    model: SnakeModel
    SIZE: int = 20

    def __init__(self, model):
        self.model = model
        self.sprites = arcade.SpriteList()

        self.offset_y = 100

        self.food_texture = self.make_texture("Red")
        self.snake_texture = self.make_texture("Green")
        self.border_texture = self.make_border_texture()

        self.refresh()

    def make_texture(self, color: str):
        image = Image.new('RGBA', (self.SIZE, self.SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        draw.rectangle([0, 0, self.SIZE - 2, self.SIZE - 2], fill=color)

        return arcade.Texture(image)

    def make_border_texture(self) -> arcade.Texture:
        totale_breedte = self.model.COLS * self.SIZE
        totale_hoogte = self.model.ROWS * self.SIZE

        image = Image.new('RGBA', (totale_breedte, totale_hoogte), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        draw.rectangle(
            [0, 0, totale_breedte - 1, totale_hoogte - 1],
            outline="white",
            width=4
        )

        return arcade.Texture(image)

    def refresh(self):
        self.sprites.clear()

        # Grid/border
        border_sprite = arcade.Sprite(self.border_texture)
        border_sprite.center_x = (self.model.COLS * self.SIZE) / 2
        border_sprite.center_y = (self.model.ROWS * self.SIZE) / 2 + self.offset_y
        self.sprites.append(border_sprite)

        # Food gedeelte
        food_coordinates = self.grid_to_coordinates(self.model.food[0], self.model.food[1])
        food_sprite = arcade.Sprite(self.food_texture)
        food_sprite.center_x = food_coordinates[0]
        food_sprite.center_y = food_coordinates[1]
        self.sprites.append(food_sprite)

        # Snake gedeelte
        for body_part in self.model.body:
            body_part_coordinates = self.grid_to_coordinates(body_part[0], body_part[1])
            snake_sprite = arcade.Sprite(self.snake_texture)
            snake_sprite.center_x = body_part_coordinates[0]
            snake_sprite.center_y = body_part_coordinates[1]
            self.sprites.append(snake_sprite)

    def grid_to_coordinates(self, col: int, row: int) -> tuple[float, float]:
        x = col * self.SIZE + (self.SIZE / 2)
        y = row * self.SIZE + (self.SIZE / 2) + self.offset_y
        return x, y

    def draw(self):
        self.sprites.draw()

        # Als het game over is, dan moet er game over komen staan in het groot
        if self.model.game_over:
            midden_x = (self.model.COLS * self.SIZE) / 2
            midden_y = (self.model.ROWS * self.SIZE) / 2 + self.offset_y

            arcade.draw_text("GAME OVER", midden_x, midden_y, arcade.color.WHITE, 30, anchor_x="center", anchor_y="center")

class UIView:
    manager: arcade.gui.UIManager
    restart_button: arcade.gui.UIFlatButton
    model: SnakeModel

    # Ik weet niet als je het wil hebben in SnakeView. Maar ik zie nu UIView als de
    # scenebuilder van java. Dus opzich vind ik het wel een logische plaats om zo statische
    # dingen als een teller ook hierbij te zetten?
    # Het enige wat ik dan wel een dubbele vind is om twee verschillende views een model mee te geven

    score_label: arcade.gui.UILabel
    highscore_label: arcade.gui.UILabel

    def __init__(self, snake_model: SnakeModel):
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.model = snake_model

        self.restart_button = arcade.gui.UIFlatButton(text="Restart", width=100, height=40)
        self.score_label = arcade.gui.UILabel(text="Score: 0", width=150, height=40, text_color=arcade.color.WHITE)
        self.highscore_label = arcade.gui.UILabel(text="High Score: 0", width=150, height=40, text_color=arcade.color.WHITE)

        self.setup_layout()

    def setup_layout(self):
        anchor = arcade.gui.UIAnchorLayout()

        hbox = arcade.gui.UIBoxLayout(vertical=False, space_between=50)
        hbox.add(self.score_label)
        hbox.add(self.restart_button)
        hbox.add(self.highscore_label)
        anchor.add(hbox, anchor_x="center_x", anchor_y="bottom", align_y=20)

        self.manager.add(anchor)

    def refresh(self):
        self.score_label.text = f"Score: {self.model.score}"
        self.highscore_label.text = f"High Score: {self.model.high_score}"

    def draw(self):
        self.manager.draw()

# --- CONTROLLER ---
class GameController(arcade.Window):
    my_model: SnakeModel
    my_view: SnakeView
    ui_view: UIView
    def __init__(self, model: SnakeModel, view: SnakeView, breedte: int, hoogte: int):
        super().__init__(width=breedte, height=hoogte, title="MVC Snake", pixel_perfect=True, resizable=False)
        arcade.set_background_color(arcade.color.BLACK)

        self.my_model = model
        self.my_view = view

        self.ui_view = UIView(model)

        @self.ui_view.restart_button.event("on_click")
        def on_click_restart(event):
            self.restart()

    def restart(self):
        self.my_model.reset()
        self.my_view.refresh()


    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.UP:
            self.my_model.set_direction((0, 1))
        elif symbol == arcade.key.DOWN:
            self.my_model.set_direction((0, -1))
        elif symbol == arcade.key.LEFT:
            self.my_model.set_direction((-1, 0))
        elif symbol == arcade.key.RIGHT:
            self.my_model.set_direction((1, 0))


    def on_update(self, delta_time: float):
        self.my_model.tick(delta_time)
        self.ui_view.refresh()
        self.my_view.refresh()

    def on_draw(self):
        self.clear()
        self.my_view.draw()
        self.ui_view.draw()


# --- STARTUP ---
if __name__ == "__main__":
    BREEDTE: int = 400
    HOOGTE: int = 600

    model = SnakeModel()
    view = SnakeView(model)
    controller = GameController(model, view, BREEDTE, HOOGTE)

    arcade.run()