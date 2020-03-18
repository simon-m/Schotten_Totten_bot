from utils import pairwise

# Base scores are designed so that consecutive combinations have a difference
# of 1 and that they are ordered according to they category first and
# value second.
# The importance of categories relative to each others can then be altered.


class ScoringScheme:
    def __init__(self, category_factors=(1, 1, 1, 1, 1)):
        if category_factors[0] <= 0:
            raise ValueError("ScoringScheme: category factors must be > 0")
        for f1, f2 in pairwise(category_factors):
            if f1 > f2:
                raise ValueError("ScoringScheme: category factors must in non-decreasing order")
        self.category_factors = category_factors

    def get_score(self, comb):
        return ScoringScheme.get_base_score(comb) * self.category_factors[comb.category]

    @staticmethod
    def get_base_score(comb):
        # Sum: score is the combination value (sum of
        # numbers) rebased to 1 for the smallest.
        # Min value: 1 (1+1+2 - 3); max value: 23 (9+9+8 - 3)
        if comb.category == 0:
            return comb.value - 3

        # Suite: score is the max value of the sum
        # plus value of the combination (the smallest number
        # of the suite).
        # Min value: 23 + 1 = 24; max value = 23 + 7 = 30
        if comb.category == 1:
            return 23 + comb.value

        # Color: score is the max value of the suite plus
        # the combination value (sum of numbers) rebased to 1.
        # Min value: 30 + 1+2+4 - 6 = 31; max value: 30 + 9+8+6 - 6 = 47
        if comb.category == 2:
            return 24 + comb.value

        # Set: score is the max value of the color plus
        # the value of the combination (number).
        # Min value: 47 + 1 = 48; max value: 47 + 9 = 56
        if comb.category == 3:
            return 47 + comb.value

        # Color suite: score is the max value of the set
        # plus de la value of the combination (smallest
        # number).
        # Min value: 56 + 1 = 57 max value: 56 + 7 = 63
        if comb.category == 4:
            return 56 + comb.value
