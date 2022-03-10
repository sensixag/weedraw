from turtle import update
import numpy as np
import os
import pathlib
import PIL
import cv2
import sys
import imgaug as im

try:

    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk

    py3 = False
except ImportError:
    import tkinter.ttk as ttk

    py3 = True
    import shutil

from typing import Text
from functools import partial
from tkinter import PhotoImage, messagebox as mbox
from PIL import Image, ImageDraw, ImageTk
from tkinter import filedialog
from osgeo import gdal, ogr, osr
from neural import ImagesManipulations as imp
from imgs_manipulations import SatureImg


class Interface(tk.Frame):
    def __init__(self, root):

        tk.Frame.__init__(self, root)
        menubar = tk.Menu(self)
        fileMenu = tk.Menu(self)

        self.width_size = 800
        self.hight_size = 600
        self.x_crop = 0
        self.y_crop = 0
        self.iterator_x = 256
        self.iterator_y = 256

        self.screen_width = 800
        self.screen_height = 700

        self.count_img = 0
        self.count_feature = 0
        self.iterator_recoil = 1.0
        self.cnt_validator = []
        self.background_percent = 0.8
        self.array_clicks = []
        self.current_points = []
        self.current_points_bkp = []
        self.draw_lines_array = [[]]
        self.features_polygons = [[]]
        self.polygons_ids_array = []
        self.vertices_ids_array = []

        self.save_draw_array = None
        self.name_tif = ""
        self.name_reference_binary = ""
        self.name_reference_neural = ""
        self.slider_pencil = 10
        self.slider_saturation = 0
        self.slider_opacity = 50
        self.slider_contourn = 50
        self.color_frame_over_center = "black"
        self.pencil_draw_bool = True
        self.polygon_draw_bool = False
        self.super_pixel_bool = False
        self.opacity = False
        self.bool_draw = False
        self.use_neural_network = False
        self.path_save_img_rgb = "dataset/rgb"
        self.path_save_img_bin = "dataset/binario"
        self.path_save_img_negative = "dataset/negativos"
        self.directory_saved = ""
        self.frame_root = root
        self.color_line = 1
        self.color_line_rgb = (255, 0, 0)
        # Valores do color_map: BLACK, RED, GREEN, BLUE
        self.color_map = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)]

        root.maxsize(self.width_size, self.hight_size)
        root.resizable(False, False)

        self.f = {"Back": "0", "Next": "1"}
        self.first_click = False
        self.first_click_bool = False
        self.ready_start = False

        self.change_button = {}
        self.bool_value = tk.StringVar()
        self.spn_box_1 = tk.StringVar()
        self.spn_box_2 = tk.StringVar()
        self.spn_box_3 = tk.StringVar()

        self.current_value_saturation = tk.DoubleVar()
        self.current_value_contourn = tk.DoubleVar()
        self.current_value_opacity = tk.DoubleVar()
        self.btn_int = tk.IntVar()

        self.var = tk.IntVar()
        self.old_choose = ""
        self.OptionList = ["Efetuar Marcacoes em Ortomosaicos", "Efetuar Marcacoes por diretorios"]

        img = ImageTk.PhotoImage(file=r"../icons/icone_sensix.png")
        root.call("wm", "iconphoto", root._w, img)

        self.event2canvas = lambda e, c: (c.canvasx(e.x), c.canvasy(e.y))

    def labelling_start(self):
        root.geometry("1290x700+60+20")
        root.maxsize(1350, 740)
        root.resizable(0, 0)
        root.title("WeeDraw")

        self.color_frame_options = "#414851"
        self.color_background = "#262930"
        self.color_frame_over_center = "black"
        self.color_buttons_center = "white"
        self.background_slider = "#414851"
        self.intern_slider = "#5a636f"
        self.slider_saturation_old = 0

        self.frame = tk.Frame(root)

        self.frame_ground = tk.Frame(root)
        self.frame_ground.place(relx=0.0, rely=0.0, relheight=1350, relwidth=740)
        self.frame_ground.configure(relief="groove", borderwidth="0", background=self.color_background)

        self.color_frame_over_center = "black"
        self.background_slider = "#414851"
        self.intern_slider = "#5a636f"

        self.set_slider_saturation = tk.Label(root, text=self.get_current_value_saturation())
        self.set_slider_contourn = tk.Label(root, text=self.get_current_value_contourn())
        self.set_slider_opacity = tk.Label(root, text=self.get_current_value_opacity())

        # Tela inferior com botoes
        self.frame_below_center = tk.Frame(root)
        self.frame_below_center.place(relx=0.178, rely=0.013, relheight=0.966, relwidth=0.817)
        self.frame_below_center.configure(relief="groove", borderwidth="0", background=self.color_frame_over_center)

        # Tela superior, onde a imagem principal é mostrada
        self.frame_over_center = tk.Frame(self.frame_below_center)
        self.frame_over_center.place(relx=0.051, rely=0.0, relheight=0.999, relwidth=0.898)
        self.frame_over_center.configure(relief="groove", borderwidth="0", background=self.color_frame_over_center)

        self.logo = PhotoImage(file=r"../icons/Logo-Escuro.png")
        self.logo = self.logo.subsample(20, 20)
        self.frame_of_options = tk.Frame(root)
        self.frame_of_options.place(relx=0.008, rely=0.014, relheight=0.964, relwidth=0.159)
        self.frame_of_options.configure(borderwidth="0", background=self.color_frame_options)

        self.set_slider_opacity = tk.Label(self.frame_of_options, text=self.get_current_value_opacity())
        self.set_slider_opacity.place(relx=0.059, rely=0.138, height=31, width=79)
        self.set_slider_opacity.configure(text="Opacidade:", fg=self.color_buttons_center, bg=self.color_frame_options)

        self.label_saturation = tk.Label(self.frame_of_options)
        self.label_saturation.place(relx=0.059, rely=0.03, height=21, width=79)
        self.label_saturation.configure(
            text="Saturação:", background=self.color_frame_options, fg=self.color_buttons_center
        )

        self.label_contourn = tk.Label(self.frame_of_options)
        self.label_contourn.place(relx=0.059, rely=0.247, height=21, width=79)
        self.label_contourn.configure(text="Contorno:", fg=self.color_buttons_center, bg=self.color_frame_options)

        self.canvas_logo = tk.Canvas(self.frame_of_options)
        self.canvas_logo.place(relx=0.04, rely=0.910, relheight=0.08, relwidth=0.94)
        self.canvas_logo.create_image(92, 30, image=self.logo, anchor="center")

        self.slider_saturation = tk.Scale(
            self.frame_of_options,
            from_=0.0,
            to=40.0,
            command=self.slider_changed_saturation,
            variable=self.current_value_saturation,
        )

        self.slider_saturation.place(relx=0.098, rely=0.0705, relheight=0.062, relwidth=0.8)
        self.slider_saturation.configure(
            length="164",
            orient="horizontal",
            borderwidth="0",
            troughcolor=self.intern_slider,
            fg="white",
            bg=self.background_slider,
            highlightbackground=self.background_slider,
        )

        self.slider_opacity = tk.Scale(
            self.frame_of_options,
            from_=0.0,
            to=255.0,
            command=self.slider_changed_opacity,
            variable=self.current_value_opacity,
        )

        self.slider_opacity.place(relx=0.098, rely=0.178, relheight=0.062, relwidth=0.8)
        self.slider_opacity.configure(
            length="164",
            orient="horizontal",
            borderwidth="0",
            troughcolor=self.intern_slider,
            fg="white",
            bg=self.background_slider,
            highlightbackground=self.background_slider,
        )

        self.slider_contourn = tk.Scale(
            self.frame_of_options,
            from_=0.0,
            to=100.0,
            command=self.slider_changed_contourn,
            variable=self.current_value_contourn,
        )
        self.slider_contourn.place(relx=0.098, rely=0.279, relheight=0.062, relwidth=0.8)
        self.slider_contourn.configure(
            length="164",
            orient="horizontal",
            borderwidth="0",
            troughcolor=self.intern_slider,
            fg="white",
            bg=self.background_slider,
            highlightbackground=self.background_slider,
        )

        self.frame = tk.Frame(root, bd=2, relief=tk.SUNKEN)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(
            self.frame_over_center,
            bd=0,
            width=self.screen_width,
            height=self.screen_height,
        )

        self.canvas.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
        self.frame_over_center.pack(expand=1)

        self.pencil_icon = PhotoImage(file=r"../icons/pencil_black_white.png")
        self.pencil_icon = self.pencil_icon.subsample(2, 2)
        self.pencil_btn = tk.Button(self.frame_below_center, image=self.pencil_icon)
        self.pencil_btn.place(relx=0.006, rely=0.004, height=43, width=43)
        self.pencil_btn.configure(borderwidth="2", text="Button", background=self.color_buttons_center)
        self.pencil_btn.bind("<Button-1>", partial(self.get_btn, key="6"))

        self.erase_icon = ImageTk.PhotoImage(file=r"../icons/eraser_black.png")
        self.erase_btn = tk.Button(self.frame_below_center, image=self.erase_icon)
        self.erase_btn.place(relx=0.006, rely=0.135, height=43, width=43)
        self.erase_btn.configure(borderwidth="2", text="Button", background=self.color_buttons_center)
        self.erase_btn.bind("<Button-1>", partial(self.get_btn, key="7"))

        self.polygon_icon = ImageTk.PhotoImage(file=r"../icons/polygon.png")
        self.polygon_btn = tk.Button(self.frame_below_center, image=self.polygon_icon)
        self.polygon_btn.place(relx=0.006, rely=0.07, height=43, width=43)
        self.polygon_btn.configure(borderwidth="2", text="Button", background=self.color_buttons_center)
        self.polygon_btn.bind("<Button-1>", partial(self.get_btn, key="9"))

        self.hide_layer_icon = ImageTk.PhotoImage(file=r"../icons/hide_layer.png")
        self.hide_layer_btn = tk.Button(self.frame_below_center, image=self.hide_layer_icon)
        self.hide_layer_btn.place(relx=0.006, rely=0.2, height=43, width=43)
        self.hide_layer_btn.configure(
            activebackground="#f9f9f9", borderwidth="2", text="Button", background=self.color_buttons_center
        )
        self.hide_layer_btn.bind("<Button-1>", partial(self.get_btn, key="8"))

        self.super_pixel_icon = ImageTk.PhotoImage(file=r"../icons/s_pixel.png")
        self.super_pixel_btn = tk.Button(self.frame_below_center, image=self.super_pixel_icon)
        self.super_pixel_btn.place(relx=0.006, rely=0.265, height=43, width=43)
        self.super_pixel_btn.configure(
            activebackground="#f9f9f9", borderwidth="2", text="Button", background=self.color_buttons_center
        )
        self.super_pixel_btn.bind("<Button-1>", partial(self.get_btn, key="10"))

        self.next_icon = PhotoImage(file=r"../icons/next.png")
        self.next_btn = tk.Button(root, image=self.next_icon)
        self.next_btn.place(relx=0.957, rely=0.43, height=70, width=43)
        self.next_btn.configure(borderwidth="2", background="white")
        self.next_btn.bind("<Button-1>", partial(self.get_btn, key="Next"))

        self.back_icon = PhotoImage(file=r"../icons/back.png")
        self.back_btn = tk.Button(root, image=self.back_icon)
        self.back_btn.place(relx=0.183, rely=0.43, height=70, width=43)
        self.back_btn.configure(borderwidth="2", background="white")
        self.back_btn.bind("<Button-1>", partial(self.get_btn, key="Back"))

        # self.percent_txt = tk.Label(self.frame_of_options, text="", font=("Helvetica", 12), bg=None)
        # self.percent_txt.place(relx=0.100, rely=0.52, height=21, width=120)

        self.img_canvas_id = self.canvas.create_image(self.screen_width // 2, self.screen_height // 2, anchor=tk.CENTER)
        self.canvas.pack()

        self.current_value_opacity.set(50.0)
        self.current_value_contourn.set(1)

    def load_image_in_screen(self, img):
        img = cv2.resize(img, (self.screen_width, self.screen_height))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.image_down = img.copy()
        img = PIL.Image.fromarray(img)

        self.image_front = ImageTk.PhotoImage(img)

        return self.image_front

    def labelling_menu(self):

        self.label1.destroy()
        self.opt.destroy()

        self.label1 = tk.Label(root)
        self.label1.place(relx=0.090, rely=0.52, height=21, width=200)
        self.label1.configure(activebackground="#f9f9f9")
        self.label1.configure(text="Selecione o Mosaico :")

        self.btn_load_mosaico = tk.Button(root)
        self.btn_load_mosaico.place(relx=0.72, rely=0.52, height=28, width=123)
        self.btn_load_mosaico.configure(takefocus="")
        self.btn_load_mosaico.configure(text="Mosaico")
        self.btn_load_mosaico.bind("<Button-1>", partial(self.get_btn, key="0"))

        self.label2 = tk.Label(root)
        self.label2.place(relx=0.11, rely=0.60, height=21, width=200)
        self.label2.configure(activebackground="#f9f9f9")
        self.label2.configure(text="Selecione o Shape de Base :")

        self.btn_shape_reference = tk.Button(root)
        self.btn_shape_reference.place(relx=0.72, rely=0.60, height=28, width=123)
        self.btn_shape_reference.configure(takefocus="")
        self.btn_shape_reference.configure(text="Shape de Base")
        self.btn_shape_reference.bind("<Button-1>", partial(self.get_btn, key="3"))

        self.label3 = tk.Label(root)
        self.label3.place(relx=0.117, rely=0.68, height=21, width=260)
        self.label3.configure(activebackground="#f9f9f9")
        self.label3.configure(text="Porcentagem de fundo preto permitida:")

        self.spinbox_backg = tk.Spinbox(root, from_=5.0, to=100.0, increment=5, textvariable=self.spn_box_1)
        self.spinbox_backg.place(relx=0.63, rely=0.69, relheight=0.046, relwidth=0.243)
        self.spinbox_backg.configure(activebackground="#f9f9f9")
        self.spinbox_backg.configure(background="white")
        self.spinbox_backg.configure(font="TkDefaultFont")
        self.spinbox_backg.configure(highlightbackground="black")
        self.spinbox_backg.configure(selectbackground="blue")
        self.spinbox_backg.configure(selectforeground="white")
        self.spinbox_backg.configure(command=partial(self.get_values_spinbox, type="Efetuar Marcacoes em Ortomosaicos"))

        self.btn_start = tk.Button(root)
        self.btn_start.place(relx=0.742, rely=0.871, height=48, width=123)
        self.btn_start.configure(takefocus="")
        self.btn_start.configure(text="Iniciar")
        self.btn_start.bind("<Button-1>", partial(self.get_btn, key="5"))

    def first_menu(self, app):

        self.logo = PhotoImage(file=r"../icons/Logo-Escuro.png")
        self.logo = self.logo.subsample(5, 5)
        self.canvas1 = tk.Canvas(root)
        self.canvas1.place(relx=0.117, rely=0.111, relheight=0.291, relwidth=0.752)
        self.canvas1.configure(borderwidth="2")
        self.canvas1.configure(relief="ridge")
        self.canvas1.configure(selectbackground="blue")
        self.canvas1.configure(selectforeground="white")
        self.canvas1.create_image(300, 90, image=self.logo, anchor="center")

        self.label1 = tk.Label(root)
        self.label1.place(relx=0.25, rely=0.578, height=21, width=200)
        self.label1.configure(text="Selecione uma opção : ")

        self.variable = tk.StringVar(app)
        self.variable.set("Ainda Nao Selecionado")

        self.opt = tk.OptionMenu(app, self.variable, *self.OptionList)
        self.opt.place(x=self.width_size * 0.50, y=self.hight_size * 0.57)

        self.label_opt = tk.Label(text="", font=("Helvetica", 12), fg="red")
        self.label_opt.pack(side="top")

        self.variable.trace("w", self.callback_opt)

    def remove_buttons(self, option="First Menu"):
        if option == "Draw Menu":
            self.label2.destroy()
            self.btn_shape_reference.destroy()
            self.label3.destroy()
            self.spinbox_backg.destroy()
            self.btn_start.destroy()
            self.btn_load_mosaico.destroy()
            # self.spinbox3.destroy()
            # self.spinbox2.destroy()
            # self.label4.destroy()
            # self.label5.destroy()

        elif option == "Start":
            self.TSeparator1.destroy()
            self.btn_load_mosaico.destroy()
            self.btn_shape_reference.destroy()
            self.btn_shape_neural.destroy()
            self.btn_start.destroy()
            self.spinbox1.destroy()
            self.spinbox2.destroy()
            self.spinbox3.destroy()
            self.Radiobutton1.destroy()
            self.label1.destroy()
            self.label2.destroy()
            self.label3.destroy()
            self.label4.destroy()
            self.label5.destroy()
            self.label6.destroy()
            self.label7.destroy()

        else:
            self.canvas1.destroy()
            self.label1.destroy()
            self.opt.destroy()
            self.label_opt.destroy()

    def get_text(self):
        text_val = self.entry_text.get()

        label_init = tk.Label(root, text=text_val)
        self.canvas_init.create_window(200, 230, window=label_init)

    # Metodos para receber os valores do slider de saturação
    def get_current_value_saturation(self):
        self.slider_saturation = int(self.current_value_saturation.get())
        print("valor slider :", self.slider_saturation)
        if self.bool_draw:
            print("Na condicao")
            self.image_down = SatureImg().saturation(
                self.image_down, self.slider_saturation - self.slider_saturation_old
            )

            if self.slider_saturation <= 10:
                self.image_down = self.imgparcela.copy()

            self.update_img(self.draw_img)
        self.slider_saturation_old = self.slider_saturation

    def slider_changed_saturation(self, event):
        self.set_slider_saturation.configure(text=self.get_current_value_saturation())

    # Metodos para receber os valores do slider de contorno
    def get_current_value_contourn(self):
        self.slider_pencil = self.current_value_contourn.get()
        if self.slider_pencil < 10:
            self.slider_pencil = 10

    def slider_changed_contourn(self, event):
        self.set_slider_contourn.configure(text=self.get_current_value_contourn())

    # Metodos para receber os valores do slider de opacidade
    def get_current_value_opacity(self):
        self.slider_opacity = int(self.current_value_opacity.get())

    def slider_changed_opacity(self, event):
        self.set_slider_opacity.configure(text=self.get_current_value_opacity())

    def get_values_spinbox(self, type=""):

        if type == "Efetuar Marcacoes por diretorios":
            if self.first_click_bool == False:
                self.iterator_recoil = float(int(self.spinbox1.get()) / 100)
                self.iterator_x = int(self.spinbox2.get())
                self.iterator_y = int(self.spinbox3.get())

        elif type == "Efetuar Marcacoes em Ortomosaicos":
            self.background_percent = float(1 - int(self.spinbox_backg.get()) / 100)
            # self.iterator_x = int(self.spinbox2.get())
            # self.iterator_y = int(self.spinbox3.get())
            self.iterator_recoil = 1.0
            # print(self.background_percent)

        else:
            values1 = self.iterator_recoil * 100
            values2 = self.iterator_x
            values3 = self.iterator_y

    def get_values_radio(self):
        self.first_click_bool = not (self.first_click_bool)

        if self.first_click_bool:
            bool_default = bool(self.bool_value.get())
            self.spn_box_1.set("80")
            self.spn_box_2.set("256")
            self.spn_box_3.set("256")

        else:
            bool_default = False
            self.bool_value.set(bool_default)

    def keyboard(self, event):
        self.key_pressed = event.char
        if self.key_pressed == "r":
            self.color_line = 1
            print("r")

        if self.key_pressed == "g":
            self.color_line = 2
            print("g")

        if self.key_pressed == "b":
            self.color_line = 3
            print("b")

        if self.key_pressed == "p":
            self.color_line = 0
            print("p")

        if self.key_pressed == "n":
            if not self.use_neural_network:
                from neural import NeuralFunctions

                self.use_neural_network = True
                self.path_neural_network = filedialog.askopenfilename(title="Selecione os pesos da rede neural :")
                self.neural_network = NeuralFunctions(self.path_neural_network)
                img = self.neural_network.predict_image(self.imgparcela)
            else:
                img = self.neural_network.predict_image(self.imgparcela)

            img = cv2.resize(img, (self.screen_width, self.screen_height))
            img = imp.gray_to_rgba(self, img)

            image_new = []
            for channel in range(img.shape[-1] - 1):
                img[img[:, :, channel] == 255] = [0, 0, 255, self.slider_opacity]

            img = Image.fromarray(img)
            for item in img.getdata():

                if item[:3] == (0, 0, 0):
                    image_new.append((0, 0, 0, 0))
                else:
                    image_new.append(item[:3] + (self.slider_opacity,))

            img.putdata(image_new)
            self.draw_img.paste(img, (0, 0), img)

        if self.super_pixel_bool:
            self.draw_img = PIL.Image.new("RGBA", (self.screen_width, self.screen_height), (0, 0, 0, 0))
            self.draw_line = ImageDraw.Draw(self.draw_img)

        self.color_line_rgb = self.color_map[self.color_line]
        print(self.color_line)

    def get_btn(self, event, key):
        self.event_btn = key
        if key == "0":
            self.name_tif = self.load_shp(0)[0]

        elif key == "1":
            self.name_reference_binary = self.load_shp(1)[1]

        elif key == "2":
            self.name_reference_neural = self.load_shp(2)[2]

        elif key == "3":
            self.name_reference_binary = self.load_shp(1)[1]

        if key == "6":
            self.pencil_draw_bool = True
            self.polygon_draw_bool = False
            self.opacity = False
            self.super_pixel_bool = False

        elif key == "7":
            self.pencil_draw_bool = False
            self.polygon_draw_bool = False
            self.opacity = False
            self.super_pixel_bool = False

        elif key == "8":
            self.opacity = not self.opacity
            if self.opacity:
                option_img = "normal"
                self.canvas.itemconfig(self.img_canvas_id, image=self.image_final)

            else:
                self.canvas.itemconfig(self.img_canvas_id, image=self.image_tk)

        elif key == "9":
            self.pencil_draw_bool = False
            self.polygon_draw_bool = True
            self.opacity = False
            self.super_pixel_bool = False

        elif key == "10":
            print("10")
            self.pencil_draw_bool = False
            self.polygon_draw_bool = False
            self.opacity = False
            self.super_pixel_bool = True

        elif (
            self.name_tif != "" and self.name_reference_binary != "" and self.name_reference_neural != "" and key == "5"
        ):
            root.geometry("800x600+50+10")
            self.ready_start = True

        elif self.name_tif != "" and self.name_reference_binary != "" and key == "5":
            # self.remove_buttons('Draw Menu')
            self.reference_binary = self.shp_to_bin(self.name_reference_binary, self.name_tif)
            self.remove_buttons("Fisrt Menu")
            self.labelling_start()
            self.remove_buttons("Draw Menu")
            self.name_tif = '"' + self.name_tif + '"'

            if self.load_progress():

                if str(self.directory_saved) == str((self.name_tif)):
                    mbox.showinfo("Information", "O Progresso Anterior foi Carregado!")
                    self.dst_img = gdal.Open("resutado_gerado.tif", gdal.GA_Update)

                else:
                    self.x_crop = 0.0
                    self.y_crop = 0.0
                    self.dst_img = gdal.GetDriverByName("GTiff").Create(
                        "resutado_gerado.tif",
                        self.mosaico.RasterXSize,
                        self.mosaico.RasterYSize,
                        1,
                        gdal.GDT_Byte,
                        options=["COMPRESS=DEFLATE"],
                    )
                    self.dst_img.SetProjection(self.mosaico.GetProjectionRef())
                    self.dst_img.SetGeoTransform(self.mosaico.GetGeoTransform())

            else:
                self.x_crop = 0.0
                self.y_crop = 0.0
                self.dst_img = gdal.GetDriverByName("GTiff").Create(
                    "resutado_gerado.tif",
                    self.mosaico.RasterXSize,
                    self.mosaico.RasterYSize,
                    1,
                    gdal.GDT_Byte,
                    options=["COMPRESS=DEFLATE"],
                )
                self.dst_img.SetProjection(self.mosaico.GetProjectionRef())
                self.dst_img.SetGeoTransform(self.mosaico.GetGeoTransform())

            self.daninha_1 = gdal.Open(self.reference_binary)
            self.daninha_band_1 = self.daninha_1.GetRasterBand(1)

            self.draw_img = PIL.Image.new("RGBA", (self.screen_width, self.screen_height), (0, 0, 0, 0))
            self.draw_line = ImageDraw.Draw(self.draw_img)

            self.draw_img_gray = PIL.Image.new("L", (self.screen_width, self.screen_height))
            self.draw_line_gray = ImageDraw.Draw(self.draw_img_gray)

            self.cnt_validator = []

            self.next_btn.bind("<Button-1>", partial(self.button_click, key="1"))
            self.back_btn.bind("<Button-1>", partial(self.button_click, key="0"))

        if self.ready_start:
            self.remove_buttons("Start")

            self.reference_binary = gdal.Open(self.shp_to_bin(self.name_reference_binary, self.name_tif), 1)
            self.reference_neural = gdal.Open(self.shp_to_bin(self.name_reference_neural, self.name_tif), 1)

            self.dst_img = gdal.GetDriverByName("GTiff").Create(
                self.name_reference_binary + "_out.tif",
                self.reference_binary.RasterXSize,
                self.reference_binary.RasterYSize,
                1,
                gdal.GDT_Byte,
                options=["COMPRESS=DEFLATE"],
            )
            self.dst_img.SetProjection(self.reference_binary.GetProjectionRef())
            self.dst_img.SetGeoTransform(self.reference_binary.GetGeoTransform())
            self.frame = tk.Frame(root, bd=2, relief=tk.SUNKEN)
            self.frame.grid_rowconfigure(0, weight=1)
            self.frame.grid_columnconfigure(0, weight=1)
            xscroll = tk.Scrollbar(self.frame_over_center, orient=tk.HORIZONTAL)
            yscroll = tk.Scrollbar(self.frame_over_center)

            self.canvas = tk.Canvas(
                self.frame,
                bd=0,
                width=self.screen_width,
                height=self.screen_height,
                xscrollcommand=xscroll.set,
                yscrollcommand=yscroll.set,
            )

            self.canvas.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
            self.frame.pack(expand=1)

            self.next_icon = PhotoImage(file=r"../icons/next.png")
            self.next_btn = tk.Button(root, image=self.next_icon)
            self.next_btn.place(relx=0.926, rely=0.363, height=83, width=43)
            self.next_btn.configure(borderwidth="2")
            self.next_btn.bind("<Button-1>", partial(self.change_dir, key="1"))

            self.back_icon = PhotoImage(file=r"../icons/back.png")
            self.back_btn = tk.Button(root, image=self.back_icon)
            self.back_btn.place(relx=0.031, rely=0.363, height=83, width=43)
            self.back_btn.configure(borderwidth="2")
            self.back_btn.bind("<Button-1>", partial(self.change_dir, key="0"))
            self.image_tk = self.load_image_in_screen(np.zeros(self.screen_width, self.screen_width, 3))

    def run(self):
        self.labelling_start()

    def callback_opt(self, *args):
        if self.variable.get() == "Efetuar Marcacoes em Ortomosaicos":
            if not os.path.isdir(self.path_save_img_rgb):
                os.makedirs(self.path_save_img_rgb, exist_ok=True)

            if not os.path.isdir(self.path_save_img_bin):
                os.makedirs(self.path_save_img_bin, exist_ok=True)

            if not os.path.isdir(self.path_save_img_negative):
                os.makedirs(self.path_save_img_negative, exist_ok=True)

            self.labelling_menu()

        self.old_choose = self.variable.get()

    def percent_progress(self, x, y, total_x, total_y):
        current_position = y / total_y
        current_position = round(current_position * 100, 2)
        return current_position

    def button_click(self, event=None, key=None):
        print("self.img_canvas_id : ", self.img_canvas_id)
        if self.bool_draw:
            self.current_value_saturation.set(0.0)

            self.count_feature = 0
            data_polygons = []

            self.save_draw_array = np.asarray(self.draw_img)
            self.save_draw_array = imp.prepare_array(self, self.save_draw_array, self.iterator_x, self.iterator_y)

            if cv2.countNonZero(self.save_draw_array) == 0:
                cv2.imwrite(
                    self.path_save_img_negative + "/daninha_{x}_{y}.png".format(x=int(self.x_crop), y=int(self.y_crop)),
                    self.imgparcela,
                )
            else:
                cv2.imwrite(
                    self.path_save_img_rgb + "/daninha_{x}_{y}.png".format(x=int(self.x_crop), y=int(self.y_crop)),
                    self.imgparcela,
                )
                cv2.imwrite(
                    self.path_save_img_bin + "/daninha_{x}_{y}.png".format(x=int(self.x_crop), y=int(self.y_crop)),
                    self.save_draw_array,
                )
                self.dst_img.GetRasterBand(1).WriteArray(self.save_draw_array, xoff=self.x_crop, yoff=self.y_crop)
                self.dst_img.FlushCache()

                self.draw_img = PIL.Image.new("RGBA", (self.screen_width, self.screen_height), (0, 0, 0, 0))
                self.draw_line = ImageDraw.Draw(self.draw_img)

                self.draw_img_gray = PIL.Image.new("L", (self.screen_width, self.screen_height))
                self.draw_line_gray = ImageDraw.Draw(self.draw_img_gray)

            self.draw_lines_array = []
            self.features_polygons = [[]]

        if key == "1":
            if self.x_crop + self.iterator_x < self.mosaico.RasterXSize and self.x_crop + self.iterator_x > 0:
                self.x_crop += self.iterator_x * self.iterator_recoil
                # print('key 1 - if 0')

                if self.x_crop + self.iterator_x > self.mosaico.RasterXSize:
                    self.x_max = self.x_crop - self.iterator_x * self.iterator_recoil
                    # print('entrou')

            if self.x_crop + self.iterator_x > self.mosaico.RasterXSize:
                self.x_crop = 0
                self.y_crop += self.iterator_y * self.iterator_recoil
                # print('key 1 - if 1')

            if self.y_crop + self.iterator_y > self.mosaico.RasterYSize:
                self.x_crop = self.x_crop
                self.y_crop = self.y_crop
                # print('key 1 - if 2')
                mbox.showinfo("Information", "Todo o Mosaico foi Percorrido!")
                self.destroy_aplication()

            self.daninha_parcela = self.daninha_band_1.ReadAsArray(
                self.x_crop, self.y_crop, self.iterator_x, self.iterator_y
            )
            while cv2.countNonZero(self.daninha_parcela) <= self.iterator_x * self.iterator_y * self.background_percent:
                if self.x_crop + self.iterator_x < self.mosaico.RasterXSize and self.x_crop + self.iterator_x > 0:
                    self.x_crop += self.iterator_x * self.iterator_recoil
                    # print('key 1 - if 0')

                    if self.x_crop + self.iterator_x > self.mosaico.RasterXSize:
                        self.x_max = self.x_crop - self.iterator_x * self.iterator_recoil
                        # print('entrou')

                if self.x_crop + self.iterator_x > self.mosaico.RasterXSize:
                    self.x_crop = 0
                    self.y_crop += self.iterator_y * self.iterator_recoil

                if self.y_crop + self.iterator_y > self.mosaico.RasterYSize:
                    self.x_crop = self.x_crop
                    self.y_crop = self.y_crop

                    mbox.showinfo("Information", "Todo o Mosaico foi Percorrido!")
                    self.destroy_aplication()
                    break

                self.daninha_parcela = self.daninha_band_1.ReadAsArray(
                    self.x_crop, self.y_crop, self.iterator_x, self.iterator_y
                )

        elif key == "0":
            if self.x_crop - self.iterator_x < self.mosaico.RasterXSize:
                self.x_crop -= self.iterator_x * self.iterator_recoil
                # print('key 0 - if 1')

                if self.x_crop <= 0:
                    self.x_crop = self.x_max
                    self.y_crop -= self.iterator_y * self.iterator_recoil

            if self.y_crop - self.iterator_y > self.mosaico.RasterYSize:
                self.x_crop = 0
                self.y_crop -= self.iterator_y * self.iterator_recoil

            self.daninha_parcela = self.daninha_band_1.ReadAsArray(
                self.x_crop, self.y_crop, self.iterator_x, self.iterator_y
            )
            while cv2.countNonZero(self.daninha_parcela) <= self.iterator_x * self.iterator_y * self.background_percent:
                if self.x_crop - self.iterator_x < self.mosaico.RasterXSize:
                    self.x_crop -= self.iterator_x * self.iterator_recoil

                    if self.x_crop <= 0:
                        self.x_crop = self.x_max
                        self.y_crop -= self.iterator_y * self.iterator_recoil

                if self.y_crop - self.iterator_y > self.mosaico.RasterYSize:
                    self.x_crop = 0
                    self.y_crop -= self.iterator_y * self.iterator_recoil

                self.daninha_parcela = self.daninha_band_1.ReadAsArray(
                    self.x_crop, self.y_crop, self.iterator_x, self.iterator_y
                )

        self.daninha_parcela = self.daninha_band_1.ReadAsArray(
            self.x_crop, self.y_crop, self.iterator_x, self.iterator_y
        )
        # self.percent_txt["text"] = (
        #    "Progress : "
        #    + str(self.percent_progress(self.x_crop, self.y_crop, self.mosaico.RasterXSize, self.mosaico.RasterYSize))
        #    + "%"
        # )
        blueparcela = self.blue.ReadAsArray(self.x_crop, self.y_crop, self.iterator_x, self.iterator_y)
        greenparcela = self.green.ReadAsArray(self.x_crop, self.y_crop, self.iterator_x, self.iterator_y)
        redparcela = self.red.ReadAsArray(self.x_crop, self.y_crop, self.iterator_x, self.iterator_y)
        self.imgparcela = cv2.merge((redparcela, greenparcela, blueparcela))
        self.imgparcela[self.daninha_parcela == 0] = 0
        self.image_down = self.imgparcela.copy()
        self.segmentation = np.zeros_like(self.image_down)

        self.img_array_tk = cv2.resize(self.imgparcela, (self.screen_width, self.screen_height))
        self.img_array_tk = PIL.Image.fromarray(self.img_array_tk)
        self.image_tk = ImageTk.PhotoImage(self.img_array_tk)
        self.first_click = True
        self.canvas.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
        self.update_img(self.img_array_tk)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        self.canvas.bind("<Button-1>", self.get_x_and_y)
        self.canvas.bind("<Button 3>", self.get_right_click)
        self.canvas.bind("<B1-Motion>", self.draw_smth)
        self.frame_root.bind("<KeyPress>", self.keyboard)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_release)

        self.canvas.pack()

    def get_right_click(self, event):
        self.current_points.clear()
        self.count_feature += 1

    def mouse_release(self, event):
        if self.super_pixel_bool:
            self.image_for_watershed = self.imgparcela.copy()

            self.image_for_watershed = cv2.resize(self.image_for_watershed, (self.screen_width, self.screen_height))
            self.segmentation = np.zeros_like(self.image_for_watershed)

            markers = cv2.watershed(self.image_for_watershed.copy(), self.image_array_gray.copy())

            for i in range(self.color_map.__len__()):
                self.segmentation[markers == i + 1] = self.color_map[i]

            self.bool_draw = True
            # self.segmentation = cv2.resize(self.segmentation, (self.iterator_x, self.iterator_y))
            # self.image_down[self.segmentation != 0] = 255

            self.segmentation = cv2.cvtColor(self.segmentation, cv2.COLOR_RGB2RGBA)
            self.segmentation = Image.fromarray(self.segmentation)
            ##
            image_new = []
            for item in self.segmentation.getdata():
                if item[:3] == (0, 0, 0):
                    image_new.append((0, 0, 0, 0))
                else:
                    image_new.append(item[:3] + (self.slider_opacity,))

            self.segmentation.putdata(image_new)

            self.draw_img.paste(self.segmentation, (0, 0), self.segmentation)
            self.update_img(self.draw_img)

    def get_x_and_y(self, event):
        self.lasx, self.lasy = event.x, event.y
        if self.polygon_draw_bool:
            self.current_points.append((self.lasx, self.lasy))
            number_points = len(self.current_points)

            if number_points > 2:
                self.draw_line.polygon(
                    (self.current_points),
                    (self.color_line_rgb + (int(self.current_value_opacity.get()),)),
                    outline="red",
                )

            elif number_points == 2:
                self.draw_line.line(
                    (self.lasx, self.lasy, event.x, event.y),
                    (self.color_line_rgb + (int(self.current_value_opacity.get()),)),
                    width=5,
                    joint="curve",
                )

            Offset = (10) / 2
            self.draw_line.ellipse(
                (self.lasx - Offset, self.lasy - Offset, self.lasx + Offset, self.lasy + Offset),
                (self.color_line_rgb + (int(self.current_value_opacity.get()),)),
            )
            self.update_img(self.draw_img)

        self.old_x = self.lasx
        self.old_y = self.lasy

    def draw_smth(self, event):
        self.lasx, self.lasy = event.x, event.y
        if self.pencil_draw_bool:
            self.draw_line.line(
                (self.old_x, self.old_y, self.lasx, self.lasy),
                (self.color_line_rgb + (int(self.current_value_opacity.get()),)),
                width=int(self.slider_pencil),
                joint="curve",
            )
            Offset = (int(self.slider_pencil)) / 2
            self.draw_line.ellipse(
                (self.lasx - Offset, self.lasy - Offset, self.lasx + Offset, self.lasy + Offset),
                (self.color_line_rgb + (int(self.current_value_opacity.get()),)),
            )
            self.bool_draw = True
            self.update_img(self.draw_img)

        if self.super_pixel_bool:
            self.lasx, self.lasy = event.x, event.y
            self.draw_line.line(
                ((self.old_x, self.old_y, self.lasx, self.lasy)),
                (self.color_line_rgb + (int(self.current_value_opacity.get()),)),
                width=int(self.slider_pencil),
            )
            Offset = (int(self.slider_pencil)) / 2
            self.draw_line.ellipse(
                (self.lasx - Offset, self.lasy - Offset, self.lasx + Offset, self.lasy + Offset),
                (self.color_line_rgb + (int(self.current_value_opacity.get()),)),
            )
            self.update_img(self.draw_img)

            self.draw_line_gray.line(
                ((self.old_x, self.old_y, self.lasx, self.lasy)), self.color_line, width=int(self.slider_pencil)
            )

            self.image_array_gray = np.array(self.draw_img_gray.copy(), dtype="float32")
            ##self.image_array_gray = cv2.resize(self.image_array_gray, (self.iterator_x, self.iterator_y))
            self.image_array_gray = np.array(self.image_array_gray, dtype="int32")

            self.bool_draw = True

        elif not self.pencil_draw_bool and not self.polygon_draw_bool:
            self.lasx, self.lasy = event.x, event.y

            self.draw_line.line(
                (self.old_x, self.old_y, self.lasx, self.lasy),
                (0, 0, 0, 0),
                width=int(self.slider_pencil / 2),
                joint="curve",
            )
            Offset = int(self.slider_pencil / 2)
            self.draw_line.ellipse(
                (self.lasx - Offset, self.lasy - Offset, self.lasx + Offset, self.lasy + Offset),
                (0, 0, 0, 0),
            )
            self.bool_draw = True
            self.update_img(self.draw_img)

        self.old_x = self.lasx
        self.old_y = self.lasy

    def update_img(self, img):

        self.image = np.array(self.image_down)
        self.image = cv2.resize(self.image, (self.screen_width, self.screen_height))
        self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2RGBA)
        self.image = PIL.Image.fromarray(self.image.copy())

        self.image.paste(self.draw_img, (0, 0), self.draw_img)
        self.image_final = ImageTk.PhotoImage(self.image)
        self.canvas.itemconfig(self.img_canvas_id, image=self.image_final)

    def load_rgb_tif(self):

        path_rgb_shp = filedialog.askopenfilename(title="Selecione O Mosaico")
        if path_rgb_shp.endswith("tif"):

            self.mosaico = gdal.Open(path_rgb_shp)
            self.red = self.mosaico.GetRasterBand(1)
            self.green = self.mosaico.GetRasterBand(2)
            self.blue = self.mosaico.GetRasterBand(3)
            self.alpha = self.mosaico.GetRasterBand(4)

            self.nx = self.mosaico.RasterXSize
            self.ny = self.mosaico.RasterYSize

            file_path = pathlib.Path(path_rgb_shp)
            self.out_file = pathlib.Path("/")
            self.out_file = file_path.parent / ("out" + ".shp")
            path_temp = file_path.parent / "temp_files"

            if path_temp.exists():
                shutil.rmtree(str(path_temp))
                os.mkdir(str(path_temp))
            else:
                os.mkdir(str(path_temp))

            self.dst_img = gdal.GetDriverByName("GTiff").Create(
                str(path_temp / "outfile.tif"), self.nx, self.ny, 1, gdal.GDT_Byte
            )
            self.dst_img.SetGeoTransform(self.mosaico.GetGeoTransform())
            self.srs = osr.SpatialReference()
            self.srs.ImportFromWkt(self.mosaico.GetProjection())
            self.dst_img.SetProjection(self.srs.ExportToWkt())
            tif_loaded = True

        else:
            mbox.showerror("Error", "Selecione um Arquivo .tif")
            tif_loaded = False

        return tif_loaded, path_rgb_shp

    def load_shp(self, type_shape=0, option="Comparar Resultados"):
        """
        Carrega o shp que sera utilido nas comparacoes
        type : 0 - Carrega o Mosaico
               1 - Representa o shape de referencia
               2 - Representa o shape da rede neural
               3 - Representa o shape de ambos
        option : Refere-se ao tipo de operacao a ser executada
        """
        if option == "Comparar Resultados":
            if type_shape == 0:

                path_reference_tif = self.load_rgb_tif()[1]
                path_reference_shp = None
                path_neural_shp = None

            elif type_shape == 1:
                path_reference_tif = None
                path_reference_shp = filedialog.askopenfilename(title="Selecione o Shape de Referência :")
                path_neural_shp = None

            elif type_shape == 2:
                path_reference_tif = None
                path_reference_shp = None
                path_neural_shp = filedialog.askopenfilename(title="Selecione o Shape da Rede Neural :")

            elif type_shape == 3:
                path_reference_shp = filedialog.askopenfilename(title="Selecione o Shape de Referência :")
                path_reference_tif = None
                path_neural_shp = filedialog.askopenfilename(title="Selecione o Shape da Rede Neural :")

            return path_reference_tif, path_reference_shp, path_neural_shp

    def shp_to_bin(self, name_shp, name_tif, burn=255):

        base_img = gdal.Open(name_tif, gdal.GA_ReadOnly)
        base_shp = ogr.Open(name_shp)
        base_shp_layer = base_shp.GetLayer()

        # output_name = name_shp + '_out.tif
        output = gdal.GetDriverByName("GTiff").Create(
            name_shp + "_out.tif",
            base_img.RasterXSize,
            base_img.RasterYSize,
            1,
            gdal.GDT_Byte,
            options=["COMPRESS=DEFLATE"],
        )
        output.SetProjection(base_img.GetProjectionRef())
        output.SetGeoTransform(base_img.GetGeoTransform())

        Band = output.GetRasterBand(1)
        raster = gdal.RasterizeLayer(output, [1], base_shp_layer, burn_values=[burn])

        Band = None
        output = None
        base_img = None
        base_shp = None

        return name_shp + "_out.tif"

    def generate_binary_tif(self):
        mbox.showinfo("Information", "Gerando Resultados: Isso pode demorar um pouco: ")
        iterator_x = 256
        iterator_y = 256

        for x in range(0, self.mosaico.RasterXSize, iterator_x):

            for y in range(0, self.mosaico.RasterYSize, iterator_y):

                if ((x + iterator_x) > self.mosaico.RasterXSize) or ((y + iterator_y) > self.mosaico.RasterYSize):
                    continue

                blueparcela = self.blue.ReadAsArray(x, y, iterator_x, iterator_y)
                greenparcela = self.green.ReadAsArray(x, y, iterator_x, iterator_y)
                redparcela = self.red.ReadAsArray(x, y, iterator_x, iterator_y)
                self.imgparcela = cv2.merge((blueparcela, greenparcela, redparcela))
                img = self.imgparcela / 255

                pr = imp.predict_image(self, img)

                if (self.imgparcela.max() > 0) and (self.imgparcela.min() < 255):
                    write_image = pr

                else:
                    pr[pr >= 255] = 0
                    write_image = pr

                self.dst_img.GetRasterBand(1).WriteArray(write_image, xoff=x, yoff=y)
                self.dst_img.self.dst_img.FlushCache()

    def generate_shape(self):

        src_band = self.dst_img.GetRasterBand(1)
        dst_layername = "daninhas"
        drv = ogr.GetDriverByName("ESRI Shapefile")
        dst_ds = drv.CreateDataSource(str(self.out_file))
        dst_layer = dst_ds.CreateLayer(dst_layername, srs=self.srs)

        gdal.Polygonize(src_band, src_band, dst_layer, -1, [], callback=None)
        dst_ds.Destroy()
        mbox.showinfo("Information", "Shape Gerado com Sucesso!: ")

    def load_progress(self):

        try:
            f = open("log_progress.txt", encoding="utf-8")
            for lines in f:
                pass

            # Caso o arquivo exista e tenha valores validos
            if (os.path.getsize("log_progress.txt")) > 0:
                values = lines.split(",")
                self.x_crop = float(values[0])
                self.y_crop = float(values[1])
                self.directory_saved = str(values[2])

            bool_check_dir = True
            f.close()

        except:
            f = open("log_progress.txt", "x", encoding="utf-8")
            bool_check_dir = False
            f.close()

        return bool_check_dir

    def destroy_aplication(self):

        if self.x_crop >= 0 and self.y_crop >= 0:
            string_text = str(self.x_crop) + "," + str(self.y_crop) + "," + str(self.name_tif) + ", \n"
            with open("log_progress.txt", "ab") as f:
                f.write(string_text.encode("utf-8", "ignore"))

        root.destroy()


if __name__ == "__main__":

    root = tk.Tk()
    obj = Interface(root)
    root.title("WeeDraw")
    root.resizable(False, False)
    obj.first_menu(root)
    root.geometry("800x800+50+10")
    root.mainloop()
