import os

from platypush.plugins import Plugin, action


class MlModel:
    def __init__(self, model_file, classes=None):
        import cv2

        self.model_file = os.path.abspath(os.path.expanduser(model_file))
        self.classes = classes or []
        self.model = cv2.dnn.readNet(model_file)

    def predict(self, img, resize=None, color_convert=None):
        import cv2
        import numpy as np

        if isinstance(img, str):
            img = cv2.imread(os.path.abspath(os.path.expanduser(img)))

        if color_convert:
            if isinstance(color_convert, str):
                color_convert = getattr(cv2, color_convert)

            img = cv2.cvtColor(img, color_convert)

        if resize:
            img = cv2.dnn.blobFromImage(img, size=tuple(resize), mean=0.5)
        else:
            img = cv2.dnn.blobFromImage(img, mean=0.5)

        self.model.setInput(img)
        output = self.model.forward()
        prediction = int(np.argmax(output))

        if self.classes:
            prediction = self.classes[prediction]

        return prediction


class MlCvPlugin(Plugin):
    """
    Plugin to train and make computer vision predictions using machine learning models.

    Requires:

        * **numpy** (``pip install numpy``)
        * **opencv** (``pip install cv2``)

    Also make sure that your OpenCV installation comes with the ``dnn`` module. To test it::

        >>> import cv2.dnn

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.models = {}

    @action
    def predict(self, img, model_file, classes=None, resize=None, color_convert=None):
        """
        Make predictions for an input image using a model file. Supported model formats include all the
        types supported by cv2.dnn (currently supported: Caffe, TensorFlow, Torch, Darknet, DLDT).

        :param model_file: Path to the model file
        :param img: Path to the image
        :param classes: List of string labels associated with the output values (e.g. ['negative', 'positive']).
            If not set then the index of the output neuron with highest value will be returned.
        :param resize: Tuple or list with the resize factor to be applied to the image before being fed to
            the model (default: None)
        :param color_convert: Color conversion to be applied to the image before being fed to the model.
            It points to a cv2 color conversion constant (e.g. ``cv2.COLOR_BGR2GRAY``) and it can be either
            the constant value itself or a string (e.g. 'COLOR_BGR2GRAY').
        """

        model_file = os.path.abspath(os.path.expanduser(model_file))

        if model_file not in self.models:
            self.models[model_file] = MlModel(model_file, classes=classes)

        return self.models[model_file].predict(img, resize=resize, color_convert=color_convert)


# vim:sw=4:ts=4:et:
