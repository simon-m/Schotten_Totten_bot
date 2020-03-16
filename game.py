import random
import itertools
import numpy as np
from collections import defaultdict
from collections.abc import MutableSet
from proba_engine import ProbaEngine
from combination_scoring import ScoringScheme
from card_combinations import CardCombinationsGenerator, CardCombination
from game_elements import ALL_CARDS, Card


# TODO: consider the fact the other player finished first when computing
# TODO: the success of a slot
class Player:
    def __init__(self, index=0, combination_scorer=ScoringScheme()):
        self.index = index
        self.opponent_index = 1 if self.index == 0 else 0
        self.hand = set()
        ccg = CardCombinationsGenerator()
        cs = combination_scorer
        self.combination_scores = {comb: cs.get_score(comb) for comb in ccg.get_all_combinations()}

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
        # Probas are the same for the empty slots so no need to compute *
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

    @staticmethod
    def get_non_locking_best_playable_combinations(all_comb_win_probas):
        # TODO: assert input is sorted
        # Sort by decreasing slot win probability
        # comb_win_probas = sorted(all_comb_win_probas, key=lambda x: x[2], reverse=True)

        # A slot is locked if the combination with highest slot win
        # probability is not playable. We keep it for later.
        slot_is_locked = [None] * 9
        selected_combs = []
        for elt in all_comb_win_probas:
            slot_index = elt[0]
            is_playable = elt[3]
            # This is the first (with highest slot win proba) combination
            # for this slot and it is not playable: lock the slot.
            # Keep only the playable combinations
            if slot_is_locked[slot_index] is None:
                if not is_playable:
                    slot_is_locked[slot_index] = True
                else:
                    slot_is_locked[slot_index] = False
                    selected_combs.append(elt)
            elif is_playable and not slot_is_locked[slot_index]:
                selected_combs.append(elt)
        # return comb_win_probas
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
        # other possible moves). If there are several such cases,
        # play one at random for the moment.
        # If there are no such moves (all best moves share at
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
            elif len(slots) < min_n_slots_probas:
                stored_cards.append(card)
                stored_slots.append(slots)

        # Remaining moves do not share cards
        if min_n_slots_probas == 1:
            # Only one move remains
            if len(stored_cards) == 1:
                card = stored_cards[0]
                slot = stored_slots[0]
                return slot[0], card
            # Multiple moves remain, play one at random. Since none of them kill
            # other combinations, we should be safe (hopefully)
            else:
                return_index = random.randint(range(len(stored_cards)))
                card = stored_cards[return_index]
                slot = stored_slots[return_index]
                return slot[0], card
        # Remaining moves share at least one card. For each such move
        # (card + slot), record the second best move in the same slot
        # not using the card (its replacement if it was killed).
        # Play the move who replacement is the worst.
        else:
            move_slot_win_proba = []
            for stored_card, card_stored_slots in zip(stored_cards, stored_slots):
                for stored_slot in card_stored_slots:
                    for slot, comb, slot_win_proba, _ in all_comb_win_probas:
                        if slot != stored_slot or stored_card in comb:
                            continue
                        # Stop at the earliest (e.g. with highest proba)
                        # move and record the slot win proba.
                        # NB: comb not really needed, only for debugging
                        move_slot_win_proba.append((stored_card, stored_slot, slot_win_proba, comb))
                        break

        card, slot, _, _ = min(move_slot_win_proba, key= lambda x: x[2])
        return slot, card

    def get_best_comb_probas(self, slot_probas, depth):

        comb_list = []
        proba_array = np.ndarray(shape=(len(slot_probas)))
        expectation_array = np.ndarray(shape=(len(slot_probas)))

        if len(slot_probas) <= depth:
            res = []
            for (m_comb, m_proba) in slot_probas.items():
                res.append((m_comb, m_proba))
            return res

        for i, (m_comb, m_proba) in enumerate(slot_probas.items()):
            comb_list.append(m_comb)
            proba_array[i] = m_proba
            expectation_array[i] = m_proba * self.combination_scores[m_comb]

        best_indexes = np.argpartition(-expectation_array, depth)[:depth]
        res = []
        for i in best_indexes:
            res.append((comb_list[i], proba_array[i]))
        return res

    def make_move(self, game_state, depth=10):
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
            # TODO: this iterates over the cartesian product of my_combinations * op_combinations
            # TODO: to reduce the computational burden, one could limit the product to the
            # TODO: k combinations with highest proba / expectation (score * proba)
            # TODO: k would be a kind of depth parameter. Smaller k would make for a weaker
            # TODO: player (adjustable difficulty level)

            m_slot_best_comb_probas = self.get_best_comb_probas(m_slot_probas, depth)
            o_slot_best_comb_probas = self.get_best_comb_probas(o_slot_probas, depth)

            """
            if slot_index <= 1:
                print("SLOT N°{}".format(slot_index))
                for c, p in o_slot_best_comb_probas:
                    print(c, p)
                print("")

                for c, p in m_slot_best_comb_probas:
                    print(c, p)
                print("")
            """


            # for m_comb, m_proba in m_slot_probas.items():
            for m_comb, m_proba in m_slot_best_comb_probas:
                # If at least one card of the combination is
                # in our hand
                is_playable = True if len(self.get_cards_in_hand_from_comb(m_comb)) > 0 else False

                # Proba for the combination to win in this slot
                slot_win_score = 0
                # for (o_comb, o_proba) in o_slot_probas.items():
                for (o_comb, o_proba) in o_slot_best_comb_probas:
                    if self.combination_scores[m_comb] > self.combination_scores[o_comb]:
                        slot_win_score += m_proba * o_proba

                all_comb_win_probas.append((slot_index, m_comb, slot_win_score, is_playable))

            if slot_index <= 1:
                print("all_comb_win_probas")
                for elt in sorted(all_comb_win_probas, key=lambda x: x[2], reverse=True):
                    print(elt)
            print("")

        # Playable combinations, provided they do not block a slot having a non-playable
        # combination with higher win probability. Sorted by slot win probability.

        all_comb_win_probas.sort(key=lambda x: x[2], reverse=True)
        best_combs = Player.get_non_locking_best_playable_combinations(all_comb_win_probas)

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
    def __init__(self, player0, player1, game_state):
        self.players = [player0, player1]
        self.players[0].index = 0
        self.players[1].index = 1
        self.game_state = game_state
        self.first_to_finish_slot = [None for _ in range(9)]

        cards = list(ALL_CARDS)
        random.shuffle(cards)
        for i in range(6):
            self.players[0].hand.append(cards.pop())
            self.players[1].hand.append(cards.pop())
        self.game_state.deck = cards

    def player_turn(self, player_index):
        slot_index, card = self.players[player_index].make_move(self.game_state)
        assert(card in self.players[player_index].hand)

        self.game_state[player_index][slot_index].add(card)
        if len(self.game_state[player_index][slot_index]) == 3 and \
                self.first_to_finish_slot is None:
            self.first_to_finish_slot = player_index

        self.players[player_index].hand.remove(card)

        if self.game_state.deck_size > 0:
            self.players[player_index].hand.append(self.game_state.draw_deck())

    def game_over(self):
        for slot0, slot1 in zip(self.game_state.slots[0], self.game_state.slots[1]):
            if len(slot0) != 3 and len(slot1 != 3):
                return False
            return True

    def get_winner(self):
        for i, (slot0, slot1) in enumerate(zip(self.game_state.slots[0], self.game_state.slots[1])):
            p0_comb = CardCombination(slot0[0], slot0[1], slot0[2])
            p1_comb = CardCombination(slot0[0], slot0[1], slot0[2])
            if p0_comb.category > p1_comb.category:
                return 0
            elif p0_comb.category == p1_comb.category and p0_comb.value > p1_comb.value:
                return 0
            elif p0_comb.category < p1_comb.category:
                return 1
            elif p0_comb.category == p1_comb.category and p0_comb.value < p1_comb.value:
                return 1
            else:
                return self.first_to_finish_slot[i]

    def play(self):
        while not self.game_over():
            self.player_turn(0)
            self.player_turn(1)

        print(self.get_winner())

