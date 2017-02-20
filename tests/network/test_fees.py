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
#         sleep(0.2)
#
#         start_time = time()
#         get_fee_cached(fast=True, expires=0)
#         initial_time = time() - start_time
#
#         start_time = time()
#         get_fee_cached(fast=True, expires=600)
#         cached_time = time() - start_time
#
#         assert initial_time > cached_time
#
#     def test_hour(self):
#         sleep(0.2)
#
#         start_time = time()
#         get_fee_cached(fast=False, expires=0)
#         initial_time = time() - start_time
#
#         start_time = time()
#         get_fee_cached(fast=False, expires=600)
#         cached_time = time() - start_time
#
#         assert initial_time > cached_time
#
#     def test_expires(self):
#         sleep(0.2)
#
#         get_fee_cached(fast=False, expires=0)
#
#         start_time = time()
#         get_fee_cached(fast=False, expires=600)
#         cached_time = time() - start_time
#
#         sleep(0.2)
#
#         start_time = time()
#         get_fee_cached(expires=0.1)
#         update_time = time() - start_time
#
#         assert update_time > cached_time
