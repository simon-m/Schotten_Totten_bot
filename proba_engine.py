from card_combinations import CardCombination, CardCombinationsGenerator
import collections
from game_elements import MAX_CARDS_PER_HAND


class ProbaEngine:

    @staticmethod
    # To compute the probability for us to get a card from the deck.
    # We must account for the opponent's cards which cannot be
    # accessed.
    def deck_proba(deck_size):
        # Proba the card is in the deck and not in the opponent's hand:
        # proba_in_deck = deck_size / (deck_size + MAX_CARDS_PER_HAND)
        # Proba to get the card from the deck if it is there:
        # proba_from_deck = 0 if deck_size == 0 else 1 / deck_size
        # The product is equivalent to:
        # 0 if deck_size == 0 else 1 / (deck_size + MAX_CARDS_PER_HAND)
        # Note: the we do not need to know the number of cards in anyone's
        # hand because if it is not the maximum it means that the deck size
        # is 0
        return 0 if deck_size == 0 else 1 / (deck_size + MAX_CARDS_PER_HAND)

    @staticmethod
    # To compute the probability for the opponent to get a card without
    # knowing their hand
    def deck_or_hand_proba(deck_size):
        # Proba the card is in the opponent's hand:
        # proba_in_hand = MAX_CARDS_PER_HAND / (deck_size + MAX_CARDS_PER_HAND)
        # Proba to get it (since it is in their hand):
        # proba_from hand = 1
        # Proba the card is in the deck and not in the opponent's hand:
        # proba_in_deck = deck_size / (deck_size + MAX_CARDS_PER_HAND)
        # proba to get the card from the deck if it is there:
        # proba_from_deck = 0 if deck_size == 0 else 1 / deck_size
        # The product is equivalent to:
        # 1 if deck_size == 0 else (MAX_CARDS_PER_HAND + 1) / (deck_size + MAX_CARDS_PER_HAND)
        # Note: the we do not need to know the number of cards in anyone's
        # hand because if it is not the maximum it means that the deck size
        # is 0
        return 1 if deck_size == 0 else (MAX_CARDS_PER_HAND + 1) / (deck_size + MAX_CARDS_PER_HAND)

    @staticmethod
    def card_is_in_slots(card, slots, pass_index=None):
        for i, slot in enumerate(slots):
            if i == pass_index:
                continue
            if card in slot:
                return True
        return False

    # For_opponent: compute the opponent combination proba given our
    # own knowledge
    @staticmethod
    def _compute_probas_for_slot(player, allowed_combs, slot_index,
                                 game_state, for_opponent=False):

        if for_opponent:
            my_slot_index = None
            op_slot_index = slot_index
            slot = game_state.slots[player.opponent_index][slot_index]
        else:
            my_slot_index = slot_index
            op_slot_index = None
            slot = game_state.slots[player.index][slot_index]

        # comb_probas = collections.defaultdict(int)
        comb_probas = {}
        for comb in allowed_combs:
            proba = 1

            for card in comb:
                # One card in the combination has been played in
                # another slot already
                if ProbaEngine.card_is_in_slots(card, game_state.slots[player.index], my_slot_index):
                    proba = 0
                    break
                if ProbaEngine.card_is_in_slots(card, game_state.slots[player.opponent_index], op_slot_index):
                    proba = 0
                    break

                if for_opponent:
                    # We have that card in our hand so the opponent cannot have it
                    if card in player.hand:
                        proba = 0
                        break
                    # The card is in the current (opponent's) slot so
                    # the proba of the combination remains the same
                    if card in slot:
                        pass  # proba *= 1
                    # Proba the opponent has the card or gets it from the deck
                    else:
                        proba *= ProbaEngine.deck_or_hand_proba(game_state.deck_size)
                else:
                    # We have that card in our hand or it is in the current
                    # slot so the proba of the combination remains the same
                    if card in player.hand or card in slot:
                        pass  # proba *= 1
                    # Proba to get the card from the deck
                    else:
                        proba *= ProbaEngine.deck_proba(game_state.deck_size)

            if proba != 0:
                comb_probas[comb] = proba

        return comb_probas

    @staticmethod
    def combination_probas_from_slot(player, game_state,
                                     slot_index, for_opponent=False):
        ccg = CardCombinationsGenerator()

        if for_opponent:
            c_slot = game_state.slots[player.opponent_index][slot_index]
        else:
            c_slot = game_state.slots[player.index][slot_index]

        if len(c_slot) == 0:
            # The only thing we now is that the opponent cannot play with
            # our cards whether in a slot or in our hand
            if for_opponent:
                forbidden_cards = player.hand.copy()
                for slot in game_state.slots[player.index]:
                    for card in slot:
                        forbidden_cards.add(card)
                allowed_combs = ccg.get_combinations_excluding_cards(forbidden_cards)
            else:
                allowed_combs = set()
                for card in player.hand:
                    # all  possible combinations considering our hand i.e.
                    # combinations for which we have at least one card.
                    # The result does not depend on the slot
                    allowed_combs |= ccg.get_combinations_from_card(card)
        elif len(c_slot) == 1:
            (card,) = c_slot
            # all  possible combinations using the card in that slot
            allowed_combs = ccg.get_combinations_from_card(card)
        elif len(c_slot) == 2:
            (card1, card2, ) = c_slot
            # all  possible combinations using the two cards in that slot
            allowed_combs = ccg.get_combinations_from_pair_of_cards(card1, card2)
        elif len(c_slot) == 3:
            if for_opponent:
                (c1, c2, c3) = c_slot
                return {CardCombination(c1, c2, c3): 1}
            else:
                return {}
        else:
            raise ValueError("ProbaEngine.combination_proba_started_slot:" +
                             "slot must contain between 0 and 2 cards." +
                             "{} found".format(len(c_slot)))

        comb_probas = ProbaEngine._compute_probas_for_slot(player, allowed_combs,
                                                           slot_index, game_state,
                                                           for_opponent)
        return comb_probas
