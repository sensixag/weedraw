# -*- coding: utf-8 -*-
# Advanced zoom for images of various types from small to huge up to several GB
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
        self.imscale = 1.0  # scale for the canvas image zoom, public for outer classes
        self.__delta = 1.3  # zoom magnitude
        self.filter = Image.ANTIALIAS  # could be: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
        self.__previous_state = 0  # previous state of the keyboard
        self.tk_menu = tk_menu
        self.image_original = image  # path to the image, should be public for outer classes
        # Create ImageFrame in placeholder widget
        self.__imframe = placeholder  # placeholder of the ImageFrame object
        # Vertical and horizontal scrollbars for canvas
        self.screen_width = 800
        self.screen_height = 700
        self.corner_left_img, self.corner_right_img = (0, 0)
        hbar = AutoScrollbar(self.__imframe, orient='horizontal')
        vbar = AutoScrollbar(self.__imframe, orient='vertical')
        hbar.grid(row=1, column=0, sticky='we')
        vbar.grid(row=0, column=1, sticky='ns')
        # Create canvas and bind it with scrollbars. Public for outer classes
        self.canvas = self.tk_menu.Canvas(self.__imframe, highlightthickness=0,
                                          xscrollcommand=hbar.set, yscrollcommand=vbar.set, 
                                          bd=0, width=self.screen_width, height=self.screen_height,)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.canvas.update()  # wait till canvas is created
        hbar.configure(command=self.scroll_x)  # bind scrollbars to the canvas
        vbar.configure(command=self.scroll_y)
        # Bind events to the Canvas
        self.canvas.bind('<Configure>', lambda event: self.show_image())  # canvas is resized
        self.canvas.bind('<ButtonPress-1>', self.move_from)  # remember canvas position
        self.canvas.bind('<B1-Motion>',     self.move_to)  # move canvas to the new position
        self.canvas.bind('<MouseWheel>', self.wheel)  # zoom for Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>',   self.wheel)  # zoom for Linux, wheel scroll down
        self.canvas.bind('<Button-4>',   self.wheel)  # zoom for Linux, wheel scroll up
        # Handle keystrokes in idle mode, because program slows down on a weak computers,
        # when too many key stroke events in the same time
        self.canvas.bind('<Key>', lambda event: self.canvas.after_idle(self.__keystroke, event))
        # Decide if this image huge or not
        self.__huge = False  # huge or not
        self.__huge_size = 14000  # define size of the huge image
        self.__band_width = 1024  # width of the tile band
        Image.MAX_IMAGE_PIXELS = 1000000000  # suppress DecompressionBombError for the big image
        with warnings.catch_warnings():  # suppress DecompressionBombWarning
            warnings.simplefilter('ignore')
            self.image = self.image_original.copy()  # open image, but down't load it
        self.imwidth, self.imheight = self.image.size  # public for outer classes
        if self.imwidth * self.imheight > self.__huge_size * self.__huge_size and \
           self.image.tile[0][0] == 'raw':  # only raw images could be tiled
            self.__huge = True  # image is huge
            self.__offset = self.image.tile[0][2]  # initial tile offset
            self.__tile = [self.image.tile[0][0],  # it have to be 'raw'
                           [0, 0, self.imwidth, 0],  # tile extent (a rectangle)
                           self.__offset,
                           self.image.tile[0][3]]  # list of arguments to the decoder
        self.__min_side = min(self.imwidth, self.imheight)  # get the smaller image side
        # Create image pyramid
        self.pyramid = [self.smaller()] if self.__huge else [self.image_original]
        # Set ratio coefficient for image pyramid
        self.__ratio = max(self.imwidth, self.imheight) / self.__huge_size if self.__huge else 1.0
        self.__curr_img = 0  # current image from the pyramid
        self.scale = self.imscale * self.__ratio  # image pyramide scale
        self.__reduction = 2  # reduction degree of image pyramid
        w, h = self.pyramid[-1].size
        while w > 512 and h > 512:  # top pyramid image is around 512 pixels in size
            w /= self.__reduction  # divide on reduction degree
            h /= self.__reduction  # divide on reduction degree
            self.pyramid.append(self.pyramid[-1].resize((int(w), int(h)), self.filter))
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle((0, 0, self.imwidth, self.imheight), width=0)
        self.img_canvas_id = self.canvas.create_image(0, 0, anchor='nw')
        self.canvas.lower(self.img_canvas_id)  # set image into background
        
        self.show_image()  # show image on the canvas
        self.canvas.focus_set()  # set focus on the canvas


    def define_canvas(self):
        return self.canvas
        
    def smaller(self):
        """ Resize image proportionally and return smaller image """
        w1, h1 = float(self.imwidth), float(self.imheight)
        w2, h2 = float(self.__huge_size), float(self.__huge_size)
        aspect_ratio1 = w1 / h1
        aspect_ratio2 = w2 / h2  # it equals to 1.0
        if aspect_ratio1 == aspect_ratio2:
            image = Image.new('RGB', (int(w2), int(h2)))
            k = h2 / h1  # compression ratio
            w = int(w2)  # band length
        elif aspect_ratio1 > aspect_ratio2:
            image = Image.new('RGB', (int(w2), int(w2 / aspect_ratio1)))
            k = h2 / w1  # compression ratio
            w = int(w2)  # band length
        else:  # aspect_ratio1 < aspect_ration2
            image = Image.new('RGB', (int(h2 * aspect_ratio1), int(h2)))
            k = h2 / h1  # compression ratio
            w = int(h2 * aspect_ratio1)  # band length
        i, j, n = 0, 1, round(0.5 + self.imheight / self.__band_width)
        while i < self.imheight:
            band = min(self.__band_width, self.imheight - i)  # width of the tile band
            self.__tile[1][3] = band  # set band width
            self.__tile[2] = self.__offset + self.imwidth * i * 3  # tile offset (3 bytes per pixel)
            self.image.size = (self.imwidth, band)  # set size of the tile band
            self.image.tile = [self.__tile]  # set tile
            cropped = self.image.crop((0, 0, self.imwidth, band))  # crop tile band
            image.paste(cropped.resize((w, int(band * k)+1), self.filter), (0, int(i * k)))
            i += band
            j += 1
        return image

    def redraw_figures(self):
        """ Dummy function to redraw figures in the children classes """
        pass

    def grid(self, **kw):
        """ Put CanvasImage widget on the parent widget """
        self.__imframe.grid(**kw)  # place CanvasImage widget on the grid
        self.__imframe.grid(sticky='nswe')  # make frame container sticky
        self.__imframe.rowconfigure(0, weight=1)  # make canvas expandable
        self.__imframe.columnconfigure(0, weight=1)

    def pack(self, **kw):
        """ Exception: cannot use pack with this widget """
        raise Exception('Cannot use pack with the widget ' + self.__class__.__name__)

    def place(self, **kw):
        """ Exception: cannot use place with this widget """
        raise Exception('Cannot use place with the widget ' + self.__class__.__name__)

    # noinspection PyUnusedLocal
    def scroll_x(self, *args, **kwargs):
        """ Scroll canvas horizontally and redraw the image """
        self.canvas.xview(*args)  # scroll horizontally
        self.show_image()  # redraw the image

    # noinspection PyUnusedLocal
    def scroll_y(self, *args, **kwargs):
        """ Scroll canvas vertically and redraw the image """
        self.canvas.yview(*args)  # scroll vertically
        self.show_image()  # redraw the image


    def update_image_canvas(self, image):
        self.image = image
        self.image_original = ImageTk.PhotoImage(self.image)
        self.huge = False  # huge or not
        self.huge_size = 14000  # define size of the huge image
        self.band_width = 1024  # width of the tile band
        self.filter = Image.ANTIALIAS
        Image.MAX_IMAGE_PIXELS = 1000000000  # suppress DecompressionBombError for the big image
        with warnings.catch_warnings():  # suppress DecompressionBombWarning
            warnings.simplefilter('ignore')
        self.imwidth, self.imheight = self.image.size  # public for outer classes
        if self.imwidth * self.imheight > self.huge_size * self.huge_size and \
        self.image.tile[0][0] == 'raw':  # only raw images could be tiled
            self.huge = True  # image is huge
            self.offset = self.image.tile[0][2]  # initial tile offset
            self.tile = [self.image.tile[0][0],  # it have to be 'raw'
                        [0, 0, self.imwidth, 0],  # tile extent (a rectangle)
                        self.offset,
                        self.image.tile[0][3]]  # list of arguments to the decoder
        self.min_side = min(self.imwidth, self.imheight)  # get the smaller image side
        # Create image pyramid
        self.pyramid = [self.smaller()] if self.huge else [self.image]
        # Set ratio coefficient for image pyramid
        self.ratio = max(self.imwidth, self.imheight) / self.huge_size if self.huge else 1.0
        self.curr_img = 0  # current image from the pyramid
        self.scale = self.imscale * self.ratio  # image pyramide scale
        self.reduction = 2  # reduction degree of image pyramid
        w, h = self.pyramid[-1].size
        while w > 512 and h > 512:  # top pyramid image is around 512 pixels in size
            w /= self.reduction  # divide on reduction degree
            h /= self.reduction  # divide on reduction degree
            self.pyramid.append(self.pyramid[-1].resize((int(w), int(h)), self.filter))
        # Put image into container rectangle and use it to set proper coordinates to the image
        #self.container = self.canvas.create_rectangle((0, 0, self.imwidth, self.imheight), width=0)
        self.show_image()  # show image on the canvas
        self.canvas.focus_set()  # set focus on the canvas

    def show_image(self):
        """ Show image on the Canvas. Implements correct image zoom almost like in Google Maps """
        box_image = self.canvas.coords(self.container)  # get image area
        box_canvas = (self.canvas.canvasx(0),  # get visible area of the canvas
                      self.canvas.canvasy(0),
                      self.canvas.canvasx(self.canvas.winfo_width()),
                      self.canvas.canvasy(self.canvas.winfo_height()))
        box_img_int = tuple(map(int, box_image))  # convert to integer or it will not work properly
        # Get scroll region box
        box_scroll = [min(box_img_int[0], box_canvas[0]), min(box_img_int[1], box_canvas[1]),
                      max(box_img_int[2], box_canvas[2]), max(box_img_int[3], box_canvas[3])]
        # Horizontal part of the image is in the visible area
        if  box_scroll[0] == box_canvas[0] and box_scroll[2] == box_canvas[2]:
            box_scroll[0]  = box_img_int[0]
            box_scroll[2]  = box_img_int[2]
        # Vertical part of the image is in the visible area
        if  box_scroll[1] == box_canvas[1] and box_scroll[3] == box_canvas[3]:
            box_scroll[1]  = box_img_int[1]
            box_scroll[3]  = box_img_int[3]
        # Convert scroll region to tuple and to integer
        self.canvas.configure(scrollregion=tuple(map(int, box_scroll)))  # set scroll region
        x1 = max(box_canvas[0] - box_image[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(box_canvas[1] - box_image[1], 0)
        x2 = min(box_canvas[2], box_image[2]) - box_image[0]
        y2 = min(box_canvas[3], box_image[3]) - box_image[1]

        self.upper_left = int(x1 / self.scale)
        self.upper_right = int(x2 / self.scale)
        self.bottom_left = int(y1 / self.scale)
        self.bottom_right = int(y2 / self.scale)

        print(self.upper_left, self.upper_right, self.bottom_left, self.bottom_left)

        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            if self.__huge and self.__curr_img < 0:  # show huge image
                h = int((y2 - y1) / self.imscale)  # height of the tile band
                self.__tile[1][3] = h  # set the tile band height
                self.__tile[2] = self.__offset + self.imwidth * int(y1 / self.imscale) * 3
                self.image.size = (self.imwidth, h)  # set size of the tile band
                self.image.tile = [self.__tile]
                image = self.image.crop((int(x1 / self.imscale), 0, int(x2 / self.imscale), h))
            else:  # show normal image
                image = self.pyramid[max(0, self.__curr_img)].crop(  # crop current img from pyramid
                                    (int(x1 // self.scale), int(y1 / self.scale),
                                     int(x2 // self.scale), int(y2 / self.scale)))
            print('_______________________________________________________________________')
            print('resolucao :', int(x1 / self.scale), int(y1 / self.scale), int(x2 / self.scale), int(y2 / self.scale))
            print('x, y  :', abs(int(x1 / self.scale) - int(x2 / self.scale)), abs(int(y1 / self.scale) - int(y2 / self.scale)))
            print('multiplicador :', self.scale)
            print('cantos :', max(box_canvas[0], box_img_int[0]), max((box_canvas[1], box_img_int[1])))

            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1)), self.filter))
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection
            self.corner_left_img, self.corner_right_img, _ = self.coord_zoom_to_draw((box_canvas[0], box_img_int[0]), (box_canvas[1], box_img_int[1]))            
            self.canvas.coords(self.img_canvas_id, self.corner_left_img, self.corner_right_img)
            self.canvas.itemconfig(self.img_canvas_id, image=imagetk)

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
            print('Else')
            print('x_pos', x_pos)
            print('y_pos', y_pos)
            print('scale', self.scale)

        return x_pos, y_pos, self.scale

    def move_to(self, event):
        """ Drag (move) canvas to the new position """
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # zoom tile and show it on the canvas

    def outside(self, x, y):
        """ Checks if the point (x,y) is outside the image area """
        bbox = self.canvas.coords(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            return False  # point (x,y) is inside the image area
        else:
            return True  # point (x,y) is outside the image area

    def wheel(self, event):
        """ Zoom with mouse wheel """
        x = self.canvas.canvasx(event.x)  # get coordinates of the event on the canvas
        y = self.canvas.canvasy(event.y)
        if self.outside(x, y): return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down, smaller
            if round(self.__min_side * self.imscale) < 30: return  # image is less than 30 pixels
            self.imscale /= self.__delta
            scale        /= self.__delta
        if event.num == 4 or event.delta == 120:  # scroll up, bigger
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height()) >> 1
            if i < self.imscale: return  # 1 pixel is bigger than the visible area
            self.imscale *= self.__delta
            scale        *= self.__delta
        # Take appropriate image from the pyramid
        k = self.imscale * self.__ratio  # temporary coefficient
        self.__curr_img = min((-1) * int(math.log(k, self.__reduction)), len(self.pyramid) - 1)
        self.scale = k * math.pow(self.__reduction, max(0, self.__curr_img))
        #
        self.canvas.scale('all', x, y, scale, scale)  # rescale all objects
        # Redraw some figures before showing image on the screen
        self.redraw_figures()  # method for child classes
        self.show_image()

    def __keystroke(self, event):
        """ Scrolling with the keyboard.
            Independent from the language of the keyboard, CapsLock, <Ctrl>+<key>, etc. """
        if event.state - self.__previous_state == 4:  # means that the Control key is pressed
            pass  # do nothing if Control key is pressed
        else:
            self.__previous_state = event.state  # remember the last keystroke state
            # Up, Down, Left, Right keystrokes
            if event.keycode in [68, 39, 102]:  # scroll right: keys 'D', 'Right' or 'Numpad-6'
                self.scroll_x('scroll',  1, 'unit', event=event)
            elif event.keycode in [65, 37, 100]:  # scroll left: keys 'A', 'Left' or 'Numpad-4'
                self.scroll_x('scroll', -1, 'unit', event=event)
            elif event.keycode in [87, 38, 104]:  # scroll up: keys 'W', 'Up' or 'Numpad-8'
                self.scroll_y('scroll', -1, 'unit', event=event)
            elif event.keycode in [83, 40, 98]:  # scroll down: keys 'S', 'Down' or 'Numpad-2'
                self.scroll_y('scroll',  1, 'unit', event=event)

    def crop(self, bbox):
        """ Crop rectangle from the image and return it """
        if self.__huge:  # image is huge and not totally in RAM
            band = bbox[3] - bbox[1]  # width of the tile band
            self.__tile[1][3] = band  # set the tile height
            self.__tile[2] = self.__offset + self.imwidth * bbox[1] * 3  # set offset of the band
            self.image.size = (self.imwidth, band)  # set size of the tile band
            self.image.tile = [self.__tile]
            return self.image.crop((bbox[0], 0, bbox[2], band))
        else:  # image is totally in RAM
            return self.pyramid[0].crop(bbox)

    def destroy(self):
        """ ImageFrame destructor """
        self.image.close()
        map(lambda i: i.close, self.pyramid)  # close all pyramid images
        del self.pyramid[:]  # delete pyramid list
        del self.pyramid  # delete pyramid variable
        self.canvas.destroy()
        self.__imframe.destroy()