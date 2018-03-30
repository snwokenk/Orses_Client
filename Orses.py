from tkinter import *
from tkinter import ttk
from tkinter import font
from PIL import Image, ImageTk

# TODO: after user successfully loaded or created, make main menu window appear

from Orses_User.User_CLI_Helper import UserCLI, User

windows_dict = dict()

client_user = None


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
            window_inst.insert_notification_label(text=valid_text, font_class=notif_label_font,
                                                  text_color="Green")
            for widgets in window_inst.mainframe_lower.grid_slaves():
                print(widgets)

        elif client_user is False:
            # password and password retype != password

            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "Passwords Do Not Match!"
            window_inst.insert_notification_label(text=valid_text, font_class=notif_label_font,
                                                  text_color="Red")
        elif client_user is None:
            # user with username already exists
            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "'{}' Already Exists On Local Machine!".format(username)
            window_inst.insert_notification_label(text=valid_text, font_class=notif_label_font,
                                                  text_color="red")


    @staticmethod
    def load_user(password, username, window_inst):
        global client_user
        client_user = UserCLI.load_user(password=password, username=username)

        if client_user:

            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "Success!\n'{}' Loaded On Local Machine!\nClient ID:\n{}".format(client_user.username,
                                                                                           client_user.client_id)
            window_inst.insert_notification_label(text=valid_text, font_class=notif_label_font,
                                                  text_color="Green")
            for widgets in window_inst.mainframe_lower.grid_slaves():
                print(widgets)

        elif client_user is False:
            # Wrong Password
            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "Wrong Password!"
            window_inst.insert_notification_label(text=valid_text, font_class=notif_label_font,
                                                  text_color="Red")
        elif client_user is None:
            # user with username already exists
            for widgets in window_inst.mainframe_lower.grid_slaves():
                widgets.grid_forget()
            valid_text = "'{}' Does Not Exist On Local Machine!".format(username)
            window_inst.insert_notification_label(text=valid_text, font_class=notif_label_font,
                                                  text_color="red")

    def launch_main_menu(self):
        pass



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
                                        state=button_state)
        self.submit_button.grid(row=0, column=1, sticky=E)

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
        print(notif_label.winfo_width())


        continue_button = ttk.Button(self.mainframe_lower, text="CONTINUE", width=continue_button_width,
                                   command=command_callback, style="cancel.TButton")
        continue_button.grid(row=10, sticky=(N,S))
        continue_button.grid_configure(padx=notif_padx, pady=notif_pady)


class BaseLoggedInWindow(Toplevel):
    """
    class holding window when logged into a user/wallet. Main Menu Window
    """
    def __init__(self, master, title, **kw):
        super().__init__(master, **kw)
        self.main_width = int(screen_width/1.25)
        self.main_height = int(screen_heigth /1.25)
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

        # middle frame
        self.middle_frame_width = int(self.main_width*0.60)
        self.middle_frame_height = self.main_height
        self.middle_frame = ttk.Frame(self.mainframe, width=self.middle_frame_width, height=self.middle_frame_height,
                                 relief="sunken", style="middle.TFrame")
        self.middle_frame.grid(column=1, row=0, sticky=(W,N,S,E))
        self.middle_frame.grid_propagate(False)

        # right frame
        self.right_frame_width = int(self.main_width*0.20)
        self.right_frame_height = self.main_height
        self.right_frame = ttk.Frame(self.mainframe, width=self.right_frame_width, height=self.right_frame_height,
                                     style="right.TFrame")
        self.right_frame.grid(column=2, row=0, sticky=(E, N, S))
        self.right_frame.grid_propagate(False)


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
ttk_style.configure("middle.TFrame", background="#181e23", foreground="black")
ttk_style.configure("right.TFrame", background="#101519")

ttk_style.configure("login.TButton", background="#36444f", foreground="white", font=font.Font(family="Times", size=6))
ttk_style.configure("cancel.TButton", background="#E1524A", foreground="black", font=font.Font(family="Times", size=12,
                                                                                               weight="bold"))
ttk_style.configure("submit.TButton", background="#43A26E", foreground="black", font=font.Font(family="Times", size=12,
                                                                                               weight="bold"))


"""
Font Declarations
"""
welcome_font = font.Font(family="clearlyu devanagari", size=24, weight="bold", underline=True)
print(font.families())

form_label_font = font.Font(family="fixed", size=16, weight="normal", underline=True)
notif_label_font = font.Font(family="fixed", size=16, weight="normal")


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

    root.mainloop()
except SystemExit:
    print("here")
    root.destroy()

