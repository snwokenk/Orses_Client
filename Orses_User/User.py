from Orses_Cryptography.PKIGeneration import PKI
from Orses_Util.Filenames_VariableNames import users_folder
from Orses_Util.FileAction import FileAction
from Orses_Wallet.WalletService import WalletServices
from Orses_Wallet.Wallet import Wallet
from Orses_Database.CreateDatabase import CreateDatabase
from Orses_Database.StoreData import StoreData
from Orses_Database.RetrieveData import RetrieveData
from Orses_Util.FileAction import FileAction
from Orses_Util import Filenames_VariableNames
from Orses_Network_Messages.Assgn_Stmt_Msg_Class import AssignmentStatementValidator
from Orses_Network_Messages.Transfer_Tx_Msg_Class import TransferTransactionValidator
from Orses_Network_Messages.Tkn_Rsv_Req_Msg_Class import TokenReservationRequestValidator
from Orses_Network_Messages.Tkn_Rvk_Req_Msg_Class import TokenRevokeRequestValidator


from Crypto.Hash import SHA256, RIPEMD160
import time, os, pathlib, json


class User:
    def __init__(self, username, password, newUser=False):
        """
        class representing the user.
        This class should allow for a user to:

        -Send token either using Assignment Statement or Token Transfer using wallet
        -receive token either through Assignment statement or Token Transfer and be able to verify confirmation
        -verify wallet balance on the blockchain

        :param username: string, keys and user details are stored under username
        :param password: password used to encrypt private keys and/or details
        :param newUser: bool, true if new user, false if not
        """
        self.username = username
        self.password = password
        self.client_id = None
        self.creation_time = None
        self.pubkey = None
        self.privkey = None
        self.pki = None
        self.newUser = newUser
        self.isNewUser = newUser

        self.__set_or_create_pki_pair()
        self.wallet_service_instance = WalletServices(client_id=self.client_id, user=self) if\
            self.client_id is not None else None
        self.associated_wallets = self.wallet_service_instance.get_associated_wallet_ids() if \
            self.wallet_service_instance is not None else None


    def __set_or_create_pki_pair(self):
        """
        sets or, if not already created, creates public private key pair for username on local machine.
        :return: none
        """

        # create an instance of PKI class (uses RSA 3072)
        pki = PKI(username=self.username, password=self.password)

        # try to load pub key, it should return false if new user, if it returns pubkey then user already created
        rsp = pki.load_pub_key()

        if rsp and self.newUser is True:
            self.isNewUser = False
            return

        elif self.newUser is True:
            pki.generate_pub_priv_key(save_in_folder=users_folder, overwrite=False)

            # set self.pki
            self.pki = pki

            # load public key, loaded as bytes and not key object
            self.pubkey = pki.load_pub_key(importedKey=False)

            # load private key, loaded as key object ready to be used for signing or encrypting
            self.privkey = pki.load_priv_key()

            # set client ID
            self.client_id = self.__create_client_id()

            # if the a new user then creation time is now and new databases are created with initial info stored

            self.creation_time = int(time.time())
            CreateDatabase().create_user_db(self.username)
            self.save_user()

        elif self.isNewUser is False:
            pass

    def __create_client_id(self):

        step1 = SHA256.new(self.pubkey).digest()
        return "ID-" + RIPEMD160.new(step1).hexdigest()

    def save_user(self):
        StoreData.store_user_info_in_db(
            client_id=self.client_id,
            pubkey=json.dumps(self.pki.load_pub_key(x_y_only=True)),
            username=self.username,
            timestamp_of_creation=self.creation_time
        )

    def load_user(self):
        user_data = RetrieveData.get_user_info(self.username)

        pki = PKI(username=self.username, password=self.password)
        if user_data:
            self.client_id = user_data[0]
            self.creation_time = user_data[1]
            self.pubkey = pki.load_pub_key(importedKey=False)
            self.privkey = pki.load_priv_key(importedKey=True)
            self.pki = pki
            self.wallet_service_instance = WalletServices(client_id=self.client_id, user=self)
            self.associated_wallets = self.wallet_service_instance.get_associated_wallet_ids()

        else:  # no user info, user not created
            return None

        if self.privkey:  # everything is well
            # creates user info database and wallet info database
            CreateDatabase()
            return self
        else: # wrong password
            return False

    def export_user(self):
        """
        used to export user into a file, which can then be taken anywhere else
        :return:
        """

        # pki = PKI(username=self.username, password=self.password)
        exp_path = os.path.join(pathlib.Path.home(), "Desktop", "CryptoHub_External_Files", "Exported_Accounts",
                                self.username + ".orses")

        FileAction.create_folder("Exported_Accounts")

        user_info_dict = dict()
        user_info_dict["username"] = self.username
        user_info_dict["client_id"] = self.client_id
        user_info_dict["creation_time"] = self.creation_time
        user_info_dict["pubkey_dict"] = self.pki.load_pub_key(x_y_only=True)
        user_info_dict["encrypted_private_key"] = self.pki.load_priv_key(importedKey=False, encrypted=True)
        user_info_dict["wallet_info"] = self.wallet_service_instance.export_all_wallets()

        with open(exp_path, "w") as outfile:
            json.dump(user_info_dict, outfile)

        return True

    def import_user(self, different_username=None):
        """
        used to import using username and password

        first checks to make sure no user by the same

        -if no file found with username on Imported_Accounts folder  returns none

        -if username found but password is wrong, returns False

        -if user found and everything okay returns self (or instance of user class)
        :return: None, False or self (instance of user).
        """

        imp_path = os.path.join(pathlib.Path.home(), "Desktop", "CryptoHub_External_Files", "Imported_Accounts",
                                self.username + ".orses")



        try:
            with open(imp_path, "r") as infile:
                user_data = json.load(infile)
        except FileNotFoundError:
            return None


        # get privkey name for user to see if any file exist
        priv_filename = Filenames_VariableNames.priv_key_filename.format(self.username)
        rsp = FileAction.open_file_from_json(filename=priv_filename, in_folder=Filenames_VariableNames.users_folder)

        if rsp:
            if different_username is None:
                # this will raise an exception if user already exists
                raise Exception("User With Username '{}' Already Exists".format(self.username))

        # if different username is specified, then user will be saved under that name
        if different_username:
            self.username = different_username
            priv_filename = Filenames_VariableNames.priv_key_filename.format(self.username)

        # instantiate a pki class
        pki = PKI(username=self.username, password=self.password)

        # save pubkey  to file and set self.pubkey, pubkey saved as python dict {"x": base85 str, "y": base85 str}
        # self.pubkey is set to bytes format
        pub_filename = Filenames_VariableNames.pub_key_filename.format(self.username)
        FileAction.save_json_into_file(pub_filename, python_json_serializable_object=user_data["pubkey_dict"],
                                       in_folder=Filenames_VariableNames.users_folder)
        self.pubkey = pki.load_pub_key(importedKey=False)

        # save and load privkey
        FileAction.save_json_into_file(priv_filename,
                                       python_json_serializable_object=user_data["encrypted_private_key"],
                                       in_folder=Filenames_VariableNames.users_folder)

        self.privkey = pki.load_priv_key(importedKey=True)

        # if priv key is false
        if not self.privkey:
            FileAction.delete_file(filename=priv_filename, in_folder=Filenames_VariableNames.users_folder)
            return False



        # set self.pki
        self.pki = pki

        # set client id
        self.client_id = user_data["client_id"]

        # set creation time
        self.creation_time = user_data["creation_time"]

        # create wallet instance
        self.wallet_service_instance = WalletServices(client_id=self.client_id, user=self)
        self.wallet_service_instance.import_all_wallets(wallet_details_dict=user_data["wallet_info"])
        self.associated_wallets = self.wallet_service_instance.get_associated_wallet_ids()

        # create database and save (will also create general client id and wallet id info database)
        CreateDatabase().create_user_db(self.username)
        self.save_user()

        return self



    # Wallets

    def create_wallet(self, wallet_nickname, wallet_password):
        """
        used to create a new wallet under a wallet nickname and password.
        if nickname already exist, will not create wallet
        :param wallet_nickname: string,
        :param wallet_password: string
        :return: dict, details of newly created wallet or blank dict if nickname already used on local machine
        """

        if wallet_nickname not in self.associated_wallets:
            is_created = self.wallet_service_instance.create_wallet(wallet_nickname=wallet_nickname, balance=50000000.0,
                                                                    client_id=self.client_id, locked_token=0.0,
                                                                    password=wallet_password)

            if is_created:
                wallet_data = self.wallet_service_instance.wallet_instance.get_wallet_details()
                wallet_data = wallet_data["details"]

                StoreData.store_wallet_info_in_db(wallet_id=wallet_data["wallet_id"],
                                                  wallet_owner=wallet_data["wallet_owner"],
                                                  wallet_pubkey=wallet_data["wallet_pubkey"],
                                                  wallet_nickname=wallet_data["wallet_nickname"],
                                                  timestamp_of_creation=wallet_data["timestamp_of_creation"],
                                                  wallet_locked_balance=wallet_data["locked_token_balance"],
                                                  wallet_balance=wallet_data["balance"],
                                                  username=self.username)

                return True

        return None

    def get_list_of_owned_wallets(self):
        list_of_wallets = self.associated_wallets

        if list_of_wallets:
            for i in list_of_wallets:
                print("\nWallet Nickname: '{}' | Wallet ID: '{}'\n".format(i, list_of_wallets[i]))
            return list_of_wallets

    def load_wallet(self, wallet_nickname, password):
        is_loaded =self.wallet_service_instance.load_a_wallet(wallet_nickname=wallet_nickname, password=password)
        if is_loaded is True:
            return True
        elif is_loaded is False:
            return False
        else:
            return None

    def unload_wallet(self, will_save=False, password=None):
        if self.wallet_service_instance:
            wallet_data = self.wallet_service_instance.wallet_instance.get_wallet_details()
            wallet_data = wallet_data["details"]

            StoreData.store_wallet_info_in_db(wallet_id=wallet_data["wallet_id"],
                                              wallet_owner=wallet_data["wallet_owner"],
                                              wallet_pubkey=wallet_data["wallet_pubkey"],
                                              wallet_nickname=wallet_data["wallet_nickname"],
                                              timestamp_of_creation=wallet_data["timestamp_of_creation"],
                                              wallet_locked_balance=wallet_data["locked_token_balance"],
                                              wallet_balance=wallet_data["balance"],
                                              username=self.username)
            self.wallet_service_instance.unload_wallet(save=will_save, password=password)

    def check_balance_of_loaded_wallet(self):

        if isinstance(self.wallet_service_instance.wallet_instance, Wallet):
            return self.wallet_service_instance.wallet_instance.get_balance()
        else:
            return "No Wallet Loaded"

    def get_wallet_id_of_loaded_wallet(self):

        if isinstance(self.wallet_service_instance.wallet_instance, Wallet):
            return self.wallet_service_instance.wallet_instance.get_wallet_id()
        else:
            return "No Wallet Loaded"

    # Functions in this section connect to the network and must use a running reactor_instance passed from CLI(or GUI)

    def create_sign_asgn_stmt(self, receiving_wid, password_for_wallet, amount, fee):

        """
        this creates an assignment statement and signs, then validates it locally before sending it to the Network
        Manager for broadcast to the network.  Before sending this to the network, wallet id must have at least
        received enough tokens to pay for the fees.

        if it is sent with a new wallet that has not received any token, this broadcast will be rejected by all nodes
        if it is a new wallet that has received tokens (tokens assigned to wallet id) then nodes will ask for wallet
        pubkey, if new client, then client pubkey will be needed also. These are all abstracted from the user.

        :param receiving_wid: wallet id of receving wallet
        :param password_for_wallet: password to decrypt privkey of wallet
        :param amount: amount of tokens to send
        :return: json encoded dictionary OR False
        """

        print("in create_sign_asgn")
        assignment_statement = \
        self.wallet_service_instance.assign_tokens(
            receiving_wid=receiving_wid, bk_connected_wid="0123456789abcdef", amount_of_tokens=amount,
            password_for_wallet=password_for_wallet, fee=fee)

        if assignment_statement:
            # validate with asgn stmt validator
            rsp = AssignmentStatementValidator(
                asgn_stmt_dict=assignment_statement,
                wallet_pubkey=self.wallet_service_instance.wallet_instance.get_wallet_pub_key(),
                user=self
            ).check_validity()

            if rsp is True:
                assignment_statement = json.dumps(assignment_statement).encode()

                return assignment_statement

        elif not assignment_statement:
            return False

        return None

    def create_transfer_transaction(self, receiving_wid, amount, fee, password_for_wallet):
        transfer_transaction = self.wallet_service_instance.transfer_tokens(receiving_wid=receiving_wid,
                                                                            amount=amount, fee=fee,
                                                                            password_for_wallet=password_for_wallet)

        if transfer_transaction:
            rsp = TransferTransactionValidator(
                transfer_tx_dict=transfer_transaction,
                wallet_pubkey=self.wallet_service_instance.wallet_instance.get_wallet_pub_key(),
                user_instance=self

            ).check_validity()

            if rsp is True:
                transfer_transaction = json.dumps(transfer_transaction).encode()

                return transfer_transaction
        elif not transfer_transaction:
            return False

        return None

    def make_wallet_bk_connected(self, amount, fee, wallet_password, time_limit, veri_node_proxies):
        token_reservation_request = self.wallet_service_instance.become_bk_connected_wallet(
            amount=amount,
            fee=fee,
            wallet_password=wallet_password,
            veri_node_proxies=veri_node_proxies,
            time_limit=time_limit
        )

        if token_reservation_request:
            rsp = TokenReservationRequestValidator(
                tkn_rsv_dict=token_reservation_request,
                wallet_pubkey=self.wallet_service_instance.wallet_instance.get_wallet_pub_key(),
                user_instance=self
            ).check_validity()

            if rsp is True:
                token_reservation_request = json.dumps(token_reservation_request).encode()
                return token_reservation_request
        elif not token_reservation_request:
            return False

        return None

    def make_wallet_not_bk_connected(self, tx_hash_of_trr, fee, wallet_password, veri_node_proxies, testing=False):
        if self.wallet_service_instance.wallet_instance.check_if_token_revoke_request_allowed() is True or testing:
            token_revoke_request = self.wallet_service_instance.become_not_bk_connected(
                tx_hash_trr=tx_hash_of_trr,
                fee=fee,
                wallet_password=wallet_password,
                veri_node_proxies=veri_node_proxies
            )

            if token_revoke_request:
                rsp = TokenRevokeRequestValidator(
                    tkn_rvk_dict=token_revoke_request,
                    wallet_pubkey=self.wallet_service_instance.wallet_instance.get_wallet_pub_key(),
                    user_instance=self
                ).check_validity()

                if rsp is True:
                    token_revoke_request = json.dumps(token_revoke_request).encode()
                    return token_revoke_request
            elif not token_revoke_request:
                return False

        return None









