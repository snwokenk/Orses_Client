"""
contains class for deriving encryption key from password using pbkdf2 algorithm
"""
import hashlib, timeit

from Crypto.Protocol import KDF
from Crypto.Random import random

from Orses_Util.FileAction import FileAction


class PasswordKey:
    def __init__(self, password, salt, desired_key_len=32):
        """

        :param password: string, must be string
        :param salt: bytes, must be bytes (will through a TypeError if not) but type error says must be string (flaw)
        :param desired_key_len: for AES256 key len is 32
        """
        self.password = password
        self.salt = salt
        self.lenght_of_key = desired_key_len

    def get_key(self):
        """
        :return:
        """

        key = KDF.PBKDF2(password=self.password, salt=self.salt, count=100000, dkLen=self.lenght_of_key)
        return key

    @staticmethod
    def decide_iterations(target_time=5):
        """
        This method will be used to decide iterations. This iteration will be encrypted with a regular pin
        and then the complete password info encrypted.

        When private key is to be decrypted, pin will be used to decrypt number of iterations and then password will
        be used to iterate
        :param target_time = this is the target time for iterations, default 5 seconds
        :return: number of iterations
        """
        # using timeit and hashlib, determine how fast a 10000 hash will take

        mysetup = "import hashlib"

        def hash_1000():
            for i in range(10000):
                hashlib.sha256(b'test')

        time_for_10000 = timeit.timeit(setup=mysetup, stmt=hash_1000, number=100)
        iterations_for_target_time = round((10000.00/time_for_10000) * 5)
        return iterations_for_target_time






if __name__ == '__main__':


    p = PasswordKey.decide_iterations()
    print(p)
    # salt1 = random.Random.urandom(16)
    #
    # key = KDF.PBKDF2("7433xxxxxxx", salt=salt1, count=100000, dkLen=32)
    # print(len(key))
    # print(key)

