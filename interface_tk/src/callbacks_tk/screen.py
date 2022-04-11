class Screen:
    def __init__(self, tk_menu, frame_over_center, screen_width, screen_height):
        self.tk_menu = tk_menu
        self.frame_over_center = frame_over_center
        self.screen_width = screen_width
        self.screen_height = screen_height

    def define_canvas(self):
        self.canvas = self.tk_menu.Canvas(
            self.frame_over_center,
            bd=0,
            width=self.screen_width,
            height=self.screen_height,
        )

        return self.canvas

    # def update_screen(self,):
