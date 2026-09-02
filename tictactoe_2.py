import arcade
import arcade.gui
from PIL import Image, ImageDraw, ImageFont

# --- MODEL ---
class FieldModel:
    row: int
    col: int
    waarde: str | None

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.waarde = None

class TictactoeModel:
    current_player: str
    winner: str | None
    board: list[list[FieldModel]]

    def __init__(self):
        self.board = [
            [FieldModel(0, 0), FieldModel(0, 1), FieldModel(0, 2)],
            [FieldModel(1, 0), FieldModel(1, 1), FieldModel(1, 2)],
            [FieldModel(2, 0), FieldModel(2, 1), FieldModel(2, 2)]
        ]
        self.current_player = "X"
        self.winner = None

    def make_move(self, row: int, col: int):
        # Enkel een zet toelaten als er nog geen winnaar is én het vakje leeg is
        if self.winner is None and self.board[row][col].waarde is None:
            self.board[row][col].waarde = self.current_player
            self.check_winner()

            # Beurt doorgeven als er nog niet gewonnen is
            if self.winner is None:
                if self.current_player == "X":
                    self.current_player = "O"
                else:
                    self.current_player = "X"

    def reset(self):
        # Maak alle bestaande vakjes weer leeg (None)
        for r in range(3):
            for c in range(3):
                self.board[r][c].waarde = None

        self.current_player = "X"
        self.winner = None

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
class FieldView(arcade.Sprite):
    model: FieldModel
    block_size: int
    current_drawn_value: str | None

    def __init__(self, model: FieldModel, block_size: int):
        super().__init__()
        self.block_size = block_size
        self.model = model

        self.refresh()

    def refresh(self):
        self.texture = self.make_field_texture()

    def make_field_texture(self) -> arcade.Texture:
        image = Image.new('RGBA', (self.block_size, self.block_size), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle([0, 0, self.block_size - 1, self.block_size - 1], outline="black", fill="white")

        if self.model.waarde is not None:

            kleur = "blue" if self.model.waarde == "X" else "red"

            draw.text(
                (self.block_size // 2, self.block_size // 2),
                text=self.model.waarde,
                fill=kleur,
                font_size=40,
                anchor="mm"
            )

        return arcade.Texture(image)


class TictactoeView:
    model: TictactoeModel
    board_sprites: arcade.SpriteList
    offset_y: int

    def __init__(self, model: TictactoeModel):
        self.board_sprites = arcade.SpriteList()
        self.model = model

        self.offset_y = 100

        self.setup_board()

    def setup_board(self):
        block_size = 100
        for row in range(3):
            for col in range(3):
                bestaand_field_model = self.model.board[row][col]

                fieldView = FieldView(bestaand_field_model, block_size=block_size)
                fieldView.center_x = (col * block_size) + (block_size / 2)
                fieldView.center_y = ((2 - row) * block_size) + (block_size / 2) + self.offset_y

                self.board_sprites.append(fieldView)

    def refresh(self):
        for sprite in self.board_sprites:
            sprite.refresh()

    def draw(self):
        self.board_sprites.draw()

        if self.model.winner:
            arcade.draw_text(
                f"{self.model.winner} wint!",
                150, 150 + self.offset_y,
                arcade.color.GREEN,
                45,
                anchor_x="center",
                anchor_y="center"
            )

class UIView:
    manager: arcade.gui.UIManager
    restart_button: arcade.gui.UIFlatButton
    status_label: arcade.gui.UILabel
    model: TictactoeModel

    def __init__(self, model: TictactoeModel):
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.model = model

        self.restart_button = arcade.gui.UIFlatButton(text="Restart", width=100, height=40)

        self.status_label = arcade.gui.UILabel(text="Beurt: X", width=150, height=40, text_color=arcade.color.BLACK)

        self.setup_layout()
        self.refresh()

    def setup_layout(self):
        anchor = arcade.gui.UIAnchorLayout()

        hbox = arcade.gui.UIBoxLayout(vertical=False, space_between=20)
        hbox.add(self.status_label)
        hbox.add(self.restart_button)

        anchor.add(hbox, anchor_x="center_x", anchor_y="bottom", align_y=30)
        self.manager.add(anchor)

    def refresh(self):
        if self.model.winner:
            self.status_label.text = f"Winnaar: {self.model.winner}"
        else:
            self.status_label.text = f"Beurt: {self.model.current_player}"

    def draw(self):
        self.manager.draw()


# --- CONTROLLER ---
class GameController(arcade.Window):
    model: TictactoeModel
    my_view: TictactoeView
    ui_view: UIView

    def __init__(self, model: TictactoeModel, view: TictactoeView, breedte: int, hoogte: int):
        super().__init__(breedte, hoogte, "MVC Tictactoe", pixel_perfect=True, resizable=False)
        arcade.set_background_color(arcade.color.WHITE)

        self.model = model
        self.my_view = view

        self.ui_view = UIView(self.model)

        @self.ui_view.restart_button.event("on_click")
        def on_click_restart(event):
            self.restart()

    def restart(self):
        self.model.reset()
        self.my_view.refresh()
        self.ui_view.refresh()

    def on_draw(self):
        self.clear()
        self.my_view.draw()
        self.ui_view.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        clicked_sprites = arcade.get_sprites_at_point((x, y), self.my_view.board_sprites)

        if len(clicked_sprites) > 0:
            geklikt_blokje: FieldView = clicked_sprites[0]

            rij = geklikt_blokje.model.row
            kolom = geklikt_blokje.model.col

            self.model.make_move(rij, kolom)

            self.my_view.refresh()
            self.ui_view.refresh()


# --- STARTUP ---
if __name__ == "__main__":
    BREEDTE: int = 300
    HOOGTE: int = 400

    model = TictactoeModel()
    view = TictactoeView(model)
    controller = GameController(model, view, BREEDTE, HOOGTE)

    arcade.run()
