import arcade


class _WrapperWindow(arcade.Window):
    def __init__(self, breedte, hoogte, titel, student_generator_functie, resizable=True):
        super().__init__(breedte, hoogte, titel)
        arcade.set_background_color(arcade.color.WHITE)
        self.teken_opdrachten = []

        # Maak de schilder aan en start de generator
        self.schilder = MyArcade(self)
        self.generator = student_generator_functie(self.schilder)

        self.wachttijd = 0.0
        arcade.schedule(self.update_stappen, 1 / 60)

    def voeg_opdracht_toe(self, functie, *args, **kwargs):
        self.teken_opdrachten.append((functie, args, kwargs))

    def update_stappen(self, delta_time: float):
        # Als we in een pauze zitten, tel de tijd af
        if self.wachttijd > 0:
            self.wachttijd -= delta_time

            return

        # Voer de code van de student uit tot de volgende 'yield' (pauze)
        try:
            pauze_tijd = next(self.generator)
            if isinstance(pauze_tijd, (int, float)):
                self.wachttijd = pauze_tijd
        except StopIteration:
            # Script van de student is klaar
            arcade.unschedule(self.update_stappen)

    def on_draw(self):
        self.clear()
        for functie, args, kwargs in self.teken_opdrachten:
            functie(*args, **kwargs)


class MyArcade:
    def __init__(self, window):
        self._window = window

    # =========================================================================
    # DIRECTE ARCADE DRAW-FUNCTIES (Met Type Hints voor IDE Auto-aanvulling)
    # =========================================================================

    def my_draw_circle_filled(self, center_x: float, center_y: float, radius: float, color: arcade.Color):
        """Teken een gevulde cirkel op het scherm."""
        self._window.voeg_opdracht_toe(arcade.draw_circle_filled, center_x, center_y, radius, color)

    def my_draw_circle_outline(self, center_x: float, center_y: float, radius: float, color: arcade.Color):
        """Teken de buitenrand van een cirkel op het scherm."""
        self._window.voeg_opdracht_toe(arcade.draw_circle_outline, center_x, center_y, radius, color)

    def my_draw_lbwh_rectangle_filled(self, left: float, bottom: float, width: float, height: float, color: arcade.Color):
        """Teken een gevulde rechthoek op het scherm."""
        self._window.voeg_opdracht_toe(arcade.draw_lbwh_rectangle_filled, left, bottom, width, height, color)

    def my_draw_lbwh_rectangle_outline(self, left: float, bottom: float, width: float, height: float, color: arcade.Color, border_width: float):
        """Teken de buitenrand van een rechthoek op het scherm."""
        self._window.voeg_opdracht_toe(arcade.draw_lbwh_rectangle_outline, left, bottom, width, height, color, border_width)

    def my_draw_line(self, start_x: float, start_y: float, end_x: float, end_y: float, color: arcade.Color, line_width: float = 1):
        """Teken een rechte lijn tussen twee punten."""
        self._window.voeg_opdracht_toe(arcade.draw_line, start_x, start_y, end_x, end_y, color, line_width)

    def my_draw_arc_filled(self, center_x: float, center_y: float, width: float, height: float, color: arcade.Color,
                           start_angle: float, end_angle: float, border_width: float = 5):
        """Teken een gevulde boog (Arcade regelt de wiskunde zelf)."""
        self._window.voeg_opdracht_toe(arcade.draw_arc_filled, center_x, center_y, width, height, color,
                                       start_angle, end_angle, border_width)

    def my_draw_arc_outline(self, center_x: float, center_y: float, width: float, height: float, color: arcade.Color,
                         start_angle: float, end_angle: float, border_width: float = 5):
        """Teken de buitenrand van een boog (Arcade regelt de wiskunde zelf)."""
        self._window.voeg_opdracht_toe(arcade.draw_arc_outline, center_x, center_y, width, height, color,
                                       start_angle, end_angle, border_width)

    def my_draw_text(self, text: str, start_x: float, start_y: float, color: arcade.Color, font_size: float = 12):
        """Teken tekst op het scherm (In tegenstelling tot ShapeList werkt dit wel direct!)."""
        self._window.voeg_opdracht_toe(arcade.draw_text, text, start_x, start_y, color, font_size)

    def my_draw_point(self, x: float, y: float, color: arcade.Color, size: float = 1.0):
        """Teken een punt op het scherm."""
        self._window.voeg_opdracht_toe(arcade.draw_point, x, y, color, size)

    def my_draw_triangle(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, color: arcade.Color):
        """Teken een gevulde driehoek op het scherm."""
        self._window.voeg_opdracht_toe(arcade.draw_triangle_filled, x1, y1, x2, y2, x3, y3, color)

    def my_draw_triangle_outline(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, color: arcade.Color, border_width: float = 5):
        """Teken de buitenrand van een driehoek op het scherm."""
        self._window.voeg_opdracht_toe(arcade.draw_triangle_outline, x1, y1, x2, y2, x3, y3, color, border_width)

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