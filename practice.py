from PIL import Image, ImageFont, ImageDraw, ImageTk

import textwrap

from tkinter import ttk
Label = ttk.Label

def truetype_font(font_path, size):
    return ImageFont.truetype(font_path, size)

class CustomFont_Label(Label):
    def __init__(self, master, text, foreground="black", truetype_font=None, font_path=None, family=None, size=None, **kwargs):
        if truetype_font is None:
            if font_path is None:
                raise ValueError("Font path can't be None")

            # Initialize font
            truetype_font = ImageFont.truetype(font_path, size)

        width, height = truetype_font.getsize(text)

        image = Image.new("RGBA", (width, height), color=(0,0,0,0))
        draw = ImageDraw.Draw(image)

        draw.text((0, 0), text, font=truetype_font, fill=foreground)

        self._photoimage = ImageTk.PhotoImage(image)
        Label.__init__(self, master, image=self._photoimage, **kwargs)


class CustomFont_Message(Label):
    def __init__(self, master, text, width, foreground="#c2c5ce", truetype_font=None, font_path=None, family=None, size=None, **kwargs):
        if truetype_font is None:
            if font_path is None:
                raise ValueError("Font path can't be None")

            # Initialize font
            truetype_font = ImageFont.truetype(font_path, size)

        lines = textwrap.wrap(text, width=width)

        width = 0
        height = 0

        line_heights = []
        for line in lines:
            line_width, line_height = truetype_font.getsize(line)
            line_heights.append(line_height)

            width = max(width, line_width)
            height += line_height

        image = Image.new("RGBA", (width, height), color=(0,0,0,0))
        draw = ImageDraw.Draw(image)

        y_text = 0
        for i, line in enumerate(lines):
            draw.text((0, y_text), line, font=truetype_font, fill=foreground)
            y_text += line_heights[i]

        self._photoimage = ImageTk.PhotoImage(image)
        Label.__init__(self, master, image=self._photoimage, **kwargs)

if __name__ == "__main__":
    try:
        from Tkinter import Tk
    except ImportError:
        from tkinter import Tk

    root = Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h))

    lorem_ipsum ="""Lorem ipsum dolor sit amet, 
consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore 
magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation 
ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril 
delenit augue duis dolore te feugait nulla facilisi."""

    # Use your font here: font_path
    CustomFont_Label(root, text="Load A Wallet", font_path="OpenSans-Regular.ttf", size=40).pack()
    CustomFont_Message(root, text=lorem_ipsum, width=40, font_path="OpenSans-Regular.ttf", size=22, background="black").pack(pady=(30,0))

    root.mainloop()



# from tkinter import *
# from tkinter import ttk
# import copy
#
#
# # https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens
#
#
# root = Tk()
# root.title("Orses Network Client")
#
# # gets the screen sizes
# screen_width = root.winfo_screenwidth()
# screen_heigth = root.winfo_screenheight()
# if screen_width > 1366:
#     screen_width = 1366
# if screen_heigth > 768:
#     screen_heigth= 768
#
# main_width = int(screen_width/1.25)
# main_height = int(screen_heigth /1.25)
#
# # root.geometry "widthXheight+X_axis+Y_axis"
# root.geometry("{}x{}+{}+{}".format(main_width, main_height, int((screen_width / 2) - (main_width / 2)),
#                                    int((screen_heigth/2) - (main_height / 2))))
#
# # use this to create custom styles for widgets
# ttk_style = ttk.Style()
#
#
# """
# *** Create Frames ***
# """
# # left frame
# ttk_style.configure("left.TFrame", background="#303335")
# left_frame_width = int(main_width*0.20)
# left_frame_height = main_height
# left_frame = ttk.Frame(root, width=left_frame_width, height=left_frame_height, style="left.TFrame")
# left_frame.grid(column=0, row=0, sticky=(W, N, S))
# # middle frame
# ttk_style.configure("middle.TFrame", background="#181e23", foreground="black")
# middle_frame_width = int(main_width*0.60)
# middle_frame_height = main_height
# middle_frame = ttk.Frame(root, width=middle_frame_width, height=middle_frame_height, relief="sunken",
#                          style="middle.TFrame")
# middle_frame.grid(column=1, row=0, sticky=(W,N,S,E))
#
# # right frame
# ttk_style.configure("right.TFrame", background="#101519")
# right_frame_width = int(main_width*0.20)
# right_frame_height = main_height
# right_frame = ttk.Frame(root, width=right_frame_width, height=right_frame_height, style="right.TFrame")
# right_frame.grid(column=2, row=0, sticky=(E, N, S))
#
# """
# *** Create Widgets For Left Frame
# """
#
#
# root.mainloop()