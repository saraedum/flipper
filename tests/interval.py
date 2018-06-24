
import unittest
from math import log10 as log
from itertools import product

import flipper

interval = flipper.kernel.Interval.from_string

class TestInterval(unittest.TestCase):
    def test_product(self):
        w = interval('0.10')
        x = interval('10000.0')
        y = interval('1.14571')
        z = interval('1.00000')
        a = interval('-1.200000')
        b = interval('1.4142135623')
        
        # Check:
        #    acc(I + J) >= min(acc(I), acc(J)) - 1,
        #    acc(I * J) >= min(acc(I), acc(J)) - log(I.lower + J.lower + 1)
        #    acc(I / J) >= min(acc(I), acc(J)) - log+(J)  # If J > I.
        #    acc(x * I) >= acc(I) - log+(x)
        
        for I, J in product([w, x, y, z, a, b], repeat=2):
            m = min(I.accuracy, J.accuracy)
            self.assertGreaterEqual((I + J).accuracy, m - 1)
            self.assertGreaterEqual((I * J).accuracy, m - log(max(I.lower + J.lower + 1, 1)))
            # self.assertGreaterEqual((I / J).accuracy, m - J.log_plus()) # Should only do this test when J > I.

