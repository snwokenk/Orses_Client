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

    def create_wallet(self):
        call("clear")
        print("\n\n* Welcome To The Command Line Interface Of The CryptoHub Blockchain Client *\n\n")
        print("\t*** YOU'RE LOGGED IN AS: {} | Client ID: {} ***\n\n".format(self.user.username, self.user.client_id))

        print("Create A Wallet: \n\n")

        wallet_nickname = input("Wallet Nickname: \n")
        wallet_password = getpass.getpass("Wallet Password: ")
        rsp = self.user.create_wallet(wallet_nickname=wallet_nickname, wallet_password=wallet_password)

        if rsp is True:
            wall_inst = self.user.wallet_service_instance.wallet_instance
            print("Wallet Created\n")
            print("Wallet Nickname Is '{}' | Wallet ID IS {} | Time Of Creation is {}\n".format(
                wall_inst.get_wallet_nickname(), wall_inst.get_wallet_id(), wall_inst.get_timestamp_of_creation())
            )
            input("Press Enter To Continue\n")
            call("clear")
            return True

        elif rsp is None:
            print("\n\n* Wallet With That Nickname Already Created On Local Machine *\n")
            input("Press Enter To Continue\"")
            call("clear")
            return None

    def load_wallet(self):
        call("clear")
        print("\n\n* Welcome To The Command Line Interface Of The CryptoHub Blockchain Client *\n\n")
        print("\t*** YOU'RE LOGGED IN AS: {} | Client ID: {} ***\n\n".format(self.user.username, self.user.client_id))

        print("Load A Wallet: \n\n")

        wallet_nickname = input("Wallet Nickname: ")
        wallet_password = getpass.getpass("Wallet Password: ")

        rsp = self.user.load_wallet(wallet_nickname=wallet_nickname, password=wallet_password)

        if rsp is True:
            wall_inst = self.user.wallet_service_instance.wallet_instance
            print("Wallet Loaded\n")
            print("Wallet Nickname Is '{}' | Wallet ID IS {} | Time Of Creation is {}\n".format(
                wall_inst.get_wallet_nickname(), wall_inst.get_wallet_id(), wall_inst.get_timestamp_of_creation())
            )
            input("Press Enter To Continue\n")
            call("clear")
            return True

        elif rsp is None:
            print("\n\n* Wallet With That Nickname Not Associated With Current Logged In User *\n")
            input("Press Enter To Continue\"")
            call("clear")
            return None

        elif rsp is False:
            print("\n\n* Wrong Wallet Password! *\n")
            input("Press Enter To Continue\"")
            call("clear")

    def list_wallets(self):
        call("clear")
        print("\n\n\t* Welcome To The Command Line Interface Of The CryptoHub Blockchain Client *\n\n")
        print("*** YOU'RE LOGGED IN AS: {} | Client ID: {} ***\n\n".format(self.user.username, self.user.client_id))
        print("List of Wallets Owned By Client ID: \n\n")

        self.user.get_list_of_owned_wallets()
        input("\nPress Enter To Continue\n")
        call("clear")

    def change_wallet_password(self):

        """
        used to
        :return:
        """
        pass
