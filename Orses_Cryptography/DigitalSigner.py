from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS

from Orses_Cryptography import PKIGeneration, Decryption
from Orses_Util import FileAction as FName

import base64

FileAction = FName.FileAction
PKI = PKIGeneration.PKI
Decrypt = Decryption.Decrypt


class DigitalSigner:
    def __init__(self, username, password):
        """
        class for digitally signing
        :param username: string,  privkey names after username
        :param password: string, used to decrypt privkey
        """
        self.username = username
        self.password = password
        self.privkey = None

        # sets self.privkey
        self.__set_or_create_key_if_not_exist()

    def __set_or_create_key_if_not_exist(self):
        """
        used to set self.privkey to private key saved under username or generate new one and set
        :return:
        """

        # instantiate PKI class:
        pki = PKI(username=self.username, password=self.password)

        # load private key into object. key is ready to be used to sign already imported
        privkey = pki.load_priv_key()

        # if it is an empty list then no key created and saved on username so generate new key
        if not privkey:
            pki.generate_pub_priv_key()
            privkey = pki.load_priv_key()  # loaded as a key object ready to use for signing

        # set self.privkey to privkey
        self.privkey = privkey

    def sign(self, message):
        """
        signs message with private key of username
        :param message: bytes string or string
        :return: bytes; signature of message using private key
        """

        # if not already a byte string turn it to making sure
        if not isinstance(message, (bytes, str)):
            message = str(message).encode()
        elif isinstance(message, str):
            message = message.encode()

        hash_of_message = SHA256.new(message)

        signer = DSS.new(self.privkey, mode="fips-186-3")

        digital_signature = signer.sign(hash_of_message)

        return digital_signature

    @staticmethod
    def wallet_sign(wallet_privkey, message):
        """
        static method used to sign with wallet privkey. used in conjunction with WalletService class
        :param wallet_privkey: private key of wallet, already imported key
        :param message: byte string,message to be signed, usually bytes of signature of client private key
        :return: bytes, digital signature
        """

        hash_of_message = SHA256.new(message)

        signer = DSS.new(wallet_privkey, mode="fips-186-3")

        digital_signature = signer.sign(hash_of_message)
        digital_signature = base64.b85encode(digital_signature).decode()

        return digital_signature
