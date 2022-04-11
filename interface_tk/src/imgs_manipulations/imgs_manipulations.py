import cv2
from PIL import Image
import numpy as np
import os

class SatureImg:
    def saturation(self, image: list, increment: float) -> list:
        image_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(image_hsv)
        if s.max() < 255:
            if increment > 0:
                s += int(increment)


        elif increment < 0:
            s -= int(increment)

        image_saturated = cv2.merge((h, s, v))
        image_saturated = cv2.cvtColor(image_saturated, cv2.COLOR_HSV2RGB)

        return image_saturated


class Watershed:
    def watershed(self, image_rgb, img_markers, color_map, screen_width, screen_height):
        image_for_watershed = image_rgb.copy()
        image_for_watershed = cv2.resize(image_for_watershed, (screen_width, screen_height))
        segmentation = np.zeros_like(image_for_watershed)

        markers = cv2.watershed(image_for_watershed.copy(), img_markers.copy())

        for i in range(len(color_map)):
            segmentation[markers == i + 1] = color_map[i]

        bool_draw = True
        segmentation = cv2.cvtColor(segmentation, cv2.COLOR_RGB2RGBA)
        segmentation = Image.fromarray(segmentation)

        return segmentation


class LoadImagesAnalises:
    def __init__(self, path_img_rgb, path_img_bin):
        self.path_img_rgb = path_img_rgb  
        self.path_img_bin = path_img_bin 

    def load_images(self):
        names_imgs_rgb_array = []
        names_imgs_bin_array = []

        for names_imgs_array in os.listdir(self.path_img_bin):
            names_imgs_rgb_array.append(self.path_img_rgb + "/" + names_imgs_array)
            names_imgs_bin_array.append(self.path_img_bin + "/" + names_imgs_array)
            
        return names_imgs_rgb_array, names_imgs_bin_array

class ImagesManipulations:
    def find_contourns(self, img, screen_width, screen_height):
        dots            = cv2.GaussianBlur(img, (21, 21), 0)
        dots_cpy       = cv2.erode(dots, (3, 3))
        dots_cpy        = cv2.dilate(dots_cpy, None, iterations=1)
        filter          = cv2.threshold(dots_cpy, 128, 255, cv2.THRESH_BINARY)[1]
        img = cv2.resize(filter, (screen_width, screen_height))
        contours, hier = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        for idx, c in enumerate(contours):  # numbers the contours
            self.x_ctn = int(sum(c[:, 0, 0]) / len(c))
            self.y_ctn = int(sum(c[:, 0, 1]) / len(c))

        return contours

    def color_to_transparency(self, img, color=(0, 0, 0), transparency=128):
        image_new = []
        for item in img.getdata():
            if item[:3] == (0, 0, 0):
                image_new.append((0, 0, 0, 0))
            else:
                image_new.append(color + (transparency,))

        img.putdata(image_new)

        return img


    def merge_binary_in_rgb(self, screen_main, img_bin, color=(0, 0, 0), transparency=255):
        
        img_bin = cv2.cvtColor(img_bin, cv2.COLOR_BGR2RGBA)
        image_pil_bin = Image.fromarray(img_bin)
        image_pil_bin = self.color_to_transparency(self, image_pil_bin, color, transparency)
        screen_main.paste(image_pil_bin, (0, 0), image_pil_bin)

        return screen_main

    def image_to_tk_screen(self, img, screen_width, screen_height, transparency):
        img = cv2.resize(img, (screen_width, screen_height))
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGBA)
        img = Image.fromarray(img)

        return img

    def draw_dir_to_tk_screen(self, img, screen_width, screen_height, transparency):
        img = cv2.resize(img, (screen_width, screen_height))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(img)

        return img


    def diff_contourns(self, img_neural, img_reference):
        """
        funcao para manipular duas imagens binarias. Efetua a diferenca e a uniao entre duas
        imagens de mesmo tamanho, considerando img_reference como referencia em seu calculo.
        entrada:
                 img_reference - Imagem de Referencia   (marcacoes manuais)
                 img_neural    - Imagem a ser comparada (rede neural)
        saida:
                 union         - uniao entre ambas as imagens
                 dif           - diferenca entre ambas imagens considerando img_reference como referencia
        """

        # img_neural = cv2.threshold(img_neural, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # img_reference = cv2.threshold(img_reference, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        union = np.logical_or(img_neural, img_reference)
        union = union.astype(np.uint8) * 255
        union[union < 128] = 0
        union[union > 100] = 255

        dif = cv2.subtract(union, img_neural)
        dif[dif < 128] = 0
        dif[dif > 100] = 255

        return union, dif

    def prepare_array(self, img, width, height):

        _img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _img = cv2.threshold(_img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        _img = cv2.resize(_img, (width, height), interpolation=cv2.INTER_AREA)

        return _img

    def gray_to_rgba(self, img):
        _img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGBA)

        return _img

    def adjust_pixels(self, src, tolerancy):
        """
        funcao para ajustar os pixels com base em uma tolerancia, eliminando contornos com areas
        menores do que o valor escolhido para tolerancy
        entrada:
                 src       - imagem da predi
                 tolerancy - valor inteiro (0 despreza a tolerancia e retorna os contornos originais)
        saida:
                 result    - contornos validos com base no valor de tolerancy
        """
        ret, binary_map = cv2.threshold(src, 127, 255, 0)
        nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            binary_map, None, None, None, 8, cv2.CV_32S
        )

        areas = stats[1:, cv2.CC_STAT_AREA]
        result = np.zeros((labels.shape), np.uint8)

        for i in range(0, nlabels - 1):
            if areas[i] >= tolerancy:
                result[labels == i + 1] = 255

        return result

    def ellipse_overlap(
        self, image, x_center, y_center, length_x, length_y, angle=0, color=(255, 255, 255), thickness=-1
    ):
        """
        funcao para sobrepor o pixel de uma determinada coordenada por uma elipse.
        entrada:
                 image    - array que define a imagem
                 x_center -  posicao do eixo x onde o pixel se encontra
                 y_center -  posicao do eixo y onde o pixel se encontra
                 length_x -  comprimento da elipse ao longo do eixo x
                 length_y -  comprimento da elipse ao longo do eixo y
                 angle    -  angulo que a elipse possui
                 color    -  cor da elipse
                 thickness-  tipo de preenchimento, -1 preenche totalmente
        saida:
                 array com a elipse na posicao determinada inserida na imagem de entrada
        """
        center_coordinates = (y_center, x_center)
        axesLength = (length_x, length_y)
        angle = angle
        startAngle = 180
        endAngle = 540

        # Cor de preenchimento da elipse
        color = color

        # Metodo de preenchimento, -1 preenche totalmente
        thickness = thickness

        image = cv2.ellipse(image, center_coordinates, axesLength, angle, startAngle, endAngle, color, thickness)

        return image
