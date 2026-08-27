import arcade
import random

class CardModel():
    value: int
    flipped: bool
    def __init__(self, start_waarde: int = 0):
        self.flipped = False
        self.value = start_waarde

    def reveal(self):
        self.flipped = True
        return self.value

    def is_flipped(self):
        return self.flipped



class CardView:
    rectangle: arcade.Rect
    card_breedte: int
    card_hoogte: int
    card_x: float
    card_y: float

    def __init__(self, card_model: CardModel, x: float, y: float, card_breedte: int, card_hoogte: int):
        self.model = card_model
        self.card_breedte = card_breedte
        self.card_hoogte = card_hoogte
        self.card_x = x
        self.card_y = y
        self.card_color = arcade.color.GREEN
        self.card_color_flipped = arcade.color.BLUE

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
        if self.model.is_flipped():
            arcade.draw_rect_filled(self.rectangle, self.card_color_flipped)
            self.draw_number()
        else:
            arcade.draw_rect_filled(self.rectangle, self.card_color)


    def draw_number(self):
        waarde = self.model.reveal()

        arcade.draw_text(
            text=waarde,
            x=self.card_x,      # Aangepast van start_x naar x
            y=self.card_y,      # Aangepast van start_y naar y
            color=arcade.color.BLACK,
            font_size=20,
            anchor_x="center",
            anchor_y="center"
        )


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

class MemoryView:
    kaartenviews: list[CardView]
    kaartbreedte: int
    kaarthoogte: int
    marge: int
    hoogte_tov_onderkant: int
    afstand_linkerkant: int

    def __init__(self, model: MemoryModel):
        super().__init__()

        self.kaartenviews = []
        self.kaartbreedte = 50
        self.kaarthoogte = 70
        self.marge = 10
        self.afstand_linkerkant = 50
        self.hoogte_tov_onderkant = 100
        for index, kaart in enumerate(model.kaarten):
            breedte = 400
            aantal_kolommen = breedte // (self.kaartbreedte + self.marge)
            rij = index // aantal_kolommen
            kolom = index % aantal_kolommen

            translate_x = self.afstand_linkerkant + (kolom * (self.kaartbreedte + self.marge))
            translate_y = self.hoogte_tov_onderkant + (rij * (self.kaarthoogte + self.marge))

            kaartview = CardView(kaart, translate_x, translate_y, self.kaartbreedte, self.kaarthoogte)
            self.kaartenviews.append(kaartview)

    def on_draw(self):
        for kaart in self.kaartenviews:
            kaart.draw()

class MemoryController(arcade.Window):
    model: MemoryModel
    memory_view: MemoryView

    def __init__(self, model, view):
        super().__init__(400, 450, "MVC Memory", pixel_perfect=True)
        arcade.set_background_color(arcade.color.WHITE)
        self.model = model
        self.memory_view = view

    def on_draw(self):
        self.clear()
        self.memory_view.on_draw()




if __name__ == "__main__":
    model = MemoryModel()
    view = MemoryView(model)
    controller = MemoryController(model, view)


    # controller.show_view(view)

    arcade.run()
