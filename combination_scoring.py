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
        # numbers) rebased to 0 for the smallest.
        # Min value: 0 (1+1+2 - 4); max value: 22 (9+9+8 - 4)
        if comb.category == 0:
            return comb.value - 4

        # Suite: score is the max value of the sum
        # plus value of the combination (the smallest number
        # of the suite).
        # Min value: 22 + 1 = 23; max value = 22 + 7 = 29
        if comb.category == 1:
            return 22 + comb.value

        # Color: score is the max value of the suite plus
        # the combination value (sum of numbers) rebased to 1.
        # Min value: 29 + 1+2+4 - 6 = 30; max value: 29 + 9+8+6 - 6 = 46
        if comb.category == 2:
            return 29 + comb.value - 6

        # Set: score is the max value of the color plus
        # the value of the combination (number).
        # Min value: 46 + 1 = 47; max value: 46 + 9 = 55
        if comb.category == 3:
            return 46 + comb.value

        # Color suite: score is the max value of the set
        # plus de la value of the combination (smallest
        # number).
        # Min value: 55 + 1 = 56; max value: 55 + 7 = 62
        if comb.category == 4:
            return 55 + comb.value
