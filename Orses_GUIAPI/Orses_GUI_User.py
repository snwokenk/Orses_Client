"""
use this interface to create a user, Load A User, Import A User,

The methods call be passed as callbacks/command to a button/action in a gui interface
"""

from Orses_User.User_CLI_Helper import UserCLI


class UserCreationActions(UserCLI):
    """
    check UserCLI For methods available:

    These are the methods available:

        create_user(password, password1, username)

        load_user(password, username)

        export_user(username, password)

        import_user(password, username, alt_username=None)


    these are static methods. So No need to instantiate just do.
    an example would be:

        from Orses_GUIAPI.Orses_GUI_User import UserCreationActions

        UserCreationActions.create_user(password, password1, username)

    """
    pass
