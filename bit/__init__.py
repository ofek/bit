from bit.format import verify_sig
from bit.network.fees import set_fee_cache_time
from bit.network.rates import SUPPORTED_CURRENCIES, set_rate_cache_time
from bit.network.services import set_service_timeout
from bit.wallet import Key, PrivateKey, PrivateKeyTestnet, wif_to_key, MultiSig, MultiSigTestnet

__version__ = '0.5.2'
