"""
Token Transfers are used to send tokens using the blockchain directly. Unlike Assignment Statements,
which use a blockchain connected wallet and get their immutability by being included in the "state" of that wallet,
Token Transfers on the other hand are directly included on the blockchain and
"""
import time, json
from Orses_Cryptography import DigitalSigner
from Crypto.Hash import SHA256


class TokenTransferTransaction:

    def __init__(self, sending_wid, receiving_wid, amount_of_tokens, fee):
        self.sending_wid = sending_wid
        self.receiving_wid = receiving_wid
        self.amount_of_tokens = amount_of_tokens
        self.fee = fee
        self.timestamp = int(time.time())

    def create_transfer_transaction(self):

        tt = {
            "snd_wid": self.sending_wid,
            "rcv_wid": self.receiving_wid,
            "amt": self.amount_of_tokens,
            "fee": self.fee,
            "time": self.timestamp
        }

        return tt

    def sign_and_return_transfer_transaction(self, wallet_privkey):

        if wallet_privkey:
            transfer_tx = self.create_transfer_transaction()

            print(transfer_tx)

            signature = DigitalSigner.DigitalSigner.wallet_sign(message=json.dumps(transfer_tx).encode(),
                                                                wallet_privkey=wallet_privkey)

            if signature is None:
                return {}
            tx_hash = SHA256.new(json.dumps(transfer_tx).encode()).hexdigest()

            transfer_tx_dict = {
                'ttx': transfer_tx,
                'sig': signature,
                "tx_hash": tx_hash

            }

            return transfer_tx_dict

        else:  # private key = b'' which means attempted decryption was with wrong password
            return {}
