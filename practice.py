from tkinter import *
from tkinter import ttk
import copy


# https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens


root = Tk()
root.title("Orses Network Client")

# gets the screen sizes
screen_width = root.winfo_screenwidth()
screen_heigth = root.winfo_screenheight()
if screen_width > 1366:
    screen_width = 1366
if screen_heigth > 768:
    screen_heigth= 768

main_width = int(screen_width/1.25)
main_height = int(screen_heigth /1.25)

# root.geometry "widthXheight+X_axis+Y_axis"
root.geometry("{}x{}+{}+{}".format(main_width, main_height, int((screen_width / 2) - (main_width / 2)),
                                   int((screen_heigth/2) - (main_height / 2))))

# use this to create custom styles for widgets
ttk_style = ttk.Style()


"""
*** Create Frames ***
"""
# left frame
ttk_style.configure("left.TFrame", background="#303335")
left_frame_width = int(main_width*0.20)
left_frame_height = main_height
left_frame = ttk.Frame(root, width=left_frame_width, height=left_frame_height, style="left.TFrame")
left_frame.grid(column=0, row=0, sticky=(W, N, S))
# middle frame
ttk_style.configure("middle.TFrame", background="#181e23", foreground="black")
middle_frame_width = int(main_width*0.60)
middle_frame_height = main_height
middle_frame = ttk.Frame(root, width=middle_frame_width, height=middle_frame_height, relief="sunken",
                         style="middle.TFrame")
middle_frame.grid(column=1, row=0, sticky=(W,N,S,E))

# right frame
ttk_style.configure("right.TFrame", background="#101519")
right_frame_width = int(main_width*0.20)
right_frame_height = main_height
right_frame = ttk.Frame(root, width=right_frame_width, height=right_frame_height, style="right.TFrame")
right_frame.grid(column=2, row=0, sticky=(E, N, S))

"""
*** Create Widgets For Left Frame
"""


root.mainloop()