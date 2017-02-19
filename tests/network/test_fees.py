# from time import sleep, time
#
# from bit.network import get_fee, get_fee_cached
#
#
# def test_get_fee():
#     assert get_fee(fast=True) != get_fee(fast=False)
#
#
# class TestFeeCache:
#     def test_fast(self):
#         start_time = time()
#         get_fee_cached(fast=True)
#         initial_time = time() - start_time
#
#         start_time = time()
#         get_fee_cached(fast=True)
#         cached_time = time() - start_time
#
#         assert initial_time > cached_time
#
#     def test_hour(self):
#         start_time = time()
#         get_fee_cached(fast=False)
#         initial_time = time() - start_time
#
#         start_time = time()
#         get_fee_cached(fast=False)
#         cached_time = time() - start_time
#
#         assert initial_time > cached_time
#
#     def test_expires(self):
#         get_fee_cached()
#
#         start_time = time()
#         get_fee_cached()
#         cached_time = time() - start_time
#
#         sleep(0.2)
#
#         start_time = time()
#         get_fee_cached(expires=0.1)
#         update_time = time() - start_time
#
#         assert update_time > cached_time
