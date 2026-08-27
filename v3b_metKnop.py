import random
import arcade

# --- MODEL ---
class CircleModel:
    def __init__(self):
        self.teller = 5

    def increment(self):
        self.teller = self.teller + 1

# --- VIEW ---
class CircleView:
    circle: arcade.shape_list.ShapeElementList
    circle_center_x: int
    circle_center_y: int
    translate_x: int
    tanslate_y: int
    buffer: int
    model: CircleModel
    text: arcade.Text

    def __init__(self, model):
        self.circle_center_x = 200
        self.circle_center_y = 240

        self.model = model

        self.buffer = -1

        self.text = arcade.Text(
            str(self.model.teller), self.circle_center_x, self.circle_center_y, arcade.color.WHITE, 14,
            anchor_x="center", anchor_y="center",
        )

    def create_circle(self):
       self.circle = arcade.shape_list.ShapeElementList()
       circle = arcade.shape_list.create_ellipse_filled(self.circle_center_x, self.circle_center_y, self.model.teller * 5, self.model.teller * 5, arcade.color.BLUE)
       self.circle.append(circle)

    def draw(self):
        if self.buffer != self.model.teller:
            self.create_circle()
            self.text.text = str(self.model.teller)
            self.buffer = self.model.teller

        self.circle.center_x = self.translate_x
        self.circle.center_y = self.tanslate_y
        self.circle.draw()

        self.text.x = self.circle_center_x + self.translate_x
        self.text.y = self.circle_center_y + self.tanslate_y
        self.text.draw()

    def translate(self, x, y):
        self.translate_x = x
        self.tanslate_y = y

class ManyCirclesView:
    dots: arcade.shape_list.ShapeElementList
    dots_center_x: int
    dots_center_y: int
    translate_x: int
    tanslate_y: int
    buffer: int
    model: CircleModel

    def __init__(self, model):
        self.model = model
        self.buffer = -1

        self.dots_center_x = 100
        self.dots_center_y = 100

    def create_dots(self):
        self.dots = arcade.shape_list.ShapeElementList()
        for i in range(1, self.model.teller + 1):
           x = random.randrange(1,200)
           y = random.randrange(1, 200)
           dot = arcade.shape_list.create_ellipse_filled(x, y, 4, 4, arcade.color.RED)
           self.dots.append(dot)

    def draw(self):
        if self.buffer != self.model.teller:
            self.create_dots()
            self.buffer = self.model.teller
        self.dots.center_x = self.dots_center_x
        self.dots.center_y = self.dots_center_y
        self.dots.draw()

    def translate(self, x, y):
        self.translate_x = x
        self.tanslate_y = y

class SuperView:
    def __init__(self, model):
        self.model = model
        self.een = CircleView(self.model)
        self.veel = ManyCirclesView(self.model)

    def draw(self):
        self.een.translate(100, 50)
        self.een.draw()
        self.veel.translate(100, 50)
        self.veel.draw()

# --- CONTROLLER ---
class GameController(arcade.Window):
    model: CircleModel
    my_view : SuperView

    def __init__(self, model, view):
        super().__init__(400, 450, "MVC Cirkel en Punten",pixel_perfect=True)
        self.model = model
        self.my_view = view
        arcade.set_background_color(arcade.color.WHITE)

    def increase(self):
        self.model.increment()

    def on_button_click(self, event):
        self.increase()

    def on_draw(self):
        self.clear()
        self.my_view.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            self.increase()


# --- STARTUP ---
if __name__ == "__main__":
    model = CircleModel()
    view = SuperView(model)
    controller = GameController(model, view)

    arcade.run()