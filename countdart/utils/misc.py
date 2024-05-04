""" Miscellaneous helper functions"""
import struct

import numpy as np


def encode_numpy(array: np.ndarray) -> bytes:
    """Encodes numpy array to bytes. Will save shape of array in bytes string.
    The decode function assumes the array is in uint8.
    See: https://stackoverflow.com/a/60457732


    Args:
        array (np.ndarray): an uint8 array to encode

    Returns:
        bytes: encoded array
    """

    if len(array.shape) == 2:
        h, w = array.shape
        c = 1
    elif len(array.shape) == 3:
        h, w, c = array.shape
    else:
        raise ValueError(
            f"Shape {array.shape} is not supported. Please use (h, w, c) or (h, w)"
        )
    shape = struct.pack(">III", h, w, c)
    encoded = shape + array.tobytes()
    return encoded


def decode_numpy(bytes: bytes) -> np.ndarray:
    """decode bytes to numpy array. Assumes the original array had uin8 format

    Args:
        bytes (bytes): the bytes

    Returns:
        np.ndarray: the resulting array
    """
    h, w, c = struct.unpack(">III", bytes[:12])
    # Add slicing here, or else the array would differ from the original
    array = np.frombuffer(bytes[12:], dtype=np.uint8).reshape(h, w, c)
    return array
