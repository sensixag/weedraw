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
