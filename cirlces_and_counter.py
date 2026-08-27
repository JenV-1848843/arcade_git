import random
import arcade
import arcade.gui

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 400
WINDOW_TITLE = "MVC Counter Demo (Arcade)"


# --------------------------------------------------------------------------
# MODEL
# --------------------------------------------------------------------------
class CounterModel:
    """Owns the counter value. Knows nothing about Arcade or drawing."""

    def __init__(self):
        self.counterValue = 0

    # def get_counter(self):
    #     return self.counterValue

    def increment_counter(self):
        self.counterValue += 1


# --------------------------------------------------------------------------
# CUSTOM UI WIDGETS
# --------------------------------------------------------------------------
class CircleWidget(arcade.gui.UIWidget):
    """A UI widget that draws a bordered box with a blue circle inside it."""

    def __init__(self, size, **kwargs):
        super().__init__(width=size, height=size, **kwargs)
        self.radius = 10
        self.max_radius = size / 2 - 5

    def do_render(self, surface):
        self.prepare_render(surface)
        # All draw calls below are relative to this widget's own 0,0 (bottom-left)
        arcade.draw_lbwh_rectangle_outline(0, 0, self.width, self.height, arcade.color.GRAY, 1)
        center_x = self.width / 2
        center_y = self.height / 2
        arcade.draw_circle_filled(center_x, center_y, self.radius, arcade.color.BLUE)

    def set_value(self, value):
        raw_radius = 10 + value * 8
        self.radius = min(raw_radius, self.max_radius)
        self.trigger_render()


class DotsWidget(arcade.gui.UIWidget):
    """A UI widget that draws a bordered box with random black dots inside it."""

    def __init__(self, width, height, **kwargs):
        super().__init__(width=width, height=height, **kwargs)
        self.dot_positions = []

    def do_render(self, surface):
        self.prepare_render(surface)
        arcade.draw_lbwh_rectangle_outline(0, 0, self.width, self.height, arcade.color.GRAY, 1)
        for x, y in self.dot_positions:
            arcade.draw_circle_filled(x, y, 3, arcade.color.BLACK)

    def set_value(self, value):
        margin = 10
        positions = []
        for _ in range(value):
            x = random.uniform(margin, self.width - margin)
            y = random.uniform(margin, self.height - margin)
            positions.append((x, y))
        self.dot_positions = positions
        self.trigger_render()


# --------------------------------------------------------------------------
# VIEW
# --------------------------------------------------------------------------
class CounterView(arcade.Window):
    """Builds the window. All drawing now goes through the UIManager."""

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        arcade.set_background_color(arcade.color.WHITE)

        self.controller = None

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        # --- Button (top-left) ---
        self.button = arcade.gui.UIFlatButton(text="Increase Counter", width=190, height=40)
        self.button.on_click = self.on_button_click
        self.button.left = 20
        self.button.top = WINDOW_HEIGHT - 20
        self.ui_manager.add(self.button)

        # --- Counter label, right of the button ---
        self.counter_label = arcade.gui.UILabel(
            text="Counter: 0",
            font_size=16,
            text_color=arcade.color.BLACK,
        )
        self.counter_label.left = self.button.right + 20
        self.counter_label.top = self.button.top
        self.ui_manager.add(self.counter_label)

        # --- Blue circle region (bottom-left) ---
        circle_size = 250
        self.circle_widget = CircleWidget(size=circle_size)
        self.circle_widget.left = 20
        self.circle_widget.bottom = 30
        self.ui_manager.add(self.circle_widget)

        # --- Random dots region (bottom-right of circle region) ---
        dots_left = 20 + circle_size + 20
        dots_width = WINDOW_WIDTH - dots_left - 20
        self.dots_widget = DotsWidget(width=dots_width, height=circle_size)
        self.dots_widget.left = dots_left
        self.dots_widget.bottom = 30
        self.ui_manager.add(self.dots_widget)

    def set_controller(self, controller):
        self.controller = controller

    # ----- state updates, called by the Controller -------------------------
    def update_counter(self, value):
        self.counter_label.text = f"Counter: {value}"

    def update_circle(self, value):
        self.circle_widget.set_value(value)

    def update_dots(self, value):
        self.dots_widget.set_value(value)

    # ----- Arcade lifecycle callbacks ---------------------------------------
    def on_draw(self):
        self.clear()
        self.ui_manager.draw()

    def on_button_click(self, event):
        if self.controller is not None:
            self.controller.on_increase_button_clicked()


# --------------------------------------------------------------------------
# CONTROLLER
# --------------------------------------------------------------------------
class CounterController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.set_controller(self)
        self.on_counter_changed(self.model.counterValue)

    def on_increase_button_clicked(self):
        self.model.increment_counter()
        self.on_counter_changed(self.model.counterValue)

    def on_counter_changed(self, value):
        self.view.update_counter(value)
        self.view.update_circle(value)
        self.view.update_dots(value)


# --------------------------------------------------------------------------
# ENTRY POINT
# --------------------------------------------------------------------------
def main():
    model = CounterModel()
    view = CounterView()
    CounterController(model, view)
    arcade.run()


if __name__ == "__main__":
    main()
