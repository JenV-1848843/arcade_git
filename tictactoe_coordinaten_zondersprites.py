import arcade
import arcade.gui
from PIL import Image, ImageDraw, ImageFont

# --- MODEL ---
class TictactoeModel:
    current_player: str
    winner: str | None

    def __init__(self):
        self.board = [[None, None, None],
                      [None, None, None],
                      [None, None, None]]
        self.current_player = "X"
        self.winner = None

    def make_move(self, row: int, col: int):
        if self.winner is None and self.board[row][col] is None:
            self.board[row][col] = self.current_player
            self.check_winner()

            if self.winner is None:
                if self.current_player == "X":
                    self.current_player = "O"
                else:
                    self.current_player = "X"

    def reset(self):
        for r in range(3):
            for c in range(3):
                self.board[r][c] = None

        self.current_player = "X"
        self.winner = None

    def check_winner(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] and self.board[i][0] is not None:
                self.winner = self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] and self.board[0][i] is not None:
                self.winner = self.board[0][i]

        if self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[0][0] is not None:
            self.winner = self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] and self.board[0][2] is not None:
            self.winner = self.board[0][2]


# --- VIEW ---
class TictactoeView:
    model: TictactoeModel
    offset_y: int
    block_size: int

    texture_x: arcade.Texture
    texture_o: arcade.Texture
    sprite_list: arcade.SpriteList

    def __init__(self, model: TictactoeModel):
        self.model = model
        self.offset_y = 100
        self.block_size = 100

        self.texture_x = self.make_letter_texture("X", "blue")
        self.texture_o = self.make_letter_texture("O", "red")

        self.sprite_list = arcade.SpriteList()
        self.refresh()

    def make_letter_texture(self, text: str, kleur: str) -> arcade.Texture:
        image = Image.new('RGBA', (self.block_size, self.block_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        draw.text(
            (self.block_size // 2, self.block_size // 2),
            text=text,
            fill=kleur,
            font_size=40,
            anchor="mm"
        )

        return arcade.Texture(image)

    def get_grid_position(self, x: float, y: float) -> tuple[int, int] | None:
        board_y = y - self.offset_y
        max_breedte = 3 * self.block_size
        max_hoogte = 3 * self.block_size

        if 0 <= x < max_breedte and 0 <= board_y < max_hoogte:
            kolom = int(x // self.block_size)
            rij = 2 - int(board_y // self.block_size)
            return (rij, kolom)

        return None

    def refresh(self):
        self.sprite_list.clear()

        for row in range(3):
            for col in range(3):
                waarde = self.model.board[row][col]
                if waarde is not None:
                    center_x = (col * self.block_size) + (self.block_size / 2)
                    center_y = ((2 - row) * self.block_size) + (self.block_size / 2) + self.offset_y

                    texture_to_use = self.texture_x if waarde == "X" else self.texture_o

                    sprite = arcade.Sprite(texture_to_use)
                    sprite.center_x = center_x
                    sprite.center_y = center_y
                    self.sprite_list.append(sprite)

    def draw(self):
        arcade.draw_line(100, 0 + self.offset_y, 100, 300 + self.offset_y, arcade.color.BLACK, 4)
        arcade.draw_line(200, 0 + self.offset_y, 200, 300 + self.offset_y, arcade.color.BLACK, 4)
        arcade.draw_line(0, 100 + self.offset_y, 300, 100 + self.offset_y, arcade.color.BLACK, 4)
        arcade.draw_line(0, 200 + self.offset_y, 300, 200 + self.offset_y, arcade.color.BLACK, 4)

        self.sprite_list.draw()

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
        super().__init__(breedte, hoogte, "MVC Tictactoe (Grid Math)", pixel_perfect=True, resizable=False)
        arcade.set_background_color(arcade.color.WHITE)

        self.model = model
        self.my_view = view
        self.ui_view = UIView(self.model)

        @self.ui_view.restart_button.event("on_click")
        def on_click_restart(event: arcade.gui.UIEvent):
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
        geklikt_vakje = self.my_view.get_grid_position(x, y)

        if geklikt_vakje is not None:
            rij, kolom = geklikt_vakje
            self.model.make_move(rij, kolom)

            self.my_view.refresh()
            self.ui_view.refresh()


# --- STARTUP ---
if __name__ == "__main__":
    BREEDTE = 300
    HOOGTE = 400

    model = TictactoeModel()
    view = TictactoeView(model)
    controller = GameController(model, view, BREEDTE, HOOGTE)

    arcade.run()
