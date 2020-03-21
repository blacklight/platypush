from typing import Dict, List, Union

from platypush.message.response import Response


class TensorflowResponse(Response):
    """
    Generic Tensorflow response.
    """
    def __init__(self, *args, model: str, **kwargs):
        """
        :param model: Name of the model.
        """
        super().__init__(*args, output={
            'model': model,
        }, **kwargs)


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


# vim:sw=4:ts=4:et:
