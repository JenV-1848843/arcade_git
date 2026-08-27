import arcade
from myarcade import MyArcade, _WrapperWindow  # pas de module-naam aan naar jouw bestandsnaam


class Schilder:
    """Vriendelijke, Nederlandstalige laag bovenop MyArcade."""

    def __init__(self, tekenaar: MyArcade):
        self._tekenaar = tekenaar

    def teken_cirkel(self, x, y, straal, kleur):
        self._tekenaar.my_draw_circle_filled(x, y, straal, kleur)

    def teken_boog(self, x, y, breedte, hoogte, kleur, start_hoek, eind_hoek, dikte=5):
        self._tekenaar.my_draw_arc_outline(
            x, y, breedte, hoogte, kleur, start_hoek, eind_hoek, dikte
        )

    def pauze(self, seconden=0.5):
        return seconden


def _naar_schilder(student_generator_functie):
    """Zorgt dat de student een Schilder krijgt i.p.v. de ruwe MyArcade-instantie."""
    def wrapper(tekenaar: MyArcade):
        schilder = Schilder(tekenaar)
        yield from student_generator_functie(schilder)
    return wrapper


def start_schilder(student_code_functie, breedte=600, hoogte=600, titel="Stapsgewijs Tekenen"):
    _WrapperWindow(breedte, hoogte, titel, _naar_schilder(student_code_functie))
    arcade.run()

if __name__ == "__main__":
    start_schilder(start_schilder)