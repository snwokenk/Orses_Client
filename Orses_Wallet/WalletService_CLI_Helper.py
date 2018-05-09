
# cryptohub
from Orses_User.User import User
from Orses_Wallet.Wallet import Wallet
from Orses_Wallet.WalletService import WalletServices
from  Orses_Network.NetworkManager import NetworkManager
from Orses_Cryptography.DigitalSigner import DigitalSigner
from Orses_Cryptography.DigitalSignerValidator import DigitalSignerValidator

import queue


class WalletServiceCLI:
    def __init__(self, user):
        self.user = user
        self.nm = NetworkManager(user=user) if user else None
        self.dict_of_active = dict()
        self.dict_of_inactive = dict()

        # assert isinstance(self.user, User), "not a user class"
        # assert isinstance(self.user.wallet_service_instance, WalletServices), "WalletService Instance Not Loaded"
        # assert isinstance(self.user.wallet_service_instance.wallet_instance, Wallet), "wallet not loaded into user"

    def set_user_instantiate_net_mgr(self, user):

        if user:
            self.user = user
            self.nm = NetworkManager(user=user)

    def get_active_peers(self):
        if self.nm:
            self.nm.get_active_peers()

    def send_tokens(self, amount, fee, receiving_wid, password_for_wallet, q_obj, reactor_instance=None):

        assert (amount > 0 and fee > 0), "Amount of Tokens To Send MUST Not Be Negative"
        # returns a statement if all is ok, else False for wrong password, none for stmts not passing validator test
        print("this is statement before")
        stmt = self.user.create_sign_asgn_stmt(amount=amount, receiving_wid=receiving_wid, fee=fee,
                                               password_for_wallet=password_for_wallet, )

        print("this is statement after", stmt)
        if stmt:
            # nm = NetworkManager(user=self.user)

            print("statement is true")

            reactor_instance.callFromThread(
                self.nm.send_assignment_statement,
                asgn_stmt=stmt,
                wallet_pubkey=self.user.wallet_service_instance.wallet_instance.get_wallet_pub_key().hex(),
                reactor_instance=reactor_instance,
                q_object_from_walletcli=q_obj
            )

        else:
            q_obj.put(-1.0)
        print('----')
        print(stmt)
        print("----")

    def transfer_tokens(self, amount, receiving_wid, fee, password_for_wallet, q_obj, reactor_instance=None):

        assert (amount > 0 and fee > 0), "Amount of Tokens To Send MUST Not Be Negative"
        ttx = self.user.create_transfer_transaction(receiving_wid=receiving_wid, amount=amount, fee=fee,
                                                    password_for_wallet=password_for_wallet)

        if ttx:

            reactor_instance.callFromThread(
                self.nm.send_transfer_transaction,
                transfer_tx=ttx,
                reactor_instance=reactor_instance,
                wallet_pubkey=self.user.wallet_service_instance.wallet_instance.get_wallet_pub_key().hex(),
                q_object_from_walletcli=q_obj
            )

        else:

            q_obj.put(-1.0)

        # sends statement, or False for wrong password
        print('----')
        print(ttx)
        print("----")

    def reserve_tokens_bk_connected_wallet(self, amount, fee, wallet_password, veri_node_proxies, q_obj, time_limit,
                                           reactor_instance=None):
        assert (amount > 0 and fee > 0), "Amount of Tokens To Send MUST Not Be Negative"

        trr = self.user.make_wallet_bk_connected(amount=amount, fee=fee, wallet_password=wallet_password,
                                                 time_limit=time_limit, veri_node_proxies=veri_node_proxies)

        if trr:

            reactor_instance.callFromThread(
                self.nm.send_token_reservation_request,
                tkn_rsv_req=trr,
                reactor_instance=reactor_instance,
                wallet_pubkey=self.user.wallet_service_instance.wallet_instance.get_wallet_pub_key().hex(),
                q_object_from_walletcli=q_obj
            )

        else:

            q_obj.put(-1.0)

        # sends statement, or False for wrong password
        print('----')
        print(trr)
        print("----")


    def revoke_reserved_tokens_bk_connected_wallet(self, trr_hash, fee, wallet_password, veri_node_proxies, q, q_obj,
                                                   reactor_instance=None):

        trx = self.user.make_wallet_not_bk_connected(tx_hash_of_trr=trr_hash, fee=fee,
                                                     wallet_password=wallet_password,
                                                     veri_node_proxies=veri_node_proxies)
        if trx:
            reactor_instance.callFromThread(
                self.nm.send_token_revoke_request,
                tkn_rvk_req=trx,
                wallet_pubkey=self.user.wallet_service_instance.wallet_instance.get_wallet_pub_key().hex(),
                reactor_instance=reactor_instance,
                q_object_from_walletcli=q_obj

            )
        print('----')
        print(trx)
        print("----")
        q.put(trx)



    def validate_wallet_keys(self, password_for_wallet):

        pubkey = self.user.wallet_service_instance.wallet_instance.get_wallet_pub_key()
        wallet_privkey = self.user.wallet_service_instance.get_privkey_of_wallet(password=password_for_wallet)
        if not wallet_privkey:
            return None
        msg = b'test'

        signature = DigitalSigner.wallet_sign(wallet_privkey=wallet_privkey, message=msg)

        # returns True if validated and False if not
        return DigitalSignerValidator.validate_wallet_signature(msg=msg, wallet_pubkey=pubkey, signature=signature)

    def list_activities_of_wallet(self):
        dict_of_activities = self.user.wallet_service_instance.wallet_instance.get_activities()

        print("Last Hash State of Wallet: ",
              self.user.wallet_service_instance.wallet_instance.get_last_saved_hash_state())

        for i in dict_of_activities:
            print("\n-----\n")
            print(i, ": ", dict_of_activities[i])
            print("\n-----\n")

    def check_pending_tokens_on_blockchain(self):
        pass

    def validate_balance_on_blockchain(self):
        pass

    def automatic_network_refresh(self, q_object, q_for_active,reactor_instance):
        """
        used to refresh network, check available peers, if only default address available, will ask from known peers.
        If this doesn't autatically work, then users must used
        :return: bool, if successful
        """
        # Todo: check if addr list is default, if it is check active addresses on default list
        # Todo: send a request for addresses message to active nodes on default list
        # Todo: using the addr dictionary returned check for active addr, create a dcit of active peers and inactive
        # Todo: create a user specific addr list using the dict of active peers
        # Todo: poll inactive list randomly and up to 3 times to see if active, after delete from list
        # Todo: any time log in to user, check for online peers or nodes from active list

        if self.nm.net_addr_mgr.is_default:
            self.nm.check_active_peers(reactor_instance=reactor_instance, q_object=q_for_active)
            self.nm.request_address_update(reactor_instance=reactor_instance)
        else:
            q_for_active.put([])

            # if true, then using default address list, request for updated address list

    def check_active_peers(self, reactor_instance):

        if self.nm:
            self.nm.check_active_peers(reactor_instance=reactor_instance, WSCLI=self)

    def manual_network_address_update(self, address_list):
        """
        will take address list from user input, verify they are connected and then update username address list
        :param address_list: list of address [[ip address, port], [ip address, port]]
        :return: True, if at least 1 of address in list responds.
        """

