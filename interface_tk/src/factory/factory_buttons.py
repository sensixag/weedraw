class ButtonFactory:
    def createButton(self, type_):
        return buttonTypes[type_]()


class ButtonBase:
    relx = 0.0
    rely = 0.0
    height = 50
    width = 50
    background = "black"
    text = "Test"

    def getButtonConfig(self):
        return (
            self.relx,
            self.rely,
            self.height,
            self.width,
            self.background,
            self.text,
        )


class ButtonLoadMosaic(ButtonBase):
    relx = 0.72
    rely = 0.52
    height = 28
    width = 123
    background = "black"
    text = "Mosaico"


class ButtonShape(ButtonBase):
    relx = 0.72
    rely = 0.60
    height = 28
    width = 123
    background = "black"
    text = "Shape"


class ButtonStart(ButtonBase):
    relx = 0.742
    rely = 0.871
    height = 48
    width = 123
    background = "black"
    text = "Iniciar"


buttonTypes = [ButtonLoadMosaic, ButtonShape, ButtonStart]
