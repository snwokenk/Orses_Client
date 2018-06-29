from Crypto.Hash import SHA256, RIPEMD160

from Orses_Cryptography.DigitalSignerValidator import DigitalSignerValidator

import time, json, base64


class TransferTransactionValidator:
    def __init__(self, transfer_tx_dict, wallet_pubkey, user_instance, timelimit=300):
        self.user = user_instance
        self.transfer_tx_dict_json = json.dumps(transfer_tx_dict["ttx"])
        self.sending_wallet_pubkey = wallet_pubkey
        self.sending_wid = transfer_tx_dict["ttx"]["snd_wid"]
        self.sending_client_id = transfer_tx_dict["client_id"]
        self.signature = transfer_tx_dict["sig"]
        self.tx_hash = transfer_tx_dict["tx_hash"]
        self.timestamp = transfer_tx_dict["ttx"]["time"]
        self.timelimit = timelimit

    def __get_pubkey_bytes(self):

        return base64.b85decode(self.sending_wallet_pubkey['x'].encode())+base64.b85decode(self.sending_wallet_pubkey['y'].encode())


    def check_validity(self):
        if (self.check_client_id_owner_of_wallet(),
                self.check_signature_valid(),
                self.check_timestamp()):
            self.user.wallet_service_instance.wallet_instance.update_to_activites(
                activity_type="ttx", tx_obj=json.loads(self.transfer_tx_dict_json), act_hash=self.tx_hash)
            return True
        else:
            return False

    def check_client_id_owner_of_wallet(self):
        step1 = SHA256.new(self.__get_pubkey_bytes() + self.sending_client_id.encode()).digest()
        derived_wid = "W" + RIPEMD160.new(step1).hexdigest()

        print("owner checkr: ", derived_wid == self.sending_wid)

        return derived_wid == self.sending_wid

    def check_signature_valid(self):
        response = DigitalSignerValidator.validate_wallet_signature(msg=self.transfer_tx_dict_json,
                                                                    wallet_pubkey=self.sending_wallet_pubkey,
                                                                    signature=self.signature)
        print("sig check: ", response)
        if response is True:
            return True
        else:
            return False

    def check_timestamp(self):
        rsp = int(time.time()) < int(self.timestamp + self.timelimit)

        print("time check", rsp)
        return rsp