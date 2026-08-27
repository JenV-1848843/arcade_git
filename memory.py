import arcade
import random

class CardModel():
    value: int
    def __init__(self, start_waarde: int = 0):
        self.value = start_waarde

    def reveal(self):
        return self.value


class MemoryController(arcade.Window):
    def __init__(self):
        super().__init__(400, 450, "MVC Memory", pixel_perfect=True)
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        self.clear()

class MemoryView(arcade.View):
    def __init__(self):
        pass



class MemoryModel:
    kaarten: list[CardModel]
    def __init__(self, aantal_kaarten: int = 10):
        if aantal_kaarten % 2 == 0:
            self.kaarten = []

            aantal_paren = aantal_kaarten // 2

            waardes = []
            for i in range(1, aantal_paren + 1):
                waardes.append(i)
                waardes.append(i)

            random.shuffle(waardes)

            for waarde in waardes:
                self.kaarten.append(CardModel(start_waarde=waarde))

    def print_kaarten(self):
        for kaarten in self.kaarten:
            print(kaarten.reveal())




if __name__ == "__main__":
    model = MemoryModel()
    model.print_kaarten()
    controller = MemoryController()
    view = MemoryView()

    arcade.run()
