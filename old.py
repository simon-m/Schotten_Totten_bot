
class CardCombinationsGenerator:
    @staticmethod
    def get_color_suites_from_color_number(c_color, c_number):
        assert (c_color in card_colors)
        assert (c_number in card_numbers)

        if c_number == 1:
            return {CardCombination(Card(c_color, c_number),
                                    Card(c_color, c_number + 1),
                                    Card(c_color, c_number + 2))}

        elif c_number == 2:
            return {CardCombination(Card(c_color, c_number - 1),
                                    Card(c_color, c_number),
                                    Card(c_color, c_number + 1)),
                    CardCombination(Card(c_color, c_number),
                                    Card(c_color, c_number + 1),
                                    Card(c_color, c_number + 2))}

        elif c_number == 8:
            return {CardCombination(Card(c_color, c_number - 2),
                                    Card(c_color, c_number - 1),
                                    Card(c_color, c_number)),
                    CardCombination(Card(c_color, c_number - 1),
                                    Card(c_color, c_number),
                                    Card(c_color, c_number + 1))}

        elif c_number == 9:
            return {CardCombination(Card(c_color, c_number - 2),
                                    Card(c_color, c_number - 1),
                                    Card(c_color, c_number))}

        else:
            return {CardCombination(Card(c_color, c_number - 2),
                                    Card(c_color, c_number - 1),
                                    Card(c_color, c_number)),
                    CardCombination(Card(c_color, c_number - 1),
                                    Card(c_color, c_number),
                                    Card(c_color, c_number + 1)),
                    CardCombination(Card(c_color, c_number),
                                    Card(c_color, c_number + 1),
                                    Card(c_color, c_number + 2))}


    @staticmethod
    def get_sets_from_color_number(c_color, c_number):
        assert (c_color in card_colors)
        assert (c_number in card_numbers)

        result = set()
        for color_comb in itertools.combinations(card_colors, 3):
            if c_color in color_comb:
                c1, c2, c3 = color_comb
                result.add(CardCombination(Card(c1, c_number),
                                           Card(c2, c_number),
                                           Card(c3, c_number)))
        return result


    @staticmethod
    def get_colors_from_color_number(c_color, c_number):
        assert (c_color in card_colors)
        assert (c_number in card_numbers)

        allowed_numbers = card_numbers - set([c_number])
        res = set()
        for comb in itertools.combinations(allowed_numbers, 2):
            res.add(CardCombination(Card(c_color, c_number),
                                    Card(c_color, comb[0]),
                                    Card(c_color, comb[1])))
        return res


    @staticmethod
    def get_suites_from_color_number(c_color, c_number):
        assert (c_color in card_colors)
        assert (c_number in card_numbers)

        res = set()
        allowed_colors = card_colors - set([c_color])

        if c_number == 1:
            for c1, c2 in itertools.product(card_colors, allowed_colors):
                res.add(CardCombination(Card(c_color, c_number),
                                        Card(c1, c_number + 1),
                                        Card(c2, c_number + 2)))
            for c in allowed_colors:
                res.add(CardCombination(Card(c_color, c_number),
                                        Card(c, c_number + 1),
                                        Card(c_color, c_number + 2)))
            return res

        elif c_number == 2:
            for c1, c2 in itertools.product(card_colors, allowed_colors):
                res.add(CardCombination(Card(c_color, c_number - 1),
                                        Card(c1, c_number),
                                        Card(c2, c_number + 1)))
                res.add(CardCombination(Card(c_color, c_number),
                                        Card(c1, c_number + 1),
                                        Card(c2, c_number + 2)))
            for c in allowed_colors:
                res.add(CardCombination(Card(c_color, c_number - 1),
                                        Card(c, c_number),
                                        Card(c_color, c_number + 1)))
                res.add(CardCombination(Card(c_color, c_number),
                                        Card(c, c_number + 1),
                                        Card(c_color, c_number + 2)))
            return res

        elif c_number == 8:
            for c1, c2 in itertools.product(card_colors, allowed_colors):
                res.add(CardCombination(Card(c_color, c_number - 2),
                                        Card(c1, c_number - 1),
                                        Card(c2, c_number)))
                res.add(CardCombination(Card(c_color, c_number - 1),
                                        Card(c1, c_number),
                                        Card(c2, c_number + 1)))
            for c in allowed_colors:
                res.add(CardCombination(Card(c_color, c_number - 2),
                                        Card(c, c_number - 1),
                                        Card(c_color, c_number)))
                res.add(CardCombination(Card(c_color, c_number - 1),
                                        Card(c, c_number),
                                        Card(c_color, c_number + 1)))
            return res

        elif c_number == 9:
            for c1, c2 in itertools.product(card_colors, allowed_colors):
                res.add(CardCombination(Card(c_color, c_number - 2),
                                        Card(c1, c_number - 1),
                                        Card(c2, c_number)))
            for c in allowed_colors:
                res.add(CardCombination(Card(c_color, c_number - 2),
                                        Card(c, c_number - 1),
                                        Card(c_color, c_number)))
            return res

        else:
            for c1, c2 in itertools.product(card_colors, allowed_colors):
                res.add(CardCombination(Card(c_color, c_number - 2),
                                        Card(c1, c_number - 1),
                                        Card(c2, c_number)))
                res.add(CardCombination(Card(c_color, c_number - 1),
                                        Card(c1, c_number),
                                        Card(c2, c_number + 1)))
                res.add(CardCombination(Card(c_color, c_number),
                                        Card(c1, c_number + 1),
                                        Card(c2, c_number + 2)))
            for c in allowed_colors:
                res.add(CardCombination(Card(c_color, c_number - 2),
                                        Card(c, c_number - 1),
                                        Card(c_color, c_number)))
                res.add(CardCombination(Card(c_color, c_number - 1),
                                        Card(c, c_number),
                                        Card(c_color, c_number + 1)))
                res.add(CardCombination(Card(c_color, c_number),
                                        Card(c, c_number + 1),
                                        Card(c_color, c_number + 2)))
            return res

    @staticmethod
    def get_combinations_from_color_number(c_color, c_number):
        """
        res = all_comb - CardCombinationsGenerator().get_color_suites_from_color_number(c_color, c_number)
        res = res - CardCombinationsGenerator().get_color_suites_from_color_number(c_color, c_number)
        res = CardCombinationsGenerator().get_color_suites_from_color_number(c_color, c_number)
        res.extend(CardCombinationsGenerator().get_sets_from_color_number(c_color, c_number))
        res.extend( CardCombinationsGenerator().get_colors_from_color_number(c_color, c_number))
        res.extend(CardCombinationsGenerator().get_suites_from_color_number(c_color, c_number))
        # res.extend(CardCombinationsGenerator().get_sums_from_color_number(c_color, c_number))
        return res
        """


"""
Unit Tests
"""


def test_color_suites(self):
    for c in card_colors:
        for n in card_numbers:
            for comb in CardCombinationsGenerator.get_color_suites_from_color_number(c, n):

                numbers = []
                for elt in comb:
                    # Check it is indeed a *color* suite
                    self.assertTrue(elt.color == c)
                    numbers.append(elt.number)

                # Check correct bound for a suite of 3 numbers
                self.assertTrue(min(numbers) >= n - 2)
                self.assertTrue(max(numbers) <= n + 2)
                # Check the required number is part of the suite
                self.assertIn(n, numbers)
                # Check numbers are consecutive
                self.assertEqual(numbers[1] - numbers[0], 1)
                self.assertEqual(numbers[2] - numbers[1], 1)


def test_sets(self):
    for n in card_numbers:
        for c in card_colors:
            for comb in CardCombinationsGenerator.get_sets_from_color_number(c, n):

                color_counts = collections.defaultdict(int)
                for elt in comb:
                    # Check all number equal the required number
                    self.assertEqual(elt.number, n)
                    color_counts[elt.color] += 1

                # Check we have three different colors
                color_counts = color_counts.values()
                self.assertEqual(max(color_counts), 1)
                self.assertEqual(sum(color_counts), 3)


def test_colors(self):
    for n in card_numbers:
        for c in card_colors:

            number_counts = collections.defaultdict(int)
            for comb in CardCombinationsGenerator.get_colors_from_color_number(c, n):
                for elt in comb:
                    # Check colors are the same as the required color
                    self.assertEqual(elt.color, c)
                    number_counts[elt.number] += 1

            # Check that each number appears in 7 (9 - required number - the remaining position)
            # combinations except the required one which must appear in all 28 (8 choose 2) of them
            allowed_numbers = card_numbers - set([n])
            for an in allowed_numbers:
                self.assertEqual(number_counts[an], 7)
            self.assertEqual(number_counts[n], 28)


def test_suites(self):
    for c in card_colors:
        for n in card_numbers:
            for comb in CardCombinationsGenerator.get_suites_from_color_number(c, n):

                numbers = []
                colors = set()
                for elt in comb:
                    numbers.append(elt.number)
                    colors.add(elt.color)

                # Check it is not a color suite
                self.assertNotEqual(len(colors), 1)

                # Check correct bound for a suite of 3 numbers
                self.assertTrue(min(numbers) >= n - 2)
                self.assertTrue(max(numbers) <= n + 2)
                # Check the required number is part of the suite
                self.assertIn(n, numbers)
                # Check numbers are consecutive
                self.assertEqual(numbers[1] - numbers[0], 1)
                self.assertEqual(numbers[2] - numbers[1], 1)
