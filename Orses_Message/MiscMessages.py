import time, json
from Orses_Cryptography import DigitalSigner
from Crypto.Hash import SHA256


class MiscMessages:

    def __init__(self, sending_wid, msg, price_per_byte=0.000011, purp='misc'):
        """

        :param sending_wid:
        :param msg:
        :param price_per_byte: fee per byte
        :param purp: purpose of message
        """
        self.sending_wid = sending_wid
        self.msg = msg
        self.price_per_byte = price_per_byte
        self.timestamp = int(time.time())
        self.purp = purp

    def calc_msg_size(self, pubkey_key_size=100, hash_size=64, time_size=10, fee_size=10):

        size_of_msg = len(self.msg) + len(self.purp)
        return size_of_msg + pubkey_key_size + hash_size + time_size + fee_size

    def determine_fee(self):

        return round(self.calc_msg_size() * self.price_per_byte, 10)

    def create_misc_msg(self):

        mm = {
            'msg': self.msg,
            'purp': self.purp,
            'time': self.timestamp,
            'fee': self.determine_fee()

        }

        return mm

    def sign_and_return_misc_message(self, wallet_privkey, wallet_pubkey):

        if wallet_privkey:
            misc_msg = self.create_misc_msg()

            signature = DigitalSigner.DigitalSigner.wallet_sign(message=json.dumps(misc_msg).encode(),
                                                                wallet_privkey=wallet_privkey)

            if signature is None:
                return {}

            msg_hash = SHA256.new(json.dumps(misc_msg).encode()).hexdigest()

            misc_msg_dict = {
                'msg_hash': msg_hash,
                'misc_msg': misc_msg,
                'sig': signature

            }

            return misc_msg_dict

        else:
            return {}
