import sys
import time
import hmac
import signal
from base64 import b32decode
import subprocess

class TOTPGenerator:
    
    def __init__(self, b32_secret, token_length=6):
        assert(len(b32_secret) % 4 == 0 and token_length in (6, 8))
        self.key = b32decode(b32_secret)
        self.token_length = token_length
        # We only support sha1.
        self.hash_name = 'sha1'
        self.modulus = 10 ** self.token_length

    def __call__(self):
        def intr_handler(signum, frame):
            print('')
            sys.exit(0)
        signal.signal(signal.SIGINT, intr_handler)
        print('Generating TOTP codes.  Enter Control-C to stop.')
        while True:
            token = self.current_token()
            print(f'\r{token}          ', end='')
            time.sleep(self.lifespan())

    def lifespan(self):
        """Number of seconds before the current token expires."""
        return 30 - (int(time.time()) % 30)

    def current_time_message(self, tv=None):
        """Returns a byte sequence of length 8 padded with leading 0's"""
        now = tv if tv else time.time()
        time_value = int(now) // 30
        result = time_value.to_bytes(length=8, byteorder='big')
        return result
                             
    def current_hash(self, tv=None):
        """Returns the hmac-sha1 digest as a byte sequence."""
        message = self.current_time_message(tv=tv)
        return hmac.digest(self.key, message, self.hash_name)

    def current_token(self, tv=None):
        """Returns a token value as a string"""
        hash = self.current_hash(tv=tv)
        # Use the last 4 bits of the hash as an index < 16
        offset = hash[-1] & 0xf;
        # Use the 4 bytes starting at the offset to construct the token.
        block = list(hash[offset:offset + 4])
        # Mask the sign bit.
        block[0] &= 0x7f
        # Build the 32 bit token.
        value = (block[0] << 24) | (block[1] << 16) | (block[2] << 8) | block[3]
        # Truncate to the specified number of digits
        otp = value % self.modulus
        return str(otp).zfill(self.token_length)
