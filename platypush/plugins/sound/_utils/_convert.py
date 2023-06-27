import numpy as np
from numpy.typing import DTypeLike, NDArray


def convert_nd_array(  # pylint: disable=too-many-return-statements
    wave: NDArray[np.floating], dtype: DTypeLike
) -> NDArray[np.number]:
    """
    Given a wave as a series of floating point numbers, convert them to the
    appropriate data type.
    """
    t = np.dtype(dtype)
    if t in {np.float16, np.float32, np.float64}:
        return wave.astype(t)
    if t == np.int8:
        return (wave * 2**8).astype(t)
    if t == np.uint8:
        return ((wave + 1) * 2**8).astype(t)
    if t == np.int16:
        return (wave * 2**15).astype(t)
    if t == np.uint16:
        return ((wave + 1) * 2**16).astype(t)
    if t == np.int32:
        return (wave * 2**31).astype(t)
    if t == np.uint32:
        return ((wave + 1) * 2**32).astype(t)

    raise AssertionError(f'Unsupported dtype: {dtype}')
