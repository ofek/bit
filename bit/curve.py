FIELD_SIZE = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
TONELLI_SHANKS_CONSTANT = (FIELD_SIZE + 1) // 4


def x_to_y(x, parity):

    y = pow(x ** 3 + 7, TONELLI_SHANKS_CONSTANT, FIELD_SIZE)

    if y & 1 != parity:
        y = FIELD_SIZE - y

    return y
