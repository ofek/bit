# from bit.crypto import EllipticCurvePrivateKey
# from bit.curve import Point
# from bit.format import wif_to_private_key_hex
# from bit.keygen import derive_private_key, generate_private_key
# from bit.network import MultiBackend
# from bit.utils import hex_to_int, int_to_hex
#
#
# class PrivateKey:
#     def __init__(self, wif=None, sync=False):
#         if wif:
#             if isinstance(wif, EllipticCurvePrivateKey):
#                 self._pk = wif
#             else:
#                 num = hex_to_int(wif_to_private_key_hex(wif))
#                 self._pk = derive_private_key(num)
#         else:
#             self._pk = generate_private_key()
#
#         public_point = self._pk.public_key().public_numbers()
#         self.public_point = Point(public_point.x, public_point.y)
#
# Key = PrivateKey
