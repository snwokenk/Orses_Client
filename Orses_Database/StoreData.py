from Orses_Database.Database import Sqlite3Database
from Orses_Util import Filenames_VariableNames
import json

class StoreData:

    @staticmethod
    def store_user_info_in_db(client_id, pubkey, username, timestamp_of_creation, user_instance):
        db = Sqlite3Database(dbName=Filenames_VariableNames.user_dbname.format(username),
                             in_folder=user_instance.fl.get_user_data_folder_path())

        db.insert_into_table(tableName=Filenames_VariableNames.user_info_tname.format(username),
                             client_id=client_id, pubkey=pubkey, username=username,
                             timestamp_of_creation=timestamp_of_creation)

        db.close_connection()

    @staticmethod
    def store_wallet_info_in_db(wallet_id, wallet_owner, wallet_pubkey, wallet_nickname, timestamp_of_creation,
                                wallet_locked_balance, wallet_balance, username, user_instance):
        """
        used to store wallet info at time of creation, stored it into 2 databases:
        1 database storing wallet info for all wallets on the local machine
        2 database for user specific wallets

        :param wallet_id: hex id of wallet
        :param wallet_owner: hex id of client
        :param wallet_pubkey: hex pubkey of wallet(pubkey in which wallet id is derived from)
        :param wallet_nickname: string wallet nickname (only for local computer
        :param timestamp_of_creation: int unix timestamp of creation
        :param wallet_locked_balance: float balance of locked tokens
        :param wallet_balance: float free balance
        :return: bool, True if successful
        """

        wallet_pubkey = json.dumps(wallet_pubkey)

        # insert in general wallet database for all wallets on local machine
        db = Sqlite3Database(dbName=Filenames_VariableNames.wallet_id_dbname,
                             in_folder=user_instance.fl.get_wallets_folder_path())

        db.insert_into_table(tableName=Filenames_VariableNames.wallet_id_tname, wallet_id=wallet_id,
                             wallet_owner=wallet_owner, wallet_pubkey=wallet_pubkey, wallet_nickname=wallet_nickname,
                             timestamp_of_creation=timestamp_of_creation, wallet_locked_balance=wallet_locked_balance,
                             wallet_balance=wallet_balance)
        db.close_connection()

        # insert into username_userdata db: wallet id info table (for user specific wallets)

        db1 = Sqlite3Database(dbName=Filenames_VariableNames.user_dbname.format(username),
                              in_folder=user_instance.fl.get_user_data_folder_path())

        db1.insert_into_table(tableName=Filenames_VariableNames.user_wallet_tname.format(username), wallet_id=wallet_id,
                              wallet_pubkey=wallet_pubkey, wallet_nickname=wallet_nickname, timestamp_of_creation=timestamp_of_creation,
                              wallet_locked_balance=wallet_locked_balance, wallet_balance=wallet_balance)

        db1.close_connection()

        return True