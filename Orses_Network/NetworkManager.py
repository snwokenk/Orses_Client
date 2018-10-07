# from twisted.internet import reactor
from Orses_Network_Messages.SpokenMessages import NetworkMessages
from Orses_Network.NetworkSpeaker import NetworkSpeakerFactory
from Orses_Network.NetworkAuditor import NetworkAuditorFactory
from Orses_Network.NetworkAddressManager import NetworkAddressManager
import time, queue



class NetworkManager:
    def __init__(self, user):
        """
        :param user: instance of current user
        """
        self.user = user
        self.net_addr_mgr = NetworkAddressManager(username=user.username) if user else None
        # assert isinstance(self.user, User), "not a user class"
        # assert isinstance(self.user.wallet_service_instance, WalletServices), "WalletService Instance Not Loaded"
        # assert isinstance(self.user.wallet_service_instance.wallet_instance, Wallet), "wallet not loaded into user"

    def set_user_instantiate_net_addr_mgr(self, user):
        if user:
            self.user = user
            self.net_addr_mgr = NetworkAddressManager(username=user.username)

    def get_active_peers(self):

        if self.net_addr_mgr:
            return self.net_addr_mgr.get_active_peers()

    def request_balance_from_from_network(self, wallet_id, reactor_instance, q_object_from_walletcli):

        # todo: add to walletcli
        spkn_msg_obj_creator_callable = NetworkMessages.message_to_be_spoken_creator(main_msg=wallet_id,
                                                                                     wallet_pubkey=None,
                                                                                     reason_msg=b'rq_bal')
        addresses = self.net_addr_mgr.get_active_peers()  # returns list of address list [["ip address", port], ]

        factory = NetworkSpeakerFactory(spkn_msg_obj_creator=spkn_msg_obj_creator_callable,
                                        queue_obj=q_object_from_walletcli, exp_conn=1, is_expecting_data=True)

        if addresses:  # if any addresses not empty
            for i in addresses:
                reactor_instance.connectTCP(host=i, port=addresses[i], factory=factory)
        elif q_object_from_walletcli:  # if addresses empty send 0.00 as success rate, if this is not done, queue object waits forever
            q_object_from_walletcli.put(0.00)

    def send_assignment_statement(self, asgn_stmt, wallet_pubkey,reactor_instance, q_object_from_walletcli):

        # Todo: for all update local balance only if 50% or more connections return "ver" message

        # returns a message to be spoken callable, when called returns a SpokenMessages instance
        spkn_msg_obj_creator_callable = NetworkMessages.message_to_be_spoken_creator(main_msg=asgn_stmt,
                                                                                     wallet_pubkey=wallet_pubkey,
                                                                                     reason_msg=b'tx_asg')

        addresses = self.net_addr_mgr.get_active_peers()  # returns list of address list [["ip address", port], ]

        factory = NetworkSpeakerFactory(spkn_msg_obj_creator=spkn_msg_obj_creator_callable,
                                        queue_obj=q_object_from_walletcli, exp_conn=1)

        if addresses:  # if any addresses not empty
            for i in addresses:
                reactor_instance.connectTCP(host=i, port=addresses[i], factory=factory)
        elif q_object_from_walletcli:  # if addresses empty send 0.00 as success rate, if this is not done, queue object waits forever
            q_object_from_walletcli.put(0.00)


        # reactor_instance.connectTCP(host="127.0.0.1", port=55600, factory=factory)

    def send_misc_messages(self, misc_message, wallet_pubkey, reactor_instance, q_object_from_walletcli):
        spkn_msg_obj_creator_callable = NetworkMessages.message_to_be_spoken_creator(main_msg=misc_message,
                                                                                     wallet_pubkey=wallet_pubkey,
                                                                                     reason_msg=b'misc_msg')

        addresses = self.net_addr_mgr.get_active_peers()  # returns list of address list [["ip address", port], ]

        factory = NetworkSpeakerFactory(spkn_msg_obj_creator=spkn_msg_obj_creator_callable,
                                        queue_obj=q_object_from_walletcli, exp_conn=1)  # exp_conn is len(addresses)

        if addresses:  # if any addresses not empty
            for i in addresses:
                reactor_instance.connectTCP(host=i, port=addresses[i], factory=factory)
        else:  # if addresses empty send 0.00 as success rate, if this is not done, queue object waits forever
            q_object_from_walletcli.put(0.00)

    def send_transfer_transaction(self, transfer_tx, wallet_pubkey, reactor_instance, q_object_from_walletcli):
        # Todo: for all update local balance only if 50% or more connections return "ver" message

        spkn_msg_obj_creator_callable = NetworkMessages.message_to_be_spoken_creator(main_msg=transfer_tx,
                                                                                     wallet_pubkey=wallet_pubkey,
                                                                                     reason_msg=b'tx_ttx')

        addresses = self.net_addr_mgr.get_active_peers()  # returns list of address list [["ip address", port], ]

        factory = NetworkSpeakerFactory(spkn_msg_obj_creator=spkn_msg_obj_creator_callable,
                                        queue_obj=q_object_from_walletcli, exp_conn=1)  # exp_conn is len(addresses)

        if addresses:  # if any addresses not empty
            for i in addresses:
                reactor_instance.connectTCP(host=i, port=addresses[i], factory=factory)
        else:  # if addresses empty send 0.00 as success rate, if this is not done, queue object waits forever
            q_object_from_walletcli.put(0.00)

    def send_token_reservation_request(self, tkn_rsv_req, wallet_pubkey, reactor_instance, q_object_from_walletcli):
        # Todo: for all update local balance only if 50% or more connections return "ver" message

        spkn_msg_obj_creator_callable = NetworkMessages.message_to_be_spoken_creator(main_msg=tkn_rsv_req,
                                                                                     wallet_pubkey=wallet_pubkey,
                                                                                     reason_msg=b'tx_trr')

        addresses = self.net_addr_mgr.get_active_peers()  # returns list of address list [["ip address", port], ]
        factory = NetworkSpeakerFactory(spkn_msg_obj_creator=spkn_msg_obj_creator_callable,
                                        queue_obj=q_object_from_walletcli, exp_conn=1)
        if addresses:  # if any addresses not empty
            for i in addresses:
                reactor_instance.connectTCP(host=i, port=addresses[i], factory=factory)
        else:  # if addresses empty send 0.00 as success rate, if this is not done, queue object waits forever
            q_object_from_walletcli.put(0.00)

    def send_token_revoke_request(self, tkn_rvk_req, wallet_pubkey, reactor_instance, q_object_from_walletcli):
        # Todo: for all update local balance only if 50% or more connections return "ver" message

        spkn_msg_obj_creator_callable = NetworkMessages.message_to_be_spoken_creator(main_msg=tkn_rvk_req,
                                                                                     wallet_pubkey=wallet_pubkey,
                                                                                     reason_msg=b'tx_trx')

        addresses = self.net_addr_mgr.get_active_peers()  # returns list of address list [["ip address", port], ]
        factory = NetworkSpeakerFactory(spkn_msg_obj_creator=spkn_msg_obj_creator_callable,
                                        queue_obj=q_object_from_walletcli, exp_conn=1)
        if addresses:  # if any addresses not empty
            for i in addresses:
                reactor_instance.connectTCP(host=i, port=addresses[i], factory=factory)
        else:  # if addresses empty send 0.00 as success rate, if this is not done, queue object waits forever
            q_object_from_walletcli.put(0.00)

    def check_active_peers(self, reactor_instance, WSCLI):
        """
        used to connect to addresses from list and check which are currently online

        :return:
        """
        addresses = self.net_addr_mgr.get_active_peers()

        factory = NetworkAuditorFactory(conn_type="check_active", exp_conn=len(addresses), WSCLI=WSCLI)

        for i in addresses:
            reactor_instance.connectTCP(host=i, port=addresses[i], factory=factory)

    def request_address_update(self, q_object_from_walletcli, reactor_instance):
        main_msg = b'adr'
        spkn_msg_obj_creator_callable = NetworkMessages.message_to_be_spoken_creator(main_msg=main_msg,
                                                                                     wallet_pubkey='0',
                                                                                     reason_msg=b'rq_adr')

        addresses = self.net_addr_mgr.get_active_peers()  # returns list of address list [["ip address", port], ]

        factory = NetworkSpeakerFactory(spkn_msg_obj_creator=spkn_msg_obj_creator_callable,
                                        queue_obj=q_object_from_walletcli, exp_conn=len(addresses))

        for i in addresses:
            reactor_instance.connectTCP(host=i, port=addresses[i], factory=factory)


