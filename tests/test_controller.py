from picpick.controller import Controller
from picpick.model import Model


def test_current_image(model: Model):
    controller = Controller(model=model)

    assert controller.current_image.path.name == 'one.jpg'
    controller.set_current_image(controller.images[1])
    assert controller.current_image.path.name == 'three.jpg'
    controller.set_current_image(controller.images[2])
    assert controller.current_image.path.name == 'two.jpg'
    controller.set_current_image(controller.images[0])
    assert controller.current_image.path.name == 'one.jpg'
