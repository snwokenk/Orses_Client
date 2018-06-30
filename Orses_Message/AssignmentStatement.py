import time, base64
from Orses_Cryptography import DigitalSigner
from Crypto.Hash import SHA256


"""
Things an assignment statement needs:
-Sending Wallet ID
-Receiving Wallet ID
-amount of tokens
-Blockchain Wallet ID
-sending wallet private key
-sending client private key
-Timestamp of Creation
"""


class AssignmentStatement:
    def __init__(self, sending_wid, receiving_wid, bk_connected_wid, amount_of_tokens,
                 fee=0.0001, timelimit=300):
        self.sending_wid = sending_wid
        self.receiving_wid = receiving_wid
        self.bk_connected_wid = bk_connected_wid
        self.amount_of_tokens = amount_of_tokens
        self.timestamp = int(time.time())
        self.fee = fee
        self.timelimit = timelimit

    def get_statement_dict(self):

        assignment_statement = {

            "snd_wid": self.sending_wid,
            "rcv_wid": self.receiving_wid,
            "amt": self.amount_of_tokens,
            "bk_con_wid": self.bk_connected_wid,
            "time": self.timestamp,
            "fee": self.fee,

        }

        return assignment_statement




    def create_conditional_assignment_statement(self, unconditional=False):
        """

        :param unconditional: bool, this is true ONLY when a blockchain connected wallet is fulfilling a conditional
        :return: string, assignment statement
        """
        fee = 1 + self.fee

        # unconditional used by Blockchain Connected Wallets to fulfil conditional statement
        if unconditional:
            assignment_statement = "{} Assigns {} CryptoHub Tokens TO {} On Behalf Of {} At {} UTC ".format(
                self.bk_connected_wid, self.amount_of_tokens, self.receiving_wid, self.sending_wid, self.timestamp
            )
        else:
            assignment_statement = "{}|{}|{}|{}|{}|{}|{}".format(
                self.sending_wid, self.receiving_wid, self.bk_connected_wid, self.amount_of_tokens, self.fee,
                self.timestamp, self.timelimit)

        # if unconditional:
        #     assignment_statement = "{} Assigns {} CryptoHub Tokens TO {} On Behalf Of {} At {} UTC ".format(
        #         self.bk_connected_wid, self.amount_of_tokens, self.receiving_wid, self.sending_wid, self.timestamp
        #     )
        # else:
        #     assignment_statement = "{} Assigns {} CryptoHub Tokens TO {} IF Same Assigns {} CryptoHub Tokens " \
        #                            "To {} By {} UTC".format(
        #         self.sending_wid, self.amount_of_tokens * fee, self.bk_connected_wid, self.amount_of_tokens,
        #         self.receiving_wid, self.timestamp + self.timelimit
        #     )
        return assignment_statement

    def sign_and_return_conditional_assignment_statement(self, wallet_privkey):
        """
        gets assignment statement and signs it.
        creates an assignment statement dictionary and includes base85 string

        steps:
        1. get signature and base85 encode byte. this will turn bytes from xbe/ type format to ascii character
            > b = base64.b85encode(signature)
        2. decode the b85 encode, this will give us a string
            > b_string = b.decode()

        enco

        :param wallet_privkey:
        :return:
        """

        if wallet_privkey:

            # get assignment statement and encode()
            asgn_stmt = self.create_conditional_assignment_statement()

            # returns base64.b85encode bytes string, to decode use base64.b85decode(bytes string)
            signature = DigitalSigner.DigitalSigner.wallet_sign(message=asgn_stmt.encode(),
                                                                wallet_privkey=wallet_privkey)
            if signature is None:
                return {}

            statement_hash = SHA256.new(asgn_stmt.encode()).hexdigest()

            # before broadcasting must add wallet pubkey and client pubkey
            asgn_stmt_dict = {
                "asgn_stmt": asgn_stmt,
                "sig": signature,
                "stmt_hsh": statement_hash,
            }
            return asgn_stmt_dict

        else:  # private key = b'' which means attempted decryption was with wrong password
            return {}


