import arcade
import arcade.gui
from PIL import Image, ImageDraw, ImageFont
from PIL._typing import _Ink


class _WrapperWindow(arcade.Window):
    def __init__(self, breedte, hoogte, titel, student_generator_functie, resizable=True):
        super().__init__(breedte, hoogte, titel, resizable=resizable)
        arcade.set_background_color(arcade.color.WHITE)

        self.breedte = breedte
        self.hoogte = hoogte

        self.image = Image.new('RGBA', (breedte, hoogte), (255, 255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)

        # 1. Maak de sprite eenmalig aan in de init
        self.arcade_texture = arcade.Texture(self.image)
        self.canvas_sprite = arcade.Sprite(self.arcade_texture)
        self.canvas_sprite.center_x = self.breedte / 2
        self.canvas_sprite.center_y = self.hoogte / 2

        self.schilder = MyArcade(self)
        self.generator = student_generator_functie(self.schilder)

        self.wachttijd = 0.0
        arcade.schedule(self.update_stappen, 1 / 60)

    def update_stappen(self, delta_time: float):
        if self.wachttijd > 0:
            self.wachttijd -= delta_time
            return

        try:
            pauze_tijd = next(self.generator)

            # 2. De student heeft net getekend! Update de texture eenmalig hier.
            self.arcade_texture = arcade.Texture(self.image)
            self.canvas_sprite.texture = self.arcade_texture

            if isinstance(pauze_tijd, (int, float)):
                self.wachttijd = pauze_tijd
        except StopIteration:
            arcade.unschedule(self.update_stappen)

    def on_draw(self):
        self.clear()
        # 3. on_draw hoeft nu enkel de reeds bestaande sprite te tekenen (super snel!)
        arcade.draw_sprite(self.canvas_sprite)


class MyArcade:
    def __init__(self, window: _WrapperWindow):
        self._window = window

    def _to_pillow_y(self, y: float) -> float:
        """Converteer Arcade Y (start onderaan) naar Pillow Y (start bovenaan)."""
        return self._window.hoogte - y

    # =========================================================================
    # PILLOW TEKEN-FUNCTIES
    # =========================================================================

    def my_draw_circle_filled(self, center_x: float, center_y: float, radius: float, color: _Ink):
        """Teken een gevulde cirkel via Pillow."""
        p_y = self._to_pillow_y(center_y)
        box = [center_x - radius, p_y - radius, center_x + radius, p_y + radius]
        self._window.draw.ellipse(box, fill=color)

    def my_draw_circle_outline(self, center_x: float, center_y: float, radius: float, color: _Ink):
        """Teken de buitenrand van een cirkel via Pillow."""
        p_y = self._to_pillow_y(center_y)
        box = [center_x - radius, p_y - radius, center_x + radius, p_y + radius]
        self._window.draw.ellipse(box, outline=color)

    def my_draw_lbwh_rectangle_filled(self, left: float, bottom: float, width: float, height: float, color: _Ink):
        """Teken een gevulde rechthoek via Pillow."""
        x0 = left
        x1 = left + width
        y1 = self._to_pillow_y(bottom)
        y0 = y1 - height
        self._window.draw.rectangle([x0, y0, x1, y1], fill=color)

    def my_draw_lbwh_rectangle_outline(self, left: float, bottom: float, width: float, height: float, color: _Ink, border_width: float = 1):
        """Teken de buitenrand van een rechthoek via Pillow."""
        x0 = left
        x1 = left + width
        y1 = self._to_pillow_y(bottom)
        y0 = y1 - height
        self._window.draw.rectangle([x0, y0, x1, y1], outline=color, width=int(border_width))

    def my_draw_line(self, start_x: float, start_y: float, end_x: float, end_y: float, color: _Ink, line_width: float = 1):
        """Teken een rechte lijn tussen twee punten via Pillow."""
        p_start_y = self._to_pillow_y(start_y)
        p_end_y = self._to_pillow_y(end_y)
        self._window.draw.line([(start_x, p_start_y), (end_x, p_end_y)], fill=color, width=int(line_width))

    def my_draw_text(self, text: str, start_x: float, start_y: float, color: _Ink, font_size: float = 12):
        """Teken tekst op het scherm via Pillow."""
        p_y = self._to_pillow_y(start_y)
        try:
            font = ImageFont.truetype("arial.ttf", int(font_size))
        except IOError:
            font = ImageFont.load_default()
        self._window.draw.text((start_x, p_y), text, fill=color, font=font)

    def my_draw_point(self, x: float, y: float, color: _Ink, size: float = 1.0):
        """Teken een punt op het scherm via Pillow."""
        p_y = self._to_pillow_y(y)
        r = size / 2
        self._window.draw.ellipse([x - r, p_y - r, x + r, p_y + r], fill=color)

    def my_draw_triangle(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, color: _Ink):
        """Teken een gevulde driehoek via Pillow."""
        p_y1 = self._to_pillow_y(y1)
        p_y2 = self._to_pillow_y(y2)
        p_y3 = self._to_pillow_y(y3)
        self._window.draw.polygon([(x1, p_y1), (x2, p_y2), (x3, p_y3)], fill=color)

    def my_draw_triangle_outline(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, color: _Ink, border_width: float = 1):
        """Teken de buitenrand van een driehoek via Pillow."""
        p_y1 = self._to_pillow_y(y1)
        p_y2 = self._to_pillow_y(y2)
        p_y3 = self._to_pillow_y(y3)
        self._window.draw.polygon([(x1, p_y1), (x2, p_y2), (x3, p_y3)], outline=color, width=int(border_width))

    # Vangt pogingen op om de standaard Arcade-functies (zonder underscore) te gebruiken:
    def __getattr__(self, name):
        if name.startswith("draw_"):
            raise AttributeError(
                f"\n\n[MyArcade Error] Function '{name}' does not exist! \n"
                f"If you are using AI-generated code, please use auto-complete (CTRL-space) instead.\n "
                f"When typing 'my_draw' + ctrl-space, all relevant drawing methods are shown.\n"
            )
        raise AttributeError(f"'MyArcade' object has no attribute '{name}'")


def main(student_code_functie, breedte=600, hoogte=600, titel="MyArcade Exercise"):
    window = _WrapperWindow(breedte, hoogte, titel, student_code_functie)
    arcade.run()

def test_alle_functies(schilder: MyArcade):
    print("[TEST] Start van de test...")

    # 1. Tekst testen
    print("[TEST] Teken text...")
    schilder.my_draw_text("Start van de tekentest...", 50, 550, "black", font_size=24)
    yield 1.0  # Wacht 1 seconde

    # 2. Rechthoek (Gevuld + Buitenrand)
    print("[TEST] Teken rechthoeken...")
    schilder.my_draw_lbwh_rectangle_filled(50, 400, 150, 100, "lightblue")
    schilder.my_draw_lbwh_rectangle_outline(50, 400, 150, 100, "blue", border_width=4)
    schilder.my_draw_text("Rechthoeken", 60, 380, "black", font_size=16)
    yield 1.0

    # 3. Cirkel (Gevuld + Buitenrand)
    print("[TEST] Teken cirkels...")
    schilder.my_draw_circle_filled(400, 450, 60, "yellow")
    schilder.my_draw_circle_outline(400, 450, 60, "orange")
    schilder.my_draw_text("Cirkels", 370, 360, "black", font_size=16)
    yield 1.0

    # 4. Lijn
    print("[TEST] Teken lijn...")
    schilder.my_draw_line(50, 300, 550, 300, "green", line_width=5)
    yield 1.0

    # 5. Driehoek (Gevuld + Buitenrand)
    print("[TEST] Teken driehoeken...")
    schilder.my_draw_triangle(100, 100, 150, 250, 200, 100, "purple")
    schilder.my_draw_triangle_outline(300, 100, 350, 250, 400, 100, "red", border_width=4)
    yield 1.0

    # 6. Punten (Points)
    print("[TEST] Teken punten...")
    schilder.my_draw_text("Punten:", 450, 200, "black", font_size=16)
    schilder.my_draw_point(470, 150, "red", size=15)
    schilder.my_draw_point(500, 150, "green", size=15)
    schilder.my_draw_point(530, 150, "blue", size=15)
    yield 1.0

    # Eindtekst
    print("[TEST] Teken eindtekst...")
    schilder.my_draw_text("Test voltooid!", 200, 50, "red", font_size=30)
    print("[TEST] Test script is klaar.")
    yield 0

if __name__ == "__main__":
    main(test_alle_functies, breedte=600, hoogte=600, titel="Test Alle Functies")