#! python3
from kivy.app import App
from kivy.uix.widget import Widget

class LifeLayout(Widget):
    pass


class LifePixels(App):
    def build(self):
        return LifeLayout()


if __name__ == "__main__":

    LifePixels().run()
