from Orses_Database.Database import Sqlite3Database
from Orses_Util import Filenames_VariableNames


class UpdateData:
    @staticmethod
    def update_wallet_info_in_db(wallet_id, wallet_locked_balance, wallet_balance, username, user_instance):

        db = Sqlite3Database(
            dbName=Filenames_VariableNames.wallet_id_dbname,
            in_folder=user_instance.fl.get_wallets_folder_path()
        )

        boolCriteria = "wallet_id = '{}'".format(wallet_id)

        new_Values = {
            "wallet_locked_balance": wallet_locked_balance,
            "wallet_balance": wallet_balance
        }

        db.update_data_in_table(
            tableName=Filenames_VariableNames.wallet_id_tname,
            boolCriteria=boolCriteria,
            dict_of_column_new_values=new_Values
        )

        db.close_connection()

        db1 = Sqlite3Database(
            dbName=Filenames_VariableNames.user_dbname.format(username),
            in_folder=user_instance.fl.get_user_data_folder_path()
        )

        db1.update_data_in_table(
            tableName=Filenames_VariableNames.user_wallet_tname.format(username),
            boolCriteria=boolCriteria,
            dict_of_column_new_values=new_Values
        )
        db1.close_connection()

