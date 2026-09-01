from enum import Enum
import arcade
import arcade.gui
from PIL import Image, ImageDraw
import random


# --- MODEL ---
class DinoModel:
    x: float
    y: float
    dy: float
    breedte: int = 40
    hoogte: int = 40
    ground_y: float = 100.0
    gravity: float = 0.6
    jump_power: float = 12.0

    def __init__(self):
        self.x = 100
        self.y = self.ground_y
        self.dy = 0.0

    def jump(self):
        if self.y == self.ground_y:
            self.dy = self.jump_power

    def step(self):
        if self.y > self.ground_y or self.dy > 0:
            self.dy -= self.gravity
            self.y += self.dy

        if self.y < self.ground_y:
            self.y = self.ground_y
            self.dy = 0.0


class CactusModellen(Enum):
    SMALL = 1
    MEDIUM = 2
    BIG = 3

class CactusModel:
    x: float
    y: float
    cactusmodel: CactusModellen
    hoogte: int
    breedte: int
    snelheid: float = 6.0

    def __init__(self, start_x: float, cactusmodel: CactusModellen, ground_y: float):
        self.x = start_x
        self.cactusmodel = cactusmodel

        match cactusmodel:
            case CactusModellen.SMALL:
                self.breedte = 20
                self.hoogte = 20
            case CactusModellen.MEDIUM:
                self.breedte = 20
                self.hoogte = 40
            case CactusModellen.BIG:
                self.breedte = 40
                self.hoogte = 40

        self.y = ground_y + (self.hoogte / 2) - 20

    def step(self):
        self.x -= self.snelheid


class DinoGameModel:
    BREEDTE: int = 800
    HOOGTE: int = 400
    TICK_RATE: float = 1.0 / 60.0

    game_over: bool
    score: int
    high_score: int
    tijd_verstreken: float
    dino: DinoModel
    cactussen: list[CactusModel]
    ticks_tot_spawn: int

    def __init__(self):
        self.game_over = False
        self.score = 0
        self.high_score = 0
        self.tijd_verstreken = 0.0

        self.dino = DinoModel()
        self.cactussen = []
        self.ticks_tot_spawn = 0

    def reset(self):
        if self.score > self.high_score:
            self.high_score = self.score
        self.game_over = False
        self.score = 0
        self.tijd_verstreken = 0.0

        self.dino = DinoModel()
        self.cactussen = []
        self.ticks_tot_spawn = 0

    def tick(self, delta_time: float):
        if self.game_over:
            return
        self.tijd_verstreken += delta_time

        while self.tijd_verstreken >= self.TICK_RATE:
            self.step()
            self.tijd_verstreken -= self.TICK_RATE

    def step(self):
        self.score += 1
        self.dino.step()
        for c in self.cactussen:
            c.step()

        self.cactussen = [c for c in self.cactussen if c.x > -50]

        self.ticks_tot_spawn -= 1
        if self.ticks_tot_spawn <= 0:
            # Kies een willekeurige Enum waarde (SMALL, MEDIUM of BIG)
            gekozen_model = random.choice(list(CactusModellen))
            nieuwe_cactus = CactusModel(start_x=self.BREEDTE + 50, ground_y=self.dino.ground_y, cactusmodel=gekozen_model)
            self.cactussen.append(nieuwe_cactus)
            self.ticks_tot_spawn = random.randint(60,150)

        self.check_collisions()

    def check_collisions(self):
        dino_links = self.dino.x - (self.dino.breedte / 2)
        dino_rechts = self.dino.x + (self.dino.breedte / 2)
        dino_onder = self.dino.y - (self.dino.hoogte / 2)
        dino_boven = self.dino.y + (self.dino.hoogte / 2)

        for c in self.cactussen:
            c_links = c.x - (c.breedte / 2)
            c_rechts = c.x + (c.breedte / 2)
            c_onder = c.y - (c.hoogte / 2)
            c_boven = c.y + (c.hoogte / 2)

            if (dino_rechts > c_links and dino_links < c_rechts and
                dino_boven > c_onder and dino_onder < c_boven):
                self.game_over = True


# --- VIEW ---
class DinoView(arcade.Sprite):
    def __init__(self, model: DinoModel, texture: arcade.Texture, offset_y: int):
        super().__init__(texture)
        self.center_x = model.x
        self.center_y = model.y + offset_y

class CactusView(arcade.Sprite):
    def __init__(self, model: CactusModel, texture: arcade.Texture, offset_y: int):
        super().__init__(texture)
        self.center_x = model.x
        self.center_y = model.y + offset_y

class DinoGameView:
    model: DinoGameModel
    sprites: arcade.SpriteList
    offset_y: int

    dino_texture: arcade.Texture
    cactus_textures: dict[CactusModellen, arcade.Texture]

    def __init__(self, model: DinoGameModel):
        self.model = model
        self.sprites = arcade.SpriteList()
        self.offset_y = 50

        self.dino_texture = self.make_texture(self.model.dino.breedte, self.model.dino.hoogte, "white")

        self.cactus_textures = {
            CactusModellen.SMALL: self.make_texture(20, 20, "green"),
            CactusModellen.MEDIUM: self.make_texture(20, 40, "green"),
            CactusModellen.BIG: self.make_texture(40, 40, "green")
        }

    def make_texture(self, breedte: int, hoogte: int, color: str) -> arcade.Texture:
        image = Image.new('RGBA', (breedte, hoogte), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle([0, 0, breedte - 1, hoogte - 1], outline="black", fill=color)
        return arcade.Texture(image)

    def refresh(self):
        self.sprites.clear()

        dino_sprite = DinoView(self.model.dino, self.dino_texture, self.offset_y)
        self.sprites.append(dino_sprite)

        for c in self.model.cactussen:
            # Pak de juiste texture op basis van de enum!
            texture = self.cactus_textures[c.cactusmodel]
            cactus_sprite = CactusView(c, texture, self.offset_y)
            self.sprites.append(cactus_sprite)

    def draw(self):
        grond_y = self.model.dino.ground_y - (self.model.dino.hoogte / 2) + self.offset_y
        arcade.draw_line(0, grond_y, self.model.BREEDTE, grond_y, arcade.color.BLACK, 2)

        self.sprites.draw()

        if self.model.game_over:
            arcade.draw_text(
                "GAME OVER!",
                self.model.BREEDTE / 2,
                self.model.HOOGTE / 2 + self.offset_y,
                arcade.color.RED, 40, anchor_x="center", anchor_y="center"
            )


# --- UI VIEW ---
class UIView:
    manager: arcade.gui.UIManager
    restart_button: arcade.gui.UIFlatButton
    model: DinoGameModel
    score_label: arcade.gui.UILabel
    highscore_label: arcade.gui.UILabel

    def __init__(self, snake_model: DinoGameModel):
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.model = snake_model

        self.restart_button = arcade.gui.UIFlatButton(text="Restart", width=100, height=40)
        self.score_label = arcade.gui.UILabel(text="Score: 0", width=150, height=40, text_color=arcade.color.BLACK)
        self.highscore_label = arcade.gui.UILabel(text="High Score: 0", width=150, height=40, text_color=arcade.color.BLACK)

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
    my_model: DinoGameModel
    my_view: DinoGameView
    ui_view: UIView

    def __init__(self, model: DinoGameModel, view: DinoGameView, breedte: int, hoogte: int):
        super().__init__(width=breedte, height=hoogte, title="MVC Dino", pixel_perfect=True, resizable=False)
        arcade.set_background_color(arcade.color.WHITE)

        self.my_model = model
        self.my_view = view
        self.ui_view = UIView(model)

        @self.ui_view.restart_button.event("on_click")
        def on_click_restart(event: arcade.gui.UIEvent):
            self.restart()

    def restart(self):
        self.my_model.reset()
        self.my_view.refresh()
        self.ui_view.refresh()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            self.my_model.dino.jump()

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
    BREEDTE: int = 800
    HOOGTE: int = 400

    model = DinoGameModel()
    view = DinoGameView(model)
    controller = GameController(model, view, BREEDTE, HOOGTE)

    arcade.run()
