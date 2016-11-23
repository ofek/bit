from bit.curve import Point, parity, x_to_y

X_CORRECT = 98231826851265556411949131072518137307566044384771278023089249290926817658893
Y_CORRECT = 18202689367598691302416718951920096486924260449729227135214517092930543058138
X_INCORRECT = 84395689074811850896746984745435708062140394031010675730965970759955946040649
Y_INCORRECT = 97122067812098339855636182336061335085559307076875328452244111716883256386667


class TestXToY:
    def test_x_to_y_correct_first_solution(self):
        assert x_to_y(X_CORRECT, Y_CORRECT & 1) == Y_CORRECT

    def test_x_to_y_incorrect_first_solution(self):
        assert x_to_y(X_INCORRECT, Y_INCORRECT & 1) == Y_INCORRECT


def test_parity():
    assert parity(2) == 0
    assert parity(5) == 1


def test_point():
    x, y = 5, 10
    point = Point(x, y)
    assert (x, y) == point
    assert repr(point) == 'Point(x=5, y=10)'
