from enum import Enum

import arcade
import arcade.gui
from PIL import Image, ImageDraw, ImageFont

class FieldValue(Enum):
    X = 1
    O = 2
    Empty = 0

class Speler(Enum):
    SPELER_X = 1
    SPELER_O = 2

# --- MODEL ---
class FieldModel:
    waarde: FieldValue

    def __init__(self):
        self.waarde = FieldValue.Empty

    def change_waarde(self, waarde: FieldValue) -> bool:
        if self.waarde == FieldValue.Empty:
            self.waarde = waarde
            return True
        return False

class TictactoeModel:
    current_player: Speler
    winner: Speler | None
    board: list[list[FieldModel]]

    def __init__(self):
        self.board = [
            [FieldModel(), FieldModel(), FieldModel()],
            [FieldModel(), FieldModel(), FieldModel()],
            [FieldModel(), FieldModel(), FieldModel()]
        ]
        self.current_player = Speler.SPELER_X
        self.winner = None

    def make_move(self, row: int, col: int):
        field = self.board[row][col]

        if self.winner is None:
            if self.current_player == Speler.SPELER_X:
                new_waarde = FieldValue.X
            else:
                new_waarde = FieldValue.O

            succes = field.change_waarde(new_waarde)
            if succes:
                self.check_winner()
                if self.winner is None:
                    if self.current_player == Speler.SPELER_X:
                        self.current_player = Speler.SPELER_O
                    else:
                        self.current_player = Speler.SPELER_X

    def reset(self):
        for r in range(3):
            for c in range(3):
                self.board[r][c].waarde = FieldValue.Empty

        self.current_player = Speler.SPELER_X
        self.winner = None

    def check_winner(self):
        winnende_waarde = FieldValue.Empty

        for i in range(3):
            # Horizontale checks
            if self.board[i][0].waarde == self.board[i][1].waarde == self.board[i][2].waarde and self.board[i][0].waarde != FieldValue.Empty:
                winnende_waarde = self.board[i][0].waarde

            # Verticale checks
            if self.board[0][i].waarde == self.board[1][i].waarde == self.board[2][i].waarde and self.board[0][i].waarde != FieldValue.Empty:
                winnende_waarde = self.board[0][i].waarde

        # Diagonale checks
        if self.board[0][0].waarde == self.board[1][1].waarde == self.board[2][2].waarde and self.board[0][0].waarde != FieldValue.Empty:
            winnende_waarde = self.board[0][0].waarde

        if self.board[0][2].waarde == self.board[1][1].waarde == self.board[2][0].waarde and self.board[0][2].waarde != FieldValue.Empty:
            winnende_waarde = self.board[0][2].waarde

        if winnende_waarde == FieldValue.X:
            self.winner = Speler.SPELER_X
        elif winnende_waarde == FieldValue.O:
            self.winner = Speler.SPELER_O


# --- VIEW ---
class FieldView(arcade.Sprite):
    model: FieldModel
    block_size: int
    row: int
    col: int

    def __init__(self, model: FieldModel, block_size: int, row: int, col: int):
        super().__init__()
        self.block_size = block_size
        self.model = model

        self.row = row
        self.col = col

        self.refresh()

    def refresh(self):
        self.texture = self.make_field_texture()

    def make_field_texture(self) -> arcade.Texture:
        image = Image.new('RGBA', (self.block_size, self.block_size), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle([0, 0, self.block_size - 1, self.block_size - 1], outline="black", fill="beige")

        if self.model.waarde != FieldValue.Empty:
            kleur = "blue" if self.model.waarde == FieldValue.X else "red"

            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except IOError:
                font = ImageFont.load_default()

            draw.text(
                (self.block_size // 2, self.block_size // 2),
                text=self.model.waarde.name,
                fill=kleur,
                font=font,
                anchor="mm"
            )

        return arcade.Texture(image)


class TictactoeView:
    model: TictactoeModel
    board_sprites: arcade.SpriteList
    OFFSET_Y: int = 100
    BLOCK_SIZE: int = 100

    def __init__(self, model: TictactoeModel):
        self.model = model
        self.board_sprites = arcade.SpriteList()
        self.setup_board()

    def refresh(self):
        for sprite in self.board_sprites:
            sprite.refresh()

    def draw(self):
        self.board_sprites.draw()

        if self.model.winner:
            winnende_letter = "X" if self.model.winner == Speler.SPELER_X else "O"
            arcade.draw_text(
                f"Speler {winnende_letter} wint!",
                150, 150 + self.OFFSET_Y,
                arcade.color.GREEN,
                35,
                anchor_x="center",
                anchor_y="center"
            )

    def setup_board(self):
        for r in range(3):
            for c in range(3):
                field_model = self.model.board[r][c]

                field_view = FieldView(field_model, block_size=TictactoeView.BLOCK_SIZE, row=r, col=c)

                field_view.center_x = (c * TictactoeView.BLOCK_SIZE) + (TictactoeView.BLOCK_SIZE / 2)
                field_view.center_y = ((2 - r) * TictactoeView.BLOCK_SIZE) + (TictactoeView.BLOCK_SIZE / 2) + TictactoeView.OFFSET_Y

                self.board_sprites.append(field_view)

    def get_clicked_grid_position(self, x: float, y: float) -> tuple[int, int] | None:
        clicked_sprites = arcade.get_sprites_at_point((x, y), self.board_sprites)
        if len(clicked_sprites) > 0:
            geklikt_blokje: FieldView = clicked_sprites[0]
            return (geklikt_blokje.row, geklikt_blokje.col)
        return None

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

    def refresh(self):
        if self.model.winner:
            winnende_letter = "X" if self.model.winner == Speler.SPELER_X else "O"
            self.status_label.text = f"Winnaar: {winnende_letter}"
        else:
            huidige_letter = "X" if self.model.current_player == Speler.SPELER_X else "O"
            self.status_label.text = f"Beurt: {huidige_letter}"

    def draw(self):
        self.manager.draw()

    def setup_layout(self):
        anchor = arcade.gui.UIAnchorLayout()
        hbox = arcade.gui.UIBoxLayout(vertical=False, space_between=20)
        hbox.add(self.status_label)
        hbox.add(self.restart_button)

        anchor.add(hbox, anchor_x="center_x", anchor_y="bottom", align_y=30)
        self.manager.add(anchor)


# --- CONTROLLER ---
class GameController(arcade.Window):
    my_model: TictactoeModel
    my_view: TictactoeView
    ui_view: UIView

    def __init__(self, model: TictactoeModel, view: TictactoeView, breedte: int = 300, hoogte: int = 400):
        super().__init__(breedte, hoogte, "MVC Tictactoe 2D", pixel_perfect=True, resizable=False)
        arcade.set_background_color(arcade.color.WHITE)

        self.my_model = model
        self.my_view = view
        self.ui_view = UIView(self.my_model)

        @self.ui_view.restart_button.event("on_click")
        def on_click_restart(event: arcade.gui.UIEvent):
            self.restart()

    def restart(self):
        self.my_model.reset()
        self.my_view.refresh()
        self.ui_view.refresh()

    def on_draw(self):
        self.clear()
        self.my_view.draw()
        self.ui_view.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        geklikte_pos = self.my_view.get_clicked_grid_position(x, y)

        if geklikte_pos is not None:
            rij, kolom = geklikte_pos
            self.my_model.make_move(rij, kolom)

            self.my_view.refresh()
            self.ui_view.refresh()


# --- STARTUP ---
if __name__ == "__main__":
    BREEDTE: int = 300
    HOOGTE: int = 400

    model = TictactoeModel()
    view = TictactoeView(model)
    controller = GameController(model, view)

    arcade.run()
