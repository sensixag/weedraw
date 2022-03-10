import cv2


class SatureImg:
    def saturation(self, image: list, increment: float) -> list:
        image_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(image_hsv)
        print("smax", s.max())
        if s.max() < 255:
            if increment > 0:
                s += int(increment)
                print(increment)
                print(s.max())

        elif increment < 0:
            print("s")
            s -= int(increment)

        image_saturated = cv2.merge((h, s, v))
        image_saturated = cv2.cvtColor(image_saturated, cv2.COLOR_HSV2RGB)

        return image_saturated
