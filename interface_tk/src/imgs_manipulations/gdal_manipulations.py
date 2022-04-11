from osgeo import gdal, ogr, osr
import cv2


class GdalManipulations:
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

    def next_img_in_mosaic(self, x_crop, y_crop, iterator_x, iterator_y, iterator_recoil, rgba_mosaic):
        if x_crop + iterator_x < rgba_mosaic.RasterXSize and x_crop + iterator_x > 0:
            x_crop += iterator_x * iterator_recoil

        if x_crop + iterator_x >= rgba_mosaic.RasterXSize:
            x_crop = 0
            y_crop += iterator_y * iterator_recoil

        if y_crop + iterator_y > rgba_mosaic.RasterYSize:
            x_crop = -1
            y_crop = -1

        return x_crop, y_crop

    def back_img_in_mosaic(self, x_crop, y_crop, iterator_x, iterator_y, iterator_recoil, rgba_mosaic):
        if x_crop - iterator_x < rgba_mosaic.RasterXSize and x_crop - iterator_x > 0:
            x_crop -= iterator_x * iterator_recoil

        if x_crop - iterator_x <= 0 and y_crop != 0:
            x_crop = rgba_mosaic.RasterXSize
            y_crop -= iterator_y * iterator_recoil

        if y_crop <= 0:
            x_crop = 0
            y_crop = 0

        return x_crop, y_crop

    def load_next_img_in_mosaic(
        self, x_crop, y_crop, iterator_x, iterator_y, background_percent, iterator_recoil, rgba_mosaic, binary_mosaic
    ):

        x_crop, y_crop = self.next_img_in_mosaic(x_crop, y_crop, iterator_x, iterator_y, iterator_recoil, rgba_mosaic)
        current_img_in_mosaic = binary_mosaic.ReadAsArray(x_crop, y_crop, iterator_x, iterator_y)

        while cv2.countNonZero(current_img_in_mosaic) <= iterator_x * iterator_y * background_percent:
            x_crop, y_crop = self.next_img_in_mosaic(
                x_crop, y_crop, iterator_x, iterator_y, iterator_recoil, rgba_mosaic
            )
            current_img_in_mosaic = binary_mosaic.ReadAsArray(x_crop, y_crop, iterator_x, iterator_y)


        return x_crop, y_crop, current_img_in_mosaic

    def load_back_img_in_mosaic(
        self, x_crop, y_crop, iterator_x, iterator_y, background_percent, iterator_recoil, rgba_mosaic, binary_mosaic
    ):

        x_crop, y_crop = self.back_img_in_mosaic(x_crop, y_crop, iterator_x, iterator_y, iterator_recoil, rgba_mosaic)
        current_img_in_mosaic = binary_mosaic.ReadAsArray(x_crop, y_crop, iterator_x, iterator_y)

        while cv2.countNonZero(current_img_in_mosaic) <= iterator_x * iterator_y * background_percent:
            x_crop, y_crop = self.back_img_in_mosaic(
                x_crop, y_crop, iterator_x, iterator_y, iterator_recoil, rgba_mosaic
            )
            current_img_in_mosaic = binary_mosaic.ReadAsArray(x_crop, y_crop, iterator_x, iterator_y)

        return x_crop, y_crop, current_img_in_mosaic

    def get_image_rgb_by_band(self, x_crop, y_crop, iterator_x, iterator_y, rgba_mosaic, binary_mosaic):
        current_img_in_mosaic = binary_mosaic.ReadAsArray(x_crop, y_crop, iterator_x, iterator_y)

        blueparcela = rgba_mosaic.GetRasterBand(3).ReadAsArray(x_crop, y_crop, iterator_x, iterator_y)
        greenparcela = rgba_mosaic.GetRasterBand(2).ReadAsArray(x_crop, y_crop, iterator_x, iterator_y)
        redparcela = rgba_mosaic.GetRasterBand(1).ReadAsArray(x_crop, y_crop, iterator_x, iterator_y)
        img = cv2.merge((redparcela, greenparcela, blueparcela))
        img[current_img_in_mosaic == 0] = 0

        return img
