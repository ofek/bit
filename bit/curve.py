from collections import namedtuple

FIELD_SIZE = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
GROUP_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
TONELLI_SHANKS_CONSTANT = (FIELD_SIZE + 1) // 4


Point = namedtuple('Point', ('x', 'y'))


def parity(num):
    return num & 1


def x_to_y(x, y_parity):

    y = pow(x ** 3 + 7, TONELLI_SHANKS_CONSTANT, FIELD_SIZE)

    if parity(y) != y_parity:
        y = FIELD_SIZE - y

    return y
