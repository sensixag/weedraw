from imgs_manipulations import SatureImg


class GetSlidersValues:
    def __init__(self, root, tk):
        self.root = root
        self.current_value_saturation = tk.DoubleVar()
        self.current_value_contourn = tk.DoubleVar()
        self.current_value_opacity = tk.DoubleVar()

    # Metodos para receber os valores do slider de saturação
    def get_current_value_saturation(self):
        self.slider_saturation = int(self.current_value_saturation.get())
        print("valor slider :", self.slider_saturation)
        if self.bool_draw:
            print("Na condicao")
            self.image_down = SatureImg().saturation(
                self.image_down, self.slider_saturation - self.slider_saturation_old
            )

            if self.slider_saturation <= 10:
                self.image_down = self.imgparcela.copy()

            self.update_img(self.draw_img)
        self.slider_saturation_old = self.slider_saturation

    def slider_changed_saturation(self, event):
        self.set_slider_saturation.configure(text=self.get_current_value_saturation())

    # Metodos para receber os valores do slider de contorno
    def get_current_value_contourn(self):
        self.slider_pencil = self.current_value_contourn.get()
        if self.slider_pencil < 10:
            self.slider_pencil = 10

    def slider_changed_contourn(self, event):
        self.set_slider_contourn.configure(text=self.get_current_value_contourn())

    # Metodos para receber os valores do slider de opacidade
    def get_current_value_opacity(self):
        self.slider_opacity = int(self.current_value_opacity.get())

    def slider_changed_opacity(self, event):
        self.set_slider_opacity.configure(text=self.get_current_value_opacity())
