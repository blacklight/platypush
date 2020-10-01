from typing import Dict, List, Union, Optional

import numpy as np
from tensorflow.keras.models import Model

from platypush.message.response import Response


class TensorflowResponse(Response):
    """
    Generic Tensorflow response.
    """
    def __init__(self, *args, model: Model, model_name: Optional[str] = None, **kwargs):
        """
        :param model: Name of the model.
        """
        super().__init__(*args, output={
            'model': model_name or model.name,
        }, **kwargs)

        self.model = model


class TensorflowTrainResponse(TensorflowResponse):
    """
    Tensorflow model fit/train response.
    """
    def __init__(self, *args, epochs: List[int], history: Dict[str, List[Union[int, float]]], **kwargs):
        """
        :param epochs: List of epoch indexes the model has been trained on.
        :param history: Train history, as a ``metric -> [values]`` dictionary where each value in ``values`` is
            the value for of that metric on a specific epoch.
        """
        super().__init__(*args, **kwargs)
        self.output['epochs'] = epochs
        self.output['history'] = history


class TensorflowPredictResponse(TensorflowResponse):
    """
    Tensorflow model prediction response.
    """
    def __init__(self, *args, prediction: np.ndarray, output_labels: Optional[List[str]] = None, **kwargs):
        super().__init__(*args, **kwargs)

        if output_labels and len(output_labels) == self.model.outputs[-1].shape[-1]:
            self.output['outputs'] = [
                {output_labels[i]: value for i, value in enumerate(p)}
                for p in prediction
            ]
        else:
            self.output['outputs'] = prediction

        if self.model.__class__.__name__ != 'LinearModel':
            prediction = [int(np.argmax(p)) for p in prediction]
            if output_labels:
                self.output['predictions'] = [output_labels[p] for p in prediction]
            else:
                self.output['predictions'] = prediction


# vim:sw=4:ts=4:et:
