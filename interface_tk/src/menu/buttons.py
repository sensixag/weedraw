from PIL import ImageTk
from tkinter import Button, PhotoImage, messagebox as mbox

from functools import partial


class Buttons:
    def __init__(self, root, tk_menu, frame):
        self.root = root
        self.tk_menu = tk_menu
        self.frame = frame

        self.color_buttons_center = "white"

    def settings_labelling_menu(self):

        self.btn_load_mosaico = self.tk_menu.Button(self.root)
        self.btn_load_mosaico.place(relx=0.72, rely=0.52, height=28, width=123)
        self.btn_load_mosaico.configure(takefocus="")
        self.btn_load_mosaico.configure(text="Mosaico")
        self.btn_load_mosaico.bind("<Button-1>", partial(self.get_btn, key="0"))

        self.label2 = self.tk_menu.Label(self.root)
        self.label2.place(relx=0.11, rely=0.60, height=21, width=200)
        self.label2.configure(activebackground="#f9f9f9")
        self.label2.configure(text="Selecione o Shape de Base :")

        self.btn_shape_reference = self.tk_menu.Button(self.root)
        self.btn_shape_reference.place(relx=0.72, rely=0.60, height=28, width=123)
        self.btn_shape_reference.configure(takefocus="")
        self.btn_shape_reference.configure(text="Shape de Base")
        self.btn_shape_reference.bind("<Button-1>", partial(self.get_btn, key="3"))

        self.label3 = self.tk_menu.Label(self.root)
        self.label3.place(relx=0.117, rely=0.68, height=21, width=260)
        self.label3.configure(activebackground="#f9f9f9")
        self.label3.configure(text="Porcentagem de fundo preto permitida:")

        self.spinbox_backg = self.tk_menu.Spinbox(
            self.root, from_=5.0, to=100.0, increment=5, textvariable=self.spn_box_1
        )
        self.spinbox_backg.place(relx=0.63, rely=0.69, relheight=0.046, relwidth=0.243)
        self.spinbox_backg.configure(activebackground="#f9f9f9")
        self.spinbox_backg.configure(background="white")
        self.spinbox_backg.configure(font="TkDefaultFont")
        self.spinbox_backg.configure(highlightbackground="black")
        self.spinbox_backg.configure(selectbackground="blue")
        self.spinbox_backg.configure(selectforeground="white")
        self.spinbox_backg.configure(command=partial(self.get_values_spinbox, type="Efetuar Marcacoes em Ortomosaicos"))

        self.btn_start = self.tk_menu.Button(self.root)
        self.btn_start.place(relx=0.742, rely=0.871, height=48, width=123)
        self.btn_start.configure(takefocus="")
        self.btn_start.configure(text="Iniciar")
        self.btn_start.bind("<Button-1>", partial(self.get_btn, key="5"))

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
