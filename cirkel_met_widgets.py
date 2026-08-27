import random
import arcade
import arcade.gui

# --- MODEL ---
class CircleModel:
    def __init__(self):
        self.teller = 5

    def increment(self):
        self.teller = self.teller + 1


# --- VIEW ---
class CircleView(arcade.gui.UIWidget):
    def __init__(self, model: CircleModel, width:int, height:int, **kwargs):
        super().__init__(width=width, height=height, **kwargs)
        self.model = model
        self.buffer = -1
        self.circle = None
        self.text = arcade.Text(
            str(self.model.teller),
            self.width / 2, self.height / 2,
            arcade.color.WHITE, 14,
            anchor_x="center", anchor_y="center",
            )

    def create_circle(self):
        self.circle = arcade.shape_list.ShapeElementList()
        straal = self.model.teller * 5
        circle = arcade.shape_list.create_ellipse_filled(
            self.width / 2, self.height / 2, straal, straal, arcade.color.BLUE
        )
        self.circle.append(circle)

    def on_update(self, dt):
        if self.buffer != self.model.teller:
            self.create_circle()
            self.text.text = str(self.model.teller)
            self.buffer = self.model.teller
            self.trigger_full_render()

    def do_render(self, surface):
        self.prepare_render(surface)
        if self.circle is None:
            self.create_circle()
        self.circle.draw()
        self.text.draw()


class ManyCirclesView(arcade.gui.UIWidget):
    def __init__(self, model: CircleModel, **kwargs):
        super().__init__(width=200, height=200, **kwargs)
        self.model = model
        self.buffer = -1
        self.dots = None

    def create_dots(self):
        self.dots = arcade.shape_list.ShapeElementList()
        for _ in range(self.model.teller):
            x = random.randrange(1, int(self.width))
            y = random.randrange(1, int(self.height))
            dot = arcade.shape_list.create_ellipse_filled(x, y, 4, 4, arcade.color.RED)
            self.dots.append(dot)

    def on_update(self, dt):
        if self.buffer != self.model.teller:
            self.create_dots()
            self.buffer = self.model.teller
            self.trigger_full_render()

    def do_render(self, surface):
        self.prepare_render(surface)
        if self.dots is None:
            self.create_dots()
        self.dots.draw()


# --- CONTROLLER ---
class GameController(arcade.Window):
    width:int
    height:int

    def __init__(self, model: CircleModel):
        super().__init__(400, 450, "MVC Cirkel en Punten", pixel_perfect=True)
        arcade.set_background_color(arcade.color.WHITE)
        self.model = model

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        een = CircleView(self.model, 700, 700)
        een.rect = een.rect.align_x(80).align_y(200)   # manual position, no anchor layout

        veel = ManyCirclesView(self.model)
        veel.rect = veel.rect.align_x(200).align_y(200)

        self.manager.add(een)
        self.manager.add(veel)

        self.increase_button = arcade.gui.UIFlatButton(text="Increase", width=150, height=40)

        @self.increase_button.event("on_click")
        def on_click_increase(event):
            self.increase()

        self.manager.add(self.increase_button)

    def increase(self):
        self.model.increment()

    def on_draw(self):
        self.clear()
        self.manager.draw()

    # def on_key_press(self, key, modifiers):
    #     if key == arcade.key.ENTER:
    #         self.increase()


# --- STARTUP ---
if __name__ == "__main__":
    model = CircleModel()
    controller = GameController(model)
    arcade.run()
