import arcade
import random

class CardModel():
    value: int
    def __init__(self, start_waarde: int = 0):
        self.value = start_waarde

    def reveal(self):
        return self.value

class CardView(arcade.View):
    rectangle: arcade.Rect
    card_breedte: int
    card_hoogte: int
    card_x: float
    card_y: float
    card_color: arcade.color

    def __init__(self,card_model: CardModel):
        self.card_hoogte = 50
        self.card_x = 20
        self.card_y = 20
        self.card_color = arcade.color.GREEN
        self.rectangle = arcade.Rect(self.card_x, self.card_y, self.card_hoogte, self.card_x, self.card_y)

    def draw(self):
        self.rectangle.center = (self.card_x, self.card_y)
        arcade.draw_rect(self.rectangle, self.card_color)



class MemoryController(arcade.Window):
    def __init__(self):
        super().__init__(400, 450, "MVC Memory", pixel_perfect=True)
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        self.clear()







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

    def kaarten(self):
        return self.kaarten

class MemoryView(arcade.View):
    kaartenviews: list[CardView]
    def __init__(self, model: MemoryModel):
        for kaart in model.kaarten:
            kaartview = CardView(kaart)
            self.kaartenviews.append(kaartview)

    def draw(self):
        self.clear()
        for kaart in self.kaartenviews:
            kaart.draw()



if __name__ == "__main__":
    model = MemoryModel()
    model.print_kaarten()
    view = MemoryView(model)
    controller = MemoryController()

    arcade.run()
