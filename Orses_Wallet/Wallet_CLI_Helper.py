# python module imports
# from subprocess import call

#cryptohub
from Orses_User.User import User
from Orses_Util.win_lin_mac_check import shell_command as call
import getpass


class WalletCLI:
    def __init__(self, user):
        self.user = user
        assert isinstance(self.user, User)

    def create_wallet(self, wallet_nickname, wallet_password, wallet_password1):
        """
        If return true, wallet_instance can be accessed using self.user.wallet_service_instance.wallet_instance

        :param wallet_nickname: chosen wallet nickname
        :param wallet_password: chosen password
        :param wallet_password1: chosen password typed again for verification
        :return: True if all, None if wallet with same nickname exists on local computer,
                 False if password and password1 do not match
        """

        if wallet_password != wallet_password1:
            return False

        # if all ok, then new wallet is created with wallet object returned, If a wallet
        return self.user.create_wallet(wallet_nickname=wallet_nickname, wallet_password=wallet_password)

    def load_wallet(self, wallet_nickname, wallet_password):
        """

        :param wallet_nickname: wallet nickname
        :param wallet_password: wallet password used to encrypt wallet
        :return: Wallet Object if all, None if wallet with nickname does not exist on local computer,
                 False if wrong password provided
        """

        return self.user.load_wallet(wallet_nickname=wallet_nickname, password=wallet_password)

    def unload_wallet(self):

        self.user.unload_wallet()

    def list_wallets(self):
        call("clear")
        print("\n\n\t* Welcome To The Command Line Interface Of The CryptoHub Blockchain Client *\n\n")
        print("*** YOU'RE LOGGED IN AS: {} | Client ID: {} ***\n\n".format(self.user.username, self.user.client_id))
        print("List of Wallets Owned By Client ID: \n\n")

        self.user.get_list_of_owned_wallets()
        input("\nPress Enter To Continue\n")
        call("clear")

