import arcade
import arcade.gui
import random

class CardModel():
    value: int
    flipped: bool
    def __init__(self, start_waarde: int = 0):
        self.flipped = False
        self.found = False
        self.value = start_waarde

    def reveal(self):
        self.flipped = True

    def is_found(self):
        return self.found

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


        self.rectangle = arcade.rect.XYWH(
            self.card_x,
            self.card_y,
            self.card_breedte,
            self.card_hoogte
        )

    def get_model(self) -> CardModel:
        return self.model

    def draw(self):
        if self.model.flipped or self.model.found:
            arcade.draw_rect_filled(self.rectangle, self.card_color_flipped)
            self.draw_number()
        else:
            arcade.draw_rect_filled(self.rectangle, self.card_color)


    def draw_number(self):
        waarde = self.model.value

        arcade.draw_text(
            text=waarde,
            x=self.card_x,
            y=self.card_y,
            color=arcade.color.BLACK,
            font_size=20,
            anchor_x="center",
            anchor_y="center"
        )


class MemoryModel:
    kaarten: list[CardModel]
    aantal_kaarten: int
    def __init__(self, aantal_kaarten: int = 10):
        self.set_kaarten(aantal_kaarten)
        self.wacht_op_terugdraaien = False
        self.timer = 0.0

    def set_kaarten(self, aantal_kaarten: int):
        if aantal_kaarten % 2 == 0:
            self.kaarten = []
            self.aantal_kaarten = aantal_kaarten

            aantal_paren = aantal_kaarten // 2

            waardes = []
            for i in range(1, aantal_paren + 1):
                waardes.append(i)
                waardes.append(i)

            random.shuffle(waardes)

            for waarde in waardes:
                self.kaarten.append(CardModel(start_waarde=waarde))


    def update(self, delta_time: float):
        if self.wacht_op_terugdraaien:
            self.timer += delta_time
            if self.timer >= 0.5:
                for kaart in self.kaarten:
                    if kaart.flipped and not kaart.found:
                        kaart.flipped = False
                self.wacht_op_terugdraaien = False
                self.timer = 0.0


    def update_kaarten(self):
        flipped_cards = []

        for kaart in self.kaarten:
            if kaart.flipped and not kaart.found:
                flipped_cards.append(kaart)

        if len(flipped_cards) == 2:
            kaart1 = flipped_cards[0]
            kaart2 = flipped_cards[1]

            if kaart1.value == kaart2.value:
                kaart1.found = True
                kaart2.found = True
            else:
                self.wacht_op_terugdraaien = True


    def get_kaarten(self):
        return self.kaarten

class MemoryView(arcade.View):
    kaartenviews: list[CardView]
    kaartbreedte: int
    kaarthoogte: int
    marge: int
    hoogte_tov_onderkant: int
    afstand_linkerkant: int
    aantal_kolommen: int

    def __init__(self, model: MemoryModel, breedte: int):
        self.kaartenviews = []
        self.kaartbreedte = 50
        self.kaarthoogte = 70
        self.marge = 10
        self.afstand_linkerkant = 50
        self.hoogte_tov_onderkant = 100
        self.aantal_kolommen = breedte // (self.kaartbreedte + self.marge)
        for index, kaart in enumerate(model.kaarten):
            rij = index // self.aantal_kolommen
            kolom = index % self.aantal_kolommen

            translate_x = self.afstand_linkerkant + (kolom * (self.kaartbreedte + self.marge))
            translate_y = self.hoogte_tov_onderkant + (rij * (self.kaarthoogte + self.marge))

            kaartview = CardView(kaart, translate_x, translate_y, self.kaartbreedte, self.kaarthoogte)
            self.kaartenviews.append(kaartview)

    def on_draw(self):
        for kaart in self.kaartenviews:
            kaart.draw()

    def flipt_kaart_op_positie(self, x: float, y: float):
        kolom = (x - self.afstand_linkerkant + self.kaartbreedte // 2) // (self.kaartbreedte + self.marge)
        rij = (y - self.hoogte_tov_onderkant + self.kaarthoogte // 2) // (self.kaarthoogte + self.marge)

        if kolom < 0 or rij < 0:
            return None

        index = int(rij) * self.aantal_kolommen + int(kolom)

        if index < 0 or index >= len(self.kaartenviews):
            return None

        kaartview = self.kaartenviews[index]

        binnen_x = kaartview.card_x - kaartview.card_breedte / 2 <= x <= kaartview.card_x + kaartview.card_breedte / 2
        binnen_y = kaartview.card_y - kaartview.card_hoogte / 2 <= y <= kaartview.card_y + kaartview.card_hoogte / 2

        if not (binnen_x and binnen_y):
            return None

        # kaartview.get_model().reveal()
        return kaartview.get_model()

class MemoryController(arcade.Window):
    model: MemoryModel
    memory_view: MemoryView

    def __init__(self, model, view, breedte: int, hoogte: int):
        super().__init__(breedte, hoogte, "MVC Memory", pixel_perfect=True)
        arcade.set_background_color(arcade.color.WHITE)
        self.model = model
        self.memory_view = view
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # The actual input field
        self.number_input = arcade.gui.UIInputText(
            x=100, y=150, width=150, height=40,
            text="0", font_size=18,
            text_color=arcade.color.BLACK,
            border_color=arcade.color.BLACK,
            caret_color=arcade.color.BLACK,
        )
        self.submit_button = arcade.gui.UIFlatButton(text="Begin", width=150, height=40)

        # wire up the click handler
        @self.submit_button.event("on_click")
        def on_click_submit(event):
            number = self.get_input_number()
            self.model.set_kaarten(number)
            self.memory_view = MemoryView(self.model, breedte)
            # self.model.set_aantal_kaarten(number)

        # Anchor it somewhere on screen
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=self.number_input, anchor_x="left", anchor_y="top")
        anchor.add(child=self.submit_button, anchor_x="right", anchor_y="top")
        self.manager.add(anchor)

    def on_draw(self):
        self.clear()
        self.memory_view.on_draw()
        self.manager.draw()

    def on_update(self, delta_time: float):
        self.model.update(delta_time)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.model.wacht_op_terugdraaien:
                return

            open_kaarten = [k for k in self.model.get_kaarten() if k.is_flipped() and not k.is_found()]
            if len(open_kaarten) >= 2:
                return

            print(f"Left click at ({x}, {y})")
            card_model = self.memory_view.flipt_kaart_op_positie(x, y)
            if card_model:
                card_model.reveal()
                self.model.update_kaarten()

    def get_input_number(self):
        try:
            return int(self.number_input.text)
        except ValueError:
            return 0

if __name__ == "__main__":
    breedte = 400
    hoogte = 450
    model = MemoryModel()
    controller = MemoryController(model, None, breedte, hoogte)
    view = MemoryView(model, breedte)
    controller.memory_view = view
    # controller.show_view()

    arcade.run()
