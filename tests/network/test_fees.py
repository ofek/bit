# from time import sleep, time
#
# import bit
# from bit.network.fees import get_fee, get_fee_cached, set_fee_cache_time
#
#
# def test_set_fee_cache_time():
#     original = bit.network.fees.DEFAULT_CACHE_TIME
#     set_fee_cache_time(30)
#     updated = bit.network.fees.DEFAULT_CACHE_TIME
#
#     assert original != updated
#     assert updated == 30
#
#     set_fee_cache_time(original)
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
