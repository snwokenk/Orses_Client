from Crypto.Hash import SHA256, RIPEMD160

from Orses_Cryptography.DigitalSignerValidator import DigitalSignerValidator

import time, json


class TokenRevokeRequestValidator:

    def __init__(self, tkn_rvk_dict, wallet_pubkey, user_instance):
        self.user = user_instance
        self.wallet_pubkey = wallet_pubkey
        self.rvk_req_json = json.dumps(tkn_rvk_dict["rvk_req"])
        self.client_id = tkn_rvk_dict["client_id"]
        self.wallet_id = tkn_rvk_dict["rvk_req"]["req_wid"]
        self.signature = tkn_rvk_dict["sig"]
        self.tx_hash = tkn_rvk_dict["tx_hash"]
        self.trr_tx_hash = tkn_rvk_dict["rvk_req"]["trr_hash"]
        pass

    def check_validity(self):
        if (self.check_client_id_owner_of_wallet(),
                self.check_signature_valid(),
                self.check_reservation_meets_minimum_time()):

            # update activities of wallet
            self.user.wallet_service_instance.wallet_instance.update_to_activites(
                activity_type="trx", tx_obj=json.loads(self.rvk_req_json), act_hash=self.tx_hash)
            return True
        else:
            return False

    def check_client_id_owner_of_wallet(self):
        step1 = SHA256.new(self.wallet_pubkey + self.client_id.encode()).digest()
        derived_wid = "W" + RIPEMD160.new(step1).hexdigest()

        print("owner check: ", derived_wid == self.wallet_id)

        return derived_wid == self.wallet_id

    def check_signature_valid(self):
        response = DigitalSignerValidator.validate_wallet_signature(msg=self.rvk_req_json,
                                                                    wallet_pubkey=self.wallet_pubkey,
                                                                    signature=self.signature)
        print("sig check: ", response)
        if response is True:
            return True
        else:
            return False

    def check_reservation_meets_minimum_time(self):
        """
        used to check if the reservation to be revoked has been reserved for at least 1/4 time of length of reservation
        :return:
        """

        # todo: check reservation using the hash, and verify it has been reserved for at least 1/4 of len of reservation
        # todo: checking will requiring checking activity

        activities = self.user.wallet_service_instance.wallet_instance.get_activities()

        if self.trr_tx_hash in activities:

            # find duration
            duration = activities[self.trr_tx_hash]["expiration"] - activities[self.trr_tx_hash]["time"] if \
                activities[self.trr_tx_hash]["type"] == "trr" else 0
            if duration > 0:

                # USE THIS FOR TESTING PURPOSES
                return self.user.wallet_service_instance.wallet_instance.check_if_token_revoke_request_allowed()

                min_timestamp = activities[self.trr_tx_hash]["time"] + int(duration/4)
                return int(time.time()) >= min_timestamp

        else:
            print("rsv_len check: ", None)
            return None

        return None
