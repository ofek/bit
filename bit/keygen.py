from multiprocessing import Event, Process, Queue, cpu_count

from coincurve import Context

from bit.base58 import BASE58_ALPHABET
from bit.crypto import ECPrivateKey
from bit.format import public_key_to_address
from bit.utils import bytes_to_hex


def generate_key_address_pair():  # pragma: no cover

    private_key = ECPrivateKey()

    address = public_key_to_address(private_key.public_key.format())

    return bytes_to_hex(private_key.secret), address


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
    elif 0 < int(cores) <= available_cores:
        cores = int(cores)
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

    keys_generated = 0

    while True:
        private_key, address = queue.get()
        keys_generated += 1
        if keys_generated % 10000 == 0:
            print(keys_generated)

        if address.startswith(prefix):
            match.set()
            for worker in workers:
                worker.join()
            return bytes_to_hex(private_key), address


def stream_key_address_pairs(queue, event):  # pragma: no cover

    context = Context()

    while True:

        private_key = ECPrivateKey(context=context)

        address = public_key_to_address(private_key.public_key.format())

        queue.put_nowait((private_key.secret, address))

        if event.is_set():
            return
