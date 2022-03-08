import numpy as np
import os
import cv2

from keras_segmentation.predict import predict
from keras.preprocessing import image
from numpy.core.records import array
from tensorflow.python.keras.backend import print_tensor
from tensorflow.python.keras.preprocessing.image import img_to_array

from matplotlib import pyplot as plt
from matplotlib import cm
from sklearn.metrics import jaccard_score

os.environ["SM_FRAMEWORK"] = "tf.keras"
import segmentation_models as sm


# model = sm.Linknet(backbone_name=BACKBONE, encoder_weights='imagenet', encoder_freeze=True, classes=1, activation='sigmoid', weights = '../pericles_examples/jocival/vgg16_Linknet_Test24.hdf5')


class NeuralFunctions:
    def __init__(self, path_neural_network) -> None:
        self.model = sm.Linknet(
            backbone_name="vgg16",
            encoder_weights="imagenet",
            encoder_freeze=True,
            classes=1,
            activation="sigmoid",
            weights=path_neural_network,
        )

    def predict_image(self, img, path_rgb="", option="array"):

        if option == "path":
            img_true = cv2.imread(path_rgb, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img_true, (256, 256))
            img = image.load_img(path_rgb, target_size=(256, 256))
            img = image.img_to_array(img)
            img = img / 255

        elif option == "array":
            img = cv2.resize(img, (256, 256))

        pr = self.model.predict(np.array([img]))[0]
        pr = pr[:, :, 0]
        pr[pr >= 0.1] = 1
        pr[pr < 0.5] = 0
        pr = pr.astype("uint8")

        pr[pr == 1] = 255

        return pr

    def iou(self, prediction, target):

        intersection = np.logical_and(target, prediction)
        union = np.logical_or(target, prediction)
        iou_score = np.sum(intersection) / np.sum(union)

        return iou_score


class ImagesManipulations:
    def find_contourns(self, img):

        # dots            = cv2.GaussianBlur(img, (21, 21), 0)
        # dots_cpy       = cv2.erode(dots, (3, 3))
        # dots_cpy        = cv2.dilate(img, None, iterations=4)
        # filter          = cv2.threshold(dots_cpy, 128, 255, cv2.THRESH_BINARY)[1]
        contours, hier = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        print(len(contours))

        for idx, c in enumerate(contours):  # numbers the contours
            self.x_ctn = int(sum(c[:, 0, 0]) / len(c))
            self.y_ctn = int(sum(c[:, 0, 1]) / len(c))

        return contours

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
