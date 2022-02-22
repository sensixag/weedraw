import cv2
import imgaug as im
import numpy as np


class Watershed:
    def __init__(self, image_rgb, markers, color_line_rgb, points, thickness):

        self.image_rgb = image_rgb
        self.marker_base = markers
        self.color_line_rgb = color_line_rgb
        self.points = points
        self.thickness = thickness

        self.marker_base = np.zeros(image_rgb.shape[0:2], dtype="int32")
        self.segmentation = np.zeros_like(image_rgb)
        self.color_line = 0

        # Valores do color_map: BLACK, RED, GREEN, BLUE
        self.color_map = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)]

        self.adjust_color(self.color_line_rgb)
        self.watershed_exec()

    def adjust_color(self, color):
        for i in range(len(self.color_map)):
            if self.color_line_rgb == self.color_map[i]:
                self.color_line = i
                print(self.color_line)

    def watershed_exec(self):
        cv2.line(self.marker_base, self.points, self.points, self.color_line, self.thickness)
        markers = cv2.watershed(self.image_rgb, self.marker_base)

        for i in range(len(self.color_map)):
            self.segmentation[markers == 0] = self.color_map[0]
            self.segmentation[markers == i + 1] = self.color_map[i]

        im.imshow(self.segmentation)
        return self.segmentation
