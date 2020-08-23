import itertools

# Globals for the time being
CARD_COLORS = {"red", "blue", "green", "brown", "purple", "yellow"}
CARD_NUMBERS = set(range(1, 10))
MAX_CARDS_PER_HAND = 6


class Card:
    def __init__(self, color, number):
        if color not in CARD_COLORS:
            raise ValueError("Card: invalid color value {}".format(color))
        if number not in CARD_NUMBERS:
            raise ValueError("Card: invalid number value {}".format(repr(number)))
        self.color = color
        self.number = number

    def __eq__(self, other):
        if self.color == other.color and self.number == other.number:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if self.number < other.number:
            return True
        if self.number == other.number and self.color < other.color:
            return True
        return False

    def __hash__(self):
        return hash((self.color, self.number))

    def __str__(self):
        return "Card({}, {})".format(self.color, self.number)

    def __repr__(self):
        return "Card(\"{}\", {})".format(self.color, self.number)


ALL_CARDS = {Card(c, n) for c, n in itertools.product(CARD_COLORS, CARD_NUMBERS)}

