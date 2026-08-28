import arcade
import arcade.gui
import random

from PIL import Image, ImageDraw


class CardModel():
    value: int
    flipped: bool
    found: bool

    def __init__(self, start_waarde: int = 0):
        self.flipped = False
        self.found = False
        self.value = start_waarde

    def get_value(self):
        return self.value

    def set_found(self):
        self.found = True


class CardView(arcade.Sprite):
    model: CardModel
    card_breedte: int
    card_hoogte: int
    center_x: float
    center_y: float
    card_texture: arcade.Texture
    card_flipped_texture: arcade.Texture

    def __init__(self, card_model: CardModel, x: float, y: float, card_breedte: int, card_hoogte: int):
        super().__init__()
        self.model = card_model
        self.card_breedte = card_breedte
        self.card_hoogte = card_hoogte
        self.center_x = x
        self.center_y = y

        self.card_texture = self.make_cardview_texture("blue", toon_cijfer=False)
        self.card_flipped_texture = self.make_cardview_texture("red", toon_cijfer=True)

        self.update_texture()

    def make_cardview_texture(self, kleur: str, toon_cijfer: bool):
        image = Image.new('RGBA', (self.card_breedte, self.card_hoogte), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)

        draw.rectangle([0, 0, self.card_breedte, self.card_hoogte], fill=kleur)

        if toon_cijfer:
            draw.text(
                (self.card_breedte // 2 - 8, self.card_hoogte // 2 - 10),
                text=str(self.model.value),
                font_size=25,
                fill=(0, 0, 0, 255)
            )

        return arcade.Texture(image)

    def update_texture(self):
        if self.model.flipped or self.model.found:
            self.texture = self.card_flipped_texture
        else:
            self.texture = self.card_texture

class MemoryModel:
    kaarten: list[CardModel]
    aantal_kaarten: int
    timer: float

    def __init__(self, aantal_kaarten: int = 10):
        self.set_kaarten(aantal_kaarten)
        self.wacht_op_terugdraaien = False
        self.timer = 0.0

    def set_kaarten(self, aantal_kaarten_paren: int):
        aantal_kaarten = aantal_kaarten_paren * 2

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

            if kaart1.get_value() == kaart2.get_value():
                kaart1.set_found()
                kaart2.set_found()
            else:
                self.wacht_op_terugdraaien = True


class MemoryView:
    def __init__(self, model: MemoryModel, breedte: int):
        self.kaartenviews = arcade.SpriteList[CardView]()
        self.kaartbreedte = 50
        self.kaarthoogte = 70
        self.marge = 10
        self.afstand_linkerkant = 50
        self.hoogte_tov_onderkant = 100

        self.aantal_kolommen = breedte // (self.kaartbreedte + self.marge)
        if self.aantal_kolommen == 0:
            self.aantal_kolommen = 1

        for index, kaart in enumerate(model.kaarten):
            rij = index // self.aantal_kolommen
            kolom = index % self.aantal_kolommen

            translate_x = self.afstand_linkerkant + (kolom * (self.kaartbreedte + self.marge))
            translate_y = self.hoogte_tov_onderkant + (rij * (self.kaarthoogte + self.marge))

            kaartview = CardView(kaart, translate_x, translate_y, self.kaartbreedte, self.kaarthoogte)
            self.kaartenviews.append(kaartview)

    def on_draw(self):
        for kaart in self.kaartenviews:
            kaart.update_texture()
        self.kaartenviews.draw()



class MemoryController(arcade.Window):
    model: MemoryModel
    view: MemoryView
    breedte: int
    hoogte: int
    def __init__(self, model: MemoryModel, view: MemoryView, breedte: int, hoogte: int):
        super().__init__(breedte, hoogte, "MVC Memory", pixel_perfect=True)
        arcade.set_background_color(arcade.color.WHITE)
        self.model = model
        self.memory_view = view
        self.scherm_breedte = breedte

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.number_input = arcade.gui.UIInputText(
            x=10, y=10, width=150, height=40,
            text="10", font_size=18,
            text_color=arcade.color.WHITE,
        )

        self.input_bg = arcade.gui.UIFlatButton(x=10, y=10, width=150, height=40, text="")

        self.submit_button = arcade.gui.UIFlatButton(
            x=170, y=10, text="Start/Reset", width=150, height=40
        )

        @self.submit_button.event("on_click")
        def on_click_submit(event):
            number = self.get_input_number()
            if number > 0:
                self.model.set_kaarten(number)
                self.memory_view = MemoryView(self.model, self.scherm_breedte)

        self.manager.add(self.input_bg)
        self.manager.add(self.number_input)
        self.manager.add(self.submit_button)

    def on_draw(self):
        self.clear()
        self.memory_view.on_draw()
        self.manager.draw()

    def on_update(self, delta_time: float):
        self.model.update(delta_time)

    def aantal_kaarten_gedraait(self):
        aantal_open = 0
        for kaart in self.model.kaarten:
            if kaart.flipped and not kaart.found:
                aantal_open += 1
        return aantal_open

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.model.wacht_op_terugdraaien:
                return

            if self.aantal_kaarten_gedraait() >= 2:
                return

            card_sprites: list[CardView] = arcade.get_sprites_at_point((x, y), self.memory_view.kaartenviews)
            if len(card_sprites) == 1:
                card_model = card_sprites[0].model
                if card_model and not card_model.flipped and not card_model.found:
                    card_model.flipped = True
                    self.model.update_kaarten()

    def get_input_number(self):
        try:
            return int(self.number_input.text)
        except ValueError:
            return 0


if __name__ == "__main__":
    breedte = 400
    hoogte = 450
    model = MemoryModel(10)
    view = MemoryView(model, breedte)
    controller = MemoryController(model, view, breedte, hoogte)

    arcade.run()
