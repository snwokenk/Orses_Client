from Crypto.Hash import SHA256, RIPEMD160

from Orses_Cryptography.DigitalSignerValidator import DigitalSignerValidator

import time, json, base64


class MiscMessageValidator:

    def __init__(self, misc_msg_dict, wallet_pubkey, user_instance, timelimit=300, price_per_byte=0.000011):

        self.user = user_instance
        self.misc_msg_dict_json = json.dumps(misc_msg_dict["misc_msg"])
        self.sending_wallet_pubkey = wallet_pubkey
        self.signature = misc_msg_dict['sig']
        self.msg_hash = misc_msg_dict["msg_hash"]
        self.main_msg = misc_msg_dict["misc_msg"]
        self.msg = self.main_msg["msg"]
        self.purp = self.main_msg["purp"]
        self.msg_fee = self.main_msg["fee"]
        self.timelimit = timelimit
        self.price_per_byte = price_per_byte
        self.msg_size = self.calc_msg_size()

    def __get_pubkey_bytes(self):

        return base64.b85decode(self.sending_wallet_pubkey['x'].encode())+base64.b85decode(self.sending_wallet_pubkey['y'].encode())

    def check_validity(self):

        if (self.check_signature_valid() and
                self.check_balance_enough_for_fee()):
            return True
        else:
            return False

    def check_signature_valid(self):

        response = DigitalSignerValidator.validate_wallet_signature(msg=self.misc_msg_dict_json,
                                                                    wallet_pubkey=self.sending_wallet_pubkey,
                                                                    signature=self.signature)
        print("sig check: ", response)
        if response is True:
            return True
        else:
            return False

    def calc_msg_size(self, pubkey_key_size=100, hash_size=64, time_size=10, fee_size=10):

        size_of_msg = len(self.msg) + len(self.purp)
        return size_of_msg + pubkey_key_size + hash_size + time_size +  fee_size

    def calc_minimum_msg_cost(self):
        """
        Messgage cost returned as ntakiriis 1 ORS = 10,000,000,000
        :return:
        """
        return int(round(self.msg_size * self.price_per_byte, 10) * 1e10)

    def check_balance_enough_for_fee(self):
        """
        Checks to verify message fee is enough and if wallet has enough tokens
        :return:
        """
        try:
            msg_fee = int(round(float(self.msg_fee), 10)*1e10)
        except ValueError as e:
            print(f" in MiscMessageValidator error: {e}")
            return False
        else:
            try:
                if msg_fee >= int(round(self.user.wallet_service_instance.wallet_instance.get_balance(), 10) * 1e10):
                    return True
                else:
                    print(f"in MiscMessageValidator, msg_fee not enough")
                    return False
            except AttributeError as e:
                print(f"in Misc_messages_Msg_class, error {e}")
                return False


