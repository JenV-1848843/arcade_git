import random
import arcade
import arcade.gui
from PIL import Image, ImageDraw, ImageFont


# --- MODEL ---
class CircleModel:
    def __init__(self):
        self.teller = 5

    def increment(self):
        self.teller = self.teller + 1


# --- VIEW ---
class CircleView(arcade.Sprite):
    def __init__(self, model: CircleModel, width: int, height: int, **kwargs):
        super().__init__()
        self.model = model
        self.img_width = width
        self.img_height = height
        self.font = ImageFont.truetype("arial.ttf", 18)
        self.redraw()

    def redraw(self):
        image = Image.new('RGBA', (self.img_width, self.img_height), color=(255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        radius = self.model.teller * 2  # radius grows with teller
        cx = self.img_width / 2
        cy = self.img_height / 2
        draw.circle((cx, cy), radius, fill="blue")
        draw.text((cx, cy), str(self.model.teller), fill="white", font=self.font, anchor="mm")
        self.texture = arcade.Texture(image)

class DotsView(arcade.Sprite):
    def __init__(self, model: CircleModel, width: int, height: int, **kwargs):
        super().__init__()
        self.model = model
        self.img_width = width
        self.img_height = height
        self.dot_radius = 4
        self.redraw()

    def redraw(self):
        image = Image.new('RGBA', (self.img_width, self.img_height), color=(255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        for _ in range(self.model.teller):
            x = random.randrange(self.dot_radius, self.img_width - self.dot_radius)
            y = random.randrange(self.dot_radius, self.img_height - self.dot_radius)
            draw.circle((x, y), self.dot_radius, fill="red")

        self.texture = arcade.Texture(image)

class SuperView:
    def __init__(self, model: CircleModel):
        self.model = model
        self.sprites = arcade.SpriteList()

        self.circleview = CircleView(self.model, 400, 400)
        self.circleview.center_x = 200
        self.circleview.center_y = 250
        self.sprites.append(self.circleview)

        self.dotsview = DotsView(self.model, 200, 200)
        self.dotsview.center_x = 200
        self.dotsview.center_y = 200
        self.sprites.append(self.dotsview)

    def redraw(self):
        self.circleview.redraw()
        self.dotsview.redraw()

    def draw(self):
        self.sprites.draw()


# --- CONTROLLER ---
class GameController(arcade.Window):
    def __init__(self, model: CircleModel, my_view: SuperView):
        super().__init__(400, 450, "MVC Cirkel en Punten", pixel_perfect=True)
        arcade.set_background_color(arcade.color.WHITE)
        self.model = model

        self.superview = my_view

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.increase_button = arcade.gui.UIFlatButton(text="Increase", width=150, height=40)
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(self.increase_button, anchor_x="center_x", anchor_y="bottom", align_y=20)
        self.manager.add(anchor)

        @self.increase_button.event("on_click")
        def on_click_increase(event):
            self.increase()

    def increase(self):
        self.model.increment()
        self.superview.redraw()

    def on_draw(self):
        self.clear()
        self.superview.draw() # views
        self.manager.draw() # UI elements like button


# --- STARTUP ---
if __name__ == "__main__":
    model = CircleModel()
    view = SuperView(model)
    controller = GameController(model, view)
    arcade.run()
