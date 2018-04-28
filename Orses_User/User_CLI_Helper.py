# python module imports
# from subprocess import call

#cryptohub
from Orses_User.User import User
from Orses_Util.win_lin_mac_check import shell_command as call
from Orses_Util.FileAction import FileAction
import getpass, os, pathlib


class UserCLI:

    @staticmethod
    def create_user(password, password1, username):
        print(password1, password)
        if password1 != password:
            return False
        user = User(username=username, password=password1, newUser=True)
        if user.isNewUser:
            return user
        else:
            return None

    @staticmethod
    def load_user(password, username):

        user = User(username=username, password=password, newUser=False).load_user()

        # user can be None == no user by user name OR False == Wrong password or User_object == User sucessfully loaded
        return user

    @staticmethod
    def export_user():
        """
        takes private key, public key files and user info database files, and puts in a folder on the desktop
        :return:
        """

        call("clear")
        print("\n\n*** The Command Line Interface Of The CryptoHub Blockchain Client ***\n\n")

        print("Export User")

        username = input("Username: ")

        while True:
            password = getpass.getpass("Password: ")

            user = User(username=username, password=password, newUser=False).load_user()

            if user:
                print("User: {} loaded\n".format(user.username))
                print("client_id: {}. creation_time: {}".format(user.client_id, user.creation_time))
                ans = input("Export This User? y/n")
                if ans.upper() == "Y":
                    rsp = user.export_user()
                    if rsp:
                        print("{} has been exported to:  \n".format(user.username))
                        path1 = os.path.join(pathlib.Path.home(), "Desktop", "CryptoHub_External_Files",
                                             "Exported_Accounts", user.username + ".cryptohub")
                        print(path1, "\n")

            elif user is False:
                print("Wrong Password!\n")

            elif user is None:
                print("No User By That Name\n")

            break

        input("Press Enter To Continue")
        call("clear")

    @staticmethod
    def import_user(password, username, alt_username=None):
        """
        finds file with public key, private key files and user info database files and puts them in path for use
        :return:
        """
        FileAction.create_folder("Imported_Accounts")

        try:
            user = User(username=username, password=password, newUser=False).import_user(
                different_username=alt_username
            )
        except Exception as e:
            if e.args:

                print(e.args[0])
                if e.args[0] == "User With Username '{}' Already Exists".format(username):
                    user = "already exists"
                    # choice = input("Would You Like To Save Imported User Under A New Username? y/n")
                    # if choice.lower() == "y":
                    #     while True:
                    #         username1 = input("Alternate Username: ")
                    #         if username == username1:
                    #             print("Alternate Same As Original. Choose An Alternate Name")
                    #             continue
                    #         break
                    #     user = User(username=username, password=password, newUser=False).import_user(
                    #         different_username=username1)
                    #     if user:
                    #         print("User: '{}' imported as '{}'\n".format(username, user.username))
                    #         print("client_id: {}. creation_time: {}\n".format(user.client_id, user.creation_time))
                    #     elif user is False:
                    #         print("Wrong Password!\n")
                    #     elif user is None:
                    #         print("User With The Same Username Already Exists!\n")
                    #
                    # else:
                    #     user = None
                else:
                    print(e)
                    user = None
            else:
                user = None


        # if user:
        #     print("User: {} imported\n".format(user.username))
        #     print("client_id: {}. creation_time: {}".format(user.client_id, user.creation_time))
        # elif user is False:
        #     print("Wrong Password!\n")
        #
        # elif user is None:
        #     print("No User By That Name\n")

        print(user)

        return user
