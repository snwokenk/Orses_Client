from tkinter import *
from tkinter import ttk
from tkinter import font
from idlelib.tooltip import  ToolTip
from PIL import Image, ImageTk
from twisted.internet import tksupport, reactor, threads

# https://stackoverflow.com/questions/17635905/ttk-entry-background-colour/17639955
# https://stackoverflow.com/questions/35229352/threading-with-twisted-with-tkinter
# http://code.activestate.com/recipes/580778-tkinter-custom-fonts/
# https://www.iconfinder.com/icons/211732/copy_icon#size=128

from Orses_User.User_CLI_Helper import UserCLI, User
from Orses_Wallet.Wallet_CLI_Helper import WalletCLI
from Orses_Wallet.WalletService_CLI_Helper import WalletServiceCLI

import queue, time
"""
begin needed functions
"""


# todo: refactor OsesCLITest that checks balance and sends misc messages
# todo: add send misc messages to Orses.py
# todo: write MiscMessage class and MiscMessageValidator
# todo: link validate_balance_on_blockchain() to button for Validate


def check_active_peers():
    """
    used to call backend function for checking active peers
    :return:
    """
    global client_user

    if client_user:
        reactor.callFromThread(WSCLI.check_active_peers, reactor_instance=reactor)
    else:
        return


def get_balance():

    q_obj = queue.Queue()

    reactor.callFromThread(
        WSCLI.validate_balance_on_blockchain,
        q_obj=q_obj,
        reactor_instance=reactor
    )


def reserve_tokens(amount, fee, wallet_password, time_limit, callback_func):
    """

    :param amount:
    :param fee:
    :param wallet_password:
    :param time_limit:
    :param callback_func: MainWalletMenuFrame.should be reserve_token_network_response()
    :return:
    """
    q_obj = queue.Queue()
    veri_node_proxies = ["ID-01f", "ID-256a"]

    if 30 <= time_limit <= 1825:  # if within this turn to seconds
        time_limit *= 86400
    elif 2592000 <= time_limit <= 157680000:
        pass
    else:
        q_obj.put("time_limit")
        response_deferred = threads.deferToThread(q_obj.get)
        response_deferred.addCallback(callback_func)
        return None

    if amount < 250000.0:
        q_obj.put("low_amount")
        response_deferred = threads.deferToThread(q_obj.get)
        response_deferred.addCallback(callback_func)
        return None
    if fee < 1.0:
        q_obj.put("low_fee")
        response_deferred = threads.deferToThread(q_obj.get)
        response_deferred.addCallback(callback_func)
        return None

    reactor.callFromThread(
        WSCLI.reserve_tokens_bk_connected_wallet,
        amount=amount,
        fee=fee,
        wallet_password=wallet_password,
        veri_node_proxies=veri_node_proxies,
        q_obj=q_obj,
        time_limit=time_limit,
        reactor_instance=reactor
    )
    response_deferred = threads.deferToThread(q_obj.get)
    response_deferred.addCallback(callback_func)


def send_tokens(amount, fee, receiving_wid, password_for_wallet, callback_func, min_ttx_amt=40):
    """
    the callback function
    :param amount:
    :param fee:
    :param receiving_wid:
    :param password_for_wallet:
    :param callback_func: function which uses the response received by q_obj for whatever (for display or for a trigger)
    :param min_ttx_amt:
    :return:
    """
    q_obj = queue.Queue()

    if amount < min_ttx_amt:

        # use asgn statement
        reactor.callFromThread(
            WSCLI.send_tokens,
            reactor_instance=reactor,
            amount=amount,
            fee=fee,
            receiving_wid=receiving_wid,
            password_for_wallet=password_for_wallet,
            q_obj=q_obj

        )

    else:
        # use transfer transaction
        print("in ttx")
        reactor.callFromThread(
            WSCLI.transfer_tokens,
            reactor_instance=reactor,
            amount=amount,
            fee=fee,
            receiving_wid=receiving_wid,
            password_for_wallet=password_for_wallet,
            q_obj=q_obj

        )
    response_deferred = threads.deferToThread(q_obj.get)
    response_deferred.addCallback(callback_func)  # send_token_network_response


def periodic_network_check(label_widget, wscli):

    label_widget["text"] = "Active Peers: {}".format(len(wscli.dict_of_active))

    print("checking")
    check_active_peers()
    # root.after(5000, periodic_network_check, label_widget, wscli)


def change_colors(num=1):

    if num <= 4:
        # using color pick find hex of green
        if num == 1:
            ttk_style.configure("try.TFrame", background="green", relief="raised")
        elif num == 2:
            ttk_style.configure("try.TFrame", background="#6ee863", relief="raised")
        elif num == 3:
            ttk_style.configure("try.TFrame", background="#5be24f", relief="raised")
        else:
            ttk_style.configure("try.TFrame", background="#42e234", relief="raised")

        num += 1
        root.after(250, change_colors, num)
    else:
        num = 1
        ttk_style.configure("try.TFrame", background="#bbe8b7", relief="raised")
        num += 1
        root.after(250, change_colors, num)


def change_user(new_val):
    global client_user
    client_user = new_val


def change_wallet(new_val):
    global client_wallet
    global client_user

    if (client_user and client_wallet) and new_val is None:
        W_CLI = WalletCLI(user=client_user)
        W_CLI.unload_wallet()
    client_wallet = new_val


def get_padx(master, child):

    root.update()
    return int((master.winfo_width() - child.winfo_width())/2)


def generate_row_number():
    gen_num = 0

    while True:
        yield gen_num
        gen_num += 1


"""
end needed functions
"""



# these variables will hold a successfully loaded user object and wallet object
client_user = None
client_wallet = None
WSCLI = WalletServiceCLI(user=client_user)

# dictionary to hold windows (if necessary)
windows_dict = dict()


"""
**** Interface For Creating A User, Loading A User, Importing A User
"""
class UserAndWalletCommands:

    @staticmethod
    def create_user(password, password1, username, window_inst):
        global client_user
        client_user = UserCLI.create_user(password1=password1, password=password, username=username)

        if client_user:
            # start BaseLoggedInWindowClass

            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "Success!\n'{}' Created On Local Machine!\nClient ID:\n{}".format(client_user.username,
                                                                                           client_user.client_id)
            window_inst.insert_notification_label(
                text=valid_text,
                font_class=notif_label_font,
                text_color="Green",
                command_callback=lambda: UserAndWalletCommands.launch_main_menu(user=client_user, window_inst=window_inst)
            )

            WSCLI.set_user_instantiate_net_mgr(user=client_user)
            # for widgets in window_inst.mainframe_lower.grid_slaves():
            #     print(widgets)

        elif client_user is False:
            # password and password retype != password

            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "Passwords Do Not Match!"
            window_inst.insert_notification_label(
                text=valid_text,
                font_class=notif_label_font,
                text_color="Red",
                command_callback=lambda: UserAndWalletCommands.launch_main_menu(user=client_user, window_inst=window_inst)
            )
        elif client_user is None:
            # user with username already exists
            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "'{}' Already Exists On Local Machine!".format(username)
            window_inst.insert_notification_label(
                text=valid_text,
                font_class=notif_label_font,
                text_color="Red",
                command_callback=lambda: UserAndWalletCommands.launch_main_menu(user=client_user, window_inst=window_inst)
            )


    @staticmethod
    def load_user(password, username, window_inst):
        global client_user
        client_user = UserCLI.load_user(password=password, username=username)

        if client_user:

            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "Success!\n'{}' Loaded On Local Machine!\nClient ID:\n{}".format(client_user.username,
                                                                                           client_user.client_id)
            window_inst.insert_notification_label(
                text=valid_text,
                font_class=notif_label_font,
                text_color="Green",
                command_callback=lambda: UserAndWalletCommands.launch_main_menu(user=client_user, window_inst=window_inst)
            )
            # for widgets in window_inst.mainframe_lower.grid_slaves():
            #     print(widgets)
            WSCLI.set_user_instantiate_net_mgr(user=client_user)

        elif client_user is False:
            # Wrong Password
            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "Incorrect Password!"
            window_inst.insert_notification_label(
                text=valid_text,
                font_class=notif_label_font,
                text_color="Red",
                command_callback=lambda: UserAndWalletCommands.launch_main_menu(user=client_user, window_inst=window_inst)
            )
        elif client_user is None:
            # user with username already exists
            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "'{}' Does Not Exist On Local Machine!".format(username)
            window_inst.insert_notification_label(
                text=valid_text,
                font_class=notif_label_font,
                text_color="red",
                command_callback=lambda: UserAndWalletCommands.launch_main_menu(user=client_user, window_inst=window_inst)
            )

    @staticmethod
    def import_user(password, username, alt_username, window_inst):
        global client_user
        if alt_username in {"", "Alt. Nickname For User(optional)"}:
            alt_username = None

        client_user = UserCLI.import_user(password=password, username=username, alt_username=alt_username)

        if client_user == "already exists":
            # User with same username already exists on local machine
            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "User With The Same Username Already Exists On This Computer!\n" \
                         "Set A different Username By Entering An Alternate Username"
            window_inst.insert_notification_label(
                text=valid_text,
                font_class=notif_label_font,
                text_color="Red",
                command_callback=lambda: UserAndWalletCommands.launch_main_menu(user=client_user, window_inst=window_inst)
            )

        elif isinstance(client_user, User):
            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "Success!\n'{}' Imported And Loaded On Local Machine!\nClient ID:\n{}".format(client_user.username,
                                                                                          client_user.client_id)
            window_inst.insert_notification_label(
                text=valid_text,
                font_class=notif_label_font,
                text_color="Green",
                command_callback=lambda: UserAndWalletCommands.launch_main_menu(user=client_user, window_inst=window_inst)
            )
            # for widgets in window_inst.mainframe_lower.grid_slaves():
            #     print(widgets)
            WSCLI.set_user_instantiate_net_mgr(user=client_user)

        elif client_user is False:

            # Wrong Password
            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "Incorrect Password!"
            window_inst.insert_notification_label(
                text=valid_text,
                font_class=notif_label_font,
                text_color="Red",
                command_callback=lambda: UserAndWalletCommands.launch_main_menu(user=client_user, window_inst=window_inst)
            )

        elif client_user is None:
            # No user by username found on Imported_Accounts Folder
            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "No User By That Name In Imported_Accounts folder"
            window_inst.insert_notification_label(
                text=valid_text,
                font_class=notif_label_font,
                text_color="Red",
                command_callback=lambda: UserAndWalletCommands.launch_main_menu(user=client_user, window_inst=window_inst)
            )

    @staticmethod
    def export_user(password, username, window_inst):
        """
        used to call User.export_user method and launch window according to
        :param password: password of account
        :param username: nickname of account
        :param window_inst: instance of BaseFormWindow
        :return:
        """

        global client_user

        # can return false==wrong password, none==no user with username exists OR
        # [user, path]== user was exported to file in path
        client_user = UserCLI.export_user(username=username, password=password)

        if client_user is None:
            # user with username already exists
            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "'{}' Does Not Exist On Local Machine!\n" \
                         "User Not Exported".format(username)
            window_inst.insert_notification_label(
                text=valid_text,
                font_class=notif_label_font,
                text_color="red",
                command_callback=lambda: UserAndWalletCommands.launch_main_menu(user=client_user, window_inst=window_inst)
            )
        elif client_user is False:
            # Wrong Password
            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "Incorrect Password!\n" \
                         "User Not Exported"
            window_inst.insert_notification_label(
                text=valid_text,
                font_class=notif_label_font,
                text_color="Red",
                command_callback=lambda: UserAndWalletCommands.launch_main_menu(user=client_user, window_inst=window_inst)
            )
        elif client_user:
            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = f"Success!\n'{client_user[0].username}' With Client ID:\n" \
                         f"{client_user[0].client_id}\n" \
                         f"Has Been Exported Into File\n" \
                         f"{client_user[1]}"
            window_inst.insert_notification_label(
                text=valid_text,
                font_class=notif_label_font,
                text_color="Green",
                command_callback=lambda: UserAndWalletCommands.launch_main_menu(user=client_user, window_inst=window_inst)
            )




    @staticmethod
    def create_wallet(wallet_nickname, wallet_password, wallet_password1):

        global client_wallet
        global client_user

        if client_user:
            client_wallet = WalletCLI(user=client_user).create_wallet(
                wallet_nickname=wallet_nickname,
                wallet_password=wallet_password,
                wallet_password1=wallet_password1)

    @staticmethod
    def load_wallet(wallet_nickname, wallet_password):
        global client_wallet
        global client_user

        if client_user:

            client_wallet = WalletCLI(user=client_user).load_wallet(
                wallet_nickname=wallet_nickname,
                wallet_password=wallet_password
            )


    @staticmethod
    def launch_main_menu(user, window_inst):
        """
        Used to launch window if user successfully loaded/created/imported
        Otherwise go backs to Load User Window
        :param user: user object (if created/loaded/imported successfully) else False or None
        :param window_inst: instance of form window
        :return:
        """


        if isinstance(user, User):
            window_inst.destroy()

            main_menu_window = BaseLoggedInWindow(root, "Orses Wallet Client: MAIN MENU", client_user=user)
            main_menu_window.insert_user_logout_quit_buttons()
            main_menu_window.insert_wallet_options()
            main_menu_window.insert_market_options()
            main_menu_window.insert_logo()


            main_menu_window.protocol("WM_DELETE_WINDOW", lambda: (change_user(None),
                                                                   change_wallet(None),
                                                                   main_menu_window.destroy(),
                                                                   root.deiconify()))
        else:
            root.deiconify()
            window_inst.destroy()


class OrsesCommands:

    @staticmethod
    def create_user():
        root.withdraw()
        print("User Created")
        create_user_window = BaseFormWindow(root, title="Orses Wallet Client: Create A User")
        windows_dict["create_user"] = create_user_window

        # row 0 Header "Create User" (should be space below, and Create User Underlined

        create_user_window.insert_header_title(title="Create A User", font_class=welcome_font)

        # row 1 Username label and row 2 Username Text Field

        create_user_window.insert_username(font_class=form_label_font)

        # row 3 password label and row 4 password Text Field show="*"

        create_user_window.insert_password(font_class=form_label_font)

        # row 5 retype password label and row 6 retype password Text Field show="*"
        create_user_window.insert_password_again(font_class=form_label_font)

        # row 7 frame with buttons Cancel column 0, submit column 1 (all row 0 of frame)

        create_user_window.insert_cancel_submit_buttons(
            command_callback=lambda: UserAndWalletCommands.create_user(
                password=create_user_window.password_text.get(),
                password1=create_user_window.password1_text.get(),
                username=create_user_window.username_text.get(),
                window_inst=create_user_window
            )
        )

        # Tells program destroy window and bring back up root (user login menu)
        create_user_window.protocol("WM_DELETE_WINDOW", lambda: (root.deiconify(), create_user_window.destroy()))

    @staticmethod
    def load_user():
        root.withdraw()
        print("User Loaded")

        load_user_window = BaseFormWindow(root, title="Orses Wallet Client: Load A User")

        # store in dictionary for use outside of this function
        windows_dict["load_user"] = load_user_window

        # row 0 Header "Create User" (should be space below, and Create User Underlined
        load_user_window.insert_header_title(title="Load A User", font_class=welcome_font)

        # row 1 Username label and row 2 Username Text Field

        load_user_window.insert_username(font_class=form_label_font)

        # row 3 password label and row 4 password Text Field show="*"

        load_user_window.insert_password(font_class=form_label_font)

        # row 7 frame with buttons Cancel column 0, submit column 1 (all row 0 of frame)
        # add command call back to either go back to login menu or Logged In Menu

        load_user_window.insert_cancel_submit_buttons(
            submit_text="LOAD",
            button_state="!disabled",
            command_callback=lambda: UserAndWalletCommands.load_user(
                password=load_user_window.password_text.get(),
                username=load_user_window.username_text.get(),
                window_inst=load_user_window
            )
        )

        # Tells program destroy window and bring back up root (user login menu)
        load_user_window.protocol("WM_DELETE_WINDOW", lambda: (root.deiconify(), load_user_window.destroy()))
        # load_user_window.submit_button.bind("<Return>", lambda: UserAndWalletCommands.load_user(
        #     password=load_user_window.password_text.get(),
        #     username=load_user_window.username_text.get(),
        #     window_inst=load_user_window
        # ))


    @staticmethod
    def export_user():
        root.withdraw()
        print("User Exported")
        export_user_window = BaseFormWindow(root, title="Orses Wallet Client: Export A User")
        windows_dict["export_user"] = export_user_window

        # row 0 Header "Create User" (should be space below, and Create User Underlined
        export_user_window.insert_header_title(title="Export A User", font_class=welcome_font)

        export_user_window.insert_username(font_class=form_label_font)

        export_user_window.insert_password(font_class=form_label_font)

        export_user_window.insert_cancel_submit_buttons(
            submit_text="LOAD",
            button_state="!disabled",
            command_callback=lambda: UserAndWalletCommands.export_user(
                password=export_user_window.password_text.get(),
                username=export_user_window.username_text.get(),
                window_inst=export_user_window
            )
        )

        export_user_window.protocol("WM_DELETE_WINDOW", lambda: (root.deiconify(), export_user_window.destroy()))

    @staticmethod
    def import_user():
        root.withdraw()
        print("User Imported")
        import_user_window = BaseFormWindow(root, title="Orses Wallet Client: Import A User")
        windows_dict["import_user"] = import_user_window

        # row 0 Header "Create User" (should be space below, and Create User Underlined
        import_user_window.insert_header_title(title="Import A User", font_class=welcome_font)

        import_user_window.insert_username(font_class=form_label_font)

        import_user_window.insert_alternate_username(font_class=form_label_font)

        import_user_window.insert_password(font_class=form_label_font)

        import_user_window.insert_cancel_submit_buttons(
            submit_text="LOAD",
            button_state="!disabled",
            command_callback=lambda: UserAndWalletCommands.import_user(
                password=import_user_window.password_text.get(),
                username=import_user_window.username_text.get(),
                alt_username=import_user_window.alt_username_text.get(),
                window_inst=import_user_window
            )
        )

        import_user_window.protocol("WM_DELETE_WINDOW", lambda: (root.deiconify(), import_user_window.destroy()))

    @staticmethod
    def enable_submit(**kw):
        print("Hello")

        if len(kw["password1"]) > 0 and len(kw["password"]) >= 8 and \
                (kw["username"] and kw["username"] != "Enter Username"):
            kw["button_instance"].state(['!disabled'])
            return 1
        else:
            return 1


    @staticmethod
    def exit_program():
        root.destroy()
        reactor.stop()
        print("Program Ended")


class BaseFormWindow(Toplevel):
    """
    class holding windows for forms
    """

    x = 0

    def __init__(self, master, title, **kw):
        super().__init__(master, **kw)
        self.resizable(False, False)
        self.form_window_width = int(screen_width/2)
        self.form_window_height = main_height
        self.x_position = int((screen_width / 2) - (self.form_window_width / 2))
        self.y_position = int((screen_heigth/2) - (self.form_window_height / 2))
        self.title(title)
        self.geometry("{}x{}+{}+{}".format(
            self.form_window_width, self.form_window_height, self.x_position, self.y_position
        ))

        # create a Mainframe
        self.mainframe = ttk.Frame(self, width=self.form_window_width, height=self.form_window_height)
        self.mainframe.grid(column=0,row=0,sticky=(N,S,E,W))
        self.mainframe.grid_propagate(False)

        # create standard top frame for form windows
        self.mainframe_top = ttk.Frame(self.mainframe, width=self.form_window_width,
                                       height=int(self.form_window_height*0.15), style="top.TFrame")

        self.mainframe_top.grid(column=0, row=0, sticky=(N, S, E, W))
        self.mainframe_top.grid_propagate(False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._insert_logo()
        self.mainframe_lower_height = int(self.form_window_height*0.86)
        self.mainframe_lower = FrameWithGeneratorRows(self.mainframe, width=self.form_window_width,
                                         height=self.mainframe_lower_height, style="lower.TFrame")
        self.mainframe_lower_row_number_generator = generate_row_number()
        self.mainframe_lower.grid(column=0, row=1, sticky=(N, S, E, W))
        self.mainframe_lower.grid_propagate(False)
        self.rowconfigure(1, weight=1)

        # Entry Text
        self.username_text = StringVar(value="")
        self.alt_username_text = StringVar(value="Alt. Nickname For User(optional)")
        self.password_text = StringVar(value="")
        self.password1_text = StringVar(value="")
        self.entry_padx = (int(self.form_window_width*0.31), 0)
        self.entry_pady = (0,int(self.mainframe_lower_height*0.05))
        BaseFormWindow.x += 1

    def _insert_logo(self):

        # logo_image is created beneath use to
        welcome1_label = ttk.Label(self.mainframe_top, image=logo_image, background="#36444f", foreground="white",
                                  font=welcome_font)
        welcome1_label.grid(column=0, row=0, sticky=(W,N,S))
        welcome1_label.grid_configure(padx=int(self.form_window_width*0.35))
        self.mainframe_top.rowconfigure(0, weight=1)

    def insert_header_title(self, title, font_class, background_color="#20262b", text_color="#c2c5ce"):

        header_padx = (int(self.form_window_width*0.31), 0)
        header_pady = (int(self.mainframe_lower_height*0.01),
                       int(self.mainframe_lower_height*0.05))
        header_label = ttk.Label(self.mainframe_lower, text=title, background=background_color,
                                 foreground=text_color, font=font_class)
        header_label.grid(row=self.mainframe_lower.next_row(), sticky=N)
        header_label.grid_configure(padx=header_padx, pady=header_pady)

    def insert_username(self, font_class, label_text="username:", background_color="#20262b", text_color="#c2c5ce"):

        username_label = ttk.Label(self.mainframe_lower, text=label_text, background=background_color,
                                   foreground=text_color, font=font_class)
        username_label.grid(row=self.mainframe_lower.next_row(), sticky=N)
        username_label.grid_configure(padx=self.entry_padx)

        username_entry =ttk.Entry(self.mainframe_lower, textvariable=self.username_text, width=36, takefocus=True)
        username_entry.grid(row=self.mainframe_lower.next_row(), sticky=S)
        username_entry.grid_configure(padx=self.entry_padx, pady=self.entry_pady)
        username_entry.focus()

    def insert_alternate_username(self, font_class, label_text="Alt. Username", background_color="#20262b", text_color="#c2c5ce"):

        username_label = ttk.Label(self.mainframe_lower, text=label_text, background=background_color,
                                   foreground=text_color, font=font_class)
        username_label.grid(row=self.mainframe_lower.next_row(), sticky=N)
        username_label.grid_configure(padx=self.entry_padx)

        username_entry =ttk.Entry(self.mainframe_lower, textvariable=self.alt_username_text, width=36,
                                  takefocus=True, validate="focusin",
                                  validatecommand=lambda: self.alt_username_text.set(""))
        username_entry.grid(row=self.mainframe_lower.next_row(), sticky=S)
        username_entry.grid_configure(padx=self.entry_padx, pady=self.entry_pady)

    def insert_password(self, font_class,label_text="Password:", background_color="#20262b", text_color="#c2c5ce"):

        password_label = ttk.Label(self.mainframe_lower, text=label_text, background=background_color,
                                   foreground=text_color, font=font_class)
        password_label.grid(row=self.mainframe_lower.next_row(), sticky=N)
        password_label.grid_configure(padx=self.entry_padx)

        password_entry =ttk.Entry(self.mainframe_lower, textvariable=self.password_text, width=36, show="*")
        password_entry.grid(row=self.mainframe_lower.next_row(), sticky=S)
        password_entry.grid_configure(padx=self.entry_padx, pady=self.entry_pady)

    def insert_password_again(self, font_class,label_text="Re-enter Password:", background_color="#20262b",
                              text_color="#c2c5ce"):

        password_label = ttk.Label(self.mainframe_lower, text=label_text, background=background_color,
                                   foreground=text_color, font=font_class)
        password_label.grid(row=self.mainframe_lower.next_row(), sticky=N)
        password_label.grid_configure(padx=self.entry_padx)

        password_entry =ttk.Entry(
            self.mainframe_lower, textvariable=self.password1_text, width=36, show="*", validate="key",
            validatecommand=lambda: OrsesCommands.enable_submit(password=self.password_text.get(),
                                                                password1=self.password1_text.get(),
                                                                username=self.username_text,
                                                                button_instance=self.submit_button)
        )
        password_entry.grid(row=self.mainframe_lower.next_row(), sticky=S)
        password_entry.grid_configure(padx=self.entry_padx, pady=self.entry_pady)

        print(password_entry["width"])

    def insert_cancel_submit_buttons(self, command_callback, submit_text="SUBMIT", button_state="disabled"):

        # frame for cancel and submit button
        cancel_submit_frame_width = int(self.form_window_width*0.38)
        cancel_submit_frame_height = 27
        cancel_submit_frame_pady = (int(self.mainframe_lower_height*0.025), 0)

        cancel_submit_frame = ttk.Frame(self.mainframe_lower, style="lower.TFrame", width=cancel_submit_frame_width,
                                        height=cancel_submit_frame_height, relief="sunken")
        cancel_submit_frame.grid(row=self.mainframe_lower.next_row(), sticky=S)
        cancel_submit_frame.grid_configure(padx=self.entry_padx, pady=cancel_submit_frame_pady)
        cancel_submit_frame.grid_propagate(False)
        cancel_submit_frame.columnconfigure(0, weight=1)
        # cancel_submit_frame.rowconfigure(0, weight=1)

        # cancel button
        cancel_button_width = int(self.form_window_width*0.015)
        cancel_button = ttk.Button(cancel_submit_frame, text="CANCEL", width=cancel_button_width,
                                   command=lambda: (root.deiconify(), self.destroy()), style="cancel.TButton")
        cancel_button.grid(row=0, column=0, sticky=W)

        # submit button
        submit_button_width = int(self.form_window_width*0.015)
        self.submit_button = ttk.Button(cancel_submit_frame, text=submit_text, width=submit_button_width,
                                   command=command_callback, style="submit.TButton",
                                        state=button_state, default="active")
        self.submit_button.grid(row=0, column=1, sticky=E)
        self.bind('<Return>', lambda event: self.submit_button.invoke())
        self.bind('<KP_Enter>', lambda event: self.submit_button.invoke())

    def insert_notification_label(self, text, font_class, command_callback, background_color="#20262b",
                                  text_color="white"):

        continue_button_width = int(self.form_window_width*0.055)
        x_axis = int((self.form_window_width/5) - (continue_button_width/5))
        # notif_padx = (int(self.form_window_width*0.15), int(self.form_window_width*0.20))
        notif_padx = x_axis
        notif_pady = (int(self.mainframe_lower_height*0.05),
                       int(self.mainframe_lower_height*0.05))
        notif_label = ttk.Label(self.mainframe_lower, text=text, background=background_color,
                                foreground=text_color, font=font_class, relief="ridge",
                                wraplength=int(self.form_window_width*0.65), justify="center")
        notif_label.grid(row=self.mainframe_lower.next_row(), sticky=N)
        notif_label.grid_configure(padx=notif_padx, pady=notif_pady)

        continue_button = ttk.Button(self.mainframe_lower, text="CONTINUE", width=continue_button_width,
                                   command=command_callback, style="cancel.TButton", default="active")
        continue_button.grid(row=self.mainframe_lower.next_row(), sticky=(N,S))
        continue_button.grid_configure(padx=notif_padx, pady=notif_pady)

        self.bind('<Return>', lambda event: continue_button.invoke())
        self.bind('<KP_Enter>', lambda event: continue_button.invoke())


class BaseLoggedInWindow(Toplevel):
    """
    class holding window when logged into a user/wallet. Main Menu Window
    """
    def __init__(self, master, title, client_user,**kw):
        super().__init__(master, **kw)
        self.resizable(False, False)
        self.main_width = int(screen_width/1.1)
        self.main_height = int(screen_heigth/1.1)
        self.title(title)
        self.geometry("{}x{}+{}+{}".format(self.main_width, self.main_height, int((screen_width / 2) - (self.main_width / 2)),
                                           int((screen_heigth/2) - (self.main_height / 2))))

        # Main frame
        self.mainframe = ttk.Frame(self, width=self.main_width, height=self.main_width)
        self.mainframe.grid(column=0,row=0,sticky=(N,S,E,W))
        self.mainframe.grid_propagate(False)

        # left frame
        self.left_frame_width = int(self.main_width*0.20)
        self.left_frame_height = self.main_height
        self.left_frame = ttk.Frame(self.mainframe, width=self.left_frame_width, height=self.left_frame_height,
                                    style="left.TFrame")
        self.left_frame.grid(column=0, row=0, sticky=(W, N, S))
        self.left_frame.grid_propagate(False)
        self.left_frame_width_btn = int(self.left_frame_width*0.045)

        # middle frame
        self.middle_frame_width = int(self.main_width*0.60)
        self.middle_frame_height = self.main_height
        self.middle_frame = ttk.Frame(self.mainframe, width=self.middle_frame_width, height=self.middle_frame_height,
                                      style="middle.TFrame")
        self.middle_frame.grid(column=1, row=0, sticky=(W,N,S,E))
        self.middle_frame.grid_propagate(False)

        # right frame
        self.right_frame_width = int(self.main_width*0.20)
        self.right_frame_height = self.main_height
        self.right_frame = ttk.Frame(self.mainframe, width=self.right_frame_width, height=self.right_frame_height,
                                     style="right.TFrame")
        self.right_frame.grid(column=2, row=0, sticky=(E, N, S))
        self.right_frame.grid_propagate(False)

        # # variables_to_be_used_outside
        self.client_id_str = StringVar(value="{}".format(client_user.client_id))

        # middle frame widgets insertion
        self.insert_notebook_widget()
        self.add_welcome_frame_to_notebook_widget()
        self.add_welcome_widgets_to_welcome_frame()

        # wallet creation frame None until Create a Wallet button pressed
        self.wallet_creation_frame = None
        self.nickname_text = StringVar()
        self.password_text = StringVar()
        self.password1_text = StringVar()

        # wallet load frame None until Load A Wallet button pressed
        self.load_wallet_frame = None
        self.load_nickname_text = StringVar()
        self.load_password_text = StringVar()

        # list owned wallet frame None until "List Owned Wallet" button pressed
        self.list_owned_wallet_frame = None


    # inside a frame at top of self.left_frame on row o
    def insert_user_logout_quit_buttons(self):
        left_frame_top_width = self.left_frame_width
        left_frame_top_height = int(self.left_frame_height*0.10)

        left_frame_top = ttk.Frame(self.left_frame, style="left.TFrame", width=left_frame_top_width,
                                   height=left_frame_top_height)
        left_frame_top.grid(row=0, column=0)
        left_frame_top.grid_propagate(False)

        log_out_button = ttk.Button(
            left_frame_top,
            text="Log Out",
            width=self.left_frame_width_btn,
            command=lambda: (change_user(None), change_wallet(None), root.deiconify(), self.destroy()),
            style="logout.TButton"
        )
        log_out_button.grid(row=0, column=1, sticky=E)
        log_out_button.grid_configure(padx=((int(self.left_frame_width)*.015), 0))

        quit_button = ttk.Button(
            left_frame_top,
            text="Exit Client",
            width=self.left_frame_width_btn,
            command=OrsesCommands.exit_program,
            style="cancel.TButton"
        )
        quit_button.grid(row=0, column=0, stick=W)
        quit_button.grid_configure(padx=((int(self.left_frame_width)*.015), 0))
        quit_button.grid_configure(padx=((int(self.left_frame_width)*.01), 0))

    # inside frame at the second top of left frame row 1
    def insert_wallet_options(self):

        left_frame_top_mid_width = self.left_frame_width
        left_frame_top__mid_height = int(self.left_frame_height*0.40)

        left_frame_top_mid = ttk.Frame(self.left_frame, style="left.TFrame", width=left_frame_top_mid_width,
                                       height=left_frame_top__mid_height)
        left_frame_top_mid.grid(row=1, column=0)
        left_frame_top_mid.grid_propagate(False)

        # insert label "Wallet Menu" and separator row 0, row 1
        wallet_frame = ttk.Frame(left_frame_top_mid, width=left_frame_top_mid_width, style="sidelabelmenu.TFrame")
        # wallet_frame.grid_propagate(False)
        wallet_frame.grid(row=0, sticky=(W,E,S,N))

        wallet_menu_label = ttk.Label(wallet_frame, text="Wallet", font=menu_header_label_font,
                                      background="#242728", foreground="#c2c5ce")
        wallet_menu_label.grid(row=0, sticky=(N,S,E,W))
        # use root.update to update width value of widgets after root.mainloop()
        root.update()
        wallet_menu_label_padx= int((left_frame_top_mid.winfo_width() - wallet_menu_label.winfo_width())/2)
        print(wallet_menu_label.winfo_width(), left_frame_top_mid.winfo_width(), left_frame_top_mid_width)
        wallet_menu_label.grid_configure(padx=wallet_menu_label_padx)

        # separator
        sep1 = ttk.Separator(left_frame_top_mid, orient=HORIZONTAL)
        sep1.grid(row=1, column=0, stick=(E, W))

        # buttons
        link_btn_width = int(left_frame_top_mid_width/10.05)  # ration is ~ 1 to 7.05

        self.insert_btn_link(left_frame_top_mid, row=2, column=0, width=link_btn_width,
                             command=lambda: self.add_wallet_creation_frame(left_frame_top_mid), text="Create A Wallet",
                             master_height=left_frame_top__mid_height)
        self.insert_btn_link(left_frame_top_mid, row=3, column=0, width=link_btn_width,
                             command=lambda: self.add_load_wallet_frame(left_frame_top_mid), text="Load A Wallet",
                             master_height=left_frame_top__mid_height)
        self.insert_btn_link(left_frame_top_mid, row=4, column=0, width=link_btn_width,
                             command=lambda: self.add_list_owned_wallets_frame(), text="List Owned Wallets",
                             master_height=left_frame_top__mid_height)

    def insert_market_options(self):
        left_frame_lower_mid_width = self.left_frame_width
        left_frame_lower__mid_height = int(self.left_frame_height*0.35)

        left_frame_lower_mid = ttk.Frame(self.left_frame, style="left.TFrame", width=left_frame_lower_mid_width,
                                         height=left_frame_lower__mid_height)
        left_frame_lower_mid.grid(row=2, column=0)
        left_frame_lower_mid.grid_propagate(False)

        market_frame = ttk.Frame(left_frame_lower_mid, width=left_frame_lower_mid_width, style="sidelabelmenu.TFrame")
        # market_frame.grid_propagate(False)
        market_frame.grid(row=0, sticky=(W,E,S,N))

        market_menu_label = ttk.Label(market_frame, text="Marketplace", font=menu_header_label_font,
                                      background="#242728", foreground="#c2c5ce")
        market_menu_label.grid(row=0, sticky=(N,S,E,W))
        # use root.update to update width value of widgets after root.mainloop()
        root.update()
        market_menu_label_padx= int((left_frame_lower_mid.winfo_width() - market_menu_label.winfo_width())/2)
        market_menu_label.grid_configure(padx=market_menu_label_padx)

    def insert_logo(self):

        logo_label = ttk.Label(self.left_frame, image=logo_image, background="#303335", foreground="white",
                                   font=welcome_font)
        logo_label.grid(row=3, column=0, sticky=(N,S,E,W))
        root.update()
        logo_label_padx= int((self.left_frame.winfo_width() - logo_label.winfo_width())/2)
        logo_label_padx = int(self.left_frame.winfo_width()/6) if logo_label_padx == 0 else logo_label_padx
        logo_label.grid_configure(padx=logo_label_padx)

    def insert_btn_link(self, master, row, column, width, text, command, master_height):
        link_button = ttk.Button(master, width=width, text=text, command=lambda: (link_button.focus(), command()),
                                 style="link.TButton")
        link_button.grid(row=row, column=column, sticky=(E, W))


        link_button.grid_configure(pady=(int(master_height*.10), 0))

    def insert_notebook_widget(self):

        self.notebookwidget = ttk.Notebook(self.middle_frame, style="middle.TNotebook", padding=0)
        self.notebookwidget.grid(row=0)

    def add_welcome_frame_to_notebook_widget(self):

        self.welcome_frame = ttk.Frame(self.notebookwidget, style="middle.TFrame", width=self.middle_frame_width,
                                       height=self.middle_frame_height)
        self.welcome_frame.grid_propagate(False)
        self.notebookwidget.add(self.welcome_frame, text="Welcome")

    def add_welcome_widgets_to_welcome_frame(self):
        # add a welcome label text

        welcome_label = ttk.Label(self.welcome_frame,
                                  text="Welcome To The\nOrses Network Wallet Client\n\nYour Client ID: ",
                                  justify="center", style="welcome.TLabel", font=welcome_label_font)

        welcome_label.grid(row=0, column=0, sticky=(N,S,E,W))
        root.update()

        welcome_label_padx = int((self.welcome_frame.winfo_width() - welcome_label.winfo_width())/2)
        welcome_label_pady = int(self.welcome_frame.winfo_height()*.10)
        welcome_label.grid_configure(padx=welcome_label_padx, pady=welcome_label_pady)



        # add a read only entry
        print(self.client_id_str.get())
        client_id_entry = ttk.Entry(self.welcome_frame, textvariable=self.client_id_str,
                                    width=len(self.client_id_str.get()),
                                    exportselection=1, style="welcome.TEntry",
                                    font=font.Font(family="Times", size=16, weight="bold",))
        client_id_entry.grid(row=2, column=0)
        root.update()

        global clipboard_image
        clipboard_image1 = clipboard_image.resize(
            (int(client_id_entry.winfo_width()/30), int(client_id_entry.winfo_height()*0.75)), Image.ANTIALIAS)
        clipboard_image_TK = ImageTk.PhotoImage(clipboard_image1)
        print("im here 1", clipboard_image_TK)

        clipboard_button_padx = int((self.welcome_frame.winfo_width() -
                                  (client_id_entry.winfo_width()))/2)
        clipboard_button = ButtonLikeCanvas(
            self.welcome_frame,
            image=clipboard_image_TK,
            c_width=clipboard_image_TK.width(),
            c_height=clipboard_image_TK.height(),
            borderwidth=1,
            padx=(0, clipboard_button_padx),
            pady=1,
            command=lambda: (root.clipboard_clear(), root.clipboard_append(self.client_id_str.get()))
        )
        clipboard_button.grid(column=0, row=3, sticky=(E, S))
        ToolTip(clipboard_button, "COPY")
        self.update()


    def add_wallet_creation_frame(self, left_frame_top_mid):

        # checks to see if self.wallet_creation_frame is already a child of self.notebookwidget
        if self.wallet_creation_frame in self.notebookwidget.winfo_children():
            self.notebookwidget.select(self.wallet_creation_frame)
            print("Already Created")
            return None
        elif self.load_wallet_frame in self.notebookwidget.winfo_children():
            self.load_wallet_frame.destroy(),
            self.load_nickname_text.set(""),
            self.load_password_text.set(""),

        elif client_wallet:
            return None

        self.wallet_creation_frame = ttk.Frame(
            self.notebookwidget,
            style="middle.TFrame",
            width=self.middle_frame_width,
            height=self.middle_frame_height
        )
        self.wallet_creation_frame.grid_propagate(False)

        self.notebookwidget.add(self.wallet_creation_frame, text="Create A Wallet")
        self.notebookwidget.select(self.wallet_creation_frame)


        # insert header title "Create A Wallet"
        header_label = ttk.Label(self.wallet_creation_frame, text="Create A Wallet", background="#181e23",
                                 foreground="white", font=welcome_font)
        header_label.grid(row=0)
        root.update()
        header_label_padx = int((self.wallet_creation_frame.winfo_width() - header_label.winfo_width())/2)
        header_label_pady = (int(self.wallet_creation_frame.winfo_height() * 0.1),
                             int(self.wallet_creation_frame.winfo_height() * 0.05))
        header_label.grid_configure(padx=header_label_padx, pady=header_label_pady)

        # insert wallet nickname label and Entry
        nickname_label = ttk.Label(self.wallet_creation_frame, text="Choose A Wallet NickName:", background="#181e23",
                                   foreground="#c2c5ce", font=form_label_font)
        nickname_label.grid(row=1, sticky=N)
        nickname_label.grid_configure(padx=get_padx(self.wallet_creation_frame, nickname_label))

        nickname_entry =ttk.Entry(self.wallet_creation_frame, textvariable=self.nickname_text, width=40, takefocus=True)
        nickname_entry.grid(row=2, sticky=S)
        nickname_entry.grid_configure(padx=get_padx(self.wallet_creation_frame, nickname_entry),
                                      pady=(0,int(self.wallet_creation_frame.winfo_height() * 0.05)))
        nickname_entry.focus()

        # insert cancel and submit buttons first but must be the last row
        cancel_submit_frame = ttk.Frame(self.wallet_creation_frame, style="middle.TFrame",
                                        width=int(self.wallet_creation_frame.winfo_width()*0.39), height=27, relief="sunken")
        cancel_submit_frame.grid(row=7)
        cancel_submit_frame.grid_propagate(False)
        root.update()  # call this to update event loop of cancel_submit_frame new width and height
        cancel_submit_frame.grid_configure(
            padx=int((self.wallet_creation_frame.winfo_width() - cancel_submit_frame.winfo_width())/2),
            pady=int(self.wallet_creation_frame.winfo_height()*.025)
        )
        cancel_submit_frame.columnconfigure(0, weight=1)
        cancel_submit_frame.columnconfigure(1, weight=1)

        cancel_button_width = int(self.wallet_creation_frame.winfo_width()*0.015)
        cancel_button = ttk.Button(cancel_submit_frame, text="CANCEL", width=cancel_button_width,
                                   command=lambda: (self.wallet_creation_frame.destroy(), self.nickname_text.set(""),
                                                    self.password_text.set(""), self.password1_text.set("")),
                                   style="cancel.TButton")
        cancel_button.grid(row=0, column=0, sticky=W)

        # submit button disabled until something is in password1 entry

        main_menu_frame = MainWalletMenuFrame(
            self.notebookwidget,
            top_window=self,
            width=self.middle_frame_width,
            height=self.middle_frame_height
        )

        # instantiate submit  button
        submit_button = ttk.Button(
            cancel_submit_frame,
            text="CREATE",
            width=cancel_button_width,
            command=lambda: (
                UserAndWalletCommands.create_wallet(
                    self.nickname_text.get(),
                    self.password_text.get(),
                    self.password1_text.get()
                ),
                self.notebookwidget.add(
                    main_menu_frame,
                    text="Wallet Loaded"
                ),
                self.notebookwidget.select(main_menu_frame),
                main_menu_frame.insert_frame_based_on_created_loaded_client_wallet(),
                self.wallet_creation_frame.destroy(),
                self.nickname_text.set(""),
                self.password_text.set(""),
                self.password1_text.set(""),
                self.change_left_frame_top_mid(left_frame_top_mid, main_menu_frame),
                print(client_user)
            ),
            style="submit.TButton",
            state="disabled", default="active"
        )

        # place submit button uton cancel_submit_frame grid
        submit_button.grid(
            row=0,
            column=1,
            sticky=E
        )

        # bind submit button to enter key and keypad enter key
        self.bind('<Return>', lambda event: submit_button.invoke())
        self.bind('<KP_Enter>', lambda event: submit_button.invoke())

        # insert wallet password label AND entry
        password_label = ttk.Label(self.wallet_creation_frame, text="Choose A Password:", background="#181e23",
                                   foreground="#c2c5ce", font=form_label_font)
        password_label.grid(row=3, sticky=N)
        password_label.grid_configure(padx=get_padx(self.wallet_creation_frame, password_label))

        password_entry =ttk.Entry(self.wallet_creation_frame, textvariable=self.password_text, width=40,
                                  takefocus=False, show="*")
        password_entry.grid(row=4, sticky=S)
        password_entry.grid_configure(padx=get_padx(self.wallet_creation_frame, password_entry),
                                      pady=(0,int(self.wallet_creation_frame.winfo_height() * 0.05)))


        # insert re_entry wallet password label AND entry
        password1_label = ttk.Label(self.wallet_creation_frame, text="Re_Enter Password:", background="#181e23",
                                   foreground="#c2c5ce", font=form_label_font)
        password1_label.grid(row=5, sticky=N)
        password1_label.grid_configure(padx=get_padx(self.wallet_creation_frame, password1_label))

        password1_entry =ttk.Entry(
            self.wallet_creation_frame,
            textvariable=self.password1_text,
            width=40,
            takefocus=False,
            show="*",
            validate="key",
            validatecommand=lambda: OrsesCommands.enable_submit(password=self.password_text.get(),
                                                                password1=self.password1_text.get(),
                                                                username=self.nickname_text,
                                                                button_instance=submit_button))
        password1_entry.grid(row=6, sticky=S)
        password1_entry.grid_configure(padx=get_padx(self.wallet_creation_frame, password1_entry),
                                       pady=(0,int(self.wallet_creation_frame.winfo_height() * 0.05)))

    def add_load_wallet_frame(self, left_frame_top_mid):
        if self.load_wallet_frame in self.notebookwidget.winfo_children():
            self.notebookwidget.select(self.load_wallet_frame)
            print("Already Created")
            return None
        elif self.wallet_creation_frame in self.notebookwidget.winfo_children():
            # if wallet creation form already displaying and user clicks load, the form and anything typed are deleted
            self.wallet_creation_frame.destroy()
            self.nickname_text.set("")
            self.password_text.set("")
            self.password1_text.set("")
        elif client_wallet:
            return None

        self.load_wallet_frame = ttk.Frame(
            self.notebookwidget,
            style="middle.TFrame",
            width=self.middle_frame_width,
            height=self.middle_frame_height
        )

        self.load_wallet_frame.grid_propagate(False)
        self.notebookwidget.add(self.load_wallet_frame, text="Load A Wallet")
        self.notebookwidget.select(self.load_wallet_frame)

        # insert header title "Load A Wallet"
        header_label = ttk.Label(self.load_wallet_frame, text="Load A Wallet", background="#181e23",
                                 foreground="white", font=welcome_font)
        header_label.grid(row=0)
        root.update()
        header_label_padx = int((self.load_wallet_frame.winfo_width() - header_label.winfo_width())/2)
        header_label_pady = (int(self.load_wallet_frame.winfo_height() * 0.1),
                             int(self.load_wallet_frame.winfo_height() * 0.05))
        header_label.grid_configure(padx=header_label_padx, pady=header_label_pady)

        # insert wallet nickname label and Entry
        nickname_label = ttk.Label(self.load_wallet_frame, text="Wallet Nickname:", background="#181e23",
                                   foreground="#c2c5ce", font=form_label_font)
        nickname_label.grid(row=1, sticky=N)
        nickname_label.grid_configure(padx=get_padx(self.load_wallet_frame, nickname_label))

        nickname_entry =ttk.Entry(self.load_wallet_frame, textvariable=self.load_nickname_text, width=40, takefocus=True)
        nickname_entry.grid(row=2, sticky=S)
        nickname_entry.grid_configure(padx=get_padx(self.load_wallet_frame, nickname_entry),
                                      pady=(0,int(self.load_wallet_frame.winfo_height() * 0.05)))
        nickname_entry.focus()

        # insert wallet password label AND entry
        password_label = ttk.Label(self.load_wallet_frame, text="Wallet Password:", background="#181e23",
                                   foreground="#c2c5ce", font=form_label_font)
        password_label.grid(row=3, sticky=N)
        password_label.grid_configure(padx=get_padx(self.load_wallet_frame, password_label))

        password_entry =ttk.Entry(self.load_wallet_frame, textvariable=self.load_password_text, width=40,
                                  takefocus=False, show="*")
        password_entry.grid(row=4, sticky=S)
        password_entry.grid_configure(padx=get_padx(self.load_wallet_frame, password_entry),
                                      pady=(0,int(self.load_wallet_frame.winfo_height() * 0.05)))

        # insert cancel and submit buttons first but must be the last row
        cancel_submit_frame = ttk.Frame(self.load_wallet_frame, style="middle.TFrame",
                                        width=int(self.load_wallet_frame.winfo_width()*0.39), height=27, relief="sunken")
        cancel_submit_frame.grid(row=5)
        cancel_submit_frame.grid_propagate(False)
        root.update()  # call this to update event loop of cancel_submit_frame new width and height
        cancel_submit_frame.grid_configure(
            padx=int((self.load_wallet_frame.winfo_width() - cancel_submit_frame.winfo_width())/2),
            pady=int(self.load_wallet_frame.winfo_height()*.025)
        )
        cancel_submit_frame.columnconfigure(0, weight=1)
        cancel_submit_frame.columnconfigure(1, weight=1)

        # insert cancel button
        cancel_button_width = int(self.load_wallet_frame.winfo_width()*0.015)
        cancel_button = ttk.Button(cancel_submit_frame, text="CANCEL", width=cancel_button_width,
                                   command=lambda: (self.load_wallet_frame.destroy(), self.load_nickname_text.set(""),
                                                    self.load_password_text.set("")),
                                   style="cancel.TButton")
        cancel_button.grid(row=0, column=0, sticky=W)

        # instantiate main menu frame and submit button
        main_menu_frame = MainWalletMenuFrame(
            self.notebookwidget,
            top_window=self,
            width=self.middle_frame_width,
            height=self.middle_frame_height
        )

        submit_button = ttk.Button(
            cancel_submit_frame,
            text="LOAD",
            width=cancel_button_width,
            command=lambda: (
                # self.unbind_all('<Return>'),
                # self.unbind_all('<KP_Enter>'),
                UserAndWalletCommands.load_wallet(
                    self.load_nickname_text.get(),
                    self.load_password_text.get(),
                ),
                self.notebookwidget.add(
                    main_menu_frame,
                    text="Wallet Loaded"
                ),
                self.notebookwidget.select(main_menu_frame),
                main_menu_frame.insert_frame_based_on_created_loaded_client_wallet(created=False),
                self.load_wallet_frame.destroy(),
                self.load_nickname_text.set(""),
                self.load_password_text.set(""),
                self.change_left_frame_top_mid(left_frame_top_mid, main_menu_frame),
                cancel_submit_frame.destroy(),
                print(client_user)
            ),
            default="active",
            style="submit.TButton"
        )
        submit_button.grid(row=0, column=1, sticky=E)
        self.bind('<Return>', lambda event: submit_button.invoke())
        self.bind('<KP_Enter>', lambda event: submit_button.invoke())

    def add_list_owned_wallets_frame(self):
        """
        used to create a frame listing owned wallets of User. List the wallet nickname and walled id
        but not the balance
        :return:
        """
        if self.list_owned_wallet_frame in self.notebookwidget.winfo_children():
            self.notebookwidget.select(self.list_owned_wallet_frame)
            print("Already Created")
            return None

        # create frame
        self.list_owned_wallet_frame = ttk.Frame(
            self.notebookwidget,
            style="middle.TFrame",
            width=self.middle_frame_width,
            height=self.middle_frame_height
        )

        # make frame maintain it's size, independently of children widgets in it
        self.list_owned_wallet_frame.grid_propagate(False)

        # add frame to notebookwidget
        self.notebookwidget.add(self.list_owned_wallet_frame, text="Wallets Owned")

        # select frame and make it displayed to user when created
        self.notebookwidget.select(self.list_owned_wallet_frame)

        # insert header title "Wallets Owned by {user}"
        header_text = f'Wallets Owned by {client_user.username}:'
        header_label = ttk.Label(self.list_owned_wallet_frame, text=header_text, justify="center",
                                  style="welcome.TLabel", font=welcome_label_font)

        header_label.grid(row=0, sticky=(N,S,E,W))

        root.update()
        header_label_padx = int((self.list_owned_wallet_frame.winfo_width() - header_label.winfo_width())/2)
        header_label_pady = (int(self.list_owned_wallet_frame.winfo_height() * 0.1),
                             int(self.list_owned_wallet_frame.winfo_height() * 0.05))

        # print("in list owned: wallet frame info: ", self.list_owned_wallet_frame.winfo_width(), header_label.winfo_width())
        header_label.grid_configure(padx=header_label_padx, pady=header_label_pady)

        list_of_wallets = list(client_user.associated_wallets.keys())
        wallets_owned_strvar = StringVar(value=list_of_wallets)
        print("list of wallets in list owned: ", list_of_wallets, wallets_owned_strvar.get())

        # height of listbox is number of rows, therefore should be at least number of wallets owned
        height_of_listbox = len(list_of_wallets)+2
        wallets_listbox = Listbox(self.list_owned_wallet_frame, height=height_of_listbox,
                                  listvariable=wallets_owned_strvar, width=64, font=("fixed", 12))
        wallets_listbox.grid(row=1)
        print("wallet listbox font: ", wallets_listbox['font'])

        # update toplevel
        root.update()

        wallet_listbox_padx = int((self.list_owned_wallet_frame.winfo_width() - wallets_listbox.winfo_width())/2)
        wallet_listbox_pady = (int(self.list_owned_wallet_frame.winfo_height() * 0.1),
                             int(self.list_owned_wallet_frame.winfo_height() * 0.05))
        wallets_listbox.grid_configure(padx=wallet_listbox_padx, pady=wallet_listbox_pady)


        # insert close button
        close_button_width = int(self.list_owned_wallet_frame.winfo_width()*0.055)
        close_button = ttk.Button(self.list_owned_wallet_frame, text="CLOSE", width=close_button_width,
                                  command=lambda: self.list_owned_wallet_frame.destroy(), style="cancel.TButton",
                                  default="active")
        close_button.grid(row=2, sticky=(N,S))
        root.update()
        x_axis = int((self.list_owned_wallet_frame.winfo_width() - close_button.winfo_width())/2)
        close_button.grid_configure(padx=x_axis, pady=5)

        self.bind('<Return>', lambda event: close_button.invoke())
        self.bind('<KP_Enter>', lambda event: close_button.invoke())

    def change_left_frame_top_mid(self, left_frame_top_mid, main_menu_frame):
        global client_wallet
        if client_wallet:
            for i in left_frame_top_mid.winfo_children():
                print("child: ", i, type(i))
                if isinstance(i, ttk.Button):
                    i.grid_remove()
            link_btn_width = int(self.left_frame_width/10.05)  # ration is ~ 1 to 7.05
            left_frame_top__mid_height = int(self.left_frame_height*0.40)
            self.insert_btn_link(
                left_frame_top_mid,
                row=5,
                column=0,
                width=link_btn_width,
                command=lambda: (
                    change_wallet(None),
                    self.undo_change_left_frame_top_mid(left_frame_top_mid, main_menu_frame)
                ),
                text="Unload Wallet",
                master_height=left_frame_top__mid_height)

        for i in left_frame_top_mid.winfo_children():
            print("checking: ", i)
            print(i.grid_info())
            print("=======")

    def undo_change_left_frame_top_mid(self, left_frame_top_mid, main_menu_frame):
        """
        method is called to destroy main frame and then
         restore buttons on left to "load a wallet", "create a wallet" "list owned wallets"
        :param left_frame_top_mid: frame in which buttons were held
        :param main_menu_frame: main frame with "send tokens" "validate balance" etc buttons
        :return:
        """


        # destroy the main menue frame
        main_menu_frame.send_token_form_frame.destroy() if main_menu_frame.send_token_form_frame else None
        main_menu_frame.reserve_token_form_frame.destroy() if main_menu_frame.reserve_token_form_frame else None
        main_menu_frame.destroy()

        # destroy the "unload wallet button, and put back the load wallet, create wallet and list wallet button
        for i in left_frame_top_mid.winfo_children():
            print("child: ", i, type(i))
            if isinstance(i, ttk.Button):
                if i.grid_info():
                    i.destroy()
                else:
                    i.grid()






""" Classes For Main Wallet Frames, Used After A Wallet Is Loaded/Created launched with LOAD OR SUBMIT Button on 
create a wallet or load a wallet frame
"""


class MainWalletFrameForNotebook(ttk.Frame):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self["style"] = "middle.TFrame"
        self.grid_propagate(False)
        self.row_count = 0
        self.column_count = 0


class MainWalletMenuFrame(MainWalletFrameForNotebook):

    """
    Use to add frame to a notebook widget, automatically sets width and height and propagate to false
    """

    def __init__(self, master, top_window: Toplevel, **kw):
        super().__init__(master, **kw)
        self.top_window = top_window
        self.top_frame = ttk.Frame(self)
        self.middle_Frame = ttk.Frame(self)
        self.lower_frame = ttk.Frame(self)
        self.notebookwidget = master

        # send token form frame None until Send Tokens button pressed
        self.send_token_form_frame = None
        self.wallet_address_text = StringVar()
        self.send_amount_float = DoubleVar()
        self.send_amount_fee_float = DoubleVar()
        self.wallet_password_text = StringVar()

        # reserve token form frame None until Reserve Tokens button pressed
        self.reserve_token_form_frame = None
        self.reserve_amount_float = DoubleVar()
        self.reserve_amount_fee_float = DoubleVar(value=1.0)
        self.reserve_length_float = DoubleVar(value=360.0)
        self.reserve_wallet_password_text = StringVar()

        self.network_response_deffered = None

    def reserve_token_network_response(self, x):
        self.network_response_deffered = x
        # if self.network_response_deffered >= 0.50:
        for i in self.reserve_token_form_frame.winfo_children():
            print("child: ", i, type(i))
            i.grid_remove()
        self.reserve_amount_float.set(0.0)
        self.reserve_amount_fee_float.set(1.0)
        self.reserve_wallet_password_text.set("")
        self.reserve_length_float.set(30.0)

        if self.network_response_deffered == "time_limit":
            text = "Reservation Not Made. Duration Of Reservation Must Be Between 30 to 1825 days or\n" \
                   "2592000 to 157680000 seconds. "
            color = "red"
        elif self.network_response_deffered == "low_amount":
            text = "Reservation Amount Can Not Be Less Than 250,000 tokens"
            color = "red"
        elif self.network_response_deffered == "low_fee":
            text = "Fee For Token Reservation Must Be 1 Token Or Greater"
            color = "red"
        elif self.network_response_deffered == 0.0:
            text = "Tokens Not Reserved. Check To Make Sure You Have Active Peers Available And You Are Connected\n" \
                   "To The Internet"
            color = "red"
        elif self.network_response_deffered < 0.0:
            text = "Wrong Wallet Password! Please Try Again"
            color = "red"
        else:
            text = "Tokens Reserved"
            color = "green"

        self.insert_notification_label(
            text=text,
            font_class=notif_label_font,
            text_color=color,
            master=self.reserve_token_form_frame
        )

    def send_token_network_response(self, x):
        """
        used in send token, reserve tokens, validate balance functions. used as a callBack function from a
        deferral object created by deferToThread
        :param x:
        :return:
        """

        self.network_response_deffered = x
        # if self.network_response_deffered >= 0.50:
        for i in self.send_token_form_frame.winfo_children():
            print("child: ", i, type(i))
            i.grid_remove()
        self.wallet_address_text.set("")
        self.send_amount_float.set(0.0)
        self.send_amount_fee_float.set(0.0)
        self.wallet_password_text.set("")
        if self.network_response_deffered == 0.0:

            text = "Tokens Not Sent. Check To Make Sure You Have Active Peers Available And You Are Connected\n" \
                   "To The Internet"
            color = "red"
        elif self.network_response_deffered < 0.0:
            text = "Wrong Wallet Password "
            color = "red"

        else:
            text = "Tokens Sent"
            color = "green"

            #

        self.insert_notification_label(
            text=text,
            font_class=notif_label_font,
            text_color=color,
            master=self.send_token_form_frame
        )




    def insert_frame_based_on_created_loaded_client_wallet(self, created=True):
        if client_wallet:
            if created:
                print("wallet client created")
            else:
                print("wallet client loaded")

            self.insert_main_menu_widgets_when_wallet_properly_loaded()

        elif client_wallet is None:
            if created:
                print("wallet with same nickname exist OR No User Loaded")
                text = "Wallet With The Same Nickname Already Exists"
            else:
                print("wallet with nickname does not exist")
                text = "wallet with nickname does not exist"

            self.insert_notification_label(
                text=text,
                font_class=notif_label_font,
                text_color="red"
            )
        elif client_wallet is False:
            if created:
                print("chosen password and retyped password does not match")
                text = "Passwords Do Not Match, Make Sure To Retype Exact Chosen Password"
            else:
                print("Incorrect Wallet Password")
                text = "Incorrect Wallet Password"
            self.insert_notification_label(
                text= text,
                font_class=notif_label_font,
                text_color="red"
            )

    def insert_main_menu_widgets_when_wallet_properly_loaded(self):
        """
        3 frames self frame (Main Wallet Menu Frame)
        top frame will hold the client id, wallet id, mini Logo(O logo), connection status,
        active peers logo
        :return:
        """
        root.update()
        # heights of frames, width == width of self frame
        self.top_frame_height = int(self.winfo_height() * 0.12)
        self.middle_Frame_height = int(self.winfo_height() * 0.04)
        self.lower_frame_height = int(self.winfo_height() * 0.80)

        # top frame
        self.top_frame["width"] = self.winfo_width()
        self.top_frame["height"] = self.top_frame_height
        self.top_frame["style"] = "middle.TFrame"
        # self.top_frame["relief"] = "raised"
        self.top_frame.grid(row=0)
        self.top_frame.grid_propagate(False)

        # middle frame
        self.middle_Frame["width"] = self.winfo_width()
        self.middle_Frame["height"] = self.middle_Frame_height
        self.middle_Frame["style"] = "middle.TFrame"
        self.middle_Frame["relief"] = "sunken"
        self.middle_Frame.grid(row=1)
        self.middle_Frame.grid_propagate(False)

        # lower frame
        self.lower_frame["width"] = self.winfo_width()
        self.lower_frame["height"] = self.lower_frame_height
        self.lower_frame["style"] = "middle.TFrame"
        self.lower_frame["relief"] = "flat"
        self.lower_frame.grid(row=2)
        self.lower_frame.grid_propagate(False)



        # get logo image
        root.update()
        image2 = Image.open("OLogo.png")
        self.logo_image = image2.resize((int(self.top_frame.winfo_height()*0.85), int(self.top_frame_height*0.85)),
                                        Image.ANTIALIAS)
        self.logo_image = ImageTk.PhotoImage(self.logo_image)
        image2.close()

        root.update()
        self.__insert_top_frame_widgets()
        self.__insert_middle_frame_widgets()
        self.__insert_lower_frame_widgets()

    def __insert_top_frame_widgets(self):
        """
        3 columns and 2 rows
        column 0 and row 0 = client id
        column 0 and row 1 = wallet id

        column 1 and row 0 = part1 of logo
        column 1 and row 1 = par2  of logo (spans 2 rows)

        column 2 and row 0 = frame with connection state label and blinking light
        column 2 and row 1 = active peers
        :return:
        """

        # insert connection widgets with a frame
        connect_info_frame = ttk.Frame(
            self.top_frame,
            style="middle.TFrame",
            width=self.top_frame.winfo_width(),
            height=int(self.top_frame.winfo_height()*0.2),
        )
        connect_info_frame.grid(row=0, column=0, sticky=S)
        connect_info_frame.grid_propagate(False)



        # connection label in column 0 row o of connection_info_frame
        check_active_peers()
        connection_label = ttk.Label(
            connect_info_frame,
            text="Active Peers: {}".format(len(WSCLI.dict_of_active)),
            background="#181e23",
            foreground="#c2c5ce",
            font=connection_top_label
        )
        connection_label.grid(row=0, column=0, sticky=(E, S))
        root.after(1000, periodic_network_check, connection_label, WSCLI)

        # connection blinker will be in column 1 row 0



        # insert logo label
        logo_label = ttk.Label(
            self.top_frame,
            image=self.logo_image,
            background="#181e23",
            foreground="white",
            font=main_menu_top_label
        )
        logo_label.grid(column=0, row=1, sticky=S)
        root.update()


        logo_label_padx = int((self.top_frame.winfo_width() - logo_label.winfo_width())/2)
        logo_label_pady = int((self.top_frame.winfo_height() - logo_label.winfo_height())/2)
        logo_label.grid_configure(padx=logo_label_padx, pady=0)

        root.update()
        print("connection frame size: ", connect_info_frame.winfo_width(), connect_info_frame.winfo_height())
        print("top_frame size", self.top_frame.winfo_width(), self.top_frame.winfo_height())
        print("logo label size: ", logo_label.winfo_width(), logo_label.winfo_height())

    def __insert_middle_frame_widgets(self):
        temp_id = client_user.wallet_service_instance.wallet_instance.get_wallet_id()
        # insert wallet label
        wallet_id_label = ttk.Label(self.middle_Frame,
                                    text=f"Wallet ID: {temp_id}",
                                    background="#181e23",
                                    foreground="#c2c5ce",
                                    font=main_menu_top_label)
        wallet_id_label.grid(column=0, row=0, sticky=(W, S))
        root.update()

        wallet_id_label_padx= (int((self.middle_Frame.winfo_width() - wallet_id_label.winfo_width())/2), 2)
        wallet_id_label_pady= int((self.middle_Frame.winfo_height() - wallet_id_label.winfo_height())/2)
        wallet_id_label.grid_configure(pady=wallet_id_label_pady,
                                       padx=wallet_id_label_padx)

        global clipboard_image
        # clipboard_image = Image.open("copy_icon.png")
        # print((int(wallet_id_label.winfo_width()/15), int(wallet_id_label.winfo_height()*0.95)))
        clipboard_image2 = clipboard_image.resize(
            (int(wallet_id_label.winfo_width()/30), int(wallet_id_label.winfo_height()*0.90)), Image.ANTIALIAS)
        clipboard_image_TK = ImageTk.PhotoImage(clipboard_image2)
        print("im here", clipboard_image_TK)

        print(clipboard_image_TK.width(), clipboard_image_TK.height())

        clipboard_button = ButtonLikeCanvas(
            self.middle_Frame,
            image=clipboard_image_TK,
            c_width=clipboard_image_TK.width(),
            c_height=clipboard_image_TK.height(),
            borderwidth=1,
            padx=(0, 100),
            pady=0,
            command=lambda: (root.clipboard_clear(), root.clipboard_append(temp_id))
        )
        clipboard_button.grid(column=1, row=0, sticky=(W))
        ToolTip(clipboard_button, "COPY")
        # clipboard_image.close()


    def __insert_lower_frame_widgets(self):
        frame_for_buttonlike_canvas = ttk.Frame(
            self.lower_frame,
            style="middle.TFrame",
            width=self.lower_frame.winfo_width(),
            height=int(self.lower_frame.winfo_height()*0.60),
        )
        frame_for_buttonlike_canvas.grid(row=0)

        # 4 square button_like canvas will be created. 1 for "send tokens" 2 for "receive tokens"
        # 3 for "validate balance" and 4 for "Make Wallet Blockchain Connected"(this is disabled if not enough tokens

        root.update()

        # first canvas button "Send Tokens"
        snd_tkn_canvas_btn = ButtonLikeCanvas(frame_for_buttonlike_canvas, text="Send Tokens", color="#33434f",
                                              command=lambda: self.add_send_token_form_frame())
        snd_tkn_canvas_btn.grid(row=0, column=0)

        # second canvas buton "Receive Tokens"
        rcv_tkn_canvas_btn = ButtonLikeCanvas(frame_for_buttonlike_canvas, text="Receive Tokens", color="#26313a")
        rcv_tkn_canvas_btn.grid(row=0, column=1)

        # 3rd canvas button "Validate Balance"
        validate_balance_canvas_btn = ButtonLikeCanvas(frame_for_buttonlike_canvas, text="Validate Balance",
                                                       color="#26313a")
        validate_balance_canvas_btn.grid(row=1, column=0)

        # 4th canvas button "Reserve Token"
        rsv_tkn_canvas_btn = ButtonLikeCanvas(frame_for_buttonlike_canvas, text="Reserve Tokens", color="#33434f",
                                              command=lambda: self.add_reserve_token_form_frame())
        rsv_tkn_canvas_btn.grid(row=1, column=1)


    # if wallet not created (false or none)
    def insert_notification_label(self, text, font_class, background_color="#181e23",
                                  text_color="white", master=None):
        """
        use to display notification if wallet is not created because of wrong password or conflicting nickname

        :param text: warning text
        :param font_class: font class (notif_label_font
        :param background_color:
        :param text_color:
        :return:
        """

        master = self if master is None else master

        # insert label
        notif_label = ttk.Label(master, text=text, background=background_color,
                                foreground=text_color, font=font_class, relief="ridge",
                                wraplength=int(master.winfo_width()*0.65), justify="center")
        notif_label.grid(row=9, sticky=N)
        root.update()
        notif_padx = int((master.winfo_width() - notif_label.winfo_width())/2)
        notif_pady = int(master.winfo_height()*0.05)
        notif_label.grid_configure(padx=notif_padx, pady=notif_pady)

        continue_button_width = int(master.winfo_width()*0.055)
        continue_button = ttk.Button(master, text="CONTINUE", width=continue_button_width,
                                     command=lambda: master.destroy(), style="cancel.TButton", default="active")
        continue_button.grid(row=10, sticky=(N,S))
        root.update()
        x_axis = int((master.winfo_width() - continue_button.winfo_width())/2)
        continue_button.grid_configure(padx=x_axis, pady=notif_pady)

        self.top_window.bind('<Return>', lambda event: continue_button.invoke())
        self.top_window.bind('<KP_Enter>', lambda event: continue_button.invoke())

    def add_send_token_form_frame(self):
        """
        This method when called will start a new tab in after "send token" is clicked which allows users
        to send input wallet address, tokens, fees (required minimum) and wallet password to send tokens
        :return:
        """

        if self.send_token_form_frame in self.notebookwidget.winfo_children():
            self.notebookwidget.select(self.send_token_form_frame)
            print("Already Created")
            return None

        self.send_token_form_frame = ttk.Frame(
            self.notebookwidget,
            style="middle.TFrame",
            width=self.lower_frame.winfo_width(),
            height=self.lower_frame_height
        )
        self.send_token_form_frame.grid_propagate(False)

        self.notebookwidget.add(self.send_token_form_frame, text="Send Tokens")
        self.notebookwidget.select(self.send_token_form_frame)

        # insert header title "Send Tokens"
        header_label = ttk.Label(self.send_token_form_frame, text="Send Tokens", background="#181e23",
                                 foreground="white", font=welcome_font)
        header_label.grid(row=0)
        root.update()
        header_label_padx = int((self.send_token_form_frame.winfo_width() - header_label.winfo_width())/2)
        header_label_pady = (int(self.send_token_form_frame.winfo_height() * 0.1),
                             int(self.send_token_form_frame.winfo_height() * 0.05))
        header_label.grid_configure(padx=header_label_padx, pady=header_label_pady)

        # insert wallet addr label and Entry
        wallet_addr_label = ttk.Label(self.send_token_form_frame, text="Receiving Wallet Address:", background="#181e23",
                                      foreground="#c2c5ce", font=form_label_font)
        wallet_addr_label.grid(row=1, sticky=N)
        wallet_addr_label.grid_configure(padx=get_padx(self.send_token_form_frame, wallet_addr_label))

        wallet_addr_entry =ttk.Entry(self.send_token_form_frame, textvariable=self.wallet_address_text, width=40, takefocus=True)
        wallet_addr_entry.grid(row=2, sticky=S)
        wallet_addr_entry.grid_configure(padx=get_padx(self.send_token_form_frame, wallet_addr_entry),
                                         pady=(0,int(self.send_token_form_frame.winfo_height() * 0.05)))
        wallet_addr_entry.focus()

        # insert Amount Label and Entry
        send_amount_label = ttk.Label(self.send_token_form_frame, text="Amount:", background="#181e23",
                                      foreground="#c2c5ce", font=form_label_font)
        send_amount_label.grid(row=3, sticky=N)
        send_amount_label.grid_configure(padx=get_padx(self.send_token_form_frame, send_amount_label))

        send_amount_entry = ttk.Entry(self.send_token_form_frame, textvariable=self.send_amount_float, width=40)
        send_amount_entry.grid(row=4, sticky=S)
        send_amount_entry.grid_configure(padx=get_padx(self.send_token_form_frame, send_amount_entry),
                                         pady=(0,int(self.send_token_form_frame.winfo_height() * 0.05)))

        # insert Fee amount Label and Entry
        send_amount_fee_label = ttk.Label(self.send_token_form_frame, text="Fee:", background="#181e23",
                                          foreground="#c2c5ce", font=form_label_font)
        send_amount_fee_label.grid(row=5, sticky=N)
        send_amount_fee_label.grid_configure(padx=get_padx(self.send_token_form_frame, send_amount_fee_label))

        send_amount_fee_entry = ttk.Entry(self.send_token_form_frame, textvariable=self.send_amount_fee_float, width=40)
        send_amount_fee_entry.grid(row=6, sticky=S)
        send_amount_fee_entry.grid_configure(padx=get_padx(self.send_token_form_frame, send_amount_fee_entry),
                                             pady=(0,int(self.send_token_form_frame.winfo_height() * 0.05)))

        # insert wallet password label AND entry
        password_label = ttk.Label(self.send_token_form_frame, text="Wallet Password:", background="#181e23",
                                   foreground="#c2c5ce", font=form_label_font)
        password_label.grid(row=7, sticky=N)
        password_label.grid_configure(padx=get_padx(self.send_token_form_frame, password_label))

        password_entry =ttk.Entry(self.send_token_form_frame, textvariable=self.wallet_password_text, width=40,
                                  takefocus=False, show="*")
        password_entry.grid(row=8, sticky=S)
        password_entry.grid_configure(padx=get_padx(self.send_token_form_frame, password_entry),
                                      pady=(0,int(self.send_token_form_frame.winfo_height() * 0.05)))



        # insert cancel and submit buttons first
        cancel_submit_frame = ttk.Frame(self.send_token_form_frame, style="middle.TFrame",
                                        width=int(self.send_token_form_frame.winfo_width()*0.39), height=27, relief="sunken")
        cancel_submit_frame.grid(row=9)
        cancel_submit_frame.grid_propagate(False)
        root.update()  # call this to update event loop of cancel_submit_frame new width and height
        cancel_submit_frame.grid_configure(
            padx=int((self.send_token_form_frame.winfo_width() - cancel_submit_frame.winfo_width())/2),
            pady=int(self.send_token_form_frame.winfo_height()*.025)
        )
        cancel_submit_frame.columnconfigure(0, weight=1)
        cancel_submit_frame.columnconfigure(1, weight=1)

        # insert cancel button
        cancel_button_width = int(self.send_token_form_frame.winfo_width()*0.015)
        cancel_button = ttk.Button(cancel_submit_frame, text="CANCEL", width=cancel_button_width,
                                   command=lambda: (self.send_token_form_frame.destroy(), self.wallet_address_text.set(""),
                                                    self.send_amount_float.set(0.0),
                                                    self.send_amount_fee_float.set(0.0),
                                                    self.wallet_password_text.set("")),
                                   style="cancel.TButton")
        cancel_button.grid(row=0, column=0, sticky=W)

        sending_label = ttk.Label(self.send_token_form_frame, text="Sending....Please Wait", background="#181e23",
                                  foreground="#c2c5ce", font=form_label_font)
        submit_button = None
        submit_button = ttk.Button(
            cancel_submit_frame,
            text="SEND",
            width=cancel_button_width,
            command=lambda: (submit_button.state(["disabled"]),send_tokens(self.send_amount_float.get(), self.send_amount_fee_float.get(), self.wallet_address_text.get(), self.wallet_password_text.get(), self.send_token_network_response),
                             sending_label.grid(row=10, sticky=N), root.update(),sending_label.grid_configure(padx=get_padx(self.send_token_form_frame, sending_label))),
            default="active",
            style="submit.TButton"
        )
        submit_button.grid(row=0, column=1, sticky=E)

        self.top_window.bind('<Return>', lambda event: submit_button.invoke())
        self.top_window.bind('<KP_Enter>', lambda event: submit_button.invoke())

        # self.top_window.bind('<Return>', lambda event: [self.top_window.unbind('<Return>'), self.top_window.unbind('<KP_Enter>'),submit_button.invoke()])
        # self.top_window.bind('<KP_Enter>', lambda event: [self.top_window.unbind('<Return>'), self.top_window.unbind('<KP_Enter>'),submit_button.invoke()])

    def add_reserve_token_form_frame(self):

        if self.reserve_token_form_frame in self.notebookwidget.winfo_children():
            self.notebookwidget.select(self.reserve_token_form_frame)
            print("Already Created")
            return None

        self.reserve_token_form_frame = FrameWithGeneratorRows(
            self.notebookwidget,
            style="middle.TFrame",
            width=self.lower_frame.winfo_width(),
            height=self.lower_frame_height
        )

        self.reserve_token_form_frame.grid_propagate(False)

        self.notebookwidget.add(self.reserve_token_form_frame, text="Reserve Tokens")
        self.notebookwidget.select(self.reserve_token_form_frame)

        # insert header title "Reserve Tokens"
        header_text = "Reserve Tokens\n" \
                      "Become A Blockchain Connected Wallet"
        header_label = ttk.Label(self.reserve_token_form_frame, text=header_text, background="#181e23",
                                 foreground="white", font=welcome_font, justify="center")
        header_label.grid(row=0)
        root.update()
        header_label_padx = int((self.reserve_token_form_frame.winfo_width() - header_label.winfo_width())/2)
        header_label_pady = (int(self.reserve_token_form_frame.winfo_height() * 0.1),
                             int(self.reserve_token_form_frame.winfo_height() * 0.05))
        header_label.grid_configure(padx=header_label_padx, pady=header_label_pady)

        # insert Reserve Amount Label and Entry
        reserve_amount_text = "Amount. Min 250k:"
        reserve_amount_label = ttk.Label(self.reserve_token_form_frame, text=reserve_amount_text, background="#181e23",
                                      foreground="#c2c5ce", font=form_label_font)
        reserve_amount_label.grid(row=1, sticky=N)
        reserve_amount_label.grid_configure(padx=get_padx(self.reserve_token_form_frame, reserve_amount_label))

        reserve_amount_entry = ttk.Entry(self.reserve_token_form_frame, textvariable=self.reserve_amount_float, width=40)
        reserve_amount_entry.grid(row=2, sticky=S)
        reserve_amount_entry.grid_configure(padx=get_padx(self.reserve_token_form_frame, reserve_amount_entry),
                                         pady=(0, int(self.reserve_token_form_frame.winfo_height() * 0.05)))

        # insert Fee Label and Entry

        reserve_amount_fee_text = "Fee. min 1:"
        reserve_amount_fee_label = ttk.Label(self.reserve_token_form_frame, text=reserve_amount_fee_text, background="#181e23",
                                             foreground="#c2c5ce", font=form_label_font)
        reserve_amount_fee_label.grid(row=3, sticky=N)
        reserve_amount_fee_label.grid_configure(padx=get_padx(self.reserve_token_form_frame, reserve_amount_fee_label))

        reserve_amount_fee_entry = ttk.Entry(self.reserve_token_form_frame, textvariable=self.reserve_amount_fee_float,
                                             width=40)
        reserve_amount_fee_entry.grid(row=4, sticky=S)
        reserve_amount_fee_entry.grid_configure(padx=get_padx(self.reserve_token_form_frame, reserve_amount_fee_entry),
                                                pady=(0, int(self.reserve_token_form_frame.winfo_height() * 0.05)))

        # insert Reserve length

        reserve_len_text = "Duration: "
        reserve_len_label = ttk.Label(self.reserve_token_form_frame, text=reserve_len_text, background="#181e23",
                                             foreground="#c2c5ce", font=form_label_font)
        reserve_len_label.grid(row=5, sticky=N)
        reserve_len_label.grid_configure(padx=get_padx(self.reserve_token_form_frame, reserve_len_label))

        reserve_len_entry = ttk.Entry(self.reserve_token_form_frame, textvariable=self.reserve_length_float,
                                             width=40)
        reserve_len_entry.grid(row=6, sticky=S)
        reserve_len_entry.grid_configure(padx=get_padx(self.reserve_token_form_frame, reserve_len_entry),
                                                pady=(0, int(self.reserve_token_form_frame.winfo_height() * 0.05)))

        # insert wallet password label AND entry
        password_label = ttk.Label(self.reserve_token_form_frame, text="Wallet Password:", background="#181e23",
                                   foreground="#c2c5ce", font=form_label_font)
        password_label.grid(row=7, sticky=N)
        password_label.grid_configure(padx=get_padx(self.reserve_token_form_frame, password_label))

        password_entry =ttk.Entry(self.reserve_token_form_frame, textvariable=self.reserve_wallet_password_text, width=40,
                                  takefocus=False, show="*")
        password_entry.grid(row=8, sticky=S)
        password_entry.grid_configure(padx=get_padx(self.reserve_token_form_frame, password_entry),
                                      pady=(0,int(self.reserve_token_form_frame.winfo_height() * 0.05)))



        # insert cancel and submit buttons first
        cancel_submit_frame = ttk.Frame(self.reserve_token_form_frame, style="middle.TFrame",
                                        width=int(self.reserve_token_form_frame.winfo_width()*0.39), height=27, relief="sunken")
        cancel_submit_frame.grid(row=9)
        cancel_submit_frame.grid_propagate(False)
        root.update()  # call this to update event loop of cancel_submit_frame new width and height
        cancel_submit_frame.grid_configure(
            padx=int((self.reserve_token_form_frame.winfo_width() - cancel_submit_frame.winfo_width())/2),
            pady=int(self.reserve_token_form_frame.winfo_height()*.025)
        )
        cancel_submit_frame.columnconfigure(0, weight=1)
        cancel_submit_frame.columnconfigure(1, weight=1)

        # insert cancel button
        cancel_button_width = int(self.reserve_token_form_frame.winfo_width()*0.015)
        cancel_button = ttk.Button(cancel_submit_frame, text="CANCEL", width=cancel_button_width,
                                   command=lambda: (self.reserve_token_form_frame.destroy(), self.wallet_address_text.set(""),
                                                    self.reserve_amount_float.set(0.0),
                                                    self.reserve_amount_fee_float.set(0.0),
                                                    self.reserve_length_float.set(0.0),
                                                    self.wallet_password_text.set("")),
                                   style="cancel.TButton")
        cancel_button.grid(row=0, column=0, sticky=W)

        # create reserve label, but only added to grid when submit button pressed
        reserving_label = ttk.Label(self.reserve_token_form_frame, text="Broadcasting To Network....Please Wait", background="#181e23",
                                    foreground="#c2c5ce", font=form_label_font)
        submit_button = None
        submit_button = ttk.Button(
            cancel_submit_frame,
            text="SEND",
            width=cancel_button_width,
            command=lambda: (submit_button.state(["disabled"]), reserve_tokens(self.reserve_amount_float.get(), self.reserve_amount_fee_float.get(), self.reserve_wallet_password_text.get(), self.reserve_length_float.get(), self.reserve_token_network_response),
                             reserving_label.grid(row=10, sticky=N), root.update(),reserving_label.grid_configure(padx=get_padx(self.send_token_form_frame, reserving_label))),
            default="active",
            style="submit.TButton"
        )
        submit_button.grid(row=0, column=1, sticky=E)
        self.top_window.bind('<Return>', lambda event: submit_button.invoke())
        self.top_window.bind('<KP_Enter>', lambda event: submit_button.invoke())



class ButtonLikeCanvas(Canvas):
    """
    use this class to create buttons from canvas
    """

    def __init__(self, master, text=None, command=None, padx=None, pady=None, image=None, color=None,
                 c_width=None, c_height=None, borderwidth=0, relief=None, **kw):

        super().__init__(master, **kw)
        assert isinstance(master, (Canvas, ttk.Frame, Frame, Toplevel, Tk)), "not proper master"
        self["width"] = int(master.winfo_width()/4) if not c_width else c_width

        self["height"] = int(master.winfo_width()/4) if not c_height else c_height

        self["relief"] = relief if relief else "flat"
        self["background"] = "#2d3e4c" if color is None else color
        self["borderwidth"] = borderwidth
        self["highlightthickness"] = 0
        self["highlightcolor"] = color if color else self["highlightcolor"]

        self.padx = padx if padx else int((master.winfo_width())/8)
        self.pady = pady if pady else int(master.winfo_height()/8)
        self.grid_configure(padx=self.padx, pady=self.pady)

        self.middle_of_canvas = (int(int(self["width"]) / 2), int(int(self["height"])/2))

        self.text = text
        self.image = image
        self.text_id = self.create_text(
            90,
            80,
            text=text,
            justify=CENTER,
            anchor=CENTER,
            font=font.Font(family="Times", size=13, weight="normal"),
            fill="white"
        ) if self.text else None

        self.image_id = self.create_image(self.middle_of_canvas[0], self.middle_of_canvas[1], image=image, anchor=CENTER)

        self.line_coord = self.bbox(self.text_id) if self.text_id else None
        self.line_id = self.create_line(self.line_coord[0], self.line_coord[3]+2, self.line_coord[2], self.line_coord[3]+2,
                                        fill="#42a1f4", width=3) if self.line_coord else None
        self.command = command

        self.bind("<Button-1>", self.__pressed)
        self.bind("<ButtonRelease-1>", lambda e: root.after(250, self.__pressed_released, e))
        self.bind("<Enter>", self._entered_canvas)
        self.bind("<Leave>", self._left_canvas)


    def __pressed(self, event):

        print(self["relief"], "\n", event, self.text_id, self.bbox(self.text_id)) if self.text_id else None
        self["relief"] = "sunken"
        # print(self.bbox(1))
        self.move(self.text_id, 1, 1) if self.text_id else None  # used to moved create_text id right and down 1 pixel (simulates button moving)
        self.move(self.line_id, 1, 1) if self.line_id else None
        self.move(self.image_id, 1, 1) if self.image_id else None

    def __pressed_released(self, event):

        print("button released", "\n", event)
        self["relief"] = "raised"
        # print(self.bbox(1))
        self.move(self.text_id, -1, -1) if self.text_id else None # used to moved create_text id left and up 1 pixel (simulates button moving)
        self.move(self.line_id, -1, -1) if self.line_id else None
        self.move(self.image_id, -1, -1) if self.image_id else None
        if callable(self.command):
            self.command()
        elif isinstance(self.command, list) and len(self.command) > 1 and callable(self.command[0]):

            command_string = f'{self.command[0].__name__}('
            for i in self.command[1:]:
                command_string += f'{i},'
            command_string += ")"

            eval(command_string)
        else:
            print("command argument must be a callable ie. function OR List with [callable, arguments]\n------\n")

    def _entered_canvas(self, event):
        print('mouse entered', "\n", event)
        self.itemconfig(self.line_id, width=5)
        print(client_wallet)
        print(vars(client_user)) if client_user else print(client_user)
        print()
        print(vars(client_user.wallet_service_instance))

    def _left_canvas(self, event):
        print("mouse left", '\n', event)
        self.itemconfig(self.line_id, width=3)


class FrameWithGeneratorRows(ttk.Frame):
    """
    frame automatically generates the proper next row number
    Use if you are adding widgets into frame sequentially.
    """
    def __init__(self, master, **kw):
        super().__init__(master, **kw)

        self.current_row = generate_row_number()

    def next_row(self):

        return next(self.current_row)







"""  Beginning Of Program"""

root = Tk()

root.title("Orses Network Wallet Client")


""" 
Styles Declarations 

"""

ttk_style = ttk.Style()
ttk_style.configure("top.TFrame", background="#36444f", foreground="black")
ttk_style.configure("lower.TFrame", background="#20262b", foreground="black")
ttk_style.configure("left.TFrame", background="#303335")
ttk_style.configure("sidelabelmenu.TFrame", background="#242728")
ttk_style.configure("middle.TFrame", background="#181e23", foreground="black")
ttk_style.configure("middle1.TFrame", background="white", foreground="black")
ttk_style.configure("right.TFrame", background="#101519")

ttk_style.configure("login.TButton", background="#36444f", foreground="#c2c5ce", font=("Times", 16, "bold"))
ttk_style.configure("cancel.TButton", background="#E1524A", foreground="black", font=("Courier", 16, "bold"))
ttk_style.configure("logout.TButton", background="#3f5ac6", foreground="black",
                    font=("Courier", 16, "bold"))
ttk_style.configure("submit.TButton", background="#43A26E", foreground="black", font=("Courier", 16, "bold"))

ttk_style.configure("link.TButton", background="#303335", foreground="#c2c5ce",
                    font=("Courier", 16, "bold"), relief="flat")
ttk_style.map(
    "link.TButton",
    background=[
        ('active', '#181e23'),
        ('focus', '#181e23')
    ]

)
ttk_style.configure("middle.TNotebook", background='#181e23', foreground="#c2c5ce")
ttk_style.configure("middle.TNotebook.Tab", background="#263038",foreground="#c2c5ce", font=("Times", 12, "normal"))
ttk_style.map(
    "middle.TNotebook.Tab",
    background=[

        ('active', "#181e23"),
        ('background', "#181e23"),
        ('selected', '#181e23'),
        ('focus', "#181e23"),
        ('invalid', "#181e23")
    ]

)
ttk_style.configure("welcome.TLabel", background="#181e23", foreground="#c2c5ce")
ttk_style.configure("welcome.TEntry", background="#181e23", foreground="#c2c5ce", fieldbackground="#181e23",
                    font=font.Font(family="Times", size=64, weight="bold",))



"""
Font Declarations
"""
welcome_font = font.Font(family="Times", size=18, weight="bold", underline=True)

print(font.families())

form_label_font = font.Font(family="Times", size=14, weight="bold", underline=True)
main_menu_top_label = font.Font(family="Times", size=12, weight="bold", )
notif_label_font = font.Font(family="Times", size=16, weight="normal")
menu_header_label_font = font.Font(family="Times", size=20, weight="normal")
welcome_label_font = font.Font(family="courier", size=20, weight="normal",)
connection_top_label = font.Font(family="Times", size=9, weight="normal")





"""
Determine Screen Size
"""
screen_width = root.winfo_screenwidth()
screen_heigth = root.winfo_screenheight()
if screen_width > 1366:
    screen_width = 1366
if screen_heigth > 768:
    screen_heigth= 768

login_frame_width = int(screen_width/2)
login_frame_height = int(screen_heigth/2)
main_width = int(screen_width/1.25)
main_height = int(screen_heigth /1.25)


"""
Set Root Geometry: (size of main window and position it opens up
"""
root.geometry("{}x{}+{}+{}".format(login_frame_width, login_frame_height,
                                   int((screen_width / 2) - (login_frame_width / 2)),
                                   int((screen_heigth/2) - (login_frame_height / 2))))




"""
Create A Main Frame which is called login_frame
"""
login_frame = ttk.Frame(root, width=login_frame_width, height=login_frame_height)
login_frame.grid(column=0, row=0, sticky=(N, S, E, W))
# root.columnconfigure(0, weight=1)
# root.rowconfigure(0, weight=1)


"""
*** Top Frame ***
"""
top_frame = ttk.Frame(login_frame, width=login_frame_width, height=int(login_frame_height*0.20), style="top.TFrame")
top_frame.grid(column=0, row=0, sticky=(N, S, E, W))
# setting grid_propagate(False) to False, stops Parent Frame from resizing to widgets in it.
top_frame.grid_propagate(False)
# rowconfigure and columnconfigure are used to determine minsize, weight(for window resizing) and pad (space within row)
login_frame.rowconfigure(0, weight=1)
login_frame.columnconfigure(0, weight=1)

"""
*** Lower Frame
"""
lower_frame= ttk.Frame(login_frame, width=login_frame_width, height=int(login_frame_height*0.81), style="lower.TFrame")
lower_frame.grid(column=0, row=1, sticky=(N, S, E, W))
lower_frame.grid_propagate(False)
login_frame.rowconfigure(1, weight=10)

"""
*** Top Frame Widgets
"""

# top frame widgets

# logo Image
image1 = Image.open("fullLogo.png")
image1 = image1.resize((int(login_frame_width/4), int(login_frame_height*0.2)), Image.ANTIALIAS)
logo_image = ImageTk.PhotoImage(image1)

welcome_label = ttk.Label(top_frame, image=logo_image, background="#36444f", foreground="white", font=welcome_font)
welcome_label.grid(column=0, row=0, sticky=(W,N,S))
welcome_label.grid_configure(padx=int(login_frame_width*0.35))
top_frame.rowconfigure(0, weight=1)


"""
*** Lower Frame Widgets
"""
button_padx = (int(login_frame_width*0.33), 0)
button_width = int(login_frame_width*0.03)
create_user_button = ttk.Button(lower_frame, text="Create A User", command=OrsesCommands.create_user,
                                style="login.TButton", width=button_width)
create_user_button.grid(column=0, row=1,)
create_user_button.grid_configure(padx=button_padx)
lower_frame.rowconfigure(1, weight=1)

login_user_button = ttk.Button(lower_frame, text="Load A User", command=OrsesCommands.load_user,
                               style="login.TButton", width=button_width)
login_user_button.grid(column=0, row=2,)
login_user_button.grid_configure(padx=button_padx)
lower_frame.rowconfigure(2, weight=1)

import_user_button = ttk.Button(lower_frame, text="Import A User", command=OrsesCommands.import_user,
                                style="login.TButton", width=button_width)
import_user_button.grid(column=0, row=3,)
import_user_button.grid_configure(padx=button_padx)
lower_frame.rowconfigure(3, weight=1)

export_user_button = ttk.Button(lower_frame, text="Export A User", command=OrsesCommands.export_user,
                                style="login.TButton", width=button_width)
export_user_button.grid(column=0, row=4,)
export_user_button.grid_configure(padx=button_padx)
lower_frame.rowconfigure(4, weight=1)


exit_button = ttk.Button(lower_frame, text="Exit Client", command=OrsesCommands.exit_program,
                         style="login.TButton", width=button_width)
exit_button.grid(column=0, row=5,)
exit_button.grid_configure(padx=button_padx)
lower_frame.rowconfigure(5, weight=1)

# self.logo_image = image2.resize((int(self.top_frame.winfo_height()*0.85), int(self.top_frame_height*0.85)),
#                                 Image.ANTIALIAS)
clipboard_image = Image.open("copy_icon.png")
icon_photo = ImageTk.PhotoImage(Image.open("OLogo.png"))

try:
    root.resizable(False, False)
    # root.iconphoto(True, logo_image)
    root.iconphoto(True, icon_photo)
    # root.after(500, print, "test")
    tksupport.install(root)
    reactor.run()
except (SystemExit, KeyboardInterrupt):
    print("Program Ended")
    root.destroy()
    reactor.stop()

