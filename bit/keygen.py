import os

from multiprocessing import Event, Process, Queue, cpu_count

from bit.base58 import BASE58_ALPHABET
from bit.crypto import (
    DEFAULT_BACKEND, SECP256K1, derive_privkey
)
from bit.format import point_to_public_key, public_key_to_address
from bit.utils import int_to_hex


def derive_private_key(num):
    return derive_privkey(num, SECP256K1, DEFAULT_BACKEND)


def generate_private_key():
    return derive_privkey(
        int.from_bytes(os.urandom(32), 'big'), SECP256K1, DEFAULT_BACKEND
    )


def generate_key_address_pair():

    private_key = generate_private_key()

    public_key = point_to_public_key(
        private_key.public_key().public_numbers(), compressed=True
    )

    address = public_key_to_address(public_key)

    return int_to_hex(private_key.private_numbers().private_value), address


def generate_matching_address(prefix, cores='all'):  # pragma: no cover

    for char in prefix:
        if char not in BASE58_ALPHABET:
            raise ValueError('{} is an invalid base58 encoded '
                             'character.'.format(char))

    if not prefix:
        return generate_key_address_pair()
    elif not prefix.startswith('1'):
        prefix = '1' + prefix

    available_cores = cpu_count()

    if cores == 'all':
        cores = available_cores
    elif 0 < cores <= available_cores:
        cores = cores
    else:
        cores = 1

    queue = Queue()
    match = Event()
    workers = []

    for _ in range(cores):
        workers.append(
            Process(target=stream_key_address_pairs, args=(queue, match))
        )

    for worker in workers:
        worker.start()

    while True:
        private_value, address = queue.get()

        if address.startswith(prefix):
            match.set()
            for worker in workers:
                worker.join()
            return int_to_hex(private_value), address


def stream_key_address_pairs(queue, event):  # pragma: no cover

    while True:

        private_key = generate_private_key()

        public_key = point_to_public_key(
            private_key.public_key().public_numbers(), compressed=True
        )

        address = public_key_to_address(public_key)

        queue.put_nowait((private_key.private_numbers().private_value, address))

        if event.is_set():
            return
