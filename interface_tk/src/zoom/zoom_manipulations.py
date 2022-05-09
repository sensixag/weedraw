# -*- coding: utf-8 -*-
import math
import numpy as np
import imgaug as im
import warnings
import tkinter as tk
import copy

from tkinter import ttk
from PIL import Image, ImageTk

class AutoScrollbar(ttk.Scrollbar):
    """ A scrollbar that hides itself if it's not needed. Works only for grid geometry manager """
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with the widget ' + self.__class__.__name__)

    def place(self, **kw):
        raise tk.TclError('Cannot use place with the widget ' + self.__class__.__name__)

class CanvasImage:
    """ Display and zoom image """
    def __init__(self, tk_menu, placeholder, image):
        """ Initialize the ImageFrame """
        self.imscale = 1.0
        self.__delta = 1.3
        self.filter = Image.ANTIALIAS
        self.tk_menu = tk_menu
        self.image_original = image  
        self.__imframe = placeholder
        self.screen_width = 800
        self.screen_height = 700
        self.__previous_state = 0
        self.corner_left_img, self.corner_right_img = (0, 0)
        hbar = AutoScrollbar(self.__imframe, orient='horizontal')
        vbar = AutoScrollbar(self.__imframe, orient='vertical')
        hbar.grid(row=0, column=0, sticky='we')
        vbar.grid(row=0, column=0, sticky='ns')

        self.canvas = self.tk_menu.Canvas(self.__imframe, highlightthickness=0,
                                          xscrollcommand=hbar.set, yscrollcommand=vbar.set, 
                                          bd=0, width=self.screen_width, height=self.screen_height,)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.canvas.update()
        hbar.configure(command=self.scroll_x)
        vbar.configure(command=self.scroll_y)
        self.canvas.bind('<Configure>', lambda event: self.show_image())  
        self.canvas.bind('<ButtonPress-1>', self.move_from)  
        self.canvas.bind('<B1-Motion>',     self.move_to)
        self.canvas.bind('<MouseWheel>', self.wheel)
        self.canvas.bind('<Button-5>',   self.wheel)
        self.canvas.bind('<Button-4>',   self.wheel)

        self.__huge = False
        self.__huge_size = 14000
        self.__band_width = 1024
        Image.MAX_IMAGE_PIXELS = 1000000000
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.image = self.image_original.copy() 
        self.imwidth, self.imheight = self.image.size
        if self.imwidth * self.imheight > self.__huge_size * self.__huge_size and \
           self.image.tile[0][0] == 'raw':
            self.__huge = True
            self.__offset = self.image.tile[0][2]
            self.__tile = [self.image.tile[0][0],
                           [0, 0, self.imwidth, 0],
                           self.__offset,
                           self.image.tile[0][3]]
        self.__min_side = min(self.imwidth, self.imheight)

        self.pyramid = [self.smaller()] if self.__huge else [self.image_original]

        self.__ratio = max(self.imwidth, self.imheight) / self.__huge_size if self.__huge else 1.0
        self.__curr_img = 0
        self.scale = self.imscale * self.__ratio
        self.__reduction = 2
        w, h = self.pyramid[-1].size
        while w > 512 and h > 512:
            w /= self.__reduction
            h /= self.__reduction
            self.pyramid.append(self.pyramid[-1].resize((int(w), int(h)), self.filter))

        self.container = self.canvas.create_rectangle((0, 0, 800, 700), width=0)
        self.img_canvas_id = self.canvas.create_image(0, 0, anchor='nw')
        self.canvas.lower(self.img_canvas_id)
        
        self.show_image() 
        self.canvas.focus_set() 

    def define_canvas(self):
        return self.canvas
        
    def smaller(self):
        """ Resize image proportionally and return smaller image """
        w1, h1 = float(self.imwidth), float(self.imheight)
        w2, h2 = float(self.__huge_size), float(self.__huge_size)
        aspect_ratio1 = w1 / h1
        aspect_ratio2 = w2 / h2
        if aspect_ratio1 == aspect_ratio2:
            image = Image.new('RGB', (int(w2), int(h2)))
            k = h2 / h1 
            w = int(w2) 
        elif aspect_ratio1 > aspect_ratio2:
            image = Image.new('RGB', (int(w2), int(w2 / aspect_ratio1)))
            k = h2 / w1
            w = int(w2)
        else:
            image = Image.new('RGB', (int(h2 * aspect_ratio1), int(h2)))
            k = h2 / h1
            w = int(h2 * aspect_ratio1)
        i, j, n = 0, 1, round(0.5 + self.imheight / self.__band_width)
        while i < self.imheight:
            band = min(self.__band_width, self.imheight - i)
            self.__tile[1][3] = band
            self.__tile[2] = self.__offset + self.imwidth * i * 3 
            self.image.size = (self.imwidth, band)
            self.image.tile = [self.__tile]
            cropped = self.image.crop((0, 0, self.imwidth, band))
            image.paste(cropped.resize((w, int(band * k)+1), self.filter), (0, int(i * k)))
            i += band
            j += 1
        return image

    def redraw_figures(self):
        """ Dummy function to redraw figures in the children classes """
        pass

    def grid(self, **kw):
        """ Put CanvasImage widget on the parent widget """
        self.__imframe.grid(**kw)
        self.__imframe.grid(sticky='nswe')
        self.__imframe.rowconfigure(0, weight=1)
        self.__imframe.columnconfigure(0, weight=1)

    def pack(self, **kw):
        """ Exception: cannot use pack with this widget """
        raise Exception('Cannot use pack with the widget ' + self.__class__.__name__)

    def place(self, **kw):
        """ Exception: cannot use place with this widget """
        raise Exception('Cannot use place with the widget ' + self.__class__.__name__)

    def scroll_x(self, *args, **kwargs):
        """ Scroll canvas horizontally and redraw the image """
        self.canvas.xview(*args)
        self.show_image()

    def scroll_y(self, *args, **kwargs):
        """ Scroll canvas vertically and redraw the image """
        self.canvas.yview(*args)
        self.show_image() 

    def update_image_canvas(self, image):
        self.image = image
        self.image_original = ImageTk.PhotoImage(self.image)
        self.huge = False
        self.huge_size = 14000 
        self.band_width = 1024 
        self.filter = Image.ANTIALIAS
        Image.MAX_IMAGE_PIXELS = 1000000000
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
        self.imwidth, self.imheight = self.image.size
        if self.imwidth * self.imheight > self.huge_size * self.huge_size and \
        self.image.tile[0][0] == 'raw':
            self.huge = True
            self.offset = self.image.tile[0][2]  
            self.tile = [self.image.tile[0][0], 
                        [0, 0, self.imwidth, 0],
                        self.offset,
                        self.image.tile[0][3]]
        self.min_side = min(self.imwidth, self.imheight)

        self.pyramid = [self.smaller()] if self.huge else [self.image]

        self.ratio = max(self.imwidth, self.imheight) / self.huge_size if self.huge else 1.0
        self.curr_img = 0
        self.scale = self.imscale * self.ratio
        self.reduction = 2
        w, h = self.pyramid[-1].size
        while w > 512 and h > 512: 
            w /= self.reduction 
            h /= self.reduction 
            self.pyramid.append(self.pyramid[-1].resize((int(w), int(h)), self.filter))
        self.show_image()
        self.canvas.focus_set()

    def show_image(self):
        """ Show image on the Canvas. Implements correct image zoom almost like in Google Maps """
        box_image = self.canvas.coords(self.container)
        box_canvas = (self.canvas.canvasx(0),
                      self.canvas.canvasy(0),
                      self.canvas.canvasx(self.canvas.winfo_width()),
                      self.canvas.canvasy(self.canvas.winfo_height()))
        
        box_img_int = tuple(map(int, box_image)) 

        box_scroll = [min(box_img_int[0], box_canvas[0]), min(box_img_int[1], box_canvas[1]),
                      max(box_img_int[2], box_canvas[2]), max(box_img_int[3], box_canvas[3])]

        if  box_scroll[0] == box_canvas[0] and box_scroll[2] == box_canvas[2]:
            box_scroll[0]  = box_img_int[0]
            box_scroll[2]  = box_img_int[2]

        if  box_scroll[1] == box_canvas[1] and box_scroll[3] == box_canvas[3]:
            box_scroll[1]  = box_img_int[1]
            box_scroll[3]  = box_img_int[3]

        self.canvas.configure(scrollregion=tuple(map(int, box_scroll)))

        x1 = max(box_canvas[0] - box_image[0], 0)
        y1 = max(box_canvas[1] - box_image[1], 0)
        x2 = min(box_canvas[2], box_image[2]) - box_image[0]
        y2 = min(box_canvas[3], box_image[3]) - box_image[1]

        self.upper_left = int(x1 / self.scale)
        self.upper_right = int(x2 / self.scale)
        self.bottom_left = int(y1 / self.scale)
        self.bottom_right = int(y2 / self.scale)

        if int(x2 - x1) > 0 and int(y2 - y1) > 0: 
            if self.__huge and self.__curr_img < 0:
                h = int((y2 - y1) / self.imscale)
                self.__tile[1][3] = h
                self.__tile[2] = self.__offset + self.imwidth * int(y1 / self.imscale) * 3
                self.image.size = (self.imwidth, h)
                self.image.tile = [self.__tile]
                image = self.image.crop((int(x1 / self.imscale), 0, int(x2 / self.imscale), h))
            else:  # show normal image
                image = self.pyramid[max(0, self.__curr_img)].crop(
                                    (int(x1 // self.scale), int(y1 / self.scale),
                                     int(x2 // self.scale), int(y2 / self.scale)))
     
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1)), self.filter))
            self.canvas.imagetk = imagetk
            self.corner_left_img, self.corner_right_img, _ = self.coord_zoom_to_draw((box_canvas[0], box_img_int[0]), (box_canvas[1], box_img_int[1]))            
            self.canvas.coords(self.img_canvas_id, self.corner_left_img, self.corner_right_img)
            self.show(imagetk)

    def move_from(self, event):
        """ Remember previous coordinates for scrolling with the mouse """
        self.canvas.scan_mark(event.x, event.y)

    def coord_zoom_to_draw(self, left_corner, right_corner):
        
        corner_left_img = max(left_corner)
        corner_right_img = max(right_corner)
        return corner_left_img, corner_right_img, self.scale

    def get_coord_to_draw(self):

        if self.corner_left_img > 0 and self.corner_right_img < 0:
            x_pos = -1*(abs(self.corner_left_img)) + self.scale * self.upper_left
            y_pos = abs(self.corner_right_img) + self.scale * self.bottom_left

        elif self.corner_left_img < 0 and self.corner_right_img > 0:
            x_pos = abs(self.corner_left_img) + self.scale * self.upper_left
            y_pos = -1*(abs(self.corner_right_img)) + self.scale * self.bottom_left

        elif self.corner_left_img > 0 and self.corner_right_img > 0:
            x_pos = abs(self.corner_left_img) + self.scale * self.upper_left
            y_pos = abs(self.corner_right_img) + self.scale * self.bottom_left

        elif self.corner_left_img < 0 and self.corner_right_img < 0:
            x_pos = -1*(abs(self.corner_left_img)) + self.scale * self.upper_left
            y_pos = -1*(abs(self.corner_right_img)) + self.scale * self.bottom_left

        elif self.corner_left_img == 0 and self.corner_right_img == 0:
            x_pos = self.scale * self.upper_left
            y_pos = self.scale * self.bottom_left

        else:
            x_pos = 0
            y_pos = 0
            self.scale = 1

        return x_pos, y_pos, self.scale

    def move_to(self, event):
        """ Drag (move) canvas to the new position """
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()

    def outside(self, x, y):
        """ Checks if the point (x,y) is outside the image area """
        bbox = self.canvas.coords(self.container)
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            return False
        else:
            return True

    def show(self, img):
        self.canvas.itemconfig(self.img_canvas_id, image=img)

    def wheel(self, event):
        """ Zoom with mouse wheel """
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.outside(x, y): return
        scale = 1.0

        if event.num == 5 or event.delta == -120:
            if round(self.__min_side * self.imscale) < 800: return
            self.imscale /= self.__delta
            scale        /= self.__delta
        if event.num == 4 or event.delta == 120:
            if round(self.imscale, 1) == 1.0:
                self.current_x = x
                self.current_y = y 
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height()) >> 1
            if i < self.imscale: return
            self.imscale *= self.__delta
            scale        *= self.__delta
        
        k = self.imscale * self.__ratio 
        self.__curr_img = min((-1) * int(math.log(k, self.__reduction)), len(self.pyramid) - 1)
        self.scale = k * math.pow(self.__reduction, max(0, self.__curr_img))

        self.canvas.scale('all', self.current_x, self.current_y, scale, scale)  

        self.redraw_figures()
        self.show_image()

    def crop(self, bbox):
        """ Crop rectangle from the image and return it """
        if self.__huge:
            band = bbox[3] - bbox[1]  
            self.__tile[1][3] = band
            self.__tile[2] = self.__offset + self.imwidth * bbox[1] * 3  
            self.image.size = (self.imwidth, band)
            self.image.tile = [self.__tile]
            return self.image.crop((bbox[0], 0, bbox[2], band))
        else:
            return self.pyramid[0].crop(bbox)

    def destroy(self):
        """ ImageFrame destructor """
        self.image.close()
        map(lambda i: i.close, self.pyramid)
        del self.pyramid[:]
        del self.pyramid
        self.canvas.destroy()
        self.__imframe.destroy()