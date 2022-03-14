from PIL import ImageTk
from tkinter import Button, PhotoImage, messagebox as mbox

from functools import partial


class ButtonFactory:
    def createButton(self, type_):
        return buttonTypes[type_]()


class ButtonBase:
    relx = 0.0
    rely = 0.0
    height = 50
    width = 50
    background = "black"
    text = "Test"

    def getButtonConfig(self):
        return (
            self.relx,
            self.rely,
            self.height,
            self.width,
            self.background,
            self.text,
        )


class ButtonLoadMosaic(ButtonBase):
    relx = 0.72
    rely = 0.52
    height = 28
    width = 123
    background = "black"
    text = "Mosaico"


class ButtonShape(ButtonBase):
    relx = 0.72
    rely = 0.60
    height = 28
    width = 123
    background = "black"
    text = "Shape"


class ButtonStart(ButtonBase):
    relx = 0.742
    rely = 0.871
    height = 48
    width = 123
    background = "black"
    text = "Iniciar"


buttonTypes = [ButtonLoadMosaic, ButtonShape, ButtonStart]


class ButtonSettingsLabelling:
    def __init__(self, root, tk_menu):
        self.root = root
        self.tk_menu = tk_menu

    def settings_labelling_menu(self):
        self.btn_load_mosaico = self.tk_menu.Button(self.root)
        self.btn_shape_reference = self.tk_menu.Button(self.root)
        self.btn_start = self.tk_menu.Button(self.root)
        option_buttons = [self.btn_load_mosaico, self.btn_shape_reference, self.btn_start]
        factory = ButtonFactory()

        for i in range(len(buttonTypes)):
            relx = factory.createButton(i).getButtonConfig()[0]
            rely = factory.createButton(i).getButtonConfig()[1]
            height = factory.createButton(i).getButtonConfig()[2]
            width = factory.createButton(i).getButtonConfig()[3]
            text = factory.createButton(i).getButtonConfig()[5]
            option_buttons[i].place(relx=relx, rely=rely, height=height, width=width)
            option_buttons[i].configure(text=text)


class ButtonsLabelling:
    def __init__(self, root, tk_menu, frame):
        self.root = root
        self.tk_menu = tk_menu
        self.frame = frame

        self.color_buttons_center = "white"

    def button_start(self):

        self.pencil_icon = PhotoImage(file=r"../icons/pencil_black_white.png")
        self.pencil_icon = self.pencil_icon.subsample(2, 2)
        self.pencil_btn = self.tk_menu.Button(self.frame, image=self.pencil_icon)
        self.pencil_btn.place(relx=0.006, rely=0.004, height=43, width=43)
        self.pencil_btn.configure(borderwidth="2", text="Button", background=self.color_buttons_center)

        self.erase_icon = ImageTk.PhotoImage(file=r"../icons/eraser_black.png")
        self.erase_btn = self.tk_menu.Button(self.frame, image=self.erase_icon)
        self.erase_btn.place(relx=0.006, rely=0.135, height=43, width=43)
        self.erase_btn.configure(borderwidth="2", text="Button", background=self.color_buttons_center)

        self.polygon_icon = ImageTk.PhotoImage(file=r"../icons/polygon.png")
        self.polygon_btn = self.tk_menu.Button(self.frame, image=self.polygon_icon)
        self.polygon_btn.place(relx=0.006, rely=0.07, height=43, width=43)
        self.polygon_btn.configure(borderwidth="2", text="Button", background=self.color_buttons_center)

        self.hide_layer_icon = ImageTk.PhotoImage(file=r"../icons/hide_layer.png")
        self.hide_layer_btn = self.tk_menu.Button(self.frame, image=self.hide_layer_icon)
        self.hide_layer_btn.place(relx=0.006, rely=0.2, height=43, width=43)
        self.hide_layer_btn.configure(
            activebackground="#f9f9f9", borderwidth="2", text="Button", background=self.color_buttons_center
        )

        self.super_pixel_icon = ImageTk.PhotoImage(file=r"../icons/s_pixel.png")
        self.super_pixel_btn = self.tk_menu.Button(self.frame, image=self.super_pixel_icon)
        self.super_pixel_btn.place(relx=0.006, rely=0.265, height=43, width=43)
        self.super_pixel_btn.configure(
            activebackground="#f9f9f9", borderwidth="2", text="Button", background=self.color_buttons_center
        )

        self.next_icon = ImageTk.PhotoImage(file=r"../icons/next.png")
        self.next_btn = self.tk_menu.Button(self.root, image=self.next_icon)
        self.next_btn.place(relx=0.957, rely=0.43, height=70, width=43)
        self.next_btn.configure(borderwidth="2", background="white")

        self.back_icon = ImageTk.PhotoImage(file=r"../icons/back.png")
        self.back_btn = self.tk_menu.Button(self.root, image=self.back_icon)
        self.back_btn.place(relx=0.183, rely=0.43, height=70, width=43)
        self.back_btn.configure(borderwidth="2", background="white")


class ButtonFactory:
    def createButton(self, type_):
        return buttonTypes[type_]()


class ButtonBase:
    relief = "flat"
    foreground = "white"

    def getButtonConfig(self):
        return self.relief, self.foreground
