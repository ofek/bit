import sys
import time
from multiprocessing import Event, Process, Queue, Value, cpu_count

from coincurve import Context

from bit.base58 import BASE58_ALPHABET, b58encode_check
from bit.crypto import ECPrivateKey, ripemd160_sha256
from bit.format import bytes_to_wif, public_key_to_address


def generate_key_address_pair():  # pragma: no cover
    private_key = ECPrivateKey()
    address = public_key_to_address(private_key.public_key.format())
    return bytes_to_wif(private_key.secret), address


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

    counter = Value('i')
    match = Event()
    queue = Queue()

    workers = []
    for _ in range(cores):
        workers.append(
            Process(
                target=generate_key_address_pairs,
                args=(prefix, counter, match, queue)
            )
        )

    for worker in workers:
        worker.start()

    keys_generated = 0
    while True:
        time.sleep(1)
        current = counter.value
        if current == keys_generated:
            if current == 0:
                continue
            break
        keys_generated = current
        s = 'Keys generated: {}\r'.format(keys_generated)
        sys.stdout.write(s)
        sys.stdout.flush()

    private_key, address = queue.get()
    print('\n\n'
          'WIF: {}\n'
          'Address: {}'.format(bytes_to_wif(private_key), address))


def generate_key_address_pairs(prefix, counter, match, queue):  # pragma: no cover

    context = Context()

    while True:
        if match.is_set():
            return

        with counter.get_lock():
            counter.value += 1

        private_key = ECPrivateKey(context=context)
        address = b58encode_check(
            b'\x00' + ripemd160_sha256(private_key.public_key.format())
        )

        if address.startswith(prefix):
            match.set()
            queue.put_nowait((private_key.secret, address))
            return
