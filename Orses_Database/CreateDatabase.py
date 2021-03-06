from Orses_Database.Database import Sqlite3Database
from Orses_Util import Filenames_VariableNames


class CreateDatabase:
    def __init__(self, user_instance):
        self.user_instance = user_instance
        self.__create_databases(user_instance=user_instance)

    def __create_databases(self, user_instance):

        self.__create_client_id_info_db(user_instance=user_instance)
        self.__create_wallet_id_info_db(user_instance=user_instance)
        self.create_user_db(username=self.user_instance.username, user_instance=user_instance)

    @staticmethod
    def __create_client_id_info_db(user_instance):

        db = Sqlite3Database(dbName=Filenames_VariableNames.client_id_dbname,
                             in_folder=user_instance.fl.get_user_data_folder_path())
        db.create_table_if_not_exist(tableName=Filenames_VariableNames.client_id_tname, primary_key="client_id",
                                     A_client_id="TEXT", B_client_pubkey="TEXT", C_username="TEXT",
                                     D_timestamp_of_creation="INT")

        db.close_connection()

    @staticmethod
    def __create_wallet_id_info_db(user_instance):

        db = Sqlite3Database(dbName=Filenames_VariableNames.wallet_id_dbname,
                             in_folder=user_instance.fl.get_wallets_folder_path())

        db.create_table_if_not_exist(tableName=Filenames_VariableNames.wallet_id_tname, primary_key="wallet_id",
                                     A_wallet_id="TEXT", B_wallet_owner="TEXT", C_wallet_pubkey="TEXT",
                                     D_wallet_nickname="TEXT", E_timestamp_of_creation="INT",
                                     F_wallet_locked_balance="REAL", G_wallet_balance="REAL",)

        db.close_connection()

    @staticmethod
    def create_user_db(username, user_instance):
        """
        creates a database named username_userdata
        password is hashed, can be used to provide password check (even though EAX already does)
        :param username: string,
        :param password: string,
        :return: None
        """

        db = Sqlite3Database(dbName=Filenames_VariableNames.user_dbname.format(username),
                             in_folder=user_instance.fl.get_user_data_folder_path())
        db.create_table_if_not_exist(tableName=Filenames_VariableNames.user_wallet_tname.format(username),
                                     primary_key="wallet_id",
                                     A_wallet_id="TEXT", C_wallet_pubkey="TEXT",
                                     D_wallet_nickname="TEXT", E_timestamp_of_creation="INT",
                                     F_wallet_locked_balance="REAL", G_wallet_balance="REAL", )

        db.create_table_if_not_exist(tableName=Filenames_VariableNames.user_info_tname.format(username),
                                     A_client_id="TEXT", B_pubkey="TEXT", C_username="TEXT",
                                     D_timestamp_of_creation="INT")
        db.close_connection()

    @staticmethod
    def create_assignment_statement_db(client_id, wallet_id, statement_hash, statement_dict):
        db = Sqlite3Database(dbName=Filenames_VariableNames.asgn_stmt_dbname,
                             in_folder=Filenames_VariableNames.data_folder)

        db.create_table_if_not_exist(tableName=Filenames_VariableNames.asgn_stmt_tname,
                                     primary_key="statement_hash", A_statement_hash="TEXT", B_client_id="TEXT",
                                     C_wallet_id="TEXT", D_statement_dict="TEXT")

        db.insert_into_table(tableName=Filenames_VariableNames.asgn_stmt_tname,
                             statement_hash=statement_hash, client_id=client_id, wallet_id=wallet_id,
                             statement_dict=statement_dict)

        db.close_connection()