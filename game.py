import random
import itertools
import numpy as np
from collections import defaultdict
from collections.abc import MutableSet
from proba_engine import ProbaEngine
from combination_scoring import ScoringScheme
from card_combinations import CardCombinationsGenerator, CardCombination
from game_elements import ALL_CARDS, Card


DEBUG =True
# seed = random.randrange(sys.maxsize)
seed = 850806568202399433
rng = random.Random(seed)
print("Seed was:", seed)



class HumanPlayer:
    def __init__(self, index=0):
        self.index = index
        self.opponent_index = 1 if self.index == 0 else 0
        self.hand = set()

    def make_move(self, game_state):
        cards_list = []
        for i, card in enumerate(self.hand):
            print("{}: {}".format(i + 1, card))
            cards_list.append(card)

        card_error_message = "Should be a number between 1 and {}".format(len(self.hand))

        valid_input = False
        card_index = None
        while not valid_input:
            try:
                user_input = input("Choose your card: ")
                card_index = int(user_input)
            except ValueError:
                print(card_error_message)

            assert card_index is not None
            if card_index < 1 or card_index > len(self.hand):
                print(card_error_message)
            else:
                valid_input = True

        slot_error_message = "Should be a number between 1 and 9"

        valid_input = False
        slot_index = None
        while not valid_input:
            try:
                user_input = input("Choose your slot: ")
                slot_index = int(user_input)
            except ValueError:
                print(slot_error_message)

            if slot_index < 1 or slot_index > 9:
                print(slot_error_message)
            else:
                valid_input = True

        return slot_index - 1, cards_list[card_index - 1]


class Player:
    def __init__(self, index=0, combination_scorer=ScoringScheme(), search_depth=20):
        self.index = index
        self.opponent_index = 1 if self.index == 0 else 0
        self.hand = set()
        ccg = CardCombinationsGenerator()
        cs = combination_scorer
        self.combination_scores = {comb: cs.get_score(comb) for comb in ccg.get_all_combinations()}
        self.search_depth = search_depth

    def get_cards_in_hand_from_comb(self, m_comb):
        # cards_in_hand = set()
        cards_in_hand = []
        for card in self.hand:
            if card in m_comb:
                # cards_in_hand.add(card)
                cards_in_hand.append(card)
        return cards_in_hand

    def get_slots_combs_probas(self, game_state, for_opponent=False):
        if for_opponent:
            slots = game_state.slots[self.opponent_index]
        else:
            slots = game_state.slots[self.index]

        slots_combs_probas = []
        # Probas are the same for the empty slots so no need to compute
        # them more than once
        empty_slots_probas = None
        for i in range(len(slots)):
            if len(slots[i]) == 0:
                if empty_slots_probas is None:
                    empty_slots_probas = ProbaEngine.combination_probas_from_slot(self, game_state, i,
                                                                                  for_opponent)
                probas = empty_slots_probas
            else:
                probas = ProbaEngine.combination_probas_from_slot(self, game_state,
                                                                  i, for_opponent)
            slots_combs_probas.append(probas)

        return slots_combs_probas

    def get_best_comb_probas(self, slot_probas):

        comb_list = []
        proba_array = np.ndarray(shape=(len(slot_probas)))
        expectation_array = np.ndarray(shape=(len(slot_probas)))

        if len(slot_probas) <= self.search_depth:
            res = []
            for (m_comb, m_proba) in slot_probas.items():
                res.append((m_comb, m_proba))
            return res

        for i, (m_comb, m_proba) in enumerate(slot_probas.items()):
            comb_list.append(m_comb)
            proba_array[i] = m_proba
            expectation_array[i] = m_proba * self.combination_scores[m_comb]

        best_indexes = np.argpartition(-expectation_array, self.search_depth)[:self.search_depth]
        res = []
        for i in best_indexes:
            res.append((comb_list[i], proba_array[i], expectation_array[i]))
        return sorted(res, key=lambda x: x[2], reverse=True)

    @staticmethod
    def get_non_locking_best_playable_combinations(all_comb_win_probas):
        # TODO: assert input is sorted
        # Sort by decreasing slot win probability
        # comb_win_probas = sorted(all_comb_win_probas, key=lambda x: x[2], reverse=True)

        # A slot is locked if the combination with highest slot win
        # probability is not playable. We keep it for later.
        slot_is_locked = [None] * 9
        selected_combs = []
        for comb in all_comb_win_probas:
            slot_index = comb[0]
            is_playable = comb[3]
            # This is the first (with highest slot win proba) combination
            # for this slot and it is not playable: lock the slot.
            # Keep only the playable combinations
            if slot_is_locked[slot_index] is None:
                if not is_playable:
                    slot_is_locked[slot_index] = True
                else:
                    slot_is_locked[slot_index] = False
                    selected_combs.append(comb)
            elif is_playable and not slot_is_locked[slot_index]:
                selected_combs.append(comb)


        # Only locked combinations are available, return all the
        # playable ones
        if len(selected_combs) == 0:
            print("DEBUG")
            for comb in all_comb_win_probas:
                print(comb)
                if comb[3]:
                    selected_combs.append(comb)

        return selected_combs

    def get_best_move_from_combs(self, best_moves, all_comb_win_probas):
        # TODO: check best_combs is sorted by slot_win_proba
        # Definition of move: a card and a slot.
        # Associated to a move are a combination and its slot win probability
        #
        # Consider cards from the highest scoring moves (same maximum slot win
        # probability).
        # The moves using (playable) cards not shared by other
        # best moves should be played (they do not kill
        # other possible moves). If there are several such cases or no such
        # move (all best moves share at
        # least one card with another best move), play the one
        # whose second best move (without the shared card) has the
        # lowest slot win proba (kill the best move whose replacement
        # has the highest slot win probability).


        # For each card which is both in our hand and part of a best
        # move (move with highest probability, could be several),
        # record in which slots the moves could have it played.
        # The number of slots (repeats included) is basically the number of
        # moves using the card.
        highest_slot_win_proba = best_moves[0][2]
        # Slots can be repeated if multiple moves use the same
        # card in the same slot
        slot_comb_by_playable_card = defaultdict(list)
        for slot, comb, slot_win_proba, _ in best_moves:
            if slot_win_proba < highest_slot_win_proba:
                break
            else:
                for card in self.get_cards_in_hand_from_comb(comb):
                    slot_comb_by_playable_card[card].append(slot)

        # stored_card, stored_slot, slot_win_proba, comb
        if len(best_moves) == 1:
            print("DEBUG")
            print(best_moves)
            print(slot_comb_by_playable_card)
            card = rng.choice(list(slot_comb_by_playable_card.keys()))
            return best_moves[0][0], card


        # Keep cards (and their associated slots) with minimum number of
        # moves using them
        min_n_slots_probas = float("inf")
        stored_cards = []
        stored_slots = []
        for card, slots in slot_comb_by_playable_card.items():
            if len(slots) < min_n_slots_probas:
                min_n_slots_probas = len(slots)
                stored_cards = [card]
                stored_slots = [slots]
            elif len(slots) == min_n_slots_probas:
                stored_cards.append(card)
                stored_slots.append(slots)

        # Remaining moves do not share cards
        if min_n_slots_probas == 1 and len(stored_cards) == 1:
            # Only one move remains
            # if len(stored_cards) == 1:
            card = stored_cards[0]
            slot = stored_slots[0]
            return slot[0], card

        # Remaining moves share at least one card. For each such move
        # (card + slot), record the second best move
        # not using the card (its replacement if it was killed).
        # Play the move who replacement is the worst.
        else:
            move_slot_win_proba = []
            for stored_card, card_stored_slots in zip(stored_cards, stored_slots):
                for stored_slot in card_stored_slots:
                    for slot, comb, slot_win_proba, _ in all_comb_win_probas:
                        # if slot != stored_slot or stored_card in comb:
                        # we kill moves not using this card in the current slot
                        if slot == stored_slot and stored_card not in comb:
                            continue
                        # we kill moves using this card in every other slot
                        if stored_card in comb:
                            continue

                        # Stop at the earliest (e.g. with highest proba)
                        # move and record the slot win proba.
                        # NB: comb not really needed, only for debugging
                        move_slot_win_proba.append((stored_card, stored_slot, slot_win_proba, comb))
                        break

        if len(move_slot_win_proba) == 0:
            print("DEBUG")
            print(best_moves)

        card, slot, _, _ = max(move_slot_win_proba, key=lambda x: x[2])
        return slot, card

    def make_move(self, game_state):
        # For each slot, the probability of possible combinations
        # (with proba non zero)
        my_slots_probas = self.get_slots_combs_probas(game_state)
        assert(len(my_slots_probas) == 9)
        op_slots_probas = self.get_slots_combs_probas(game_state, True)
        assert (len(op_slots_probas) == 9)

        # Probability to win a slot for a combination in the given
        # slot. Pooled over all slots
        all_comb_win_probas = []

        # For each pair of slots (mine vs the opponent's)
        for slot_index, (m_slot_probas, o_slot_probas) in enumerate(zip(my_slots_probas, op_slots_probas)):
            m_slot_best_comb_probas = self.get_best_comb_probas(m_slot_probas)
            o_slot_best_comb_probas = self.get_best_comb_probas(o_slot_probas)

            if DEBUG:
                print("SLOT N°{}".format(slot_index))
                for c, p, e in m_slot_best_comb_probas:
                    print(c, p, e)
                print("")

                for c, p, e in o_slot_best_comb_probas:
                    print(c, p, e)
                print("")

            # for m_comb, m_proba in m_slot_probas.items():
            for m_comb, m_proba, m_exp in m_slot_best_comb_probas:
                # If at least one card of the combination is
                # in our hand
                is_playable = True if len(self.get_cards_in_hand_from_comb(m_comb)) > 0 else False

                # Proba for the combination to win in this slot
                # FIXME: current computations do not result in good behaviour
                slot_win_score = 0
                # for (o_comb, o_proba) in o_slot_probas.items():
                for o_comb, o_proba, m_exp in o_slot_best_comb_probas:
                    m_score = self.combination_scores[m_comb]
                    o_score = self.combination_scores[o_comb]
                    if m_score > o_score:
                        slot_win_score += m_proba * o_proba
                    elif m_score == o_score:
                        # The adversary finished the same combination before us so we
                        # cannot win this slot
                        if game_state.slots[self.opponent_index][slot_index] == 3:
                            slot_win_score -= m_proba * o_proba
                        else:
                            pass
                    else:
                        slot_win_score -= m_proba * o_proba

                all_comb_win_probas.append((slot_index, m_comb, slot_win_score, is_playable))


        if DEBUG:
            print("all_comb_win_probas")
            for elt in sorted(all_comb_win_probas, key=lambda x: x[2], reverse=True):
                print(elt)
        print("")


        # Playable combinations, provided they do not block a slot having a non-playable
        # combination with higher win probability. Sorted by slot win probability.
        all_comb_win_probas.sort(key=lambda x: x[2], reverse=True)
        best_combs = Player.get_non_locking_best_playable_combinations(all_comb_win_probas)

        if DEBUG:
            print("Non locking")
            for elt in sorted(best_combs, key=lambda x: x[2], reverse=True):
                print(elt)
            print("")

        slot_to_play, card_to_play = self.get_best_move_from_combs(best_combs, all_comb_win_probas)
        return slot_to_play, card_to_play


class Slot(MutableSet):

    def __init__(self):
        self.elements = set()

    def add(self, element):
        if element in self:
            raise ValueError("Slot.add(): cannot have duplicate elements")
        if len(self.elements) == 3:
            raise ValueError("Slot.add(): cannot have more than 3 elements")
        else:
            self.elements.add(element)

    def discard(self, element):
        raise NotImplementedError("Slot.discard(): cannot discard elements")

    def __contains__(self, element):
        return True if element in self.elements else False

    def __iter__(self):
        return self.elements.__iter__()

    def __len__(self):
        return len(self.elements)

    def __repr__(self):
        return self.elements.__repr__()

    def __str__(self):
        return self.elements.__str__()


class GameState:
    def __init__(self, deck=None):
        self._is_init = False
        # Where players build their combinations
        self.slots = [[Slot() for _ in range(9)], [Slot() for _ in range(9)]]
        if deck is None:
            self.deck = set([])
        else:
            self.deck = set(deck)

    @property
    def deck(self):
        raise AttributeError("GameState.deck is private."
                             "The public interface consists of the "
                             "deck_size attribute and method draw_deck()")

    @deck.setter
    def deck(self, deck):
        if not self._is_init:
            self._deck = deck
            self._is_init = True
        else:
            raise AttributeError("GameState.deck is private."
                                 "The public interface consists of the "
                                 "deck_size attribute and method draw_deck()")

    @property
    def deck_size(self):
        return len(self._deck)

    def draw_deck(self):
        return self._deck.pop()


class Game:
    def __init__(self, player0, player1):
        self.players = [player0, player1]
        self.players[0].index = 0
        self.players[1].index = 1
        self.first_to_finish_slot = [None for _ in range(9)]

        cards = list(ALL_CARDS)
        rng.shuffle(cards)
        for i in range(6):
            self.players[0].hand.add(cards.pop())
            self.players[1].hand.add(cards.pop())
        self.game_state = GameState(cards)

    def player_turn(self, player_index):
        slot_index, card = self.players[player_index].make_move(self.game_state)
        assert(card in self.players[player_index].hand)

        self.game_state.slots[player_index][slot_index].add(card)
        if len(self.game_state.slots[player_index][slot_index]) == 3 and \
                self.first_to_finish_slot is None:
            self.first_to_finish_slot = player_index

        self.players[player_index].hand.remove(card)

        if self.game_state.deck_size > 0:
            self.players[player_index].hand.add(self.game_state.draw_deck())

    def game_winner(self):
        player_n_slot_won = [0, 0]
        for i, (slot0, slot1) in enumerate(zip(self.game_state.slots[0], self.game_state.slots[1])):
            if len(slot0) == 3 and len(slot1) == 3:
                slot_winner = self.get_slot_winner(i)
                if slot_winner is not None:
                    player_n_slot_won[slot_winner] += 1
        if player_n_slot_won[0] == 5:
            return 0
        elif player_n_slot_won[1] == 5:
            return 1
        else:
            return None

    def get_slot_winner(self, slot_index):
        (card1, card2, card3, ) = self.game_state.slots[0][slot_index]
        p0_comb = CardCombination(card1, card2, card3)
        (card1, card2, card3, ) = self.game_state.slots[1][slot_index]
        p1_comb = CardCombination(card1, card2, card3)
        if p0_comb.category > p1_comb.category:
            return 0
        elif p0_comb.category == p1_comb.category and p0_comb.value > p1_comb.value:
            return 0
        elif p0_comb.category < p1_comb.category:
            return 1
        elif p0_comb.category == p1_comb.category and p0_comb.value < p1_comb.value:
            return 1
        else:
            return self.first_to_finish_slot[slot_index]

    @staticmethod
    def display_slot(slot_index, slot):
        if len(slot) == 3:
            (c1, c2, c3,) = slot
            comb = CardCombination(c1, c2, c3)
            print("  - {}: {}".format(slot_index + 1, comb))
        else:
            print("  - {}: {}".format(slot_index + 1, slot))

    def display_game(self):
        print("deck_size: {}".format(self.game_state.deck_size))
        print("--")
        print("p0 hand: {}".format(self.players[0].hand))
        for i, slot in enumerate(self.game_state.slots[0]):
            Game.display_slot(i, slot)
        print("--")
        print("p1 hand: {}".format(self.players[1].hand))
        for i, slot in enumerate(self.game_state.slots[1]):
            Game.display_slot(i, slot)

    def play(self):
        self.display_game()
        print("")
        game_over = None
        while game_over is None:
            self.player_turn(0)
            self.display_game()
            self.player_turn(1)
            self.display_game()
            game_over = self.game_winner()
            print("")

        print("Winner: {}".format(self.game_over()))
        for i, (slot0, slot1) in enumerate(zip(self.game_state.slots[0], self.game_state.slots[1])):
            slot_winner = None
            if len(slot0) == 3 and len(slot1) == 3:
                slot_winner = self.get_slot_winner(i)
            print("Winner for slot {}: player {}".format(i, slot_winner))
            print(Game.display_slot(slot0))
            print(Game.display_slot(slot1))
            print("--")

