import unittest

from main import HuurCalc


class TestHuurCalc(unittest.TestCase):
    def setUp(self):
        self.calculator = HuurCalc(
            room_studio_sqm=59,
            total_shared_area_sqm=0,
            shared_living_room=False,
            shared_kitchen=False,
            shared_shower=False,
            shared_toilet=False,
            total_residents=1
        )

    def test_dependant_room_sqm_points(self):
        expected_points = 295.0
        self.assertEqual(self.calculator.dependant_room_sqm_points, expected_points)

    def test_heating_points(self):
        expected_points = 44.25
        self.assertEqual(self.calculator.heating_points, expected_points)

    def test_bonus_points_kitchen(self):
        expected_points = 20
        self.assertEqual(self.calculator.bonus_points(bonus_type="kitchen"), expected_points)

    def test_bonus_points_toilet(self):
        expected_points = 22
        self.assertEqual(self.calculator.bonus_points(bonus_type="toilet"), expected_points)

    def test_bonus_points_shower(self):
        expected_points = 15
        self.assertEqual(self.calculator.bonus_points(bonus_type="shower"), expected_points)

    def test_bonus_points_nonexistent_type(self):
        expected_points = 0
        self.assertEqual(self.calculator.bonus_points(bonus_type="nonexistent_type"), expected_points)

    def test_bonus_points_shared_max_residents(self):
        self.calculator.total_residents = 6
        self.calculator.shared_toilet = True
        expected_points = 0
        self.assertEqual(self.calculator.bonus_points(bonus_type="toilet"), expected_points)

    def test_bonus_points_shared_within_max_residents(self):
        self.calculator.total_residents = 5
        self.calculator.shared_toilet = True
        expected_points = 4
        self.assertEqual(self.calculator.bonus_points(bonus_type="toilet"), expected_points)

    def test_bonus_points_own(self):
        self.calculator.shared_kitchen = False
        expected_points = 20
        self.assertEqual(self.calculator.bonus_points(bonus_type="kitchen"), expected_points)

    def test_bonus_points_shared_false(self):
        self.calculator.shared_kitchen = False
        expected_points = 20
        self.assertEqual(self.calculator.bonus_points(bonus_type="kitchen"), expected_points)

    def test_bonus_points_shared_true(self):
        self.calculator.shared_kitchen = True
        expected_points = 4
        self.assertEqual(self.calculator.bonus_points(bonus_type="kitchen"), expected_points)

    def test_calculate_points(self):
        expected_points = 408.25
        self.assertEqual(self.calculator.calculate_points(), expected_points)


if __name__ == '__main__':
    unittest.main()