from Orses_User.User import User
from Orses_Wallet.WalletService_CLI_Helper import WalletServiceCLI
import json


if __name__ == '__main__':

    create = False
    createWallet = False

    if create is True:
        user1 = User(username="test2", password="7433xxxxxx", newUser=True)
    elif create is False:
        user1 = User(username="test2", password="7433xxxxxx").load_user()
    else:
        user1 =  User(username="test2", password="7433xxxxxx").import_user()

    # print(user1.pubkey)
    # print("\n\n-------")
    # print(user1.privkey)

    # create or load wallet
    if createWallet is True:
        print(user1.create_wallet("test2Wallet", "7433xxxxxx"))
    else:
        print("in OrsesCLITEST Wallet Loaded:  ", user1.load_wallet("test2Wallet", "7433xxxxxx"))

    print("user wallet: ", user1.wallet_service_instance.wallet_instance)
    # validate keys

    wlci = WalletServiceCLI(user=user1)
    print("11", wlci)
    print("in OrsesCLITest.py Keys are validated: ", wlci.validate_wallet_keys("7433xxxxxx"))


    # wlci.list_activities_of_wallet()

    # data1 = user1.wallet_service_instance.export_all_wallets()
    #
    # for i in data1:
    #     print(f"{i}: {data1[i]}")
    #     print()
    #
    #
    #
    #
    #
    # # check assignment statment
    # print(user1.create_sign_asgn_stmt(receiving_wid="wfe3", password_for_wallet="7433xxxxxx", amount=1, fee=0.01))
    #
    # trr = user1.make_wallet_bk_connected(amount=251000, fee=1, wallet_password="7433xxxxxx", time_limit=86400, veri_node_proxies=["wfefddfj", "wfjkdjdfkj"])
    # print(trr)
    #
    # trr_dict = json.loads(trr.decode())
    # print("----")
    # print(user1.make_wallet_not_bk_connected(wallet_password="7433xxxxxx", fee=1.0,
    #                                          tx_hash_of_trr=trr_dict["tx_hash"], veri_node_proxies=trr_dict, testing=True))
    #
    # print("\nTransfer Transaction: \n")
    # print(user1.create_transfer_transaction(receiving_wid="wfe34", password_for_wallet="7433xxxxxx", amount=150, fee=0.50))
    # user1.unload_wallet()



