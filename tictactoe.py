import random
import arcade
from PIL import Image, ImageDraw, ImageFont

# --- MODEL ---
class FieldModel:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.waarde = None

class TictactoeModel:
    def __init__(self):
        self.board = [
            [FieldModel(0, 0), FieldModel(0, 1), FieldModel(0, 2)],
            [FieldModel(1, 0), FieldModel(1, 1), FieldModel(1, 2)],
            [FieldModel(2, 0), FieldModel(2, 1), FieldModel(2, 2)]
        ]
        self.current_player = "X"
        self.winner = None

    def make_move(self, row, col):
        if self.winner is None and self.board[row][col].waarde is None:
            self.board[row][col].waarde = self.current_player
            self.check_winner()

            if self.winner is None:
                if self.current_player == "X":
                    self.current_player = "O"
                else:
                    self.current_player = "X"

    def check_winner(self):
        for i in range(3):
            if self.board[i][0].waarde == self.board[i][1].waarde == self.board[i][2].waarde and self.board[i][0].waarde is not None:
                self.winner = self.board[i][0].waarde
            if self.board[0][i].waarde == self.board[1][i].waarde == self.board[2][i].waarde and self.board[0][i].waarde is not None:
                self.winner = self.board[0][i].waarde

        if self.board[0][0].waarde == self.board[1][1].waarde == self.board[2][2].waarde and self.board[0][0].waarde is not None:
            self.winner = self.board[0][0].waarde
        if self.board[0][2].waarde == self.board[1][1].waarde == self.board[2][0].waarde and self.board[0][2].waarde is not None:
            self.winner = self.board[0][2].waarde


# --- VIEW ---
class TictactoeView:
    def __init__(self, model):
        self.board_sprites = arcade.SpriteList()
        self.model = model

        self.setup_board()

    def setup_board(self):
        block_size = 100
        for row in range(3):
            for col in range(3):
                bestaand_field_model = self.model.board[row][col]

                fieldView = FieldView(bestaand_field_model, block_size=block_size)
                fieldView.center_x = (col * block_size) + (block_size / 2)
                fieldView.center_y = ((2 - row) * block_size) + (block_size / 2)

                self.board_sprites.append(fieldView)

    def draw(self):
        for sprite in self.board_sprites:
            sprite.update_if_needed()

        self.board_sprites.draw()

        if self.model.winner:
            arcade.draw_text(
                f"{self.model.winner} wint!",
                150, 150,
                arcade.color.GREEN,
                45,
                anchor_x="center",
                anchor_y="center"
            )

class FieldView(arcade.Sprite):
    def __init__(self, model: FieldModel, block_size: int):
        super().__init__()
        self.block_size = block_size
        self.model = model

        self.current_drawn_value = None

        self.texture = self.make_field_texture()

    def update_if_needed(self):
        if self.current_drawn_value != self.model.waarde:
            self.texture = self.make_field_texture()

    def make_field_texture(self):
        image = Image.new('RGBA', (self.block_size, self.block_size), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle([0, 0, self.block_size - 1, self.block_size - 1], outline="black", fill="white")

        if self.model.waarde is not None:
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except IOError:
                font = ImageFont.load_default()

            kleur = "blue" if self.model.waarde == "X" else "red"

            draw.text(
                (self.block_size // 2, self.block_size // 2),
                text=self.model.waarde,
                fill=kleur,
                font=font,
                anchor="mm"
            )

        self.current_drawn_value = self.model.waarde

        return arcade.Texture(image)


# --- CONTROLLER ---
class GameController(arcade.Window):
    def __init__(self, model, view):
        super().__init__(300, 300, "Tictactoe", pixel_perfect=True)
        self.model = model
        self.my_view = view
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        self.clear()
        self.my_view.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        clicked_sprites: list[FieldView] = arcade.get_sprites_at_point((x, y), self.my_view.board_sprites)

        if len(clicked_sprites) > 0:
            geklikt_blokje: FieldView = clicked_sprites[0]

            rij = geklikt_blokje.model.row
            kolom = geklikt_blokje.model.col

            self.model.make_move(rij, kolom)


# --- STARTUP ---
if __name__ == "__main__":
    model = TictactoeModel()
    view = TictactoeView(model)
    controller = GameController(model, view)

    arcade.run()
