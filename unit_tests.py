import sys
import unittest
import collections
import itertools
from card_combinations import CardCombination, CardCombinationsGenerator
from game_elements import Card, ALL_CARDS, MAX_CARDS_PER_HAND
from game import Slot, GameState, HumanPlayer, Player, Game
from proba_engine import ProbaEngine
from combination_scoring import ScoringScheme


"""
class TestCard(unittest.TestCase):
    def test_constructor(self):
        self.assertRaises(ValueError, Card, "grellow", 1)
        self.assertRaises(ValueError, Card, "red", 0)
        self.assertRaises(ValueError, Card, "blue", 10)

        card = Card("red", 1)
        self.assertEqual(card.color, "red")
        self.assertEqual(card.number, 1)
        self.assertEqual("{}".format(card), "Card(red, 1)")

    def test_comparators(self):
        card1 = Card("red", 1)
        card1b = Card("red", 1)
        self.assertEqual(card1, card1b)

        card2 = Card("blue", 5)
        self.assertNotEqual(card1, card2)

        card3 = Card("red", 3)
        self.assertNotEqual(card1, card3)
        self.assertTrue(card1 < card3)

        card4 = Card("green", 1)
        self.assertNotEqual(card1, card3)
        self.assertTrue(card4 < card1)

        cards = sorted([card1, card1b, card2, card3, card4])
        self.assertTrue(cards[0] == card4)
        self.assertTrue(cards[1] == card1 or cards[2] == card1)
        self.assertTrue(cards[1] == card1b or cards[2] == card1b)
        self.assertTrue(cards[3] == card3)
        self.assertTrue(cards[4] == card2)

        test_set = {card1, card1b, card2, card3, card4}
        self.assertEqual(len(test_set), 4)


TestCard().test_constructor()
TestCard().test_comparators()


class TestCardCombination(unittest.TestCase):
    def test_constructor(self):
        card1 = Card("red", 1)
        card2 = Card("blue", 9)
        card3 = Card("green", 3)
        cc = CardCombination(card1, card2, card3)

        self.assertEqual(cc.cards[0], card1)
        self.assertEqual(cc.cards[1], card3)
        self.assertEqual(cc.cards[2], card2)

    def test_compute_name_value_category(self):
        card1 = Card("red", 2)
        card2 = Card("red", 3)
        card3 = Card("red", 4)
        cc = CardCombination(card1, card2, card3)
        self.assertEqual(cc.name, "Color suite")
        self.assertEqual(cc.category, 4)
        self.assertEqual(cc.value, 2)

        card1 = Card("red", 6)
        card2 = Card("yellow", 6)
        card3 = Card("purple", 6)
        cc = CardCombination(card1, card2, card3)
        self.assertEqual(cc.name, "Set")
        self.assertEqual(cc.category, 3)
        self.assertEqual(cc.value, 6)

        card1 = Card("red", 6)
        card2 = Card("red", 7)
        card3 = Card("red", 4)
        cc = CardCombination(card1, card2, card3)
        self.assertEqual(cc.name, "Color")
        self.assertEqual(cc.category, 2)
        self.assertEqual(cc.value, 17)

        card1 = Card("red", 7)
        card2 = Card("brown", 9)
        card3 = Card("red", 8)
        cc = CardCombination(card1, card2, card3)
        self.assertEqual(cc.name, "Suite")
        self.assertEqual(cc.category, 1)
        self.assertEqual(cc.value, 7)

        card1 = Card("red", 1)
        card2 = Card("brown", 9)
        card3 = Card("red", 8)
        cc = CardCombination(card1, card2, card3)
        self.assertEqual(cc.name, "Sum")
        self.assertEqual(cc.category, 0)
        self.assertEqual(cc.value, 18)

    def test_comparators(self):
        card1a = Card("red", 7)
        card2a = Card("brown", 9)
        card3a = Card("red", 8)
        cca = CardCombination(card1a, card2a, card3a)

        card1b = Card("red", 7)
        card2b = Card("brown", 9)
        card3b = Card("red", 8)
        ccb = CardCombination(card1b, card2b, card3b)

        self.assertEqual(cca, ccb)

        card1c = Card("red", 1)
        card2c = Card("brown", 9)
        card3c = Card("red", 8)
        ccc = CardCombination(card1c, card2c, card3c)

        self.assertNotEqual(cca, ccc)
        self.assertTrue(ccc < cca)

        test_set = {cca, ccb, ccc}
        self.assertEqual(len(test_set), 2)


TestCardCombination().test_constructor()
TestCardCombination().test_compute_name_value_category()
TestCardCombination().test_comparators()


class TestCardCombinationsGenerator(unittest.TestCase):
    def test_get_all_combinations(self):
        ccg = CardCombinationsGenerator()
        self.assertIsNone(ccg._all_combinations_cache)
        self.assertEqual(len(ccg.get_all_combinations()), 24804)
        self.assertIsNotNone(ccg._all_combinations_cache)
        self.assertEqual(len(ccg.get_all_combinations()), 24804)

    def test_get_combinations_from_card(self):
        for c_card in ALL_CARDS:
            combs = sorted(CardCombinationsGenerator.get_combinations_from_card(c_card))
            self.assertEqual(len(combs), 1378)

            comb_type_dict = collections.defaultdict(int)
            for comb in combs:
                comb_type_dict[comb.name] += 1

            if c_card.number == 1 or c_card.number == 9:
                self.assertEqual(comb_type_dict["Color suite"], 1)
                self.assertEqual(comb_type_dict["Suite"], 35)
                self.assertEqual(comb_type_dict["Color"], 27)
            elif c_card.number == 2 or c_card.number == 8:
                self.assertEqual(comb_type_dict["Color suite"], 2)
                self.assertEqual(comb_type_dict["Suite"], 70)
                self.assertEqual(comb_type_dict["Color"], 26)
            else:
                self.assertEqual(comb_type_dict["Color suite"], 3)
                self.assertEqual(comb_type_dict["Suite"], 105)
                self.assertEqual(comb_type_dict["Color"], 25)

            self.assertEqual(comb_type_dict["Set"], 10)

    # Not exhaustive
    def test_get_combinations_from_pair_of_cards(self):
        for card1, card2 in itertools.combinations(ALL_CARDS, 2):

            if card2 < card1:
                card1, card2 = card2, card1

            combs = sorted(CardCombinationsGenerator.get_combinations_from_pair_of_cards(card1, card2))
            self.assertEqual(len(combs), 52)

            comb_type_dict = collections.defaultdict(int)
            for comb in combs:
                comb_type_dict[comb.name] += 1

            if card1.color == card2.color:
                self.assertEqual(comb_type_dict["Color"], 7 - comb_type_dict["Color suite"])

                if card2.number - card1.number == 2:
                    self.assertEqual(comb_type_dict["Color suite"], 1)
                    self.assertEqual(comb_type_dict["Suite"], 5)
                elif card2.number - card1.number == 1:
                    if card1.number == 1 or card2.number == 9:
                        self.assertEqual(comb_type_dict["Color suite"], 1)
                        self.assertEqual(comb_type_dict["Suite"], 5)
                    else:
                        self.assertEqual(comb_type_dict["Color suite"], 2)
                        self.assertEqual(comb_type_dict["Suite"], 10)
            else:
                self.assertEqual(comb_type_dict["Color"], 0)
                if card2.number - card1.number == 2:
                    self.assertEqual(comb_type_dict["Suite"], 6)
                elif card2.number - card1.number == 1:
                    if card1.number == 1 or card2.number == 9:
                        self.assertEqual(comb_type_dict["Suite"], 6)
                    else:
                        self.assertEqual(comb_type_dict["Suite"], 12)

            if card1.number == card2.number:
                self.assertEqual(comb_type_dict["Set"], 4)

    def test_get_combinations_excluding_cards(self):
        ccg = CardCombinationsGenerator()

        # combs = CardCombinationsGenerator.get_combinations_excluding_cards([])
        combs = ccg.get_all_combinations([])
        self.assertEqual(len(combs), 24804)

        cards = [Card("red", 1), Card("blue", 1), Card("green", 1),
                 Card("yellow", 1), Card("brown", 1), Card("purple", 1)]
        # combs = CardCombinationsGenerator.get_combinations_excluding_cards(cards)
        combs = ccg.get_all_combinations(cards)
        self.assertEqual(len(combs), 17296)

        counter = [0, 0, 0, 0, 0]
        for comb in combs:
            counter[comb.category] += 1

        # Color suites without a 1: 6 per color
        self.assertEqual(counter[4], 36)
        # Sets except ones: 6 choose 3 per number
        self.assertEqual(counter[3], 160)
        # Colors without a 1: (8 choose 3 ) - 6 (color suites) per color
        self.assertEqual(counter[2], 300)
        # Suites without a 1: 6 * 5 * 6 (two first position with different colors) +
        # 6 * 1 * 5 (two first positions with the same color) = 210 for each
        # starting number
        self.assertEqual(counter[1], 1260)
        # Sums without a 1: 17296 (3 choose 48) - 36 - 160 - 300 - 1260
        self.assertEqual(counter[0], 15540)


TestCardCombinationsGenerator().test_get_all_combinations()
TestCardCombinationsGenerator().test_get_combinations_from_card()
TestCardCombinationsGenerator().test_get_combinations_from_pair_of_cards()
TestCardCombinationsGenerator().test_get_combinations_excluding_cards()


# Not at all exhaustive
class TestProbaEngine(unittest.TestCase):

    def test_combination_probas_from_slot(self):
        pe = ProbaEngine()
        player = Player(0)
        
        # Slot is full so all combinations have proba 0 except one
        gs = GameState()
        gs.slots[0][0].add(Card("blue", 3))
        gs.slots[0][0].add(Card("blue", 4))
        gs.slots[0][0].add(Card("blue", 7))
        player.hand = {Card("blue", 1), Card("blue", 2), Card("blue", 3)}
        comb_probas = pe.combination_probas_from_slot(player, gs, 0)
        self.assertEqual(len(comb_probas), 0)

        # Color suite is in our hand
        gs = GameState()
        player.hand = {Card("blue", 1), Card("blue", 2), Card("blue", 3)}
        comb = CardCombination(Card("blue", 1), Card("blue", 2), Card("blue", 3))
        comb_probas = pe.combination_probas_from_slot(player, gs, 0)
        self.assertEqual(comb_probas[comb], 1)

        # Color suite with one member missing, with various deck sizes
        # Assume we only have 3 cards in our hand for the sake of simplicity
        max_deck_size = 54 - MAX_CARDS_PER_HAND - 3
        player.hand = {Card("blue", 1), Card("blue", 2), Card("red", 3)}
        comb = CardCombination(Card("blue", 1), Card("blue", 2), Card("blue", 3))
        allowed_cards = ALL_CARDS - {Card("blue", 1), Card("blue", 2), Card("red", 3)}

        for i in range(max_deck_size):
            deck = []
            for j, elt in enumerate(allowed_cards):
                if j >= i:
                    break
                deck.append(elt)
            gs = GameState(deck)
            comb_probas = pe.combination_probas_from_slot(player, gs, 0)
            self.assertAlmostEqual(comb_probas[comb],
                                   0 if gs.deck_size == 0 else 1 / (gs.deck_size + MAX_CARDS_PER_HAND))

        # Color suite with one member missing but is already in a slot
        gs = GameState()
        gs.slots[0][0].add(Card("blue", 3))
        player.hand = {Card("blue", 1), Card("blue", 2), Card("red", 3)}
        comb = CardCombination(Card("blue", 1), Card("blue", 2), Card("blue", 3))
        comb_probas = pe.combination_probas_from_slot(player, gs, 0)
        self.assertEqual(comb_probas[comb], 1)

        # Color suite with two members missing but one is already in a slot,
        # with various deck sizes
        # Assume we only have 3 cards in our hand for the sake of simplicity
        max_deck_size = 54 - MAX_CARDS_PER_HAND - 4
        player.hand = {Card("blue", 1), Card("green", 2), Card("red", 3)}
        comb = CardCombination(Card("blue", 1), Card("blue", 2), Card("blue", 3))
        allowed_cards = ALL_CARDS - {Card("blue", 1), Card("green", 2),
                                     Card("red", 3), Card("blue", 3)}
        for i in range(max_deck_size):
            deck = []
            for j, elt in enumerate(allowed_cards):
                if j >= i:
                    break
                deck.append(elt)
            gs = GameState(deck)
            gs.slots[0][0].add(Card("blue", 3))
            comb_probas = pe.combination_probas_from_slot(player, gs, 0)
            self.assertAlmostEqual(comb_probas[comb],
                                   0 if gs.deck_size == 0 else 1 / (gs.deck_size + MAX_CARDS_PER_HAND))

        # Color suite with two members missing but one is in our slot and the other
        # is in the adversary's
        gs = GameState()
        gs.slots[0][0].add(Card("blue", 3))
        gs.slots[1][0].add(Card("blue", 2))

        player.hand = {Card("blue", 1), Card("red", 2), Card("red", 3)}
        comb = CardCombination(Card("blue", 1), Card("blue", 2), Card("blue", 3))
        comb_probas = pe.combination_probas_from_slot(player, gs, 0)
        self.assertEqual(comb_probas[comb], 0)

        # Color suite with two members missing but one is in a slot and the other
        # taken in another combinations
        gs = GameState()
        gs.slots[0][0].add(Card("blue", 3))
        gs.slots[1][0].add(Card("blue", 2))
        gs.slots[1][0].add(Card("green", 2))

        player.hand = {Card("blue", 1), Card("red", 2), Card("red", 3)}
        comb = CardCombination(Card("blue", 1), Card("blue", 2), Card("blue", 3))
        comb_probas = pe.combination_probas_from_slot(player, gs, 0)
        self.assertEqual(comb_probas[comb], 0)

        # Color suite with two members missing but both are in a slot
        gs = GameState()
        gs.slots[0][0].add(Card("blue", 3))
        gs.slots[0][0].add(Card("blue", 2))
        player.hand = {Card("blue", 1), Card("red", 2), Card("red", 3)}
        comb = CardCombination(Card("blue", 1), Card("blue", 2), Card("blue", 3))
        comb_probas = pe.combination_probas_from_slot(player, gs, 0)
        self.assertEqual(comb_probas[comb], 1)

        # Color suite with no members in hand but two are are already in a slot,
        # with various deck sizes
        # Assume we only have 3 cards in our hand for the sake of simplicity
        max_deck_size = 54 - MAX_CARDS_PER_HAND - 5
        player.hand = {Card("yellow", 1), Card("green", 2), Card("red", 3)}
        comb = CardCombination(Card("blue", 1), Card("blue", 2), Card("blue", 3))
        allowed_cards = ALL_CARDS - {Card("yellow", 1), Card("green", 2), Card("red", 3),
                                     Card("blue", 2), Card("blue", 3)}

        for i in range(max_deck_size):
            deck = []
            for j, elt in enumerate(allowed_cards):
                if j >= i:
                    break
                deck.append(elt)
            gs = GameState(deck)
            gs.slots[0][0].add(Card("blue", 3))
            gs.slots[0][0].add(Card("blue", 2))
            comb_probas = pe.combination_probas_from_slot(player, gs, 0)
            self.assertAlmostEqual(comb_probas[comb],
                                   0 if gs.deck_size == 0 else 1 / (gs.deck_size + 6))

    def test_combination_probas_from_slot_for_opponent(self):
        pe = ProbaEngine()
        player = Player(0)

        # Test for an arbitrary combination with no cards currently known
        # (in an empty slot)
        max_deck_size = 54
        player.hand = {}
        allowed_cards = ALL_CARDS

        for i in range(max_deck_size):
            deck = []
            for j, elt in enumerate(allowed_cards):
                if j >= i:
                    break
                deck.append(elt)
            gs = GameState(deck)
            comb = CardCombination(Card("brown", 2), Card("yellow", 3), Card("purple", 5))
            comb_probas = pe.combination_probas_from_slot(player, gs, 0, True)
            self.assertAlmostEqual(comb_probas[comb],
                                   1 if gs.deck_size == 0 else
                                   ((MAX_CARDS_PER_HAND + 1) / (MAX_CARDS_PER_HAND + gs.deck_size)) ** 3)

        # Opponent started a set but we have all the remaining cards
        gs = GameState()
        gs.slots[1][0].add(Card("brown", 1))
        gs.slots[1][0].add(Card("yellow", 1))
        player.hand = {Card("blue", 1), Card("red", 1), Card("green", 1), Card("purple", 1)}
        comb1 = CardCombination(Card("brown", 1), Card("yellow", 1), Card("blue", 1))
        comb2 = CardCombination(Card("brown", 1), Card("yellow", 1), Card("purple", 1))
        comb_probas = pe.combination_probas_from_slot(player, gs, 0, True)
        self.assertEqual(comb_probas[comb1], 0)
        self.assertEqual(comb_probas[comb2], 0)

        # Same as above but the slot only has one card
        gs = GameState()
        gs.slots[1][0].add(Card("yellow", 1))
        player.hand = {Card("blue", 1), Card("red", 1), Card("green", 1), Card("purple", 1),
                       Card("brown", 1)}
        comb1 = CardCombination(Card("brown", 1), Card("yellow", 1), Card("blue", 1))
        comb2 = CardCombination(Card("green", 1), Card("yellow", 1), Card("purple", 1))
        comb_probas = pe.combination_probas_from_slot(player, gs, 0, True)
        self.assertEqual(comb_probas[comb1], 0)
        self.assertEqual(comb_probas[comb2], 0)

        # Same as above, but we only have 3 ones
        # Assume we only have 3 cards in our hand for simplicity
        max_deck_size = 54 - 6 - 5
        player.hand = {Card("blue", 1), Card("red", 1), Card("green", 1)}
        comb = CardCombination(Card("brown", 1), Card("yellow", 1), Card("purple", 1))
        allowed_cards = ALL_CARDS - {Card("blue", 1), Card("green", 1),
                                     Card("red", 1), Card("brown", 1), Card("yellow", 1)}

        for i in range(max_deck_size):
            deck = []
            for j, elt in enumerate(allowed_cards):
                if j >= i:
                    break
                deck.append(elt)
            gs = GameState(deck)
            gs.slots[1][0].add(Card("brown", 1))
            gs.slots[1][0].add(Card("yellow", 1))
            comb_probas = pe.combination_probas_from_slot(player, gs, 0, True)

            self.assertAlmostEqual(comb_probas[comb],
                                   1 if gs.deck_size == 0 else
                                   (MAX_CARDS_PER_HAND + 1) / (MAX_CARDS_PER_HAND + gs.deck_size))


TestProbaEngine().test_combination_probas_from_slot()
TestProbaEngine().test_combination_probas_from_slot_for_opponent()


class TestScoringScheme(unittest.TestCase):

    def test_get_base_score(self):
        sc = ScoringScheme()

        min_sum = 1000
        min_suite = 1000
        min_color = 1000
        min_set = 1000
        min_color_suite = 1000

        max_sum = 0
        max_suite = 0
        max_color = 0
        max_set = 0
        max_color_suite = 0

        min_val = 1000
        max_val = 0

        for comb in CardCombinationsGenerator().get_all_combinations():
            score = sc.get_base_score(comb)
            if comb.category == 0:
                min_sum = min(min_sum, score)
                max_sum = max(max_sum, score)
            if comb.category == 1:
                min_suite = min(min_suite, score)
                max_suite = max(max_suite, score)
            if comb.category == 2:
                min_color = min(min_color, score)
                max_color = max(max_color, score)
                min_val = min(min_val, comb.value)
                max_val = max(max_val, comb.value)
            if comb.category == 3:
                min_set = min(min_set, score)
                max_set = max(max_set, score)
            if comb.category == 4:
                min_color_suite = min(min_color_suite, score)
                max_color_suite = max(max_color_suite, score)

        self.assertEqual(min_sum, 0)
        self.assertEqual(min_suite - max_sum, 1)
        self.assertEqual(min_color - max_suite, 1)
        self.assertEqual(min_set - max_color, 1)
        self.assertEqual(min_color_suite - max_set, 1)
        self.assertEqual(max_color_suite, 62)

    def test_get_score(self):
        self.assertRaises(ValueError, ScoringScheme, (1, 2, 3, 4, 0))
        self.assertRaises(ValueError, ScoringScheme, (0, 2, 3, 4, 0))
        self.assertRaises(ValueError, ScoringScheme, (0, 2, 3, 4, 1))
        sc = ScoringScheme([1, 2, 3, 4, 5])

        min_sum = 1000
        min_suite = 1000
        min_color = 1000
        min_set = 1000
        min_color_suite = 1000

        max_sum = 0
        max_suite = 0
        max_color = 0
        max_set = 0
        max_color_suite = 0

        min_val = 1000
        max_val = 0

        for comb in CardCombinationsGenerator().get_all_combinations():
            score = sc.get_score(comb)
            if comb.category == 0:
                min_sum = min(min_sum, score)
                max_sum = max(max_sum, score)
            if comb.category == 1:
                min_suite = min(min_suite, score)
                max_suite = max(max_suite, score)
            if comb.category == 2:
                min_color = min(min_color, score)
                max_color = max(max_color, score)
                min_val = min(min_val, comb.value)
                max_val = max(max_val, comb.value)
            if comb.category == 3:
                min_set = min(min_set, score)
                max_set = max(max_set, score)
            if comb.category == 4:
                min_color_suite = min(min_color_suite, score)
                max_color_suite = max(max_color_suite, score)

        self.assertEqual(min_sum, 0)
        self.assertEqual(min_suite - max_sum, 24)
        self.assertEqual(min_color - max_suite, 32)
        self.assertEqual(min_set - max_color, 50)
        self.assertEqual(min_color_suite - max_set, 60)
        self.assertEqual(max_color_suite, 310)


TestScoringScheme().test_get_base_score()
TestScoringScheme().test_get_score()


class TestSlot(unittest.TestCase):

    def test_add(self):
        s = Slot()
        s.add(1)
        s.add(2)
        s.add(3)

        def add_again(elt):
            s.add(elt)
        self.assertRaises(ValueError, add_again, 1)
        self.assertRaises(ValueError, add_again, 4)


TestSlot().test_add()


class TestGameState(unittest.TestCase):

    def test_constructor(self):
        gs = GameState(ALL_CARDS)

        def try_get_deck():
            _ = gs.deck
        self.assertRaises(AttributeError, try_get_deck)

        def try_set_deck():
            gs.deck = []
        self.assertRaises(AttributeError, try_set_deck)

    def test_interface(self):
        gs = GameState(ALL_CARDS)
        self.assertEqual(gs.deck_size, 54)
        self.assertIsInstance(gs.draw_deck(), Card)
        self.assertEqual(gs.deck_size, 53)

    def test_add_to_slot(self):
        gs = GameState(ALL_CARDS)
        card = Card("blue", 2)
        gs.add_to_slot(0, 0, card)
        played_card, = gs.played_cards
        self.assertEqual(played_card, Card("blue", 2))
        slot_card,  = gs.slots[0][0]
        self.assertEqual(slot_card, Card("blue", 2))


TestGameState().test_constructor()
TestGameState().test_interface()
TestGameState().test_add_to_slot()


class TestPlayer(unittest.TestCase):

    def test_constructor(self):
        player = Player(0)
        self.assertEqual(len(player.combination_scores), 24804)

    def test_get_cards_in_hand_from_comb(self):
        player = Player(0)
        player.hand.add(Card("green", 1))

        comb = CardCombination(Card("blue", 1), Card("green", 2), Card("green", 3))
        self.assertEqual(len(player.get_cards_in_hand_from_comb(comb)), 0)
        comb = CardCombination(Card("green", 1), Card("green", 2), Card("green", 3))
        self.assertEqual(len(player.get_cards_in_hand_from_comb(comb)), 1)

        player.hand.add(Card("brown", 9))
        comb = CardCombination(Card("blue", 1), Card("green", 2), Card("brown", 9))
        self.assertEqual(player.get_cards_in_hand_from_comb(comb), [Card("brown", 9)])
        comb = CardCombination(Card("green", 1), Card("green", 2), Card("brown", 9))
        self.assertEqual(player.get_cards_in_hand_from_comb(comb), [Card("green", 1), Card("brown", 9)])

    def test_get_slots_combs_probas(self):
        player = Player(0)
        player.hand.add(Card("blue", 9))
        player.hand.add(Card("blue", 7))

        gs = GameState([Card("blue", 3)])
        gs.slots[0][1].add(Card("blue", 6))
        gs.slots[0][2].add(Card("green", 6))
        gs.slots[0][2].add(Card("green", 7))
        gs.slots[0][3].add(Card("purple", 6))
        gs.slots[0][3].add(Card("purple", 7))
        gs.slots[0][3].add(Card("purple", 8))

        slots_probas = player.get_slots_combs_probas(gs)

        # Not possible since the 6 is in the next slot
        comb = CardCombination(Card("blue", 6), Card("blue", 9), Card("blue", 7))
        self.assertEqual(slots_probas[0][comb], 0)
        self.assertEqual(slots_probas[0], slots_probas[4])
        self.assertEqual(slots_probas[0], slots_probas[5])
        self.assertEqual(slots_probas[0], slots_probas[6])
        self.assertEqual(slots_probas[0], slots_probas[7])
        self.assertEqual(slots_probas[0], slots_probas[8])

        comb = CardCombination(Card("blue", 6), Card("blue", 9), Card("blue", 7))
        self.assertEqual(slots_probas[1][comb], 1)
        # Possible because there is one card in the deck
        comb = CardCombination(Card("blue", 3), Card("blue", 9), Card("blue", 7))
        self.assertAlmostEqual(slots_probas[0][comb], 1 / 7)
        # Same thing, what is in the deck should not matter as we, as a player,
        # cannot know its contents
        comb = CardCombination(Card("blue", 4), Card("blue", 9), Card("blue", 7))
        self.assertAlmostEqual(slots_probas[0][comb], 1 / 7)

        # Combination is plain impossible for that slot
        self.assertNotIn(comb, slots_probas[2])
        # Possible because there is one card in the deck
        comb = CardCombination(Card("green", 5), Card("green", 6), Card("green", 7))
        self.assertAlmostEqual(slots_probas[2][comb], 1 / 7)
        # Combination is playable now
        player.hand.add(Card("green", 5))
        slots_probas = player.get_slots_combs_probas(gs)
        self.assertEqual(slots_probas[2][comb], 1)

        # Slot is full
        self.assertEqual(len(slots_probas[3]), 0)

    def test_get_non_locking_best_playable_combinations(self):
        slot_comb_probas = [
            (0, None, 0.7, True),
            (0, None, 0.2, True),
            (1, None, 0.4, True),
            (1, None, 0.6, False),
            (2, None, 0.6, True),
            (2, None, 0.4, False),
            (3, None, 0.9, False),
            (3, None, 0.2, False)
        ]
        expected_result = [
            (0, None, 0.7, True),
            (2, None, 0.6, True),
            (0, None, 0.2, True)
        ]

        slot_comb_probas.sort(key=lambda x: x[2], reverse=True)
        result = Player.get_non_locking_best_playable_combinations(slot_comb_probas)
        self.assertEqual(result, expected_result)

    # TODO: more thorough tests
    def test_get_best_move_from_combs(self):

        player = Player(0)
        player.hand.add(Card("blue", 2))
        slot_comb_best_probas = [
            (1, CardCombination(Card("blue", 1), Card("blue", 2), Card("blue", 3)), 0.7, True),
            (2, CardCombination(Card("blue", 2), Card("green", 2), Card("yellow", 2)), 0.65, True),
            (5, CardCombination(Card("blue", 3), Card("green", 3), Card("purple", 3)), 0.6, True)
        ]
        slot_comb_all_probas = sorted(slot_comb_best_probas + [
            (1, CardCombination(Card("red", 2), Card("red", 3), Card("red", 4)), 0.5, False),
            (2, CardCombination(Card("purple", 2), Card("green", 2), Card("yellow", 2)), 0.6, False),
            (5, CardCombination(Card("red", 3), Card("green", 3), Card("yellow", 3)), 0.4, True)
        ], key=lambda x: x[2], reverse=True)

        # Only one choice: playing that one card is the best move
        # slot, card = player.get_best_move_from_combs(slot_comb_best_probas,
        #                                             slot_comb_all_probas +
        #                                             slot_comb_best_probas)
        # self.assertEqual(slot, 1)
        # self.assertEqual(card, Card("blue", 2))

        # Two cards results in a best move for a single slot: favor the card
        # which kills the combination with lowest slot win probability
        player.hand.add(Card("blue", 3))
        slot, card = player.get_best_move_from_combs(slot_comb_best_probas,
                                                     slot_comb_all_probas +
                                                     slot_comb_best_probas)
        self.assertEqual(slot, 1)
        self.assertEqual(card, Card("blue", 3))

        # Same thing but bets moves are from different slots
        player = Player(0)
        player.hand.add(Card("blue", 2))
        player.hand.add(Card("green", 3))
        slot_comb_best_probas = [
            (0, CardCombination(Card("blue", 1), Card("blue", 2), Card("blue", 3)), 0.7, True),
            (2, CardCombination(Card("green", 4), Card("green", 5), Card("green", 6)), 0.65, True),
            (9, CardCombination(Card("red", 2), Card("blue", 2), Card("yellow", 2)), 0.2, True)
        ]
        slot_comb_all_probas =  sorted(slot_comb_best_probas + [
            (8, CardCombination(Card("red", 3), Card("green", 3), Card("purple", 3)), 0.3, False),
        ], key=lambda x: x[2], reverse=True)
        slot, card = player.get_best_move_from_combs(slot_comb_best_probas,
                                                     slot_comb_all_probas +
                                                     slot_comb_best_probas)
        self.assertEqual(slot, 0)
        self.assertEqual(card, Card("blue", 2))

    def test_get_best_comb_probas(self):
        player = Player(0)

        comb_probas = {}
        comb1 = CardCombination(Card("green", 7), Card("green", 8), Card("green", 9))
        comb2 = CardCombination(Card("green", 6), Card("blue", 6), Card("yellow", 6))
        comb3 = CardCombination(Card("yellow", 9), Card("red", 9), Card("purple", 9))
        comb_probas[comb1] = 0.9  # E = 0.9 * 62 = 55.8
        comb_probas[CardCombination(Card("blue", 7), Card("blue", 8), Card("blue", 9))] = 0.1  # E = 0.1 * 62 = 6.2
        comb_probas[comb3] = 0.4  # E = 0.4 * 55 = 22
        comb_probas[CardCombination(Card("yellow", 9), Card("yellow", 1), Card("yellow", 6))] = 0.2  # E = 0.2 * 16 = 7.8
        comb_probas[CardCombination(Card("red", 7), Card("blue", 8), Card("red", 9))] = 0.1  # E = 0.1 * 29 = 2.9
        comb_probas[comb2] = 0.95  # E = 0.95 * 53 = 50.35

        results = sorted(player.get_best_comb_probas(comb_probas, 3),
                         key=lambda x: x[1], reverse=True)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0][0], comb2)
        self.assertEqual(results[1][0], comb1)
        self.assertEqual(results[2][0], comb3)
        self.assertAlmostEqual(results[0][1], 0.95)
        self.assertAlmostEqual(results[1][1], 0.9)
        self.assertAlmostEqual(results[2][1], 0.4)

    def test_make_move(self):

        player = Player(0)
        player.hand.add(Card("blue", 9))
        player.hand.add(Card("red", 1))
        player.hand.add(Card("green", 5))
        player.hand.add(Card("purple", 2))
        player.hand.add(Card("brown", 5))
        player.hand.add(Card("red", 2))

        gs = GameState([Card("green", 9)])
        gs.slots[0][1].add(Card("blue", 7))
        gs.slots[0][1].add(Card("blue", 8))
        gs.slots[1][1].add(Card("green", 7))
        gs.slots[1][1].add(Card("green", 8))

        move = player.make_move(gs)
        self.assertEqual(move, (1, Card("blue", 9)))

        ##
        # Conflict: it is better to complete the set
        # of 9, even though the color suite 7 8 9
        # would beat the color suit 5 6 7 since 6 7 8
        # can beat it as well
        player = Player(0)
        player.hand.add(Card("blue", 9))
        player.hand.add(Card("red", 1))
        player.hand.add(Card("blue", 6))
        player.hand.add(Card("purple", 2))
        player.hand.add(Card("brown", 5))
        player.hand.add(Card("red", 4))

        gs = GameState(list(range(30)))  # just for the size
        gs.slots[0][0].add(Card("blue", 7))
        gs.slots[0][0].add(Card("blue", 8))

        gs.slots[1][0].add(Card("green", 5))
        gs.slots[1][0].add(Card("green", 6))
        gs.slots[1][0].add(Card("green", 7))

        gs.slots[0][1].add(Card("red", 9))
        gs.slots[0][1].add(Card("green", 9))

        gs.slots[1][1].add(Card("yellow", 8))
        gs.slots[1][1].add(Card("red", 8))
        gs.slots[1][1].add(Card("brown", 8))

        gs.slots[1][2].add(Card("yellow", 9))

        gs.slots[1][3].add(Card("purple", 9))

        gs.slots[1][4].add(Card("brown", 9))

        move = player.make_move(gs)
        self.assertEqual(move, (0, Card("blue", 6)))

        player.hand.remove(Card("blue", 6))
        player.hand.add(Card("green", 3))
        move = player.make_move(gs)
        self.assertEqual(move, (1, Card("blue", 9)))




TestPlayer().test_constructor()
TestPlayer().test_get_cards_in_hand_from_comb()
TestPlayer().test_get_slots_combs_probas()
TestPlayer().test_get_non_locking_best_playable_combinations()
TestPlayer().test_get_best_move_from_combs()
TestPlayer().test_get_best_comb_probas()
TestPlayer().test_make_move()
"""


class TestPlayer(unittest.TestCase):
    def test_get_winning_counter_combs(self):
        gs = GameState(ALL_CARDS)
        gs.slots[1][1].add(Card("blue", 7))
        gs.slots[1][2].add(Card("red", 7))
        gs.slots[1][2].add(Card("red", 8))
        gs.slots[1][3].add(Card("brown", 7))
        gs.slots[1][3].add(Card("brown", 8))
        gs.slots[1][3].add(Card("brown", 9))

        player = Player()
        ccg = CardCombinationsGenerator()

        combs = ccg.get_all_combinations()
        for comb in combs:
            # print(comb)
            for i in reversed(range(4)):
                cc = player.get_winning_counter_combs(comb, gs.slots[1][i], gs)
                # print(i, len(cc))
                for elt in cc:
                    self.assertTrue(elt.category >= comb.category or
                                    elt.value >= comb.value)

        # TODO
        # def test_get_move_scores(self):


TestPlayer().test_get_winning_counter_combs()


# TODO: test HumanPlayer
# TODO: rename and debug Player
# game = Game(Player(0), Player(1))
# game = Game(Player(0, ScoringScheme((1, 2, 3, 6, 10))),
#             Player(1, ScoringScheme((1, 2, 3, 6, 10))))
# game = Game(Player(0, ScoringScheme((1, 16, 50, 422, 543))),
#             HumanPlayer(1))

# game.play()
