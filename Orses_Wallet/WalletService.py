from Orses_Wallet import Wallet
from Orses_Util import Filenames_VariableNames, FileAction
from Orses_Cryptography.PKIGeneration import WalletPKI
from Orses_Message import AssignmentStatement, TransferTransaction, TokenReservationRequest, TokenReservationRevoke

# TODO: in associated_wallets create a w


class WalletServices:
    def __init__(self, client_id, user):
        self.user = user
        self.username = user.username
        self.password = user.password
        self.wallet_instance = None
        self.client_id = client_id
        self.associated_wallets = None
        self.__get_associated_wallets()

    def __get_associated_wallets(self):
        """
        used to get dictionary of wallet id's associated with Username.
        key is a nickname for each wallet, value is the wallet id
        if no wallet id, returns an empty dictionary
        :return: dict
        """

        filename = Filenames_VariableNames.username_wallets.format(self.username)
        folder_name = Filenames_VariableNames.wallet_details_folder
        username_wallets = FileAction.FileAction.open_file_from_json(filename=filename,
                                                                     in_folder=folder_name)
        if username_wallets:
            self.associated_wallets = username_wallets
        else:
            self.associated_wallets = {}

        print("in walletservice.py, _get_associated_wallets: ", self.associated_wallets)

    def get_associated_wallet_ids(self):
        return self.associated_wallets

    def update_associated_wallet_id_dict(self, wallet_nickname, wallet_id):
        self.associated_wallets[wallet_nickname] = wallet_id
        filename = Filenames_VariableNames.username_wallets.format(self.username)
        folder_name = Filenames_VariableNames.wallet_details_folder
        FileAction.FileAction.save_json_into_file(filename=filename,
                                                  python_json_serializable_object=self.associated_wallets,
                                                  in_folder=folder_name)

    def create_wallet(self, wallet_nickname, balance, client_id, locked_token, password):

        wl = WalletPKI(wallet_nickname=wallet_nickname, password=password)
        wl.generate_pub_priv_key(save_in_folder=Filenames_VariableNames.wallets_folder)

        self.wallet_instance = Wallet.Wallet(balance=balance, client_id=client_id, locked_token=locked_token,
                                             pubkey=wl.load_pub_key(importedKey=False, x_y_only=True,
                                                                    user_or_wallet="wallet"),
                                             wallet_nickname=wallet_nickname, wallet_pki=wl)

        self.update_associated_wallet_id_dict(wallet_nickname=wallet_nickname,
                                              wallet_id=self.wallet_instance.get_wallet_id())

        self.wallet_instance.save_wallet_details(password=password)

        self.associated_wallets[wallet_nickname] = self.wallet_instance.get_wallet_id()
        return True

    def load_a_wallet(self, wallet_nickname, password, get_wallet_details=False):
        """

        :param wallet_nickname:
        :param password:
        :param get_wallet_details: if this is true, only get the details of the wallet in a dictionary
        :return:
        """
        wl = WalletPKI(wallet_nickname=wallet_nickname, password=password)
        if wallet_nickname in self.associated_wallets:
            wallet_id = self.associated_wallets[wallet_nickname]
            self.wallet_instance = Wallet.Wallet.load_wallet_details(
                wallet_id=wallet_id,
                password=password,
                wallet_nickname=wallet_nickname,
                walletpki=wl,
                get_wallet_details=get_wallet_details
            )

            if get_wallet_details is True:
                pass

            return True if self.wallet_instance else False
        else:
            return None

    def export_all_wallets(self):
        """
        this will get all associated wallet datas (in its encrypted formats for inclusion in export file of user)

        example of returned dict:
        ---

        # this key will always be present
        "associated_wallets": {'test1Wallet': 'W25cb9cebc3f968d43bf6f11b0c1868fdd64dc558'}  # can have more or {}

        # wallet id as key and encrypted list containing wallet details as value
        "W25cb9cebc3f968d43bf6f11b0c1868fdd64dc558":
        ['hex value of encrypted wallet details ', 'hex of tag', 'hex of nonce', 'hex of salt']

        # key for privkey, also == to filename
        "test1Wallet_wallet_encrypted_key":
        ['hex value of encrypted private key( "d" variable of ECDSA key) ', 'hex of tag', 'hex of nonce', 'hex of salt']

        # key for public key (pubkey also stored in wallet details. Value is dict containg "x" and  "y" ints for ECDSA
        "test1Wallet_wallet_pubkey":
        {'x': 'G#pAsy|5{uPtth_M_j|n*a90nFlP83`c(R1i9DK!', 'y': 'umWMsZz3P}{LWmc#pPY=$w~y4?g~XU8(aluUaILP'}

        -----

        if more than 1 wallet then more entries will be in following this pattern

        :return:
        """
        wallet_detail = dict()
        wallet_detail["associated_wallets"] = self.associated_wallets

        if self.associated_wallets:
            for i in self.associated_wallets:
                wallet_detail[self.associated_wallets[i]] = FileAction.FileAction.open_file_from_json(
                    filename=self.associated_wallets[i],
                    in_folder=Filenames_VariableNames.wallet_details_folder
                )
                w_pki = WalletPKI(i, None)  # since no decryption is taking place password is none
                wallet_detail[w_pki.privkey_file] = w_pki.load_priv_key(encrypted=True, user_or_wallet="wallet")
                wallet_detail[w_pki.pubkey_file] = w_pki.load_pub_key(x_y_only=True, user_or_wallet="wallet")

        return wallet_detail

    def import_all_wallets(self, wallet_details_dict):

        # set associated wallets and create file

        username_wallets = FileAction.FileAction.save_json_into_file(
            filename=Filenames_VariableNames.username_wallets.format(self.username),
            python_json_serializable_object=wallet_details_dict["associated_wallets"],
            in_folder=Filenames_VariableNames.wallet_details_folder
        )
        self.associated_wallets = wallet_details_dict["associated_wallets"]

        # save each wallets encrypted data, privkey and pubkey in file
        if self.associated_wallets:
            for i in self.associated_wallets:
                FileAction.FileAction.save_json_into_file(
                    filename=self.associated_wallets[i],
                    python_json_serializable_object=wallet_details_dict[self.associated_wallets[i]],
                    in_folder=Filenames_VariableNames.wallet_details_folder
                )
                w_pki = WalletPKI(i, None)  # since no decryption is taking place password is none
                w_pki.save_imported_privkey(wallet_details_dict[w_pki.privkey_file])
                w_pki.save_imported_pubkey(wallet_details_dict[w_pki.pubkey_file])

        return True

    def unload_wallet(self, save=False, password=None):
        if save:
            assert password is not None, "'password' parameter must not be None if 'save' parameter is True"
            if isinstance(self.wallet_instance, Wallet.Wallet):
                self.wallet_instance.save_wallet_details(password=password)

        self.wallet_instance = None

    def update_save_wallet_details(self, password):

        self.wallet_instance.save_wallet_details(password=password, username=self.username)

    def return_wallet_details(self):

        if isinstance(self.wallet_instance, Wallet.Wallet):
            return self.wallet_instance.get_wallet_details()
        else:
            return {}

    def get_privkey_of_wallet(self, password, imported_key=True):

        if isinstance(self.wallet_instance, Wallet.Wallet):
            return WalletPKI(wallet_nickname=self.wallet_instance.get_wallet_nickname(),
                             password=password).load_priv_key(importedKey=imported_key, user_or_wallet="wallet")
        else:
            return b''

    def validate_balances(self):
        pass

    def assign_tokens(self, receiving_wid, bk_connected_wid, amount_of_tokens, fee, password_for_wallet):
        asgn_stmt_object = AssignmentStatement.AssignmentStatement(
            sending_wid=self.wallet_instance.get_wallet_id(),
            receiving_wid=receiving_wid,
            bk_connected_wid=bk_connected_wid,
            amount_of_tokens=amount_of_tokens,
            fee=fee
        )

        assignment_statement = asgn_stmt_object.sign_and_return_conditional_assignment_statement(
            wallet_privkey=self.get_privkey_of_wallet(password=password_for_wallet)
        )

        if assignment_statement:

            # assignment_statement["wallet_id"] = self.wallet_instance.get_wallet_id()
            assignment_statement["client_id"] = self.client_id

            return assignment_statement
        else:
            return {}

    def transfer_tokens(self, receiving_wid, amount, fee, password_for_wallet):
        transfer_tx_obj = TransferTransaction.TokenTransferTransaction(
            sending_wid=self.wallet_instance.get_wallet_id(),
            receiving_wid=receiving_wid,
            amount_of_tokens=amount,
            fee=fee

        )

        transfer_transaction = transfer_tx_obj.sign_and_return_transfer_transaction(
            wallet_privkey=self.get_privkey_of_wallet(password=password_for_wallet)
        )

        if transfer_transaction:

            transfer_transaction["client_id"] = self.client_id

            return transfer_transaction

        else:  # returns empty dictionary because wallet privkey was not decrypted with right password
            return {}

    def become_bk_connected_wallet(self, amount, fee, wallet_password, time_limit, veri_node_proxies):
        tkn_req_obj = TokenReservationRequest.TokenReservationRequest(
            requesting_wid=self.wallet_instance.get_wallet_id(),
            time_limit=time_limit,
            tokens_to_reserve=amount,
            fee=fee

        )
        token_reservation_request = tkn_req_obj.sign_and_return_reservation_request(
            wallet_privkey=self.get_privkey_of_wallet(password=wallet_password),
            veri_node_proxies=veri_node_proxies
            # veri_node_proxies=["ID-fe1234abcd", "ID-ab1d3F457"]
        )

        if token_reservation_request:
            token_reservation_request["client_id"] = self.client_id

            return token_reservation_request

        else:
            return {}

    def become_not_bk_connected(self, tx_hash_trr, wallet_password, fee, veri_node_proxies):

        tkn_rvk_obj = TokenReservationRevoke.TokenReservationRevoke(
            requesting_wid=self.wallet_instance.get_wallet_id(),
            fee=fee,
            tx_hash_trr=tx_hash_trr

        )

        token_revoke_request = tkn_rvk_obj.sign_and_return_revoke_request(
            wallet_privkey=self.get_privkey_of_wallet(password=wallet_password),
            veri_node_proxies=veri_node_proxies
        )
        if token_revoke_request:
            token_revoke_request["client_id"] = self.client_id
            return token_revoke_request
        else:
            return {}

    def verify_balance_on_blockchain(self, wallet_id):
        pass

