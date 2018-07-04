from Orses_Database.Database import Sqlite3Database
from Orses_Util import Filenames_VariableNames
from sqlite3 import OperationalError


class RetrieveData:

    @staticmethod
    def get_user_info(username, user_instance):
        db = Sqlite3Database(dbName=Filenames_VariableNames.user_dbname.format(username),
                             in_folder=user_instance.fl.get_user_data_folder_path())
        columnToSelect = "client_id, timestamp_of_creation"
        try:

            response = db.select_data_from_table(tableName=Filenames_VariableNames.user_info_tname.format(username),
                                                 columnsToSelect=columnToSelect)
        except OperationalError:
            response = None
            db.delete_database()



        # returns [client_id, pubkey in hex format, timestamp_of_creation
        if response:
            db.close_connection()
            return response[0]
        return None




    # @staticmethod
    # def get_wallet_pubkey_from_db(wallet_id, user_instance):
    #
    #     """
    #     returns public key of wallet id
    #     :param wallet_id:
    #     :return:
    #     """
    #     db = Sqlite3Database(
    #         dbName=Filenames_VariableNames.wallet_id_dbname,
    #         in_folder=user_instance.fl.get_wallets_folder_path(),
    #     )
    #
    #     columns_to_select = "wallet_pubkey"
    #     boolcriteria = "wallet_id = '{}'".format(wallet_id)
    #     pubkey = db.select_data_from_table(tableName=Filenames_VariableNames.wallet_id_tname,
    #                                        columnsToSelect=columns_to_select, boolCriteria=boolcriteria)
    #     if pubkey:
    #         return pubkey[0][0]
    #     else:
    #         return ""

    # @staticmethod
    # def get_client_pubkey_from_db(client_id):
    #
    #     db = Sqlite3Database(dbName=Filenames_VariableNames.client_id_dbname, in_folder=Filenames_VariableNames.data_folder)
    #
    #     columns_to_select = "client_pubkey"
    #     boolcriteria = "client_id = '{}'".format(client_id)
    #     pubkey = db.select_data_from_table(tableName=Filenames_VariableNames.client_id_tname,
    #                                        columnsToSelect=columns_to_select, boolCriteria=boolcriteria)
    #     if pubkey:
    #         return pubkey[0][0]
    #     else:
    #         return ""
