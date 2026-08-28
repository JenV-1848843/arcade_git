import arcade
from PIL import Image, ImageDraw
import arcade

import random

# --- MODEL ---
class SnakeModel:
    def __init__(self):
        self.cols = 20
        self.rows = 20

        self.body = [(10, 10), (10, 9), (10, 8)]

        self.direction = (0, 1)

        self.food = self.spawn_food()
        self.game_over = False

    def spawn_food(self):
        while True:
            food = (random.randint(0, self.cols - 1), random.randint(0, self.rows - 1))
            if food not in self.body:
                return food

    def update(self):
        if self.game_over:
            return

        head_col, head_row = self.body[0]
        d_col, d_row = self.direction
        new_head = (head_col + d_col, head_row + d_row)

        if not (0 <= new_head[0] < self.cols and 0 <= new_head[1] < self.rows):
            self.game_over = True
            return
        if new_head in self.body:
            self.game_over = True
            return

        self.body.insert(0, new_head)

        if new_head == self.food:
            self.food = self.spawn_food()
        else:
            self.body.pop()

# --- VIEW ---
class SnakeView:
    def __init__(self, model):
        self.model = model
        self.block_size = 20
        self.sprites = arcade.SpriteList()

        self.food_texture = self.make_texture((255, 0, 0))    # Rood voor eten
        self.snake_texture = self.make_texture((0, 255, 0))   # Groen voor slang

    def make_texture(self, color):
        image = Image.new('RGBA', (self.block_size, self.block_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        draw.rectangle([0, 0, self.block_size - 2, self.block_size - 2], fill=color)

        return arcade.Texture(image)

    def draw(self):
        self.sprites.clear()

        food_x = self.model.food[0] * self.block_size + (self.block_size / 2)
        food_y = self.model.food[1] * self.block_size + (self.block_size / 2)

        food_sprite = arcade.Sprite(self.food_texture)
        food_sprite.center_x = food_x
        food_sprite.center_y = food_y
        self.sprites.append(food_sprite)

        for col, row in self.model.body:
            x = col * self.block_size + (self.block_size / 2)
            y = row * self.block_size + (self.block_size / 2)

            snake_sprite = arcade.Sprite(self.snake_texture)
            snake_sprite.center_x = x
            snake_sprite.center_y = y
            self.sprites.append(snake_sprite)

        self.sprites.draw()

        if self.model.game_over:
            arcade.draw_text("GAME OVER", 200, 200, arcade.color.WHITE, 30, anchor_x="center", anchor_y="center")


# --- CONTROLLER ---
class GameController(arcade.Window):
    def __init__(self, model, view):
        super().__init__(400, 400, "Snake MVC", pixel_perfect=True)
        self.model = model
        self.my_view = view
        arcade.set_background_color(arcade.color.BLACK)

        self.set_update_rate(1 / 8)

    def on_draw(self):
        self.clear()
        self.my_view.draw()

    def on_update(self, delta_time):
        self.model.update()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP and self.model.direction != (0, -1):
            self.model.direction = (0, 1)
        elif key == arcade.key.DOWN and self.model.direction != (0, 1):
            self.model.direction = (0, -1)
        elif key == arcade.key.LEFT and self.model.direction != (1, 0):
            self.model.direction = (-1, 0)
        elif key == arcade.key.RIGHT and self.model.direction != (-1, 0):
            self.model.direction = (1, 0)


# --- STARTUP ---
if __name__ == "__main__":
    model = SnakeModel()
    view = SnakeView(model)
    controller = GameController(model, view)

    arcade.run()