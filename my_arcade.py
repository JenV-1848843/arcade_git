import math
import arcade
import arcade.shape_list


class WrapperWindow(arcade.Window):
    def __init__(self, breedte, hoogte, titel, student_generator_functie):
        super().__init__(breedte, hoogte, titel, pixel_perfect=True, resizable=True)
        arcade.set_background_color(arcade.color.WHITE)

        # De centrale ShapeElementList voor alle vormen
        self.vormen_lijst = arcade.shape_list.ShapeElementList()
        self.vormen_lijst2 = arcade.shape_list.ShapeElementList()


        # Maak de schilder-interface aan en koppel de generator
        self.my_arcade = MyArcade(self)
        self.generator = student_generator_functie(self.my_arcade)

        self.wachttijd = 0.0
        arcade.schedule(self.update_stappen, 1 / 60)

    def update_stappen(self, delta_time: float):
        if self.wachttijd > 0:
            self.wachttijd -= delta_time
            return

        try:
            pauze_tijd = next(self.generator)
            if isinstance(pauze_tijd, (int, float)):
                self.wachttijd = pauze_tijd
        except StopIteration:
            arcade.unschedule(self.update_stappen)

    def on_draw(self):
        self.clear()
        self.vormen_lijst.draw()


class MyArcade:
    def __init__(self, window):
        self._window = window

    def create_ellipse_filled(self, x, y, straal, kleur):
        vorm = arcade.shape_list.create_ellipse_filled(x, y, straal * 2, straal * 2, kleur)
        self._window.vormen_lijst.append(vorm)

    def create_ellipse_outline(self, x, y, straal, kleur, dikte=1):
        vorm = arcade.shape_list.create_ellipse_outline(x, y, straal * 2, straal * 2, kleur, dikte)
        self._window.vormen_lijst.append(vorm)

    def create_rectangle_filled(self, links, onder, breedte, hoogte, kleur):
        # create_rectangle_filled werkt met een middelpunt, niet met links/onder
        midden_x = links + breedte / 2
        midden_y = onder + hoogte / 2
        vorm = arcade.shape_list.create_rectangle_filled(midden_x, midden_y, breedte, hoogte, kleur)
        self._window.vormen_lijst.append(vorm)

    def create_rectangle_outline(self, links, onder, breedte, hoogte, kleur, dikte=1):
        midden_x = links + breedte / 2
        midden_y = onder + hoogte / 2
        vorm = arcade.shape_list.create_rectangle_outline(midden_x, midden_y, breedte, hoogte, kleur, dikte)
        self._window.vormen_lijst.append(vorm)

    def create_line(self, start_x, start_y, eind_x, eind_y, kleur, dikte=1):
        vorm = arcade.shape_list.create_line(start_x, start_y, eind_x, eind_y, kleur, dikte)
        self._window.vormen_lijst.append(vorm)

    def create_polygon(self, x, y, breedte, hoogte, kleur, start_hoek, eind_hoek, num_segments=30):
        # Punten berekenen langs de rand van de boog...
        points = []
        a, b = breedte / 2, hoogte / 2
        for i in range(num_segments + 1):
            angle_rad = math.radians(start_hoek + (eind_hoek - start_hoek) * i / num_segments)
            points.append((x + a * math.cos(angle_rad), y + b * math.sin(angle_rad)))
        # ...en het middelpunt toevoegen zodat het een gevulde 'taartpunt' wordt
        points.append((x, y))
        vorm = arcade.shape_list.create_polygon(points, kleur)
        self._window.vormen_lijst.append(vorm)

    # Dit is ARC, naam van arcade behouden?
    def create_line_strip(self, x, y, breedte, hoogte, kleur, start_hoek, eind_hoek, dikte=5, num_segments=30):
        points = []
        a, b = breedte / 2, hoogte / 2
        for i in range(num_segments + 1):
            angle_rad = math.radians(start_hoek + (eind_hoek - start_hoek) * i / num_segments)
            points.append((x + a * math.cos(angle_rad), y + b * math.sin(angle_rad)))
        vorm = arcade.shape_list.create_line_strip(points, kleur, line_width=dikte)
        self._window.vormen_lijst.append(vorm)

    def pauze(self, seconden=0.5):
        return seconden


def start_my_arcade(student_code_functie, breedte=600, hoogte=600, titel="Stapsgewijs Tekenen"):
    WrapperWindow(breedte, hoogte, titel, student_code_functie)
    arcade.run()
