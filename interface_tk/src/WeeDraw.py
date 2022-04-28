import numpy as np
import os
import pathlib
import PIL
import cv2
import sys
import math
import warnings

from tkinter.colorchooser import askcolor

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
from tkinter import Button, PhotoImage, messagebox as mbox
from PIL import Image, ImageDraw, ImageTk
from tkinter import filedialog
from osgeo import gdal, ogr, osr


from callbacks_tk import Screen
from menu import ButtonSettingsLabelling, ButtonsLabelling
from neural import NeuralFunctions
from imgs_manipulations import *
from imgs_manipulations import ImagesManipulations as imp
from draw import Draw
from zoom import *
from utils import LogCustom

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
        self.iterator_recoil = 1.0
        self.cnt_validator = []
        self.background_percent = 0.8
        self.array_clicks = []
        self.current_points = []
        self.current_points_bkp = []
        self.draw_array = [[]]
        self.features_polygons = [[]]
        self.polygons_ids_array = []
        self.vertices_ids_array = []

        self.save_draw_array = None
        self.option_of_draw = "CNT"
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
        self.validate_contorn = False
        self.opacity = False
        self.bool_draw = False
        self.delete_contourn = False
        self.use_neural_network = False
        self.path_save_img_rgb = "dataset/rgb"
        self.path_save_img_bin = "dataset/binario"
        self.path_save_img_negative = "dataset/negativos"
        self.user_choosed = ''
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
        self.check_neural = tk.IntVar()

        self.old_choose = ""
        self.OptionList = ["Efetuar Marcacoes em Ortomosaicos", "Analisar os Resultados"]
        img = ImageTk.PhotoImage(file=r"../icons/icone_sensix.png")
        root.call("wm", "iconphoto", root._w, img)

        self.event2canvas = lambda e, c: (c.canvasx(e.x), c.canvasy(e.y))

    def labelling_start(self):
        root.geometry("1290x700+60+20")
        root.maxsize(1350, 740)
        root.resizable(0, 0)
        root.title("WeeDraw")

        self.label1.destroy()
        self.opt.destroy()

        self.label1 = tk.Label(root)
        self.label1.place(relx=0.090, rely=0.52, height=21, width=200)
        self.label1.configure(activebackground="#f9f9f9", text="Selecione o Mosaico :")

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

        self.set_slider_saturation = tk.Label(root, text="")
        self.set_slider_contourn = tk.Label(root, text="")
        self.set_slider_opacity = tk.Label(root, text="")

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
            from_=1.0,
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

        #self.canvas = Screen(tk, self.frame_over_center, self.screen_width, self.screen_height).define_canvas()
        image, _ = self.screen_main, self.draw = Draw().create_screen_to_draw(self.screen_width, self.screen_height)
        self.canvas_obj = CanvasImage(tk, self.frame_over_center, image)
        self.canvas = self.canvas_obj.define_canvas()
        self.frame_over_center.pack(expand=1)

        self.buttons = ButtonsLabelling(root, tk, self.frame_below_center)
        self.buttons.button_start()

        self.buttons.pencil_btn.bind("<Button-1>", partial(self.get_btn, key="6"))
        self.buttons.erase_btn.bind("<Button-1>", partial(self.get_btn, key="7"))
        self.buttons.polygon_btn.bind("<Button-1>", partial(self.get_btn, key="9"))
        self.buttons.hide_layer_btn.bind("<Button-1>", partial(self.get_btn, key="8"))
        self.buttons.super_pixel_btn.bind("<Button-1>", partial(self.get_btn, key="10"))
        self.buttons.next_btn.bind("<Button-1>", partial(self.get_btn, key="Next"))
        self.buttons.back_btn.bind("<Button-1>", partial(self.get_btn, key="Back"))

        self.button_select_color = tk.Button(root, text="Cor para marcação", command=self.change_color, fg="white")
        self.button_select_color.place(relx=0.025, rely=0.375, height=43, width=165)
        self.button_select_color.configure(bg=self.color_background)

        #self.img_canvas_id = self.canvas.create_image(0, 0, anchor='nw')

        self.current_value_opacity.set(50.0)
        self.current_value_contourn.set(1)

    def settings_labelling_menu(self):

        self.label1.destroy()
        self.opt.destroy()

        self.label1 = tk.Label(root)
        self.label1.place(relx=0.090, rely=0.52, height=21, width=200)
        self.label1.configure(activebackground="#f9f9f9")
        self.label1.configure(text="Selecione o Mosaico :")

        self.label2 = tk.Label(root)
        self.label2.place(relx=0.11, rely=0.60, height=21, width=200)
        self.label2.configure(activebackground="#f9f9f9")
        self.label2.configure(text="Selecione o Shape de Base :")

        self.label3 = tk.Label(root)
        self.label3.place(relx=0.117, rely=0.68, height=21, width=260)
        self.label3.configure(activebackground="#f9f9f9")
        self.label3.configure(text="Porcentagem de fundo preto permitida :")

        self.spinbox_backg = tk.Spinbox(root, from_=5.0, to=100.0, increment=5, textvariable=self.spn_box_1)
        self.spinbox_backg.place(relx=0.63, rely=0.69, relheight=0.046, relwidth=0.243)
        self.spinbox_backg.configure(
            activebackground="#f9f9f9",
            background="white",
            font="TkDefaultFont",
            highlightbackground="black",
            selectbackground="blue",
            selectforeground="white",
            command=partial(self.get_values_spinbox, type="Efetuar Marcacoes em Ortomosaicos"),
        )

        self.buttons = ButtonSettingsLabelling(root, tk)
        self.buttons.settings_labelling_menu()
        self.buttons.btn_load_mosaico.bind("<Button-1>", partial(self.get_btn, key="0"))
        self.buttons.btn_shape_reference.bind("<Button-1>", partial(self.get_btn, key="3"))
        self.buttons.btn_start.bind("<Button-1>", partial(self.get_btn, key="5"))
        self.button_check_nn = tk.Checkbutton(
            root, text="Utilizar Rede Neural", variable=self.use_neural_network, command=self.use_nn
        )
        self.button_check_nn.place(x=85, y=450)

    def first_menu(self, app):

        self.logo = PhotoImage(file=r"../icons/Logo-Escuro.png")
        self.logo = self.logo.subsample(5, 5)
        self.canvas_first_menu = tk.Canvas(root)
        self.canvas_first_menu.place(relx=0.117, rely=0.111, relheight=0.291, relwidth=0.752)
        self.canvas_first_menu.configure(borderwidth="2")
        self.canvas_first_menu.configure(relief="ridge")
        self.canvas_first_menu.configure(selectbackground="blue")
        self.canvas_first_menu.configure(selectforeground="white")
        self.canvas_first_menu.create_image(300, 90, image=self.logo, anchor="center")

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
            self.label3.destroy()
            self.spinbox_backg.destroy()

        else:
            self.canvas_first_menu.destroy()
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
        if self.bool_draw:
            self.image_down = SatureImg().saturation(
                self.image_down, self.slider_saturation - self.slider_saturation_old
            )

            if self.slider_saturation <= 10:
                self.image_down = self.imgparcela.copy()

            self.update_img(self.screen_main)
        self.slider_saturation_old = self.slider_saturation

    def slider_changed_saturation(self, event):
        self.set_slider_saturation.configure(text=self.get_current_value_saturation())

    def slider_changed_contourn(self, event):
        self.slider_pencil = self.current_value_contourn.get()
        if self.slider_pencil < 1:
            self.slider_pencil = 1

        self.set_slider_contourn.configure(text=self.current_value_contourn.get())

    def get_current_value_opacity(self):
        self.slider_opacity = int(self.current_value_opacity.get())

    def slider_changed_opacity(self, event):
        self.set_slider_opacity.configure(text=self.get_current_value_opacity())

    def get_values_spinbox(self, type=""):
        if type == "Efetuar Marcacoes em Ortomosaicos":
            self.background_percent = float(1 - int(self.spinbox_backg.get()) / 100)
            self.iterator_recoil = 1.0

    def keyboard(self, event):
        self.key_pressed = event.char
        self.key_code = event.keycode

        if self.key_code == 32 or self.key_code == 65:
            self.array_screen_neural = np.asarray(self.screen_main)
            img = imp.prepare_array(self, self.array_screen_neural, self.screen_width, self.screen_height, False)

            contours = imp.find_contourns(self, img, self.screen_width, self.screen_height)
            cv2.fillPoly(self.array_screen_neural, pts=contours, color=(self.color_line_rgb + (self.slider_opacity,)),)
            self.screen_neural = Image.fromarray(self.array_screen_neural)
            self.screen_main.paste(self.screen_neural, (0, 0), self.screen_neural)

            self.update_img(self.screen_main)
       
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
            self.validate_contorn = False

        elif key == "7":
            self.pencil_draw_bool = False
            self.polygon_draw_bool = False
            self.opacity = False
            self.validate_contorn = False

        elif key == "8":
            self.opacity = not self.opacity
            if self.opacity:
                option_img = "normal"
                self.canvas_obj.show(self.image_final)
            else:
                self.canvas_obj.show(self.image_tk)

        elif key == "9":
            self.pencil_draw_bool = False
            self.polygon_draw_bool = True
            self.opacity = False
            self.validate_contorn = False

        elif key == "10":
            self.pencil_draw_bool = False
            self.polygon_draw_bool = False
            self.opacity = False
            self.validate_contorn = True

        elif (
            self.name_tif != "" and self.name_reference_binary != "" and self.name_reference_neural != "" and key == "5"
        ):
            root.geometry("800x600+50+10")
            self.ready_start = True

        elif self.name_tif != "" and self.name_reference_binary != "" and key == "5":
            # self.remove_buttons('Draw Menu')
            self.reference_binary = GdalManipulations.shp_to_bin(self, self.name_reference_binary, self.name_tif)
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

            self.screen_main, self.draw = Draw().create_screen_to_draw(self.screen_width, self.screen_height)
            self.screen_watershed, self.draw_watershed = Draw().create_screen_to_draw(
                self.screen_width, self.screen_height, "L"
            )

            self.cnt_validator = []

            self.buttons.next_btn.bind("<Button-1>", partial(self.button_click, key="1"))
            self.buttons.back_btn.bind("<Button-1>", partial(self.button_click, key="0"))

    def callback_opt(self, *args):
        if self.variable.get() == "Efetuar Marcacoes em Ortomosaicos":
            self.user_choosed = 'DRAW'
            if not os.path.isdir(self.path_save_img_rgb):
                os.makedirs(self.path_save_img_rgb, exist_ok=True)

            if not os.path.isdir(self.path_save_img_bin):
                os.makedirs(self.path_save_img_bin, exist_ok=True)

            if not os.path.isdir(self.path_save_img_negative):
                os.makedirs(self.path_save_img_negative, exist_ok=True)

            self.settings_labelling_menu()

        if self.variable.get() == "Analisar os Resultados":
            self.user_choosed = 'ANALISES'
            self.change_imgs = 0

            self.imgs_rgb_array, self.imgs_bin_array = LoadImagesAnalises('dataset/rgb', 'dataset/binario').load_images()
            self.labelling_start()
            self.screen_main, self.draw = Draw().create_screen_to_draw(self.screen_width, self.screen_height)
            self.buttons.next_btn.bind("<Button-1>", partial(self.button_click, key="1"))
            self.buttons.back_btn.bind("<Button-1>", partial(self.button_click, key="0"))


        self.old_choose = self.variable.get()

    def percent_progress(self, x, y, total_x, total_y):
        current_position = y / total_y
        current_position = round(current_position * 100, 2)
        return current_position

    def button_click(self, event=None, key=None):
        if self.bool_draw:
            self.save_draws()
        
        if self.user_choosed == "DRAW":
            
            if self.x_crop >= 0 and self.y_crop >= 0:
                string_text = str(self.x_crop) + "," + str(self.y_crop) + "," + str(self.name_tif) + ", \n"
                with open("log_progress.txt", "ab") as f:
                    f.write(string_text.encode("utf-8", "ignore"))

            if key == "1":
                self.bool_draw = True
                self.x_crop, self.y_crop, self.daninha_parcela = GdalManipulations().load_next_img_in_mosaic(self.x_crop, self.y_crop, self.iterator_x, self.iterator_y, self.background_percent, self.iterator_recoil, self.mosaico, self.daninha_band_1)

            elif key == "0":
                self.x_crop, self.y_crop, self.daninha_parcela = GdalManipulations().load_back_img_in_mosaic(self.x_crop, self.y_crop, self.iterator_x, self.iterator_y, self.background_percent, self.iterator_recoil, self.mosaico, self.daninha_band_1)

            self.imgparcela = GdalManipulations().get_image_rgb_by_band(
                self.x_crop, self.y_crop, self.iterator_x, self.iterator_y, self.mosaico, self.daninha_band_1
            )

            self.image_down = self.imgparcela.copy()
            self.image_down = cv2.resize(self.image_down, (self.screen_width, self.screen_height))
            if self.use_neural_network:
                self.validate_contorn = True
                self.array_screen_neural = np.array(self.screen_neural)
                img = self.neural_network.predict_image(self.imgparcela)
                if self.option_of_draw == "CNT":
                    self.contours = imp.find_contourns(self, img, self.screen_width, self.screen_height)
                    cv2.drawContours(self.array_screen_neural, self.contours, -1, (self.color_line_rgb + (255,)), 2)
                    self.screen_neural = Image.fromarray(self.array_screen_neural)
                    self.screen_main.paste(self.screen_neural, (0, 0), self.screen_neural)

                else:
                    img = imp.image_to_tk_screen(self, img, self.screen_width, self.screen_height, self.slider_opacity)
                    img = imp.color_to_transparency(self, img=img, color=self.color_line_rgb, transparency=self.slider_opacity)
                    self.screen_main.paste(img, (0, 0), img)

                self.update_img(self.screen_main)

            self.segmentation = np.zeros_like(self.image_down)

        if self.user_choosed == "ANALISES":       

            self.screen_marking, self.draw_marking = Draw().create_screen_to_draw(self.screen_width, self.screen_height)
            self.draw_marking_array = np.array(self.screen_marking)

            if key == "1":
                self.bool_draw = True
                self.imgparcela = cv2.imread(self.imgs_rgb_array[self.change_imgs])
                self.img_bin = cv2.imread(self.imgs_bin_array[self.change_imgs])
                self.img_bin = cv2.resize(self.img_bin, (self.screen_width, self.screen_height))

                if self.option_of_draw == "CNT":
                    self.img_bin = cv2.cvtColor(self.img_bin, cv2.COLOR_BGR2GRAY)
                    self.img_bin = self.img_bin.astype("uint8")
                    self.contours = imp.find_contourns(self, self.img_bin, self.screen_width, self.screen_height)
                    cv2.drawContours(self.draw_marking_array, self.contours, -1, (self.color_line_rgb + (255,)), 2)
                    self.draw_marking = Image.fromarray(self.draw_marking_array)
                
                else:
                    self.draw_marking = Image.fromarray(cv2.cvtColor(self.img_bin, cv2.COLOR_BGR2RGBA))
                    self.draw_marking = imp.color_to_transparency(self, self.draw_marking, self.color_line_rgb, transparency=self.slider_opacity)

                self.image_down = self.imgparcela.copy()
                self.screen_main.paste(self.draw_marking, (0, 0), self.draw_marking)
                self.change_imgs += 1

            elif key == "0":

                if self.change_imgs-1 < 0:
                    tk.messagebox.showinfo(title="Aviso", message="Esta é a Primeira Imagem")
                    pass
                
                elif self.change_imgs >= 1:
                    self.change_imgs -=1

                self.imgparcela = cv2.imread(self.imgs_rgb_array[self.change_imgs])
                self.img_bin = cv2.imread(self.imgs_bin_array[self.change_imgs])
                self.img_bin = cv2.resize(self.img_bin, (self.screen_width, self.screen_height))

                if self.option_of_draw == "CNT":
                    self.img_bin = cv2.cvtColor(self.img_bin, cv2.COLOR_BGR2GRAY)
                    self.img_bin = self.img_bin.astype("uint8")
                    self.contours = imp.find_contourns(self, self.img_bin, self.screen_width, self.screen_height)
                    cv2.drawContours(self.draw_marking_array, self.contours, -1, (self.color_line_rgb + (255,)), 2)
                    self.draw_marking = Image.fromarray(self.draw_marking_array)
                
                else:
                    self.draw_marking = Image.fromarray(cv2.cvtColor(self.img_bin, cv2.COLOR_BGR2RGBA))
                    self.draw_marking = imp.color_to_transparency(self, self.img_bin, self.color_line_rgb, transparency=self.slider_opacity)

                self.image_down = self.imgparcela.copy()
                self.screen_main.paste(self.draw_marking, (0, 0), self.draw_marking)


        self.img_array_tk = cv2.resize(self.imgparcela, (self.screen_width, self.screen_height))
        self.img_array_tk = PIL.Image.fromarray(self.img_array_tk)
        self.image_tk = ImageTk.PhotoImage(self.img_array_tk)
        self.first_click = True
        self.update_img(self.img_array_tk)

        self.canvas.bind("<Button-1>", self.get_x_and_y)
        self.canvas.bind("<Button 3>", self.get_right_click)
        self.canvas.bind("<B1-Motion>", self.draw_smth)
        self.frame_root.bind("<KeyPress>", self.keyboard)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_release)

    def change_color(self):
        color = askcolor(title="Selecione a cor para utilizar na marcação ")
        self.color_line_rgb = color[0]
        root.configure(bg=color[1])

    def get_right_click(self, event):
        self.current_points.clear()

    def use_nn(self):
        self.use_neural_network = True
        self.path_neural_network = "archives/vgg16_Linknet_3.hdf5"
        self.neural_network = NeuralFunctions(self.path_neural_network)
        self.screen_neural, _ = Draw().create_screen_to_draw(self.screen_width, self.screen_height)

    def mouse_release(self, event):
        self.update_img(self.screen_main)

    def get_x_and_y(self, event):
        scale = self.canvas_obj.get_coord_to_draw()[2]
        self.lasx = abs((self.canvas.canvasx(event.x)) + self.canvas_obj.get_coord_to_draw()[0]) / scale
        self.lasy = abs((self.canvas.canvasy(event.y)) + self.canvas_obj.get_coord_to_draw()[1]) / scale

        if self.polygon_draw_bool:
            self.current_points.append((self.lasx, self.lasy))
            self.draw = Draw().draw_polygon(self.current_points, self.draw, self.color_line_rgb, self.lasx, self.lasy, int(self.current_value_opacity.get()))
            self.update_img(self.screen_main)

        if self.use_neural_network and self.option_of_draw == "CNT" and self.validate_contorn:
            self.ctn = []
            if self.first_click == True:
                self.array_screen_neural = np.array(self.screen_neural)
                for i in range(0, len(self.contours)):
                    self.cnt_validator.append(False)

                self.first_click = False

            for i in range(0, len(self.cnt_validator)):
                r = cv2.pointPolygonTest(self.contours[i], (self.lasx, self.lasy), False)
                if r > 0:
                    self.cnt_validator[i] = not self.cnt_validator[i]
                    self.ctn = self.contours[i]

                    if self.cnt_validator[i] == True:
                        cv2.drawContours(self.array_screen_neural, [self.ctn], 0, (self.color_line_rgb + (255,)), 3)
                        cv2.fillPoly(self.array_screen_neural, pts=[self.ctn], color=(self.color_line_rgb + (self.slider_opacity,)),)

                    elif self.cnt_validator[i] == False:
                        cv2.drawContours(self.array_screen_neural, [self.ctn], 0, (0, 0, 0, 255), 3)
                        cv2.fillPoly(self.array_screen_neural, pts=[self.ctn], color=(0, 0, 0, self.slider_opacity))

                    self.screen_neural = Image.fromarray(self.array_screen_neural)
                    self.screen_main.paste(self.screen_neural, (0, 0), self.screen_neural)
                    self.update_img(self.screen_main)

            self.bool_draw = True
            self.update_img(self.screen_main)

        self.old_x = self.lasx
        self.old_y = self.lasy

    def draw_smth(self, event):
        scale = self.canvas_obj.get_coord_to_draw()[2]
        self.lasx = abs((self.canvas.canvasx(event.x)) + self.canvas_obj.get_coord_to_draw()[0]) / scale
        self.lasy = abs((self.canvas.canvasy(event.y)) + self.canvas_obj.get_coord_to_draw()[1]) / scale
        if self.pencil_draw_bool:
            self.draw = Draw().draw_countour(self.draw, self.color_line_rgb, self.old_x, self.old_y, self.lasx, self.lasy, int(self.current_value_opacity.get()), int(self.slider_pencil))
            self.bool_draw = True
            self.update_img(self.screen_main)

        elif not self.pencil_draw_bool and not self.polygon_draw_bool and not self.validate_contorn:
            self.draw.line(
                (self.old_x, self.old_y, self.lasx, self.lasy),
                (0, 0, 0, 0),
                width=int(self.slider_pencil / 2),
                joint="curve",
            )
            Offset = int(self.slider_pencil / 2)
            self.draw.ellipse(
                (self.lasx - Offset, self.lasy - Offset, self.lasx + Offset, self.lasy + Offset),
                (0, 0, 0, 0),
            )
            self.bool_draw = True
            self.update_img(self.screen_main)
            
        self.old_x = self.lasx
        self.old_y = self.lasy

    def update_img(self, img):
        self.image = np.array(self.image_down)
        self.image = cv2.resize(self.image, (self.screen_width, self.screen_height))
        self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2RGBA)
        self.image = PIL.Image.fromarray(self.image.copy())

        self.image.paste(self.screen_main, (0, 0), self.screen_main)
        self.image_final = ImageTk.PhotoImage(self.image)
        self.canvas_obj.update_image_canvas(self.image)
     
    def load_rgb_tif(self):

        path_rgb_shp = filedialog.askopenfilename(title="Selecione O Mosaico")
        if path_rgb_shp.endswith("tif"):

            self.mosaico = gdal.Open(path_rgb_shp)
            self.band_1 = self.mosaico.GetRasterBand(1)
            self.band_2 = self.mosaico.GetRasterBand(2)
            self.band_3 = self.mosaico.GetRasterBand(3)
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

    def save_progress(self):
        if self.x_crop >= 0 and self.y_crop >= 0:
            log_custom = LogCustom().register_log()
            string_text = str(self.x_crop) + "," + str(self.y_crop) + "," + str(self.name_tif) + "," + str(log_custom)
            with open("log_progress.txt", "ab") as f:
                f.write(string_text.encode("utf-8", "ignore"))

    def destroy_aplication(self):
        if self.user_choosed != 'ANALISES':
            self.save_progress()
            root.destroy()

    def eliminate_invalidated_contourns(self):
        self.array_screen_neural = np.array(self.screen_neural)

        for i in range(len(self.cnt_validator)):
            if self.cnt_validator[i] == True:
                cv2.drawContours(self.array_screen_neural, self.contours[i], -1, (0, 0, 0, 255), 5)
                cv2.fillPoly(self.array_screen_neural, pts=[self.contours[i]], color=(0, 0, 0, 255))
            
                self.screen_neural = Image.fromarray(self.array_screen_neural)
                self.screen_neural = imp.color_to_transparency(self, img=self.screen_neural, color=(0, 0, 0), transparency=self.slider_opacity)
                self.screen_main.paste(self.screen_neural, (0, 0), self.screen_neural)
                imp.color_to_transparency
                self.update_img(self.screen_main)

    def updade_contourns(self):
        self.array_screen_neural = np.array(self.screen_neural)

        for i in range(len(self.cnt_validator)):
            if self.cnt_validator[i] == True:
                cv2.drawContours(self.array_screen_neural, self.contours[i], -1, (self.color_line_rgb + (255,)), 3)
                cv2.fillPoly(
                    self.array_screen_neural,
                    pts=[self.contours[i]],
                    color=(self.color_line_rgb + (self.slider_opacity,)),
                )

            else:
                cv2.drawContours(self.array_screen_neural, self.contours[i], -1, (0, 0, 0, 255), 3)
                cv2.fillPoly(self.array_screen_neural, pts=[self.contours[i]], color=(0, 0, 0, 255))
            
        self.screen_neural = Image.fromarray(self.array_screen_neural)
        self.screen_main.paste(self.screen_neural, (0, 0), self.screen_neural)


    def save_draws(self):
        if self.user_choosed == 'DRAW':
            #self.eliminate_invalidated_contourns()
            self.cnt_validator = []
            self.save_progress()

            if self.polygon_draw_bool:
                self.current_points.clear()
                self.polygon_draw_bool = False 

            self.current_value_saturation.set(0.0)

            self.save_draw_array = np.asarray(self.screen_main)
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

                self.screen_neural, _, = Draw().reset_draw_screen(self.screen_main, self.screen_watershed, self.screen_width, self.screen_height, option="CLEAN_JUST_OUTLINE_RGB")


                self.screen_main, self.draw, self.screen_watershed, self.draw_watershed = Draw().reset_draw_screen(
                    self.screen_main, self.screen_watershed, self.screen_width, self.screen_height
                )

        if self.user_choosed == "ANALISES":        
            self.screen_marking, _  = Draw().reset_draw_screen(outline_rgb=self.screen_marking, outline_gray=self.draw_marking,screen_width=self.screen_width, screen_height=self.screen_height, option="CLEAN_JUST_OUTLINE_RGB"
                )

        self.screen_main, self.draw = Draw().reset_draw_screen(self.screen_main, self.draw, self.screen_width, self.screen_height, option="CLEAN_JUST_OUTLINE_RGB")


if __name__ == "__main__":
    root = tk.Tk()
    obj = Interface(root)
    root.title("WeeDraw")
    root.resizable(False, False)
    obj.first_menu(root)
    root.geometry("800x800+50+10")
    root.rowconfigure(0, weight=0)  
    root.columnconfigure(0, weight=0)
    root.protocol("WM_DELETE_WINDOW", obj.destroy_aplication)
    root.mainloop()
