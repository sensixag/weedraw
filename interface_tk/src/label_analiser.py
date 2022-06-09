import numpy as np
import os
import pathlib
import PIL
import cv2
import sys
import time
import warnings

from tkinter.colorchooser import askcolor
from functools import partial

from callbacks_tk import Screen
from tkinter import Button, PhotoImage, messagebox as mbox
from menu import ButtonSettingsLabelling, ButtonsLabelling
from imgs_manipulations import *
from imgs_manipulations import ImagesManipulations as imp
from draw import Draw
from zoom import *

class LabelAnaliser(tk.Frame):
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

        self.option_of_draw = "CNT"
        self.pencil_draw_bool = True
        self.polygon_draw_bool = False
        self.validate_contorn = False
        self.opacity = False
        self.bool_draw = False
        self.bool_save_image = tk.IntVar()
        self.color_line_rgb = (255, 0, 0)
        self.frame_root = root
        
        self.path_save_img_bin = "dataset/binario"
        
        self.current_value_saturation = tk.DoubleVar()
        self.current_value_contourn = tk.DoubleVar()
        self.current_value_opacity = tk.DoubleVar()
        self.current_value_erase = tk.DoubleVar()
        
        self.OptionList = ["Analisar os Resultados"]
        self.slider_pencil = 1

        root.maxsize(self.width_size, self.hight_size)
        root.resizable(False, False)

        img = ImageTk.PhotoImage(file=r"../icons/icone_sensix.png")
        root.call("wm", "iconphoto", root._w, img)


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
        self.set_slider_erase = tk.Label(root, text="")

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
        self.label_contourn.place(relx=0.059, rely=0.247, height=21, width=50)
        self.label_contourn.configure(text="Lapis:", fg=self.color_buttons_center, bg=self.color_frame_options)

        self.label_erase = tk.Label(self.frame_of_options)
        self.label_erase.place(relx=0.059, rely=0.356, height=21, width=73)
        self.label_erase.configure(text="Borracha:", fg=self.color_buttons_center, bg=self.color_frame_options)

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

        self.slider_erase = tk.Scale(
            self.frame_of_options,
            from_=1.0,
            to=100.0,
            command= self.slider_changed_erase,
            variable=self.current_value_erase,
        )
        self.slider_erase.place(relx=0.098, rely=0.380, relheight=0.062, relwidth=0.8)

        self.slider_erase.configure(
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

        self.button_save_image = tk.Checkbutton(self.frame_of_options, text="Salvar Modificações ", variable=self.bool_save_image, onvalue=1, offvalue=0, background=self.color_frame_options, bg='white')
        self.button_save_image.place(x=22, y=390, width=165)

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
        self.buttons.close_btn.bind("<Button-1>", partial(self.get_btn, key="Close"))
        self.buttons.next_btn.bind("<Button-1>", partial(self.get_btn, key="Next"))
        self.buttons.back_btn.bind("<Button-1>", partial(self.get_btn, key="Back"))

        self.button_select_color = tk.Button(root, text="Cor para marcação", command=self.change_color)
        self.button_select_color.place(relx=0.025, rely=0.48, height=43, width=165)
        self.button_select_color.configure(bg='white')

        #self.img_canvas_id = self.canvas.create_image(0, 0, anchor='nw')

        self.current_value_opacity.set(50.0)
        self.current_value_contourn.set(1)

    def keyboard(self, event):
        self.key_pressed = event.char
        self.key_code = event.keycode

        if self.key_code == 32 or self.key_code == 65:
            self.fill()

    def fill(self):
        self.array_screen_neural = np.asarray(self.screen_main)
        img = imp.prepare_array(self, self.array_screen_neural, self.screen_width, self.screen_height, False)

        contours = imp.find_contourns(self, img, self.screen_width, self.screen_height)
        cv2.fillPoly(self.array_screen_neural, pts=contours, color=(self.color_line_rgb + (self.slider_opacity,)),)
        self.screen_neural = Image.fromarray(self.array_screen_neural)
        self.screen_main.paste(self.screen_neural, (0, 0), self.screen_neural)

        self.update_img(self.screen_main)

    def button_click(self, event=None, key=None):
        if self.bool_draw:
            self.save_draws()
        
        if self.user_choosed == "ANALISES":       

            self.screen_marking, self.draw_marking = Draw().create_screen_to_draw(self.screen_width, self.screen_height)
            self.draw_marking_array = np.array(self.screen_marking)

            if key == "1":
                self.bool_draw = True
                self.current_bin_name = self.imgs_bin_array[self.change_imgs]
                self.current_rgb_name = self.imgs_rgb_array[self.change_imgs]
                self.imgparcela = cv2.imread(self.current_rgb_name)
                self.img_bin = cv2.imread(self.current_bin_name)
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

                if self.change_imgs+1 == len(self.imgs_rgb_array):
                    tk.messagebox.showinfo(title="Aviso", message="Esta é Ultima Imagem")

                elif self.change_imgs < len(self.imgs_rgb_array):
                    self.change_imgs +=1

            elif key == "0":

                if self.change_imgs-1 < 0:
                    tk.messagebox.showinfo(title="Aviso", message="Esta é a Primeira Imagem")
                
                elif self.change_imgs >= 1:
                    self.change_imgs -=1

                self.current_bin_name = self.imgs_bin_array[self.change_imgs]
                self.current_rgb_name = self.imgs_rgb_array[self.change_imgs]                
                
                self.imgparcela = cv2.imread(self.current_rgb_name)
                self.img_bin = cv2.imread(self.current_bin_name)
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

    def get_right_click(self, event):
        self.current_points.clear()


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
                width=int(self.slider_erase / 2),
                joint="curve",
            )
            Offset = int(self.slider_erase / 2)
            self.draw.ellipse(
                (self.lasx - Offset, self.lasy - Offset, self.lasx + Offset, self.lasy + Offset),
                (0, 0, 0, 0),
            )
            self.bool_draw = True
            self.update_img(self.screen_main)
            
        self.old_x = self.lasx
        self.old_y = self.lasy

    def change_color(self):
        color = askcolor(title="Selecione a cor para utilizar na marcação ")
        self.color_line_rgb = color[0]
        root.configure(bg=color[1])

    def get_current_value_opacity(self):
        self.slider_opacity = int(self.current_value_opacity.get())

    def slider_changed_opacity(self, event):
        self.set_slider_opacity.configure(text=self.get_current_value_opacity())

    def get_current_value_saturation(self):
        self.slider_saturation = int(self.current_value_saturation.get())
        if self.bool_draw:
            self.image_down = SatureImg().saturation(self.imgparcela, increment=self.slider_saturation)

        if self.slider_saturation <= 10:
            self.image_down = self.imgparcela.copy()

        self.update_img(self.screen_main)
        self.slider_saturation_old = self.slider_saturation

    def slider_changed_erase(self, event):
        self.slider_erase = self.current_value_erase.get()
        self.set_slider_erase.configure(text=self.current_value_erase.get())

    def slider_changed_saturation(self, event):
        self.set_slider_saturation.configure(text=self.get_current_value_saturation())

    def slider_changed_contourn(self, event):
        self.slider_pencil = self.current_value_contourn.get()
        if self.slider_pencil < 1:
            self.slider_pencil = 1

        self.set_slider_contourn.configure(text=self.current_value_contourn.get())


    def save_draws(self):
        if self.bool_save_image.get() == 1:
            self.bool_save_image.set(0)
            self.fill()

            if self.polygon_draw_bool:
                self.current_points.clear()
                self.polygon_draw_bool = False
               
            self.current_value_saturation.set(0.0)

            self.save_draw_array = np.asarray(self.screen_main)
            self.save_draw_array = imp.prepare_array(self, self.save_draw_array, self.iterator_x, self.iterator_y)
            
            cv2.imwrite(self.current_bin_name, self.save_draw_array)
                   
        self.screen_marking, _  = Draw().reset_draw_screen(outline_rgb=self.screen_marking, outline_gray=self.draw_marking,screen_width=self.screen_width, screen_height=self.screen_height, option="CLEAN_JUST_OUTLINE_RGB")
        self.screen_main, self.draw = Draw().reset_draw_screen(self.screen_main, self.draw, self.screen_width, self.screen_height, option="CLEAN_JUST_OUTLINE_RGB")


    def update_img(self, img):
        self.image = np.array(self.image_down)
        self.image = cv2.resize(self.image, (self.screen_width, self.screen_height))
        self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2RGBA)
        self.image = PIL.Image.fromarray(self.image.copy())

        self.image.paste(self.screen_main, (0, 0), self.screen_main)
        self.image_final = ImageTk.PhotoImage(self.image)
        self.canvas_obj.update_image_canvas(self.image)

    def remove_current_img(self, remove_img):
        if remove_img:
            print(self.imgs_bin_array[self.change_imgs])
            os.system('rm ' + str(self.current_bin_name))
            os.system('rm ' + str(self.current_rgb_name))
            tk.messagebox.showinfo(message="Imagem Excluida!!")
            self.imgs_rgb_array.remove(self.current_rgb_name)
            self.imgs_bin_array.remove(self.current_bin_name)

        else:
            tk.messagebox.showinfo(message="Imagem não Excluida")

    def get_btn(self, event, key):
        if key == "Close":
            print("Close")
            remove_img_answer = tk.messagebox.askquestion("Excluir Imagem?", "Você quer realmente excluir esta imagem?")
            self.remove_current_img(remove_img_answer)

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

    def callback_opt(self, *args):

        if self.variable.get() == "Analisar os Resultados":
            self.user_choosed = 'ANALISES'
            self.change_imgs = 0

            self.imgs_rgb_array, self.imgs_bin_array = LoadImagesAnalises('dataset/rgb', 'dataset/binario').load_images()
            self.labelling_start()
            self.screen_main, self.draw = Draw().create_screen_to_draw(self.screen_width, self.screen_height)
            self.buttons.next_btn.bind("<Button-1>", partial(self.button_click, key="1"))
            self.buttons.back_btn.bind("<Button-1>", partial(self.button_click, key="0"))

if __name__ == "__main__":
    root = tk.Tk()
    obj = LabelAnaliser(root)
    root.title("WeeDraw Analiser")
    root.resizable(False, False)
    obj.first_menu(root)
    root.geometry("800x800+50+10")
    root.rowconfigure(0, weight=0)  
    root.columnconfigure(0, weight=0)
    root.mainloop()
