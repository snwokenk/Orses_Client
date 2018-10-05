from Orses_User.User import User
from Orses_Wallet.WalletService_CLI_Helper import WalletServiceCLI
import json, queue

from twisted.internet import reactor, threads


# used to test for newly created wallet with no tokens receiving tokens
# then sending misc messages

def call_when_running(callable_function, **kwargs):

    d = threads.deferToThread(callable_function, reactor, **kwargs)
    d.addCallback(lambda x: reactor.stop())
    d.addErrback(lambda x: print(x))


def test_one(reactor_inst, ):
    """
    pass to call_when_running
    :return:
    """

    # load already created user

    user2 = User(
        username="autotest1",
        password="abcdefgh"
    ).load_user()

    # check if user is  none
    if user2 is None:
        print("create a user names 'autotest1' with password 'abcdefgh'\n"
              "then create a wallet name 'autowallet1' with password 'abcdefgh'")
        return

    # load already created wallet if user is not none
    user2.load_wallet(
        wallet_nickname='autowallet1',
        password='abcdefgh'
    )

    # create queue object

    q_obj = queue.Queue()

    # instantiate wallet service CLI  (Name should be changed soon)
    w2 = WalletServiceCLI(
        user=user2
    )

    print("checking balance")
    # validate balance: balance
    w2.validate_balance_on_blockchain(
        q_obj=q_obj,
        reactor_instance=reactor_inst
    )

    # wait for response

    try:
        balance = q_obj.get(timeout=7)

    except queue.Empty:
        print(f"Response timed out")
        return

    print(f"Balance of autowallet1 {balance}")

    input("Send some tokens to this wallet using another wallet with tokens on the blockchain\n"
          " wait for it to be included in blockchain then validate balance again")


    print("checking for balance again")
    # validate balance: balance
    w2.validate_balance_on_blockchain(
        q_obj=q_obj,
        reactor_instance=reactor_inst
    )

    try:
        balance = q_obj.get(timeout=10)

    except queue.Empty:
        print(f"Response timed out")
        return

    print(balance)

    return



def main():
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


if __name__ == '__main__':

    try:
        reactor.callWhenRunning(
            call_when_running,
            callable_function=test_one,
        )

        reactor.run()
    except KeyboardInterrupt:

        reactor.stop()
        print("Keyboard interrupted")


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



