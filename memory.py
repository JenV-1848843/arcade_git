import arcade

class MemoryController(arcade.Window):
    def __init__(self):
        super().__init__(400, 450, "MVC Memory", pixel_perfect=True)
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        self.clear()

class MemoryView(arcade.View):
    def __init__(self):
        super().__init__()

class MemoryModel(arcade.View):
    def __init__(self, start_waarde = 0):
        self.x : float= 0.0
        self.y : float= 0.0
        self.value : int = start_waarde

    def reveal(self):
        return self.value



if __name__ == "__main__":
    controller = MemoryController()
    arcade.run()