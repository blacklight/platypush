import json
import os
import pathlib
import random
import shutil
import threading
from contextlib import contextmanager
from datetime import datetime
from typing import List, Dict, Any, Union, Optional, Tuple, Iterable

import numpy as np
from tensorflow.keras import Model
from tensorflow.keras.layers import Layer
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras import utils

from platypush.config import Config
from platypush.context import get_bus
from platypush.message.event.tensorflow import TensorflowEpochStartedEvent, TensorflowEpochEndedEvent, \
    TensorflowBatchStartedEvent, TensorflowBatchEndedEvent, TensorflowTrainStartedEvent, TensorflowTrainEndedEvent
from platypush.message.response.tensorflow import TensorflowTrainResponse, TensorflowPredictResponse
from platypush.plugins import Plugin, action


class TensorflowPlugin(Plugin):
    """
    This plugin can be used to create, train, load and make predictions with TensorFlow-compatible machine learning
    models.

    Triggers:

        - :class:`platypush.message.event.tensorflow.TensorflowEpochStartedEvent`
            when a Tensorflow model training/evaluation epoch begins.
        - :class:`platypush.message.event.tensorflow.TensorflowEpochEndedEvent`
            when a Tensorflow model training/evaluation epoch ends.
        - :class:`platypush.message.event.tensorflow.TensorflowBatchStartedEvent`
            when a Tensorflow model training/evaluation batch starts being processed.
        - :class:`platypush.message.event.tensorflow.TensorflowBatchEndedEvent`
            when a the processing of a Tensorflow model training/evaluation batch ends.
        - :class:`platypush.message.event.tensorflow.TensorflowTrainStartedEvent`
            when a Tensorflow model starts being trained.
        - :class:`platypush.message.event.tensorflow.TensorflowTrainEndedEvent`
            when the training phase of a Tensorflow model ends.

    Requires:

        * **numpy** (``pip install numpy``)
        * **pandas** (``pip install pandas``) (optional, for CSV parsing)
        * **tensorflow** (``pip install 'tensorflow>=2.0'``)
        * **keras** (``pip install keras``)

    """

    _image_extensions = ['jpg', 'jpeg', 'bmp', 'tiff', 'tif', 'png', 'gif']
    _numpy_extensions = ['npy', 'npz']
    _csv_extensions = ['csv', 'tsv']
    _supported_data_file_extensions = [*_csv_extensions, *_numpy_extensions, *_image_extensions]

    def __init__(self, workdir: Optional[str] = None, **kwargs):
        """
        :param workdir: Working directory for TensorFlow, where models will be stored and looked up by default
            (default: PLATYPUSH_WORKDIR/tensorflow).
        """
        super().__init__(**kwargs)
        self.models: Dict[str, Model] = {}
        self._models_lock = threading.RLock()
        self._model_locks: Dict[str, threading.RLock()] = {}
        self._work_dir = os.path.abspath(os.path.expanduser(workdir)) if workdir else \
            os.path.join(Config.get('workdir'), 'tensorflow')

        self._models_dir = os.path.join(self._work_dir, 'models')
        pathlib.Path(self._models_dir).mkdir(mode=0o755, exist_ok=True, parents=True)

    @contextmanager
    def _lock_model(self, model_name: str):
        with self._models_lock:
            if model_name not in self._model_locks:
                self._model_locks[model_name] = threading.RLock()

        try:
            success = self._model_locks[model_name].acquire(blocking=True, timeout=30.)
            assert success, 'Unable to acquire the model lock'
            yield
        finally:
            # noinspection PyBroadException
            try:
                self._model_locks[model_name].release()
            except:
                pass

    def _load_model(self, model_name: str, reload: bool = False) -> Model:
        if model_name in self.models and not reload:
            return self.models[model_name]

        model = None
        model_dir = None

        if os.path.isdir(os.path.join(self._models_dir, model_name)):
            model_dir = os.path.join(self._models_dir, model_name)
            model = load_model(model_dir)
        else:
            model_name = os.path.abspath(os.path.expanduser(model_name))
            if model_name in self.models and not reload:
                return self.models[model_name]

            if os.path.isfile(model_name):
                model_dir = str(pathlib.Path(model_name).parent)
                model = load_model(model_name)
            elif os.path.isdir(model_name):
                model_dir = model_name
                model = load_model(model_dir)

        assert model, 'Could not find model: {}'.format(model_name)
        model.input_labels = []
        model.output_labels = []
        labels_file = os.path.join(model_dir, 'labels.json')

        if os.path.isfile(labels_file):
            with open(labels_file, 'r') as f:
                labels = json.load(f)
            if isinstance(labels, dict):
                if 'input' in labels:
                    model.input_labels = labels['input']
                if 'output' in labels:
                    model.output_labels = labels['output']
            elif hasattr(labels, '__iter__'):
                model.output_labels = labels

        with self._lock_model(model_name):
            self.models[model_name] = model

        return model

    def _generate_callbacks(self, model: str):
        from tensorflow.keras.callbacks import LambdaCallback
        return [LambdaCallback(
            on_epoch_begin=self.on_epoch_begin(model),
            on_epoch_end=self.on_epoch_end(model),
            on_batch_begin=self.on_batch_begin(model),
            on_batch_end=self.on_batch_end(model),
            on_train_begin=self.on_train_begin(model),
            on_train_end=self.on_train_end(model),
        )]

    @staticmethod
    def on_epoch_begin(model: str):
        def callback(epoch: int, logs: Optional[dict] = None):
            get_bus().post(TensorflowEpochStartedEvent(model=model, epoch=epoch, logs=logs))
        return callback

    @staticmethod
    def on_epoch_end(model: str):
        def callback(epoch: int, logs: Optional[dict] = None):
            get_bus().post(TensorflowEpochEndedEvent(model=model, epoch=epoch, logs=logs))
        return callback

    @staticmethod
    def on_batch_begin(model: str):
        def callback(batch: int, logs: Optional[dict] = None):
            get_bus().post(TensorflowBatchStartedEvent(model=model, batch=batch, logs=logs))
        return callback

    @staticmethod
    def on_batch_end(model: str):
        def callback(batch, logs: Optional[dict] = None):
            get_bus().post(TensorflowBatchEndedEvent(model=model, batch=batch, logs=logs))
        return callback

    @staticmethod
    def on_train_begin(model: str):
        def callback(logs: Optional[dict] = None):
            get_bus().post(TensorflowTrainStartedEvent(model=model, logs=logs))
        return callback

    @staticmethod
    def on_train_end(model: str):
        def callback(logs: Optional[dict] = None):
            get_bus().post(TensorflowTrainEndedEvent(model=model, logs=logs))
        return callback

    @action
    def load(self, model: str, reload: bool = False) -> Dict[str, Any]:
        """
        (Re)-load a model from the file system.

        :param model: Name of the model. It can be a folder name stored under ``<workdir>/models``, or an absolute path
            to a model directory or file (Tensorflow directories, Protobuf models and HDF5 files are supported).
        :param reload: If ``True``, the model will be reloaded from the filesystem even if it's been already
            loaded, otherwise the model currently in memory will be kept (default: ``False``).
        :return: The model configuration.
        """
        model = self._load_model(model, reload=reload)
        return model.get_config()

    @action
    def unload(self, model: str) -> None:
        """
        Remove a loaded model from memory.

        :param model: Name of the model.
        """
        with self._lock_model(model):
            assert model in self.models, 'The model {} is not loaded'.format(model)
            del self.models[model]

    @action
    def remove(self, model: str) -> None:
        """
        Unload a module and, if stored on the filesystem, remove its resource files as well.
        WARNING: This operation is not reversible.

        :param model: Name of the model.
        """
        with self._lock_model(model):
            if model in self.models:
                del self.models[model]

        model_dir = os.path.join(self._models_dir, model)
        if os.path.isdir(model_dir):
            shutil.rmtree(model_dir)

    @action
    def create_network(self,
                       name: str,
                       layers: List[Union[Layer, Dict[str, Any]]],
                       input_names: Optional[List[str]] = None,
                       output_names: Optional[List[str]] = None,
                       optimizer: Optional[str] = 'rmsprop',
                       loss: Optional[Union[str, List[str], Dict[str, str]]] = None,
                       metrics: Optional[
                           Union[str, List[Union[str, List[str]]], Dict[str, Union[str, List[str]]]]] = None,
                       loss_weights: Optional[Union[List[float], Dict[str, float]]] = None,
                       sample_weight_mode: Optional[Union[str, List[str], Dict[str, str]]] = None,
                       weighted_metrics: Optional[List[str]] = None,
                       target_tensors=None,
                       **kwargs) -> Dict[str, Any]:
        """
        Create a neural network TensorFlow Keras model.

        :param name: Name of the model.
        :param layers: List of layers. Example:

          .. code-block:: javascript

            [
              // Input flatten layer with 10 units
              {
                "type": "Flatten",
                "input_shape": [10, 10]
              },

              // Dense hidden layer with 500 units
              {
                "type": "Dense",
                "units": 500,
                "activation": "relu"
              },

              // Dense hidden layer with 100 units
              {
                "type": "Dense",
                "units": 100,
                "activation": "relu"
              },

              // Dense output layer with 2 units (labels) and ``softmax`` activation function
              {
                "type": "Dense",
                "units": 2,
                "activation": "softmax"
              }
            ]

        :param input_names: List of names for the input units (default: TensorFlow name auto-assign logic).
        :param output_names: List of labels for the output units (default: TensorFlow name auto-assign logic).
        :param optimizer: Optimizer, see <https://keras.io/optimizers/> (default: ``rmsprop``).
        :param loss: Loss function, see <https://keras.io/losses/>. An objective function is any callable with
            the signature ``scalar_loss = fn(y_true, y_pred)``. If the model has multiple outputs, you can use a
            different loss on each output by passing a dictionary or a list of losses. The loss value that will be
            minimized by the model will then be the sum of all individual losses (default: None).

        :param metrics: List of metrics to be evaluated by the model during training and testing. Typically you will
            use ``metrics=['accuracy']``. To specify different metrics for different outputs of a multi-output model,
            you could also pass a dictionary, such as
            ``metrics={'output_a': 'accuracy', 'output_b': ['accuracy', 'mse']}``. You can also pass a list
            ``(len = len(outputs))`` of lists of metrics such as ``metrics=[['accuracy'], ['accuracy', 'mse']]`` or
            ``metrics=['accuracy', ['accuracy', 'mse']]``. Default: ``['accuracy']``.

        :param loss_weights: Optional list or dictionary specifying scalar coefficients (Python floats) to weight the
            loss contributions of different model outputs. The loss value that will be minimized by the model
            will then be the *weighted sum* of all individual losses, weighted by the `loss_weights` coefficients.
            If a list, it is expected to have a 1:1 mapping to the model's outputs. If a tensor, it is expected to map
            output names (strings) to scalar coefficients.

        :param sample_weight_mode: If you need to do time-step-wise sample weighting (2D weights), set this to
            ``"temporal"``. ``None`` defaults to sample-wise weights (1D). If the model has multiple outputs,
            you can use a different ``sample_weight_mode`` on each output by passing a dictionary or a list of modes.

        :param weighted_metrics: List of metrics to be evaluated and weighted by ``sample_weight`` or ``class_weight``
            during training and testing.

        :param target_tensors: By default, Keras will create placeholders for the model's target, which will be fed
            with the target data during training. If instead you would like to use your own target tensors (in turn,
            Keras will not expect external numpy data for these targets at training time), you can specify them via the
            ``target_tensors`` argument. It can be a single tensor (for a single-output model), a list of tensors,
            or a dict mapping output names to target tensors.

        :param kwargs: Extra arguments to pass to ``Model.compile()``.

        :return: The model configuration, as a dict. Example:

          .. code-block:: json

            {
              "name": "test_model",
              "layers": [
                {
                  "class_name": "Flatten",
                  "config": {
                    "name": "flatten",
                    "trainable": true,
                    "batch_input_shape": [
                      null,
                      10
                    ],
                    "dtype": "float32",
                    "data_format": "channels_last"
                  }
                },
                {
                  "class_name": "Dense",
                  "config": {
                    "name": "dense",
                    "trainable": true,
                    "dtype": "float32",
                    "units": 100,
                    "activation": "relu",
                    "use_bias": true,
                    "kernel_initializer": {
                      "class_name": "GlorotUniform",
                      "config": {
                        "seed": null
                      }
                    },
                    "bias_initializer": {
                      "class_name": "Zeros",
                      "config": {}
                    },
                    "kernel_regularizer": null,
                    "bias_regularizer": null,
                    "activity_regularizer": null,
                    "kernel_constraint": null,
                    "bias_constraint": null
                  }
                },
                {
                  "class_name": "Dense",
                  "config": {
                    "name": "dense_1",
                    "trainable": true,
                    "dtype": "float32",
                    "units": 50,
                    "activation": "relu",
                    "use_bias": true,
                    "kernel_initializer": {
                      "class_name": "GlorotUniform",
                      "config": {
                        "seed": null
                      }
                    },
                    "bias_initializer": {
                      "class_name": "Zeros",
                      "config": {}
                    },
                    "kernel_regularizer": null,
                    "bias_regularizer": null,
                    "activity_regularizer": null,
                    "kernel_constraint": null,
                    "bias_constraint": null
                  }
                },
                {
                  "class_name": "Dense",
                  "config": {
                    "name": "dense_2",
                    "trainable": true,
                    "dtype": "float32",
                    "units": 2,
                    "activation": "softmax",
                    "use_bias": true,
                    "kernel_initializer": {
                      "class_name": "GlorotUniform",
                      "config": {
                        "seed": null
                      }
                    },
                    "bias_initializer": {
                      "class_name": "Zeros",
                      "config": {}
                    },
                    "kernel_regularizer": null,
                    "bias_regularizer": null,
                    "activity_regularizer": null,
                    "kernel_constraint": null,
                    "bias_constraint": null
                  }
                }
              ]
            }

        """
        from tensorflow.keras import Sequential
        model = Sequential(name=name)
        for layer in layers:
            if not isinstance(layer, Layer):
                layer = self._layer_from_dict(layer.pop('type'), **layer)
            model.add(layer)

        if not metrics:
            metrics = ['accuracy']

        model.compile(
            optimizer=optimizer,
            loss=loss,
            metrics=metrics,
            loss_weights=loss_weights,
            sample_weight_mode=sample_weight_mode,
            weighted_metrics=weighted_metrics,
            target_tensors=target_tensors,
            **kwargs
        )

        model.input_labels = input_names or []
        model.output_labels = output_names or []

        with self._lock_model(name):
            self.models[name] = model
        return model.get_config()

    @action
    def create_regression(self,
                          name: str,
                          units: int = 1,
                          input_names: Optional[List[str]] = None,
                          output_names: Optional[List[str]] = None,
                          activation: str = 'linear',
                          use_bias: bool = True,
                          kernel_initializer: str = 'glorot_uniform',
                          bias_initializer: str = 'zeros',
                          kernel_regularizer: Optional[str] = None,
                          bias_regularizer: Optional[str] = None,
                          optimizer: Optional[str] = 'rmsprop',
                          loss: Optional[Union[str, List[str], Dict[str, str]]] = 'mse',
                          metrics: Optional[
                              Union[str, List[Union[str, List[str]]], Dict[str, Union[str, List[str]]]]] = None,
                          loss_weights: Optional[Union[List[float], Dict[str, float]]] = None,
                          sample_weight_mode: Optional[Union[str, List[str], Dict[str, str]]] = None,
                          weighted_metrics: Optional[List[str]] = None,
                          target_tensors=None,
                          **kwargs) -> Dict[str, Any]:
        """
        Create a linear/logistic regression model.

        :param name: Name of the model.
        :param units: Output dimension (default: 1).
        :param input_names: List of names for the input units (default: TensorFlow name auto-assign logic).
        :param output_names: List of labels for the output units (default: TensorFlow name auto-assign logic).
        :param activation: Activation function to be used (default: None).
        :param use_bias: Whether to calculate the bias/intercept for this model. If set
            to False, no bias/intercept will be used in calculations, e.g., the data
            is already centered (default: True).
        :param kernel_initializer: Initializer for the ``kernel`` weights matrices (default: ``glorot_uniform``).
        :param bias_initializer: Initializer for the bias vector (default: ``zeros``).
        :param kernel_regularizer: Regularizer for kernel vectors (default: None).
        :param bias_regularizer: Regularizer for bias vectors (default: None).
        :param optimizer: Optimizer, see <https://keras.io/optimizers/> (default: ``rmsprop``).
        :param loss: Loss function, see <https://keras.io/losses/>. An objective function is any callable with
            the signature ``scalar_loss = fn(y_true, y_pred)``. If the model has multiple outputs, you can use a
            different loss on each output by passing a dictionary or a list of losses. The loss value that will be
            minimized by the model will then be the sum of all individual losses (default: ``mse``, mean squared error).

        :param metrics: List of metrics to be evaluated by the model during training and testing. Typically you will
            use ``metrics=['accuracy']``. To specify different metrics for different outputs of a multi-output model,
            you could also pass a dictionary, such as
            ``metrics={'output_a': 'accuracy', 'output_b': ['accuracy', 'mse']}``. You can also pass a list
            ``(len = len(outputs))`` of lists of metrics such as ``metrics=[['accuracy'], ['accuracy', 'mse']]`` or
            ``metrics=['accuracy', ['accuracy', 'mse']]``. Default: ``['mae', 'mse']``.

        :param loss_weights: Optional list or dictionary specifying scalar coefficients (Python floats) to weight the
            loss contributions of different model outputs. The loss value that will be minimized by the model
            will then be the *weighted sum* of all individual losses, weighted by the `loss_weights` coefficients.
            If a list, it is expected to have a 1:1 mapping to the model's outputs. If a tensor, it is expected to map
            output names (strings) to scalar coefficients.

        :param sample_weight_mode: If you need to do time-step-wise sample weighting (2D weights), set this to
            ``"temporal"``. ``None`` defaults to sample-wise weights (1D). If the model has multiple outputs,
            you can use a different ``sample_weight_mode`` on each output by passing a dictionary or a list of modes.

        :param weighted_metrics: List of metrics to be evaluated and weighted by ``sample_weight`` or ``class_weight``
            during training and testing.

        :param target_tensors: By default, Keras will create placeholders for the model's target, which will be fed
            with the target data during training. If instead you would like to use your own target tensors (in turn,
            Keras will not expect external numpy data for these targets at training time), you can specify them via the
            ``target_tensors`` argument. It can be a single tensor (for a single-output model), a list of tensors,
            or a dict mapping output names to target tensors.

        :param kwargs: Extra arguments to pass to ``Model.compile()``.

        :return: Configuration of the model, as a dict. Example:

          .. code-block:: json

            {
              "name": "test_regression_model",
              "trainable": true,
              "dtype": "float32",
              "units": 1,
              "activation": "linear",
              "use_bias": true,
              "kernel_initializer": {
                "class_name": "GlorotUniform",
                "config": {
                  "seed": null
                }
              },
              "bias_initializer": {
                "class_name": "Zeros",
                "config": {}
              },
              "kernel_regularizer": null,
              "bias_regularizer": null
            }

        """
        from tensorflow.keras.experimental import LinearModel
        model = LinearModel(
            units=units,
            activation=activation,
            use_bias=use_bias,
            kernel_initializer=kernel_initializer,
            bias_initializer=bias_initializer,
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            name=name)

        model.input_names = input_names or []

        if output_names:
            assert units == len(output_names)
            model.output_labels = output_names
        else:
            model.output_labels = []

        if not metrics:
            metrics = ['mae', 'mse']

        model.compile(
            optimizer=optimizer,
            loss=loss,
            metrics=metrics,
            loss_weights=loss_weights,
            sample_weight_mode=sample_weight_mode,
            weighted_metrics=weighted_metrics,
            target_tensors=target_tensors,
            **kwargs
        )

        with self._lock_model(name):
            self.models[name] = model
        return model.get_config()

    @staticmethod
    def _layer_from_dict(layer_type: str, *args, **kwargs) -> Layer:
        from tensorflow.keras import layers
        cls = getattr(layers, layer_type)
        assert issubclass(cls, Layer)
        return cls(*args, **kwargs)

    @staticmethod
    def _get_csv_data(data_file: str) -> np.ndarray:
        import pandas as pd
        return pd.read_csv(data_file).to_numpy()

    @staticmethod
    def _get_numpy_data(data_file: str) -> np.ndarray:
        return np.load(data_file)

    @staticmethod
    def _get_numpy_compressed_data(data_file: str) -> np.ndarray:
        return list(np.load(data_file).values()).pop()

    @classmethod
    def _get_image(cls, image_file: str, model: Model) -> np.ndarray:
        input_shape = model.inputs[0].shape
        size = input_shape[1:3].as_list()
        assert len(size) == 2, 'The model {} does not have enough dimensions to process an image (shape: {})'.format(
            model.name, size)

        colors = input_shape[3:]
        if len(colors) == 0 or colors[0] == 1:
            color_mode = 'grayscale'
        elif colors[0] == 3:
            color_mode = 'rgb'
        elif colors[0] == 4:
            color_mode = 'rgba'
        else:
            raise AssertionError('The input tensor should have either 1 (grayscale), 3 (rgb) or 4 (rgba) units. ' +
                                 'Found: {}'.format(colors[0]))

        img = image.load_img(image_file, target_size=size, color_mode=color_mode)
        data = image.img_to_array(img)
        if data.shape[-1] == 1:
            # Squeeze extra color channels
            data = np.squeeze(data)
        return data

    @classmethod
    def _get_dir(cls, directory: str, model: Model) -> Dict[str, Iterable]:
        labels = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
        assert set(model.output_labels) == set(labels),\
            'The directory {dir} should contain exactly {n} subfolders named {names}'.format(
                dir=directory, n=len(model.output_labels), names=model.output.labels)

        ret = {}
        for label in labels:
            subdir = os.path.join(directory, label)
            ret[label] = [
                cls._get_data(os.path.join(subdir, f), model)
                for f in os.listdir(subdir)
                if f.split('.')[-1] in cls._supported_data_file_extensions
            ]

        return ret

    @classmethod
    def _get_outputs(cls, data: Union[str, np.ndarray, Iterable], model: Model) -> np.ndarray:
        if isinstance(data, str):
            if model.output_labels:
                label_index = model.output_labels.index(data)
                if label_index >= 0:
                    return np.array([1 if i == label_index else 0 for i in range(len(model.output_labels))])

            return np.array([data])

        if len(data) > 0 and isinstance(data[0], str):
            return np.array([cls._get_outputs(item, model) for item in data])

        return data

    @classmethod
    def _get_data(cls, data: Union[str, np.ndarray, Iterable, Dict[str, Union[Iterable, np.ndarray]]], model: Model) \
            -> Union[np.ndarray, Iterable, Dict[str, Union[Iterable, np.ndarray]]]:
        if isinstance(data, List) or isinstance(data, Tuple):
            if len(data) and isinstance(data[0], str):
                return np.array([cls._get_data(item, model) for item in data])

        if not isinstance(data, str):
            return data

        if data.startswith('http://') or data.startswith('https://'):
            filename = '{timestamp}_{filename}'.format(
                timestamp=datetime.now().timestamp(), filename=data.split('/')[-1])
            data_file = utils.get_file(filename, data)
        else:
            data_file = os.path.abspath(os.path.expanduser(data))

        extensions = [ext for ext in cls._supported_data_file_extensions if data_file.endswith('.' + ext)]

        if os.path.isfile(data_file):
            assert extensions, 'Unsupported type for file {}. Supported extensions: {}'.format(
                data_file, cls._supported_data_file_extensions
            )

            extension = extensions.pop()
            if extension in cls._csv_extensions:
                return cls._get_csv_data(data_file)
            if extension == 'npy':
                return cls._get_numpy_data(data_file)
            if extension == 'npz':
                return cls._get_numpy_compressed_data(data_file)
            if extension in cls._image_extensions:
                return cls._get_image(data_file, model)

            raise AssertionError('Unsupported file type: {}'.format(data_file))
        elif os.path.isdir(data_file):
            return cls._get_dir(data_file, model)

        return data

    @classmethod
    def _get_dataset(cls,
                     inputs: Union[str, np.ndarray, Iterable, Dict[str, Union[Iterable, np.ndarray]]],
                     outputs: Optional[Union[str, np.ndarray, Iterable, Dict[str, Union[Iterable, np.ndarray]]]],
                     model: Model) \
            -> Tuple[Union[np.ndarray, Iterable, Dict[str, Union[Iterable, np.ndarray]]],
                     Optional[Union[np.ndarray, Iterable, Dict[str, Union[Iterable, np.ndarray]]]]]:
        inputs = cls._get_data(inputs, model)
        if outputs:
            outputs = cls._get_outputs(outputs, model)
        elif isinstance(inputs, dict) and model.output_labels:
            pairs = []
            for i, label in enumerate(model.output_labels):
                data = inputs.get(label, [])
                pairs.extend([(d, tuple(1 if i == j else 0 for j, _ in enumerate(model.output_labels)))
                              for d in data])

            random.shuffle(pairs)
            inputs = np.asarray([p[0] for p in pairs])
            outputs = np.asarray([p[1] for p in pairs])

        return inputs, outputs

    @action
    def train(self,
              model: str,
              inputs: Union[str, np.ndarray, Iterable, Dict[str, Union[Iterable, np.ndarray]]],
              outputs: Optional[Union[str, np.ndarray, Iterable]] = None,
              batch_size: Optional[int] = None,
              epochs: int = 1,
              verbose: int = 1,
              validation_split: float = 0.,
              validation_data: Optional[Tuple[Union[np.ndarray, Iterable]]] = None,
              shuffle: Union[bool, str] = True,
              class_weight: Optional[Dict[int, float]] = None,
              sample_weight: Optional[Union[np.ndarray, Iterable]] = None,
              initial_epoch: int = 0,
              steps_per_epoch: Optional[int] = None,
              validation_steps: int = None,
              validation_freq: int = 1,
              max_queue_size: int = 10,
              workers: int = 1,
              use_multiprocessing: bool = False) -> TensorflowTrainResponse:
        """
        Trains a model on a dataset for a fixed number of epochs.

        :param model: Name of the model. It can be a folder name stored under ``<workdir>/models``, or an absolute path
            to a model directory or file (Tensorflow directories, Protobuf models and HDF5 files are supported).
        :param inputs: Input data. It can be:

          - A numpy array (or array-like), or a list of arrays in case the model has multiple inputs.
          - A TensorFlow tensor, or a list of tensors in case the model has multiple inputs.
          - A dict mapping input names to the corresponding array/tensors, if the model has named inputs.
          - A ``tf.data`` dataset. Should return a tuple of either ``(inputs, targets)`` or
            ``(inputs, targets, sample_weights)``.
          - A generator or ``keras.utils.Sequence`` returning ``(inputs, targets)`` or
            ``(inputs, targets, sample weights)``.
          - A string that points to a file. Supported formats:

              - CSV with header (``.csv`` extension``)
              - Numpy raw or compressed files (``.npy`` or ``.npz`` extension)
              - Image files
              - An HTTP URL pointing to one of the file types listed above
              - Directories with images. If ``inputs`` points to a directory of images then the following
                conventions are followed:

                - The folder must contain exactly as many subfolders as the output units of your model. If
                  the model has ``output_labels`` then those subfolders should be named as the output labels.
                  Each subfolder will contain training examples that match the associated label (e.g.
                  ``positive`` will contain all the positive images and ``negative`` all the negative images).
                - ``outputs`` doesn't have to be specified.

        :param outputs: Target data. Like the input data `x`, it can be a numpy array (or array-like) or TensorFlow
            tensor(s). It should be consistent with `x` (you cannot have Numpy inputs and tensor targets, or inversely).
            If `x` is a dataset, generator, or `keras.utils.Sequence` instance, `y` should not be specified
            (since targets will be obtained from `x`).

        :param batch_size: Number of samples per gradient update. If unspecified, ``batch_size`` will default to 32.
            Do not specify the ``batch_size`` if your data is in the form of symbolic tensors, datasets,
            generators, or ``keras.utils.Sequence`` instances (since they generate batches).

        :param epochs: Number of epochs to train the model. An epoch is an iteration over the entire ``x`` and ``y``
            data provided. Note that in conjunction with ``initial_epoch``, ``epochs`` is to be understood as
            "final epoch". The model is not trained for a number of iterations given by ``epochs``, but merely until
            the epoch of index ``epochs`` is reached.

        :param verbose: Verbosity mode. 0 = silent, 1 = progress bar, 2 = one line per epoch.
            Note that the progress bar is not particularly useful when
            logged to a file, so verbose=2 is recommended when not running
            interactively (eg, in a production environment).

        :param validation_split: Float between 0 and 1.
            Fraction of the training data to be used as validation data. The model will set apart this fraction
            of the training data, will not train on it, and will evaluate the loss and any model metrics on this data
            at the end of each epoch. The validation data is selected from the last samples in the ``x`` and ``y``
            data provided, before shuffling. Not supported when ``x`` is a dataset, generator or ``keras.utils.Sequence`` instance.

        :param validation_data: Data on which to evaluate the loss and any model metrics at the end of each epoch.
            The model will not be trained on this data. ``validation_data`` will override ``validation_split``.
            ``validation_data`` could be:

                - tuple ``(x_val, y_val)`` of arrays/numpy arrays/tensors
                - tuple ``(x_val, y_val, val_sample_weights)`` of Numpy arrays
                - dataset

            For the first two cases, ``batch_size`` must be provided. For the last case, ``validation_steps`` could be
            provided.

        :param shuffle: Boolean (whether to shuffle the training data before each epoch) or str (for 'batch').
            'batch' is a special option for dealing with the limitations of HDF5 data; it shuffles in batch-sized
            chunks. Has no effect when ``steps_per_epoch`` is not ``None``.

        :param class_weight: Optional dictionary mapping class indices (integers) to a weight (float) value, used
            for weighting the loss function (during training only). This can be useful to tell the model to
            "pay more attention" to samples from an under-represented class.

        :param sample_weight: Optional iterable/numpy array of weights for the training samples, used for weighting
            the loss function (during training only). You can either pass a flat (1D) numpy array/iterable with the
            same length as the input samples (1:1 mapping between weights and samples), or in the case of temporal data,
            you can pass a 2D array with shape ``(samples, sequence_length)``, to apply a different weight to every
            time step of every sample. In this case you should make sure to specify ``sample_weight_mode="temporal"``
            in ``compile()``. This argument is not supported when ``x`` is a dataset, generator, or
            ``keras.utils.Sequence`` instance, instead provide the sample_weights as the third element of ``x``.

        :param initial_epoch: Epoch at which to start training (useful for resuming a previous training run).

        :param steps_per_epoch: Total number of steps (batches of samples) before declaring one epoch finished and
            starting the next epoch. When training with input tensors such as TensorFlow data tensors, the default
            ``None`` is equal to the number of samples in your dataset divided by the batch size, or 1 if that cannot
            be determined. If x is a ``tf.data`` dataset, and 'steps_per_epoch' is None, the epoch will run until the
            input dataset is exhausted. This argument is not supported with array inputs.

        :param validation_steps: Only relevant if ``validation_data`` is provided and is a ``tf.data`` dataset. Total
            number of steps (batches of samples) to draw before stopping when performing validation at the end of
            every epoch. If 'validation_steps' is None, validation will run until the ``validation_data`` dataset is
            exhausted. In the case of a infinite dataset, it will run into a infinite loop. If 'validation_steps' is
            specified and only part of the dataset will be consumed, the evaluation will start from the beginning of
            the dataset at each epoch. This ensures that the same validation samples are used every time.

        :param validation_freq: Only relevant if validation data is provided. Integer or ``collections_abc.Container``
            instance (e.g. list, tuple, etc.). If an integer, specifies how many training epochs to run before a
            new validation run is performed, e.g. ``validation_freq=2`` runs validation every 2 epochs. If a
            Container, specifies the epochs on which to run validation, e.g. ``validation_freq=[1, 2, 10]`` runs
            validation at the end of the 1st, 2nd, and 10th epochs.

        :param max_queue_size: Used for generator or ``keras.utils.Sequence`` input only. Maximum size for
            the generator queue. If unspecified, ``max_queue_size`` will default to 10.

        :param workers: Used for generator or ``keras.utils.Sequence`` input only. Maximum number of processes
            to spin up when using process-based threading. If unspecified, ``workers`` will default to 1. If 0, will
            execute the generator on the main thread.

        :param use_multiprocessing: Used for generator or ``keras.utils.Sequence`` input only. If ``True``,
            use process-based threading. If unspecified, ``use_multiprocessing`` will default to ``False``.
            Note that because this implementation relies on multiprocessing, you should not pass non-picklable
            arguments to the generator as they can't be passed easily to children processes.

        :return: :class:`platypush.message.response.tensorflow.TensorflowTrainResponse`
        """
        name = model
        model = self._load_model(model)
        inputs, outputs = self._get_dataset(inputs, outputs, model)

        ret = model.fit(
            x=inputs,
            y=outputs,
            batch_size=batch_size,
            epochs=epochs,
            verbose=verbose,
            callbacks=self._generate_callbacks(name),
            validation_split=validation_split,
            validation_data=validation_data,
            shuffle=shuffle,
            class_weight=class_weight,
            sample_weight=sample_weight,
            initial_epoch=initial_epoch,
            steps_per_epoch=steps_per_epoch,
            validation_steps=validation_steps,
            validation_freq=validation_freq,
            max_queue_size=max_queue_size,
            workers=workers,
            use_multiprocessing=use_multiprocessing,
        )

        return TensorflowTrainResponse(model=model, model_name=name, epochs=ret.epoch, history=ret.history)

    @action
    def evaluate(self,
                 model: str,
                 inputs: Union[str, np.ndarray, Iterable, Dict[str, Union[Iterable, np.ndarray]]],
                 outputs: Optional[Union[str, np.ndarray, Iterable]] = None,
                 batch_size: Optional[int] = None,
                 verbose: int = 1,
                 sample_weight: Optional[Union[np.ndarray, Iterable]] = None,
                 steps: Optional[int] = None,
                 max_queue_size: int = 10,
                 workers: int = 1,
                 use_multiprocessing: bool = False) -> Union[Dict[str, float], List[float]]:
        """
        Returns the loss value and metrics values for the model in test model.

        :param model: Name of the model. It can be a folder name stored under ``<workdir>/models``, or an absolute path
            to a model directory or file (Tensorflow directories, Protobuf models and HDF5 files are supported).
        :param inputs: Input data. It can be:

          - A numpy array (or array-like), or a list of arrays in case the model has multiple inputs.
          - A TensorFlow tensor, or a list of tensors in case the model has multiple inputs.
          - A dict mapping input names to the corresponding array/tensors, if the model has named inputs.
          - A ``tf.data`` dataset. Should return a tuple of either ``(inputs, targets)`` or
            ``(inputs, targets, sample_weights)``.
          - A generator or ``keras.utils.Sequence`` returning ``(inputs, targets)`` or
            ``(inputs, targets, sample weights)``.
          - A string that points to a file. Supported formats:

              - CSV with header (``.csv`` extension``)
              - Numpy raw or compressed files (``.npy`` or ``.npz`` extension)
              - Image files
              - An HTTP URL pointing to one of the file types listed above
              - Directories with images. If ``inputs`` points to a directory of images then the following
                conventions are followed:

                - The folder must contain exactly as many subfolders as the output units of your model. If
                  the model has ``output_labels`` then those subfolders should be named as the output labels.
                  Each subfolder will contain training examples that match the associated label (e.g.
                  ``positive`` will contain all the positive images and ``negative`` all the negative images).
                - ``outputs`` doesn't have to be specified.


        :param outputs: Target data. Like the input data `x`, it can be a numpy array (or array-like) or TensorFlow tensor(s).
            It should be consistent with `x` (you cannot have Numpy inputs and tensor targets, or inversely).
            If `x` is a dataset, generator, or `keras.utils.Sequence` instance, `y` should not be specified
            (since targets will be obtained from `x`).

        :param batch_size: Number of samples per gradient update. If unspecified, ``batch_size`` will default to 32.
            Do not specify the ``batch_size`` if your data is in the form of symbolic tensors, datasets,
            generators, or ``keras.utils.Sequence`` instances (since they generate batches).

        :param verbose: Verbosity mode. 0 = silent, 1 = progress bar, 2 = one line per epoch.
            Note that the progress bar is not particularly useful when
            logged to a file, so verbose=2 is recommended when not running
            interactively (eg, in a production environment).

        :param sample_weight: Optional iterable/numpy array of weights for the training samples, used for weighting
            the loss function (during training only). You can either pass a flat (1D) numpy array/iterable with the
            same length as the input samples (1:1 mapping between weights and samples), or in the case of temporal data,
            you can pass a 2D array with shape ``(samples, sequence_length)``, to apply a different weight to every
            time step of every sample. In this case you should make sure to specify ``sample_weight_mode="temporal"``
            in ``compile()``. This argument is not supported when ``x`` is a dataset, generator, or
            ``keras.utils.Sequence`` instance, instead provide the sample_weights as the third element of ``x``.

        :param steps: Total number of steps (batches of samples) before declaring the evaluation round finished.
            Ignored with the default value of ``None``. If x is a ``tf.data`` dataset and ``steps`` is None, 'evaluate'
            will run until the dataset is exhausted. This argument is not supported with array inputs.

        :param max_queue_size: Used for generator or ``keras.utils.Sequence`` input only. Maximum size for the generator
            queue. If unspecified, ``max_queue_size`` will default to 10.

        :param workers: Used for generator or ``keras.utils.Sequence`` input only. Maximum number of processes
            to spin up when using process-based threading. If unspecified, ``workers`` will default to 1. If 0, will
            execute the generator on the main thread.

        :param use_multiprocessing: Used for generator or ``keras.utils.Sequence`` input only. If ``True``,
            use process-based threading. If unspecified, ``use_multiprocessing`` will default to ``False``.
            Note that because this implementation relies on multiprocessing, you should not pass non-picklable
            arguments to the generator as they can't be passed easily to children processes.

        :return: ``{test_metric: metric_value}`` dictionary if the ``metrics_names`` of the model are specified,
            otherwise a list with the result test metrics (loss is usually the first value).
        """

        name = model
        model = self._load_model(model)
        inputs, outputs = self._get_dataset(inputs, outputs, model)

        ret = model.evaluate(
            x=inputs,
            y=outputs,
            batch_size=batch_size,
            verbose=verbose,
            sample_weight=sample_weight,
            steps=steps,
            callbacks=self._generate_callbacks(name),
            max_queue_size=max_queue_size,
            workers=workers,
            use_multiprocessing=use_multiprocessing
        )

        ret = ret if isinstance(ret, list) else [ret]
        if not model.metrics_names:
            return ret

        return {model.metrics_names[i]: value for i, value in enumerate(ret)}

    @action
    def predict(self,
                model: str,
                inputs: Union[str, np.ndarray, Iterable, Dict[str, Union[Iterable, np.ndarray]]],
                batch_size: Optional[int] = None,
                verbose: int = 0,
                steps: Optional[int] = None,
                max_queue_size: int = 10,
                workers: int = 1,
                use_multiprocessing: bool = False) -> TensorflowPredictResponse:
        """
        Generates output predictions for the input samples.

        :param model: Name of the model. It can be a folder name stored under ``<workdir>/models``, or an absolute path
            to a model directory or file (Tensorflow directories, Protobuf models and HDF5 files are supported).
        :param inputs: Input data. It can be:

          - A numpy array (or array-like), or a list of arrays in case the model has multiple inputs.
          - A TensorFlow tensor, or a list of tensors in case the model has multiple inputs.
          - A dict mapping input names to the corresponding array/tensors, if the model has named inputs.
          - A ``tf.data`` dataset. Should return a tuple of either ``(inputs, targets)`` or
            ``(inputs, targets, sample_weights)``.
          - A generator or ``keras.utils.Sequence`` returning ``(inputs, targets)`` or
            ``(inputs, targets, sample weights)``.
          - A string that points to a file. Supported formats:

              - CSV with header (``.csv`` extension``)
              - Numpy raw or compressed files (``.npy`` or ``.npz`` extension)
              - Image files
              - An HTTP URL pointing to one of the file types listed above

        :param batch_size: Number of samples per gradient update. If unspecified, ``batch_size`` will default to 32.
            Do not specify the ``batch_size`` if your data is in the form of symbolic tensors, datasets,
            generators, or ``keras.utils.Sequence`` instances (since they generate batches).

        :param verbose: Verbosity mode, 0 or 1.

        :param steps: Total number of steps (batches of samples) before declaring the prediction round finished.
            Ignored with the default value of ``None``. If x is a ``tf.data`` dataset and ``steps`` is None, ``predict``
            will run until the input dataset is exhausted.

        :param max_queue_size: Integer. Used for generator or ``keras.utils.Sequence`` input only. Maximum size for
            the generator queue (default: 10).

        :param workers: Used for generator or ``keras.utils.Sequence`` input only. Maximum number of processes
            to spin up when using process-based threading. If unspecified, ``workers`` will default to 1. If 0, will
            execute the generator on the main thread.

        :param use_multiprocessing: Used for generator or ``keras.utils.Sequence`` input only. If ``True``,
            use process-based threading. If unspecified, ``use_multiprocessing`` will default to ``False``.
            Note that because this implementation relies on multiprocessing, you should not pass non-picklable
            arguments to the generator as they can't be passed easily to children processes.

        :return: :class:`platypush.message.response.tensorflow.TensorflowPredictResponse`. Format:

            - For regression models with no output labels specified: ``outputs`` will contain the output vector:

                .. code-block:: json

                  {
                      "outputs": [[3.1415]]
                  }

            - For regression models with output labels specified: ``outputs`` will be a list of ``{label -> value}``
              maps:

                .. code-block:: json

                  {
                      "outputs": [
                          {
                              "x": 42.0,
                              "y": 43.0
                          }
                      ]
                  }

            - For neural networks: ``outputs`` will contain the list of the output vector like in the case of
              regression, and ``predictions`` will store the list of ``argmax`` (i.e. the index of the output unit with the
              highest value) or their labels, if the model has output labels:

                .. code-block:: json

                  {
                      "predictions": [
                          "positive"
                      ],
                      "outputs": [
                          {
                              "positive": 0.998,
                              "negative": 0.002
                          }
                      ]
                  }

        """
        name = model
        model = self._load_model(model)
        inputs = self._get_data(inputs, model)
        if isinstance(inputs, np.ndarray) and \
                len(model.inputs[0].shape) == len(inputs.shape) + 1 and \
                (model.inputs[0].shape[0] is None or model.inputs[0].shape[0].value is None):
            inputs = np.asarray([inputs])

        ret = model.predict(
            inputs,
            batch_size=batch_size,
            verbose=verbose,
            steps=steps,
            callbacks=self._generate_callbacks(name),
            max_queue_size=max_queue_size,
            workers=workers,
            use_multiprocessing=use_multiprocessing
        )

        return TensorflowPredictResponse(model=model, model_name=name, prediction=ret,
                                         output_labels=model.output_labels)

    @action
    def save(self, model: str, overwrite: bool = True, **opts) -> None:
        """
        Save a model in memory to the filesystem. The model files will be stored under
        ``<WORKDIR>/models/<model_name>``.

        :param model: Model name.
        :param overwrite: Overwrite the model files if they already exist.
        :param opts: Extra options to be passed to ``Model.save()``.
        """
        model_name = model
        model_dir = None

        if os.path.isdir(os.path.join(self._models_dir, model_name)) or model_name in self.models:
            model_dir = os.path.join(self._models_dir, model_name)
        else:
            model_file = os.path.abspath(os.path.expanduser(model_name))
            if os.path.isfile(model_file):
                model_dir = str(pathlib.Path(model_file).parent)
            elif os.path.isdir(model_file):
                model_dir = model_file

        model = self.models.get(model_name, self.models.get(model_dir))
        assert model, 'No such model loaded: {}'.format(model_name)
        pathlib.Path(model_dir).mkdir(parents=True, exist_ok=True)

        with self._lock_model(model_name):
            labels = {}
            labels_file = os.path.join(model_dir, 'labels.json')

            if hasattr(model, 'input_labels') and model.input_labels:
                labels['input'] = model.input_labels
            if hasattr(model, 'output_labels') and model.output_labels:
                if hasattr(labels, 'input'):
                    labels['output'] = model.output_labels
                else:
                    labels = model.output_labels

            if labels:
                with open(labels_file, 'w') as f:
                    json.dump(labels, f)

            model.save(model_name if os.path.isfile(model_name) else model_dir, overwrite=overwrite, options=opts)


# vim:sw=4:ts=4:et:
