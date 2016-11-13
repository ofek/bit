from multiprocessing import Event, Process, Queue, cpu_count

from bit.base58 import BASE58_ALPHABET, b58encode
from bit.crypto import (
    DEFAULT_BACKEND, RIPEMD160, SECP256K1, SHA256, Hash, generate_private_key
)
from bit.format import (
    MAIN_PUBKEY_HASH, PUBLIC_KEY_UNCOMPRESSED,
    point_to_public_key, public_key_to_address
)
from bit.utils import int_to_hex


def generate_key_address_pair():

    private_key = generate_private_key(SECP256K1, DEFAULT_BACKEND)

    public_key = point_to_public_key(
        private_key.public_key().public_numbers(), compressed=False
    )

    bitcoin_address = public_key_to_address(public_key)

    return int_to_hex(
        private_key.private_numbers().private_value
    ), bitcoin_address


def generate_matching_address(prefix, cores='all'):

    available_cores = cpu_count()

    if not cores:
        cores = 1
    elif cores == 'all':
        cores = available_cores
    elif 0 < cores <= available_cores:
        cores = cores
    else:
        cores = 1

    for char in prefix:
        if char not in BASE58_ALPHABET:
            raise ValueError('{} is an invalid base58 encoded '
                             'character.'.format(char))

    if not prefix:
        return generate_key_address_pair()
    elif not prefix.startswith('1'):
        prefix = '1' + prefix

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


def stream_key_address_pairs(queue, event):

    while True:

        private_key = generate_private_key(SECP256K1, DEFAULT_BACKEND)
        public_key_point = private_key.public_key().public_numbers()

        x = public_key_point.x.to_bytes(32, 'big')
        y = public_key_point.y.to_bytes(32, 'big')

        public_key = PUBLIC_KEY_UNCOMPRESSED + x + y

        public_key_digest = Hash(SHA256, DEFAULT_BACKEND)
        public_key_digest.update(public_key)
        public_key_digest = public_key_digest.finalize()

        ripemd160 = Hash(RIPEMD160, DEFAULT_BACKEND)
        ripemd160.update(public_key_digest)
        ripemd160 = MAIN_PUBKEY_HASH + ripemd160.finalize()

        ripemd160_digest = Hash(SHA256, DEFAULT_BACKEND)
        ripemd160_digest.update(ripemd160)
        ripemd160_digest = ripemd160_digest.finalize()

        address_checksum = Hash(SHA256, DEFAULT_BACKEND)
        address_checksum.update(ripemd160_digest)
        address_checksum = address_checksum.finalize()[:4]

        binary_address = ripemd160 + address_checksum
        bitcoin_address = b58encode(binary_address)

        queue.put_nowait((private_key.private_numbers().private_value, bitcoin_address))

        if event.is_set():
            return
