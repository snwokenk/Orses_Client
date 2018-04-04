from tkinter import *
from tkinter import ttk
from tkinter import font
from PIL import Image, ImageTk

# https://stackoverflow.com/questions/17635905/ttk-entry-background-colour/17639955
# TODO: after user successfully loaded or created, make main menu window appear

from Orses_User.User_CLI_Helper import UserCLI, User

def change_user(new_val):
    global client_user
    client_user = new_val


def change_wallet(new_val):
    global client_wallet
    client_wallet = new_val

# these variables will hold a successfully loaded user object and wallet object
client_user = None
client_wallet = None

# dictionary to hold windows (if necessary)
windows_dict = dict()

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
            for widgets in window_inst.mainframe_lower.grid_slaves():
                print(widgets)

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
            for widgets in window_inst.mainframe_lower.grid_slaves():
                print(widgets)

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
    def launch_main_menu(user, window_inst):
        """
        Used to launch window if user successfully loaded/created/imported
        Otherwise go backs to Load User Window
        :param user: user object (if created/loaded/imported successfully) else False or None
        :param window_inst: instance of form window
        :return:
        """

        print("I'm here")

        if user:
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
        print("User Exported")
        export_user_window = BaseFormWindow(root, title="Orses Wallet Client: Export A User")
        windows_dict["export_user"] = export_user_window

        # row 0 Header "Create User" (should be space below, and Create User Underlined
        export_user_window.insert_header_title(title="Export A User", font_class=welcome_font)

    @staticmethod
    def import_user():
        print("User Imported")
        import_user_window = BaseFormWindow(root, title="Orses Wallet Client: Import A User")
        windows_dict["import_user"] = import_user_window

        # row 0 Header "Create User" (should be space below, and Create User Underlined
        import_user_window.insert_header_title(title="Import A User", font_class=welcome_font)

    @staticmethod
    def enable_submit(**kw):

        if len(kw["password1"]) > 0 and len(kw["password"]) >= 8 and \
                (kw["username"] and kw["username"] != "Enter Username"):
            kw["button_instance"].state(['!disabled'])
            return 1
        else:
            return 1


    @staticmethod
    def exit_program():
        root.destroy()
        pass


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
        self.mainframe_lower = ttk.Frame(self.mainframe, width=self.form_window_width,
                                         height=self.mainframe_lower_height, style="lower.TFrame")
        self.mainframe_lower.grid(column=0, row=1, sticky=(N, S, E, W))
        self.mainframe_lower.grid_propagate(False)
        self.rowconfigure(1, weight=1)

        # Entry Text
        self.username_text = StringVar(value="")
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

    def insert_header_title(self, title, font_class, background_color="#20262b", text_color="white"):

        header_padx = (int(self.form_window_width*0.31), 0)
        header_pady = (int(self.mainframe_lower_height*0.01),
                       int(self.mainframe_lower_height*0.05))
        header_label = ttk.Label(self.mainframe_lower, text=title, background=background_color,
                                 foreground=text_color, font=font_class)
        header_label.grid(row=0, sticky=N)
        header_label.grid_configure(padx=header_padx, pady=header_pady)

    def insert_username(self, font_class, label_text="username:", background_color="#20262b", text_color="white"):

        username_label = ttk.Label(self.mainframe_lower, text=label_text, background=background_color,
                                   foreground=text_color, font=font_class)
        username_label.grid(row=1, sticky=N)
        username_label.grid_configure(padx=self.entry_padx)

        username_entry =ttk.Entry(self.mainframe_lower, textvariable=self.username_text, width=36, takefocus=True)
        username_entry.grid(row=2, sticky=S)
        username_entry.grid_configure(padx=self.entry_padx, pady=self.entry_pady)
        username_entry.focus()

    def insert_password(self, font_class,label_text="Password:", background_color="#20262b", text_color="white"):

        password_label = ttk.Label(self.mainframe_lower, text=label_text, background=background_color,
                                   foreground=text_color, font=font_class)
        password_label.grid(row=3, sticky=N)
        password_label.grid_configure(padx=self.entry_padx)

        password_entry =ttk.Entry(self.mainframe_lower, textvariable=self.password_text, width=36, show="*")
        password_entry.grid(row=4, sticky=S)
        password_entry.grid_configure(padx=self.entry_padx, pady=self.entry_pady)

    def insert_password_again(self, font_class,label_text="Re-enter Password:", background_color="#20262b",
                              text_color="white"):

        password_label = ttk.Label(self.mainframe_lower, text=label_text, background=background_color,
                                   foreground=text_color, font=font_class)
        password_label.grid(row=5, sticky=N)
        password_label.grid_configure(padx=self.entry_padx)

        password_entry =ttk.Entry(
            self.mainframe_lower, textvariable=self.password1_text, width=36, show="*", validate="key",
            validatecommand=lambda: OrsesCommands.enable_submit(password=self.password_text.get(),
                                                                password1=self.password1_text.get(),
                                                                username=self.username_text,
                                                                button_instance=self.submit_button)
        )
        password_entry.grid(row=6, sticky=S)
        password_entry.grid_configure(padx=self.entry_padx, pady=self.entry_pady)

        print(password_entry["width"])

    def insert_cancel_submit_buttons(self, command_callback, submit_text="SUBMIT", button_state="disabled"):

        # frame for cancel and submit button
        cancel_submit_frame_width = int(self.form_window_width*0.38)
        cancel_submit_frame_height = 27
        cancel_submit_frame_pady = (int(self.mainframe_lower_height*0.025), 0)

        cancel_submit_frame = ttk.Frame(self.mainframe_lower, style="lower.TFrame", width=cancel_submit_frame_width,
                                        height=cancel_submit_frame_height, relief="sunken")
        cancel_submit_frame.grid(row=7, sticky=S)
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
        notif_label.grid(row=9, sticky=N)
        notif_label.grid_configure(padx=notif_padx, pady=notif_pady)

        continue_button = ttk.Button(self.mainframe_lower, text="CONTINUE", width=continue_button_width,
                                   command=command_callback, style="cancel.TButton", default="active")
        continue_button.grid(row=10, sticky=(N,S))
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
            command=root.destroy,
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
                                      background="#242728", foreground="white")
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
                             command=lambda: self.add_welcome_frame_to_notebook_widget(), text="Create A Wallet",
                             master_height=left_frame_top__mid_height)
        self.insert_btn_link(left_frame_top_mid, row=3, column=0, width=link_btn_width,
                             command=lambda: print("Pushed"), text="Load A Wallet",
                             master_height=left_frame_top__mid_height)
        self.insert_btn_link(left_frame_top_mid, row=4, column=0, width=link_btn_width,
                             command=lambda: print("Pushed"), text="List Owned Wallets",
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
                                      background="#242728", foreground="white")
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
        link_button = ttk.Button(master, width=width, text=text, command=command, style="link.TButton")
        link_button.grid(row=row, column=column, sticky=(E, W))


        link_button.grid_configure(pady=(int(master_height*.10), 0))

    def insert_notebook_widget(self):

        self.notebookwidget = ttk.Notebook(self.middle_frame, style="middle.TNotebook")
        self.notebookwidget.grid(row=0)

    def add_welcome_frame_to_notebook_widget(self):

        self.welcome_frame = ttk.Frame(self.notebookwidget, style="middle.TFrame", width=self.middle_frame_width,
                                       height=self.middle_frame_height)
        self.welcome_frame.grid_propagate(False)
        self.notebookwidget.add(self.welcome_frame, text="Welcome")

    def add_welcome_widgets_to_welcome_frame(self):
        # add a welcome label text

        welcome_label = ttk.Label(self.welcome_frame, text="Welcome To The\nOrses Network Wallet Client\n\nClient ID: ",
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
                                    font=font.Font(family="Times", size=24, weight="bold",))
        client_id_entry.grid(row=2, column=0)

    def add_wallet_creation_frame(self):

        self.wallet_creation_frame = ttk.Frame(
            self.notebookwidget,
            style="middle.TFrame",
            width=self.middle_frame_width,
            height=self.middle_frame_height
        )
        self.welcome_frame.grid_propagate(False)
        self.notebookwidget.add(self.welcome_frame, text="Create A Wallet")





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

ttk_style.configure("login.TButton", background="#36444f", foreground="white", font=font.Font(family="Times", size=6))
ttk_style.configure("cancel.TButton", background="#E1524A", foreground="black", font=font.Font(family="Times", size=12,
                                                                                               weight="bold"))
ttk_style.configure("logout.TButton", background="#3f5ac6", foreground="black",
                    font=font.Font(family="Times", size=12, weight="bold"))
ttk_style.configure("submit.TButton", background="#43A26E", foreground="black", font=font.Font(family="Times", size=12,
                                                                                               weight="bold"))

ttk_style.configure("link.TButton", background="#303335", foreground="white",
                    font=font.Font(family="Times", size=14, weight="bold"), relief="flat")
ttk_style.map(
    "link.TButton",
    background=[
        ('active', '#181e23'),
        ('focus', '#181e23')
    ]

)
ttk_style.configure("middle.TNotebook", background='#181e23', foreground="white",
                    font=font.Font(family="Times", size=120, weight="bold"))
ttk_style.configure("middle.TNotebook.Tab", background='white', foreground="black",
                    font=font.Font(family="Times", size=120, weight="bold"))
ttk_style.configure("welcome.TLabel", background="#181e23", foreground="white")
ttk_style.configure("welcome.TEntry", background="#181e23", foreground="white", fieldbackground="#181e23",
                    font=font.Font(family="Times", size=32, weight="bold",))



"""
Font Declarations
"""
welcome_font = font.Font(family="clearlyu devanagari", size=24, weight="bold", underline=True)
print(font.families())

form_label_font = font.Font(family="fixed", size=16, weight="normal", underline=True)
notif_label_font = font.Font(family="fixed", size=16, weight="normal")
menu_header_label_font = font.Font(family="song ti", size=24, weight="normal")
welcome_label_font = font.Font(family="Times", size=32, weight="bold",)



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
image1 = Image.open("Orses.png")
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

try:
    root.resizable(False, False)
    root.iconphoto(True, logo_image)
    root.mainloop()
except SystemExit:
    print("here")
    root.destroy()

