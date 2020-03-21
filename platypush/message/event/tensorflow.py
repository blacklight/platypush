from typing import Optional, Dict, Union

from platypush.message.event import Event


class TensorflowEvent(Event):
    def __init__(self, model: str, logs: Optional[Dict[str, Union[int, float]]], *args, **kwargs):
        """
        :param model: Name of the Tensorflow model.
        :param logs: Logs and metrics.
        """
        super().__init__(*args, model=model, logs=logs, **kwargs)


class TensorflowEpochStartedEvent(TensorflowEvent):
    """
    Triggered when a Tensorflow model training/evaluation epoch begins.
    """
    def __init__(self, epoch: int, *args, **kwargs):
        """
        :param epoch: Epoch index.
        """
        super().__init__(*args, epoch=epoch, **kwargs)


class TensorflowEpochEndedEvent(TensorflowEvent):
    """
    Triggered when a Tensorflow model training/evaluation epoch ends.
    """
    def __init__(self, epoch: int, *args, **kwargs):
        """
        :param epoch: Epoch index.
        """
        super().__init__(*args, epoch=epoch, **kwargs)


class TensorflowBatchStartedEvent(TensorflowEvent):
    """
    Triggered when a Tensorflow model training/evaluation batch starts being processed.
    """
    def __init__(self, batch: int, *args, **kwargs):
        """
        :param batch: Batch index.
        """
        super().__init__(*args, batch=batch, **kwargs)


class TensorflowBatchEndedEvent(TensorflowEvent):
    """
    Triggered when a the processing of a Tensorflow model training/evaluation batch ends.
    """
    def __init__(self, batch: int, *args, **kwargs):
        """
        :param batch: Batch index.
        """
        super().__init__(*args, batch=batch, **kwargs)


class TensorflowTrainStartedEvent(TensorflowEvent):
    """
    Triggered when a Tensorflow model starts being trained.
    """


class TensorflowTrainEndedEvent(TensorflowEvent):
    """
    Triggered when the training phase of a Tensorflow model ends.
    """


# vim:sw=4:ts=4:et:
