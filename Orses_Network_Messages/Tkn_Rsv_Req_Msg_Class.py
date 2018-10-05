from Crypto.Hash import SHA256, RIPEMD160

from Orses_Cryptography.DigitalSignerValidator import DigitalSignerValidator

import time, json, base64


class TokenReservationRequestValidator:
    def __init__(self, tkn_rsv_dict, wallet_pubkey, user_instance):
        self.user = user_instance
        self.rsv_req_json = json.dumps(tkn_rsv_dict["rsv_req"])
        self.amount = tkn_rsv_dict["rsv_req"]["amt"]
        self.fee = tkn_rsv_dict["rsv_req"]["fee"]
        self.timestamp = tkn_rsv_dict["rsv_req"]["time"]
        self.resevation_expiration = tkn_rsv_dict["rsv_req"]["exp"]
        self.wallet_pubkey = wallet_pubkey
        self.client_id = tkn_rsv_dict["client_id"]
        self.wallet_id = tkn_rsv_dict["rsv_req"]["req_wid"]
        self.signature = tkn_rsv_dict["sig"]
        self.tx_hash = tkn_rsv_dict["tx_hash"]

    def __get_pubkey_bytes(self):

        return base64.b85decode(self.wallet_pubkey['x'].encode())+base64.b85decode(self.wallet_pubkey['y'].encode())

    def check_validity(self):
        if (self.check_client_id_owner_of_wallet() and
                self.check_signature_valid() and
                self.check_minimum_time() and
                self.check_if_wallet_has_enough_token()):

            # update activities of wallet
            self.user.wallet_service_instance.wallet_instance.update_to_activites(
                activity_type="trr", tx_obj=json.loads(self.rsv_req_json), act_hash=self.tx_hash)
            return True
        else:
            return False

    def check_client_id_owner_of_wallet(self):
        step1 = SHA256.new(self.__get_pubkey_bytes() + self.client_id.encode()).digest()
        derived_wid = "W" + RIPEMD160.new(step1).hexdigest()

        print("owner checkr: ", derived_wid == self.wallet_id)

        return derived_wid == self.wallet_id

    def check_signature_valid(self):
        response = DigitalSignerValidator.validate_wallet_signature(msg=self.rsv_req_json,
                                                                    wallet_pubkey=self.wallet_pubkey,
                                                                    signature=self.signature)
        print("sig check: ", response)
        if response is True:
            return True
        else:
            return False

    def check_if_wallet_has_enough_token(self):
        """
        reservation request must be to reserve at least 250000, fee to reserve is 1 token
        :return: bool, true if amount being reserved and wallet balance is at least 250001
        """

        # checks to make sure tokens reserved are at least 250,000 and wallet has enough for tokens + fees
        rsp = self.user.wallet_service_instance.wallet_instance.get_balance() >= (self.amount + self.fee) >= \
        (250000 + self.fee)

        print("balance check: ", rsp)

        return rsp

    def check_minimum_time(self):
        """
        tokens must be reserved for at least 30*86400 seconds. Reservation could be revoked after 1/4 time has passed
        minimum reservation time = 2592000 seconds
        minimum time until ability to revoke = 648000 seconds (7.5 days)
        :return:
        """
        rsp = (self.resevation_expiration - self.timestamp) >= 2592000  # 30 days in seconds

        print("minimum time check: ", rsp)

        return rsp
