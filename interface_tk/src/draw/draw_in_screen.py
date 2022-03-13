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
