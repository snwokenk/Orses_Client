"""
This class is used to manage the assignment statement network message object
A network message manager handles the updating of this class

A network message will have what attribute the message is trying to update in a message object
"""

from Crypto.Hash import SHA256, RIPEMD160

from Orses_Cryptography.DigitalSignerValidator import DigitalSignerValidator
from Orses_Database import Database, CreateDatabase, RetrieveData

import time, base64


# TODO: complete assgn statement class. Allow statement to be stored locally and broadcasted for verification by nodes
# TODO: and by the blockchain connected wallet

class AssignmentStatementValidator:
    """
    This class is instantiated by client and used to check validity of message,
    Then assign stmt send to node and this class is used by node to check also.
    if message is validated, node sends a ver message
    else a rej message is sent if invalid
    """
    def __init__(self, asgn_stmt_dict, wallet_pubkey, user):
        self.user = user
        self.asgn_stmt= asgn_stmt_dict["asgn_stmt"]
        self.asgn_stmt_list = asgn_stmt_dict["asgn_stmt"].split(sep='|')
        self.sending_wallet_pubkey = wallet_pubkey
        self.sending_wid = self.asgn_stmt_list[0]
        self.sending_client_id = asgn_stmt_dict["client_id"]
        self.signature = asgn_stmt_dict["sig"]
        self.stmt_hash = asgn_stmt_dict["stmt_hsh"]
        self.timestamp = self.asgn_stmt_list[-2]
        self.timelimit = self.asgn_stmt_list[-1]

    def __get_pubkey_bytes(self):

        return base64.b85decode(self.sending_wallet_pubkey['x'].encode())+base64.b85decode(self.sending_wallet_pubkey['y'].encode())

    def check_validity(self):
        if (self.check_client_id_owner_of_wallet(),
                self.check_signature_valid(),
                self.check_timestamp()):
            self.user.wallet_service_instance.wallet_instance.update_to_activites(
                activity_type="asgn_stmt", tx_obj=self.asgn_stmt_list, act_hash=self.stmt_hash)
            return True
        else:
            return False

    def check_client_id_owner_of_wallet(self):
        step1 = SHA256.new(self.__get_pubkey_bytes() + self.sending_client_id.encode()).digest()
        derived_wid = "W" + RIPEMD160.new(step1).hexdigest()

        print("owner checkr: ", derived_wid == self.sending_wid)

        return derived_wid == self.sending_wid

    def check_signature_valid(self):
        response = DigitalSignerValidator.validate_wallet_signature(msg=self.asgn_stmt,
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






