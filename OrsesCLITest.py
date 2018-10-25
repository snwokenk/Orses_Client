from Orses_User.User import User
from Orses_Wallet.WalletService_CLI_Helper import WalletServiceCLI
from Orses_Util.FileAction import FileAction
import json, queue, time, os

from twisted.internet import reactor, threads


# used to test for newly created wallet with no tokens receiving tokens
# then sending misc messages

def call_when_running(callable_function, **kwargs):

    d = threads.deferToThread(callable_function, reactor, **kwargs)
    d.addCallback(lambda x: reactor.stop())
    d.addErrback(lambda x: print(x))


def test_one(reactor_inst=reactor, username="bb1", wallet_nickname="bb11"):
    """
    pass to call_when_running
    :return:
    """

    # load already created user
    password = "xxx"
    user2 = User(
        username=username,
        password=password
    ).load_user()


    # check if user is  none
    if user2 is None:
        print("create a user names 'autotest1' with password 'abcdefgh'\n"
              "then create a wallet name 'autowallet1' with password 'abcdefgh'")
        return

    # load already created wallet if user is not none
    user2.load_wallet(
        wallet_nickname=wallet_nickname,
        password=password
    )


    # create queue object

    q_obj = queue.Queue()

    # instantiate wallet service CLI  (Name should be changed soon)
    w2 = WalletServiceCLI(
        user=user2
    )

    admin_path = os.path.join(os.path.dirname(os.getcwd()), "Orses_Core","sandbox", "sn", "startup_file")
    data: dict = FileAction.open_file_from_json(admin_path)
    admin_id = data.get("admin_id")

    if admin_id:
        # verinode_proxies = input("Enter verinode proxies, separated by commas")
        # verinode_proxies = verinode_proxies.replace(" ", "")
        # verinode_proxies = verinode_proxies.split(",")
        verinode_proxies = [admin_id]
    else:
        print("no admin _id")
        return False

    w2.reserve_tokens_bk_connected_wallet(
        amount=251000.00,
        fee=1.00,
        time_limit=360.00,
        veri_node_proxies=verinode_proxies,
        q_obj=q_obj,
        wallet_password=password,
        reactor_instance=reactor_inst

    )

    try:
        resp = q_obj.get(timeout=10)

    except queue.Empty:
        print(f"Response timed out")
        return False

    if resp > 0:

        balance_validated = check_till_balance_confirmed(
            reactor_inst=reactor_inst,
            user=user2
        )
        if balance_validated:
            return True

    return False


def check_till_balance_confirmed(reactor_inst, user, timeout=300, new_tx_sent=False):
    # create queue object

    q_obj = queue.Queue()

    # instantiate wallet service CLI  (Name should be changed soon)
    w2 = WalletServiceCLI(
        user=user
    )

    print("checking for balance ")
    # **** validate balance: balance ****
    target_time = time.time() + timeout


    if new_tx_sent is True:
        print("Waiting for 1 minute before checking balance")
        time.sleep(60)
    while time.time() < target_time:
        w2.validate_balance_on_blockchain(
            q_obj=q_obj,
            reactor_instance=reactor_inst
        )

        try:
            balance = q_obj.get(timeout=10)

        except queue.Empty:
            print(f"Response timed out")
            return
        balance = json.loads(balance)

        print(f"this is balance {balance}")
        if not balance[1] and balance[0][-1] != 0:
            print(f"this is balance {balance}\n"
                  f"Orses token Balance is {[float(bal)/1e10 for bal in balance[0][:3] if bal]}\n"
                  f"Balance validated")
            return True
        else:
            print(f"this is balance {balance}\n"
                  f"Orses token Balance is {[float(bal)/1e10 for bal in  balance[0][:3]]}")
        time.sleep(20)

    return False


def first_test(reactor_inst, username="bb1", wallet_nickname="bb11"):

    """
    in first test send tokens to 2 wallets
    300,000 tokens to W0f869cdbc270f73f26a975a076def7c4553826e5
    500 tokens to W415eb032ce5cb7ec38a1c3e6597118f2cc52836e
    :param reactor_inst:
    :param username:
    :param wallet_nickname:
    :return:
    """


    print("running first test")
    # load already created user
    password = "xxx"  # should be wallet for both user and wallet
    user2 = User(
        username=username,
        password=password
    ).load_user()


    # check if user is  none
    if not user2:
        print(f"create a user with name {username} with password\n"
              f"then create a wallet name {wallet_nickname}")
        return
    # load already created wallet if user is not none

    user2.load_wallet(
        wallet_nickname=wallet_nickname,
        password=password
    )

    w2 = WalletServiceCLI(
        user=user2
    )

    check_till_balance_confirmed(
        reactor_inst=reactor_inst,
        user=user2
    )

    q_obj = queue.Queue()

    w2.transfer_tokens(
        amount=300000,
        fee=0.01,
        receiving_wid="W0f869cdbc270f73f26a975a076def7c4553826e5",  # autowallet1
        password_for_wallet=password,
        q_obj=q_obj,
        reactor_instance=reactor_inst
    )

    success = q_obj.get()
    print(success)

    if success > 0:
        print(f"successfully sent to first wallet")
    else:
        print(f"not successful action 1")
        return False

    w2.transfer_tokens(
        amount=500,
        fee=0.0001,
        receiving_wid="Wf482b228fe4eca8be53aa0e333ba24c7e8ae9670",  # bosoko1
        password_for_wallet=password,
        q_obj=q_obj,
        reactor_instance=reactor_inst
    )
    try:
        success = q_obj.get(timeout=10)
    except queue.Empty:
        print(f"Response timed out")
        return False

    if success > 0:
        print(f"successfully sent to second wallet")
        return True
    else:
        print(f"not successful action 2")
        return False


def second_test(reactor_inst, username="autotest1", wallet_nickname="autowallet1"):
    """
    Check for autotest1 balance, once included in the block, send a token reservation request,
    then check for balance until added
    :param reactor_inst:
    :param username:
    :param wallet_nickname:
    :return:
    """

    print("second test running")

    # load already created user
    password = "abcdefgh"
    user2 = User(
        username=username,
        password=password
    ).load_user()

    # check if user is  none
    if not user2:
        print(f"create a user with name {username} with password\n"
              f"then create a wallet name {wallet_nickname}")
        return
    # load already created wallet if user is not none

    user2.load_wallet(
        wallet_nickname=wallet_nickname,
        password=password
    )

    balance_validated = check_till_balance_confirmed(
        reactor_inst=reactor_inst,
        user=user2,
        new_tx_sent=True
    )

    if balance_validated:
        pass
    else:
        return False

    w2 = WalletServiceCLI(
        user=user2
    )

    q_obj = queue.Queue()
    admin_path = os.path.join(os.path.dirname(os.getcwd()), "Orses_Core","sandbox", "sn", "startup_file")
    data: dict = FileAction.open_file_from_json(admin_path)
    admin_id = data.get("admin_id")

    if admin_id:
        # verinode_proxies = input("Enter verinode proxies, separated by commas")
        # verinode_proxies = verinode_proxies.replace(" ", "")
        # verinode_proxies = verinode_proxies.split(",")
        verinode_proxies = [admin_id]
    else:
        print("no admin _id")
        return False

    w2.reserve_tokens_bk_connected_wallet(
        amount=251000.00,
        fee=1.00,
        time_limit=360.00,
        veri_node_proxies=verinode_proxies,
        q_obj=q_obj,
        wallet_password=password,
        reactor_instance=reactor_inst

    )

    try:
        resp = q_obj.get(timeout=10)

    except queue.Empty:
        print(f"Response timed out")
        return False

    if resp > 0:

        balance_validated = check_till_balance_confirmed(
            reactor_inst=reactor_inst,
            user=user2,
            new_tx_sent=True
        )
        if balance_validated:
            return True

    return False


def third_test(reactor_inst, username="bosoko1", wallet_nickname="wallet1"):
    """

    run test which sends tokens using an assignment statement
    sending wallet will be wallet sent 500 tokens
    :param reactor_inst:
    :param username:
    :param wallet_nickname:
    :return:
    """

    print("Third test running")
    # load already created user
    password = "xxx"
    user2 = User(
        username=username,
        password=password
    ).load_user()

    # check if user is  none
    if not user2:
        print(f"create a user with name {username} with password\n"
              f"then create a wallet name {wallet_nickname}")
        return
    # load already created wallet if user is not none

    user2.load_wallet(
        wallet_nickname=wallet_nickname,
        password=password
    )

    balance_validated = check_till_balance_confirmed(
        reactor_inst=reactor_inst,
        user=user2
    )

    if balance_validated:
        pass
    else:
        return False

    w2 = WalletServiceCLI(
        user=user2
    )

    q_obj = queue.Queue()

    w2.send_tokens(
        amount=25,
        fee=0.0001,
        password_for_wallet=password,
        receiving_wid="W71c7a921199d97c64dfe11bb71663d3078eccabb",  # auto2wallet
        q_obj=q_obj,
        reactor_instance=reactor
    )
    "41a92a7833096859454fe336b281a33dbfeb635e16c4c2507891341e260cdd45"
    rsp = q_obj.get(timeout=420)

    print(rsp)

    return True

def fourth_test(reactor_inst, username="autotest2", wallet_nickname="auto2wallet"):
    print("Fourth test running")
    # load already created user
    password = "sn"
    user2 = User(
        username=username,
        password=password
    ).load_user()

    # check if user is  none
    if not user2:
        print(f"create a user with name {username} with password\n"
              f"then create a wallet name {wallet_nickname}")
        return
    # load already created wallet if user is not none

    user2.load_wallet(
        wallet_nickname=wallet_nickname,
        password=password
    )

    balance_validated = check_till_balance_confirmed(
        reactor_inst=reactor_inst,
        user=user2
    )

    print(f"balance is Validated {balance_validated}")

def run_tests(reactor_inst):

    succ = first_test(
        reactor_inst=reactor
    )

    if succ:
        succ2 = second_test(
            reactor_inst=reactor
        )

        if succ2:
            succ3 = third_test(
                reactor_inst=reactor
            )

            if succ3:

                return True

    return False


if __name__ == '__main__':

    try:
        reactor.callWhenRunning(
            call_when_running,
            callable_function=fourth_test,


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



