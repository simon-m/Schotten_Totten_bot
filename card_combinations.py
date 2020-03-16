import itertools
from utils import pairwise
from game_elements import ALL_CARDS


class CardCombination:
    def __init__(self, card1, card2, card3):
        assert(card1 != card2)
        assert(card1 != card3)
        self.cards = tuple(sorted([card1, card2, card3]))
        self.name = None
        self.category = None
        self.value = None
        self.compute_name_value_category()

    def compute_name_value_category(self):
        has_single_color = True
        for c1, c2 in pairwise(self.cards):
            if c1.color != c2.color:
                has_single_color = False

        is_suite = True
        for c1, c2 in pairwise(self.cards):
            if c1.number < c2.number - 1 or \
               c1.number == c2.number:
                is_suite = False

        is_set = True
        for c1, c2 in pairwise(self.cards):
            if c1.number != c2.number:
                is_set = False

        if has_single_color:
            # Color suite. Strongest combination.
            # The smallest card number gives its strength
            # relative to other color suites
            if is_suite:
                self.name = "Color suite"
                self.category = 4
                self.value = self.cards[0].number
            # Color.
            # The sum of the card numbers gives its
            # strength relative to other colors
            else:
                self.name = "Color"
                self.category = 2
                self.value = self.cards[0].number + \
                             self.cards[1].number + \
                             self.cards[2].number
        elif is_suite:
            # Suite. Strongest combination.
            # The smallest card number gives its strength
            # relative to other suites
            if is_suite:
                self.name = "Suite"
                self.category = 1
                self.value = self.cards[0].number
        elif is_set:
            # Set. Second strongest combination.
            # Any card number gives its strength
            # relative to other sets
            self.name = "Set"
            self.category = 3
            self.value = self.cards[0].number
        else:
            # Sum: weakest combination.
            # The sum of the card numbers gives its
            # strength relative to other sums.
            self.name = "Sum"
            self.category = 0
            self.value = self.cards[0].number + \
                         self.cards[1].number + \
                         self.cards[2].number

    def __eq__(self, other):
        for c1, c2 in zip(self.cards, other.cards):
            if c1 != c2:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if self.category < other.category:
            return True
        if self.category == other.category and self.value < other.value:
            return True
        return False

    def __hash__(self):
        return hash(self.cards)

    def __iter__(self):
        return self.cards.__iter__()

    def __str__(self):
        return "{}: {}".format(self.name, self.cards)

    def __repr__(self):
        return self.__str__()


class CardCombinationsGenerator:

    def __init__(self):
        self._all_combinations_cache = None

    def get_all_combinations(self):
        if self._all_combinations_cache is None:
            self._all_combinations_cache = set()
            for card1, card2, card3 in itertools.combinations(ALL_CARDS, 3):
                self._all_combinations_cache.add(CardCombination(card1, card2, card3))
        return self._all_combinations_cache

    @staticmethod
    def get_combinations_from_card(c_card):
        allowed_cards = ALL_CARDS - {c_card}
        all_combs = set()
        for card1, card2 in itertools.combinations(allowed_cards, 2):
            all_combs.add(CardCombination(c_card, card1, card2))
        return all_combs

    @staticmethod
    def get_combinations_from_pair_of_cards(card1, card2):
        allowed_cards = ALL_CARDS - {card1, card2}
        all_combs = set()
        for card in allowed_cards:
            all_combs.add(CardCombination(card1, card2, card))
        return all_combs

    @staticmethod
    def get_combinations_excluding_cards(forbidden_cards):
        allowed_cards = ALL_CARDS - set(forbidden_cards)
        all_combs = set()
        for card1, card2, card3 in itertools.combinations(allowed_cards, 3):
            all_combs.add(CardCombination(card1, card2, card3))
        return all_combs
