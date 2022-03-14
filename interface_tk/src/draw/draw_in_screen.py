from PIL import Image, ImageDraw


class Draw:
    def draw_polygon(self, current_points, draw_line, color_line_rgb, position_x, position_y, transparency):
        number_points = len(current_points)
        if number_points > 2:
            draw_line.polygon(
                (current_points),
                (color_line_rgb + (transparency,)),
                outline="red",
            )

        elif number_points == 2:
            draw_line.line(
                (position_x, position_y, position_x, position_y),
                (color_line_rgb + (transparency,)),
                width=5,
                joint="curve",
            )

        Offset = (10) / 2
        draw_line.ellipse(
            (position_x - Offset, position_y - Offset, position_x + Offset, position_y + Offset),
            (color_line_rgb + (transparency,)),
        )

        return draw_line

    def draw_countour(
        self, draw_line, color_line_rgb, old_position_x, old_position_y, position_x, position_y, transparency, width
    ):
        draw_line.line(
            (old_position_x, old_position_y, position_x, position_y),
            (color_line_rgb + (transparency,)),
            width=width,
            joint="curve",
        )
        Offset = (width) / 2
        draw_line.ellipse(
            (position_x - Offset, position_y - Offset, position_x + Offset, position_y + Offset),
            (color_line_rgb + (transparency,)),
        )

        return draw_line

    def reset_draw_screen(self, outline_rgb, outline_gray, screen_width, screen_height, option="ALL"):

        if option == "CLEAN_JUST_OUTLINE_RGB":
            outline_rgb = Image.new("RGBA", (screen_width, screen_height), (0, 0, 0, 0))
            outline_rgb_line = ImageDraw.Draw(outline_rgb)

            return outline_rgb, outline_rgb_line

        if option == "CLEAN_JUST_OUTLINE_GRAY":
            outline_gray = Image.new("L", (screen_width, screen_height))
            outline_gray_line = ImageDraw.Draw(outline_gray)

            return outline_gray, outline_gray_line

        else:
            outline_rgb = Image.new("RGBA", (screen_width, screen_height), (0, 0, 0, 0))
            outline_rgb_line = ImageDraw.Draw(outline_rgb)

            outline_gray = Image.new("L", (screen_width, screen_height))
            outline_gray_line = ImageDraw.Draw(outline_gray)

            return outline_rgb, outline_rgb_line, outline_gray, outline_gray_line
