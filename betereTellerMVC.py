import arcade


# --- MODEL ---
class CircleModel:
    def __init__(self):
        self.teller = 5

    def increment(self):
        self.teller = self.teller+1


# --- VIEW ---
class CircleView:
    def __init__(self, model):
        self.model = model

    def draw(self):
        # De View bevat de specifieke tekenlogica
        arcade.draw_circle_filled(200, 200, self.model.teller, arcade.color.BLUE)
        arcade.draw_text(self.model.teller, 20, 20, arcade.color.BLACK, 20)
        arcade.set_background_color(arcade.color.YELLOW)


# --- CONTROLLER ---
class GameController(arcade.Window):
    def __init__(self, model, view):
        super().__init__(500, 400, "Strikte MVC Cirkel",pixel_perfect=True)
        self.model = model
        self.myView = view


    def on_draw(self):
        self.clear()
        # Controller delegeert de weergave volledig aan de View
        self.myView.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            # Controller verwerkt invoer en stuurt de verandering naar het Model
            self.model.increment()


# --- STARTUP ---
if __name__ == "__main__":
    model = CircleModel()
    view = CircleView(model)
    controller = GameController(model, view)

    arcade.run()