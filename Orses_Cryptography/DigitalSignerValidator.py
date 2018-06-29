from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA, ECC

#todo: reimplement feautures using RSA

import base64


class DigitalSignerValidator:

    def __init__(self,  pubkey):
        """

        to turn pubkey to
        used to validate signature of message
        :param pubkey: dict {"x": base85encoded string, "y": same as x}

        """
        self.pubkey = None
        self.__import_pubkey(pubkey)

    def __import_pubkey(self, pubkey):
        """
        creates an rsa pub key object and sets self.pubkey to it
        :param pubkey: hex or bytes representation of key
        :return: None
        """

        # new implementation public key is two numbers {"x": base85 string, "y": base85 string}
        # this string can be turned back into number using:
        # x_int = base64.b85decode(string.encode())
        # x_int = int.from_bytes(x_int, "big")
        try:
            self.pubkey = RSA.importKey(bytes.fromhex(pubkey))
        except TypeError:
            if isinstance(pubkey, bytes):
                self.pubkey = RSA.importKey(pubkey)

    def validate(self, message, signature):
        """
        used to validate signature
        :param message: string or byte string, message to validate signature(assignment statements, token transfers etc)
        :param signature: bytes string or hex string
        :return:
        """
        if self.pubkey is None or not isinstance(message, (str, bytes)):
            return ''
        elif not isinstance(signature, (str, bytes)):
            return ''



        try:
            hash_of_message = SHA256.new(message)
        except TypeError:
            hash_of_message = SHA256.new(message.encode())
        if isinstance(signature, str):
            signature = bytes.fromhex(signature)

        try:
            pkcs1_15.new(self.pubkey).verify(hash_of_message, signature=signature)
        except ValueError:
            return False
        else:
            return True

    @staticmethod
    def validate_wallet_signature(msg, wallet_pubkey: dict, signature):
        """

        :param msg:
        :param wallet_pubkey:
        :param signature:
        :return:
        """
        try:
            x_int = base64.b85decode(wallet_pubkey["x"].encode())
            x_int = int.from_bytes(x_int, "big")

            y_int = base64.b85decode(wallet_pubkey["y"].encode())
            y_int = int.from_bytes(y_int, "big")
        except KeyError:
            return False

        signature = signature.encode()
        signature = base64.b85decode(signature)

        # if it a string
        try:
            hash_of_message = SHA256.new(msg)
        except TypeError:
            hash_of_message = SHA256.new(msg.encode())

        try:
            wallet_pubkey = ECC.construct(point_x=x_int, point_y=y_int, curve="P-256").public_key()
            verifier = DSS.new(wallet_pubkey, mode="fips-186-3")
            verifier.verify(hash_of_message, signature=signature)
        except ValueError:
            return False
        else:
            return True



