import arcade
import random

class CardModel():
    value: int
    def __init__(self, start_waarde: int = 0):
        self.value = start_waarde

    def reveal(self):
        return self.value

class CardView:
    rectangle: arcade.Rect
    card_breedte: int
    card_hoogte: int
    card_x: float
    card_y: float

    def __init__(self, card_model: CardModel):
        self.model = card_model
        self.card_breedte = 50
        self.card_hoogte = 70
        self.card_x = 50
        self.card_y = 50
        self.card_color = arcade.color.GREEN

        self.rectangle = arcade.rect.Rect(
            self.card_x - (self.card_breedte // 2),
            self.card_x + (self.card_breedte // 2),
            self.card_y - (self.card_hoogte // 2),
            self.card_y + (self.card_hoogte // 2),
            self.card_breedte,
            self.card_hoogte,
            self.card_x,
            self.card_y
        )

    def draw(self):
        arcade.draw_rect_filled(self.rectangle, self.card_color)



class MemoryController(arcade.Window):
    def __init__(self):
        super().__init__(400, 450, "MVC Memory", pixel_perfect=True)
        arcade.set_background_color(arcade.color.WHITE)

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
        super().__init__()
        self.kaartenviews = []
        for kaart in model.kaarten:
            kaartview = CardView(kaart)
            self.kaartenviews.append(kaartview)

    def on_draw(self):
        self.clear()
        for kaart in self.kaartenviews:
            kaart.draw()



if __name__ == "__main__":
    model = MemoryModel()
    model.print_kaarten()

    controller = MemoryController()

    view = MemoryView(model)

    controller.show_view(view)

    arcade.run()
