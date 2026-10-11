import math
import unittest

import numpy as np

import chords


class TestChords(unittest.TestCase):
    def test_pairings_are_permutations(self):
        p = chords.all_pairings()
        self.assertEqual(len(p), math.factorial(8))
        self.assertTrue(all(sorted(row) == list(chords.N_SLOTS) for row in p[:: 997]))
        for step in (1, 3, 5, 7):
            self.assertEqual(sorted(chords.fixed_offset(step)), list(chords.N_SLOTS))
            self.assertEqual(chords.chord_lengths(chords.fixed_offset(step)), [step] * 8)

    def test_mean_over_the_ring(self):
        # Π|e_j − s| = |1 − s^16| on the 16 roots of unity, so the mean of −ln|e − s| is
        # −ln|1 − s^16| / 16, near 0 for a source inside: the reference as a quiet point.
        s = np.array([[0.5, 0.2]])
        z = complex(0.5, 0.2)
        self.assertAlmostEqual(chords.potentials(s).mean(), -math.log(abs(1 - z ** 16)) / 16)


if __name__ == "__main__":
    unittest.main()
