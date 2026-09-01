from enum import Enum
import arcade
import arcade.gui
from PIL import Image, ImageDraw

# --- MODEL ---
class BallModel:
    x: float
    y: float
    dx: float
    dy: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.dx = 2.0
        self.dy = 2.0

    def step(self):
        self.x += self.dx
        self.y += self.dy


class Direction(Enum):
    UP = 1
    DOWN = 2


class BlockerModel:
    x: float
    y: float
    blocker_breedte: float
    blocker_hoogte: float
    direction: Direction | None

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.blocker_breedte = 20.0
        self.blocker_hoogte = 100.0
        self.direction = None

    def step(self):
        snelheid = 5.0
        new_y = self.y

        if self.direction == Direction.UP:
            new_y = self.y + snelheid
        elif self.direction == Direction.DOWN:
            new_y = self.y - snelheid

        if not self.illegal_position(new_y):
            self.y = new_y

    def illegal_position(self, y: float) -> bool:
        return (y - self.blocker_hoogte // 2) <= 0 or (y + self.blocker_hoogte // 2) >= 300

    def set_direction(self, direction: Direction | None):
        self.direction = direction


class PongModel:
    BREEDTE: int = 400
    HOOGTE: int = 300
    spelerA: BlockerModel
    spelerB: BlockerModel
    winner: str
    game_over: bool

    tijd_verstreken: float
    TICK_RATE: float = 1.0 / 60.0

    def __init__(self):
        self.game_over = False
        self.ball = BallModel(200.0, 150.0)
        self.spelerA = BlockerModel(20.0, 150.0)
        self.spelerB = BlockerModel(380.0, 150.0)
        self.winner = "Speler A"

        self.tijd_verstreken = 0.0

    def reset(self):
        self.game_over = False
        self.winner = "Speler A"
        self.tijd_verstreken = 0.0

        self.ball.x, self.ball.y = 200.0, 150.0
        self.ball.dx, self.ball.dy = 2.0, 2.0

        self.spelerA.y = 150.0
        self.spelerA.direction = None

        self.spelerB.y = 150.0
        self.spelerB.direction = None

    def tick(self, delta_time: float):
        if self.game_over:
            return

        self.tijd_verstreken += delta_time

        while self.tijd_verstreken >= self.TICK_RATE:
            self.step()
            self.tijd_verstreken -= self.TICK_RATE

    def step(self):
        self.ball.step()
        self.spelerA.step()
        self.spelerB.step()

        self.check_bounces()

    def check_bounces(self):
        radius = 5.0

        if self.ball.x - radius <= 0:
            self.winner = "Speler B"
            self.game_over = True
            return

        elif self.ball.x + radius >= self.BREEDTE:
            self.winner = "Speler A"
            self.game_over = True
            return

        if self.illegal_position_x(self.ball.x, radius):
            self.switch_winner()
            self.ball.dx = -self.ball.dx

        if self.illegal_position_y(self.ball.y, radius):
            self.ball.dy = -self.ball.dy

    def switch_winner(self):
        if self.winner == "Speler A":
            self.winner = "Speler B"
        else:
            self.winner = "Speler A"

    def illegal_position_x(self, x: float, radius: float) -> bool:
        half_breedte_a = self.spelerA.blocker_breedte / 2
        half_hoogte_a = self.spelerA.blocker_hoogte / 2

        raakt_x_a = (x - radius <= self.spelerA.x + half_breedte_a) and (x - radius >= self.spelerA.x - half_breedte_a)
        raakt_y_a = (self.ball.y >= self.spelerA.y - half_hoogte_a) and (self.ball.y <= self.spelerA.y + half_hoogte_a)

        # Enkel botsen als we naar links (Speler A) bewegen
        if raakt_x_a and raakt_y_a and self.ball.dx < 0:
            return True

        half_breedte_b = self.spelerB.blocker_breedte / 2
        half_hoogte_b = self.spelerB.blocker_hoogte / 2

        raakt_x_b = (x + radius >= self.spelerB.x - half_breedte_b) and (x + radius <= self.spelerB.x + half_breedte_b)
        raakt_y_b = (self.ball.y >= self.spelerB.y - half_hoogte_b) and (self.ball.y <= self.spelerB.y + half_hoogte_b)

        # Enkel botsen als we naar rechts (Speler B) bewegen
        if raakt_x_b and raakt_y_b and self.ball.dx > 0:
            return True

        return False

    def illegal_position_y(self, y: float, radius: float) -> bool:
        # Enkel botsen als we effectief richting die muur bewegen (anti-plak fix)
        if y - radius <= 0 and self.ball.dy < 0:
            return True
        if y + radius >= self.HOOGTE and self.ball.dy > 0:
            return True
        return False


# --- VIEW ---
class BallView(arcade.Sprite):
    ball_model: BallModel
    size_ball: int
    offset_y: int

    def __init__(self, ball_model: BallModel, offset_y: int = 0):
        super().__init__()
        self.ball_model = ball_model
        self.size_ball = 10
        self.offset_y = offset_y

        image = Image.new('RGBA', (self.size_ball, self.size_ball), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        midden = self.size_ball // 2
        draw.circle((midden, midden), radius=midden, fill="black")

        self.texture = arcade.Texture(image)
        self.refresh()

    def refresh(self):
        self.center_x = self.ball_model.x
        self.center_y = self.ball_model.y + self.offset_y


class BlockerView(arcade.Sprite):
    model: BlockerModel
    offset_y: int

    def __init__(self, model: BlockerModel, offset_y: int = 0):
        super().__init__()
        self.model = model
        self.offset_y = offset_y

        self.texture = self.make_blocker_texture()
        self.refresh()

    def make_blocker_texture(self) -> arcade.Texture:
        breedte = int(self.model.blocker_breedte)
        hoogte = int(self.model.blocker_hoogte)
        image = Image.new('RGBA', (breedte, hoogte), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        draw.rectangle([0, 0, breedte - 1, hoogte - 1], fill="black")

        return arcade.Texture(image)

    def refresh(self):
        self.center_x = self.model.x
        self.center_y = self.model.y + self.offset_y

class PongView:
    model: PongModel
    sprites: arcade.SpriteList
    ballview: BallView
    border_texture: arcade.Texture
    view_spelerA: BlockerView
    view_spelerB: BlockerView
    offset_y: int

    def __init__(self, model: PongModel):
        self.model = model
        self.sprites = arcade.SpriteList()

        self.offset_y = 100

        self.view_spelerA = BlockerView(self.model.spelerA, self.offset_y)
        self.view_spelerB = BlockerView(self.model.spelerB, self.offset_y)

        self.border_texture = self.make_border_texture()
        border_sprite = arcade.Sprite(self.border_texture)
        border_sprite.center_x = self.model.BREEDTE / 2
        border_sprite.center_y = (self.model.HOOGTE / 2) + self.offset_y
        self.sprites.append(border_sprite)

        self.sprites.append(self.view_spelerA)
        self.sprites.append(self.view_spelerB)

        self.ballview = BallView(self.model.ball, self.offset_y)
        self.sprites.append(self.ballview)

    def make_border_texture(self) -> arcade.Texture:
        image = Image.new('RGBA', (self.model.BREEDTE, self.model.HOOGTE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle([0, 0, self.model.BREEDTE - 1, self.model.HOOGTE - 1], outline="black", width=4)
        return arcade.Texture(image)

    def refresh(self):
        self.ballview.refresh()
        self.view_spelerA.refresh()
        self.view_spelerB.refresh()

    def draw(self):
        self.sprites.draw()

        if self.model.game_over:
            arcade.draw_text(
                f"{self.model.winner} wint!",
                self.model.BREEDTE / 2,
                (self.model.HOOGTE / 2) + self.offset_y,
                arcade.color.GREEN,
                35,
                anchor_x="center",
                anchor_y="center"
            )


class UIView:
    manager: arcade.gui.UIManager
    restart_button: arcade.gui.UIFlatButton
    status_label: arcade.gui.UILabel
    model: PongModel

    def __init__(self, model: PongModel):
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.model = model

        self.restart_button = arcade.gui.UIFlatButton(text="Restart", width=100, height=40)
        self.status_label = arcade.gui.UILabel(text="Aan de bal: Speler A", width=250, height=40, text_color=arcade.color.BLACK)

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
        if self.model.game_over:
            self.status_label.text = f"Winnaar: {self.model.winner}"
        else:
            self.status_label.text = f"Laatst geraakt: {self.model.winner}"

    def draw(self):
        self.manager.draw()


# --- CONTROLLER ---
class GameController(arcade.Window):
    model: PongModel
    my_view: PongView
    ui_view: UIView

    def __init__(self, model: PongModel, view: PongView, breedte: int, hoogte: int):
        super().__init__(breedte, hoogte, "MVC Pong", pixel_perfect=True, resizable=False)
        arcade.set_background_color(arcade.color.WHITE)

        self.model = model
        self.my_view = view
        self.ui_view = UIView(self.model)

        @self.ui_view.restart_button.event("on_click")
        def on_click_restart(event: arcade.gui.UIEvent): # <-- AANGEPAST: Type hint toegevoegd
            self.restart()

    def restart(self):
        self.model.reset()
        self.my_view.refresh()
        self.ui_view.refresh()

    def on_draw(self):
        self.clear()
        self.my_view.draw()
        self.ui_view.draw()

    def on_update(self, delta_time: float):
        self.model.tick(delta_time)

        self.my_view.refresh()
        self.ui_view.refresh()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.W:
            self.model.spelerA.set_direction(Direction.UP)
        elif symbol == arcade.key.S:
            self.model.spelerA.set_direction(Direction.DOWN)
        elif symbol == arcade.key.UP:
            self.model.spelerB.set_direction(Direction.UP)
        elif symbol == arcade.key.DOWN:
            self.model.spelerB.set_direction(Direction.DOWN)

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol in (arcade.key.W, arcade.key.S):
            self.model.spelerA.set_direction(None)
        elif symbol in (arcade.key.UP, arcade.key.DOWN):
            self.model.spelerB.set_direction(None)


# --- STARTUP ---
if __name__ == "__main__":
    BREEDTE = 400
    HOOGTE = 400

    model = PongModel()
    view = PongView(model)
    controller = GameController(model, view, BREEDTE, HOOGTE)

    arcade.run()
